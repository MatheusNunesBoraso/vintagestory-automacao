using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Vintagestory.API.Common;
using Vintagestory.API.Common.Entities;
using Vintagestory.API.Config;
using Vintagestory.API.MathTools;
using Vintagestory.API.Server;
using Vintagestory.API.Util;
using Vintagestory.GameContent;

namespace Automacao
{
    // =====================================================================
    // SENTINELA ELÉTRICA — a Sentinela antiga, agora dentro da Automação.
    // Vigia num raio (a "Área" da janela é o alcance), atira virotes (munição infinita) em bicho bravo,
    // mas só com energia. A cabeça gira pelo renderer genérico (vigiando = vai e volta, alerta = dá a volta).
    // =====================================================================
    public class TrabalhoSentinela : Trabalho, IAcoes
    {
        public override string Code => "sentinela";
        // O consumo é fixo por tipo na rede: fica no meio-termo (vigiando ~1, atirando ~3)
        public override float Consumo => 2f;
        public override float ConsumoAgora(BEMaquina m) => m.ModoAtual == "alerta" ? 3f : 1f;
        public override float Intervalo => 3600f;   // não usa o ciclo do núcleo: atira no tick próprio
        public override int RaioPadrao => 20;
        public override bool PrecisaEspaco => false;
        public override string[] Opcoes => new[] { "som", "alvo-drifters", "alvo-temporais", "alvo-lobos", "alvo-hienas", "alvo-ursos", "alvo-gafanhotos" };

        static readonly float[] Cadencias = { 0.5f, 1f, 1.4f, 2f, 3f };
        static readonly float[] Danos = { 2f, 4f, 6f, 8f, 12f };
        static readonly string[] Ignorar = { "*hacked*", "*baby*", "*pup*" };
        const float VelocidadeVirote = 1.6f;
        const double AlturaCano = 16.25 / 16.0;
        const double DistBoca = 0.97;
        static readonly AssetLocation SomTiro = new AssetLocation("game", "sounds/bow-release");
        static readonly AssetLocation SomAchou = new AssetLocation("game", "sounds/effect/latch");
        static readonly AssetLocation Virote = new AssetLocation("automacao", "bolt");
        static readonly AssetLocation Flecha = new AssetLocation("game", "arrow-iron");

        static float Cadencia(BEMaquina m) => Cadencias[GameMath.Clamp(m.Dados.GetInt("cad", 2), 0, Cadencias.Length - 1)];
        static float Dano(BEMaquina m) => Danos[GameMath.Clamp(m.Dados.GetInt("dano", 1), 0, Danos.Length - 1)];

        public override bool TemTrabalho(BEMaquina m) => true;

        public override void Inicializar(BEMaquina m)
        {
            // Tick rápido (5x por segundo) só pra mirar e atirar; o núcleo cuida do resto
            if (m.Api.Side == EnumAppSide.Server) m.RegisterGameTickListener(dt => Mirar(m), 200);
        }

        IEnumerable<string> Alvos(BEMaquina m)
        {
            if (m.Opcao("alvo-drifters")) yield return "drifter-*";
            if (m.Opcao("alvo-gafanhotos")) yield return "locust-*";
            if (m.Opcao("alvo-temporais")) { yield return "bowtorn-*"; yield return "shiver-*"; yield return "bell-*"; yield return "bellmini-*"; }
            if (m.Opcao("alvo-lobos")) yield return "wolf-*";
            if (m.Opcao("alvo-hienas")) yield return "hyena-*";
            if (m.Opcao("alvo-ursos")) yield return "bear-*";
        }

        void Mirar(BEMaquina m)
        {
            var world = m.Api.World;
            bool pode = m.Ligada && m.Energizado && m.NaRede && m.Energia > 0.3f;
            if (!pode) { Perdeu(m); return; }

            var cabeca = new Vec3d(m.Pos.X + 0.5, m.Pos.Y + AlturaCano, m.Pos.Z + 0.5);
            float alcance = m.Raio;
            var padroes = Alvos(m).ToArray();
            if (padroes.Length == 0) { Perdeu(m); return; }

            var alvo = world.GetNearestEntity(cabeca, alcance, alcance,
                e => Inimigo(e, padroes) && cabeca.SquareDistanceTo(e.Pos.XYZ) <= alcance * alcance && Ve(m, cabeca, Mira(e)));
            if (alvo == null) { Perdeu(m); return; }

            long agora = world.ElapsedMilliseconds;
            if (m.Dados.GetLong("alvoId") != alvo.EntityId)
            {
                m.Dados.SetLong("alvoId", alvo.EntityId);
                if (m.Opcao("som")) world.PlaySoundAt(SomAchou, cabeca.X, cabeca.Y, cabeca.Z, null, false, 24, 1);
                m.Dados.SetLong("proxTiro", Math.Max(m.Dados.GetLong("proxTiro"), agora + 250));
            }
            if (!m.Dados.GetBool("alerta")) { m.Dados.SetBool("alerta", true); m.MarkDirty(true); }
            m.Dados.SetLong("alertaAte", agora + 3000);

            if (agora >= m.Dados.GetLong("proxTiro"))
            {
                Atirar(m, cabeca, Mira(alvo));
                m.Dados.SetLong("proxTiro", agora + (long)(1000 / Math.Max(0.1f, Cadencia(m))));
            }
        }

