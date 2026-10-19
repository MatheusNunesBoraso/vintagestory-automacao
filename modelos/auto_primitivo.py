"""
AUTOMAÇÃO — Começo à mão: 4 peças primitivas (madeira, folhas, sílex, pedra, couro) que ajudam a
chegar no cobre, na engrenagem e na primeira rede sem pular etapa do jogo. Tudo movido à mão
(segurar o clique).

  Peneira de Balanço  — peneira suspensa por cordas num cavalete; balança e peneira 4 cascalhos.
  Torno de Vara       — torno de pedal com vara-mola; tábua vira Engrenagem de Madeira.
  Gerador de Manivela — caixote com rotor de cobre entre 2 pedras-ímã; gira a manivela, sai energia.
  Fole de Couro       — fole de tábua e couro ao lado da fogueira/forno; esquenta e poupa lenha.

Regras do usuário: nada flutuando, nada sobreposto, coerência mecânica (eixo no centro, redondo
gira em furo, corda vai de ponto a ponto).
"""
import math

TEX = {
    "silex": "game:block/stone/flint",
    "areia": "game:block/stone/sand/andesite",
    "pepita": "game:item/resource/nugget/nativecopper",
    "ima": "game:block/stone/rock/basalt1",
}

T8 = math.tan(math.pi / 8)


def disco(box, nome, c, r, a0, a1, tex, eixo="y"):
    """Cilindro octogonal (4 fatias giradas), igual ao do auto_maq_j. r = raio até a face."""
    w = 2 * r * T8
    out = []
    for i in range(4):
        s = i * 0.02
        if eixo == "y":
            f, t, o = [c[0] - r, a0 + s, c[2] - w / 2], [c[0] + r, a1 - s, c[2] + w / 2], [c[0], a0, c[2]]
        elif eixo == "x":
            f, t, o = [a0 + s, c[1] - r, c[2] - w / 2], [a1 - s, c[1] + r, c[2] + w / 2], [a0, c[1], c[2]]
        else:
            f, t, o = [c[0] - r, c[1] - w / 2, a0 + s], [c[0] + r, c[1] + w / 2, a1 - s], [c[0], c[1], a0]
        out.append(box(f"{nome}{i}", f, t, tex, {eixo: 45 * i} if i else None, o if i else None))
    return out


def dentes_x(box, nome, cy, cz, x0, x1, r0, r1, larg, n, tex):
    """Dentes de engrenagem em volta do eixo X (engrenagem em pé)."""
    out = []
    for i in range(n):
        a = 360 / n * i
        out.append(box(f"{nome}{i}", [x0, cy + r0, cz - larg / 2], [x1, cy + r1, cz + larg / 2], tex,
                       {"x": a} if a else None, [x0, cy, cz] if a else None))
    return out


def dentes_y(box, nome, cx, cz, y0, y1, r0, r1, larg, n, tex, giro0=0):
    """Dentes de engrenagem em volta do eixo Y (engrenagem deitada)."""
    out = []
    for i in range(n):
        a = giro0 + 360 / n * i
        out.append(box(f"{nome}{i}", [cx - larg / 2, y0, cz - r1], [cx + larg / 2, y1, cz - r0], tex,
                       {"y": a} if a else None, [cx, y0, cz] if a else None))
    return out


