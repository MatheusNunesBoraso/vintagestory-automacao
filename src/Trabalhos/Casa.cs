using System;
using System.Collections.Generic;
using System.Linq;
using Vintagestory.API.Common;
using Vintagestory.API.Common.Entities;
using Vintagestory.API.Config;
using Vintagestory.API.MathTools;
using Vintagestory.API.Server;
using Vintagestory.GameContent;

namespace Automacao
{
    /// <summary>Coisinhas que as peças da casa usam em comum.</summary>
    static class CasaUtil
    {
        public static string L(string k, params object[] a) => Lang.Get("automacao:" + k, a);

        public static long Agora(BEMaquina m) => m.Api.World.ElapsedMilliseconds;

        /// <summary>Faiscazinha azul (mesma cor da energia) num ponto.</summary>
        public static void Faisca(BEMaquina m, Vec3d p, int qtd = 8)
        {
            var props = new SimpleParticleProperties(qtd, qtd, ColorUtil.ToRgba(255, 255, 232, 111),
                p.AddCopy(-0.15, -0.1, -0.15), p.AddCopy(0.15, 0.2, 0.15), new Vec3f(-1.5f, 0.5f, -1.5f), new Vec3f(1.5f, 2f, 1.5f),
                0.35f, 0.4f, 0.15f, 0.3f, EnumParticleModel.Cube) { VertexFlags = 200 };
            m.Api.World.SpawnParticles(props);
        }

        /// <summary>Cache de posições achadas na área (procurar a área toda todo segundo pesa).</summary>
        static readonly Dictionary<string, (long ms, List<BlockPos> lista)> cache = new Dictionary<string, (long, List<BlockPos>)>();

        public static List<BlockPos> Achar(BEMaquina m, string tipo, System.Func<BlockPos, Block, bool> teste, long validadeMs = 20000)
        {
            string k = tipo + "@" + m.Pos + "#" + m.Raio;
            long agora = Agora(m);
            if (cache.TryGetValue(k, out var c) && agora - c.ms < validadeMs) return c.lista;
            var lista = m.Procurar(teste);
            cache[k] = (agora, lista);
            return lista;
        }
    }

    // =====================================================================
    // ILUMINAÇÃO ELÉTRICA — acende sozinha quando escurece (a luz de verdade vem da variante "aceso")
    // =====================================================================
    public class TrabalhoLuz : Trabalho
    {
        public override string Code => "luz";
        public override float Consumo => 1f;
        public override float Intervalo => 30f;
        public override bool PrecisaEspaco => false;

        public override bool TemTrabalho(BEMaquina m) => !m.IsDay();

        public override string Modo(BEMaquina m)
        {
            if (!m.Ligada || !m.Energizado) return "parado";
            if (m.IsDay()) return "dia";
            return m.Energia > 0.05f ? "noite" : "parado";
        }

        public override string Info(BEMaquina m) => m.ModoAtual == "noite" ? CasaUtil.L("info-luz-acesa") : CasaUtil.L("info-luz-dia");
    }

    // =====================================================================
    // BOMBA D'ÁGUA E IRRIGADOR — puxa água e molha a lavoura da área (a terra nunca seca)
    // =====================================================================
    public class TrabalhoBomba : Trabalho
    {
        public override string Code => "bomba";
        public override float Consumo => 1f;
        public override float Intervalo => 8f;
        public override int RaioPadrao => 6;
        public override bool PrecisaEspaco => false;

        static bool TemAgua(BEMaquina m) => m.AguaEncostada() > 0 || m.AcharAgua(m.Pos.ToVec3d(), null, 1) != null &&
            m.AcharAgua(m.Pos.ToVec3d(), null, 1).DistanceTo(m.Pos) <= 3;

        static List<BlockPos> Lavouras(BEMaquina m) =>
            CasaUtil.Achar(m, "lavoura", (p, b) => b is BlockFarmland);

        public override bool TemTrabalho(BEMaquina m)
        {
            if (!TemAgua(m)) return false;
            var ba = m.Api.World.BlockAccessor;
            return Lavouras(m).Any(p => ba.GetBlockEntity(p) is BlockEntityFarmland f && f.MoistureLevel < 0.95f);
        }