        static void Perdeu(BEMaquina m)
        {
            m.Dados.SetLong("alvoId", 0);
            if (m.Dados.GetBool("alerta") && m.Api.World.ElapsedMilliseconds > m.Dados.GetLong("alertaAte"))
            {
                m.Dados.SetBool("alerta", false);
                m.MarkDirty(true);
            }
        }

        static Vec3d Mira(Entity e)
        {
            double h = e.SelectionBox?.Y2 ?? 1;
            return e.Pos.XYZ.Add(0, h * 0.55, 0);
        }

        static bool Inimigo(Entity e, string[] padroes)
        {
            if (e == null || !e.Alive || e is EntityPlayer || e is not EntityAgent) return false;
            string path = e.Code?.Path;
            if (path == null) return false;
            if (Ignorar.Any(p => WildcardUtil.Match(p, path))) return false;
            return padroes.Any(p => WildcardUtil.Match(p, path));
        }

        /// <summary>Linha de visão: anda pela reta e para se bater em bloco sólido.</summary>
        static bool Ve(BEMaquina m, Vec3d de, Vec3d ate)
        {
            var ba = m.Api.World.BlockAccessor;
            var dir = ate - de;
            double len = dir.Length();
            if (len < 0.01) return true;
            dir.Mul(1 / len);
            var bp = new BlockPos(0, 0, 0, m.Pos.dimension);
            for (double d = DistBoca; d < len - 0.5; d += 0.35)
            {
                bp.Set((int)Math.Floor(de.X + dir.X * d), (int)Math.Floor(de.Y + dir.Y * d), (int)Math.Floor(de.Z + dir.Z * d));
                if (bp.Equals(m.Pos)) continue;
                var boxes = ba.GetBlock(bp)?.GetCollisionBoxes(ba, bp);
                if (boxes == null || boxes.Length == 0) continue;
                double px = de.X + dir.X * d - bp.X, py = de.Y + dir.Y * d - bp.Y, pz = de.Z + dir.Z * d - bp.Z;
                foreach (var box in boxes)
                    if (px >= box.X1 && px <= box.X2 && py >= box.Y1 && py <= box.Y2 && pz >= box.Z1 && pz <= box.Z2) return false;
            }
            return true;
        }

        void Atirar(BEMaquina m, Vec3d cabeca, Vec3d mira)
        {
            var world = m.Api.World;
            var type = world.GetEntityType(Virote);
            if (type == null) return;
            var entity = world.ClassRegistry.CreateEntity(type);
            if (entity is not IProjectile proj) return;

            proj.FiredBy = null;
            proj.Damage = Dano(m);
            proj.DamageTier = 2;
            proj.DropOnImpactChance = 0;
            var flecha = world.GetItem(Flecha);
            if (flecha != null) proj.ProjectileStack = new ItemStack(flecha);

            double yaw = Math.Atan2(mira.X - cabeca.X, mira.Z - cabeca.Z);
            var boca = cabeca.AddCopy(Math.Sin(yaw) * DistBoca, 0, Math.Cos(yaw) * DistBoca);
            var dir = mira - boca;
            dir.Normalize();
            entity.Pos.SetPosWithDimension(boca.Add(0, m.Pos.dimension * BlockPos.DimensionBoundary, 0));
            entity.Pos.Motion.Set(dir.X * VelocidadeVirote, dir.Y * VelocidadeVirote, dir.Z * VelocidadeVirote);
            entity.World = world;
            proj.PreInitialize();
            world.SpawnPriorityEntity(entity);
            if (m.Opcao("som")) world.PlaySoundAt(SomTiro, cabeca.X, cabeca.Y, cabeca.Z, null, true, 24, 1);
            m.Dados.SetInt("tiros", m.Dados.GetInt("tiros") + 1);
        }

