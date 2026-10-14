using System;
using System.Collections.Generic;
using System.Linq;
using Vintagestory.API.Common;
using Vintagestory.API.Common.Entities;
using Vintagestory.API.Config;
using Vintagestory.API.Datastructures;
using Vintagestory.API.MathTools;
using Vintagestory.API.Util;
using Vintagestory.GameContent;

namespace Automacao
{
    // =====================================================================
    // As máquinas que fazem o serviço dos ofícios dos minions (portado do Minions Ofícios / Minion Colhedor /
    // Serraria d'Água). Sem minion andando: a máquina mexe direto no alvo mais perto da área, um por ciclo.
    // =====================================================================

    /// <summary>Ajudas comuns: busca na área com cache (TemTrabalho roda todo segundo) e ponto pra calcular distância.</summary>
    static class Area
    {
        static readonly Dictionary<string, (long ate, List<BlockPos> lista)> cache = new Dictionary<string, (long, List<BlockPos>)>();

        /// <summary>Procura na área da máquina, guardando o resultado por alguns segundos.</summary>
        public static List<BlockPos> Achar(BEMaquina m, string chave, System.Func<BlockPos, Block, bool> teste, long validadeMs = 4000)
        {
            string k = m.Pos + "|" + m.Raio + "|" + chave;
            long agora = m.Api.World.ElapsedMilliseconds;
            if (cache.TryGetValue(k, out var c) && agora < c.ate) return c.lista;
            var lista = m.Procurar(teste);
            cache[k] = (agora + validadeMs, lista);
            if (cache.Count > 4000) cache.Clear();
            return lista;
        }

        /// <summary>Esquece a busca (depois de mexer no mundo).</summary>
        public static void Esquecer(BEMaquina m, string chave) => cache.Remove(m.Pos + "|" + m.Raio + "|" + chave);

        public static Vec3d Centro(BEMaquina m) => m.Pos.ToVec3d().Add(0.5, 0.5, 0.5);

        public static void Som(IWorldAccessor w, string som, BlockPos p, float alcance = 12, float vol = 1)
        {
            w.PlaySoundAt(new AssetLocation(som), p.X + 0.5, p.Y + 0.5, p.Z + 0.5, null, true, alcance, vol);
        }

        public static string L(string key, params object[] args) => Lang.Get("automacao:" + key, args);
    }

    // =====================================================================
    // COLHEITADEIRA — colhe frutinhas dos arbustos e a lavoura madura da área; replanta com a semente
    // =====================================================================
    public class TrabalhoColheitadeira : Trabalho
    {
        public override string Code => "colheitadeira";
        public override float Consumo => 1;
        public override float Intervalo => 3;
        public override string[] Opcoes => new[] { "frutas", "horta", "replantar" };
        public override bool Insumo(ItemStack s) => s?.Collectible?.Code?.Path?.StartsWith("seeds-") == true;

        static string TipoDaPlanta(BlockCrop crop) => crop.Variant["type"] ?? crop.FirstCodePart(1);

        static bool Madura(BEMaquina m, BlockPos pos, Block block)
        {
            if (block is BlockCrop crop)
            {
                if (!m.Opcao("horta") || crop.CropProps == null) return false;
                if (TipoDaPlanta(crop) == "pumpkin") return false;   // a rama da abóbora fica
                return crop.CurrentCropStage >= crop.CropProps.GrowthStages;
            }
            if (!m.Opcao("frutas") || block.EntityClass == null) return false;
            var bush = block.GetBEBehavior<BEBehaviorFruitingBush>(pos);
            return bush?.BState != null && bush.BState.Growthstate == EnumFruitingBushGrowthState.Ripe;
        }

        List<BlockPos> Maduras(BEMaquina m) => Area.Achar(m, "maduras", (p, b) => Madura(m, p, b), 5000)
            .Where(p => Madura(m, p, m.Api.World.BlockAccessor.GetBlock(p))).ToList();

        public override bool TemTrabalho(BEMaquina m) => Maduras(m).Count > 0;

        public override void Trabalhar(BEMaquina m)
        {
            var world = m.Api.World;
            var ba = world.BlockAccessor;
            var pos = m.MaisPerto(Maduras(m), Area.Centro(m), null);
            if (pos == null) return;
            var block = ba.GetBlock(pos);
            var cesta = new List<ItemStack>();

            if (block is BlockCrop crop)
            {
                var drops = (crop.GetDrops(world, pos, null) ?? Array.Empty<ItemStack>()).Where(s => s != null && s.StackSize > 0).ToList();
                string type = TipoDaPlanta(crop);
                var farmland = ba.GetBlockEntity(pos.DownCopy()) as BlockEntityFarmland;
                ba.SetBlock(0, pos);
                ba.TriggerNeighbourBlockUpdate(pos);
                farmland?.OnCropBlockBroken();
                Area.Som(world, "game:sounds/block/plant", pos, 16);
                if (m.Opcao("replantar") && farmland != null && Replantar(m, farmland, crop, type, drops))
                    m.Dados.SetInt("replantou", m.Dados.GetInt("replantou") + 1);
                cesta.AddRange(drops);
            }
            else
            {
                var bush = block.GetBEBehavior<BEBehaviorFruitingBush>(pos);
                if (bush?.BState == null) return;
                var fruta = bush.GetRipeDrops(null);
                bush.BState.Growthstate = EnumFruitingBushGrowthState.Mature;
                bush.BState.TransitionHoursLeft = bush.GetHoursForNextStage();
                bush.BState.MeshDirty = true;
                bush.Blockentity.MarkDirty(true);
                world.PlaySoundAt(bush.HarvestableSound ?? new AssetLocation("game:sounds/block/plant"), pos.X + 0.5, pos.Y + 0.5, pos.Z + 0.5, null, true, 16);
                if (fruta != null) cesta.AddRange(fruta.Where(s => s != null && s.StackSize > 0));
            }
            Area.Esquecer(m, "maduras");
            m.Guardar(cesta);
        }