        public override void Trabalhar(BEMaquina m)
        {
            var ba = m.Api.World.BlockAccessor;
            int n = 0;
            foreach (var p in Lavouras(m))
            {
                if (ba.GetBlockEntity(p) is not BlockEntityFarmland f || f.MoistureLevel >= 0.95f) continue;
                // Igual o regador do jogo: um tanto de "segundos regando" por canteiro
                f.WaterFarmland(1.5f, false);
                n++;
            }
            if (n > 0) m.Som("game:sounds/effect/watering", 0.4f, 16);
            m.Dados.SetInt("regados", n);
        }

        public override string Info(BEMaquina m)
        {
            if (m.Api.Side == EnumAppSide.Server && !TemAgua(m)) return CasaUtil.L("info-bomba-semagua");
            return CasaUtil.L("info-bomba", m.Dados.GetInt("regados"));
        }
    }

    // =====================================================================
    // GELADEIRA — com energia, a comida do bauzinho estraga 10x mais devagar
    // =====================================================================
    public class TrabalhoGeladeira : Trabalho
    {
        public override string Code => "geladeira";
        public override float Consumo => 3f;
        public override float Intervalo => 60f;
        public override bool PrecisaEspaco => false;
        const float Lentidao = 0.1f;

        public override void Inicializar(BEMaquina m)
        {
            // Liga no próprio inventário: o jogo pergunta a velocidade de estragar de cada item guardado
            m.Inventory.OnAcquireTransitionSpeed += (tipo, stack, mul) =>
            {
                if (tipo != EnumTransitionType.Perish && tipo != EnumTransitionType.Ripen) return mul;
                return Gelando(m) ? mul * Lentidao : mul;
            };
        }

        static bool Gelando(BEMaquina m) => m.Ligada && m.Trabalhando;

        static bool Estraga(BEMaquina m, ItemStack s)
        {
            var props = s?.Collectible?.GetTransitionableProperties(m.Api.World, s, null);
            return props != null && props.Any(p => p.Type == EnumTransitionType.Perish);
        }

        public override bool TemTrabalho(BEMaquina m) => m.TemNoBau(s => Estraga(m, s));

        public override string Info(BEMaquina m) => Gelando(m) ? CasaUtil.L("info-geladeira-ok") : CasaUtil.L("info-geladeira-quente");
    }

    // =====================================================================
    // AQUECEDOR — quando está frio, esquenta quem estiver perto (corpo não esfria dentro de casa)
    // =====================================================================
    public class TrabalhoAquecedor : Trabalho
    {
        public override string Code => "aquecedor";
        public override float Consumo => 3f;
        public override float Intervalo => 60f;
        public override int RaioPadrao => 6;
        public override bool PrecisaEspaco => false;

        static float TempAr(BEMaquina m) =>
            m.Api.World.BlockAccessor.GetClimateAt(m.Pos, EnumGetClimateMode.NowValues)?.Temperature ?? 20;

        public override bool TemTrabalho(BEMaquina m) => TempAr(m) < 16;

        public override void Tick(BEMaquina m, float dt)
        {
            if (!m.Trabalhando || m.Api.Side != EnumAppSide.Server) return;
            foreach (var pl in m.Api.World.AllOnlinePlayers)
            {
                var e = pl.Entity;
                if (e == null) continue;
                if (Math.Abs(e.Pos.X - m.Pos.X - 0.5) > m.Raio || Math.Abs(e.Pos.Z - m.Pos.Z - 0.5) > m.Raio || Math.Abs(e.Pos.Y - m.Pos.Y) > 4) continue;
                var bt = e.GetBehavior<EntityBehaviorBodyTemperature>();
                if (bt == null) continue;
                // Sobe devagar até a temperatura normal (como ficar perto de uma fogueira)
                if (bt.CurBodyTemperature < bt.NormalBodyTemperature)
                    bt.CurBodyTemperature = Math.Min(bt.NormalBodyTemperature, bt.CurBodyTemperature + 0.15f * dt * m.Energia);
            }
        }

        public override string Info(BEMaquina m)
        {
            if (m.Api.Side != EnumAppSide.Server) return null;
            float t = TempAr(m);
            return t < 16 ? CasaUtil.L("info-aquecedor-frio", (int)t) : CasaUtil.L("info-aquecedor-quente", (int)t);
        }
    }

