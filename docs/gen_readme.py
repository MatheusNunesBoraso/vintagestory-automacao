"""Monta o README.md do repositório a partir dos modelos (título, descrição) + fotos em docs/img."""
import io
import contextlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
_trabalho = os.path.join(os.path.dirname(RAIZ), "_modelos3d")
sys.path.insert(0, _trabalho if os.path.isdir(_trabalho) else os.path.join(RAIZ, "modelos"))
sys.path.insert(0, RAIZ)
with contextlib.redirect_stdout(io.StringIO()):
    import gen_modelos as g  # noqa: E402
    import gen_mod as gm  # noqa: E402  (receitas e o que entra no mod)
import json  # noqa: E402

with open(os.path.join(RAIZ, "modinfo.json"), encoding="utf-8") as _f:
    VERSAO = json.load(_f)["version"]

GASTO = {  # energia por segundo enquanto trabalha (fontes: quanto geram)
    "roda": "gera 2 a 12", "torre": "gera 3 a 12 na chuva + raios", "catavento": "gera até 10", "solar": "gera até ~7 de dia",
    "gerador": "gera 3 a 8", "bateria": "guarda 20 000 · entrega até 40/s", "poste": "alcance 8 blocos pra cada lado",
    "colheitadeira": "1", "moedor": "3", "peneira": "3", "pesca": "1", "serraria": "8", "carvoeira": "3", "colmeia": "1",
    "defumador": "3", "vigia": "1", "cogumelos": "1", "esteira": "1", "cocho": "1", "bancada": "3", "acendedor": "1 (só de noite)",
    "olaria": "3", "fornalha": "8", "luz": "1 (só de noite)", "bomba": "1", "geladeira": "3", "elevador": "8 por viagem",
    "forja": "8", "portao": "2 (só quando mexe)", "cerca": "1", "aquecedor": "3 (no frio)", "estabilizador": "8",
    "curtume": "1", "tear": "1", "alambique": "3", "chocadeira": "1", "pedreira": "8", "sonda": "3", "painel": "1",
    "prensa": "1", "fogao": "3", "calendario": "1", "sentinela": "1 vigiando · 3 atirando",
    "peneira_balanco": "à mão (segure o clique)", "torno_vara": "à mão (segure o clique)",
    "gerador_manivela": "gera 2 enquanto gira", "pedestal_raio": "não usa (o raio faz tudo)",
}

NOVIDADES = [
    ("1.3.1", "Pedestal do Raio: alcance de 64 pra **256 blocos** (antes, perto da beirada da região, ele nunca pegava raio) e mostra se agora tem trovoada ou se está frio demais pra raio."),
    ("1.3.0", "**Pedestal do Raio**: encaixe uma Engrenagem Enferrujada e, na tempestade, o raio de verdade do jogo cai nele e ela vira **Engrenagem Temporal**. "
              "Luz, Poste, Torre de Tempestade, Painel Solar, Estabilizador e Calendário voltaram a pedir **vidro** (estavam pedindo lenha por engano)."),
    ("1.2.0", "Começo à mão sem tábua (tábua precisa de serra de metal): agora é lenha, graveto, capim seco, sílex e pedra solta. "
              "**Modo automático**: Shift + clique com a mão vazia e a peça trabalha sozinha enquanto você está por perto."),
    ("1.1.0", "**Começo à mão**: Peneira de Balanço, Torno de Vara (faz a **Engrenagem de Madeira**, que serve nas fontes de energia) e Gerador de Manivela. "
              "Estufa de Cogumelos cultiva até 2 espécies por bloco, sem precisar de tronco."),
    ("1.0.1", "Janela das máquinas refeita: nada de texto por cima dos botões, chavinhas nas opções e o botão **Como funciona?** que abre o Manual no capítulo da peça."),
]


def grade(padrao):
    return "<br>".join("<code>" + "".join(f"[{c if c != ' ' else '&nbsp;'}]" for c in linha.ljust(3)) + "</code>" for linha in padrao)


def receitas(itens):
    linhas = ["| Peça | Receita (bancada 3x3) | Ingredientes |", "|---|---|---|"]
    for k, m in itens:
        padrao = gm.RECEITAS.get(k, gm.RECEITA_PADRAO)
        letras = sorted({c for linha in padrao for c in linha if c != " "})
        ing = " · ".join(f"**{c}** {gm.NOMES_ING[c]}" for c in letras)
        if m["auto"].get("cat") == "energia" and "G" in letras:
            ing += " <sub>(ou Engrenagem de Madeira no lugar da enferrujada)</sub>"
        linhas.append(f"| {m['title']} | {grade(padrao)} | {ing} |")
    return "\n".join(linhas)


def resumo(desc, n=230):
    d = desc.split(". ")
    out = ""
    for frase in d:
        if len(out) + len(frase) > n and out:
            break
        out += frase.rstrip(".") + ". "
    return out.strip()


