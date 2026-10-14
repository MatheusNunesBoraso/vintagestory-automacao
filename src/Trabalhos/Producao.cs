using System;
using System.Collections.Generic;
using System.Linq;
using Vintagestory.API.Common;
using Vintagestory.API.Config;
using Vintagestory.API.Datastructures;
using Vintagestory.API.MathTools;
using Vintagestory.GameContent;

namespace Automacao
{
    // =====================================================================
    // PRODUÇÃO — máquinas que transformam o que está no bauzinho.
    // Todas trabalham "por ciclo": a cada Intervalo segundos com energia cheia, fazem uma porção
    // e guardam o resultado no próprio bauzinho. Sem energia, param onde estão.
    // =====================================================================
    static class Prod
    {
        public static bool Game(ItemStack s, System.Func<string, bool> t) => s?.Collectible?.Code?.Domain == "game" && t(s.Collectible.Code.Path);

        public static CollectibleObject Pegar(IWorldAccessor w, string code)
        {
            var loc = new AssetLocation(code);
            return (CollectibleObject)w.GetItem(loc) ?? w.GetBlock(loc);
        }

        public static ItemStack Novo(IWorldAccessor w, string code, int qtd)
        {
            var c = Pegar(w, code);
            return c == null || qtd <= 0 ? null : new ItemStack(c, qtd);
        }

        /// <summary>Divide uma pilha grande em pilhas que respeitam o tamanho máximo.</summary>
        public static List<ItemStack> EmPilhas(ItemStack s, int total)
        {
            var outp = new List<ItemStack>();
            int max = Math.Max(1, s.Collectible.MaxStackSize);
            while (total > 0)
            {
                int q = Math.Min(max, total);
                var n = s.Clone();
                n.StackSize = q;
                outp.Add(n);
                total -= q;
            }
            return outp;
        }

        /// <summary>Resolve um JsonItemStack (com placeholders tipo {fruit} já trocados pelo jogo ao carregar).</summary>
        public static ItemStack Resolver(IWorldAccessor w, JsonItemStack js)
        {
            if (js == null) return null;
            if (js.ResolvedItemstack == null) js.Resolve(w, "automacao");
            return js.ResolvedItemstack?.Clone();
        }

        public static ItemSlot Slot(BEMaquina m, System.Func<ItemStack, bool> qual) =>
            m.Inventory.FirstOrDefault(s => !s.Empty && qual(s.Itemstack));

        /// <summary>Pega um único item (separa se a pilha tiver mais de um) e devolve o slot onde ele ficou sozinho.</summary>
        public static ItemSlot Separar(BEMaquina m, ItemSlot slot)
        {
            if (slot.StackSize <= 1) return slot;
            var livre = m.Inventory.FirstOrDefault(s => s.Empty);
            if (livre == null) return null;
            livre.Itemstack = slot.TakeOut(1);
            slot.MarkDirty();
            livre.MarkDirty();
            return livre;
        }

        public static string Nome(ItemStack s) => s?.GetName() ?? "?";
    }

    // =====================================================================
    // CARVOEIRA — 4 lenhas viram 1 carvão (igual o minion carvoeiro, mas aos poucos)
    // =====================================================================
    public class TrabalhoCarvoeira : Trabalho
    {
        public override string Code => "carvoeira";
        public override float Consumo => 3;
        public override float Intervalo => 20;
        const int LenhaPorCarvao = 4;

        public override bool Insumo(ItemStack s) => Prod.Game(s, p => p == "firewood" || p == "agedfirewood" || p.StartsWith("firewood-"));

        public override bool TemTrabalho(BEMaquina m) => m.ContarNoBau(Insumo) >= LenhaPorCarvao;

        public override void Trabalhar(BEMaquina m)
        {
            if (m.TirarDoBau(Insumo, LenhaPorCarvao).Sum(s => s.StackSize) < LenhaPorCarvao) return;
            m.Guardar(Prod.Novo(m.Api.World, "game:charcoal", 1));
            m.Som("game:sounds/effect/extinguish1", 0.3f);
        }

        public override string Info(BEMaquina m) =>
            Lang.Get("automacao:info-carvoeira", m.ContarNoBau(Insumo), m.ContarNoBau(s => Prod.Game(s, p => p == "charcoal")));
    }

    // =====================================================================
    // DEFUMADOR — carne crua vira curada/defumada, peixe vira defumado (1 por ciclo)
    // =====================================================================
    public class TrabalhoDefumador : Trabalho
    {
        public override string Code => "defumador";
        public override float Consumo => 3;
        public override float Intervalo => 30;

