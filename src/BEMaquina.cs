using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Vintagestory.API.Client;
using Vintagestory.API.Common;
using Vintagestory.API.Config;
using Vintagestory.API.Datastructures;
using Vintagestory.API.MathTools;
using Vintagestory.API.Server;
using Vintagestory.API.Util;
using Vintagestory.GameContent;

namespace Automacao
{
    /// <summary>
    /// Toda peça da Automação: fonte, bateria, poste ou máquina. Bauzinho de 16 espaços, energia vinda da rede,
    /// ciclo de trabalho, janela, animação e as ferramentas que os trabalhos usam (procurar na área, achar água...).
    /// </summary>
    public class BEMaquina : BlockEntityOpenableContainer
    {
        public const int PacketLigar = 3101, PacketPegarTudo = 3102, PacketOpcao = 3103, PacketConexoes = 3104,
                         PacketRaio = 3105, PacketAcao = 3106;
        public const int ScanDown = 4, ScanUp = 4;

        readonly InventoryGeneric inventory;
        GuiDialogMaquina dialog;
        MaquinaRenderer renderer;

        // ---- estado (salvo e mandado pro cliente) ----
        public string OwnerUid, OwnerName;
        public bool Ligada = true;
        public int Raio = -1;
        public Dictionary<string, bool> Opcoes = new Dictionary<string, bool>();
        /// <summary>0..1: quanto da energia pedida a rede entregou no último segundo.</summary>
        public float Energia;
        /// <summary>A rede em que está tem energia (gerando ou com bateria)?</summary>
        public bool Energizado;
        /// <summary>Ligada num poste?</summary>
        public bool NaRede;
        public bool Quer;          // pediu energia neste segundo
        public bool Trabalhando;   // trabalhou/gerou neste segundo
        public float Progresso;
        public float UltimaGeracao;
        public float Carga;        // bateria
        public string ModoAtual = "";
        public int Feitos;
        /// <summary>Dados livres de cada trabalho (salvos junto).</summary>
        public TreeAttribute Dados = new TreeAttribute();

        // Processo de forno/varal (portado dos minions)
        public List<ItemStack> Processo = new List<ItemStack>();
        public double ProcessoProntoEm;
        public long UltimoAlarmeMs = -999999, AlarmeAteMs;
        public bool EmAlarme => Api != null && Api.World.ElapsedMilliseconds < AlarmeAteMs;

        List<BlockPos> aguaCache;
        long aguaCacheMs;
        long lastChatMs;

        public override InventoryBase Inventory => inventory;
        public override string InventoryClassName => "automacao";

        public BEMaquina()
        {
            inventory = new InventoryGeneric(16, null, null);
        }

        // ================== informação do bloco ==================
        public string Codigo => Block?.Attributes?["trabalho"].AsString() ?? Block?.Code?.FirstCodePart();
        public Trabalho Trabalho => Trabalho.Pegar(Codigo);
        public string Titulo => Lang.Get("automacao:block-" + (Block?.Code?.FirstCodePart() ?? "?"));
        public string[] Modos => Block?.Attributes?["modos"].AsArray<string>() ?? new[] { "parado", "ligado" };
        public string ModoTrabalhando => Block?.Attributes?["modoTrabalhando"].AsString() ?? Modos.Last();
        public bool TemBau => Block?.Attributes?["bau"].AsBool(true) ?? true;

        public BlockFacing Frente => BlockFacing.FromCode(Api?.World.BlockAccessor.GetBlock(Pos).Variant["side"] ?? Block?.Variant["side"]) ?? BlockFacing.SOUTH;

        public bool Opcao(string key) => !Opcoes.TryGetValue(key, out bool v) || v;

        public bool IsDay()
        {
            float h = Api.World.Calendar.HourOfDay;
            return h >= 6f && h < 19.5f;
        }