        public override string Modo(BEMaquina m)
        {
            if (!m.Ligada || !m.Energizado || !m.NaRede) return "parado";
            return m.Dados.GetBool("alerta") ? "alerta" : "vigiando";
        }

        public override string Info(BEMaquina m) =>
            Lang.Get("automacao:info-sentinela", m.Raio, Cadencia(m).ToString("0.#"), Dano(m).ToString("0"), m.Dados.GetInt("tiros"));

        public IEnumerable<(string code, string texto)> Botoes(BEMaquina m)
        {
            yield return ("cad", Lang.Get("automacao:btn-sentinela-cadencia", Cadencia(m).ToString("0.#")));
            yield return ("dano", Lang.Get("automacao:btn-sentinela-dano", Dano(m).ToString("0")));
        }

        public void Acao(BEMaquina m, IPlayer p, string acao)
        {
            if (acao == "cad") m.Dados.SetInt("cad", (m.Dados.GetInt("cad", 2) + 1) % Cadencias.Length);
            if (acao == "dano") m.Dados.SetInt("dano", (m.Dados.GetInt("dano", 1) + 1) % Danos.Length);
        }
    }

    // =====================================================================
    // VIGIA ELÉTRICO — holofote girando e sino: quando chega drifter/bicho bravo na área,
    // toca o sino, avisa no chat de onde vem e fica em alerta uns 30 s.
    // =====================================================================
    public class TrabalhoVigia : Trabalho
    {
        public override string Code => "vigia";
        public override float Consumo => 1f;
        public override float Intervalo => 3600f;
        public override int RaioPadrao => 16;
        public override bool PrecisaEspaco => false;

        static readonly string[] Ameacas = { "drifter-", "locust-", "bowtorn", "shiver", "bellmini", "bell", "wolf-", "hyena-", "bear-" };
        const long IntervaloAlarmeMs = 60000;
        static readonly AssetLocation Sino = new AssetLocation("game", "sounds/effect/deepbell");

        public override bool TemTrabalho(BEMaquina m) => true;

        public override void Tick(BEMaquina m, float dt)
        {
            if (!m.Ligada || !m.Energizado || !m.NaRede) return;
            var world = m.Api.World;
            long agora = world.ElapsedMilliseconds;
            if (agora - m.UltimoAlarmeMs < IntervaloAlarmeMs) return;
            // olha a cada 2 s
            if (agora - m.Dados.GetLong("olhou") < 2000) return;
            m.Dados.SetLong("olhou", agora);

            var centro = m.Pos.ToVec3d().Add(0.5, 0.5, 0.5);
            var bicho = world.GetEntitiesAround(centro, m.Raio, 8, e =>
                e.Alive && e.Code != null && Ameacas.Any(a => e.Code.Path.StartsWith(a)) && !e.Code.Path.Contains("baby"))
                .OrderBy(e => e.Pos.SquareDistanceTo(centro)).FirstOrDefault();
            if (bicho == null) return;

            m.UltimoAlarmeMs = agora;
            m.AlarmeAteMs = agora + 30000;
            for (int i = 0; i < 3; i++)
                world.RegisterCallback(_ => world.PlaySoundAt(Sino, centro.X, centro.Y + 1, centro.Z, null, false, 64, 1f), i * 700);

            double dx = bicho.Pos.X - centro.X, dz = bicho.Pos.Z - centro.Z;
            string lado = Math.Abs(dx) > Math.Abs(dz) ? (dx > 0 ? "leste" : "oeste") : (dz > 0 ? "sul" : "norte");
            int dist = (int)Math.Sqrt(dx * dx + dz * dz);
            m.Dados.SetString("ultimo", bicho.GetName());
            m.Falar("alarme-vigia", true, bicho.GetName(), Lang.Get("automacao:lado-" + lado), dist);
            m.MarkDirty(true);
        }

        public override string Modo(BEMaquina m)
        {
            if (!m.Ligada || !m.Energizado || !m.NaRede) return "parado";
            return m.EmAlarme ? "alerta" : "ligado";
        }

        public override string Info(BEMaquina m)
        {
            string ult = m.Dados.GetString("ultimo");
            return m.EmAlarme ? Lang.Get("automacao:info-vigia-alerta", ult ?? "?")
                 : Lang.Get("automacao:info-vigia", m.Raio) + (string.IsNullOrEmpty(ult) ? "" : "<br>" + Lang.Get("automacao:info-vigia-ultimo", ult));
        }
    }