        static readonly Dictionary<string, string> Vira = new Dictionary<string, string>
        {
            ["fish-raw"] = "game:fish-smoked",
            ["fish-cured"] = "game:fish-cured-smoked",
            ["redmeat-raw"] = "game:redmeat-cured",
            ["poultry-raw"] = "game:poultry-cured",
            ["bushmeat-raw"] = "game:bushmeat-cured",
        };

        static string Destino(ItemStack s) =>
            s?.Collectible?.Code?.Domain == "game" && Vira.TryGetValue(s.Collectible.Code.Path, out var d) ? d : null;

        public override bool Insumo(ItemStack s) => Destino(s) != null;
        public override bool TemTrabalho(BEMaquina m) => m.TemNoBau(Insumo);

        public override void Trabalhar(BEMaquina m)
        {
            var w = m.Api.World;
            // Até 4 pedaços de uma vez (cabem nos ganchos do carrossel)
            foreach (var s in m.TirarDoBau(Insumo, 4))
            {
                var outp = Prod.Novo(w, Destino(s), s.StackSize);
                m.Guardar(outp ?? s);
            }
        }

        public override string Info(BEMaquina m) => Lang.Get("automacao:info-defumador", m.ContarNoBau(Insumo));
    }

    // =====================================================================
    // OLARIA — barro vira tigela/telha/pote/vaso já queimados (porte do oleiro)
    // =====================================================================
    public class TrabalhoOlaria : Trabalho
    {
        public override string Code => "olaria";
        public override float Consumo => 3;
        public override float Intervalo => 15;
        public override string[] Opcoes => new[] { "telhas", "tigelas", "potes", "vasos" };

        public override bool Insumo(ItemStack s) => Prod.Game(s, p => p.StartsWith("clay-"));

        (string code, int custo, int qtd) Receita(BEMaquina m, string cor)
        {
            string queimada = cor == "red" ? "earthyorange" : cor;
            var ligadas = Opcoes.Where(m.Opcao).ToList();
            if (ligadas.Count == 0) ligadas.Add("tigelas");
            // Vai alternando entre as opções ligadas
            int vez = m.Dados.GetInt("vez");
            string faz = ligadas[vez % ligadas.Count];
            switch (faz)
            {
                case "telhas": return ("game:shingle-burned-" + (cor == "blue" ? "black" : cor), 4, 12);
                case "potes": return ("game:crock-" + queimada + "-fired", 2, 1);
                case "vasos": return ("game:flowerpot-" + queimada + "-fired", 4, 1);
                default: return ("game:bowl-" + queimada + "-fired", 1, 1);
            }
        }

        static string Cor(ItemStack s) => s.Collectible.Variant["type"] ?? s.Collectible.Code.Path.Substring(5);

        public override bool TemTrabalho(BEMaquina m)
        {
            var slot = Prod.Slot(m, Insumo);
            if (slot == null) return false;
            var (_, custo, _) = Receita(m, Cor(slot.Itemstack));
            return m.ContarNoBau(s => Insumo(s) && Cor(s) == Cor(slot.Itemstack)) >= custo;
        }

        public override void Trabalhar(BEMaquina m)
        {
            var w = m.Api.World;
            var slot = Prod.Slot(m, Insumo);
            if (slot == null) return;
            string cor = Cor(slot.Itemstack);
            var (code, custo, qtd) = Receita(m, cor);
            var obj = Prod.Pegar(w, code);
            if (obj == null) { code = "game:bowl-" + (cor == "red" ? "earthyorange" : cor) + "-fired"; custo = 1; qtd = 1; obj = Prod.Pegar(w, code); }
            if (obj == null) return;
            var barro = m.TirarDoBau(s => Insumo(s) && Cor(s) == cor, custo);
            if (barro.Sum(s => s.StackSize) < custo) { m.Guardar(barro); return; }
            m.Guardar(Prod.EmPilhas(new ItemStack(obj), qtd));
            m.Dados.SetInt("vez", m.Dados.GetInt("vez") + 1);
        }

        public override string Info(BEMaquina m) => Lang.Get("automacao:info-olaria", m.ContarNoBau(Insumo));
    }

    // =====================================================================
    // BANCADA — conserta ferramenta/armadura gasta com material do mesmo tipo (porte do ferreiro).
    // Metal precisa de carvão no bauzinho. Cada remendo deixa o item um pouco mais "cansado" (teto cai 1%).
    // =====================================================================
    public class TrabalhoBancada : Trabalho
    {
        public override string Code => "bancada";
        public override float Consumo => 3;
        public override float Intervalo => 8;
        public override bool PrecisaEspaco => false;
        public const string RemendosAttr = "bancadaremendos-remendos";

        class Material { public System.Func<ItemStack, bool> Serve; public float Fracao; public bool Metal; }

        static bool Existe(IWorldAccessor w, string path) => w.GetItem(new AssetLocation("game", path)) != null;