    // =====================================================================
    // PORTÃO ELÉTRICO — abre sozinho pra jogador que chega perto, fecha quando todo mundo sai
    // (bicho e drifter não abrem). Sem energia: abre e fecha na mão.
    // =====================================================================
    public class TrabalhoPortao : Trabalho
    {
        public override string Code => "portao";
        public override float Consumo => 2f;
        public override float Intervalo => 60f;
        public override bool PrecisaEspaco => false;
        const double Perto = 3.5;

        static bool Aberto(BEMaquina m) => m.Dados.GetBool("aberto");
        static bool Mexendo(BEMaquina m) => CasaUtil.Agora(m) < m.Dados.GetLong("mexendoAte");

        static bool JogadorPerto(BEMaquina m)
        {
            // O portão tem 2 blocos de largura: mede do meio dele
            var c = m.Pos.ToVec3d().Add(0.5, 0.5, 0.5);
            return m.Api.World.AllOnlinePlayers.Any(p => p.Entity != null && p.Entity.Alive &&
                p.Entity.Pos.SquareDistanceTo(c) < (Perto + 0.5) * (Perto + 0.5));
        }

        void Mexer(BEMaquina m, bool abrir)
        {
            m.Dados.SetBool("aberto", abrir);
            m.Dados.SetLong("mexendoAte", CasaUtil.Agora(m) + 2500);
            m.Som("game:sounds/effect/latch", 0.7f, 16);
            m.MarkDirty(true);
        }

        public override void Tick(BEMaquina m, float dt)
        {
            if (m.Api.Side != EnumAppSide.Server || !m.Ligada || !m.Energizado) return;
            bool quer = JogadorPerto(m);
            if (quer != Aberto(m)) Mexer(m, quer);
        }

        public override bool TemTrabalho(BEMaquina m) => Mexendo(m);

        public override string Estado(BEMaquina m) => Aberto(m) ? "aberto" : "fechado";

        public override string Modo(BEMaquina m)
        {
            if (!m.Energizado) return "parado";
            return Mexendo(m) ? "abrindo" : "fechado";
        }

        public override bool Interagir(BEMaquina m, IPlayer p, BlockSelection sel)
        {
            // Com energia ele se vira sozinho (abre a janela); sem energia, é um portão comum
            if (m.Energizado && m.Ligada) return false;
            if (m.Api.Side == EnumAppSide.Server) Mexer(m, !Aberto(m));
            return true;
        }

        public override string Info(BEMaquina m) =>
            (Aberto(m) ? CasaUtil.L("info-portao-aberto") : CasaUtil.L("info-portao-fechado")) +
            (m.Energizado ? "" : "\n" + CasaUtil.L("info-portao-manual"));
    }

    // =====================================================================
    // CERCA ELÉTRICA — choquinho que empurra (e machuca um pouco) os bichos bravos; assusta os pequenos
    // =====================================================================
    public class TrabalhoCerca : Trabalho
    {
        public override string Code => "cerca";
        public override float Consumo => 1f;
        public override float Intervalo => 60f;
        public override bool PrecisaEspaco => false;

        static readonly string[] Bravos = { "drifter", "wolf", "bear", "hyena", "pig-wild", "boar", "locust", "bowtorn", "shiver", "bell", "jackal", "deer-" };
        static readonly string[] Pequenos = { "hare", "fox", "raccoon", "gazelle", "chicken-wild", "rabbit" };

        public override bool TemTrabalho(BEMaquina m) => true;