        // ================== ciclo ==================
        public override void Initialize(ICoreAPI api)
        {
            base.Initialize(api);
            var t = Trabalho;
            if (Raio < 0) Raio = t?.RaioPadrao ?? 8;

            if (api.Side == EnumAppSide.Server)
            {
                api.ModLoader.GetModSystem<RedeEnergia>()?.Registrar(this);
                RegisterGameTickListener(ServerTick, 1000);
                try { t?.Inicializar(this); } catch (Exception e) { api.Logger.Warning("[Automação] {0} init: {1}", Codigo, e.Message); }
            }
            else if (api is ICoreClientAPI capi)
            {
                renderer = new MaquinaRenderer(capi, this);
                capi.Event.RegisterRenderer(renderer, EnumRenderStage.Opaque, "automacao");
                try { t?.Inicializar(this); } catch { }
            }
        }

        void ServerTick(float dt)
        {
            var t = Trabalho;
            if (t == null) return;
            string antes = ModoAtual + Energizado + Trabalhando + (int)(Progresso * 10) + (int)Carga;

            try { t.Tick(this, dt); }
            catch (Exception e) { Api.Logger.Warning("[Automação] {0} tick: {1}", Codigo, e.Message); }

            if (t.Tipo == "maquina")
            {
                bool tem = false;
                if (Ligada)
                {
                    try { tem = t.TemTrabalho(this) && (!t.PrecisaEspaco || TemEspaco()); }
                    catch (Exception e) { Api.Logger.Warning("[Automação] {0} temtrabalho: {1}", Codigo, e.Message); }
                }
                Quer = tem;
                Trabalhando = tem && Energia > 0.01f;
                if (Trabalhando)
                {
                    Progresso += dt * Energia;
                    if (Progresso >= t.Intervalo)
                    {
                        Progresso = 0;
                        try { t.Trabalhar(this); Feitos++; }
                        catch (Exception e) { Api.Logger.Warning("[Automação] {0} trabalho: {1}", Codigo, e.Message); }
                    }
                }
            }
            else if (t.Tipo == "fonte")
            {
                Trabalhando = Ligada && UltimaGeracao > 0.01f;
            }

            ModoAtual = CalcularModo(t);
            TrocarEstado(t);
            string depois = ModoAtual + Energizado + Trabalhando + (int)(Progresso * 10) + (int)Carga;
            if (antes != depois) MarkDirty(true);
        }

        /// <summary>Blocos com variante "estado" (luz acesa de verdade, portão que abre): troca o bloco sem perder nada.</summary>
        void TrocarEstado(Trabalho t)
        {
            var estados = Block?.Attributes?["estados"].AsArray<string>();
            if (estados == null || estados.Length < 2) return;
            string quer = null;
            try { quer = t.Estado(this); } catch { }
            if (quer == null)
            {
                var glow = Block.Attributes["glowModos"].AsArray<string>();
                bool brilha = glow != null ? glow.Contains(ModoAtual) : Energizado && (Trabalhando || t.Tipo != "maquina");
                quer = brilha ? estados[1] : estados[0];
            }
            var atual = Api.World.BlockAccessor.GetBlock(Pos);
            if (atual.Variant["estado"] == quer) return;
            var nb = Api.World.GetBlock(atual.CodeWithVariant("estado", quer));
            if (nb == null || nb.Id == 0) return;
            Api.World.BlockAccessor.ExchangeBlock(nb.Id, Pos);
            Api.World.BlockAccessor.MarkBlockDirty(Pos);
        }

        string CalcularModo(Trabalho t)
        {
            string m = null;
            try { m = t.Modo(this); } catch { }
            if (m != null) return m;
            var modos = Modos;
            if (t.Tipo == "fonte") return Trabalhando ? ModoTrabalhando : modos[0];
            if (t.Tipo == "poste") return Energizado ? ModoTrabalhando : modos[0];
            return Trabalhando ? ModoTrabalhando : modos[0];
        }

        // ================== clique direito ==================
        public bool OnInteract(IPlayer byPlayer, BlockSelection blockSel)
        {
            if (string.IsNullOrEmpty(OwnerUid) && Api.Side == EnumAppSide.Server)
            {
                OwnerUid = byPlayer.PlayerUID;
                OwnerName = byPlayer.PlayerName;
                MarkDirty(true);
            }
            var t = Trabalho;
            try { if (t != null && t.Interagir(this, byPlayer, blockSel)) return true; }
            catch (Exception e) { Api.Logger.Warning("[Automação] {0} interagir: {1}", Codigo, e.Message); }
            return OnPlayerRightClick(byPlayer, blockSel);
        }