        static bool Replantar(BEMaquina m, BlockEntityFarmland farmland, BlockCrop crop, string type, List<ItemStack> drops)
        {
            var world = m.Api.World;
            var seedCode = new AssetLocation(crop.Code.Domain, "seeds-" + type);
            var cropBlock = world.GetBlock(new AssetLocation(crop.Code.Domain, "crop-" + type + "-1"));
            if (cropBlock == null || !farmland.CanPlant()) return false;

            ItemStack seed = null;
            var daColheita = drops.FirstOrDefault(s => s.Collectible?.Code != null && s.Collectible.Code.Equals(seedCode));
            if (daColheita != null)
            {
                seed = daColheita.Clone();
                seed.StackSize = 1;
                if (--daColheita.StackSize <= 0) drops.Remove(daColheita);
            }
            else
            {
                seed = m.TirarDoBau(s => s.Collectible.Code.Equals(seedCode), 1).FirstOrDefault();
                if (seed == null) return false;
            }

            var sel = new BlockSelection { Position = farmland.Pos.Copy(), Face = BlockFacing.UP, HitPosition = new Vec3d(0.5, 1, 0.5) };
            try
            {
                if (farmland.TryPlant(cropBlock, new DummySlot(seed), null, sel)) return true;
            }
            catch
            {
                // Sem quem plantou (não tem minion): planta direto
                var acima = farmland.Pos.UpCopy();
                if (world.BlockAccessor.GetBlock(acima).Id == 0)
                {
                    world.BlockAccessor.SetBlock(cropBlock.Id, acima);
                    return true;
                }
            }
            drops.Add(seed);
            return false;
        }

        public override string Info(BEMaquina m) =>
            m.Api.Side == EnumAppSide.Server ? Area.L("info-colheitadeira", Maduras(m).Count, m.Feitos) : Area.L("info-feitos", m.Feitos);
    }

    // =====================================================================
    // MOEDOR — mói grão/minério do bauzinho (mesmas receitas do moinho de mão)
    // =====================================================================
    public class TrabalhoMoedor : Trabalho
    {
        public override string Code => "moedor";
        public override float Consumo => 3;
        public override float Intervalo => 4;

        static ItemStack Moido(ItemStack s) => s?.Collectible?.GrindingProps?.GroundStack?.ResolvedItemstack;
        public override bool Insumo(ItemStack s) => Moido(s) != null;

        public override bool TemTrabalho(BEMaquina m) => m.TemNoBau(s => Moido(s) != null);

        public override void Trabalhar(BEMaquina m)
        {
            // Até 4 de cada vez, como quem gira a mó
            var tirou = m.TirarDoBau(s => Moido(s) != null, 4);
            if (tirou.Count == 0) return;
            var saida = new List<ItemStack>();
            foreach (var g in tirou)
            {
                var o = Moido(g).Clone();
                o.StackSize *= g.StackSize;
                saida.Add(o);
            }
            m.Guardar(saida);
            m.Som("game:sounds/block/quern", 0.6f, 12);
        }

        public override string Info(BEMaquina m) => m.TemNoBau(s => Moido(s) != null)
            ? Area.L("info-moedor", m.ContarNoBau(s => Moido(s) != null)) : Area.L("info-moedor-vazio");
    }

    // =====================================================================
    // PENEIRA — peneira cascalho/areia/terra do bauzinho com a tabela da bateia do jogo
    // =====================================================================
    public class TrabalhoPeneira : Trabalho
    {
        public override string Code => "peneira";
        public override float Consumo => 3;
        public override float Intervalo => 5;

        static bool Peneiravel(ItemStack s) => s?.Block?.Attributes?["pannable"].AsBool(false) == true;
        public override bool Insumo(ItemStack s) => Peneiravel(s);

        public override bool TemTrabalho(BEMaquina m) => m.TemNoBau(Peneiravel);

        public override void Trabalhar(BEMaquina m)
        {
            var tirou = m.TirarDoBau(Peneiravel, 1);
            if (tirou.Count == 0) return;
            var world = m.Api.World;
            var achados = new List<ItemStack>();
            // Como na bateia do jogo: algumas sacudidas por bloco de material
            for (int i = 0; i < 3; i++)
            {
                var a = Bateia.Sortear(world, tirou[0].Block);
                if (a != null) achados.Add(a);
            }
            m.Guardar(achados);
            m.Som("game:sounds/block/sand", 0.7f, 12);
        }

        public override string Info(BEMaquina m) => m.TemNoBau(Peneiravel)
            ? Area.L("info-peneira", m.ContarNoBau(Peneiravel)) : Area.L("info-peneira-vazio");
    }

    /// <summary>A tabela de achados da bateia do próprio jogo (atributo panningDrops).</summary>
    public static class Bateia
    {
        static Dictionary<string, PanningDrop[]> tabela;

        static void Carregar(IWorldAccessor world)
        {
            if (tabela != null) return;
            var pan = world.SearchBlocks(new AssetLocation("game:pan-*")).FirstOrDefault();
            var json = pan?.Attributes?["panningDrops"];
            if (json == null || !json.Exists)
            {
                world.Logger.Error("[Automação] Não achei a tabela de achados da bateia do jogo.");
                tabela = new Dictionary<string, PanningDrop[]>();
                return;
            }
            var t = json.AsObject<Dictionary<string, PanningDrop[]>>();
            bool lore = world.Config.GetAsBool("loreContent", true);
            foreach (var key in t.Keys.ToArray())
            {
                var list = t[key].Where(d => d != null && (lore || !d.ManMade)).ToArray();
                foreach (var d in list)
                    if (!d.Code.Path.Contains("{rocktype}")) d.Resolve(world, "automacao");
                t[key] = list;
            }
            tabela = t;
        }

        public static ItemStack Sortear(IWorldAccessor world, Block fonte)
        {
            Carregar(world);
            string code = fonte?.Code?.ToShortString();
            PanningDrop[] drops = null;
            foreach (var key in tabela.Keys)
                if (code != null && WildcardUtil.Match(key, code)) drops = tabela[key];
            if (drops == null || drops.Length == 0) return null;

            string rock = fonte?.Variant?["rock"] ?? "granite";
            var rand = world.Rand;
            var embaralhado = drops.ToArray();
            embaralhado.Shuffle(rand);
            foreach (var d in embaralhado)
            {
                if (rand.NextDouble() >= d.Chance.nextFloat()) continue;
                ItemStack stack = d.ResolvedItemstack;
                if (d.Code.Path.Contains("{rocktype}"))
                {
                    var loc = new AssetLocation(d.Code.Domain, d.Code.Path.Replace("{rocktype}", rock));
                    CollectibleObject obj = d.Type == EnumItemClass.Block ? world.GetBlock(loc) : world.GetItem(loc);
                    stack = obj != null ? new ItemStack(obj) : null;
                }
                return stack?.Clone();
            }
            return null;
        }
    }