    // =====================================================================
    // CALENDÁRIO ELÉTRICO — hora, data, estação, previsão de chuva pros próximos dias e a
    // tempestade temporal (quantos dias faltam, se está acontecendo; avisa no chat quando chega perto).
    // O servidor calcula tudo e guarda em m.Dados (o cliente só lê).
    // =====================================================================
    public class TrabalhoCalendario : Trabalho
    {
        public override string Code => "calendario";
        public override float Consumo => 1f;
        public override float Intervalo => 3600f;
        public override bool PrecisaEspaco => false;

        public override bool TemTrabalho(BEMaquina m) => true;

        public override void Tick(BEMaquina m, float dt)
        {
            var w = m.Api.World;
            var cal = w.Calendar;
            bool ligado = m.Ligada && m.Energizado && m.NaRede;
            m.Dados.SetBool("ligado", ligado);
            if (!ligado) return;

            // Hora e data (sempre)
            m.Dados.SetString("hora", $"{cal.FullHourOfDay:00}:{(int)((cal.HourOfDay - cal.FullHourOfDay) * 60):00}");
            int dia = (int)(cal.TotalDays % cal.DaysPerMonth) + 1;
            m.Dados.SetString("data", Lang.Get("automacao:cal-data", dia, Lang.Get("month-" + cal.MonthName), cal.Year));

            // Estação e dias até a próxima
            var est = cal.GetSeason(m.Pos);
            float rel = cal.GetSeasonRel(m.Pos);
            float prox = (float)Math.Ceiling(rel * 4 + 0.0001) / 4f;
            int diasEst = (int)Math.Ceiling((prox - rel) * cal.DaysPerYear);
            m.Dados.SetString("estacao", Lang.Get("automacao:cal-estacao", Lang.Get("automacao:estacao-" + est.ToString().ToLowerInvariant()), Math.Max(1, diasEst)));

            // Tempestade temporal
            var sts = m.Api.ModLoader.GetModSystem<SystemTemporalStability>();
            var sd = sts?.StormData;
            bool tempOn = w.Config.GetString("temporalStorms", "sometimes") != "off" && sd != null;
            bool agora = tempOn && sd.nowStormActive;
            double falta = tempOn ? sd.nextStormTotalDays - cal.TotalDays : double.MaxValue;
            m.Dados.SetBool("tormenta", tempOn && (agora || falta < 1));
            string tor;
            if (!tempOn) tor = Lang.Get("automacao:cal-tor-off");
            else if (agora) tor = Lang.Get("automacao:cal-tor-agora");
            else tor = Lang.Get("automacao:cal-tor-falta", falta < 1 ? Lang.Get("automacao:cal-menos1dia") : Lang.Get("automacao:cal-dias", (int)Math.Ceiling(falta)),
                Lang.Get("automacao:cal-tor-forca-" + sd.nextStormStrength.ToString().ToLowerInvariant()));
            m.Dados.SetString("tor", tor);

            // Aviso no chat: uma vez por tempestade, quando faltar menos de 1 dia
            if (tempOn && !agora && falta < 1 && m.Dados.GetDouble("avisou") != sd.nextStormTotalDays)
            {
                m.Dados.SetDouble("avisou", sd.nextStormTotalDays);
                m.Falar("alarme-tormenta", true, (int)Math.Max(1, falta * cal.HoursPerDay));
            }

            // Previsão do tempo (pesado: só a cada 30 s)
            long ms = w.ElapsedMilliseconds;
            if (ms - m.Dados.GetLong("prevEm", -999999) > 30000)
            {
                m.Dados.SetLong("prevEm", ms);
                var ws = m.Api.ModLoader.GetModSystem<WeatherSystemBase>();
                var sb = new StringBuilder();
                string[] nomes = { "cal-hoje", "cal-amanha", "cal-depois" };
                double hoje = Math.Floor(cal.TotalDays);
                for (int d = 0; d < 3; d++)
                {
                    float maxChuva = 0;
                    if (ws != null)
                        for (int h = 0; h < 8; h++)
                        {
                            double td = hoje + d + h / 8.0;
                            if (d == 0 && td < cal.TotalDays - 0.125) continue;
                            try { maxChuva = Math.Max(maxChuva, ws.GetPrecipitation(m.Pos.X + 0.5, m.Pos.Y, m.Pos.Z + 0.5, td)); } catch { }
                        }
                    float temp = 10;
                    try { temp = w.BlockAccessor.GetClimateAt(m.Pos, EnumGetClimateMode.ForSuppliedDate_TemperatureOnly, hoje + d + 0.5).Temperature; } catch { }
                    string tempo = maxChuva < 0.1f ? "cal-sol" : maxChuva < 0.35f ? "cal-nublado" : temp < 0 ? "cal-neve" : maxChuva > 0.7f ? "cal-tempestade" : "cal-chuva";
                    if (sb.Length > 0) sb.Append("<br>");
                    sb.Append(Lang.Get("automacao:cal-prev", Lang.Get("automacao:" + nomes[d]), Lang.Get("automacao:" + tempo), (int)Math.Round(temp)));
                }
                m.Dados.SetString("prev", sb.ToString());
            }
        }

