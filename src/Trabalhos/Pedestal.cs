using System;
using System.Collections.Generic;
using System.Linq;
using Vintagestory.API.Client;
using Vintagestory.API.Common;
using Vintagestory.API.Config;
using Vintagestory.API.MathTools;
using Vintagestory.API.Server;
using Vintagestory.GameContent;

namespace Automacao
{
    /// <summary>
    /// Pedestal do Raio: guarda 1 Engrenagem Enferrujada no berço. Em tempestade puxa pra ele os raios de verdade
    /// do jogo que caem por perto (desvia o ponto de impacto) e, quando o raio cai, a enferrujada vira Temporal.
    /// Sem energia. A engrenagem fica no espaço 0 do bauzinho (sem janela: entra e sai pelo clique).
    /// </summary>
    public class TrabalhoPedestalRaio : Trabalho
    {
        public override string Code => "pedestal_raio";
        public override string Tipo => "pedestal";

        /// <summary>Distância (pra cada lado, no plano) de onde o pedestal puxa o raio.</summary>
        public const int Alcance = 256;

        static readonly AssetLocation Ferrugem = new AssetLocation("game", "gear-rusty");
        static readonly AssetLocation Temporal = new AssetLocation("game", "gear-temporal");

        /// <summary>Pedestais carregados no servidor (o desvio do raio procura aqui).</summary>
        internal static readonly HashSet<BEMaquina> Carregados = new HashSet<BEMaquina>();

        static ItemSlot Berco(BEMaquina m) => m.Inventory[0];
        public static bool TemFerrugem(BEMaquina m) => Berco(m).Itemstack?.Collectible?.Code?.Equals(Ferrugem) == true;
        static bool TemTemporal(BEMaquina m) => Berco(m).Itemstack?.Collectible?.Code?.Equals(Temporal) == true;

        /// <summary>Nada em cima: o raio do jogo cai no bloco mais alto da coluna, então tem que ser o próprio pedestal.</summary>
        public static bool CeuAberto(BEMaquina m) => m.Api.World.BlockAccessor.GetRainMapHeightAt(m.Pos.X, m.Pos.Z) <= m.Pos.Y;

        public override void Inicializar(BEMaquina m)
        {
            if (m.Api.Side == EnumAppSide.Server) Carregados.Add(m);
        }

        public override void Removido(BEMaquina m) => Carregados.Remove(m);

        public override string Modo(BEMaquina m) => TemFerrugem(m) ? "enferrujada" : TemTemporal(m) ? "temporal" : "vazio";

        public override bool Interagir(BEMaquina m, IPlayer p, BlockSelection sel)
        {
            var mao = p.InventoryManager.ActiveHotbarSlot;
            var berco = Berco(m);

            // Mão vazia: tira o que estiver no berço
            if (mao == null || mao.Empty)
            {
                if (berco.Empty) { Mao.Erro(m, Code); return true; }
                if (m.Api.Side != EnumAppSide.Server) return true;
                var st = berco.TakeOutWhole();
                berco.MarkDirty();
                Mao.Dar(m, p, st);
                m.Som("game:sounds/effect/latch", 0.5f);
                Atualizar(m);
                return true;
            }

            // Engrenagem Enferrujada na mão: encaixa (só 1)
            if (mao.Itemstack.Collectible.Code.Equals(Ferrugem))
            {
                if (!berco.Empty) { if (m.Api is ICoreClientAPI) Mao.Erro(m, Code); return true; }
                if (m.Api.Side != EnumAppSide.Server) return true;
                berco.Itemstack = mao.TakeOut(1);
                mao.MarkDirty();
                berco.MarkDirty();
                m.Som("game:sounds/effect/latch", 0.6f);
                Atualizar(m);
                return true;
            }

            Mao.Erro(m, Code);
            return true;
        }

        static void Atualizar(BEMaquina m)
        {
            m.ModoAtual = m.Trabalho.Modo(m);
            m.MarkDirty(true);
        }

        /// <summary>O raio caiu no pedestal: a enferrujada vira temporal.</summary>
        public static void Atingido(BEMaquina m)
        {
            if (m.Api?.Side != EnumAppSide.Server || !TemFerrugem(m)) return;
            var item = m.Api.World.GetItem(Temporal);
            if (item == null) return;
            Berco(m).Itemstack = new ItemStack(item);
            Berco(m).MarkDirty();
            m.Feitos++;
            m.Som("game:sounds/effect/translocate-active", 0.8f, 24);
            AvisarTodos(m);
            Atualizar(m);
        }