    // =====================================================================
    // PESCA — o cesto-rede desce na água funda da área e volta com peixe (às vezes tralha)
    // =====================================================================
    public class TrabalhoPesca : Trabalho
    {
        public override string Code => "pesca";
        public override float Consumo => 1;
        public override float Intervalo => 12;
        const int AguaMinima = 10;

        public override bool TemTrabalho(BEMaquina m) => m.AcharAgua(Area.Centro(m), null, AguaMinima) != null;

        public override void Trabalhar(BEMaquina m)
        {
            var world = m.Api.World;
            var agua = m.AcharAgua(Area.Centro(m), null, AguaMinima);
            if (agua == null) return;
            Area.Som(world, "game:sounds/environment/smallsplash", agua, 12);
            if (world.Rand.NextDouble() > 0.6) return;   // não beliscou
            bool salgada = world.BlockAccessor.GetBlock(agua, BlockLayersAccess.Fluid)?.Code?.Path?.Contains("saltwater") == true;
            var peixe = Pesca.Sortear(world, salgada);
            if (peixe != null) m.Guardar(peixe);
        }

        public override string Info(BEMaquina m)
        {
            if (m.Api.Side != EnumAppSide.Server) return Area.L("info-feitos", m.Feitos);
            return m.AcharAgua(Area.Centro(m), null, AguaMinima) == null ? Area.L("info-pesca-semagua") : Area.L("info-pesca", m.Feitos);
        }
    }

    /// <summary>Peixe cru do jogo (doce ou salgado), às vezes tralha.</summary>
    public static class Pesca
    {
        static readonly string[] Doce = { "alewife", "bream", "chub", "perch", "crappie", "trout", "bass", "carp", "catfish", "pickerel", "tilapia", "walleye", "salmon" };
        static readonly string[] Salgada = { "herring", "mackerel", "perch", "bream", "haddock", "hake", "pollock", "gurnard", "snapper", "salmon" };
        static readonly (string code, float peso, int qtd)[] Tralha =
        {
            ("stick", 5, 1), ("cattailtops", 4, 1), ("bone", 3, 1), ("rope", 1.5f, 1), ("flint", 1, 1), ("nugget-nativecopper", 0.5f, 1),
        };
        const float TralhaTotal = 15;
        static List<Item> doce, salgada;

        public static ItemStack Sortear(IWorldAccessor world, bool salgadaAgua)
        {
            if (doce == null)
            {
                doce = new List<Item>();
                salgada = new List<Item>();
                foreach (var item in world.Items)
                {
                    var code = item?.Code;
                    if (code == null || code.Domain != "game" || !code.Path.StartsWith("fishraw-") || !code.Path.EndsWith("-adult")) continue;
                    string hab = item.Variant?["habitat"], type = item.Variant?["type"];
                    if (hab == "freshwater" && Doce.Contains(type)) doce.Add(item);
                    else if (hab == "saltwater" && Salgada.Contains(type)) salgada.Add(item);
                }
            }
            var rand = world.Rand;
            double r = rand.NextDouble() * 100;
            if (r < TralhaTotal)
            {
                foreach (var (code, peso, qtd) in Tralha)
                {
                    if (r < peso)
                    {
                        var it = world.GetItem(new AssetLocation("game", code));
                        return it != null ? new ItemStack(it, qtd) : null;
                    }
                    r -= peso;
                }
            }
            var lista = salgadaAgua ? salgada : doce;
            if (lista.Count == 0) lista = salgadaAgua ? doce : salgada;
            return lista.Count == 0 ? null : new ItemStack(lista[rand.Next(lista.Count)]);
        }
    }

    // =====================================================================
    // SERRARIA — tora do bauzinho vira tábua (rendimento das receitas de serrote do jogo; 12/tora)
    // =====================================================================
    public class TrabalhoSerraria : Trabalho
    {
        public override string Code => "serraria";
        public override float Consumo => 8;
        public override float Intervalo => 6;

        static Dictionary<AssetLocation, ItemStack> mapa;
        static List<GridRecipe> feitoDe;

        static Dictionary<AssetLocation, ItemStack> Mapa(IWorldAccessor world)
        {
            var receitas = world.GridRecipes;
            if (mapa != null && ReferenceEquals(feitoDe, receitas)) return mapa;
            var m = new Dictionary<AssetLocation, ItemStack>();
            foreach (var r in receitas)
            {
                if (r == null || !r.Enabled || r.ResolvedIngredients == null) continue;
                var outp = r.Output?.ResolvedItemStack;
                if (outp?.Collectible?.Code == null || !outp.Collectible.Code.Path.StartsWith("plank-")) continue;
                ItemStack entrada = null;
                int ferramentas = 0, outros = 0;
                foreach (var ing in r.ResolvedIngredients)
                {
                    if (ing == null) continue;
                    if (ing.IsTool) { ferramentas++; continue; }
                    outros++;
                    entrada = ing.ResolvedItemStack;
                }
                if (ferramentas != 1 || outros != 1 || entrada?.Collectible?.Code == null) continue;
                string path = entrada.Collectible.Code.Path;
                if (!path.StartsWith("log-") && !path.StartsWith("logsection-")) continue;
                m[entrada.Collectible.Code] = outp.Clone();
            }
            // Tora sem casca: rende o mesmo que a tora da mesma madeira
            foreach (var b in world.Blocks)
            {
                var code = b?.Code;
                if (code == null || !code.Path.StartsWith("debarkedlog-")) continue;
                string wood = b.Variant?["wood"];
                if (wood == null) continue;
                if (m.TryGetValue(new AssetLocation(code.Domain, "log-placed-" + wood + "-ud"), out var p)) m[code] = p.Clone();
            }
            mapa = m;
            feitoDe = receitas;
            return m;
        }