        public override string Modo(BEMaquina m)
        {
            if (!m.Ligada || !m.Energizado || !m.NaRede) return "parado";
            return m.Dados.GetBool("tormenta") ? "tormenta" : "ligado";
        }

        public override string Info(BEMaquina m)
        {
            if (!m.Dados.GetBool("ligado")) return Lang.Get("automacao:cal-apagado");
            return $"<strong>{m.Dados.GetString("hora")}</strong> — {m.Dados.GetString("data")}<br>{m.Dados.GetString("estacao")}<br><br>" +
                   $"<strong>{Lang.Get("automacao:cal-previsao")}</strong><br>{m.Dados.GetString("prev")}<br><br>" +
                   $"<strong>{Lang.Get("automacao:cal-tempestade-temporal")}</strong><br>{m.Dados.GetString("tor")}";
        }
    }

    // =====================================================================
    // PAINEL DA REDE — mostra o resumo da rede (o núcleo já copia pra m.Dados).
    // =====================================================================
    public class TrabalhoPainel : Trabalho
    {
        public override string Code => "painel";
        public override float Consumo => 1f;
        public override float Intervalo => 3600f;
        public override bool PrecisaEspaco => false;
        public override bool TemTrabalho(BEMaquina m) => true;

        public override string Modo(BEMaquina m) => m.Ligada && m.Energizado && m.NaRede ? "ligado" : "parado";

        public override string Info(BEMaquina m)
        {
            if (!m.NaRede || !m.Dados.HasAttribute("rGera")) return Lang.Get("automacao:painel-semrede");
            var d = m.Dados;
            float gera = d.GetFloat("rGera"), pede = d.GetFloat("rPede"), carga = d.GetFloat("rCarga"), cap = d.GetFloat("rCap");
            float saldo = gera - pede;
            string saldoTxt = saldo >= 0
                ? Lang.Get("automacao:painel-sobra", saldo.ToString("0.#"))
                : Lang.Get("automacao:painel-falta", (-saldo).ToString("0.#"));
            string bat = cap <= 0 ? Lang.Get("automacao:painel-sembateria")
                : Lang.Get("automacao:painel-bateria", (int)carga, (int)cap, (int)(carga / cap * 100), Barra(carga / cap));
            string dura = "";
            if (saldo < 0 && carga > 0) dura = "<br>" + Lang.Get("automacao:painel-dura", Tempo(carga / -saldo));
            else if (saldo > 0 && cap > carga) dura = "<br>" + Lang.Get("automacao:painel-enche", Tempo((cap - carga) / saldo));
            int paradas = d.GetInt("rParadas");
            return Lang.Get("automacao:painel-resumo", gera.ToString("0.#"), pede.ToString("0.#")) + "<br>" + saldoTxt + "<br>" + bat + dura + "<br>" +
                   Lang.Get("automacao:painel-pecas", d.GetInt("rPostes"), d.GetInt("rPecas")) +
                   (paradas > 0 ? "<br><font color=\"#ff6b5a\">" + Lang.Get("automacao:painel-paradas", paradas) + "</font>" : "");
        }

        static string Barra(float f)
        {
            int n = GameMath.Clamp((int)Math.Round(f * 10), 0, 10);
            return new string('█', n) + new string('░', 10 - n);
        }

        static string Tempo(float segundos)
        {
            if (segundos < 120) return Lang.Get("automacao:tempo-seg", (int)segundos);
            if (segundos < 7200) return Lang.Get("automacao:tempo-min", (int)(segundos / 60));
            return Lang.Get("automacao:tempo-h", (segundos / 3600).ToString("0.#"));
        }
    }