        public override void Tick(BEMaquina m, float dt)
        {
            if (m.Api.Side != EnumAppSide.Server || !m.Trabalhando) return;
            var centro = m.Pos.ToVec3d().Add(0.5, 0.5, 0.5);
            var achados = m.Api.World.GetEntitiesAround(centro, 1.8f, 2f, e => e.Alive && e is not EntityPlayer && !(e is EntityItem));
            foreach (var e in achados)
            {
                string code = e.Code?.Path ?? "";
                bool bravo = Bravos.Any(b => code.StartsWith(b) || code.Contains(b));
                bool pequeno = Pequenos.Any(b => code.StartsWith(b));
                if (!bravo && !pequeno) continue;
                // Empurra pra longe do mourão
                var dir = e.ServerPos.XYZ.Sub(centro);
                dir.Y = 0;
                double len = Math.Max(0.1, dir.Length());
                e.ServerPos.Motion.Add(dir.X / len * 0.35, 0.15, dir.Z / len * 0.35);
                if (bravo)
                    e.ReceiveDamage(new DamageSource { Source = EnumDamageSource.Block, SourceBlock = m.Block, SourcePos = centro, Type = EnumDamageType.Electricity }, 1.5f);
                CasaUtil.Faisca(m, e.ServerPos.XYZ.Add(0, e.SelectionBox.Y2 / 2, 0));
                m.Som("game:sounds/effect/fuse", 0.5f, 16);
                m.Dados.SetInt("choques", m.Dados.GetInt("choques") + 1);
            }
            // Faísca de vez em quando, só pra mostrar que está ligada
            if (m.Api.World.Rand.NextDouble() < 0.04) CasaUtil.Faisca(m, centro.AddCopy(0, 0.5, 0), 3);
        }

        public override string Info(BEMaquina m) => CasaUtil.L("info-cerca", m.Dados.GetInt("choques"));
    }

    // =====================================================================
    // ELEVADOR — estações na mesma coluna se ligam sozinhas; leva você ou só o bauzinho
    // (substitui o mod Dumbwaiter)
    // =====================================================================
    public class TrabalhoElevador : Trabalho, IAcoes
    {
        public override string Code => "elevador";
        public override float Consumo => 8f;
        public override float Intervalo => 60f;
        public override bool PrecisaEspaco => false;
        const int Alcance = 128;

        static bool Viajando(BEMaquina m) => CasaUtil.Agora(m) < m.Dados.GetLong("viajandoAte");

        static List<int> Estacoes(BEMaquina m)
        {
            string s = m.Dados.GetString("estacoes", "");
            return s.Split(',', StringSplitOptions.RemoveEmptyEntries).Select(int.Parse).ToList();
        }

        static BEMaquina EstacaoEm(BEMaquina m, int y) =>
            m.Api.World.BlockAccessor.GetBlockEntity(new BlockPos(m.Pos.X, y, m.Pos.Z, m.Pos.dimension)) is BEMaquina be && be.Codigo == "elevador" ? be : null;

        public override void Tick(BEMaquina m, float dt)
        {
            if (m.Api.Side != EnumAppSide.Server) return;
            // Procura as outras estações da coluna de vez em quando
            long agora = CasaUtil.Agora(m);
            if (agora - m.Dados.GetLong("procurouEm") < 5000) return;
            m.Dados.SetLong("procurouEm", agora);
            var ys = new List<int>();
            var ba = m.Api.World.BlockAccessor;
            int maxY = ba.MapSizeY - 1;
            var tmp = new BlockPos(m.Pos.X, 0, m.Pos.Z, m.Pos.dimension);
            for (int y = Math.Max(1, m.Pos.Y - Alcance); y <= Math.Min(maxY, m.Pos.Y + Alcance); y++)
            {
                if (y == m.Pos.Y) continue;
                tmp.Y = y;
                if (ba.GetBlock(tmp)?.Code?.Domain == "automacao" && ba.GetBlock(tmp).Code.Path.StartsWith("elevador")) ys.Add(y);
            }
            string novo = string.Join(",", ys);
            if (novo != m.Dados.GetString("estacoes", "")) { m.Dados.SetString("estacoes", novo); m.MarkDirty(true); }
        }

        public override bool TemTrabalho(BEMaquina m) => Viajando(m);

        public override string Modo(BEMaquina m)
        {
            if (Viajando(m)) return "subindo";
            return m.Energizado ? "ligado" : "parado";
        }

        public IEnumerable<(string code, string texto)> Botoes(BEMaquina m)
        {
            foreach (int y in Estacoes(m).OrderByDescending(y => y))
            {
                bool sobe = y > m.Pos.Y;
                yield return ("ir:" + y, CasaUtil.L(sobe ? "elev-subir" : "elev-descer", y, Math.Abs(y - m.Pos.Y)));
            }
            foreach (int y in Estacoes(m).OrderByDescending(y => y))
                yield return ("mandar:" + y, CasaUtil.L("elev-mandar", y));
        }

