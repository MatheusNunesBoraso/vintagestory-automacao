using System;
using System.Collections.Generic;
using System.Linq;
using Vintagestory.API.Client;
using Vintagestory.API.Common;
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
            m.Falar("pedestal-virou", true);
            Atualizar(m);
        }

        public override string Info(BEMaquina m)
        {
            if (TemTemporal(m)) return Mao.L("info-pedestal-pronta");
            if (!TemFerrugem(m)) return Mao.L("info-pedestal-vazio");
            if (!CeuAberto(m)) return Mao.L("info-pedestal-coberto");
            return Mao.L("info-pedestal-esperando", Alcance) + "\n" + Clima(m);
        }

        /// <summary>
        /// O jogo só solta raio no evento de trovoada (heavythunder / lightthunder) e só com 12°C ou mais:
        /// chuva comum não tem raio. Diz pro jogador em qual caso está.
        /// </summary>
        static string Clima(BEMaquina m)
        {
            try
            {
                var clima = m.Api.ModLoader.GetModSystem<WeatherSystemBase>();
                int tam = m.Api.World.BlockAccessor.RegionSize;
                long idx = clima.MapRegionIndex2D(m.Pos.X / tam, m.Pos.Z / tam);
                if (!clima.weatherSimByMapRegion.TryGetValue(idx, out var sim) || sim?.CurWeatherEvent == null) return "";
                var ev = sim.CurWeatherEvent.State;
                if (ev.LightningRate <= 0) return Mao.L("info-pedestal-semtrovoada");
                float temp = m.Api.World.BlockAccessor.GetClimateAt(m.Pos, EnumGetClimateMode.NowValues)?.Temperature ?? 99;
                if (temp < ev.LightningMinTemp) return Mao.L("info-pedestal-frio", (int)temp, (int)ev.LightningMinTemp);
                return Mao.L("info-pedestal-trovoada");
            }
            catch { return ""; }
        }
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
