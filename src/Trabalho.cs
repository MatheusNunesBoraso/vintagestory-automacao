using System;
using System.Collections.Generic;
using Vintagestory.API.Common;

namespace Automacao
{
    /// <summary>
    /// O que uma peça da Automação faz. A máquina (BEMaquina) cuida de energia, bauzinho, janela, animação e salvar;
    /// cada Trabalho só diz se gera/gasta energia, se tem serviço e o que faz em cada ciclo.
    /// Tudo roda no servidor, menos o que estiver marcado.
    /// </summary>
    public abstract class Trabalho
    {
        /// <summary>Mesmo código do atributo "trabalho" do bloco (ex.: "moedor").</summary>
        public abstract string Code { get; }

        /// <summary>"fonte", "bateria", "poste" ou "maquina".</summary>
        public virtual string Tipo => "maquina";

        /// <summary>Energia por segundo enquanto trabalha (1 = pouco, 3 = médio, 8 = muito).</summary>
        public virtual float Consumo => 2f;

        /// <summary>Consumo deste segundo (padrão = Consumo). Ex.: a Sentinela gasta mais atirando.</summary>
        public virtual float ConsumoAgora(BEMaquina m) => Consumo;

        /// <summary>Segundos por ciclo de trabalho com energia cheia.</summary>
        public virtual float Intervalo => 4f;

        /// <summary>Área em volta (blocos pra cada lado) pra quem trabalha no mundo.</summary>
        public virtual int RaioPadrao => 8;

        /// <summary>Precisa de espaço no bauzinho pra trabalhar.</summary>
        public virtual bool PrecisaEspaco => true;

        /// <summary>Itens que a máquina usa (não saem no "Pegar tudo" automático de outras máquinas, ex. esteira).</summary>
        public virtual bool Insumo(ItemStack s) => false;

        /// <summary>Liga/desliga extras na janela. Texto em lang: "automacao:opcao-{chave}".</summary>
        public virtual string[] Opcoes => Array.Empty<string>();

        // ---------------- fonte ----------------
        /// <summary>Quanto gera agora (energia por segundo). Chamado 1x por segundo pela rede.</summary>
        public virtual float Gerar(BEMaquina m) => 0;

        // ---------------- bateria ----------------
        public virtual float Capacidade => 0;
        public virtual float TaxaMax => 0;

        // ---------------- máquina ----------------
        /// <summary>Tem serviço agora? (decide se pede energia). Chamado 1x por segundo.</summary>
        public virtual bool TemTrabalho(BEMaquina m) => false;

        /// <summary>Um ciclo de trabalho (a cada Intervalo segundos com energia).</summary>
        public virtual void Trabalhar(BEMaquina m) { }

        /// <summary>Todo segundo, com ou sem energia (alarmes, luz, portão...).</summary>
        public virtual void Tick(BEMaquina m, float dt) { }

        /// <summary>Modo visual (os mesmos do visualizador: animação, o que aparece). null = automático.</summary>
        public virtual string Modo(BEMaquina m) => null;

        /// <summary>Variante "estado" do bloco (só blocos que têm: luz apagado/aceso, portão fechado/aberto). null = automático.</summary>
        public virtual string Estado(BEMaquina m) => null;

        /// <summary>Linhas extras ao olhar o bloco e na janela.</summary>
        public virtual string Info(BEMaquina m) => null;

        /// <summary>Peça movida à mão (Começo à mão): segurar o clique direito usa; não abre janela.</summary>
        public virtual bool Manual => false;

        /// <summary>Peça manual: chamado enquanto o jogador segura o clique (nos dois lados).
        /// segundos = desde que começou a segurar. false = para.</summary>
        public virtual bool Segurar(BEMaquina m, IPlayer p, float segundos) => true;

        /// <summary>Clique direito antes da janela abrir. true = já tratou (não abre a janela).</summary>
        public virtual bool Interagir(BEMaquina m, IPlayer p, BlockSelection sel) => false;

        public virtual void Inicializar(BEMaquina m) { }
        public virtual void Removido(BEMaquina m) { }

        // ---------------------------------------------------------------
        static readonly Dictionary<string, Trabalho> todos = new Dictionary<string, Trabalho>();

        public static void Registrar(Trabalho t) => todos[t.Code] = t;

        public static Trabalho Pegar(string code) => code != null && todos.TryGetValue(code, out var t) ? t : null;

        public static IEnumerable<Trabalho> Todos => todos.Values;
    }

    /// <summary>Peça sem lógica própria ainda (só gasta energia e anima quando ligada).</summary>
    public class TrabalhoSimples : Trabalho
    {
        readonly string code;
        public TrabalhoSimples(string code) { this.code = code; }
        public override string Code => code;
    }
}