        public override bool OnPlayerRightClick(IPlayer byPlayer, BlockSelection blockSel)
        {
            if (Api.Side == EnumAppSide.Client)
            {
                if (dialog == null)
                {
                    dialog = new GuiDialogMaquina(this, inventory, Pos, (ICoreClientAPI)Api);
                    dialog.OnClosed += () => { dialog?.Dispose(); dialog = null; };
                }
                dialog.TryOpen();
            }
            else
            {
                byPlayer.InventoryManager.OpenInventory(inventory);
            }
            return true;
        }

        public override void OnReceivedClientPacket(IPlayer fromPlayer, int packetid, byte[] data)
        {
            base.OnReceivedClientPacket(fromPlayer, packetid, data);
            switch (packetid)
            {
                case PacketLigar:
                    Ligada = !Ligada;
                    MarkDirty(true);
                    break;
                case PacketPegarTudo:
                    foreach (var slot in inventory)
                    {
                        if (slot.Empty) continue;
                        if (!fromPlayer.InventoryManager.TryGiveItemstack(slot.Itemstack, true)) continue;
                        if (slot.Itemstack.StackSize <= 0) slot.Itemstack = null;
                        slot.MarkDirty();
                    }
                    MarkDirty(true);
                    break;
                case PacketOpcao:
                    {
                        string key = SerializerUtil.Deserialize<string>(data);
                        Opcoes[key] = !Opcao(key);
                        MarkDirty(true);
                        break;
                    }
                case PacketRaio:
                    {
                        int d = SerializerUtil.Deserialize<int>(data);
                        Raio = GameMath.Clamp(Raio + d, 2, 24);
                        MarkDirty(true);
                        break;
                    }
                case PacketConexoes:
                    Api.ModLoader.GetModSystem<RedeEnergia>()?.MandarConexoes(this, fromPlayer as IServerPlayer);
                    break;
                case PacketAcao:
                    {
                        string acao = SerializerUtil.Deserialize<string>(data);
                        if (Trabalho is IAcoes ac) ac.Acao(this, fromPlayer, acao);
                        MarkDirty(true);
                        break;
                    }
            }
        }

        // ================== ferramentas pros trabalhos ==================
        public bool TemEspaco() => inventory.Any(s => s.Empty);

        public bool TemNoBau(System.Func<ItemStack, bool> qual) => inventory.Any(s => !s.Empty && qual(s.Itemstack));

        public int ContarNoBau(System.Func<ItemStack, bool> qual) => inventory.Where(s => !s.Empty && qual(s.Itemstack)).Sum(s => s.StackSize);

        /// <summary>Tira do bauzinho até 'max' itens que servem (pode vir de vários espaços).</summary>
        public List<ItemStack> TirarDoBau(System.Func<ItemStack, bool> qual, int max)
        {
            var outp = new List<ItemStack>();
            int falta = max;
            foreach (var slot in inventory)
            {
                if (falta <= 0) break;
                if (slot.Empty || !qual(slot.Itemstack)) continue;
                var st = slot.TakeOut(Math.Min(falta, slot.StackSize));
                if (st == null) continue;
                falta -= st.StackSize;
                var junto = outp.FirstOrDefault(o => o.Equals(Api.World, st, GlobalConstants.IgnoredStackAttributes));
                if (junto != null) junto.StackSize += st.StackSize; else outp.Add(st);
                slot.MarkDirty();
            }
            if (outp.Count > 0) MarkDirty(true);
            return outp;
        }