        /// <summary>Tábuas da tora: o rendimento da receita, mas pelo menos 12 (como serrote de verdade).</summary>
        static ItemStack Tabuas(IWorldAccessor world, ItemStack tora)
        {
            if (tora?.Collectible?.Code == null) return null;
            if (Mapa(world).TryGetValue(tora.Collectible.Code, out var p))
            {
                var c = p.Clone();
                if (tora.Collectible.Code.Path.StartsWith("log-")) c.StackSize = Math.Max(c.StackSize, 12);
                return c;
            }
            // Sem receita achada: tora com variante de madeira -> plank-<madeira>
            string wood = tora.Collectible.Variant?["wood"];
            if (wood == null || !tora.Collectible.Code.Path.StartsWith("log")) return null;
            var plank = world.GetItem(new AssetLocation("game", "plank-" + wood));
            return plank != null ? new ItemStack(plank, 12) : null;
        }

        public override bool Insumo(ItemStack s) => s?.Collectible?.Code?.Path?.StartsWith("log") == true
                                                   || s?.Collectible?.Code?.Path?.StartsWith("debarkedlog-") == true;

        public override bool TemTrabalho(BEMaquina m) => m.TemNoBau(s => Tabuas(m.Api.World, s) != null);

        public override void Trabalhar(BEMaquina m)
        {
            var world = m.Api.World;
            var tirou = m.TirarDoBau(s => Tabuas(world, s) != null, 1);
            if (tirou.Count == 0) return;
            var t = Tabuas(world, tirou[0]);
            var saida = new List<ItemStack>();
            for (int n = t.StackSize; n > 0;)
            {
                int q = Math.Min(n, Math.Max(1, t.Collectible.MaxStackSize));
                var s = t.Clone();
                s.StackSize = q;
                saida.Add(s);
                n -= q;
            }
            m.Guardar(saida);
            m.Som("game:sounds/block/chop" + (1 + world.Rand.Next(3)), 0.7f, 16);
        }

        public override string Info(BEMaquina m)
        {
            int toras = m.ContarNoBau(s => Tabuas(m.Api.World, s) != null);
            return toras > 0 ? Area.L("info-serraria", toras) : Area.L("info-serraria-vazio");
        }
    }

    // =====================================================================
    // COLMEIA — tira o favo das colmeias de palha prontas da área, sem matar o enxame
    // =====================================================================
    public class TrabalhoColmeia : Trabalho
    {
        public override string Code => "colmeia";
        public override float Consumo => 1;
        public override float Intervalo => 4;

        static bool Pronta(IWorldAccessor world, BlockPos p, Block b)
        {
            if (!(b is BlockSkep) || b.Variant["type"] != "populated") return false;
            return world.BlockAccessor.GetBlockEntity(p) is BlockEntityBeehive be && be.Harvestable;
        }

        List<BlockPos> Prontas(BEMaquina m) => Area.Achar(m, "colmeias", (p, b) => Pronta(m.Api.World, p, b), 5000)
            .Where(p => Pronta(m.Api.World, p, m.Api.World.BlockAccessor.GetBlock(p))).ToList();

        public override bool TemTrabalho(BEMaquina m) => Prontas(m).Count > 0;

        public override void Trabalhar(BEMaquina m)
        {
            var world = m.Api.World;
            var p = m.MaisPerto(Prontas(m), Area.Centro(m), null);
            if (p == null) return;
            var be = (BlockEntityBeehive)world.BlockAccessor.GetBlockEntity(p);

            // Desmarca "pronta" e começa outro ciclo (como o jogo faz), mas a colmeia continua com as abelhas
            var tree = new TreeAttribute();
            be.ToTreeAttributes(tree);
            tree.SetInt("harvestable", 0);
            tree.SetDouble("harvestableAtTotalHours", world.Calendar.TotalHours + 12.0 * (3.0 + world.Rand.NextDouble() * 8.0));
            be.FromTreeAttributes(tree, world);
            be.MarkDirty(true);

            var favo = world.GetItem(new AssetLocation("game:honeycomb"));
            if (favo != null) m.Guardar(new ItemStack(favo, 2 + world.Rand.Next(3)));
            Area.Som(world, "game:sounds/block/plant", p);
            Area.Esquecer(m, "colmeias");
        }

        public override string Info(BEMaquina m)
        {
            if (m.Api.Side != EnumAppSide.Server) return Area.L("info-feitos", m.Feitos);
            int todas = Area.Achar(m, "skeps", (p, b) => b is BlockSkep && b.Variant["type"] == "populated", 10000).Count;
            return todas == 0 ? Area.L("info-colmeia-nenhuma") : Area.L("info-colmeia", todas, Prontas(m).Count);
        }
    }

    // =====================================================================
    // COGUMELOS — cuida dos Troncos de Cogumelos da área (esvazia a bandeja e ressemeia),
    // coloca troncos do bauzinho na sombra e cata cogumelo do mato.
    // =====================================================================
    public class TrabalhoCogumelos : Trabalho
    {
        public override string Code => "cogumelos";
        public override float Consumo => 1;
        public override float Intervalo => 3;
        public override string[] Opcoes => new[] { "troncos", "plantar", "mato", "semveneno" };
        const int MargemSol = 5;
        const int RaioPlantar = 5;

        static bool EhTronco(Block b) => b?.Code != null && b.Code.Domain == "troncocogumelos" && b.Code.Path.StartsWith("tronco-");

        static BlockEntityContainer Tronco(IBlockAccessor ba, BlockPos p) =>
            EhTronco(ba.GetBlock(p)) ? ba.GetBlockEntity(p) as BlockEntityContainer : null;

        static string Semente(BlockEntity be)
        {
            var t = new TreeAttribute();
            be.ToTreeAttributes(t);
            return t.GetString("seed");
        }

        static bool Venenoso(IWorldAccessor world, ItemStack st) =>
            (st.Collectible.GetNutritionProperties(world, st, null)?.Health ?? 0) < 0;

        static bool Cogumelo(ItemStack st) => st?.Block is BlockMushroom;
        public override bool Insumo(ItemStack s) => EhTronco(s?.Block) || Cogumelo(s);

        bool DoMato(BEMaquina m, BlockPos p, Block b)
        {
            if (!(b is BlockMushroom) || b.Code.Domain != "game" || b.Variant["state"] == "harvested") return false;
            var world = m.Api.World;
            if (m.Opcao("semveneno") && Venenoso(world, new ItemStack(b))) return false;
            return true;
        }

        bool TroncoComServico(BEMaquina m, BlockPos p, Block b, bool temSemente)
        {
            if (!EhTronco(b) || !(m.Api.World.BlockAccessor.GetBlockEntity(p) is BlockEntityContainer be)) return false;
            if (!be.Inventory.Empty) return true;
            return temSemente && Semente(be) == null;
        }

