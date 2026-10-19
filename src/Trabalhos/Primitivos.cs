using System;
using Vintagestory.API.Client;
using Vintagestory.API.Common;
using Vintagestory.API.Config;
using Vintagestory.GameContent;

namespace Automacao
{
    // =====================================================================
    // COMEÇO À MÃO — peças primitivas movidas à mão (segurar o clique direito), sem energia.
    // Ajudam a chegar no cobre, na engrenagem e na primeira rede sem pular etapa do jogo.
    // =====================================================================
    public static class Mao
    {
        public static string L(string k, params object[] a) => Lang.Get("automacao:" + k, a);

        /// <summary>Aviso vermelho no meio da tela (só no cliente).</summary>
        public static void Erro(BEMaquina m, string code)
        {
            if (m.Api is ICoreClientAPI capi) capi.TriggerIngameError(m, "automacao-" + code, L("erro-" + code));
        }

        /// <summary>Entrega pro jogador; se não couber, cai em cima da peça.</summary>
        public static void Dar(BEMaquina m, IPlayer p, ItemStack st)
        {
            if (st == null) return;
            p.InventoryManager.TryGiveItemstack(st, true);
            if (st.StackSize > 0) m.Api.World.SpawnItemEntity(st, m.Pos.ToVec3d().Add(0.5, 1.1, 0.5));
        }

        /// <summary>De onde sai o material: a mão; no modo automático, qualquer lugar do inventário (mão primeiro).</summary>
        public static ItemSlot Fonte(BEMaquina m, IPlayer p, System.Func<ItemStack, bool> serve, int min = 1)
        {
            var mao = p.InventoryManager.ActiveHotbarSlot;
            if (mao?.Itemstack != null && serve(mao.Itemstack) && mao.StackSize >= min) return mao;
            if (!m.Auto) return null;
            foreach (var inv in new IInventory[] { p.InventoryManager.GetHotbarInventory(), p.InventoryManager.GetOwnInventory(GlobalConstants.backpackInvClassName) })
            {
                if (inv == null) continue;
                foreach (var slot in inv)
                    if (slot?.Itemstack != null && serve(slot.Itemstack) && slot.StackSize >= min) return slot;
            }
            return null;
        }

        /// <summary>Fechou mais um ciclo de 'ciclo' segundos segurando o clique?</summary>
        public static bool Ciclo(BEMaquina m, float segundos, float ciclo)
        {
            if (segundos < m.ProximoManual + ciclo) return false;
            m.ProximoManual += ciclo;
            return true;
        }
    }

    /// <summary>Peneira de Balanço: cascalho/areia da mão, 4 por vez, com a tabela da bateia do jogo.</summary>
    public class TrabalhoPeneiraBalanco : Trabalho
    {
        public override string Code => "peneira_balanco";
        public override string Tipo => "manual";
        public override bool Manual => true;
        const float Tempo = 3.5f;
        const int PorVez = 4;

        static bool Peneiravel(ItemStack s) => s?.Block?.Attributes?["pannable"].AsBool(false) == true;

        public override bool Segurar(BEMaquina m, IPlayer p, float segundos)
        {
            var slot = Mao.Fonte(m, p, Peneiravel);
            if (slot == null) { Mao.Erro(m, Code); return false; }
            if (m.Api.Side != EnumAppSide.Server) return true;

            if (segundos == 0) m.Som("game:sounds/player/panning", 0.5f);
            if (!Mao.Ciclo(m, segundos, Tempo)) return true;

            var fonte = slot.Itemstack.Block;
            int n = Math.Min(PorVez, slot.StackSize);
            slot.TakeOut(n);
            slot.MarkDirty();
            for (int i = 0; i < n; i++) Mao.Dar(m, p, Bateia.Sortear(m.Api.World, fonte));
            m.Feitos += n;
            m.Som("game:sounds/block/sand", 0.5f);
            // Acabou o que tinha na mão: para (no automático procura mais no inventário na próxima)
            if (slot.Empty && !m.Auto) return false;
            m.Som("game:sounds/player/panning", 0.5f);
            return true;
        }

        public override string Info(BEMaquina m) => Mao.L("info-peneira_balanco");
    }

    /// <summary>Torno de Vara: 2 lenhas da mão = 1 Engrenagem de Madeira.</summary>
    public class TrabalhoTornoVara : Trabalho
    {
        public override string Code => "torno_vara";
        public override string Tipo => "manual";
        public override bool Manual => true;
        const float Tempo = 4f;
        const int Tabuas = 2;   // lenhas por engrenagem

        static bool Tabua(ItemStack s) => s?.Collectible?.Code?.Domain == "game" && (s.Collectible.Code.Path == "firewood" || s.Collectible.Code.Path.StartsWith("plank-"));

        public override bool Segurar(BEMaquina m, IPlayer p, float segundos)
        {
            var slot = Mao.Fonte(m, p, Tabua, Tabuas);
            if (slot == null) { Mao.Erro(m, Code); return false; }
            if (m.Api.Side != EnumAppSide.Server) return true;

            // Rangido da vara ao começar
            if (segundos == 0)
                m.Som("game:sounds/block/woodcreak_" + (1 + m.Api.World.Rand.Next(4)), 0.4f);
            if (!Mao.Ciclo(m, segundos, Tempo)) return true;

            var item = m.Api.World.GetItem(new AssetLocation("automacao", "engrenagemmadeira"));
            if (item == null) return false;
            slot.TakeOut(Tabuas);
            slot.MarkDirty();
            Mao.Dar(m, p, new ItemStack(item));
            m.Feitos++;
            m.Som("game:sounds/block/planks", 0.6f);
            if (slot.StackSize < Tabuas && !m.Auto) return false;
            m.Som("game:sounds/block/woodcreak_" + (1 + m.Api.World.Rand.Next(4)), 0.4f);
            return true;
        }

        public override string Info(BEMaquina m) => Mao.L("info-torno_vara");
    }

    /// <summary>Gerador de Manivela: gera um pouquinho enquanto alguém gira; gasta a fome de quem gira.</summary>
    public class TrabalhoGeradorManivela : Trabalho
    {
        public override string Code => "gerador_manivela";
        public override string Tipo => "fonte";
        public override bool Manual => true;
        const float Geracao = 2f;
        const float FomePorSegundo = 3f;

        public override float Gerar(BEMaquina m) => m.Usando ? Geracao : 0;

        public override bool Segurar(BEMaquina m, IPlayer p, float segundos)
        {
            if (m.Api.Side != EnumAppSide.Server) return true;
            if (!Mao.Ciclo(m, segundos, 1f)) return true;
            p.Entity?.GetBehavior<EntityBehaviorHunger>()?.ConsumeSaturation(FomePorSegundo);
            if (((int)segundos) % 2 == 0) m.Som("game:sounds/block/woodcreak_" + (1 + m.Api.World.Rand.Next(4)), 0.35f);
            return true;
        }

        public override string Info(BEMaquina m) => m.Usando ? null : Mao.L("info-gerador_manivela");
    }
}