        /// <summary>Guarda no bauzinho. O que não couber cai no chão em cima da máquina.</summary>
        public void Guardar(IEnumerable<ItemStack> stacks)
        {
            var sobra = new List<ItemStack>();
            foreach (var stack in stacks)
            {
                if (stack == null || stack.StackSize <= 0) continue;
                var source = new DummySlot(stack);
                foreach (var slot in inventory)
                {
                    if (source.Empty) break;
                    if (slot.Empty || !slot.Itemstack.Equals(Api.World, stack, GlobalConstants.IgnoredStackAttributes)) continue;
                    source.TryPutInto(Api.World, slot, source.StackSize);
                }
                foreach (var slot in inventory)
                {
                    if (source.Empty) break;
                    if (slot.Empty) source.TryPutInto(Api.World, slot, source.StackSize);
                }
                if (!source.Empty) sobra.Add(source.Itemstack);
            }
            foreach (var s in sobra) Api.World.SpawnItemEntity(s, Pos.ToVec3d().Add(0.5, 1.1, 0.5));
            MarkDirty(true);
        }

        public void Guardar(ItemStack stack) => Guardar(new[] { stack });

        /// <summary>Compatível com o código dos minions (cesta -> bauzinho).</summary>
        public void Deposit(List<ItemStack> carried)
        {
            Guardar(carried);
            carried.Clear();
        }

        public bool InRange(BlockPos p) =>
            Math.Abs(p.X - Pos.X) <= Raio && Math.Abs(p.Z - Pos.Z) <= Raio && p.Y >= Pos.Y - ScanDown && p.Y <= Pos.Y + ScanUp;

        /// <summary>Todos os blocos da área que passam no teste.</summary>
        public List<BlockPos> Procurar(System.Func<BlockPos, Block, bool> teste)
        {
            var ba = Api.World.BlockAccessor;
            var list = new List<BlockPos>();
            var tmp = new BlockPos(Pos.dimension);
            for (int dx = -Raio; dx <= Raio; dx++)
                for (int dz = -Raio; dz <= Raio; dz++)
                    for (int dy = -ScanDown; dy <= ScanUp; dy++)
                    {
                        tmp.Set(Pos.X + dx, Pos.Y + dy, Pos.Z + dz);
                        var b = ba.GetBlock(tmp);
                        if (b.Id == 0) continue;
                        if (teste(tmp, b)) list.Add(tmp.Copy());
                    }
            return list;
        }

        public BlockPos MaisPerto(IEnumerable<BlockPos> lista, Vec3d de, ISet<BlockPos> pular)
        {
            BlockPos best = null;
            double bd = double.MaxValue;
            foreach (var p in lista)
            {
                if (pular != null && pular.Contains(p)) continue;
                double d = p.DistanceSqTo(de.X, de.Y, de.Z);
                if (d < bd) { bd = d; best = p; }
            }
            return best;
        }

        public BlockPos AcharAgua(Vec3d de, ISet<BlockPos> pular, int minAgua)
        {
            long now = Api.World.ElapsedMilliseconds;
            if (aguaCache == null || now - aguaCacheMs > 10000)
            {
                aguaCacheMs = now;
                var ba = Api.World.BlockAccessor;
                aguaCache = new List<BlockPos>();
                var tmp = new BlockPos(Pos.dimension);
                for (int dx = -Raio; dx <= Raio; dx++)
                    for (int dz = -Raio; dz <= Raio; dz++)
                        for (int dy = ScanUp; dy >= -ScanDown; dy--)
                        {
                            tmp.Set(Pos.X + dx, Pos.Y + dy, Pos.Z + dz);
                            if (!Agua(ba, tmp)) continue;
                            var acima = tmp.UpCopy();
                            if (Agua(ba, acima) || ba.GetBlock(acima).Id != 0) break;
                            aguaCache.Add(tmp.Copy());
                            break;
                        }
            }
            var ok = aguaCache.Where(p => aguaCache.Count(q => Math.Abs(q.X - p.X) <= 2 && Math.Abs(q.Z - p.Z) <= 2) >= minAgua);
            return MaisPerto(ok, de, pular);
        }

        /// <summary>Quantos blocos de água encostados na máquina (dos 4 lados, nesta altura e uma abaixo).</summary>
        public int AguaEncostada()
        {
            var ba = Api.World.BlockAccessor;
            int n = 0;
            foreach (var f in BlockFacing.HORIZONTALS)
                for (int dy = 0; dy >= -1; dy--)
                    if (Agua(ba, Pos.AddCopy(f).Up(dy))) n++;
            return n;
        }