        public void Acao(BEMaquina m, IPlayer p, string acao)
        {
            var sp = p as IServerPlayer;
            void Avisar(string k, params object[] a) => sp?.SendMessage(GlobalConstants.GeneralChatGroup, CasaUtil.L(k, a), EnumChatType.Notification);
            var partes = acao.Split(':');
            if (partes.Length != 2 || !int.TryParse(partes[1], out int y)) return;
            if (!m.Energizado || !m.Ligada) { Avisar("elev-semenergia"); return; }
            var alvo = EstacaoEm(m, y);
            if (alvo == null) { Avisar("elev-naoachou", y); return; }

            long ate = CasaUtil.Agora(m) + 6000;
            m.Dados.SetLong("viajandoAte", ate);
            alvo.Dados.SetLong("viajandoAte", ate);

            if (partes[0] == "ir")
            {
                var e = p.Entity;
                if (e == null) return;
                CasaUtil.Faisca(m, e.Pos.XYZ.Add(0, 1, 0), 20);
                m.Som("game:sounds/effect/translocate-active", 0.6f, 16);
                e.TeleportTo(new Vec3d(alvo.Pos.X + 0.5, alvo.Pos.Y + 0.2, alvo.Pos.Z + 0.5));
                alvo.Som("game:sounds/effect/translocate-active", 0.6f, 16);
                CasaUtil.Faisca(alvo, alvo.Pos.ToVec3d().Add(0.5, 1, 0.5), 20);
            }
            else if (partes[0] == "mandar")
            {
                var carga = new List<ItemStack>();
                foreach (var slot in m.Inventory)
                {
                    if (slot.Empty) continue;
                    carga.Add(slot.TakeOutWhole());
                    slot.MarkDirty();
                }
                if (carga.Count == 0) { Avisar("elev-bauvazio"); return; }
                alvo.Guardar(carga);
                m.Som("game:sounds/effect/gears", 0.6f, 16);
                alvo.Som("game:sounds/effect/gears", 0.6f, 16);
                Avisar("elev-mandou", y);
            }
            m.MarkDirty(true);
            alvo.MarkDirty(true);
        }

        public override string Info(BEMaquina m)
        {
            var ests = Estacoes(m);
            return ests.Count == 0 ? CasaUtil.L("info-elev-sozinho") : CasaUtil.L("info-elev", ests.Count, string.Join(", ", ests.OrderByDescending(y => y)));
        }
    }

    // =====================================================================
    // CHOCADEIRA — ovos de galinha no bauzinho viram pintinho depois de ~3 dias de jogo com energia
    // =====================================================================
    public class TrabalhoChocadeira : Trabalho
    {
        public override string Code => "chocadeira";
        public override float Consumo => 1f;
        public override float Intervalo => 60f;
        public override bool PrecisaEspaco => false;
        const double HorasPraChocar = 72;

        static bool Ovo(ItemStack s) => s?.Collectible?.Code?.Path == "egg-chicken-raw";

        public override bool TemTrabalho(BEMaquina m) => m.TemNoBau(Ovo);

        public override void Tick(BEMaquina m, float dt)
        {
            if (m.Api.Side != EnumAppSide.Server) return;
            double agora = m.Api.World.Calendar.TotalHours;
            double ultima = m.Dados.GetDouble("ultH", agora);
            m.Dados.SetDouble("ultH", agora);
            if (!m.Trabalhando) return;
            double horas = m.Dados.GetDouble("horas") + Math.Max(0, agora - ultima);
            if (horas >= HorasPraChocar)
            {
                horas = 0;
                if (m.TirarDoBau(Ovo, 1).Count > 0) Nascer(m);
            }
            m.Dados.SetDouble("horas", horas);
        }

        static void Nascer(BEMaquina m)
        {
            var w = m.Api.World;
            var tipo = w.GetEntityType(new AssetLocation("game", "chicken-baby"));
            if (tipo == null) return;
            var e = w.ClassRegistry.CreateEntity(tipo);
            // Sai pela frente da chocadeira
            var f = m.Frente;
            e.ServerPos.SetPos(m.Pos.X + 0.5 + f.Normali.X * 0.9, m.Pos.Y + 0.1, m.Pos.Z + 0.5 + f.Normali.Z * 0.9);
            e.Pos.SetFrom(e.ServerPos);
            w.SpawnEntity(e);
            m.Dados.SetLong("nasceuEm", CasaUtil.Agora(m));
            m.Som("game:sounds/creature/chicken/chick1", 0.8f, 16);
            m.Falar("chocadeira-nasceu", true);
        }

