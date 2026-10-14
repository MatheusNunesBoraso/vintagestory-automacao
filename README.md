<div align="center">

<img src="docs/img/modicon.png" width="128" alt="ícone">

# ⚡ Automação — Vintage Story

**Energia sem fio, máquinas velhas e enferrujadas fazendo o trabalho chato — e um Manual que ensina tudo.**

![Vintage Story 1.22](https://img.shields.io/badge/Vintage%20Story-1.22-6fe8ff?style=for-the-badge)
![Versão](https://img.shields.io/badge/vers%C3%A3o-1.0.0-e0a64a?style=for-the-badge)
![Peças](https://img.shields.io/badge/pe%C3%A7as-43-9cff8f?style=for-the-badge)
![Idioma](https://img.shields.io/badge/idioma-pt--br-ff9ce0?style=for-the-badge)

<img src="docs/img/rede.png" alt="Uma base inteira ligada pela Automação" width="100%">

<sub>Uma base de exemplo com todas as peças da Automação — cada quadrado colorido é o alcance de um Poste de Energia.</sub>

</div>

---

## O que é

A **Automação** traz energia pro Vintage Story do jeito que o jogo merece: nada de cabo, nada de cara de ficção científica.
São máquinas velhas de ferro enferrujado, madeira gasta e cobre esverdeado, com musgo nos cantos — cada uma com motor,
engrenagens que engatam de verdade, uma lampadinha azul que acende quando tem energia e um **bauzinho** de 16 espaços.

- **5 fontes de energia**: água, chuva/raio, vento, sol e lenha.
- **Baterias** guardam a sobra pra noite e pro inverno.
- **Postes de Energia** levam a energia **sem fio, por alcance** (8 blocos pra cada lado). Clicou no poste, vê o alcance e o caminho da energia.
- **36 máquinas** fazem o trabalho chato: moer, peneirar, pescar, serrar, fazer carvão, defumar, colher, tirar mel, cuidar de cogumelo, levar as coisas pros baús, encher cocho, consertar ferramenta, acender tocha, fazer cerâmica, fundir, forjar, prensar fruta, destilar, cozinhar, curtir couro, tecer, chocar ovo, cavar pedreira, achar minério, gelar comida, esquentar a casa, iluminar, irrigar, abrir portão, eletrificar cerca, elevador, calendário com previsão da **tempestade temporal**, estabilizador temporal e a **Sentinela**.
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

## ⚡ Fontes de energia

| | Peça | O que faz | Energia/s |
|---|---|---|---|
| <img src="docs/img/catavento.png" width="150" alt="Cata-vento Gerador"> | **Cata-vento Gerador** | Fonte de energia do vento — pra quem não mora perto de rio. Torre de madeira com hélice de lona velha e dínamo de cobre no cubo; o leme vira ela pro vento sozinho. | gera até 10 |
| <img src="docs/img/gerador.png" width="150" alt="Gerador a Lenha"> | **Gerador a Lenha** | Energia de emergência, em qualquer lugar: caldeirinha a vapor. Bota lenha, tábua ou carvão na fornalha (carvão dura mais), a água ferve, o vapor gira o volante e o volante puxa o dínamo. | gera 3 a 8 |
| <img src="docs/img/solar.png" width="150" alt="Painel Solar"> | **Painel Solar** | Placas de vidro escuro com moldura de cobre velho num cavalete de madeira: viram devagar seguindo o sol. Gera de dia — mais no verão e ao meio-dia, pouco nublado, nada à noite ou com chuva. | gera até ~7 de dia |
| <img src="docs/img/roda.png" width="150" alt="Roda Geradora"> | **Roda Geradora** | Fonte de energia da água. Fica na beira do rio: a correnteza gira a roda, a caixa de engrenagens acelera e o dínamo de cobre gera energia, que sai pelo borne da frente. | gera 2 a 12 |
| <img src="docs/img/torre.png" width="150" alt="Torre de Tempestade"> | **Torre de Tempestade** | Fonte de energia do tempo. Tem 2 andares de altura. Quando chove, a água cai no funil de cobre e gira a turbininha (energia pouca e contínua). | gera 3 a 12 na chuva + raios |

## 🔋 Baterias e postes

| | Peça | O que faz | Energia/s |
|---|---|---|---|
| <img src="docs/img/bateria.png" width="150" alt="Bateria"> | **Bateria** | Guarda energia pra quando a fonte para (noite sem chuva, rio congelado...). Caixote com 4 jarros de barro ligados em série; o marcador da frente mostra a carga em 4 barrinhas e o clique direito mostra o número. | guarda 20 000 · entrega até 40/s |
| <img src="docs/img/poste.png" width="150" alt="Poste de Energia"> | **Poste de Energia** | SEM FIO: o poste manda a energia por alcance. Tudo que estiver dentro do quadrado dele (8 blocos pra cada lado) se liga sozinho — fontes, baterias e máquinas. | alcance 8 blocos pra cada lado |

## ⚙️ Máquinas

| | Peça | O que faz | Energia/s |
|---|---|---|---|
| <img src="docs/img/acendedor.png" width="150" alt="Acendedor de Lampiões"> | **Acendedor de Lampiões** | Versão elétrica do Lamparineiro. | 1 (só de noite) |
| <img src="docs/img/alambique.png" width="150" alt="Alambique"> | **Alambique** | Destila sozinho: bota vinho, cidra, cerveja ou fermentado na panela de cobre e a fornalha elétrica esquenta (o soprador de trás atiça). | 3 |
| <img src="docs/img/aquecedor.png" width="150" alt="Aquecedor"> | **Aquecedor** | Estufa de ferro fundido com resistências em brasa atrás da grade e aletas de radiador: mantém a casa quente num raio (8 blocos) sem fogueira — dentro do alcance a temperatura do corpo não cai no inverno. | 3 (no frio) |
| <img src="docs/img/bancada.png" width="150" alt="Bancada Elétrica"> | **Bancada Elétrica** | Versão elétrica do Ferreiro. | 3 |
| <img src="docs/img/bomba.png" width="150" alt="Bomba d'Água e Irrigador"> | **Bomba d'Água e Irrigador** | Bomba de balancim ("cavalo de pau") na beira da água: o motor gira a caixa de engrenagens, que balança o balancim; ele puxa o pistão do cilindro, que tira água do rio pelo cano. | 1 |
| <img src="docs/img/calendario.png" width="150" alt="Calendário Elétrico"> | **Calendário Elétrico** | Armário de relógio velho que sabe tudo do tempo. Em cima: o relógio com a hora do jogo. Embaixo: o dia e o mês. A fileira do meio é a previsão — hoje / amanhã / depois de amanhã (sol, nublado ou chuva; neve no inverno). | 1 |
| <img src="docs/img/carvoeira.png" width="150" alt="Carvoeira Elétrica"> | **Carvoeira Elétrica** | Versão elétrica do Carvoeiro: bota lenha (ou toras) e ela vira carvão sozinha, sem montar poço de carvão. | 3 |
| <img src="docs/img/cerca.png" width="150" alt="Cerca Elétrica"> | **Cerca Elétrica** | Mourão com isoladores de barro e 3 fios de arame de cobre — coloque um do lado do outro e os fios emendam sozinhos. | 1 |
| <img src="docs/img/chocadeira.png" width="150" alt="Chocadeira"> | **Chocadeira** | Caixa de madeira com tampa de vidro e lâmpada de calor: põe os ovos (galados) na palha e ela mantém a temperatura certa, igual a galinha chocando. O pintinho sai sozinho e fica do lado. | 1 |
| <img src="docs/img/cocho.png" width="150" alt="Cocho Automático"> | **Cocho Automático** | Versão elétrica do Pastor. Bote ração (grão, feno) no silo: a rosca vai soltando no cocho e enche os cochos dos bichos na área sem passar do limite. | 1 |
| <img src="docs/img/colheitadeira.png" width="150" alt="Colheitadeira"> | **Colheitadeira** | Versão elétrica do Colhedor. Coloca no meio da horta: o motor gira o pinhão, que gira a coroa presa na luva do poste, e o braço dá a volta devagar. | 1 |
| <img src="docs/img/colmeia.png" width="150" alt="Colmeia Elétrica"> | **Colmeia Elétrica** | Versão elétrica do Apicultor: o fumegador elétrico acalma as abelhas, a máquina tira os favos das colmeias e skeps da área (sem picada!) e a centrífuga redonda gira os quadros — o motor em pé em cima da ponte toca o eixo direto — separando o mel da cera. | 1 |
| <img src="docs/img/curtume.png" width="150" alt="Curtume Automático"> | **Curtume Automático** | Faz todo o trabalho chato do couro sozinho: bota a pele crua no bauzinho e ela passa pelo barril de cal (solta o pelo), pelo rolo raspador (raspa) e pelo barril de tanino (curte), até sair couro pronto. | 1 |
| <img src="docs/img/defumador.png" width="150" alt="Defumador Elétrico"> | **Defumador Elétrico** | Versão elétrica do Defumador: pendura carne e peixe nos ganchos do carrossel redondo, a grelha elétrica esquenta e solta a fumaça, e o carrossel vai girando pra defumar tudo por igual — em cima do teto o pinhão do motor toca a engrenagem de coroa do eixo. | 3 |
| <img src="docs/img/elevador.png" width="150" alt="Elevador"> | **Elevador** | Substitui o mod Dumbwaiter (o dele vai ser removido, então tire os baús das estações antigas antes, porque elas somem). | 8 por viagem |
| <img src="docs/img/estabilizador.png" width="150" alt="Estabilizador Temporal"> | **Estabilizador Temporal** | A máquina grande: núcleo temporal azul preso entre dois cálices de ferro, com anéis girando em volta e engrenagens nas colunas. | 8 |
| <img src="docs/img/esteira.png" width="150" alt="Esteira Transportadora"> | **Esteira Transportadora** | Versão elétrica do Tropeiro. Esteira de lona velha sobre rolos, entre trilhos de ferro: leva sozinha o que as máquinas produzem (bauzinho de cada uma) pros baús do armazém — respeitando o que cada máquina precisa de insumo. | 1 |
| <img src="docs/img/cogumelos.png" width="150" alt="Estufa de Cogumelos"> | **Estufa de Cogumelos** | Versão elétrica do Cogumeleiro: o motor toca a bomba, que puxa água do barril, sobe pelo cano e o aspersor gira soltando névoa nos troncos de cogumelo da área — nascem mais rápido e mesmo fora da sombra. | 1 |
| <img src="docs/img/fogao.png" width="150" alt="Fogão Elétrico"> | **Fogão Elétrico** | Fogão de ferro fundido de 2 bocas: a panela de barro (cozinha a receita da panela do jogo sozinho, no ponto, e a tampa treme quando ferve) e a chaleira de cobre (ferve água). Embaixo, o forninho com janelinha assa pão e torta. | 3 |
| <img src="docs/img/forja.png" width="150" alt="Forja Automática"> | **Forja Automática** | Forja e bigorna automáticas: o braseiro elétrico esquenta o lingote ou a placa e o martinete (martelo movido a motor) bate sozinho na bigorna, fazendo a receita simples que você escolher no clique direito — placa, pregos, cabeças de ferramenta, rebites. | 8 |
| <img src="docs/img/fornalha.png" width="150" alt="Fornalha Elétrica"> | **Fornalha Elétrica** | Fornalha de barro com resistências elétricas: faz o que a fogueira/forno faz, sem lenha nem carvão. | 8 |
| <img src="docs/img/geladeira.png" width="150" alt="Geladeira"> | **Geladeira** | Geladeira antiga "de motor em cima": armário de tábua forrado de chapa, com 2 portas grossas vedadas com couro (congelador em cima, geladeira embaixo), serpentina de cobre atrás e a caixa redonda do compressor em cima, com a ventoinha girando. | 3 |
| <img src="docs/img/luz.png" width="150" alt="Iluminação Elétrica"> | **Iluminação Elétrica** | Poste de rua velho de ferro fundido, com 2 blocos de altura: pé de pedra, coluna redonda com anéis e uma lanterna pendurada no braço. Acende sozinho quando escurece e apaga quando amanhece, sem óleo nem vela. | 1 (só de noite) |
| <img src="docs/img/moedor.png" width="150" alt="Moedor Elétrico"> | **Moedor Elétrico** | Versão elétrica do Moleiro. Bota grão ou minério no funil: ele cai no olho da mó; o pinhão do motor engata nos pinos da roda de cima e gira a mó (igual moinho antigo). A farinha / minério moído sai pela bica pro caixote. | 3 |
| <img src="docs/img/olaria.png" width="150" alt="Olaria Elétrica"> | **Olaria Elétrica** | Versão elétrica do Oleiro. Torno de oleiro de verdade: o motor encosta uma roda de atrito no volante embaixo da mesa e o vaso gira lá em cima. | 3 |
| <img src="docs/img/painel.png" width="150" alt="Painel da Rede"> | **Painel da Rede** | Quadro de madeira e latão pra pendurar na parede: mostra a rede toda de um jeito fácil. | 1 |
| <img src="docs/img/pedreira.png" width="150" alt="Pedreira Automática"> | **Pedreira Automática** | Bate-estaca de pedreira: o motor lá em cima gira o pinhão, que puxa a cremalheira presa no martelo; o martelo sobe correndo entre as 2 guias de ferro e cai com tudo no buraco. | 8 |
| <img src="docs/img/peneira.png" width="150" alt="Peneira Elétrica"> | **Peneira Elétrica** | Versão elétrica do Garimpeiro. | 3 |
| <img src="docs/img/pesca.png" width="150" alt="Pesca Elétrica"> | **Pesca Elétrica** | Versão elétrica do Pescador. Fica na beira do rio ou lago com a lança por cima da água: o motor gira o tambor, que solta a corda e desce o cesto-rede; espera um pouco e enrola de volta, despejando os peixes no caixote do deque. | 1 |
| <img src="docs/img/portao.png" width="150" alt="Portão Elétrico"> | **Portão Elétrico** | Portão de 2 blocos de largura que abre sozinho quando você (ou alguém da sua lista de amigos) chega perto e fecha depois que passou. À noite fica trancado, e nunca abre pra drifter nem bicho. | 2 (só quando mexe) |
| <img src="docs/img/prensa.png" width="150" alt="Prensa de Frutas"> | **Prensa de Frutas** | Prensa de fuso de verdade: o cesto redondo de aduelas (com 2 aros de ferro) fica apoiado na bacia; o motor lá em cima gira a coroa (a porca do fuso) pelo pinhão, e o fuso desce sem girar, empurrando o disco redondo de prensar contra as frutas. | 1 |
| <img src="docs/img/sentinela.png" width="150" alt="Sentinela Elétrica"> | **Sentinela Elétrica** | A Sentinela agora faz parte da Automação (um mod a menos): a mesma torre de ferro enferrujado que vigia girando e atira virotes em drifters, lobos, ursos, hienas e criaturas temporais — munição infinita, mas cada disparo gasta energia. | 1 vigiando · 3 atirando |
| <img src="docs/img/serraria.png" width="150" alt="Serraria Elétrica"> | **Serraria Elétrica** | Versão elétrica do Lenhador. A tora vai empurrada pela bancada contra a serra circular (o motor de baixo gira a serra pela correia) e sai cortada; 12 tábuas por tora caem no bauzinho (sem gastar serrote). | 8 |
| <img src="docs/img/sonda.png" width="150" alt="Sonda de Minério"> | **Sonda de Minério** | Tripé de ferro com uma broca fininha que gira entrando no chão — é a picareta de prospecção, só que sozinha e no chunk inteiro: o motor pendurado embaixo da caixa gira a coroa da broca pelo pinhão. | 3 |
| <img src="docs/img/tear.png" width="150" alt="Tear Elétrico"> | **Tear Elétrico** | Linho vira pano sozinho: o motor puxa por correia a roda de fiar, que fia o linho, e o tear tece — o liço sobe e desce abrindo os fios, a lançadeira passa no meio e o pente bate a trama. | 1 |
| <img src="docs/img/vigia.png" width="150" alt="Vigia Elétrico"> | **Vigia Elétrico** | Versão elétrica do Vigia: o pinhão do motor gira a engrenagem do holofote, que varre a área de noite. | 1 |

## 📖 O Manual

O **Manual da Automação** é um livro que você ganha automaticamente na primeira vez que entra num mundo com o mod — mundo novo ou já criado.
Perdeu? Faz outro na bancada com **2 papéis + 1 couro**. Clique direito com ele na mão pra abrir.

- **Comece aqui**: como a energia funciona, sua primeira rede, glossário e perguntas frequentes.
- **Fontes, Baterias e Máquinas**: um capítulo por peça, com a receita desenhada.
- **Guia dos 100 dias**: do dia 1 (sílex, gravetos, abrigo) até o ferro e a primeira automação — passando por cobre, bronze, preparar o inverno, o que é o inverno, tempestade temporal e estabilidade.
- **Enciclopédia**: agricultura, cozinha, conservas, animais, caça e pesca, mineração e prospecção, metalurgia, cerâmica, roupas e armaduras, construção, ferramentas, comércio, ruínas e saúde.

## Receitas

Receitas baratas, no espírito do jogo: tábuas, pedra, sílex, gravetos, corda e a **engrenagem enferrujada** em toda máquina;
cobre nas peças elétricas (fontes, bateria, poste). Todas estão no Manual, no capítulo de cada peça.

## Instalação

1. Baixe o `automacao.zip` na aba [Releases](../../releases).
2. Coloque em `%APPDATA%\VintagestoryData\Mods` (não precisa descompactar).
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