        public static bool Agua(IBlockAccessor ba, BlockPos p)
        {
            var f = ba.GetBlock(p, BlockLayersAccess.Fluid);
            return f?.LiquidCode == "water" || f?.LiquidCode == "saltwater";
        }

        public Vec3d PontoDeTrabalho() => Pos.ToVec3d().Add(0.5, 0, 0.5);
        public Vec3d DoorPos() => Pos.ToVec3d().Add(0.5, 0, 0.5);

        /// <summary>Fala no chat pra quem estiver perto (alarme vai mais longe e sempre fala).</summary>
        public void Falar(string key, bool force = false, params object[] args)
        {
            if (Api.Side != EnumAppSide.Server) return;
            bool alarme = key.StartsWith("alarme");
            long now = Api.World.ElapsedMilliseconds;
            if (!force && now - lastChatMs < 20000) return;
            lastChatMs = now;
            double alcance = alarme ? 128 : 32;
            foreach (var p in Api.World.AllOnlinePlayers.OfType<IServerPlayer>())
            {
                if (p.Entity == null || p.Entity.Pos.DistanceTo(Pos.ToVec3d().Add(0.5, 0, 0.5)) > alcance) continue;
                string text = Lang.GetL(p.LanguageCode, "automacao:fala-" + key, args);
                p.SendMessage(GlobalConstants.GeneralChatGroup, $"<strong>{Lang.GetL(p.LanguageCode, "automacao:block-" + Block.Code.FirstCodePart())}:</strong> {text}",
                    alarme ? EnumChatType.Notification : EnumChatType.OthersMessage);
            }
        }

        public void Som(string som, float volume = 0.6f, float alcance = 16)
        {
            Api.World.PlaySoundAt(new AssetLocation(som), Pos.X + 0.5, Pos.Y + 0.5, Pos.Z + 0.5, null, true, alcance, volume);
        }

        // ================== info ==================
        public override void GetBlockInfo(IPlayer forPlayer, StringBuilder dsc)
        {
            var t = Trabalho;
            if (t == null) return;
            dsc.AppendLine(StatusTexto());
            string extra = null;
            try { extra = t.Info(this); } catch { }
            if (!string.IsNullOrEmpty(extra)) dsc.AppendLine(extra);
        }

        public string StatusTexto()
        {
            var t = Trabalho;
            string L(string k, params object[] a) => Lang.Get("automacao:" + k, a);
            if (t == null) return "";
            switch (t.Tipo)
            {
                case "fonte":
                    if (!NaRede) return L("st-fonte-semposte", UltimaGeracao.ToString("0.#"));
                    return UltimaGeracao > 0.01f ? L("st-gerando", UltimaGeracao.ToString("0.#")) : L("st-fonte-parada");
                case "bateria":
                    return L("st-bateria", (int)Carga, (int)t.Capacidade, (int)(Carga / Math.Max(1, t.Capacidade) * 100)) + (NaRede ? "" : "\n" + L("st-semposte"));
                case "poste":
                    return Energizado ? L("st-poste-ok") : L("st-poste-sem");
                default:
                    if (!Ligada) return L("st-desligada");
                    if (!NaRede) return L("st-semposte");
                    if (Trabalhando) return L("st-trabalhando", (int)(Energia * 100));
                    if (Quer) return L("st-semenergia");
                    if (t.PrecisaEspaco && !TemEspaco()) return L("st-baucheio");
                    return L("st-esperando");
            }
        }