        public override string Modo(BEMaquina m)
        {
            if (CasaUtil.Agora(m) - m.Dados.GetLong("nasceuEm", -999999) < 20000) return "nasceu";
            return m.Trabalhando ? "ligado" : "parado";
        }

        public override string Info(BEMaquina m)
        {
            if (!m.TemNoBau(Ovo)) return CasaUtil.L("info-choc-semovo");
            double h = m.Dados.GetDouble("horas");
            return CasaUtil.L("info-choc", (int)(h / HorasPraChocar * 100), Math.Max(0, (HorasPraChocar - h) / 24).ToString("0.#"));
        }
    }

    // =====================================================================
    // PEDREIRA AUTOMÁTICA — cava um buraco 3x3 pra baixo, um bloco por vez, guardando tudo
    // =====================================================================
    public class TrabalhoPedreira : Trabalho
    {
        public override string Code => "pedreira";
        public override float Consumo => 8f;
        public override float Intervalo => 3f;

        static bool Cavavel(Block b) =>
            b != null && b.Id != 0 && !b.IsLiquid() && b.Code?.Path?.StartsWith("mantle") != true &&
            (b.BlockMaterial == EnumBlockMaterial.Stone || b.BlockMaterial == EnumBlockMaterial.Ore ||
             b.BlockMaterial == EnumBlockMaterial.Gravel || b.BlockMaterial == EnumBlockMaterial.Sand ||
             b.BlockMaterial == EnumBlockMaterial.Soil);

        /// <summary>Próximo bloco pra cavar (camada por camada). null = acabou (fundo, água, lava ou rocha do fundo).</summary>
        static BlockPos Proximo(BEMaquina m, out string porque)
        {
            porque = null;
            var ba = m.Api.World.BlockAccessor;
            int y = m.Dados.GetInt("y", m.Pos.Y - 1);
            var tmp = new BlockPos(m.Pos.dimension);
            for (; y >= 1; y--)
            {
                bool camadaTemAlgo = false;
                for (int dx = -1; dx <= 1; dx++)
                    for (int dz = -1; dz <= 1; dz++)
                    {
                        tmp.Set(m.Pos.X + dx, y, m.Pos.Z + dz);
                        var fluido = ba.GetBlock(tmp, BlockLayersAccess.Fluid);
                        if (fluido != null && fluido.IsLiquid()) { porque = "liquido"; return null; }
                        var b = ba.GetBlock(tmp);
                        if (b.Code?.Path?.StartsWith("mantle") == true) { porque = "fundo"; return null; }
                        if (Cavavel(b) && ba.GetBlockEntity(tmp) == null)
                        {
                            camadaTemAlgo = true;
                            m.Dados.SetInt("y", y);
                            return tmp.Copy();
                        }
                    }
                if (!camadaTemAlgo) m.Dados.SetInt("y", y - 1);
            }
            porque = "fundo";
            return null;
        }

        public override bool TemTrabalho(BEMaquina m)
        {
            var p = Proximo(m, out string porque);
            m.Dados.SetString("parou", porque ?? "");
            return p != null;
        }

        public override void Trabalhar(BEMaquina m)
        {
            var p = Proximo(m, out _);
            if (p == null) return;
            var w = m.Api.World;
            var b = w.BlockAccessor.GetBlock(p);
            var drops = b.GetDrops(w, p, null, 1f);
            w.BlockAccessor.SetBlock(0, p);
            w.BlockAccessor.TriggerNeighbourBlockUpdate(p);
            if (drops != null) m.Guardar(drops.Where(d => d != null));
            w.PlaySoundAt(new AssetLocation("game:sounds/effect/stonecrush"), p.X + 0.5, p.Y + 0.5, p.Z + 0.5, null, true, 16, 0.6f);
            m.Dados.SetInt("cavados", m.Dados.GetInt("cavados") + 1);
        }

        public override string Info(BEMaquina m)
        {
            int prof = m.Pos.Y - m.Dados.GetInt("y", m.Pos.Y - 1);
            string s = CasaUtil.L("info-pedreira", prof, m.Dados.GetInt("cavados"));
            string porque = m.Dados.GetString("parou", "");
            if (porque == "liquido") s += "\n" + CasaUtil.L("info-pedreira-agua");
            else if (porque == "fundo") s += "\n" + CasaUtil.L("info-pedreira-fundo");
            return s;
        }
    }