def modelos(k):
    box = k.box
    terminal, lampada = k.terminal, k.lampada

    # =================================================================
    # PENEIRA DE BALANÇO — cavalete de 2 postes sobre dormentes, travessa em cima; a peneira (moldura
    # de tábua com fundo de cesto trançado) pende de uma cruzeta por 4 cordas e balança no eixo da
    # travessa. Embaixo, a bandeja que apara a areia fina.
    # =================================================================
    pen_base = []
    for lado, z0, z1 in (("n", 0.5, 2.5), ("s", 13.5, 15.5)):
        pen_base += [
            box(f"dormente_{lado}", [1, 0, z0], [15, 2, z1], "logbark", faces={"east": "logend", "west": "logend"}),
            box(f"poste_{lado}", [7, 2, z0], [9, 22, z1], "darkwood"),
        ]
        zc0, zc1 = z0 + 0.4, z1 - 0.4
        pen_base += [
            box(f"mao_{lado}_o", [4.5, 1.3, zc0], [5.5, 8.7, zc1], "mossy", {"z": -33.69}, [5, 5, (zc0 + zc1) / 2]),
            box(f"mao_{lado}_l", [10.5, 1.3, zc0], [11.5, 8.7, zc1], "darkwood", {"z": 33.69}, [11, 5, (zc0 + zc1) / 2]),
        ]
    pen_base += [
        box("travessa", [6.75, 22, 0.25], [9.25, 23.5, 15.75], "darkwood"),
        box("travessa_amarra_n", [6.6, 21.9, 1], [9.4, 23.65, 2], "rope"),
        box("travessa_amarra_s", [6.6, 21.9, 14], [9.4, 23.65, 15], "rope"),
        # Bandeja no chão que apara a areia fina
        box("bandeja_fundo", [3, 0, 3.5], [13, 0.75, 12.5], "planks"),
        box("bandeja_n", [3, 0.75, 3.5], [13, 2.5, 4.25], "darkwood"),
        box("bandeja_s", [3, 0.75, 11.75], [13, 2.5, 12.5], "darkwood"),
        box("bandeja_o", [3, 0.75, 4.25], [3.75, 2.5, 11.75], "darkwood"),
        box("bandeja_l", [12.25, 0.75, 4.25], [13, 2.5, 11.75], "darkwood"),
        box("areia_fina", [3.75, 0.75, 4.25], [12.25, 1.6, 11.75], "areia"),
        box("musgo_dormente", [1.5, 2, 13.6], [4, 2.1, 15.4], "moss"),
        box("silex_dormente", [11, 2, 0.8], [12.2, 2.5, 2], "silex"),
    ]
    pen_balanco = [
        box("alca_corda", [7.6, 18.9, 7.6], [8.4, 22, 8.4], "rope"),
        box("cruzeta", [3, 18.1, 7.5], [13, 18.9, 8.5], "darkwood"),
        box("cruzeta_o", [2, 18, 3.25], [3, 19, 12.75], "darkwood"),
        box("cruzeta_l", [13, 18, 3.25], [14, 19, 12.75], "darkwood"),
    ]
    for nome, x0, z0 in (("no", 2.25, 3.5), ("so", 2.25, 12), ("ne", 13.25, 3.5), ("se", 13.25, 12)):
        pen_balanco.append(box(f"corda_{nome}", [x0, 8, z0], [x0 + 0.5, 18, z0 + 0.5], "rope"))
    pen_balanco += [
        box("aro_n", [2, 6, 3], [14, 8, 3.75], "planks"),
        box("aro_s", [2, 6, 12.25], [14, 8, 13], "planks"),
        box("aro_o", [2, 6, 3.75], [2.75, 8, 12.25], "darkwood"),
        box("aro_l", [13.25, 6, 3.75], [14, 8, 12.25], "darkwood"),
        box("fundo_trancado", [2.75, 6.1, 3.75], [13.25, 6.6, 12.25], "basketside"),
        box("cascalho", [4, 6.6, 5], [12, 7.4, 11], "gravel"),
        box("cascalho_monte", [5.5, 7.4, 6.5], [10.5, 7.9, 9.5], "gravel"),
        box("pepita1", [6, 7.9, 7], [6.8, 8.3, 7.6], "pepita"),
        box("pepita2", [9, 7.4, 10], [9.8, 7.8, 10.6], "pepita"),
        # Cabo pra empurrar (lado leste)
        box("cabo_n", [14, 6.75, 5], [15.5, 7.5, 5.75], "darkwood"),
        box("cabo_s", [14, 6.75, 10.25], [15.5, 7.5, 11], "darkwood"),
        box("pegador", [15.5, 6.6, 4.5], [16.25, 7.6, 11.5], "mossy"),
        box("pegador_couro", [15.45, 6.55, 7], [16.3, 7.65, 9], "leather"),
    ]

    # =================================================================
    # TORNO DE VARA — banco de 2 trilhos sobre cavaletes, 2 cabeçotes; a peça gira presa entre eles.
    # A corda dá voltas na peça: em cima vai até a vara-mola (amarrada no esteio), embaixo até o
    # pedal. Pisa → a peça gira pra um lado; a vara puxa de volta → gira pro outro (vai-e-vem).
    # =================================================================
    CY, CZ = 13, 8   # eixo da peça
    tor_base = []
    for lado, x0, x1 in (("o", 1, 3), ("l", 13, 15)):
        tor_base += [
            box(f"perna_{lado}_n", [x0, 0, 4.5], [x1, 7, 6.5], "bark"),
            box(f"perna_{lado}_s", [x0, 0, 9.5], [x1, 7, 11.5], "bark"),
            box(f"chapeu_{lado}", [x0 - 0.25, 7, 4], [x1 + 0.25, 8, 12], "darkwood"),
        ]
    tor_base += [
        box("trilho_n", [0.5, 8, 5], [15.5, 10, 6.5], "darkwood", faces={"east": "logend", "west": "logend"}),
        box("trilho_s", [0.5, 8, 9.5], [15.5, 10, 11], "mossy", faces={"east": "logend", "west": "logend"}),
        # Cabeçotes encaixados no vão dos trilhos, travados por um calço por baixo
        box("cabecote_o", [3.5, 8, 6.5], [5.5, 16, 9.5], "darkwood"),
        box("cabecote_l", [10.5, 8, 6.5], [12.5, 16, 9.5], "darkwood"),
        box("calco_o", [3.25, 7, 5], [5.75, 8, 11], "planks"),
        box("calco_l", [10.25, 7, 5], [12.75, 8, 11], "planks"),
        # Apoio da ferramenta (na frente, longe dos dentes que giram)
        box("braco_apoio_o", [3.5, 10.5, 3.75], [5.5, 11.25, 6.5], "planks"),
        box("braco_apoio_l", [10.5, 10.5, 3.75], [12.5, 11.25, 6.5], "planks"),
        box("apoio", [3.5, 11.25, 3.75], [12.5, 12, 4.75], "darkwood"),
        # Formão de sílex deitado no apoio, ponta na peça
        box("formao_lamina", [7.5, 12, 4], [8.1, 12.4, 5.2], "silex"),
        box("formao_cabo", [7.45, 12, 1], [8.15, 12.6, 4], "darkwood"),
        box("formao_amarra", [7.35, 11.95, 3.6], [8.25, 12.65, 4.2], "rope"),
        # Esteio atrás (sul) com a vara-mola amarrada em cima
        box("esteio", [9, 0, 14.75], [10.5, 24, 16], "bark"),
        box("esteio_musgo", [8.95, 0.05, 14.7], [10.55, 3, 16.05], "moss"),
        # Dobradiça do pedal (tora no chão, lado norte)
        box("pedal_eixo", [8.5, 0, 0.5], [11, 1, 2.5], "logbark", faces={"east": "logend", "west": "logend"}),
        # Engrenagens prontas no chão (a de cima um pouco girada)
        *disco(box, "pronta1", (5.5, 0, 13.6), 1.8, 0, 0.6, "planks"),
        *dentes_y(box, "pronta1_dente", 5.5, 13.6, 0, 0.6, 1.75, 2.4, 0.7, 8, "planks"),
        *disco(box, "pronta2", (5.5, 0, 13.6), 1.5, 0.6, 1.1, "darkwood"),
        *dentes_y(box, "pronta2_dente", 5.5, 13.6, 0.6, 1.1, 1.45, 2.0, 0.6, 8, "darkwood", giro0=20),
        # Lascas de madeira no chão
        box("lasca1", [6.5, 0, 6], [7.4, 0.2, 6.6], "planks", {"y": 30}),
        box("lasca2", [5.8, 0, 7.6], [6.5, 0.2, 8.1], "planks", {"y": -20}),
        box("lasca3", [7.6, 0, 9.2], [8.3, 0.2, 9.8], "planks", {"y": 55}),
    ]
    tor_peca = [
        *disco(box, "tarugo_o", (0, CY, CZ), 1.5, 5.5, 7, "logbark", eixo="x"),
        *disco(box, "tarugo_l", (0, CY, CZ), 1.5, 8.5, 10.5, "logbark", eixo="x"),
        *disco(box, "corda_voltas", (0, CY, CZ), 1.7, 9.1, 9.9, "rope", eixo="x"),
        # Engrenagem sendo entalhada no meio da peça
        *disco(box, "engr", (0, CY, CZ), 2.6, 7, 8.5, "planks", eixo="x"),
        *dentes_x(box, "engr_dente", CY, CZ, 7.1, 8.4, 2.55, 3.3, 0.8, 10, "planks"),
    ]
    tor_vara = [
        box("vara", [9, 24, 7.25], [10, 25, 16], "darkwood", faces={"north": "logend", "south": "logend"}),
        box("vara_amarra", [8.8, 23.4, 14.6], [10.7, 25.2, 16.15], "rope"),
        box("corda_cima", [9.25, 14.5, 7.75], [9.75, 24, 8.25], "rope"),
    ]
    tor_pedal = [
        box("pedal", [8.75, 1, 1], [10.75, 1.75, 14.5], "planks"),
        box("pedal_ripa", [8.75, 1.75, 12.5], [10.75, 2.1, 13.25], "darkwood"),
        box("corda_baixo", [9.25, 1.75, 7.75], [9.75, 11.5, 8.25], "rope"),
    ]

    # =================================================================
    # GERADOR DE MANIVELA — caixote aberto em cima; eixo redondo passa por furos nas paredes.
    # No meio do eixo, o rotor (carretel enrolado de fio de cobre) gira entre 2 pedras-ímã.
    # Manivela de um lado, volante de pedra do outro. Escova de carvão encosta no rotor e leva a
    # energia pro borne em cima da ponte.
    # =================================================================
    GY, GZ = 6.5, 8
    ger_base = [
        box("chao", [3.5, 0, 3], [12.5, 1, 13], "planks"),
        box("parede_n", [3.5, 1, 3], [12.5, 9, 3.75], "planks"),
        box("parede_s", [3.5, 1, 12.25], [12.5, 9, 13], "mossy"),
    ]
    for lado, x0, x1 in (("o", 3.5, 4.25), ("l", 11.75, 12.5)):
        # Parede com furo redondo-ish (1.2 x 1.2) pro eixo
        ger_base += [
            box(f"parede_{lado}_baixo", [x0, 1, 3.75], [x1, 5.9, 12.25], "planks"),
            box(f"parede_{lado}_cima", [x0, 7.1, 3.75], [x1, 9, 12.25], "planks"),
            box(f"parede_{lado}_n", [x0, 5.9, 3.75], [x1, 7.1, 7.4], "planks"),
            box(f"parede_{lado}_s", [x0, 5.9, 8.6], [x1, 7.1, 12.25], "planks"),
        ]
    ger_base += [
        # Mancais (colares de madeira) por fora dos furos
        box("mancal_o", [2.75, 5.5, 7], [3.5, 7.5, 9], "darkwood"),
        box("mancal_l", [12.5, 5.5, 7], [12.9, 7.5, 9], "darkwood"),
        # Pedras-ímã dos dois lados do rotor
        box("ima_n", [6.1, 1, 4.25], [9.9, 7.5, 5.75], "ima"),
        box("ima_s", [6.1, 1, 10.25], [9.9, 7.5, 11.75], "ima"),
        # Ponte por cima com a escova de carvão e o borne
        box("ponte", [3.5, 9, 7.25], [12.5, 9.75, 8.75], "darkwood"),
        box("escova", [7.6, 8.5, 7.6], [8.4, 9, 8.4], "coal"),
        *terminal(8, 9.75, 8, "borne"),
        *lampada(5.5, 9, 3.375),
        # Cinta de corda em volta do caixote (4 tiras por fora)
        box("cinta_n", [3.5, 4, 2.8], [12.5, 4.6, 3], "rope"),
        box("cinta_s", [3.5, 4, 13], [12.5, 4.6, 13.2], "rope"),
        box("cinta_o", [3.3, 4, 2.8], [3.5, 4.6, 13.2], "rope"),
        box("cinta_l", [12.5, 4, 2.8], [12.7, 4.6, 13.2], "rope"),
        box("musgo_caixote", [9.5, 9, 3], [12, 9.1, 3.75], "moss"),
    ]
    ger_gira = [
        *disco(box, "eixo_o", (0, GY, GZ), 0.45, 2.5, 5.6, "darkwood", eixo="x"),
        *disco(box, "eixo_l", (0, GY, GZ), 0.45, 10.4, 13, "darkwood", eixo="x"),
        *disco(box, "carretel_o", (0, GY, GZ), 2.4, 5.6, 6, "darkwood", eixo="x"),
        *disco(box, "rotor", (0, GY, GZ), 2, 6, 10, "bronze", eixo="x"),
        *disco(box, "carretel_l", (0, GY, GZ), 2.4, 10, 10.4, "darkwood", eixo="x"),
        *disco(box, "volante", (0, GY, GZ), 4.25, 13, 14.5, "stonewheel", eixo="x"),
        box("volante_cubo", [14.5, 5.75, 7.25], [15.25, 7.25, 8.75], "darkwood"),
        box("manivela_braco", [1.75, 6, 7.5], [2.5, 11, 8.5], "darkwood"),
        box("manivela_cabo", [0.25, 10, 7.5], [1.75, 11, 8.5], "darkwood"),
        box("manivela_couro", [0.4, 9.85, 7.35], [1.6, 11.15, 8.65], "leather"),
    ]

    # =================================================================
    # FOLE DE COURO — tábua de baixo fixa num par de toras; tábua de cima abre e fecha na dobradiça
    # do cabeçote (lado do bico). As dobras de couro abrem em leque entre as duas. Pedra em cima
    # faz o peso da volta. O bico de barro sopra pro bloco do lado (fogueira / forno).
    # =================================================================
    HX, HY, HZ = 12, 5.5, 8      # dobradiça
    ABRE = 10                    # graus de abertura no meio do curso (vai de 0 a 2x isso)
    fol_base = [
        box("tora_o", [2, 0, 4.5], [4, 3, 11.5], "logbark", faces={"north": "logend", "south": "logend"}),
        box("tora_l", [8.5, 0, 4.5], [10.5, 3, 11.5], "logbark", faces={"north": "logend", "south": "logend"}),
        box("tabua_baixo", [1, 3, 3.5], [12, 4, 12.5], "planks"),
        box("cabecote", [12, 3, 5], [14, 6.5, 11], "darkwood"),
        box("cabecote_amarra", [12.4, 2.9, 4.9], [13.2, 6.6, 11.1], "rope"),
        box("bico", [14, 4, 7], [16, 5.5, 9], "fired"),
        box("musgo_tora", [10.5, 0.5, 5], [10.58, 2.5, 7], "moss"),
    ]
    rot = lambda f: ({"z": -ABRE * f}, [HX, HY, HZ])
    fol_tampa = [
        box("tabua_cima", [1, 5, 3.5], [12, 6, 12.5], "planks", *rot(1)),
        box("cabo_poste", [1.5, 6, 7.5], [2.5, 9, 8.5], "darkwood", *rot(1)),
        box("cabo_pegador", [1.25, 9, 5], [2.75, 10, 11], "mossy", *rot(1)),
        box("pedra_peso", [5, 6, 5.5], [8.5, 7.5, 10.5], "cobble", *rot(1)),
        box("remendo_couro", [9, 6, 6.5], [11, 6.08, 9.5], "leather", *rot(1)),
    ]
    dobras = {}
    for i, f in enumerate((0.2, 0.4, 0.6, 0.8)):
        y = 4 + f - 0.075
        dobras[f"dobra{i}"] = (f, [box(f"dobra{i}", [1.3, y, 3.75], [12, y + 0.15, 12.25], "couro", *rot(f))])

    AMP = math.radians(ABRE)
    return {
        "auto_peneira_balanco": {
            "title": "Peneira de Balanço",
            "parts": {
                "base": {"label": "Cavalete (parado)", "elements": pen_base},
                "balanco": {"label": "Peneira (balança)", "elements": pen_balanco},
            },
            "auto": {
                "cat": "primitivo",
                "desc": "Peneira de moldura de tábua com fundo de cesto trançado, pendurada por 4 cordas num cavalete de madeira. Ponha cascalho ou areia e SEGURE o clique direito: ela balança e peneira 4 de uma vez, com a mesma tabela de achados da bateia do jogo (pepitas de cobre, estanho, sílex...). Não dá mais coisa que a bateia — só cansa menos. A areia fina cai na bandeja de baixo. Sem energia: é tudo à mão. Receita: lenha, gravetos e capim seco.",
                "pivots": {"balanco": [8, 22, 8]},
                "modes": [["parado", "Parada"], ["usando", "Balançando"]],
                "default": "usando",
                "anim": [{"part": "balanco", "swing": "z", "freq": 0.9, "amp": 0.12}],
                "fx": {"usando": [{"type": "dust", "at": [8, 5.6, 8]}]},
                "cam": {"pos": [2.7, 2.1, 3.1], "target": [0.5, 0.7, 0.5]},
            },
        },
        "auto_torno_vara": {
            "title": "Torno de Vara",
            "parts": {
                "base": {"label": "Banco (parado)", "elements": tor_base},
                "peca": {"label": "Peça (vai e vem)", "elements": tor_peca},
                "vara": {"label": "Vara-mola", "elements": tor_vara},
                "pedal": {"label": "Pedal", "elements": tor_pedal},
            },
            "auto": {
                "cat": "primitivo",
                "desc": "Torno de pedal à moda antiga: a corda dá voltas na peça, vai até a vara-mola em cima e até o pedal embaixo. SEGURE o clique direito pra pedalar: a peça gira pra lá e pra cá e o formão de sílex vai entalhando. Cada 2 lenhas (ou tábuas) viram 1 Engrenagem de Madeira, que serve no lugar da engrenagem enferrujada SÓ nas peças de energia da Automação (a enferrujada continua valendo ouro no comerciante). Receita: lenha, gravetos e sílex.",
                "pivots": {"peca": [8, CY, CZ], "vara": [9.75, 24.5, 15.5], "pedal": [9.75, 1.4, 1.75]},
                "modes": [["parado", "Parado"], ["usando", "Pedalando"]],
                "default": "usando",
                "anim": [{"part": "peca", "swing": "x", "freq": 1, "amp": 2.4},
                         {"part": "vara", "swing": "x", "freq": 1, "amp": -0.035},
                         {"part": "pedal", "swing": "x", "freq": 1, "amp": 0.06}],
                "fx": {"usando": [{"type": "dust", "at": [8, 12.6, 5.4]}]},
                "cam": {"pos": [2.6, 1.9, -1.4], "target": [0.5, 0.7, 0.5]},
            },
        },
        "auto_gerador_manivela": {
            "title": "Gerador de Manivela",
            "parts": {
                "base": {"label": "Caixote (parado)", "elements": ger_base},
                "gira": {"label": "Manivela, rotor e volante", "elements": ger_gira},
            },
            "auto": {
                "cat": "primitivo",
                "desc": "Caixote de tábua com um carretel enrolado de fio de cobre girando entre duas pedras-ímã. SEGURE o clique direito pra girar a manivela: enquanto gira, sai um pouquinho de energia (uns 2 por segundo) pra rede. O volante de pedra do outro lado deixa o giro macio. Dá pra testar a primeira máquina antes de ter rio ou vento, mas cansa: sua fome cai mais rápido enquanto gira. Receita: lenha, pedras soltas, graveto e pepitas de cobre (da Peneira de Balanço).",
                "pivots": {"gira": [8, GY, GZ]},
                "modes": [["parado", "Parado"], ["girando", "Girando a manivela"]],
                "default": "girando",
                "anim": [{"part": "gira", "spin": "x", "speed": 3}],
                "glow": ["girando"],
                "cam": {"pos": [-1.2, 1.6, 2.6], "target": [0.5, 0.35, 0.5]},
            },
        },
        "auto_fole": {
            "title": "Fole de Couro",
            "parts": {
                "base": {"label": "Fole (parado)", "elements": fol_base},
                "tampa": {"label": "Tábua de cima", "elements": fol_tampa},
                **{n: {"label": f"Dobra de couro {i + 1}", "elements": els} for i, (n, (f, els)) in enumerate(dobras.items())},
            },
            "auto": {
                "cat": "primitivo",
                "desc": "Fole de duas tábuas com dobras de couro, deitado num par de toras. Coloque com o bico de barro virado pra fogueira, forno de barro ou forja e SEGURE o clique direito pra bombear: o fogo esquenta mais rápido e gasta menos lenha (bom pra derreter o primeiro cobre no cadinho). A pedra em cima faz o peso da volta. Receita: tábuas, couro, barro e uma pedra.",
                "pivots": {"tampa": [HX, HY, HZ], **{n: [HX, HY, HZ] for n in dobras}},
                "modes": [["parado", "Parado"], ["usando", "Bombeando"]],
                "default": "usando",
                "anim": [{"part": "tampa", "swing": "z", "freq": 0.8, "amp": AMP}]
                        + [{"part": n, "swing": "z", "freq": 0.8, "amp": AMP * f} for n, (f, _) in dobras.items()],
                "fx": {"usando": [{"type": "sparks", "at": [16.5, 4.75, 8]}]},
                "cam": {"pos": [-1.0, 1.4, 2.4], "target": [0.5, 0.3, 0.5]},
            },
        },
    }