        /// <summary>Lugar na sombra, perto da máquina, com chão firme, pra colocar um tronco novo.</summary>
        BlockPos LugarPraTronco(BEMaquina m)
        {
            var world = m.Api.World;
            var ba = world.BlockAccessor;
            int maxSol = Math.Max(0, world.SunBrightness - MargemSol);
            var lista = new List<BlockPos>();
            int r = Math.Min(m.Raio, RaioPlantar);
            var tmp = new BlockPos(m.Pos.dimension);
            for (int dx = -r; dx <= r; dx++)
                for (int dz = -r; dz <= r; dz++)
                    for (int dy = -2; dy <= 2; dy++)
                    {
                        tmp.Set(m.Pos.X + dx, m.Pos.Y + dy, m.Pos.Z + dz);
                        if (Math.Abs(dx) <= 1 && Math.Abs(dz) <= 1 && dy == 0) continue;   // grudado na máquina, não
                        var b = ba.GetBlock(tmp);
                        if (b.Id != 0 && b.Replaceable < 6000) continue;
                        if (BEMaquina.Agua(ba, tmp)) continue;
                        if (!ba.GetBlock(tmp.DownCopy()).SideSolid[BlockFacing.UP.Index]) continue;
                        if (ba.GetLightLevel(tmp.UpCopy(), EnumLightLevelType.OnlySunLight) > maxSol) continue;
                        bool vizinho = false;
                        foreach (var f in BlockFacing.HORIZONTALS)
                            if (EhTronco(ba.GetBlock(tmp.AddCopy(f)))) { vizinho = true; break; }
                        if (!vizinho) lista.Add(tmp.Copy());
                    }
            return m.MaisPerto(lista, Area.Centro(m), null);
        }

        List<BlockPos> Troncos(BEMaquina m) => Area.Achar(m, "troncos", (p, b) => EhTronco(b), 5000);
        List<BlockPos> Mato(BEMaquina m) => Area.Achar(m, "mato", (p, b) => DoMato(m, p, b), 5000)
            .Where(p => DoMato(m, p, m.Api.World.BlockAccessor.GetBlock(p))).ToList();

        public override bool TemTrabalho(BEMaquina m)
        {
            bool semente = m.TemNoBau(Cogumelo);
            var ba = m.Api.World.BlockAccessor;
            if (m.Opcao("troncos") && Troncos(m).Any(p => TroncoComServico(m, p, ba.GetBlock(p), semente))) return true;
            if (m.Opcao("mato") && Mato(m).Count > 0) return true;
            if (m.Opcao("plantar") && m.TemNoBau(st => EhTronco(st.Block)))
            {
                // Lugar pra tronco é caro de achar: só olha de vez em quando
                long agora = m.Api.World.ElapsedMilliseconds;
                if (agora - m.Dados.GetLong("procurouLugar") > 10000)
                {
                    m.Dados.SetLong("procurouLugar", agora);
                    m.Dados.SetBool("temLugar", LugarPraTronco(m) != null);
                }
                if (m.Dados.GetBool("temLugar")) return true;
            }
            return false;
        }

        public override void Trabalhar(BEMaquina m)
        {
            var world = m.Api.World;
            var ba = world.BlockAccessor;
            var cesta = new List<ItemStack>();
            var c = Area.Centro(m);

            if (m.Opcao("troncos"))
            {
                bool semente = m.TemNoBau(Cogumelo);
                var p = m.MaisPerto(Troncos(m).Where(q => TroncoComServico(m, q, ba.GetBlock(q), semente)), c, null);
                if (p != null)
                {
                    CuidarDoTronco(m, p, cesta);
                    m.Guardar(cesta);
                    return;
                }
            }
            if (m.Opcao("plantar") && m.TemNoBau(st => EhTronco(st.Block)))
            {
                var p = LugarPraTronco(m);
                if (p != null && Plantar(m, p, cesta))
                {
                    Area.Esquecer(m, "troncos");
                    m.Guardar(cesta);
                    return;
                }
            }
            if (m.Opcao("mato"))
            {
                var p = m.MaisPerto(Mato(m), c, null);
                if (p != null) Colher(m, p, ba.GetBlock(p), cesta);
                Area.Esquecer(m, "mato");
            }
            m.Guardar(cesta);
        }

        bool CuidarDoTronco(BEMaquina m, BlockPos p, List<ItemStack> cesta)
        {
            var world = m.Api.World;
            var be = Tronco(world.BlockAccessor, p);
            if (be == null) return false;
            bool fez = false;
            foreach (var slot in be.Inventory)
            {
                if (slot.Empty) continue;
                cesta.Add(slot.TakeOutWhole());
                slot.MarkDirty();
                fez = true;
            }
            if (fez) be.MarkDirty(true);
            if (Semente(be) == null) fez |= Semear(m, be, cesta);
            if (fez) Area.Som(world, "game:sounds/block/plant", p);
            return fez;
        }

        /// <summary>Semeia o tronco com um cogumelo (do que acabou de colher ou do bauzinho), comestível primeiro.</summary>
        bool Semear(BEMaquina m, BlockEntity be, List<ItemStack> cesta)
        {
            var world = m.Api.World;
            ItemStack semente;
            var daCesta = cesta.Where(Cogumelo).OrderBy(st => Venenoso(world, st) ? 1 : 0).FirstOrDefault();
            if (daCesta != null)
            {
                semente = daCesta.Clone();
                semente.StackSize = 1;
                if (--daCesta.StackSize <= 0) cesta.Remove(daCesta);
            }
            else
            {
                var tirou = m.TirarDoBau(st => Cogumelo(st) && !Venenoso(world, st), 1);
                if (tirou.Count == 0) tirou = m.TirarDoBau(Cogumelo, 1);
                semente = tirou.FirstOrDefault();
            }
            if (semente == null) return false;

            var t = new TreeAttribute();
            be.ToTreeAttributes(t);
            t.SetString("seed", semente.Block.Code.ToString());
            t.SetDouble("progress", 0);
            t.SetDouble("cycle", 2.0 + world.Rand.NextDouble() * 2.0);
            be.FromTreeAttributes(t, world);
            be.MarkDirty(true);
            return true;
        }

