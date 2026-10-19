using System;
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
    /// Janela de toda peça: à esquerda o estado (energia, o que está fazendo, números) e os controles;
    /// à direita o bauzinho. Tudo é medido antes de montar (nada de altura fixa), então texto comprido
    /// em qualquer idioma empurra os botões pra baixo em vez de passar por cima deles.
    /// </summary>
    public class GuiDialogMaquina : GuiDialogBlockEntity
    {
        readonly BEMaquina be;
        string ultimaAssinatura;
        // Alturas reservadas pros textos: só crescem enquanto a janela está aberta, pra ela não ficar pulando
        double altStatus, altInfo;

        const double W = 340;        // largura da coluna da esquerda
        const double AltBotao = 28;
        const double Vao = 5;

        static readonly double[] Dim = { 0.78, 0.73, 0.65, 1 };

        public GuiDialogMaquina(BEMaquina be, InventoryBase inventory, BlockPos pos, ICoreClientAPI capi)
            : base(be.Titulo, inventory, pos, capi)
        {
            this.be = be;
            if (IsDuplicate) return;
            if (be.TemBau) capi.World.Player.InventoryManager.OpenInventory(inventory);
            Compose();
        }

        static string L(string key, params object[] args) => Lang.Get("automacao:" + key, args);

        static CairoFont FonteStatus() => CairoFont.WhiteSmallText().WithWeight(FontWeight.Bold);
        static CairoFont FonteInfo() => CairoFont.WhiteDetailText().WithColor(Dim).WithLineHeightMultiplier(1.1);

        string Assinatura()
        {
            var t = be.Trabalho;
            string acoes = t is IAcoes ac ? string.Join(",", ac.Botoes(be).Select(b => b.code + b.texto)) : "";
            return be.Ligada + "|" + acoes + "|" + be.Raio + "|" + RedeCliente.MostrandoAlcance(be);
        }

        // ---------------- textos ----------------

        string TextoStatus()
        {
            string s = be.StatusTexto();
            if (string.IsNullOrEmpty(s)) return "";
            string cor = CorStatus();
            s = s.Replace("\n", "<br>");
            return cor == null ? s : $"<font color=\"{cor}\">{s}</font>";
        }

        /// <summary>Verde = trabalhando/gerando, laranja = falta poste ou energia, cinza = desligada.</summary>
        string CorStatus()
        {
            var t = be.Trabalho;
            if (t == null) return null;
            if (t.Tipo != "poste" && t.Tipo != "bateria" && !be.Ligada) return "#a09a90";
            if (t.Tipo == "poste") return be.Energizado ? "#9fe08a" : "#e8a24a";
            if (t.Tipo != "bateria" && !be.NaRede) return "#e8a24a";
            if (t.Tipo == "fonte") return be.UltimaGeracao > 0.01f ? "#9fe08a" : "#e8a24a";
            if (be.Trabalhando) return "#9fe08a";
            return null;
        }

        string TextoInfo()
        {
            string extra = null;
            try { extra = be.Trabalho?.Info(be); } catch { }
            string dono = string.IsNullOrEmpty(be.OwnerName) ? "" : L("dono", be.OwnerName);
            string txt = extra ?? "";
            if (dono != "") txt += (txt == "" ? "" : "<br><br>") + "<font color=\"#8a8478\">" + dono + "</font>";
            return txt.Replace("\r", "").Replace("\n", "<br>");
        }

        /// <summary>Altura (sem escala) que um texto VTML ocupa numa caixa de largura w.</summary>
        double Altura(string vtml, CairoFont fonte, double w)
        {
            if (string.IsNullOrEmpty(vtml)) return 0;
            var b = ElementBounds.Fixed(0, 0, w, 10).WithParent(capi.Gui.WindowBounds);
            var rt = new GuiElementRichtext(capi, VtmlUtil.Richtextify(capi, vtml, fonte), b);
            rt.CalcHeightAndPositions();
            double h = rt.TotalHeight / RuntimeEnv.GUIScale;
            rt.Dispose();
            return Math.Ceiling(h) + 2;
        }

        /// <summary>Fonte de botão que cabe na largura (diminui um pouco se o texto for comprido).</summary>
        static CairoFont FonteQueCabe(string texto, double largura)
        {
            var f = CairoFont.SmallButtonText();
            while (f.UnscaledFontsize > 10 && f.GetTextExtents(texto).Width / RuntimeEnv.GUIScale > largura - 14)
                f.UnscaledFontsize -= 0.5;
            return f;
        }

        // ---------------- montagem ----------------

        void Compose()
        {
            var t = be.Trabalho;
            ultimaAssinatura = Assinatura();

            string status = TextoStatus(), info = TextoInfo();
            altStatus = Math.Max(altStatus, Altura(status, FonteStatus(), W));
            altInfo = Math.Max(altInfo, Altura(info, FonteInfo(), W));

            double y = 30;
            var filhos = new List<ElementBounds>();
            ElementBounds Caixa(double x, double h, double w) { var b = ElementBounds.Fixed(x, y, w, h); filhos.Add(b); return b; }

            var bStatus = Caixa(0, Math.Max(altStatus, 18), W); y += bStatus.fixedHeight + 6;
            ElementBounds bInfo = null;
            if (altInfo > 0) { bInfo = Caixa(0, altInfo, W); y += altInfo; }
            y += 10;
            var bLinha = Caixa(0, 1, W); y += 10;

            // Cada controle vira uma função que adiciona o elemento no composer
            var montar = new List<Action<GuiComposer>>();
            int n = 0;

            void Botao(string texto, ActionConsumable acao, double x = 0, double w = W, bool avanca = true)
            {
                var b = Caixa(x, AltBotao, w);
                string key = "b" + n++;
                montar.Add(c => c.AddButton(texto, acao, b, FonteQueCabe(texto, w), EnumButtonStyle.Small, key));
                if (avanca) y += AltBotao + Vao;
            }

            if (t != null && t.Tipo != "poste" && t.Tipo != "bateria")
                Botao(be.Ligada ? L("btn-desligar") : L("btn-ligar"), () => { Mandar(BEMaquina.PacketLigar); return true; });

            if (t != null && t.Tipo == "poste")
            {
                bool mostrando = RedeCliente.MostrandoAlcance(be);
                Botao(mostrando ? L("btn-alcance-esconder") : L("btn-alcance"), () => { RedeCliente.AlternarAlcance(be, RedeEnergia.Alcance); Recompor(); return true; });
                Botao(L("btn-conexoes"), () => { Mandar(BEMaquina.PacketConexoes); TryClose(); return true; });
            }

            if (be.Block?.Attributes?["usaArea"].AsBool() == true)
            {
                // [ - ]  Área: 9x9 blocos  [ + ]  [ Ver ]
                const double bw = 34, verW = 82;
                bool mostrando = RedeCliente.MostrandoAlcance(be);
                Botao("-", () => { Mandar(BEMaquina.PacketRaio, SerializerUtil.Serialize(-1)); return true; }, 0, bw, false);
                var bArea = ElementBounds.Fixed(bw + 4, y + 5, W - 2 * bw - verW - 16, AltBotao); filhos.Add(bArea);
                string area = L("area", be.Raio * 2 + 1);
                montar.Add(c => c.AddStaticText(area, CairoFont.WhiteSmallText().WithOrientation(EnumTextOrientation.Center), bArea));
                Botao("+", () => { Mandar(BEMaquina.PacketRaio, SerializerUtil.Serialize(1)); return true; }, W - verW - bw - 8, bw, false);
                Botao(mostrando ? L("btn-ver-esconder") : L("btn-ver"), () => { RedeCliente.AlternarAlcance(be, be.Raio); Recompor(); return true; }, W - verW, verW);
            }

            // Opções liga/desliga: chavinha + nome
            if (t != null && t.Opcoes.Length > 0)
            {
                y += 4;
                foreach (var op in t.Opcoes)
                {
                    string key = op;
                    var bSw = Caixa(0, 24, 24);
                    var bNome = ElementBounds.Fixed(32, y + 3, W - 32, 22); filhos.Add(bNome);
                    string sw = "op-" + key, nome = L("opcao-" + key);
                    montar.Add(c => c
                        .AddSwitch(on => Mandar(BEMaquina.PacketOpcao, SerializerUtil.Serialize(key)), bSw, sw, 24, 3)
                        .AddStaticText(nome, CairoFont.WhiteSmallText(), bNome));
                    y += 24 + Vao;
                }
                y += 4;
            }

            // Botões próprios da peça; "ant"/"prox" ficam lado a lado
            if (t is IAcoes acoes)
            {
                var lista = acoes.Botoes(be).ToList();
                for (int i = 0; i < lista.Count; i++)
                {
                    var (code, texto) = lista[i];
                    string cod = code;
                    if (cod == "ant" && i + 1 < lista.Count && lista[i + 1].code == "prox")
                    {
                        string prox = lista[i + 1].texto;
                        double meia = (W - 6) / 2;
                        Botao(texto, () => { Mandar(BEMaquina.PacketAcao, SerializerUtil.Serialize("ant")); return true; }, 0, meia, false);
                        Botao(prox, () => { Mandar(BEMaquina.PacketAcao, SerializerUtil.Serialize("prox")); return true; }, meia + 6, meia);
                        i++;
                        continue;
                    }
                    Botao(texto, () => { Mandar(BEMaquina.PacketAcao, SerializerUtil.Serialize(cod)); return true; });
                }
            }

            // "Como funciona": abre o manual no capítulo desta peça (a descrição comprida mora lá)
            y += 2;
            Botao(L("btn-manual"), () => { GuiDialogManual.AbrirEm(capi, be.Titulo); return true; });

            // Bauzinho
            ElementBounds grid = null, pegar = null, tituloBau = null;
            if (be.TemBau)
            {
                tituloBau = ElementBounds.Fixed(W + 24, 30, 210, 22);
                grid = ElementStdBounds.SlotGrid(EnumDialogArea.None, W + 24, 56, 4, 4);
                pegar = ElementBounds.Fixed(W + 24, 270, 206, AltBotao);
                filhos.AddRange(new[] { tituloBau, grid, pegar });
            }

            var bg = ElementBounds.Fill.WithFixedPadding(GuiStyle.ElementToDialogPadding);
            bg.BothSizing = ElementSizing.FitToChildren;
            bg.WithChildren(filhos.ToArray());
            var dialogBounds = ElementStdBounds.AutosizedMainDialog.WithAlignment(EnumDialogArea.RightMiddle).WithFixedAlignmentOffset(-GuiStyle.DialogToScreenPadding, 0);

            ClearComposers();
            var comp = capi.Gui.CreateCompo("automacao" + BlockEntityPosition, dialogBounds)
                .AddShadedDialogBG(bg)
                .AddDialogTitleBar(DialogTitle, () => TryClose())
                .BeginChildElements(bg)
                    .AddRichtext(status, FonteStatus(), bStatus, "status");
            if (bInfo != null) comp.AddRichtext(info, FonteInfo(), bInfo, "info");
            comp.AddStaticCustomDraw(bLinha, (ctx, surface, b) =>
            {
                ctx.SetSourceRGBA(1, 1, 1, 0.15);
                ctx.Rectangle(b.drawX, b.drawY, b.InnerWidth, Math.Max(1, b.InnerHeight));
                ctx.Fill();
            });
            foreach (var m in montar) m(comp);
            if (be.TemBau)
            {
                comp.AddStaticText(L("bauzinho"), CairoFont.WhiteSmallishText(), tituloBau)
                    .AddItemSlotGrid(Inventory, SendInvPacket, 4, grid, "bau")
                    .AddButton(L("btn-pegartudo"), () => { Mandar(BEMaquina.PacketPegarTudo); return true; }, pegar, CairoFont.SmallButtonText(), EnumButtonStyle.Small);
            }
            comp.EndChildElements();
            SingleComposer = comp.Compose();

            if (t != null)
                foreach (var op in t.Opcoes)
                    SingleComposer.GetSwitch("op-" + op)?.SetValue(be.Opcao(op));
        }

        void Recompor() => Compose();

        void Mandar(int id, byte[] data = null) => capi.Network.SendBlockEntityPacket(BlockEntityPosition, id, data);

        void SendInvPacket(object p) => capi.Network.SendBlockEntityPacket(BlockEntityPosition.X, BlockEntityPosition.Y, BlockEntityPosition.Z, p);

        /// <summary>O BE mudou (chegou pacote do servidor): atualiza os textos e remonta se algo não cabe mais.</summary>
        public void Atualizar()
        {
            if (SingleComposer == null) return;
            if (Assinatura() != ultimaAssinatura) { Compose(); return; }

            string status = TextoStatus(), info = TextoInfo();
            double hs = Altura(status, FonteStatus(), W), hi = Altura(info, FonteInfo(), W);
            bool semInfo = SingleComposer.GetRichtext("info") == null;
            if (hs > Math.Max(altStatus, 18) + 1 || hi > altInfo + 1 || (semInfo && hi > 0)) { Compose(); return; }

            SingleComposer.GetRichtext("status")?.SetNewText(status, FonteStatus());
            SingleComposer.GetRichtext("info")?.SetNewText(info, FonteInfo());
            var t = be.Trabalho;
            if (t != null)
                foreach (var op in t.Opcoes)
                    SingleComposer.GetSwitch("op-" + op)?.SetValue(be.Opcao(op));
        }

        public override void OnGuiClosed()
        {
            base.OnGuiClosed();
            if (be.TemBau) capi.World.Player.InventoryManager.CloseInventory(Inventory);
        }
    }
}
