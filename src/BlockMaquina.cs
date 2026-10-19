using System;
using System.Linq;
using System.Text;
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
            if (world.BlockAccessor.GetBlockEntity(blockSel.Position) is BEMaquina be)
            {
                if (be.Trabalho?.Manual == true)
                {
                    // Shift + clique com a mão vazia: liga/desliga o automático (faz o "segurar" por você)
                    if (byPlayer.Entity.Controls.ShiftKey && byPlayer.InventoryManager.ActiveHotbarSlot?.Empty != false)
                    {
                        be.AlternarAuto(byPlayer);
                        return true;
                    }
                    return be.ComecarManual(byPlayer);
                }
                return be.OnInteract(byPlayer, blockSel);
            }
            return base.OnBlockInteractStart(world, byPlayer, blockSel);
        }

        // Peças "Começo à mão": segurar o clique
        public override bool OnBlockInteractStep(float secondsUsed, IWorldAccessor world, IPlayer byPlayer, BlockSelection blockSel)
        {
            if (world.BlockAccessor.GetBlockEntity(blockSel.Position) is BEMaquina be && be.Trabalho?.Manual == true)
                return be.SegurarManual(byPlayer, secondsUsed);
            return base.OnBlockInteractStep(secondsUsed, world, byPlayer, blockSel);
        }

        public override void OnBlockInteractStop(float secondsUsed, IWorldAccessor world, IPlayer byPlayer, BlockSelection blockSel)
        {
            if (world.BlockAccessor.GetBlockEntity(blockSel.Position) is BEMaquina be && be.Trabalho?.Manual == true) be.SoltarManual();
            base.OnBlockInteractStop(secondsUsed, world, byPlayer, blockSel);
        }

        public override bool OnBlockInteractCancel(float secondsUsed, IWorldAccessor world, IPlayer byPlayer, BlockSelection blockSel, EnumItemUseCancelReason cancelReason)
        {
            if (world.BlockAccessor.GetBlockEntity(blockSel.Position) is BEMaquina be && be.Trabalho?.Manual == true) be.SoltarManual();
            return true;
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

        /// <summary>
        /// Dica ao olhar pro bloco: só o estado e os números (a descrição comprida fica no item e no manual),
        /// depois "Gire com a chave inglesa" e o "Mod de @mtnunes", cada um na sua linha.
        /// </summary>
        public override string GetPlacedBlockInfo(IWorldAccessor world, BlockPos pos, IPlayer forPlayer)
        {
            var sb = new StringBuilder();
            try { world.BlockAccessor.GetBlockEntity(pos)?.GetBlockInfo(forPlayer, sb); }
            catch (Exception e) { api.Logger.Error(e); }
            string txt = sb.ToString().TrimEnd();
            foreach (var bh in BlockBehaviors)
            {
                string extra = bh.GetPlacedBlockInfo(world, pos, forPlayer)?.Trim();
                if (!string.IsNullOrEmpty(extra)) txt += (txt == "" ? "" : "\n") + extra;
            }
            return txt + (txt == "" ? "" : "\n") + Lang.Get("automacao:mod-de");
        }

        public override string GetPlacedBlockName(IWorldAccessor world, BlockPos pos) => Lang.Get("automacao:block-" + Code.FirstCodePart());
    }
}
