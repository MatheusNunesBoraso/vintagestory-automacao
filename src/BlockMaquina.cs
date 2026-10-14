using System;
using System.Linq;
using Vintagestory.API.Common;
using Vintagestory.API.Config;
using Vintagestory.API.MathTools;
using Vintagestory.GameContent;

namespace Automacao
{
    /// <summary>Bloco de toda peça da Automação: ao colocar, a frente vira pro jogador; clique direito vai pro BEMaquina.</summary>
    public class BlockMaquina : Block
    {
        public override bool TryPlaceBlock(IWorldAccessor world, IPlayer byPlayer, ItemStack itemstack, BlockSelection blockSel, ref string failureCode)
        {
            if (!CanPlaceBlock(world, byPlayer, blockSel, ref failureCode)) return false;
            // Frente do modelo = sul (+z). Vira pro lado de onde o jogador está olhando.
            var facing = BlockFacing.HorizontalFromAngle(byPlayer.Entity.Pos.Yaw).Opposite;
            var block = world.GetBlock(CodeWithVariant("side", facing.Code)) ?? this;
            world.BlockAccessor.SetBlock(block.Id, blockSel.Position, itemstack);
            return true;
        }

        public override bool OnBlockInteractStart(IWorldAccessor world, IPlayer byPlayer, BlockSelection blockSel)
        {
            // Chave inglesa: deixa o comportamento de girar cuidar
            var hand = byPlayer.InventoryManager.ActiveHotbarSlot?.Itemstack;
            if (hand?.Collectible?.Code?.Path?.StartsWith("wrench") == true) return base.OnBlockInteractStart(world, byPlayer, blockSel);
            if (world.BlockAccessor.GetBlockEntity(blockSel.Position) is BEMaquina be) return be.OnInteract(byPlayer, blockSel);
            return base.OnBlockInteractStart(world, byPlayer, blockSel);
        }

        public override ItemStack[] GetDrops(IWorldAccessor world, BlockPos pos, IPlayer byPlayer, float dropQuantityMultiplier = 1)
        {
            // Sempre volta o bloco "de frente pro sul" (o do inventário), não a variante girada
            var b = world.GetBlock(CodeWithVariant("side", "south")) ?? this;
            return new[] { new ItemStack(b) };
        }

        public override ItemStack OnPickBlock(IWorldAccessor world, BlockPos pos)
        {
            var b = world.GetBlock(CodeWithVariant("side", "south")) ?? this;
            return new ItemStack(b);
        }

        public override string GetPlacedBlockName(IWorldAccessor world, BlockPos pos) => Lang.Get("automacao:block-" + Code.FirstCodePart());
    }
}
