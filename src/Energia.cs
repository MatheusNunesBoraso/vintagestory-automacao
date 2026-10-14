using System;
using System.Linq;
using Vintagestory.API.Common;
using Vintagestory.API.Config;
using Vintagestory.API.MathTools;
using Vintagestory.GameContent;

namespace Automacao
{
    // =====================================================================
    // FONTES — quanto cada uma gera por segundo (E/s). Máquinas gastam 1 (pouco), 3 (médio), 8 (muito).
    // =====================================================================

    /// <summary>Roda Geradora: precisa de água encostada (do lado da roda). Mais água correndo = mais energia.</summary>
    public class TrabalhoRoda : Trabalho
    {
        public override string Code => "roda";
        public override string Tipo => "fonte";
        public override float Gerar(BEMaquina m)
        {
            int agua = m.AguaEncostada();
            if (agua == 0) return 0;
            // Água corrente (rio) gera mais que parada
            var ba = m.Api.World.BlockAccessor;
            bool corrente = BlockFacing.HORIZONTALS.Any(f =>
            {
                var b = ba.GetBlock(m.Pos.AddCopy(f), BlockLayersAccess.Fluid);
                return b?.Variant?["flow"] != null && b.Variant["flow"] != "still";
            });
            return Math.Min(8, 2 + agua) * (corrente ? 1.5f : 1f);
        }
        public override string Info(BEMaquina m) => m.AguaEncostada() == 0 ? Lang.Get("automacao:info-roda-semagua") : null;
    }

    /// <summary>Torre de Tempestade: chuva gira a turbininha; tempestade forte enche o garrafão (raio).</summary>
    public class TrabalhoTorre : Trabalho
    {
        public override string Code => "torre";
        public override string Tipo => "fonte";

        static float Chuva(BEMaquina m)
        {
            var ws = m.Api.ModLoader.GetModSystem<WeatherSystemBase>();
            if (ws == null) return 0;
            var p = m.Pos;
            float prec = ws.GetPrecipitation(p.X + 0.5, p.Y + 0.5, p.Z + 0.5);
            // só conta se o céu estiver aberto em cima
            int chuvaY = m.Api.World.BlockAccessor.GetRainMapHeightAt(p.X, p.Z);
            return chuvaY <= p.Y + 3 ? prec : 0;
        }

        public override float Gerar(BEMaquina m)
        {
            float c = Chuva(m);
            if (c < 0.05f) return 0;
            float g = 3 + c * 9;
            // Tempestade forte: de vez em quando "cai um raio" e o garrafão enche (rajada grande)
            if (c > 0.6f && m.Api.World.Rand.NextDouble() < 0.02)
            {
                g += 600;
                m.Dados.SetDouble("raioEm", m.Api.World.ElapsedMilliseconds);
                m.Som("game:sounds/weather/lightning-verynear", 0.5f, 48);
            }
            return g;
        }

        public override string Modo(BEMaquina m)
        {
            if (m.UltimaGeracao <= 0.01f) return "sol";
            bool raio = m.Api.World.ElapsedMilliseconds - m.Dados.GetDouble("raioEm", -99999) < 20000;
            return raio || m.UltimaGeracao > 9 ? "raio" : "chuva";
        }
    }

    /// <summary>Cata-vento: vento × altura. Quanto mais alto em relação ao nível do mar, mais.</summary>
    public class TrabalhoCatavento : Trabalho
    {
        public override string Code => "catavento";
        public override string Tipo => "fonte";
        public override float Gerar(BEMaquina m)
        {
            var ws = m.Api.ModLoader.GetModSystem<WeatherSystemBase>();
            if (ws == null) return 0;
            var vento = ws.WeatherDataSlowAccess.GetWindSpeed(m.Pos.ToVec3d());
            float altura = GameMath.Clamp((m.Pos.Y - m.Api.World.SeaLevel) / 40f, 0.3f, 1.6f);
            return (float)Math.Min(10, vento * 10 * altura);
        }
    }