        static List<Material> Materiais(IWorldAccessor world, ItemStack tool)
        {
            var list = new List<Material>();
            var coll = tool.Collectible;
            string mat = coll.Variant["metal"] ?? coll.Variant["material"];
            if (coll.Variant["construction"] == "hide") mat = "leather";
            mat ??= coll.FirstCodePart() switch { "bow" or "oar" or "firestarter" => "wood", "sling" => "leather", _ => null };
            if (mat == null) return list;
            if (mat.StartsWith("bone-")) mat = mat.Substring(5);
            else if (mat.StartsWith("bone") && mat.Length > 4) mat = mat.Substring(4);

            if (Existe(world, "ingot-" + mat))
            {
                string m = mat;
                if (Existe(world, "metalbit-" + m)) list.Add(new Material { Serve = s => Prod.Game(s, p => p == "metalbit-" + m), Fracao = 0.10f, Metal = true });
                list.Add(new Material { Serve = s => Prod.Game(s, p => p == "ingot-" + m), Fracao = 0.50f, Metal = true });
                return list;
            }
            switch (mat)
            {
                case "leather": list.Add(new Material { Serve = s => Prod.Game(s, p => p.StartsWith("leather-")), Fracao = 0.25f }); break;
                case "linen": list.Add(new Material { Serve = s => Prod.Game(s, p => p.StartsWith("cloth-")), Fracao = 0.25f }); break;
                case "wood": list.Add(new Material { Serve = s => Prod.Game(s, p => p.StartsWith("plank-")), Fracao = 0.20f }); break;
                case "bone": list.Add(new Material { Serve = s => Prod.Game(s, p => p == "bone"), Fracao = 0.25f }); break;
                case "flint": list.Add(new Material { Serve = s => Prod.Game(s, p => p == "flint"), Fracao = 0.25f }); break;
                default:
                    string r = mat;
                    if (Existe(world, "stone-" + r)) list.Add(new Material { Serve = s => Prod.Game(s, p => p == "stone-" + r), Fracao = 0.25f });
                    list.Add(new Material { Serve = s => Prod.Game(s, p => p == "flint"), Fracao = 0.25f });
                    break;
            }
            return list;
        }

        static bool Carvao(ItemStack s) => Prod.Game(s, p => p == "charcoal" || p.StartsWith("coal-") || p == "coke");

        static int Teto(int max, int remendos) =>
            Math.Max((int)Math.Ceiling(max * 0.6), (int)Math.Floor(max * (1 - 0.01 * remendos)));

        static bool Gasto(ItemStack s)
        {
            var c = s?.Collectible;
            if (c == null) return false;
            int max = c.GetMaxDurability(s);
            if (max <= 1) return false;
            int rem = s.Attributes?.GetInt(RemendosAttr) ?? 0;
            return c.GetRemainingDurability(s) < Teto(max, rem + 1);
        }

        public override bool Insumo(ItemStack s) =>
            Gasto(s) || Carvao(s) || Prod.Game(s, p => p.StartsWith("metalbit-") || p.StartsWith("ingot-") || p.StartsWith("leather-")
                                               || p.StartsWith("cloth-") || p.StartsWith("plank-") || p == "bone" || p == "flint" || p.StartsWith("stone-"));

        (ItemSlot item, ItemSlot mat, Material m)? Proximo(BEMaquina maq)
        {
            var world = maq.Api.World;
            bool temCarvao = maq.TemNoBau(Carvao);
            foreach (var slot in maq.Inventory)
            {
                if (slot.Empty || !Gasto(slot.Itemstack)) continue;
                foreach (var m in Materiais(world, slot.Itemstack))
                {
                    if (m.Metal && !temCarvao) continue;
                    var ms = maq.Inventory.FirstOrDefault(s => !s.Empty && s != slot && m.Serve(s.Itemstack));
                    if (ms != null) return (slot, ms, m);
                }
            }
            return null;
        }

        public override bool TemTrabalho(BEMaquina m) => Proximo(m) != null;

        public override void Trabalhar(BEMaquina maq)
        {
            var achou = Proximo(maq);
            if (achou == null) return;
            var (item, mat, m) = achou.Value;
            var world = maq.Api.World;
            var tool = item.Itemstack;
            var c = tool.Collectible;
            int max = c.GetMaxDurability(tool), cur = c.GetRemainingDurability(tool);
            int rem = (tool.Attributes?.GetInt(RemendosAttr) ?? 0) + 1;

            mat.TakeOut(1); mat.MarkDirty();
            if (m.Metal) maq.TirarDoBau(Carvao, 1);
            c.SetDurability(tool, Math.Min(Teto(max, rem), cur + (int)Math.Ceiling(max * m.Fracao)));
            tool.Attributes.SetInt(RemendosAttr, rem);
            item.MarkDirty();
            maq.MarkDirty(true);
            maq.Som("game:sounds/effect/anvilhit" + (1 + world.Rand.Next(3)), 0.6f);
        }

