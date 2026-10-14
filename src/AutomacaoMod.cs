using System;
using System.Linq;
using System.Reflection;
using Vintagestory.API.Common;
using Vintagestory.API.Config;
using Vintagestory.API.Server;

namespace Automacao
{
    public class AutomacaoMod : ModSystem
    {
        public override void Start(ICoreAPI api)
        {
            api.RegisterBlockClass("BlockMaquina", typeof(BlockMaquina));
            api.RegisterBlockEntityClass("BEMaquina", typeof(BEMaquina));
            api.RegisterBlockBehaviorClass("AutomacaoGirarChave", typeof(BlockBehaviorGirarComChave));
            api.RegisterItemClass("ItemManualAutomacao", typeof(ItemManual));

            // Todos os Trabalho do assembly se registram sozinhos
            foreach (var t in typeof(AutomacaoMod).Assembly.GetTypes())
            {
                if (t.IsAbstract || !typeof(Trabalho).IsAssignableFrom(t) || t == typeof(TrabalhoSimples)) continue;
                if (t.GetConstructor(Type.EmptyTypes) == null) continue;
                try { Trabalho.Registrar((Trabalho)Activator.CreateInstance(t)); }
                catch (Exception e) { api.Logger.Warning("[Automação] não registrei {0}: {1}", t.Name, e.Message); }
            }
        }

        public override void AssetsFinalize(ICoreAPI api)
        {
            // Bloco com trabalho que ainda não tem classe: vira "simples" (anima quando tem energia)
            foreach (var b in api.World.Blocks)
            {
                if (b?.Code?.Domain != "automacao") continue;
                string code = b.Attributes?["trabalho"].AsString();
                if (code != null && Trabalho.Pegar(code) == null) Trabalho.Registrar(new TrabalhoSimples(code));
            }
        }

        public override void StartServerSide(ICoreServerAPI api)
        {
            // O Manual: todo jogador ganha um na primeira vez que entra (mundo novo ou já criado)
            api.Event.PlayerNowPlaying += player =>
            {
                var attrs = player.Entity?.WatchedAttributes;
                if (attrs == null || attrs.GetBool("automacaoManualRecebido")) return;
                var item = api.World.GetItem(new AssetLocation("automacao", "manual"));
                if (item == null) return;
                var stack = new ItemStack(item);
                if (!player.InventoryManager.TryGiveItemstack(stack, true))
                    api.World.SpawnItemEntity(stack, player.Entity.Pos.XYZ);
                attrs.SetBool("automacaoManualRecebido", true);
                player.SendMessage(GlobalConstants.GeneralChatGroup, Lang.GetL(player.LanguageCode, "automacao:manual-ganhou"), EnumChatType.Notification);
            };
        }
    }
}