        bool Colher(BEMaquina m, BlockPos p, Block b, List<ItemStack> cesta)
        {
            if (!DoMato(m, p, b)) return false;
            var world = m.Api.World;
            var ba = world.BlockAccessor;
            var drops = b.GetDrops(world, p, null) ?? Array.Empty<ItemStack>();
            cesta.AddRange(drops.Where(d => d != null && d.StackSize > 0));
            // Os de lado (orelha-de-pau) ficam "colhidos" e voltam; os do chão nascem de novo do micélio
            var colhido = b.Variant["side"] != null ? world.GetBlock(b.CodeWithVariant("state", "harvested")) : null;
            if (colhido != null && colhido.Id != 0) ba.ExchangeBlock(colhido.Id, p);
            else ba.SetBlock(0, p);
            ba.TriggerNeighbourBlockUpdate(p);
            Area.Som(world, "game:sounds/block/plant", p);
            return true;
        }

        bool Plantar(BEMaquina m, BlockPos p, List<ItemStack> cesta)
        {
            var world = m.Api.World;
            var ba = world.BlockAccessor;
            var aqui = ba.GetBlock(p);
            if ((aqui.Id != 0 && aqui.Replaceable < 6000) || !ba.GetBlock(p.DownCopy()).SideSolid[BlockFacing.UP.Index]) return false;
            var tirou = m.TirarDoBau(st => EhTronco(st.Block), 1);
            if (tirou.Count == 0) return false;
            // Deitado com a bandeja virada pra máquina
            var lado = BlockFacing.HorizontalFromAngle((float)Math.Atan2(m.Pos.X - p.X, m.Pos.Z - p.Z));
            var bloco = world.GetBlock(new AssetLocation("troncocogumelos", $"tronco-{lado.Code}-vazia")) ?? tirou[0].Block;
            ba.SetBlock(bloco.Id, p);
            ba.TriggerNeighbourBlockUpdate(p);
            var be = Tronco(ba, p);
            if (be != null) Semear(m, be, cesta);
            Area.Som(world, "game:sounds/block/planks", p);
            m.Dados.SetLong("procurouLugar", 0);
            return true;
        }

        public override string Info(BEMaquina m)
        {
            if (m.Api.Side != EnumAppSide.Server) return Area.L("info-feitos", m.Feitos);
            return Area.L("info-cogumelos", Troncos(m).Count, Mato(m).Count);
        }
    }

    // =====================================================================
    // ESTEIRA — leva o que as outras máquinas da área produziram (bauzinho delas, menos o que elas usam)
    // pros baús da área. Um lote (até 4 pilhas) por ciclo, direto de uma máquina pra um baú.
    // =====================================================================
    public class TrabalhoEsteira : Trabalho
    {
        public override string Code => "esteira";
        public override float Consumo => 1;
        public override float Intervalo => 2;
        public override int RaioPadrao => 12;
        public override bool PrecisaEspaco => false;
        const int PilhasPorVez = 4;

        static bool EhBau(BlockEntity be) => be is BlockEntityGenericTypedContainer;

        /// <summary>O que dá pra levar do bauzinho dessa máquina (não leva o que ela usa pra trabalhar).</summary>
        static IEnumerable<ItemSlot> Produtos(BEMaquina eu, BlockEntity be)
        {
            if (!(be is BEMaquina outra) || outra.Pos.Equals(eu.Pos) || !outra.TemBau) yield break;
            var t = outra.Trabalho;
            if (t == null || t is TrabalhoEsteira) yield break;
            foreach (var s in outra.Inventory)
            {
                if (s.Empty) continue;
                bool usa = false;
                try { usa = t.Insumo(s.Itemstack); } catch { }
                if (!usa) yield return s;
            }
        }

        /// <summary>2 = baú já tem igual com espaço, 1 = tem espaço vazio, 0 = não cabe.</summary>
        static int Cabe(IWorldAccessor world, BlockEntityContainer bau, ItemStack st)
        {
            int nota = 0;
            foreach (var s in bau.Inventory)
            {
                if (s.Empty) nota = Math.Max(nota, 1);
                else if (s.Itemstack.Equals(world, st, GlobalConstants.IgnoredStackAttributes) && s.StackSize < s.Itemstack.Collectible.MaxStackSize) return 2;
            }
            return nota;
        }

        List<BlockPos> Baus(BEMaquina m) => Area.Achar(m, "baus", (p, b) => b.EntityClass != null && EhBau(m.Api.World.BlockAccessor.GetBlockEntity(p)), 6000);
        List<BlockPos> Maquinas(BEMaquina m) => Area.Achar(m, "maquinas", (p, b) => b.Code?.Domain == "automacao" && !p.Equals(m.Pos), 6000);

        BlockPos MelhorBau(BEMaquina m, ItemStack st, Vec3d de)
        {
            var world = m.Api.World;
            var baus = Baus(m)
                .Select(p => (p, be: world.BlockAccessor.GetBlockEntity(p) as BlockEntityContainer))
                .Where(x => x.be != null)
                .Select(x => (x.p, n: Cabe(world, x.be, st)))
                .Where(x => x.n > 0).ToList();
            if (baus.Count == 0) return null;
            int melhor = baus.Max(x => x.n);
            return m.MaisPerto(baus.Where(x => x.n == melhor).Select(x => x.p), de, null);
        }

        (BEMaquina de, List<ItemSlot> slots)? Proxima(BEMaquina m)
        {
            var ba = m.Api.World.BlockAccessor;
            foreach (var p in Maquinas(m).OrderBy(p => p.DistanceSqTo(m.Pos.X, m.Pos.Y, m.Pos.Z)))
            {
                if (!(ba.GetBlockEntity(p) is BEMaquina outra)) continue;
                var slots = Produtos(m, outra).ToList();
                if (slots.Count == 0) continue;
                if (slots.Any(s => MelhorBau(m, s.Itemstack, p.ToVec3d()) != null)) return (outra, slots);
            }
            return null;
        }

        public override bool TemTrabalho(BEMaquina m) => Proxima(m) != null;