        public override string Info(BEMaquina m)
        {
            int gastos = m.ContarNoBau(Gasto);
            return gastos == 0 ? Lang.Get("automacao:info-bancada-nada") : Lang.Get("automacao:info-bancada", gastos);
        }
    }

    // =====================================================================
    // FORNALHA — derrete o que o jogo sabe derreter (minério, pepita, metal → lingote) e assa comida.
    // Respeita o SmeltedRatio: 5 pepitas = 1 lingote, por exemplo. Sem molde nem cadinho.
    // =====================================================================
    public class TrabalhoFornalha : Trabalho
    {
        public override string Code => "fornalha";
        public override float Consumo => 8;
        public override float Intervalo => 10;
        /// <summary>A fornalha elétrica chega até 1500 °C (dá pra ferro, aço não).</summary>
        public const int TempMax = 1500;

        public static bool Derrete(IWorldAccessor w, ItemStack s, int tempMax)
        {
            var p = s?.Collectible?.CombustibleProps;
            if (p?.SmeltedStack == null || p.MeltingPoint > tempMax) return false;
            return Prod.Resolver(w, p.SmeltedStack) != null;
        }

        public override bool Insumo(ItemStack s) => s?.Collectible?.CombustibleProps?.SmeltedStack != null;

        ItemSlot Proximo(BEMaquina m) => m.Inventory.FirstOrDefault(s =>
            !s.Empty && Derrete(m.Api.World, s.Itemstack, TempMax) && s.StackSize >= Math.Max(1, s.Itemstack.Collectible.CombustibleProps.SmeltedRatio));

        public override bool TemTrabalho(BEMaquina m) => Proximo(m) != null;

        public override void Trabalhar(BEMaquina m)
        {
            var slot = Proximo(m);
            if (slot == null) return;
            var props = slot.Itemstack.Collectible.CombustibleProps;
            int ratio = Math.Max(1, props.SmeltedRatio);
            // Até 4 "porções" por ciclo
            int porcoes = Math.Min(4, slot.StackSize / ratio);
            var saida = Prod.Resolver(m.Api.World, props.SmeltedStack);
            if (saida == null || porcoes <= 0) return;
            slot.TakeOut(porcoes * ratio);
            slot.MarkDirty();
            m.Guardar(Prod.EmPilhas(saida, saida.StackSize * porcoes));
            m.Som("game:sounds/effect/cooking", 0.4f);
        }

        public override string Info(BEMaquina m)
        {
            var s = Proximo(m);
            return s == null ? Lang.Get("automacao:info-fornalha-nada") : Lang.Get("automacao:info-fornalha", Prod.Nome(s.Itemstack));
        }
    }

    // =====================================================================
    // FOGÃO — refeição de panela (receitas do jogo) se tiver tigela queimada; senão assa/cozinha o que é comida
    // =====================================================================
    public class TrabalhoFogao : Trabalho
    {
        public override string Code => "fogao";
        public override float Consumo => 3;
        public override float Intervalo => 12;
        const int TempMax = 300;

        static bool Tigela(ItemStack s) => Prod.Game(s, p => p.StartsWith("bowl-") && p.EndsWith("-fired"));

        static bool Comida(IWorldAccessor w, ItemStack s)
        {
            var p = s?.Collectible?.CombustibleProps;
            if (p?.SmeltedStack == null || p.MeltingPoint > TempMax) return false;
            if (p.SmeltingType != EnumSmeltType.Cook && p.SmeltingType != EnumSmeltType.Bake) return false;
            return Prod.Resolver(w, p.SmeltedStack) != null;
        }

        public override bool Insumo(ItemStack s) => Tigela(s) || s?.Collectible?.NutritionProps != null
            || s?.Collectible?.CombustibleProps?.SmeltingType == EnumSmeltType.Cook || s?.Collectible?.CombustibleProps?.SmeltingType == EnumSmeltType.Bake;