def tabela(itens):
    linhas = ["| | Peça | O que faz | Energia/s |", "|---|---|---|---|"]
    for k, m in itens:
        img = f'<img src="docs/img/{k}.png" width="150" alt="{m["title"]}">'
        linhas.append(f"| {img} | **{m['title']}** | {resumo(m['auto']['desc'])} | {GASTO.get(k, '—')} |")
    return "\n".join(linhas)


def main():
    mods = gm.mods()
    por_cat = lambda c: sorted([(k, m) for k, m in mods.items() if m["auto"].get("cat") == c], key=lambda x: x[1]["title"])
    n_maq = len(por_cat("maquina"))
    md = f"""<div align="center">

<img src="docs/img/modicon.png" width="128" alt="ícone">

# ⚡ Automação — Vintage Story

**Energia sem fio, máquinas velhas e enferrujadas fazendo o trabalho chato — e um Manual que ensina tudo.**

![Vintage Story 1.22](https://img.shields.io/badge/Vintage%20Story-1.22-6fe8ff?style=for-the-badge)
![Versão](https://img.shields.io/badge/vers%C3%A3o-{VERSAO}-e0a64a?style=for-the-badge)
![Peças](https://img.shields.io/badge/pe%C3%A7as-{len(mods)}-9cff8f?style=for-the-badge)
![Idioma](https://img.shields.io/badge/idioma-pt--br-ff9ce0?style=for-the-badge)

<img src="docs/img/rede.png" alt="Uma base inteira ligada pela Automação" width="100%">

<sub>Uma base de exemplo com todas as peças da Automação — cada quadrado colorido é o alcance de um Poste de Energia.</sub>

</div>

---

## O que é

A **Automação** traz energia pro Vintage Story do jeito que o jogo merece: nada de cabo, nada de cara de ficção científica.
São máquinas velhas de ferro enferrujado, madeira gasta e cobre esverdeado, com musgo nos cantos — cada uma com motor,
engrenagens que engatam de verdade, uma lampadinha azul que acende quando tem energia e um **bauzinho** de 16 espaços.

- **{len(por_cat('energia'))} fontes de energia**: água, chuva/raio, vento, sol e lenha.
- **Baterias** guardam a sobra pra noite e pro inverno.
- **Postes de Energia** levam a energia **sem fio, por alcance** (8 blocos pra cada lado). Clicou no poste, vê o alcance e o caminho da energia.
- **{n_maq} máquinas** fazem o trabalho chato: moer, peneirar, pescar, serrar, fazer carvão, defumar, colher, tirar mel, cuidar de cogumelo, levar as coisas pros baús, encher cocho, consertar ferramenta, acender tocha, fazer cerâmica, fundir, forjar, prensar fruta, destilar, cozinhar, curtir couro, tecer, chocar ovo, cavar pedreira, achar minério, gelar comida, esquentar a casa, iluminar, irrigar, abrir portão, eletrificar cerca, elevador, calendário com previsão da **tempestade temporal**, estabilizador temporal e a **Sentinela**.
- **Começo à mão**: {len(por_cat('primitivo'))} peças movidas no braço (segurar o clique), sem energia, pra chegar no cobre e na primeira rede sem pular etapa.
- **Pedestal do Raio**: o raio da tempestade transforma Engrenagem Enferrujada em **Engrenagem Temporal**.
- **O Manual**: você ganha na primeira vez que entra no mundo (novo ou já criado) e também dá pra fazer. Tem o guia de cada peça com a receita e um **guia completo dos primeiros 100 dias**: inverno, comida, metalurgia, animais, perigos, tempestade temporal e dicas de veterano.

## Como a energia funciona

```mermaid
flowchart LR
    R[🌊 Roda Geradora] --> P1((Poste))
    T[⛈️ Torre de Tempestade] --> P1
    S[☀️ Painel Solar] --> P1
    V[🌬️ Cata-vento] --> P1
    G[🔥 Gerador a Lenha] --> P1
    P1 <--> B[(🔋 Baterias)]
    P1 -. alcance .-> P2((Poste))
    P2 --> M1[⚙️ Máquinas]
    P1 --> M2[⚙️ Máquinas]
```

1. Toda **fonte**, **bateria** e **máquina** dentro do alcance de um **Poste de Energia** (8 blocos pra cada lado, 8 pra cima/baixo) entra na rede dele, sozinha.
2. Postes que alcançam um ao outro viram **uma rede só** — dá pra levar energia longe.
3. A cada segundo a rede soma o que as fontes geram e o que as máquinas pedem. Sobrou? Vai pras baterias. Faltou? As baterias cobrem. Acabou tudo? As máquinas param e a lampadinha apaga.
4. No mundo a energia é **invisível**. Na janela do poste tem **Mostrar alcance** e **Ver conexões** (desenha o caminho por alguns segundos).
5. Toda peça **gira com a chave inglesa** do jogo e mostra o estado ao olhar pra ela.

## 🆕 Novidades

{chr(10).join(f"- **{v}** — {t}" for v, t in NOVIDADES)}

## 🪵 Começo à mão

Sem energia: segure o clique direito pra usar (ou **Shift + clique com a mão vazia** pro modo automático).

{tabela(por_cat('primitivo') + por_cat('pedestal'))}

### ⛈️ Pedestal do Raio

Encaixe uma **Engrenagem Enferrujada** no berço (clique direito com ela na mão) e deixe o pedestal **a céu aberto**.
Quando tem **trovoada** (chuva comum não solta raio, e o jogo só solta raio com **12°C ou mais**), ele puxa pra ele os raios de verdade que caem até **256 blocos** dali: o raio desce pela vara de ponta de sílex,
passa pela lasca que encosta na engrenagem e ela vira **Engrenagem Temporal**. Uma por raio. Clique com a mão vazia pra pegar.
Olhe pro pedestal pra saber se agora tem trovoada ou se está frio demais. Cuidado: o raio machuca quem estiver perto!

## ⚡ Fontes de energia

{tabela(por_cat('energia'))}

## 🔋 Baterias e postes

{tabela(por_cat('bateria'))}

## ⚙️ Máquinas

{tabela(por_cat('maquina'))}

## 📖 O Manual

O **Manual da Automação** é um livro que você ganha automaticamente na primeira vez que entra num mundo com o mod — mundo novo ou já criado.
Perdeu? Faz outro na bancada com **2 papéis + 1 couro**. Clique direito com ele na mão pra abrir.

- **Comece aqui**: como a energia funciona, sua primeira rede, glossário e perguntas frequentes.
- **Fontes, Baterias e Máquinas**: um capítulo por peça, com a receita desenhada.
- **Guia dos 100 dias**: do dia 1 (sílex, gravetos, abrigo) até o ferro e a primeira automação — passando por cobre, bronze, preparar o inverno, o que é o inverno, tempestade temporal e estabilidade.
- **Enciclopédia**: agricultura, cozinha, conservas, animais, caça e pesca, mineração e prospecção, metalurgia, cerâmica, roupas e armaduras, construção, ferramentas, comércio, ruínas e saúde.

## Receitas

Receitas baratas, no espírito do jogo: o **Começo à mão** sai só com lenha, graveto, capim seco, sílex e pedra solta;
as máquinas usam tábuas, pedra, sílex, gravetos, corda e a **engrenagem enferrujada**; cobre e **vidro** nas peças elétricas.
Também estão no Manual, no capítulo de cada peça. As letras abaixo mostram a grade da bancada (`[ ]` = vazio).

<details><summary><b>🪵 Começo à mão</b></summary>

{receitas(por_cat('primitivo') + por_cat('pedestal'))}

</details>

<details><summary><b>⚡ Fontes de energia</b></summary>

{receitas(por_cat('energia'))}

</details>

<details><summary><b>🔋 Baterias e postes</b></summary>

{receitas(por_cat('bateria'))}

</details>

<details><summary><b>⚙️ Máquinas</b></summary>

{receitas(por_cat('maquina'))}

</details>

## Instalação

1. Baixe o `automacao.zip` na aba [Releases](../../releases).
2. Coloque em `%APPDATA%\\VintagestoryData\\Mods` (não precisa descompactar).
3. Precisa estar no servidor **e** no cliente. Vintage Story **1.22**.

> **Vindo da Sentinela?** A Sentinela agora faz parte da Automação (Sentinela Elétrica). Tire o mod `sentinela`: a Automação traz um remapeamento pras sentinelas antigas virarem a nova (se o jogo perguntar, aceite).
> **Vindo do Dumbwaiter?** O Elevador da Automação faz o mesmo (anda entre estações e manda baús). Tire os baús das estações antigas antes de remover o outro mod.

## Pra quem quer mexer

- `src/` — o mod em C# (.NET 10). O núcleo é `BEMaquina` (bauzinho, energia, janela), `RedeEnergia` (rede sem fio), `MaquinaRenderer` (anima as partes) e `src/Trabalhos/` (o que cada máquina faz).
- `modelos/` — os modelos 3D são **gerados por código** (`auto_*.py`, com o kit de peças em `gen_modelos.py`). `checa_flutuando.py` e `checa_sobreposto.py` garantem que nenhuma peça flutua nem se sobrepõe.
- `gen_mod.py` — transforma os modelos em assets do jogo (shapes, blocktypes, lang, receitas, Manual).
- Compilar: `py -I gen_mod.py` e depois `dotnet build -c Release` (já empacota e instala o zip).

---

<div align="center">

Mod de **@mtnunes** · feito com carinho (e muita ferrugem) pra comunidade de Vintage Story

</div>
"""
    with open(os.path.join(RAIZ, "README.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print("README ok:", len(mods), "peças")


if __name__ == "__main__":
    main()
