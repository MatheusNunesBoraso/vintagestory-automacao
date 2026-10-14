using System;
using System.Collections.Generic;
using System.Linq;
using ProtoBuf;
using Vintagestory.API.Client;
using Vintagestory.API.Common;
using Vintagestory.API.MathTools;
using Vintagestory.API.Server;

namespace Automacao
{
    [ProtoContract]
    public class PacoteConexoes
    {
        [ProtoMember(1)] public List<double> Linhas = new List<double>();   // x1,y1,z1,x2,y2,z2 ...
    }

    /// <summary>
    /// A rede SEM FIO. A cada segundo: postes que alcançam um ao outro (8 blocos pra cada lado) viram uma rede;
    /// cada fonte/bateria/máquina entra na rede do poste mais perto que a alcança. Na rede: soma o que as fontes
    /// geram, o que as máquinas pedem, e a bateria cobre a diferença (ou guarda a sobra).
    /// </summary>
    public class RedeEnergia : ModSystem
    {
        public const int Alcance = 8;

        ICoreServerAPI sapi;
        readonly Dictionary<BlockPos, BEMaquina> pecas = new Dictionary<BlockPos, BEMaquina>();
        /// <summary>Resumo de cada rede (pro Painel e pro poste): por posição de poste.</summary>
        public readonly Dictionary<BlockPos, ResumoRede> Resumo = new Dictionary<BlockPos, ResumoRede>();
        readonly Dictionary<BlockPos, int> redeDe = new Dictionary<BlockPos, int>();
        readonly List<ResumoRede> redes = new List<ResumoRede>();

        public class ResumoRede
        {
            public int Id;
            public float Gerando, Pedindo, Carga, Capacidade;
            public List<BEMaquina> Postes = new List<BEMaquina>(), Pecas = new List<BEMaquina>();
        }

        public override bool ShouldLoad(EnumAppSide forSide) => true;

        public override void Start(ICoreAPI api)
        {
            api.Network.RegisterChannel("automacao-rede").RegisterMessageType<PacoteConexoes>();
        }

        public override void StartServerSide(ICoreServerAPI api)
        {
            sapi = api;
            api.Event.RegisterGameTickListener(Tick, 1000);
        }

        public override void StartClientSide(ICoreClientAPI api)
        {
            RedeCliente.Iniciar(api);
            api.Network.GetChannel("automacao-rede").SetMessageHandler<PacoteConexoes>(RedeCliente.MostrarConexoes);
        }

        public void Registrar(BEMaquina be) => pecas[be.Pos.Copy()] = be;
        public void Remover(BEMaquina be) => pecas.Remove(be.Pos);

        static bool Alcanca(BlockPos poste, BlockPos p) =>
            Math.Abs(poste.X - p.X) <= Alcance && Math.Abs(poste.Z - p.Z) <= Alcance && Math.Abs(poste.Y - p.Y) <= Alcance;

        public ResumoRede RedeDa(BEMaquina be) => redeDe.TryGetValue(be.Pos, out int id) && id < redes.Count ? redes[id] : null;