        /// <summary>Monta uma porção de refeição com o que tem no bauzinho (1 de cada ingrediente obrigatório).</summary>
        static (CookingRecipe r, List<(ItemSlot slot, int qtd)> uso)? Refeicao(BEMaquina m)
        {
            if (!m.TemNoBau(Tigela)) return null;
            List<CookingRecipe> receitas;
            try { receitas = m.Api.GetCookingRecipes(); } catch { return null; }
            if (receitas == null) return null;
            foreach (var r in receitas)
            {
                if (r?.Ingredients == null || !r.Enabled || !r.IsFood) continue;
                var uso = new List<(ItemSlot, int)>();
                bool ok = true;
                foreach (var ing in r.Ingredients)
                {
                    if (ing.MinQuantity <= 0) continue;
                    if (ing.PortionSizeLitres > 0) { ok = false; break; }   // líquidos: deixa pro jogador
                    var slot = m.Inventory.FirstOrDefault(s => !s.Empty && !Tigela(s.Itemstack) && !uso.Any(u => u.Item1 == s)
                                                              && s.StackSize >= ing.MinQuantity && ing.Matches(s.Itemstack));
                    if (slot == null) { ok = false; break; }
                    uso.Add((slot, ing.MinQuantity));
                }
                if (!ok || uso.Count == 0) continue;
                var stacks = uso.Select(u => { var c = u.Item1.Itemstack.Clone(); c.StackSize = u.Item2; return c; }).ToArray();
                try { if (!r.Matches(stacks)) continue; } catch { continue; }
                return (r, uso);
            }
            return null;
        }

        ItemSlot ProximaComida(BEMaquina m) => m.Inventory.FirstOrDefault(s => !s.Empty && Comida(m.Api.World, s.Itemstack));

        public override bool TemTrabalho(BEMaquina m) => Refeicao(m) != null || ProximaComida(m) != null;

        public override void Trabalhar(BEMaquina m)
        {
            var w = m.Api.World;
            var meal = Refeicao(m);
            if (meal != null)
            {
                var (r, uso) = meal.Value;
                var tigela = Prod.Slot(m, Tigela);
                string cor = tigela.Itemstack.Collectible.Variant["color"] ?? "blue";
                var bloco = w.GetBlock(new AssetLocation("game:bowl-" + cor + "-meal")) as BlockMeal;
                if (bloco != null)
                {
                    var conteudo = uso.Select(u => u.slot.TakeOut(u.qtd)).ToArray();
                    foreach (var u in uso) u.slot.MarkDirty();
                    tigela.TakeOut(1);
                    tigela.MarkDirty();
                    var prato = new ItemStack(bloco);
                    bloco.SetContents(r.Code, prato, conteudo, 1);
                    m.Guardar(prato);
                    m.Som("game:sounds/effect/cooking", 0.4f);
                    return;
                }
            }
            var slot = ProximaComida(m);
            if (slot == null) return;
            var props = slot.Itemstack.Collectible.CombustibleProps;
            int ratio = Math.Max(1, props.SmeltedRatio);
            int porcoes = Math.Min(4, slot.StackSize / ratio);
            var saida = Prod.Resolver(w, props.SmeltedStack);
            if (saida == null || porcoes <= 0) return;
            slot.TakeOut(porcoes * ratio);
            slot.MarkDirty();
            m.Guardar(Prod.EmPilhas(saida, saida.StackSize * porcoes));
            m.Som("game:sounds/effect/cooking", 0.3f);
        }

        public override string Info(BEMaquina m)
        {
            var meal = Refeicao(m);
            if (meal != null) return Lang.Get("automacao:info-fogao-refeicao");
            var s = ProximaComida(m);
            return s == null ? Lang.Get("automacao:info-fogao-nada") : Lang.Get("automacao:info-fogao", Prod.Nome(s.Itemstack));
        }
    }

    // =====================================================================
    // FORJA — faz uma receita de bigorna escolhida (◀ ▶ na janela) com os lingotes do bauzinho.
    // Gasta ceil(voxels / 42) lingotes, como no jogo (um lingote = 42 voxels).
    // =====================================================================
    public class TrabalhoForja : Trabalho, IAcoes
    {
        public override string Code => "forja";
        public override float Consumo => 8;
        public override float Intervalo => 20;

        public override bool Insumo(ItemStack s) => Prod.Game(s, p => p.StartsWith("ingot-"));

        static int Voxels(SmithingRecipe r)
        {
            if (r.Voxels == null) return 42;
            int n = 0;
            foreach (bool v in r.Voxels) if (v) n++;
            return Math.Max(1, n);
        }

        public static int Lingotes(SmithingRecipe r) => (int)Math.Ceiling(Voxels(r) / 42.0);