    // =====================================================================
    // SONDA DE MINÉRIO — lê o chunk inteiro embaixo dela e diz quanto tem de cada minério e em que fundura
    // =====================================================================
    public class TrabalhoSonda : Trabalho, IAcoes
    {
        public override string Code => "sonda";
        public override float Consumo => 3f;
        public override float Intervalo => 2f;
        public override bool PrecisaEspaco => false;
        const int CamadasPorCiclo = 6;

        public override bool TemTrabalho(BEMaquina m) => !m.Dados.GetBool("pronta");

        public override void Trabalhar(BEMaquina m)
        {
            var ba = m.Api.World.BlockAccessor;
            int y = m.Dados.GetInt("scanY", m.Pos.Y - 1);
            int cx = m.Pos.X / 16 * 16, cz = m.Pos.Z / 16 * 16;
            var achados = Ler(m);
            var tmp = new BlockPos(m.Pos.dimension);
            for (int n = 0; n < CamadasPorCiclo && y >= 1; n++, y--)
                for (int x = 0; x < 16; x++)
                    for (int z = 0; z < 16; z++)
                    {
                        tmp.Set(cx + x, y, cz + z);
                        var b = ba.GetBlock(tmp);
                        if (b?.Code == null || !b.Code.Path.StartsWith("ore-")) continue;
                        string tipo = b.Variant["type"] ?? b.Code.SecondCodePart();
                        int fundo = m.Pos.Y - y;
                        if (!achados.TryGetValue(tipo, out var a)) a = (0, fundo, fundo);
                        achados[tipo] = (a.qtd + 1, Math.Min(a.min, fundo), Math.Max(a.max, fundo));
                    }
            m.Dados.SetInt("scanY", y);
            if (y < 1)
            {
                m.Dados.SetBool("pronta", true);
                m.Som("game:sounds/effect/receptionbell", 0.6f, 16);
            }
            Gravar(m, achados);
        }

        static Dictionary<string, (int qtd, int min, int max)> Ler(BEMaquina m)
        {
            var d = new Dictionary<string, (int, int, int)>();
            foreach (var parte in m.Dados.GetString("minerios", "").Split(';', StringSplitOptions.RemoveEmptyEntries))
            {
                var c = parte.Split(':');
                if (c.Length == 4) d[c[0]] = (int.Parse(c[1]), int.Parse(c[2]), int.Parse(c[3]));
            }
            return d;
        }

        static void Gravar(BEMaquina m, Dictionary<string, (int qtd, int min, int max)> d) =>
            m.Dados.SetString("minerios", string.Join(";", d.Select(kv => $"{kv.Key}:{kv.Value.qtd}:{kv.Value.min}:{kv.Value.max}")));

        public IEnumerable<(string code, string texto)> Botoes(BEMaquina m)
        {
            yield return ("denovo", CasaUtil.L("sonda-denovo"));
        }

        public void Acao(BEMaquina m, IPlayer p, string acao)
        {
            if (acao != "denovo") return;
            m.Dados.RemoveAttribute("minerios");
            m.Dados.RemoveAttribute("scanY");
            m.Dados.SetBool("pronta", false);
        }

        public override string Info(BEMaquina m)
        {
            var d = Ler(m);
            int y = m.Dados.GetInt("scanY", m.Pos.Y - 1);
            string cab = m.Dados.GetBool("pronta") ? CasaUtil.L("info-sonda-pronta")
                : CasaUtil.L("info-sonda-lendo", Math.Max(0, (int)(100.0 * (m.Pos.Y - y) / Math.Max(1, m.Pos.Y))));
            if (d.Count == 0) return cab + "\n" + CasaUtil.L("info-sonda-nada");
            var linhas = d.OrderByDescending(kv => kv.Value.qtd).Take(12).Select(kv =>
            {
                string nome = Lang.GetIfExists("game:ore-" + kv.Key) ?? kv.Key;
                return CasaUtil.L("info-sonda-linha", nome, kv.Value.qtd, kv.Value.min, kv.Value.max);
            });
            return cab + "\n" + string.Join("\n", linhas);
        }
    }
}