        void Tick(float dt)
        {
            var todas = pecas.Values.Where(b => b.Api != null && b.Trabalho != null).ToList();
            var postes = todas.Where(b => b.Trabalho.Tipo == "poste").ToList();

            // 1) Postes que se alcançam = mesma rede (union-find simples)
            var pai = Enumerable.Range(0, postes.Count).ToArray();
            int Raiz(int i) { while (pai[i] != i) i = pai[i] = pai[pai[i]]; return i; }
            for (int i = 0; i < postes.Count; i++)
                for (int j = i + 1; j < postes.Count; j++)
                    if (Alcanca(postes[i].Pos, postes[j].Pos)) pai[Raiz(i)] = Raiz(j);

            redes.Clear();
            redeDe.Clear();
            Resumo.Clear();
            var idDaRaiz = new Dictionary<int, int>();
            for (int i = 0; i < postes.Count; i++)
            {
                int r = Raiz(i);
                if (!idDaRaiz.TryGetValue(r, out int id))
                {
                    id = redes.Count;
                    idDaRaiz[r] = id;
                    redes.Add(new ResumoRede { Id = id });
                }
                redes[id].Postes.Add(postes[i]);
                postes[i].NaRede = true;
                redeDe[postes[i].Pos] = id;
            }

            // 2) Cada peça entra na rede do poste mais perto que a alcança
            foreach (var b in todas)
            {
                if (b.Trabalho.Tipo == "poste") continue;
                BEMaquina melhor = null;
                double md = double.MaxValue;
                foreach (var p in postes)
                {
                    if (!Alcanca(p.Pos, b.Pos)) continue;
                    double d = p.Pos.DistanceSqTo(b.Pos.X, b.Pos.Y, b.Pos.Z);
                    if (d < md) { md = d; melhor = p; }
                }
                if (melhor == null)
                {
                    b.NaRede = false;
                    b.Energizado = false;
                    b.Energia = 0;
                    if (b.Trabalho.Tipo == "fonte") b.UltimaGeracao = SafeGerar(b);
                    continue;
                }
                int id = redeDe[melhor.Pos];
                redeDe[b.Pos] = id;
                redes[id].Pecas.Add(b);
                b.NaRede = true;
            }

            // 3) Balanço de cada rede
            foreach (var rede in redes)
            {
                var fontes = rede.Pecas.Where(b => b.Trabalho.Tipo == "fonte").ToList();
                var baterias = rede.Pecas.Where(b => b.Trabalho.Tipo == "bateria").ToList();
                var maquinas = rede.Pecas.Where(b => b.Trabalho.Tipo == "maquina").ToList();

                float gera = 0;
                foreach (var f in fontes)
                {
                    f.UltimaGeracao = f.Ligada ? SafeGerar(f) : 0;
                    gera += f.UltimaGeracao;
                }
                float pede = maquinas.Where(m => m.Quer && m.Ligada).Sum(m => { try { return m.Trabalho.ConsumoAgora(m); } catch { return m.Trabalho.Consumo; } });
                float carga = baterias.Sum(b => b.Carga), cap = baterias.Sum(b => b.Trabalho.Capacidade);
                float taxa = baterias.Sum(b => b.Trabalho.TaxaMax);

                float fracao;
                float saldo = gera - pede;
                if (saldo >= 0)
                {
                    fracao = 1;
                    // Sobra vai pras baterias (dividida pelo espaço livre de cada uma)
                    float guardar = Math.Min(saldo, taxa);
                    float livre = cap - carga;
                    if (livre > 0 && guardar > 0)
                        foreach (var b in baterias)
                        {
                            float sua = (b.Trabalho.Capacidade - b.Carga) / livre * guardar;
                            b.Carga = Math.Min(b.Trabalho.Capacidade, b.Carga + sua * dt);
                        }
                }
                else
                {
                    float falta = -saldo;
                    float tirar = Math.Min(Math.Min(falta, taxa), carga / Math.Max(dt, 0.001f));
                    if (carga > 0 && tirar > 0)
                        foreach (var b in baterias)
                        {
                            float sua = b.Carga / carga * tirar;
                            b.Carga = Math.Max(0, b.Carga - sua * dt);
                        }
                    fracao = pede > 0 ? GameMath.Clamp((gera + tirar) / pede, 0, 1) : 1;
                }

                bool tem = gera > 0.01f || baterias.Any(b => b.Carga > 0.5f);
                foreach (var m in maquinas) m.Energia = m.Quer && m.Ligada ? fracao : (tem ? 1 : 0);
                foreach (var b in rede.Pecas.Concat(rede.Postes)) b.Energizado = tem;

                rede.Gerando = gera;
                rede.Pedindo = pede;
                rede.Carga = baterias.Sum(b => b.Carga);
                rede.Capacidade = cap;
                foreach (var p in rede.Postes) Resumo[p.Pos] = rede;
                // Cópia do resumo em cada peça (o cliente lê daqui: poste, painel)
                foreach (var b in rede.Pecas.Concat(rede.Postes))
                {
                    b.Dados.SetFloat("rGera", gera);
                    b.Dados.SetFloat("rPede", pede);
                    b.Dados.SetFloat("rCarga", rede.Carga);
                    b.Dados.SetFloat("rCap", cap);
                    b.Dados.SetInt("rPostes", rede.Postes.Count);
                    b.Dados.SetInt("rPecas", rede.Pecas.Count);
                    b.Dados.SetInt("rParadas", maquinas.Count(x => x.Quer && x.Energia < 0.99f));
                }
            }
            foreach (var b in todas) b.MarkDirty(false);
        }

        static float SafeGerar(BEMaquina b)
        {
            try { return Math.Max(0, b.Trabalho.Gerar(b)); }
            catch { return 0; }
        }

        /// <summary>Manda pro jogador o caminho da energia da rede deste poste (botão "Ver conexões").</summary>
        public void MandarConexoes(BEMaquina poste, IServerPlayer player)
        {
            if (player == null) return;
            var rede = RedeDa(poste);
            var pk = new PacoteConexoes();
            if (rede != null)
            {
                Vec3d Topo(BEMaquina b) => b.Pos.ToVec3d().Add(0.5, b.Trabalho.Tipo == "poste" ? 1.85 : 0.8, 0.5);
                // poste -> poste (árvore pelo mais perto)
                var ligados = new List<BEMaquina> { rede.Postes[0] };
                var faltam = rede.Postes.Skip(1).ToList();
                while (faltam.Count > 0)
                {
                    BEMaquina a = null, b = null;
                    double md = double.MaxValue;
                    foreach (var x in ligados)
                        foreach (var y in faltam)
                        {
                            if (!Alcanca(x.Pos, y.Pos)) continue;
                            double d = x.Pos.DistanceSqTo(y.Pos.X, y.Pos.Y, y.Pos.Z);
                            if (d < md) { md = d; a = x; b = y; }
                        }
                    if (b == null) break;
                    Add(pk, Topo(a), Topo(b));
                    ligados.Add(b);
                    faltam.Remove(b);
                }
                // peça -> poste dela
                foreach (var b in rede.Pecas)
                {
                    var p = rede.Postes.Where(x => Alcanca(x.Pos, b.Pos)).OrderBy(x => x.Pos.DistanceSqTo(b.Pos.X, b.Pos.Y, b.Pos.Z)).FirstOrDefault();
                    if (p == null) continue;
                    if (b.Trabalho.Tipo == "fonte") Add(pk, Topo(b), Topo(p)); else Add(pk, Topo(p), Topo(b));
                }
            }
            sapi.Network.GetChannel("automacao-rede").SendPacket(pk, player);
        }