        /// <summary>Receitas que dá pra fazer com algum lingote do bauzinho (agrupadas por metal).</summary>
        static List<(SmithingRecipe r, string metal)> Possiveis(BEMaquina m)
        {
            var outp = new List<(SmithingRecipe, string)>();
            List<SmithingRecipe> todas;
            try { todas = m.Api.GetSmithingRecipes(); } catch { return outp; }
            if (todas == null) return outp;
            var lingotes = m.Inventory.Where(s => !s.Empty && Prod.Game(s.Itemstack, p => p.StartsWith("ingot-"))).Select(s => s.Itemstack).ToList();
            var vistos = new HashSet<string>();
            foreach (var r in todas)
            {
                if (r?.Ingredient == null) continue;
                foreach (var ing in lingotes)
                {
                    bool serve;
                    try { serve = r.Ingredient.SatisfiesAsIngredient(ing, false); } catch { serve = false; }
                    if (!serve) continue;
                    string metal = ing.Collectible.Variant["metal"] ?? ing.Collectible.Code.Path.Substring(6);
                    string key = r.Code + "|" + metal;
                    if (vistos.Add(key)) outp.Add((r, metal));
                }
            }
            return outp.OrderBy(x => x.Item2).ThenBy(x => x.Item1.Code?.ToString()).ToList();
        }

        static ItemStack Saida(BEMaquina m, SmithingRecipe r, string metal)
        {
            var w = m.Api.World;
            var js = r.Output;
            if (js == null) return null;
            // Receitas com {metal} no nome da saída
            if (js.Code != null && js.Code.Path.Contains("{metal}"))
            {
                var loc = new AssetLocation(js.Code.Domain, js.Code.Path.Replace("{metal}", metal));
                var c = js.Type == EnumItemClass.Block ? (CollectibleObject)w.GetBlock(loc) : w.GetItem(loc);
                return c == null ? null : new ItemStack(c, Math.Max(1, js.StackSize));
            }
            return Prod.Resolver(w, js);
        }

        (SmithingRecipe r, string metal)? Escolhida(BEMaquina m)
        {
            var lista = Possiveis(m);
            if (lista.Count == 0) return null;
            int i = m.Dados.GetInt("receita");
            i = ((i % lista.Count) + lista.Count) % lista.Count;
            return lista[i];
        }

        public override bool TemTrabalho(BEMaquina m)
        {
            if (!m.Opcao("fazer")) return false;
            var e = Escolhida(m);
            if (e == null) return false;
            var (r, metal) = e.Value;
            return m.ContarNoBau(s => Prod.Game(s, p => p == "ingot-" + metal)) >= Lingotes(r) && Saida(m, r, metal) != null;
        }

        public override string[] Opcoes => new[] { "fazer" };

        public override void Trabalhar(BEMaquina m)
        {
            var e = Escolhida(m);
            if (e == null) return;
            var (r, metal) = e.Value;
            var saida = Saida(m, r, metal);
            if (saida == null) return;
            int n = Lingotes(r);
            var tirou = m.TirarDoBau(s => Prod.Game(s, p => p == "ingot-" + metal), n);
            if (tirou.Sum(s => s.StackSize) < n) { m.Guardar(tirou); return; }
            m.Guardar(saida);
            m.Som("game:sounds/effect/anvilhit" + (1 + m.Api.World.Rand.Next(3)), 0.7f, 24);
        }

        public IEnumerable<(string code, string texto)> Botoes(BEMaquina m)
        {
            var e = Escolhida(m);
            string nome = e == null ? Lang.Get("automacao:forja-sem-receita") : (Saida(m, e.Value.r, e.Value.metal)?.GetName() ?? "?") + $" ({Lingotes(e.Value.r)})";
            yield return ("ant", "◀ " + Lang.Get("automacao:forja-anterior"));
            yield return ("nome", nome);
            yield return ("prox", Lang.Get("automacao:forja-proxima") + " ▶");
        }

        public void Acao(BEMaquina m, IPlayer p, string acao)
        {
            int i = m.Dados.GetInt("receita");
            if (acao == "ant") i--;
            else if (acao == "prox") i++;
            m.Dados.SetInt("receita", i);
        }

        public override string Info(BEMaquina m)
        {
            var e = Escolhida(m);
            if (e == null) return Lang.Get("automacao:info-forja-nada");
            var (r, metal) = e.Value;
            return Lang.Get("automacao:info-forja", Saida(m, r, metal)?.GetName() ?? "?", Lingotes(r), metal);
        }
    }

    // =====================================================================
    // ALAMBIQUE — pega um recipiente com bebida destilável (vinho, cidra, hidromel...) e destila no próprio recipiente
    // =====================================================================
    public class TrabalhoAlambique : Trabalho
    {
        public override string Code => "alambique";
        public override float Consumo => 3;
        public override float Intervalo => 30;
        public override bool PrecisaEspaco => false;

        static DistillationProps Props(ItemStack liquido)
        {
            var a = liquido?.Collectible?.Attributes?["distillationProps"];
            if (a == null || !a.Exists) return null;
            try { return a.AsObject<DistillationProps>(); } catch { return null; }
        }

        static ItemSlot Proximo(BEMaquina m) => m.Inventory.FirstOrDefault(s =>
        {
            if (s.Empty || s.Itemstack.Collectible is not ILiquidInterface li) return false;
            var cont = li.GetContent(s.Itemstack);
            return cont != null && Props(cont) != null;
        });

