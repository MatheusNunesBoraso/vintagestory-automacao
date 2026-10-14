using System.Collections.Generic;
using System.Linq;
using Cairo;
using Vintagestory.API.Client;
using Vintagestory.API.Common;
using Vintagestory.API.Config;
using Vintagestory.API.MathTools;
using Vintagestory.API.Util;
using Vintagestory.GameContent;

namespace Automacao
{
    /// <summary>
    /// Janela de toda peça: à esquerda o estado (energia, o que está fazendo, números) e os botões;
    /// à direita o bauzinho. Poste tem "Mostrar alcance" e "Ver conexões".
    /// </summary>
    public class GuiDialogMaquina : GuiDialogBlockEntity
    {
        readonly BEMaquina be;
        string ultimaAssinatura;

        static readonly double[] Dim = { 0.75, 0.7, 0.62, 1 };

        public GuiDialogMaquina(BEMaquina be, InventoryBase inventory, BlockPos pos, ICoreClientAPI capi)
            : base(be.Titulo, inventory, pos, capi)
        {
            this.be = be;
            if (IsDuplicate) return;
            if (be.TemBau) capi.World.Player.InventoryManager.OpenInventory(inventory);
            Compose();
        }

        static string L(string key, params object[] args) => Lang.Get("automacao:" + key, args);

        string Assinatura()
        {
            var t = be.Trabalho;
            string acoes = t is IAcoes ac ? string.Join(",", ac.Botoes(be).Select(b => b.code + b.texto)) : "";
            return be.Ligada + "|" + acoes + "|" + string.Join(",", be.Opcoes.Select(k => k.Key + k.Value)) + "|" + be.Raio + "|" + RedeCliente.MostrandoAlcance(be);
        }