        static void Add(PacoteConexoes pk, Vec3d a, Vec3d b)
        {
            pk.Linhas.AddRange(new[] { a.X, a.Y, a.Z, b.X, b.Y, b.Z });
        }
    }

    /// <summary>Lado do cliente: desenha o alcance do poste e as conexões por alguns segundos.</summary>
    public static class RedeCliente
    {
        static ICoreClientAPI capi;
        const int Slot = 7731;
        static BlockPos alcanceDe;
        static List<double> linhas;
        static long linhasAte;

        public static void Iniciar(ICoreClientAPI api)
        {
            capi = api;
            api.Event.RegisterGameTickListener(_ => Particulas(), 100);
        }

        public static bool MostrandoAlcance(BEMaquina be) => alcanceDe != null && alcanceDe.Equals(be.Pos);

        public static void AlternarAlcance(BEMaquina be, int raio)
        {
            if (MostrandoAlcance(be)) { Limpar(); return; }
            alcanceDe = be.Pos.Copy();
            var ba = capi.World.BlockAccessor;
            var blocks = new List<BlockPos>();
            var colors = new List<int>();
            int cor = ColorUtil.ToRgba(120, 255, 232, 111);
            for (int dx = -raio; dx <= raio; dx++)
                for (int dz = -raio; dz <= raio; dz++)
                {
                    if (Math.Abs(dx) != raio && Math.Abs(dz) != raio) continue;
                    for (int dy = 6; dy >= -8; dy--)
                    {
                        var p = new BlockPos(be.Pos.X + dx, be.Pos.Y + dy, be.Pos.Z + dz, be.Pos.dimension);
                        var b = ba.GetBlock(p);
                        if (b.Id == 0 || b.CollisionBoxes == null || b.CollisionBoxes.Length == 0) continue;
                        blocks.Add(p);
                        colors.Add(cor);
                        break;
                    }
                }
            capi.World.HighlightBlocks(capi.World.Player, Slot, blocks, colors, EnumHighlightBlocksMode.Absolute, EnumHighlightShape.Arbitrary);
        }

        public static void Esquecer(BEMaquina be)
        {
            if (capi != null && MostrandoAlcance(be)) Limpar();
        }

        static void Limpar()
        {
            alcanceDe = null;
            capi?.World.HighlightBlocks(capi.World.Player, Slot, new List<BlockPos>(), new List<int>());
        }

        public static void MostrarConexoes(PacoteConexoes pk)
        {
            linhas = pk.Linhas;
            linhasAte = capi.World.ElapsedMilliseconds + 8000;
        }

        static readonly SimpleParticleProperties faisca = new SimpleParticleProperties(
            1, 1, ColorUtil.ToRgba(255, 255, 232, 111), new Vec3d(), new Vec3d(), new Vec3f(), new Vec3f(), 0.6f, 0, 0.25f, 0.35f, EnumParticleModel.Cube)
        { VertexFlags = 200, WithTerrainCollision = false };

        static void Particulas()
        {
            if (linhas == null || capi.World.ElapsedMilliseconds > linhasAte) { linhas = null; return; }
            float k = (capi.World.ElapsedMilliseconds % 1000) / 1000f;
            for (int i = 0; i + 5 < linhas.Count; i += 6)
            {
                var a = new Vec3d(linhas[i], linhas[i + 1], linhas[i + 2]);
                var b = new Vec3d(linhas[i + 3], linhas[i + 4], linhas[i + 5]);
                double len = a.DistanceTo(b);
                int n = Math.Max(2, (int)(len * 1.5));
                for (int j = 0; j < n; j++)
                {
                    double t = ((double)j / n + k / n * 3) % 1;
                    var p = new Vec3d(a.X + (b.X - a.X) * t, a.Y + (b.Y - a.Y) * t + Math.Sin(t * Math.PI) * 0.6, a.Z + (b.Z - a.Z) * t);
                    faisca.MinPos = p;
                    capi.World.SpawnParticles(faisca);
                }
            }
        }
    }
}