        /// <summary>Avisa no chat todo mundo online (o raio pode cair longe de quem está esperando), com distância e direção.</summary>
        static void AvisarTodos(BEMaquina m)
        {
            var centro = m.Pos.ToVec3d().Add(0.5, 0.5, 0.5);
            foreach (var p in m.Api.World.AllOnlinePlayers.OfType<IServerPlayer>())
            {
                string lc = p.LanguageCode;
                string onde = "";
                if (p.Entity != null)
                {
                    double dx = centro.X - p.Entity.Pos.X, dz = centro.Z - p.Entity.Pos.Z;
                    int dist = (int)Math.Round(Math.Sqrt(dx * dx + dz * dz));
                    onde = dist < 8 ? Lang.GetL(lc, "automacao:fala-pedestal-aqui")
                        : Lang.GetL(lc, "automacao:fala-pedestal-longe", dist, Lang.GetL(lc, "automacao:rumo-" + Rumo(dx, dz)));
                }
                p.SendMessage(GlobalConstants.GeneralChatGroup,
                    $"<strong>{Lang.GetL(lc, "automacao:block-pedestal_raio")}:</strong> {Lang.GetL(lc, "automacao:fala-pedestal-virou")}{onde}",
                    EnumChatType.Notification);
            }
        }

        /// <summary>Rumo de 8 pontas (o norte do jogo é -Z).</summary>
        static string Rumo(double dx, double dz)
        {
            string[] r = { "l", "se", "s", "so", "o", "no", "n", "ne" };
            double ang = Math.Atan2(dz, dx) * GameMath.RAD2DEG;
            return r[((int)Math.Round(ang / 45) % 8 + 8) % 8];
        }

        public override string Info(BEMaquina m)
        {
            if (TemTemporal(m)) return Mao.L("info-pedestal-pronta");
            if (!TemFerrugem(m)) return Mao.L("info-pedestal-vazio");
            if (!CeuAberto(m)) return Mao.L("info-pedestal-coberto");
            return Mao.L("info-pedestal-esperando", Alcance) + "\n" + Clima(m);
        }

        /// <summary>
        /// Chance de raio, com as mesmas contas do jogo (WeatherSimulationRegion.TickEvery25ms): a cada 200 ms cada
        /// região sorteia um raio com chance LightningRate, se no CENTRO dela fizer o calor mínimo e houver nuvem
        /// (RainCloudOverlay > 0,15); o raio cai num ponto qualquer a até 200 blocos do centro. O pedestal pega o que
        /// cair a até <see cref="Alcance"/> blocos — inclusive raio das regiões vizinhas.
        /// Sem trovoada, mostra quando o tempo muda e a chance da próxima ser trovoada com raio.
        /// </summary>
        static string Clima(BEMaquina m)
        {
            try
            {
                var clima = m.Api.ModLoader.GetModSystem<WeatherSystemBase>();
                var ba = m.Api.World.BlockAccessor;
                int tam = ba.RegionSize;
                int rx = m.Pos.X / tam, rz = m.Pos.Z / tam;
                if (!clima.weatherSimByMapRegion.TryGetValue(clima.MapRegionIndex2D(rx, rz), out var aqui) || aqui?.CurWeatherEvent == null) return "";

                // Raios por minuto que caem no alcance (soma da região do pedestal e das 8 vizinhas)
                double porMinuto = 0;
                for (int dx = -1; dx <= 1; dx++)
                    for (int dz = -1; dz <= 1; dz++)
                    {
                        if (!clima.weatherSimByMapRegion.TryGetValue(clima.MapRegionIndex2D(rx + dx, rz + dz), out var sim) || sim?.CurWeatherEvent == null) continue;
                        var ev = sim.CurWeatherEvent.State;
                        if (ev.LightningRate <= 0) continue;
                        var cc = CentroClima(m, rx + dx, rz + dz, tam);
                        if (cc == null || cc.Temperature < ev.LightningMinTemp || cc.RainCloudOverlay <= 0.15f) continue;
                        double cx = (rx + dx) * tam + tam / 2, cz = (rz + dz) * tam + tam / 2;
                        porMinuto += 300 * ev.LightningRate * Cobre(m.Pos.X + 0.5 - cx) * Cobre(m.Pos.Z + 0.5 - cz);
                    }

                var lin = new List<string>();
                double horasAte = aqui.CurWeatherEvent.State.ActiveUntilTotalHours - m.Api.World.Calendar.TotalHours;
                if (porMinuto > 0)
                {
                    int pct = Pct(1 - Math.Exp(-porMinuto));
                    lin.Add(Mao.L("info-pedestal-chance", pct, (int)Math.Round(60 / porMinuto)));
                    if (horasAte > 0) lin.Add(Mao.L("info-pedestal-dura", Horas(horasAte)));
                    return string.Join("\n", lin);
                }

                // Sem raio agora: diz o porquê (olhando a região do pedestal)
                var st = aqui.CurWeatherEvent.State;
                var centro = CentroClima(m, rx, rz, tam);
                if (st.LightningRate <= 0) lin.Add(Mao.L("info-pedestal-semtrovoada"));
                else if (centro != null && centro.Temperature < st.LightningMinTemp) lin.Add(Mao.L("info-pedestal-frio", (int)centro.Temperature, (int)st.LightningMinTemp));
                else lin.Add(Mao.L("info-pedestal-semnuvem"));

                int prox = Pct(ChanceProximaTrovoada(aqui, centro));
                lin.Add(horasAte > 0 ? Mao.L("info-pedestal-proxima", Horas(horasAte), prox) : Mao.L("info-pedestal-proxima-ja", prox));
                return string.Join("\n", lin);
            }
            catch { return ""; }
        }