        void Compose()
        {
            var t = be.Trabalho;
            ultimaAssinatura = Assinatura();
            const double w = 300;
            double y = 30;
            var bounds = new List<ElementBounds>();
            ElementBounds B(double h, double x = 0, double ww = w) { var b = ElementBounds.Fixed(x, y, ww, h); bounds.Add(b); return b; }

            var status = B(40); y += 44;
            var info = B(150); y += 156;

            var botoes = new List<(ElementBounds b, string texto, ActionConsumable acao, bool ativo)>();
            void Botao(string texto, ActionConsumable acao, bool ativo = false)
            {
                botoes.Add((B(28), texto, acao, ativo));
                y += 32;
            }

            if (t != null && t.Tipo != "poste" && t.Tipo != "bateria")
                Botao(be.Ligada ? L("btn-desligar") : L("btn-ligar"), () => { Mandar(BEMaquina.PacketLigar); return true; }, !be.Ligada);
            if (t != null && t.Tipo == "poste")
            {
                Botao(L("btn-alcance"), () => { RedeCliente.AlternarAlcance(be, RedeEnergia.Alcance); Recompor(); return true; }, RedeCliente.MostrandoAlcance(be));
                Botao(L("btn-conexoes"), () => { Mandar(BEMaquina.PacketConexoes); TryClose(); return true; });
            }
            bool usaArea = be.Block?.Attributes?["usaArea"].AsBool() == true;
            if (usaArea)
            {
                var menos = ElementBounds.Fixed(0, y, 40, 28); var area = ElementBounds.Fixed(46, y, 150, 28); var mais = ElementBounds.Fixed(202, y, 40, 28);
                var ver = ElementBounds.Fixed(248, y, 52, 28);
                bounds.AddRange(new[] { menos, area, mais, ver });
                botoes.Add((menos, "-", () => { Mandar(BEMaquina.PacketRaio, SerializerUtil.Serialize(-1)); return true; }, false));
                botoes.Add((mais, "+", () => { Mandar(BEMaquina.PacketRaio, SerializerUtil.Serialize(1)); return true; }, false));
                botoes.Add((ver, L("btn-ver"), () => { RedeCliente.AlternarAlcance(be, be.Raio); Recompor(); return true; }, RedeCliente.MostrandoAlcance(be)));
                botoes.Add((area, L("area", be.Raio * 2 + 1), () => true, false));
                y += 32;
            }
            if (t != null)
                foreach (var op in t.Opcoes)
                {
                    string key = op;
                    Botao((be.Opcao(key) ? "✓ " : "✗ ") + L("opcao-" + key), () => { Mandar(BEMaquina.PacketOpcao, SerializerUtil.Serialize(key)); return true; }, be.Opcao(key));
                }
            if (t is IAcoes acoes)
                foreach (var (code, texto) in acoes.Botoes(be))
                {
                    string cod = code;
                    Botao(texto, () => { Mandar(BEMaquina.PacketAcao, SerializerUtil.Serialize(cod)); return true; });
                }

            // Bauzinho
            ElementBounds grid = null, pegar = null, tituloBau = null;
            if (be.TemBau)
            {
                tituloBau = ElementBounds.Fixed(w + 20, 30, 210, 22);
                grid = ElementStdBounds.SlotGrid(EnumDialogArea.None, w + 20, 56, 4, 4);
                pegar = ElementBounds.Fixed(w + 20, 270, 210, 30);
                bounds.AddRange(new[] { tituloBau, grid, pegar });
            }

            var bg = ElementBounds.Fill.WithFixedPadding(GuiStyle.ElementToDialogPadding);
            bg.BothSizing = ElementSizing.FitToChildren;
            bg.WithChildren(bounds.ToArray());
            var dialogBounds = ElementStdBounds.AutosizedMainDialog.WithAlignment(EnumDialogArea.RightMiddle).WithFixedAlignmentOffset(-GuiStyle.DialogToScreenPadding, 0);

            ClearComposers();
            var c = capi.Gui.CreateCompo("automacao" + BlockEntityPosition, dialogBounds)
                .AddShadedDialogBG(bg)
                .AddDialogTitleBar(DialogTitle, () => TryClose())
                .BeginChildElements(bg)
                    .AddDynamicText("", CairoFont.WhiteSmallishText().WithWeight(FontWeight.Bold), status, "status")
                    .AddRichtext("", CairoFont.WhiteDetailText().WithColor(Dim), info, "info");
            int i = 0;
            foreach (var (b, texto, acao, ativo) in botoes)
            {
                c.AddSmallButton(texto, acao, b, EnumButtonStyle.Normal, "b" + i);
                i++;
            }
            if (be.TemBau)
            {
                c.AddStaticText(L("bauzinho"), CairoFont.WhiteSmallishText(), tituloBau)
                 .AddItemSlotGrid(Inventory, SendInvPacket, 4, grid, "bau")
                 .AddSmallButton(L("btn-pegartudo"), () => { Mandar(BEMaquina.PacketPegarTudo); return true; }, pegar);
            }
            c.EndChildElements();
            SingleComposer = c.Compose();
            Atualizar();
        }

        void Recompor() => Compose();

        void Mandar(int id, byte[] data = null) => capi.Network.SendBlockEntityPacket(BlockEntityPosition, id, data);

        void SendInvPacket(object p) => capi.Network.SendBlockEntityPacket(BlockEntityPosition.X, BlockEntityPosition.Y, BlockEntityPosition.Z, p);

        /// <summary>O BE mudou (chegou pacote do servidor): atualiza os textos e recompõe se os botões mudaram.</summary>
        public void Atualizar()
        {
            if (SingleComposer == null) return;
            if (Assinatura() != ultimaAssinatura) { Compose(); return; }
            SingleComposer.GetDynamicText("status")?.SetNewText(be.StatusTexto());
            string extra = null;
            try { extra = be.Trabalho?.Info(be); } catch { }
            string desc = Lang.Get("automacao:resumo-" + be.Block?.Code?.FirstCodePart());
            if (desc.StartsWith("automacao:")) desc = "";
            string dono = string.IsNullOrEmpty(be.OwnerName) ? "" : "\n" + L("dono", be.OwnerName);
            string txt = (extra ?? "") + (string.IsNullOrEmpty(extra) ? "" : "<br><br>") + desc + dono;
            SingleComposer.GetRichtext("info")?.SetNewText(txt.Replace("\n", "<br>"), CairoFont.WhiteDetailText().WithColor(Dim));
        }

        public override void OnGuiClosed()
        {
            base.OnGuiClosed();
            if (be.TemBau) capi.World.Player.InventoryManager.CloseInventory(Inventory);
        }
    }
}