        public override bool Insumo(ItemStack s) => s?.Collectible is ILiquidInterface;
        public override bool TemTrabalho(BEMaquina m) => Proximo(m) != null;

        public override void Trabalhar(BEMaquina m)
        {
            var slot = Proximo(m);
            if (slot == null) return;
            slot = Prod.Separar(m, slot);
            if (slot == null) return;
            var li = (ILiquidInterface)slot.Itemstack.Collectible;
            var cont = li.GetContent(slot.Itemstack);
            var props = Props(cont);
            var destilado = Prod.Resolver(m.Api.World, props?.DistilledStack);
            if (destilado == null) return;
            // Mesmo cálculo do condensador do jogo: itens de líquido × ratio
            destilado.StackSize = Math.Max(1, (int)(cont.StackSize * props.Ratio));
            if (slot.Itemstack.Collectible is ILiquidSink sink) sink.SetContent(slot.Itemstack, destilado);
            slot.MarkDirty();
            m.MarkDirty(true);
            m.Som("game:sounds/effect/cooking", 0.4f);
        }

        public override string Info(BEMaquina m)
        {
            var s = Proximo(m);
            if (s == null) return Lang.Get("automacao:info-alambique-nada");
            var cont = ((ILiquidInterface)s.Itemstack.Collectible).GetContent(s.Itemstack);
            return Lang.Get("automacao:info-alambique", Prod.Nome(cont));
        }
    }

    // =====================================================================
    // PRENSA — fruta com juiceableProperties vira suco num balde/jarra/barril vazio do bauzinho; sobra o bagaço
    // =====================================================================
    public class TrabalhoPrensa : Trabalho
    {
        public override string Code => "prensa";
        public override float Consumo => 1;
        public override float Intervalo => 10;

        static JuiceableProperties Props(ItemStack s)
        {
            var a = s?.Collectible?.Attributes?["juiceableProperties"];
            if (a == null || !a.Exists) return null;
            try { return a.AsObject<JuiceableProperties>(null, s.Collectible.Code.Domain); } catch { return null; }
        }

        static bool Fruta(ItemStack s) => Props(s) != null;

        /// <summary>Recipiente que aceita este suco (vazio, ou já com o mesmo suco e com espaço).</summary>
        static ItemSlot Recipiente(BEMaquina m, ItemStack suco)
        {
            return m.Inventory.FirstOrDefault(s =>
            {
                if (s.Empty || s.Itemstack.Collectible is not ILiquidSink || s.Itemstack.Collectible is not ILiquidInterface li) return false;
                if (li.IsFull(s.Itemstack)) return false;
                var cont = li.GetContent(s.Itemstack);
                return cont == null || cont.Equals(m.Api.World, suco, GlobalConstants.IgnoredStackAttributes);
            });
        }

        public override bool Insumo(ItemStack s) => Fruta(s) || s?.Collectible is ILiquidSink;

        ItemSlot ProximaFruta(BEMaquina m) => m.Inventory.FirstOrDefault(s => !s.Empty && Fruta(s.Itemstack));

        public override bool TemTrabalho(BEMaquina m)
        {
            var f = ProximaFruta(m);
            if (f == null) return false;
            var suco = Prod.Resolver(m.Api.World, Props(f.Itemstack).LiquidStack);
            return suco != null && Recipiente(m, suco) != null;
        }

        public override void Trabalhar(BEMaquina m)
        {
            var w = m.Api.World;
            var fruta = ProximaFruta(m);
            if (fruta == null) return;
            var props = Props(fruta.Itemstack);
            var suco = Prod.Resolver(w, props.LiquidStack);
            if (suco == null) return;
            var rec = Recipiente(m, suco);
            if (rec == null) return;
            rec = Prod.Separar(m, rec);
            if (rec == null) return;

            int qtd = Math.Min(8, fruta.StackSize);
            float litros = (props.LitresPerItem ?? 0.3125f) * qtd;
            var cprops = BlockLiquidContainerBase.GetContainableProps(suco);
            float itensPorLitro = cprops?.ItemsPerLitre ?? 100;
            suco.StackSize = Math.Max(1, (int)(litros * itensPorLitro));
            var sink = (ILiquidSink)rec.Itemstack.Collectible;
            int foi = sink.TryPutLiquid(rec.Itemstack, suco, litros);
            if (foi <= 0) return;
            // Usou só as frutas que couberam
            int usadas = Math.Max(1, (int)Math.Ceiling(foi / itensPorLitro / (props.LitresPerItem ?? 0.3125f)));
            usadas = Math.Min(usadas, qtd);
            fruta.TakeOut(usadas);
            fruta.MarkDirty();
            rec.MarkDirty();
            var bagaco = Prod.Resolver(w, props.PressedStack);
            if (bagaco != null) { bagaco.StackSize = Math.Max(1, usadas / 4); m.Guardar(bagaco); }
            m.MarkDirty(true);
            m.Som("game:sounds/effect/squeezehoneycomb", 0.4f);
        }