        public override void Trabalhar(BEMaquina m)
        {
            var achou = Proxima(m);
            if (achou == null) return;
            var (de, slots) = achou.Value;
            var world = m.Api.World;
            int levou = 0;
            foreach (var s in slots)
            {
                if (levou >= PilhasPorVez || s.Empty) break;
                var bauPos = MelhorBau(m, s.Itemstack, de.Pos.ToVec3d());
                if (bauPos == null || !(world.BlockAccessor.GetBlockEntity(bauPos) is BlockEntityContainer bau)) continue;
                int antes = s.StackSize;
                foreach (var d in bau.Inventory)   // primeiro onde já tem igual
                    if (!s.Empty && !d.Empty && d.Itemstack.Equals(world, s.Itemstack, GlobalConstants.IgnoredStackAttributes))
                        if (s.TryPutInto(world, d, s.StackSize) > 0) d.MarkDirty();
                foreach (var d in bau.Inventory)
                    if (!s.Empty && d.Empty)
                        if (s.TryPutInto(world, d, s.StackSize) > 0) d.MarkDirty();
                if (s.StackSize != antes || s.Empty)
                {
                    s.MarkDirty();
                    bau.MarkDirty(true);
                    levou++;
                }
            }
            if (levou > 0)
            {
                de.MarkDirty(true);
                m.Dados.SetInt("levou", m.Dados.GetInt("levou") + levou);
                m.Som("game:sounds/block/chestopen", 0.4f, 12);
            }
        }

        public override string Info(BEMaquina m)
        {
            if (m.Api.Side != EnumAppSide.Server) return Area.L("info-esteira", m.Dados.GetInt("levou"));
            if (Baus(m).Count == 0) return Area.L("info-esteira-sembau");
            return Area.L("info-esteira", m.Dados.GetInt("levou"));
        }
    }

    // =====================================================================
    // COCHO — enche os cochos com a ração do bauzinho, recolhe os ovos dos ninhos (deixa os que estão chocando),
    // fecha as porteiras de noite e avisa quando nasce filhote.
    // =====================================================================
    public class TrabalhoCocho : Trabalho
    {
        public override string Code => "cocho";
        public override float Consumo => 1;
        public override float Intervalo => 3;
        public override int RaioPadrao => 12;
        public override bool PrecisaEspaco => false;
        public override string[] Opcoes => new[] { "cochos", "ovos", "porteiras", "filhotes" };

        static ItemSlot Racao(BEMaquina m, BlockEntityTrough t)
        {
            var world = m.Api.World;
            var cfgs = t.contentConfigs;
            if (cfgs == null || t.IsFull) return null;
            var dentro = t.Inventory[0];
            foreach (var s in m.Inventory)
            {
                if (s.Empty || ItemSlotTrough.getContentConfig(world, cfgs, s) == null) continue;
                if (!dentro.Empty && !dentro.Itemstack.Equals(world, s.Itemstack, GlobalConstants.IgnoredStackAttributes)) continue;
                return s;
            }
            return null;
        }

        public override bool Insumo(ItemStack s)
        {
            var c = s?.Collectible?.Code;
            if (c == null || c.Domain != "game") return false;
            string p = c.Path;
            return p.StartsWith("grain-") || p.StartsWith("vegetable-") || p == "drygrass" || p.StartsWith("hay-")
                || p.StartsWith("legume-") || p.StartsWith("pressedmash-") || p.StartsWith("rawcassava");
        }

        static bool Chocando(ItemSlot s) => s.Itemstack.Attributes?["chick"] != null;

        bool Precisa(BEMaquina m, BlockPos p)
        {
            var be = m.Api.World.BlockAccessor.GetBlockEntity(p);
            if (be is BlockEntityTrough t) return m.Opcao("cochos") && Racao(m, t) != null;
            if (be is BlockEntityHenBox n) return m.Opcao("ovos") && m.TemEspaco() && n.Inventory.Any(s => !s.Empty && !Chocando(s));
            return false;
        }

        List<BlockPos> Lugares(BEMaquina m) => Area.Achar(m, "cochos", (p, b) => b is BlockTroughBase || b.Code?.Path == "henbox"
            || (b.EntityClass != null && m.Api.World.BlockAccessor.GetBlockEntity(p) is BlockEntityHenBox), 8000);

        public override bool TemTrabalho(BEMaquina m) => Lugares(m).Any(p => Precisa(m, p));

        public override void Trabalhar(BEMaquina m)
        {
            var world = m.Api.World;
            var alvo = m.MaisPerto(Lugares(m).Where(p => Precisa(m, p)), Area.Centro(m), null);
            if (alvo == null) return;
            var be = world.BlockAccessor.GetBlockEntity(alvo);
            bool fez = false;
            if (be is BlockEntityTrough t)
            {
                var de = Racao(m, t);
                if (de == null) return;
                // Respeita o limite do cocho (porções inteiras, até encher)
                var cfg = ItemSlotTrough.getContentConfig(world, t.contentConfigs, de);
                var dentro = t.Inventory[0];
                int q = Math.Max(1, cfg.QuantityPerFillLevel), cap = q * Math.Max(1, cfg.MaxFillLevels);
                int falta = cap - (dentro.Empty ? 0 : dentro.StackSize);
                int foi = Math.Min(falta, de.StackSize) / q * q;
                if (foi > 0)
                {
                    var tirou = de.TakeOut(foi);
                    de.MarkDirty();
                    if (dentro.Empty) dentro.Itemstack = tirou;
                    else dentro.Itemstack.StackSize += foi;
                    dentro.MarkDirty();
                    t.MarkDirty(true);
                    m.MarkDirty(true);
                    fez = true;
                }
            }
            else if (be is BlockEntityHenBox n)
            {
                var ovos = new List<ItemStack>();
                foreach (var s in n.Inventory)
                {
                    if (s.Empty || Chocando(s)) continue;
                    ovos.Add(s.TakeOutWhole());
                    s.MarkDirty();
                    fez = true;
                }
                if (fez) n.MarkDirty(true);
                m.Guardar(ovos);
            }
            if (fez) Area.Som(world, "game:sounds/block/plant", alvo);
        }

        static bool Filhote(Entity e) => e.Alive && (e.Code.Path.Contains("-baby") || e.Code.Path.EndsWith("poult"));