        /// <summary>Clima no centro da região, na altura da chuva (é onde o jogo confere calor e nuvem).</summary>
        static ClimateCondition CentroClima(BEMaquina m, int rx, int rz, int tam)
        {
            var ba = m.Api.World.BlockAccessor;
            var c = new BlockPos(rx * tam + tam / 2, 0, rz * tam + tam / 2);
            c.Y = ba.GetRainMapHeightAt(c);
            if (c.Y == 0) c.Y = m.Api.World.SeaLevel;
            return ba.GetClimateAt(c, EnumGetClimateMode.NowValues);
        }

        /// <summary>Parte (0–1) do quadrado de ±200 blocos onde o raio cai que fica dentro do alcance, num eixo.</summary>
        static double Cobre(double distCentro) => GameMath.Clamp(200 + Alcance - Math.Abs(distCentro), 0, 400) / 400.0;

        /// <summary>
        /// Chance do próximo tempo ser trovoada com raio. Imita WeatherSimulationRegion.RandomWeatherEvent — que soma os
        /// pesos ajustados ao clima mas desconta o peso cheio de cada um — e o re-sorteio quando sai um tempo que não
        /// pode acontecer ali (ShouldStop).
        /// </summary>
        static double ChanceProximaTrovoada(WeatherSimulationRegion sim, ClimateCondition c)
        {
            var evs = sim.WeatherEvents;
            if (evs == null || evs.Length == 0 || c == null) return 0;
            float total = 0;
            foreach (var e in evs) total += e.config.getWeight(c.WorldgenRainfall, c.Temperature);
            if (total <= 0) return 0;
            double acum = 0, valido = 0, raio = 0;
            for (int i = 0; i < evs.Length; i++)
            {
                double antes = Math.Min(acum, total);
                acum += evs[i].config.Weight;
                double p = (i == evs.Length - 1 ? total : Math.Min(acum, total)) - antes;
                if (p <= 0) continue;
                if (evs[i].AllowStop && evs[i].config.getWeight(c.Rainfall, c.Temperature) <= 0) continue;
                valido += p;
                var l = evs[i].config.Lightning;
                if (l != null && l.LightningRate > 0 && c.Temperature >= l.MinTemperature) raio += p;
            }
            return valido > 0 ? raio / valido : 0;
        }

        static int Pct(double p) => p <= 0 ? 0 : Math.Max(1, Math.Min(100, (int)Math.Round(p * 100)));

        static string Horas(double h) => h < 1 ? Mao.L("info-pedestal-menos1h") : Mao.L("info-pedestal-horas", (int)Math.Round(h));
    }

    /// <summary>Desvia os raios do jogo pro Pedestal do Raio mais perto que esteja esperando um.</summary>
    public class PedestalRaioSistema : ModSystem
    {
        ICoreServerAPI sapi;

        public override bool ShouldLoad(EnumAppSide side) => side == EnumAppSide.Server;

        public override void StartServerSide(ICoreServerAPI api)
        {
            sapi = api;
            var clima = api.ModLoader.GetModSystem<WeatherSystemServer>();
            if (clima != null) clima.OnLightningImpactBegin += AoCairRaio;
            else api.Logger.Warning("[Automação] sem sistema de clima: o Pedestal do Raio não vai funcionar");
        }

        void AoCairRaio(ref Vec3d pos, ref EnumHandling handling)
        {
            if (handling != EnumHandling.PassThrough) return;
            BEMaquina alvo = null;
            double melhor = double.MaxValue;
            // Chunk descarregado: o pedestal não está mais no mundo
            TrabalhoPedestalRaio.Carregados.RemoveWhere(m => m.Api == null || sapi.World.BlockAccessor.GetBlockEntity(m.Pos) != m);
            foreach (var m in TrabalhoPedestalRaio.Carregados)
            {
                if (!TrabalhoPedestalRaio.TemFerrugem(m) || !TrabalhoPedestalRaio.CeuAberto(m)) continue;
                double dx = m.Pos.X + 0.5 - pos.X, dz = m.Pos.Z + 0.5 - pos.Z;
                if (Math.Abs(dx) > TrabalhoPedestalRaio.Alcance || Math.Abs(dz) > TrabalhoPedestalRaio.Alcance) continue;
                double d = dx * dx + dz * dz;
                if (d < melhor) { melhor = d; alvo = m; }
            }
            if (alvo == null) return;

            // O raio vai cair no topo do pedestal (o jogo acha a altura pela coluna); converte quando ele chega
            pos = new Vec3d(alvo.Pos.X + 0.5, alvo.Pos.Y + 1, alvo.Pos.Z + 0.5);
            var p = alvo.Pos.Copy();
            sapi.Event.RegisterCallback(_ =>
            {
                if (sapi.World.BlockAccessor.GetBlockEntity(p) is BEMaquina m && m.Codigo == "pedestal_raio")
                    TrabalhoPedestalRaio.Atingido(m);
            }, 350);
        }

        public override void Dispose() => TrabalhoPedestalRaio.Carregados.Clear();
    }
}