        public override string Info(BEMaquina m)
        {
            var f = ProximaFruta(m);
            if (f == null) return Lang.Get("automacao:info-prensa-nada");
            var suco = Prod.Resolver(m.Api.World, Props(f.Itemstack).LiquidStack);
            return suco != null && Recipiente(m, suco) == null ? Lang.Get("automacao:info-prensa-semrecipiente") : Lang.Get("automacao:info-prensa", Prod.Nome(f.Itemstack));
        }
    }

    // =====================================================================
    // CURTUME — couro cru (ou em qualquer etapa) vira couro pronto. Com cal ou tanino no bauzinho é 2x mais rápido.
    // Tamanho do couro: pequeno 1, médio 2, grande 3, enorme 5 (igual o barril do jogo).
    // =====================================================================
    public class TrabalhoCurtume : Trabalho
    {
        public override string Code => "curtume";
        public override float Consumo => 1;
        public override float Intervalo => 30;

        static readonly string[] Etapas = { "raw", "soaked", "scraped", "prepared" };
        static readonly Dictionary<string, int> Rende = new Dictionary<string, int> { ["small"] = 1, ["medium"] = 2, ["large"] = 3, ["huge"] = 5 };

        static bool Couro(ItemStack s) => Prod.Game(s, p => p.StartsWith("hide-")) && Etapas.Contains(s.Collectible.Variant["type"]) && Rende.ContainsKey(s.Collectible.Variant["size"] ?? "");

        static bool Ajuda(ItemStack s) => Prod.Game(s, p => p.StartsWith("powder-lime") || p == "lime" || p.StartsWith("quicklime") || p.Contains("tannin") || p == "oakbark");

        public override bool Insumo(ItemStack s) => Couro(s) || Ajuda(s);
        public override bool TemTrabalho(BEMaquina m) => m.TemNoBau(Couro);

        public override void Trabalhar(BEMaquina m)
        {
            // Cada ciclo avança uma etapa; com cal/tanino avança duas
            int passos = m.TirarDoBau(Ajuda, 1).Count > 0 ? 2 : 1;
            var slot = Prod.Slot(m, Couro);
            if (slot == null) return;
            var c = slot.Itemstack.Collectible;
            int etapa = Array.IndexOf(Etapas, c.Variant["type"]) + passos;
            var w = m.Api.World;
            var um = slot.TakeOut(1);
            slot.MarkDirty();
            if (etapa >= Etapas.Length)
            {
                m.Guardar(Prod.Novo(w, "game:leather-normal-plain", Rende[c.Variant["size"]]));
            }
            else
            {
                var prox = Prod.Novo(w, "game:hide-" + Etapas[etapa] + "-" + c.Variant["size"], 1);
                m.Guardar(prox ?? um);
            }
        }

        public override string Info(BEMaquina m) => Lang.Get("automacao:info-curtume", m.ContarNoBau(Couro));
    }

    // =====================================================================
    // TEAR — fibra de linho vira barbante (1:1, como a roca); 4 barbantes viram 1 pano de linho
    // =====================================================================
    public class TrabalhoTear : Trabalho
    {
        public override string Code => "tear";
        public override float Consumo => 1;
        public override float Intervalo => 6;
        public override string[] Opcoes => new[] { "pano" };

        static bool Fibra(ItemStack s) => Prod.Game(s, p => p == "flaxfibers");
        static bool Barbante(ItemStack s) => Prod.Game(s, p => p == "flaxtwine");

        public override bool Insumo(ItemStack s) => Fibra(s) || Barbante(s);

        public override bool TemTrabalho(BEMaquina m) => m.TemNoBau(Fibra) || (m.Opcao("pano") && m.ContarNoBau(Barbante) >= 4);

        public override void Trabalhar(BEMaquina m)
        {
            var w = m.Api.World;
            if (m.Opcao("pano") && m.ContarNoBau(Barbante) >= 4)
            {
                m.TirarDoBau(Barbante, 4);
                m.Guardar(Prod.Novo(w, "game:linen-normal-down", 1));
                return;
            }
            int n = m.TirarDoBau(Fibra, 2).Sum(s => s.StackSize);
            if (n > 0) m.Guardar(Prod.Novo(w, "game:flaxtwine", n));
        }

        public override string Info(BEMaquina m) => Lang.Get("automacao:info-tear", m.ContarNoBau(Fibra), m.ContarNoBau(Barbante));
    }
}