        // Filhotes e porteiras: com ou sem serviço, mas só com energia
        public override void Tick(BEMaquina m, float dt)
        {
            if (!m.Ligada || !m.Energizado) return;
            var world = m.Api.World;
            long agora = world.ElapsedMilliseconds;
            if (agora - m.Dados.GetLong("ultimaConta") < 30000) return;
            m.Dados.SetLong("ultimaConta", agora);

            if (m.Opcao("filhotes"))
            {
                int r = m.Raio + 1;
                var c = m.Pos.ToVec3d().Add(0.5, 0, 0.5);
                var lista = world.GetEntitiesAround(c, r, 8, e => Filhote(e) && Math.Abs(e.Pos.X - c.X) <= r && Math.Abs(e.Pos.Z - c.Z) <= r);
                int n = lista.Length;
                int antes = m.Dados.GetInt("filhotes", -1);
                if (antes >= 0 && n > antes) m.Falar("filhote", true, lista[lista.Length - 1].GetName());
                m.Dados.SetInt("filhotes", n);
            }

            if (m.Opcao("porteiras") && !m.IsDay())
            {
                int noite = (int)Math.Floor(world.Calendar.TotalHours / 24 - 0.5);
                if (m.Dados.GetInt("fechouNaNoite", -1) != noite)
                {
                    m.Dados.SetInt("fechouNaNoite", noite);
                    var ba = world.BlockAccessor;
                    int fechou = 0;
                    foreach (var p in m.Procurar((q, b) => b is BlockBaseDoor d && d.IsOpened() && b.Code.Path.Contains("gate")))
                    {
                        var b = ba.GetBlock(p);
                        var fechada = world.GetBlock(b.CodeWithVariant("state", "closed"));
                        if (fechada == null) continue;
                        ba.ExchangeBlock(fechada.Id, p);
                        ba.MarkBlockDirty(p);
                        fechou++;
                    }
                    if (fechou > 0)
                    {
                        m.Som("game:sounds/block/hewnfancegate", 1, 16);
                        m.Falar("porteira", true, fechou);
                    }
                }
            }
        }

        public override string Info(BEMaquina m)
        {
            if (m.Api.Side != EnumAppSide.Server) return Area.L("info-feitos", m.Feitos);
            var ba = m.Api.World.BlockAccessor;
            var l = Lugares(m);
            int cochos = l.Count(p => ba.GetBlockEntity(p) is BlockEntityTrough);
            int ninhos = l.Count(p => ba.GetBlockEntity(p) is BlockEntityHenBox);
            return Area.L("info-cocho", cochos, ninhos, m.ContarNoBau(Insumo));
        }
    }

    // =====================================================================
    // ACENDEDOR — de noite reacende tocha apagada, troca a queimada e põe tocha nos suportes vazios
    // (com as tochas do bauzinho). O lampião dele também acende (dá luz de verdade).
    // =====================================================================
    public class TrabalhoAcendedor : Trabalho
    {
        public override string Code => "acendedor";
        public override float Consumo => 1;
        public override float Intervalo => 2;
        public override int RaioPadrao => 12;
        public override bool PrecisaEspaco => false;
        public override string[] Opcoes => new[] { "suportes" };

        static bool Tocha(ItemStack s) =>
            s?.Collectible?.Code?.Domain == "game" && s.Collectible.Code.Path.StartsWith("torch-")
            && (s.Collectible.Variant["state"] == "lit" || s.Collectible.Variant["state"] == "extinct");

        public override bool Insumo(ItemStack s) => Tocha(s);

        /// <summary>0 = nada; 1 = só reacender (de graça); 2 = precisa de uma tocha do bauzinho.</summary>
        static int Servico(BEMaquina m, Block b)
        {
            var c = b?.Code;
            if (c == null || c.Domain != "game") return 0;
            if (b is BlockTorch)
                return b.Variant["state"] == "extinct" ? 1 : b.Variant["state"] == "burnedout" ? 2 : 0;
            if (b is BlockTorchHolder h && h.Empty && m.Opcao("suportes") && b.Variant["material"] != "ruined") return 2;
            return 0;
        }

        static bool Pode(BEMaquina m, Block b, bool temTocha)
        {
            int n = Servico(m, b);
            return n == 1 || (n == 2 && temTocha);
        }

        List<BlockPos> Alvos(BEMaquina m)
        {
            bool tem = m.TemNoBau(Tocha);
            var ba = m.Api.World.BlockAccessor;
            return Area.Achar(m, "tochas", (p, b) => b is BlockTorch || b is BlockTorchHolder, 8000)
                .Where(p => Pode(m, ba.GetBlock(p), tem)).ToList();
        }

        public override bool TemTrabalho(BEMaquina m) => !m.IsDay() && Alvos(m).Count > 0;

        public override void Trabalhar(BEMaquina m)
        {
            var world = m.Api.World;
            var ba = world.BlockAccessor;
            var p = m.MaisPerto(Alvos(m), Area.Centro(m), null);
            if (p == null) return;
            var b = ba.GetBlock(p);
            int n = Servico(m, b);
            if (n == 0) return;
            if (n == 2 && m.TirarDoBau(Tocha, 1).Count == 0) return;

            if (b is BlockTorch)
            {
                string tipo = n == 1 ? b.Variant["type"] : "basic";
                var acesa = world.GetBlock(new AssetLocation("game", $"torch-{tipo}-lit-{b.Variant["orientation"]}"))
                         ?? world.GetBlock(b.CodeWithVariant("state", "lit"));
                if (acesa == null) return;
                ba.SetBlock(acesa.Id, p);
            }
            else
            {
                var cheio = world.GetBlock(b.CodeWithVariant("state", "filled"));
                if (cheio == null) return;
                ba.ExchangeBlock(cheio.Id, p);
            }
            ba.MarkBlockDirty(p);
            Area.Som(world, "game:sounds/torch-ignite", p, 16);
            Area.Esquecer(m, "tochas");
        }

        public override string Modo(BEMaquina m)
        {
            if (!m.Ligada || !m.Energizado) return "parado";
            return m.IsDay() ? "dia" : "noite";
        }

        // O lampião só dá luz de verdade de noite (e com energia)
        public override string Estado(BEMaquina m) => m.Ligada && m.Energizado && !m.IsDay() ? "aceso" : "apagado";

        public override string Info(BEMaquina m)
        {
            if (m.Api.Side != EnumAppSide.Server) return Area.L("info-feitos", m.Feitos);
            if (m.IsDay()) return Area.L("info-acendedor-dia", m.ContarNoBau(Tocha));
            return Area.L("info-acendedor", Alvos(m).Count, m.ContarNoBau(Tocha));
        }
    }
}
