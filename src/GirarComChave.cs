using System;
using System.Linq;
using Vintagestory.API.Client;
using Vintagestory.API.Common;
using Vintagestory.API.Config;
using Vintagestory.API.MathTools;
using Vintagestory.GameContent;

namespace Automacao
{
    /// <summary>
    /// Girar o bloco com a chave inglesa do jogo: clique direito gira 90° no sentido horário, esquerdo no anti-horário.
    /// Troca só a variante "side" (ExchangeBlock), então o bauzinho, a carga e o estado continuam os mesmos.
    /// </summary>
    public class BlockBehaviorGirarComChave : BlockBehavior, IWrenchOrientable
    {
        static readonly string[] Order = { "north", "east", "south", "west" };
        static ItemStack[] wrenches;

        public BlockBehaviorGirarComChave(Block block) : base(block) { }

        public void Rotate(EntityAgent byEntity, BlockSelection blockSel, int dir)
        {
            var world = byEntity.World;
            var cur = world.BlockAccessor.GetBlock(blockSel.Position);
            int i = Array.IndexOf(Order, cur?.Variant?["side"]);
            if (i < 0) return;
            int next = (i + (dir < 0 ? 1 : 3)) % 4;
            var nb = world.GetBlock(cur.CodeWithVariant("side", Order[next]));
            if (nb == null || nb.Id == 0) return;
            world.BlockAccessor.ExchangeBlock(nb.Id, blockSel.Position);
            world.BlockAccessor.MarkBlockDirty(blockSel.Position);
        }

        public override string GetPlacedBlockInfo(IWorldAccessor world, BlockPos pos, IPlayer forPlayer)
        {
            return Lang.Get("automacao:girar-chave-info") + "\n";
        }

        public override WorldInteraction[] GetPlacedBlockInteractionHelp(IWorldAccessor world, BlockSelection selection, IPlayer forPlayer, ref EnumHandling handling)
        {
            wrenches ??= world.SearchItems(new AssetLocation("game", "wrench-*")).Select(it => new ItemStack(it)).ToArray();
            if (wrenches.Length == 0) return Array.Empty<WorldInteraction>();
            return new[]
            {
                new WorldInteraction { ActionLangCode = "automacao:girar-chave", MouseButton = EnumMouseButton.Right, Itemstacks = wrenches }
            };
        }
    }
}