    /// <summary>Painel Solar: de dia, céu aberto; menos quando nublado/chuva; mais no verão.</summary>
    public class TrabalhoSolar : Trabalho
    {
        public override string Code => "solar";
        public override string Tipo => "fonte";
        public override float Gerar(BEMaquina m)
        {
            var w = m.Api.World;
            int sol = w.BlockAccessor.GetLightLevel(m.Pos.UpCopy(), EnumLightLevelType.TimeOfDaySunLight);
            if (sol < 8) return 0;
            var ws = m.Api.ModLoader.GetModSystem<WeatherSystemBase>();
            float chuva = ws?.GetPrecipitation(m.Pos.X, m.Pos.Y, m.Pos.Z) ?? 0;
            var estacao = w.Calendar.GetSeason(m.Pos);
            float fe = estacao == EnumSeason.Summer ? 1.25f : estacao == EnumSeason.Winter ? 0.6f : 1f;
            return Math.Max(0, (sol - 7) / 15f * 6 * fe * (1 - chuva * 0.8f));
        }
        public override string Modo(BEMaquina m) => m.UltimaGeracao <= 0.01f ? "parado" : m.UltimaGeracao < 2.5f ? "nublado" : "ligado";
    }

    /// <summary>Gerador a Lenha: queima combustível do bauzinho (lenha, carvão, tábua...).</summary>
    public class TrabalhoGerador : Trabalho
    {
        public override string Code => "gerador";
        public override string Tipo => "fonte";
        public override bool Insumo(ItemStack s) => s?.Collectible?.CombustibleProps?.BurnDuration > 0;

        public override float Gerar(BEMaquina m)
        {
            double resta = m.Dados.GetDouble("queima");
            if (resta <= 0)
            {
                var c = m.TirarDoBau(Insumo, 1).FirstOrDefault();
                if (c == null) return 0;
                // Mais tempo e mais quente = mais energia: 1 lenha (~16 s no jogo) rende ~ 4 min aqui
                var props = c.Collectible.CombustibleProps;
                resta = props.BurnDuration * 15;
                m.Dados.SetDouble("forca", GameMath.Clamp(props.BurnTemperature / 140f, 3, 8));
            }
            m.Dados.SetDouble("queima", resta - 1);
            return (float)m.Dados.GetDouble("forca", 5);
        }

        public override string Info(BEMaquina m)
        {
            double r = m.Dados.GetDouble("queima");
            return r > 0 ? Lang.Get("automacao:info-gerador", (int)(r / 60) + 1) : Lang.Get("automacao:info-gerador-vazio");
        }
    }

    // =====================================================================
    // BATERIA E POSTE
    // =====================================================================
    public class TrabalhoBateria : Trabalho
    {
        public override string Code => "bateria";
        public override string Tipo => "bateria";
        public override float Capacidade => 20000;
        public override float TaxaMax => 40;
        public override bool PrecisaEspaco => false;
        public override string Modo(BEMaquina m)
        {
            float f = m.Carga / Capacidade;
            return f < 0.02f ? "vazia" : f < 0.7f ? "meia" : "cheia";
        }
    }

    public class TrabalhoPoste : Trabalho
    {
        public override string Code => "poste";
        public override string Tipo => "poste";
        public override bool PrecisaEspaco => false;
        public override string Info(BEMaquina m)
        {
            if (!m.Dados.HasAttribute("rGera")) return null;
            return Lang.Get("automacao:info-poste", m.Dados.GetFloat("rGera").ToString("0.#"), m.Dados.GetFloat("rPede").ToString("0.#"),
                (int)m.Dados.GetFloat("rCarga"), (int)m.Dados.GetFloat("rCap"), m.Dados.GetInt("rPostes"), m.Dados.GetInt("rPecas"));
        }
    }
}