        // ================== salvar / sincronizar ==================
        public override void ToTreeAttributes(ITreeAttribute tree)
        {
            base.ToTreeAttributes(tree);
            tree.SetString("owner", OwnerUid ?? "");
            tree.SetString("ownerName", OwnerName ?? "");
            tree.SetBool("ligada", Ligada);
            tree.SetInt("raio", Raio);
            tree.SetFloat("energia", Energia);
            tree.SetBool("energizado", Energizado);
            tree.SetBool("narede", NaRede);
            tree.SetBool("quer", Quer);
            tree.SetBool("trab", Trabalhando);
            tree.SetFloat("prog", Progresso);
            tree.SetFloat("ger", UltimaGeracao);
            tree.SetFloat("carga", Carga);
            tree.SetString("modo", ModoAtual ?? "");
            tree.SetInt("feitos", Feitos);
            tree.SetDouble("procPronto", ProcessoProntoEm);
            tree.SetLong("alarmeAte", AlarmeAteMs);
            var op = new TreeAttribute();
            foreach (var kv in Opcoes) op.SetBool(kv.Key, kv.Value);
            tree["opcoes"] = op;
            tree["dados"] = Dados;
            var pr = new TreeAttribute();
            for (int i = 0; i < Processo.Count; i++) pr.SetItemstack("s" + i, Processo[i]);
            pr.SetInt("n", Processo.Count);
            tree["processo"] = pr;
        }

        public override void FromTreeAttributes(ITreeAttribute tree, IWorldAccessor worldForResolving)
        {
            base.FromTreeAttributes(tree, worldForResolving);
            OwnerUid = tree.GetString("owner", "");
            OwnerName = tree.GetString("ownerName", "");
            Ligada = tree.GetBool("ligada", true);
            Raio = tree.GetInt("raio", Raio);
            Energia = tree.GetFloat("energia");
            Energizado = tree.GetBool("energizado");
            NaRede = tree.GetBool("narede");
            Quer = tree.GetBool("quer");
            Trabalhando = tree.GetBool("trab");
            Progresso = tree.GetFloat("prog");
            UltimaGeracao = tree.GetFloat("ger");
            Carga = tree.GetFloat("carga");
            ModoAtual = tree.GetString("modo", "");
            Feitos = tree.GetInt("feitos");
            ProcessoProntoEm = tree.GetDouble("procPronto");
            AlarmeAteMs = tree.GetLong("alarmeAte");
            Opcoes.Clear();
            if (tree["opcoes"] is ITreeAttribute op)
                foreach (var kv in op) Opcoes[kv.Key] = op.GetBool(kv.Key);
            Dados = tree["dados"] as TreeAttribute ?? new TreeAttribute();
            Processo.Clear();
            if (tree["processo"] is ITreeAttribute pr)
            {
                int n = pr.GetInt("n");
                for (int i = 0; i < n; i++)
                {
                    var s = pr.GetItemstack("s" + i);
                    if (s == null) continue;
                    s.ResolveBlockOrItem(worldForResolving);
                    Processo.Add(s);
                }
            }
            if (Api?.Side == EnumAppSide.Client) dialog?.Atualizar();
        }

        // ================== limpeza ==================
        public override void OnBlockRemoved()
        {
            base.OnBlockRemoved();
            Sair();
            try { Trabalho?.Removido(this); } catch { }
        }

        public override void OnBlockBroken(IPlayer byPlayer = null)
        {
            // Bateria guarda a carga no item? (não: a carga se perde, igual o jogo faz com coisas quentes)
            base.OnBlockBroken(byPlayer);
        }

        public override void OnBlockUnloaded()
        {
            base.OnBlockUnloaded();
            Sair();
        }

        void Sair()
        {
            if (Api?.Side == EnumAppSide.Server) Api.ModLoader.GetModSystem<RedeEnergia>()?.Remover(this);
            if (renderer != null)
            {
                (Api as ICoreClientAPI)?.Event.UnregisterRenderer(renderer, EnumRenderStage.Opaque);
                renderer.Dispose();
                renderer = null;
            }
            dialog?.TryClose();
            RedeCliente.Esquecer(this);
        }
    }

    /// <summary>Trabalho que tem botões próprios na janela (ex.: elevador, forja).</summary>
    public interface IAcoes
    {
        /// <summary>Botões (código, texto) que aparecem na janela.</summary>
        IEnumerable<(string code, string texto)> Botoes(BEMaquina m);
        void Acao(BEMaquina m, IPlayer p, string acao);
    }
}