    // =====================================================================
    // ESTABILIZADOR TEMPORAL — enquanto ligado e com energia, deixa a estabilidade temporal alta
    // num raio em volta (a "Área" da janela). Funciona nos dois lados (o cliente usa pro efeito na tela).
    // =====================================================================
    public class TrabalhoEstabilizador : Trabalho
    {
        public override string Code => "estabilizador";
        public override float Consumo => 8f;
        public override float Intervalo => 3600f;
        public override int RaioPadrao => 16;
        public override bool PrecisaEspaco => false;
        public override bool TemTrabalho(BEMaquina m) => true;

        public override void Inicializar(BEMaquina m)
        {
            EspEstabilidade.Garantir(m.Api);
            m.RegisterGameTickListener(dt => EspEstabilidade.Atualizar(m), 1000);
        }

        public override void Removido(BEMaquina m) => EspEstabilidade.Tirar(m.Pos);

        public override string Modo(BEMaquina m) => Ativo(m) ? "ligado" : "parado";

        public static bool Ativo(BEMaquina m) => m.Ligada && m.Energizado && m.NaRede && (m.Api.Side == EnumAppSide.Client || m.Energia > 0.5f);

        public override string Info(BEMaquina m) =>
            Ativo(m) ? Lang.Get("automacao:info-estab-on", m.Raio * 2 + 1) : Lang.Get("automacao:info-estab-off");
    }

    /// <summary>Lista dos estabilizadores ligados + o "gancho" na estabilidade temporal do jogo.</summary>
    public static class EspEstabilidade
    {
        class Ativo { public BlockPos Pos; public int Raio; public long Ms; }

        static readonly Dictionary<string, Dictionary<BlockPos, Ativo>> porLado = new Dictionary<string, Dictionary<BlockPos, Ativo>>();
        static readonly HashSet<string> ligados = new HashSet<string>();
        const float Estavel = 1.5f;

        static Dictionary<BlockPos, Ativo> Lista(EnumAppSide lado)
        {
            string k = lado.ToString();
            if (!porLado.TryGetValue(k, out var d)) porLado[k] = d = new Dictionary<BlockPos, Ativo>();
            return d;
        }

        public static void Garantir(ICoreAPI api)
        {
            string k = api.Side + "@" + api.World.GetHashCode();
            if (ligados.Contains(k)) return;
            var sts = api.ModLoader.GetModSystem<SystemTemporalStability>();
            if (sts == null) return;
            ligados.Add(k);
            var lista = Lista(api.Side);
            lista.Clear();
            sts.OnGetTemporalStability += (stab, x, y, z) =>
            {
                if (lista.Count == 0 || stab >= Estavel) return stab;
                long agora = api.World.ElapsedMilliseconds;
                foreach (var a in lista.Values)
                {
                    if (agora - a.Ms > 5000) continue;   // descarregou e não avisou: ignora
                    if (Math.Abs(x - a.Pos.X - 0.5) <= a.Raio + 0.5 && Math.Abs(z - a.Pos.Z - 0.5) <= a.Raio + 0.5 && Math.Abs(y - a.Pos.Y) <= a.Raio)
                        return Estavel;
                }
                return stab;
            };
        }

        public static void Atualizar(BEMaquina m)
        {
            var lista = Lista(m.Api.Side);
            if (TrabalhoEstabilizador.Ativo(m))
                lista[m.Pos.Copy()] = new Ativo { Pos = m.Pos.Copy(), Raio = Math.Max(2, m.Raio), Ms = m.Api.World.ElapsedMilliseconds };
            else
                lista.Remove(m.Pos);
        }

        public static void Tirar(BlockPos pos)
        {
            foreach (var l in porLado.Values) l.Remove(pos);
        }
    }

    /// <summary>
    /// Compatibilidade com a Sentinela antiga: o block entity salvo no mundo se chama "BESentinela".
    /// Com o mod Sentinela removido, esse nome passa a criar uma máquina da Automação (junto com o remap do bloco).
    /// </summary>
    public class EspSentinelaCompat : ModSystem
    {
        public override double ExecuteOrder() => 0.2;

        public override void Start(ICoreAPI api)
        {
            if (api.ModLoader.IsModEnabled("sentinela")) return;
            try { api.RegisterBlockEntityClass("BESentinela", typeof(BEMaquina)); }
            catch (Exception e) { api.Logger.Warning("[Automação] compat Sentinela: {0}", e.Message); }
        }
    }
}
