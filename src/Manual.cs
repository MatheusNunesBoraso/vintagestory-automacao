using System;
using System.Collections.Generic;
using System.Linq;
using Vintagestory.API.Client;
using Vintagestory.API.Common;
using Vintagestory.API.Config;
using Vintagestory.API.Datastructures;
using Vintagestory.API.MathTools;

namespace Automacao
{
    /// <summary>O Manual da Automação: clique direito com ele na mão abre o livro.</summary>
    public class ItemManual : Item
    {
        GuiDialogManual dialog;

        public override void OnHeldInteractStart(ItemSlot slot, EntityAgent byEntity, BlockSelection blockSel, EntitySelection entitySel, bool firstEvent, ref EnumHandHandling handling)
        {
            if (!firstEvent) return;
            handling = EnumHandHandling.PreventDefault;
            if (api is ICoreClientAPI capi)
            {
                dialog ??= new GuiDialogManual(capi);
                if (dialog.IsOpened()) dialog.TryClose(); else dialog.TryOpen();
            }
        }
    }

    public class CapituloManual
    {
        public string Titulo;
        public string Grupo;
        public string Texto;   // VTML (o "html" do jogo)
    }

    /// <summary>
    /// Livro com capítulos à esquerda e o texto à direita (rolando). O conteúdo vem de
    /// assets/automacao/config/manual-{idioma}.json (gerado junto com o mod).
    /// </summary>
    public class GuiDialogManual : GuiDialogGeneric
    {
        List<CapituloManual> capitulos;
        int atual;
        string filtroGrupo;

        public GuiDialogManual(ICoreClientAPI capi) : base(Lang.Get("automacao:manual-titulo"), capi)
        {
            Carregar();
        }

        void Carregar()
        {
            string lang = Lang.CurrentLocale?.StartsWith("pt") == true ? "pt-br" : "en";
            var asset = capi.Assets.TryGet(new AssetLocation("automacao", $"config/manual-{lang}.json"))
                     ?? capi.Assets.TryGet(new AssetLocation("automacao", "config/manual-pt-br.json"));
            capitulos = asset?.ToObject<List<CapituloManual>>() ?? new List<CapituloManual>
            {
                new CapituloManual { Titulo = "?", Texto = "Manual não encontrado." }
            };
            filtroGrupo = capitulos[0].Grupo;
        }

        public override void OnGuiOpened()
        {
            base.OnGuiOpened();
            Compor();
        }

        void Compor()
        {
            var tela = capi.Gui.WindowBounds;
            double alt = Math.Min(760, tela.InnerHeight / RuntimeEnv.GUIScale - 120);
            double larg = Math.Min(1180, tela.InnerWidth / RuntimeEnv.GUIScale - 80);
            const double menuW = 290;

            var grupos = capitulos.Select(c => c.Grupo).Distinct().ToList();
            var abas = grupos.Select((g, i) => new GuiTab { Name = g, DataInt = i }).ToArray();
            int abaAtual = Math.Max(0, grupos.IndexOf(filtroGrupo));

            var abasB = ElementBounds.Fixed(0, -24, larg, 25);
            var menu = ElementBounds.Fixed(0, 30, menuW, alt - 30);
            var menuClip = menu.ForkBoundingParent();
            var menuScroll = ElementBounds.Fixed(menuW + 4, 30, 16, alt - 30);
            var texto = ElementBounds.Fixed(menuW + 34, 30, larg - menuW - 60, alt - 30);
            var textoClip = texto.ForkBoundingParent();
            var textoScroll = ElementBounds.Fixed(larg - 20, 30, 16, alt - 30);

            var bg = ElementBounds.Fill.WithFixedPadding(GuiStyle.ElementToDialogPadding);
            bg.BothSizing = ElementSizing.FitToChildren;
            bg.WithChildren(menuClip, menuScroll, textoClip, textoScroll);
            var dlg = ElementStdBounds.AutosizedMainDialog.WithAlignment(EnumDialogArea.CenterMiddle);

            var lista = capitulos.Select((c, i) => (c, i)).Where(x => x.c.Grupo == filtroGrupo).ToList();
            var comp = capi.Gui.CreateCompo("automacao-manual", dlg)
                .AddShadedDialogBG(bg)
                .AddDialogTitleBar(DialogTitle, () => TryClose())
                .AddHorizontalTabs(abas, abasB, i => { filtroGrupo = grupos[i]; atual = lista0(i); Compor(); }, CairoFont.WhiteSmallText(), CairoFont.WhiteSmallText().WithColor(GuiStyle.ActiveButtonTextColor), "abas")
                .BeginChildElements(bg)
                    .BeginClip(menuClip)
                        .AddContainer(menu, "menu")
                    .EndClip()
                    .AddVerticalScrollbar(v => Rolar("menu", menu, v), menuScroll, "menuScroll")
                    .BeginClip(textoClip)
                        .AddRichtext(capitulos[atual].Texto ?? "", CairoFont.WhiteSmallText().WithLineHeightMultiplier(1.15), texto, "texto")
                    .EndClip()
                    .AddVerticalScrollbar(v => Rolar("texto", texto, v), textoScroll, "textoScroll")
                .EndChildElements();

            var cont = comp.GetContainer("menu");
            double y = 0;
            foreach (var (c, i) in lista)
            {
                int idx = i;
                var b = ElementBounds.Fixed(0, y, menuW - 8, 30);
                var botao = new GuiElementTextButton(capi, (idx == atual ? "▶ " : "") + c.Titulo,
                    CairoFont.WhiteSmallText(), CairoFont.WhiteSmallText().WithColor(GuiStyle.ActiveButtonTextColor),
                    () => { atual = idx; Compor(); return true; }, b, EnumButtonStyle.Small);
                cont.Add(botao);
                y += 33;
            }
            SingleComposer = comp.Compose();
            comp.GetHorizontalTabs("abas").activeElement = abaAtual;
            comp.GetScrollbar("menuScroll").SetHeights((float)(alt - 30), (float)Math.Max(alt - 30, y));
            var rt = comp.GetRichtext("texto");
            comp.GetScrollbar("textoScroll").SetHeights((float)(alt - 30), (float)Math.Max(alt - 30, rt.Bounds.fixedHeight));
        }

        int lista0(int grupo)
        {
            string g = capitulos.Select(c => c.Grupo).Distinct().ElementAt(grupo);
            return capitulos.FindIndex(c => c.Grupo == g);
        }

        void Rolar(string nome, ElementBounds b, float v)
        {
            b.fixedY = 30 - v;
            b.CalcWorldBounds();
        }
    }
}
