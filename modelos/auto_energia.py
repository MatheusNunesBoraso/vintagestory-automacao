"""
AUTOMAÇÃO — fontes de energia, baterias e fio.
Energia = brilho azul temporal (textura 'luz'); cobre velho nos fios; ferro enferrujado nas carcaças.
"""

TEX = {
    "vidro_claro": "game:block/glass/plain",
    "telhado_ferro": "game:block/metal/tarnished/sheet/rusty-iron2",
}

WHEEL = [17.5, 8, 8]


def modelos(k):
    box, terminal, lampada, fio = k.box, k.terminal, k.lampada, k.fio

    # =================================================================
    # RODA GERADORA — na beira do rio: a roda d'água gira o dínamo de cobre
    # =================================================================
    roda_base = [
        box("alicerce", [1, 0, 1], [15, 3, 15], "cobble"),
        box("borda", [0.5, 2.75, 0.5], [15.5, 3.5, 15.5], "brick"),
        box("cinta", [0.75, 1, 0.75], [15.25, 1.75, 15.25], "darkiron"),
        # Mancal do eixo da roda na parede leste (o eixo da roda passa por dentro e entra na caixa)
        box("mancal", [13.5, 3.5, 6], [16, 10, 10], "darkiron"),
        box("mancal_tampa", [13.25, 9.5, 5.75], [16.25, 10.25, 10.25], "rebite"),
        # Caixa de engrenagens fechada: entra o eixo da roda, sai o eixo do dínamo (acelera)
        box("caixa_eng", [9, 3.5, 4.5], [13.5, 11, 11.5], "carcaca"),
        box("caixa_eng_frente", [9.25, 4.5, 11.5], [13.25, 10, 11.75], "engrenagens"),
        box("caixa_eng_tampa", [9, 11, 4.25], [13.75, 11.75, 11.75], "rebite"),
        # Dínamo aberto: 2 tampas rebitadas seguram o eixo; a bobina gira no meio dos ímãs
        box("dinamo_tampa_o", [1, 3.5, 3.5], [2, 13, 12.5], "rebite"),
        box("dinamo_tampa_l", [8.5, 3.5, 3.5], [9, 13, 12.5], "rebite"),
        box("ima_cima", [2, 12.5, 5], [8.5, 13, 11], "darkiron"),
        box("ima_baixo", [2, 3.5, 5], [8.5, 4.5, 11], "darkiron"),
        box("ima_n", [2, 6, 3.5], [8.5, 11, 4], "carcaca"),
        box("ima_s", [2, 6, 12], [8.5, 11, 12.5], "carcaca"),
        box("enrolado_n", [3.5, 6.75, 3.35], [7, 10.25, 4.08], "bobina"),
        box("enrolado_s", [3.5, 6.75, 11.92], [7, 10.25, 12.65], "bobina"),
        # Telhadinho de chapa sobre o dínamo (proteção da chuva)
        box("tel_poste_no", [1, 3.5, 1], [2, 15.5, 2], "darkwood"),
        box("tel_poste_so", [1, 3.5, 14], [2, 15.5, 15], "mossy"),
        box("tel_poste_ne", [12.5, 3.5, 1], [13.5, 14.3, 2], "darkwood"),
        box("tel_poste_se", [12.5, 3.5, 14], [13.5, 14.3, 15], "darkwood"),
        box("telhado", [0.25, 15, 0.25], [14.25, 15.75, 15.75], "telhado_ferro", {"z": -6}, [7, 15, 8]),
        box("telhado_ferrugem", [4, 15.75, 3], [8, 15.9, 6], "corroded", {"z": -6}, [7, 15, 8]),
        # Antena (borne) ligada no enrolamento + lampadinha em cima da caixa
        *terminal(4.5, 3.5, 13, "borne"),
        box("fio_borne", [4.25, 6.55, 12.6], [4.75, 7.05, 13.2], "cobre"),
        *lampada(11.25, 11.75, 9.5),
        box("musgo1", [1.2, 3.5, 12.75], [3.1, 3.7, 13.9], "moss"),
        box("musgo2", [9.5, 11.75, 4.5], [12, 11.9, 6.5], "moss"),
    ]
    # Bobina girando entre os ímãs + eixo que atravessa as tampas e entra na caixa de engrenagens
    roda_rotor = [
        box("rotor", [2.1, 5.5, 5.5], [8.4, 11.5, 10.5], "bobina"),
        box("rotor2", [2.25, 6, 5], [8.25, 11, 11], "bobina"),
        box("rotor_fenda1", [2.18, 8.25, 4.9], [8.32, 8.75, 11.1], "darkiron"),
        box("rotor_fenda2", [2.3, 5.4, 7.75], [8.2, 11.6, 8.25], "darkiron"),
        box("rotor_eixo", [8.4, 8, 7.5], [9.6, 9, 8.5], "iron"),
        box("rotor_eixo_o", [1.6, 8, 7.5], [2.2, 9, 8.5], "iron"),
    ]
    # Roda d'água do kit, sem a "engrenagem" quadrada (o eixo entra direto na caixa de engrenagens)
    roda_roda = [e for e in k.water_wheel() if e["name"] != "engrenagem_pe"]

    # =================================================================
    # TORRE DE TEMPESTADE — para-raios em cima, funil de chuva com turbininha no meio,
    # garrafão de vidro que guarda o raio embaixo. Sol: nada; chuva: pouco; raio: muito.
    # =================================================================
    torre_base = [
        box("pe_pedra", [2, 0, 2], [14, 2.5, 14], "cobble"),
        box("pe_borda", [1.5, 2.25, 1.5], [14.5, 3, 14.5], "brick"),
        # 4 pernas de madeira inclinadas pro centro (treliça), 2 blocos de altura
        box("perna_no", [2.5, 3, 2.5], [4, 30, 4], "darkwood", {"x": 4, "z": -4}, [3.25, 3, 3.25]),
        box("perna_ne", [12, 3, 2.5], [13.5, 30, 4], "darkwood", {"x": 4, "z": 4}, [12.75, 3, 3.25]),
        box("perna_so", [2.5, 3, 12], [4, 30, 13.5], "mossy", {"x": -4, "z": -4}, [3.25, 3, 12.75]),
        box("perna_se", [12, 3, 12], [13.5, 30, 13.5], "darkwood", {"x": -4, "z": 4}, [12.75, 3, 12.75]),
        # Travessas em X
        box("trav_n", [3, 14, 2.75], [13, 15, 3.5], "planks"),
        box("trav_s", [3, 14, 12.5], [13, 15, 13.25], "planks"),
        box("trav_o", [2.75, 14, 3.5], [3.5, 15, 12.5], "planks"),
        box("trav_l", [12.5, 14, 3.5], [13.25, 15, 12.5], "planks"),
        box("x_n1", [3, 6, 2.9], [13, 6.8, 3.4], "planks", {"z": 35}),
        box("x_n2", [3, 6, 2.9], [13, 6.8, 3.4], "planks", {"z": -35}),
        box("x_s1", [3, 6, 12.6], [13, 6.8, 13.1], "planks", {"z": 35}),
        box("x_s2", [3, 6, 12.6], [13, 6.8, 13.1], "planks", {"z": -35}),
        box("cinta_topo", [4, 27, 4], [12, 28, 12], "darkiron"),
        # Funil de chuva (bacia de cobre) no meio da torre
        box("funil_fundo", [5.5, 15, 5.5], [10.5, 16, 10.5], "cobre"),
        box("funil_n", [3.5, 16, 3.5], [12.5, 19, 4.25], "cobre", {"x": -15}, [8, 16, 4]),
        box("funil_s", [3.5, 16, 11.75], [12.5, 19, 12.5], "cobre", {"x": 15}, [8, 16, 12]),
        box("funil_o", [3.5, 16, 4.25], [4.25, 19, 11.75], "cobre", {"z": 15}, [4, 16, 8]),
        box("funil_l", [11.75, 16, 4.25], [12.5, 19, 11.75], "cobre", {"z": -15}, [12, 16, 8]),
        box("bica", [7.25, 11.5, 7.25], [8.75, 15, 8.75], "cobre"),
        # Carcaça da turbininha de chuva (embaixo do funil)
        box("turb_caixa_n", [5, 8, 5], [11, 11.5, 5.75], "carcaca"),
        box("turb_caixa_s", [5, 8, 10.25], [11, 11.5, 11], "carcaca"),
        box("turb_caixa_o", [5, 8, 5.75], [5.75, 11.5, 10.25], "carcaca"),
        box("turb_caixa_l", [10.25, 8, 5.75], [11, 11.5, 10.25], "carcaca"),
        box("turb_bica_saida", [10.25, 7, 7.25], [13, 8, 8.75], "darkiron", {"z": -15}, [11, 8, 8]),
        # Garrafão de vidro que guarda o raio (bobina dentro); na tampa, o dínamo da turbininha
        box("garrafa_base", [5, 3, 5], [11, 4, 11], "brass"),
        box("garrafa_n", [5.5, 4, 5.5], [10.5, 7.5, 5.75], "vidro_claro"),
        box("garrafa_s", [5.5, 4, 10.25], [10.5, 7.5, 10.5], "vidro_claro"),
        box("garrafa_o", [5.5, 4, 5.75], [5.75, 7.5, 10.25], "vidro_claro"),
        box("garrafa_l", [10.25, 4, 5.75], [10.5, 7.5, 10.25], "vidro_claro"),
        box("garrafa_bobina", [7.5, 4, 7.5], [8.5, 7.5, 8.5], "bobina"),
        box("garrafa_carga", [6.5, 4.05, 6.5], [9.5, 7.25, 9.5], "luz"),
        box("garrafa_tampa", [5, 7.5, 5], [11, 8, 11], "brass"),
        box("dinamo_turbina", [6.5, 8, 6.5], [9.5, 8.5, 9.5], "bobina"),
        *terminal(12.25, 3, 10.5, "borne"),
        # Cabo de cobre do para-raios: desce por fora da torre até o garrafão
        box("cabo_topo", [11.9, 27.25, 7.8], [14, 27.75, 8.2], "cobre"),
        box("cabo_desce", [13.6, 3, 7.8], [14, 27.25, 8.2], "cobre"),
        box("cabo_baixo", [11, 3, 7.8], [13.6, 3.4, 8.2], "cobre"),
        *[box(f"cabo_grampo{i}", [13.45, y, 7.65], [14.15, y + 0.5, 8.35], "darkiron") for i, y in enumerate([9, 15.5, 22])],
        # Para-raios: ponta de ferro com anéis de cobre e esferas
        box("mastro", [7.25, 28, 7.25], [8.75, 40, 8.75], "iron"),
        box("anel1", [6.25, 31, 6.25], [9.75, 31.75, 9.75], "cobre"),
        box("anel2", [6.75, 35, 6.75], [9.25, 35.75, 9.25], "cobre"),
        box("ponta", [7.6, 40, 7.6], [8.4, 44, 8.4], "cobre"),
        box("esfera_o", [3.5, 33, 7], [5.5, 35, 9], "bobina"),
        box("braco_o", [5.5, 33.75, 7.75], [7.25, 34.25, 8.25], "iron"),
        box("esfera_l", [10.5, 33, 7], [12.5, 35, 9], "bobina"),
        box("braco_l", [8.75, 33.75, 7.75], [10.5, 34.25, 8.25], "iron"),
        *lampada(8, 28, 11.5, "lampada"),
        box("musgo", [8, 3, 1.75], [11.5, 3.15, 4], "moss"),
    ]
    torre_turbina = [box("turb_eixo", [7.55, 7.6, 7.55], [8.45, 11.5, 8.45], "iron")]
    for i in range(4):
        torre_turbina.append(box(f"turb_pa{i}", [5.9, 8.75, 7.6], [10.1, 10.75, 8.4], "corroded", {"y": 45 * i}, [8, 9.75, 8]))

    # =================================================================
    # BATERIA — caixote com 4 jarros de barro (tipo pilha de Leyden), tampas de cobre
    # ligadas em série; marcador na frente com 4 barrinhas que acendem conforme a carga.
    # =================================================================
    bat_base = [
        box("caixote_fundo", [1, 0, 1], [15, 1.5, 15], "planks"),
        box("ripa_n", [1, 1.5, 1], [15, 7, 2], "planks"),
        box("ripa_s", [1, 1.5, 14], [15, 7, 15], "planks"),
        box("ripa_o", [1, 1.5, 2], [2, 7, 14], "darkwood"),
        box("ripa_l", [14, 1.5, 2], [15, 7, 14], "darkwood"),
        box("palha", [2, 1.5, 2], [14, 3, 14], "hay"),
        # Cantoneiras de ferro por fora dos 4 cantos (2 chapinhas em L cada)
        *[e for (x0, x1, xa, xb, z0, z1, za, zb, n) in [
            (0.75, 2.5, 0.75, 1, 0.75, 1, 1, 2.5, "no"), (13.5, 15.25, 15, 15.25, 0.75, 1, 1, 2.5, "ne"),
            (0.75, 2.5, 0.75, 1, 15, 15.25, 13.5, 15, "so"), (13.5, 15.25, 15, 15.25, 15, 15.25, 13.5, 15, "se")]
          for e in (box(f"canto_{n}_a", [x0, 0, z0], [x1, 7.5, z1], "darkiron"),
                    box(f"canto_{n}_b", [xa, 0, za], [xb, 7.5, zb], "darkiron"))],
        # Painel do marcador na frente (4 barrinhas)
        box("painel", [3.5, 2, 15], [12.5, 6.5, 15.5], "darkiron"),
        box("painel_moldura", [3.25, 6.5, 15], [12.75, 6.95, 15.6], "brass"),
        *[box(f"vela{i + 1}_vazia", [4 + i * 2, 2.75, 15.5], [5.5 + i * 2, 5.75, 15.6], "coal") for i in range(4)],
        *terminal(4.5, 7, 1.5, "borne_entra"),
        *terminal(11.5, 7, 1.5, "borne_sai"),
        box("etiqueta", [6.5, 3, 0.9], [9.5, 5.5, 1], "paper"),
        box("musgo", [2, 7, 14.1], [5, 7.12, 14.9], "moss"),
    ]
    jarros = []
    for i, (x, z) in enumerate([(5, 6.5), (11, 6.5), (5, 11.5), (11, 11.5)]):
        jarros += [
            box(f"jarro{i}", [x - 2.25, 3, z - 2.25], [x + 2.25, 10, z + 2.25], "fired"),
            box(f"jarro{i}_ombro", [x - 1.8, 10, z - 1.8], [x + 1.8, 11, z + 1.8], "fired"),
            box(f"jarro{i}_tampa", [x - 1.55, 11, z - 1.55], [x + 1.55, 11.75, z + 1.55], "cobre"),
            box(f"jarro{i}_haste", [x - 0.4, 11.7, z - 0.4], [x + 0.4, 13.25, z + 0.4], "cobre"),
            box(f"jarro{i}_faixa", [x - 2.4, 6, z - 2.4], [x + 2.4, 6.75, z + 2.4], "bobina"),
        ]
    # Ligação em série: borne de entrada -> jarro 0 -> 2 -> 3 -> 1 -> borne de saída
    jarros += [
        box("elo_entra_sobe", [4.2, 10.25, 1.2], [4.8, 12.5, 1.8], "cobre"),
        box("elo_entra", [4.25, 12.25, 1.5], [4.75, 12.75, 6.5], "cobre"),
        box("elo_02", [4.75, 12.65, 6.5], [5.25, 13.15, 11.5], "cobre"),
        box("elo_23", [5, 12.25, 11.25], [11, 12.75, 11.75], "cobre"),
        box("elo_31", [10.75, 12.65, 6.5], [11.25, 13.15, 11.5], "cobre"),
        box("elo_sai", [11.25, 12.25, 1.5], [11.75, 12.75, 6.5], "cobre"),
        box("elo_sai_sobe", [11.2, 10.25, 1.2], [11.8, 12.5, 1.8], "cobre"),
    ]
    bat_carga = [
        *[box(f"vela{i + 1}", [4.05 + i * 2, 2.8, 15.55], [5.45 + i * 2, 5.7, 15.7], "luz") for i in range(4)],
        # Brilhinho em cima da tampa de cada jarro quando cheia
        *[box(f"brilho{i}", [x - 1.2, 11.75, z - 1.2], [x + 1.2, 11.8, z + 1.2], "luz")
          for i, (x, z) in enumerate([(5, 6.5), (11, 6.5), (5, 11.5), (11, 11.5)])],
    ]

    # =================================================================
    # POSTE DE ENERGIA — SEM FIO: manda a energia por alcance. Tudo que estiver dentro do quadrado
    # (fonte, bateria, máquina ou outro poste) se liga sozinho. Clique direito mostra o alcance.
    # =================================================================
    poste = [
        box("pe", [5.5, 0, 5.5], [10.5, 1.5, 10.5], "cobble"),
        box("pe_cunha_n", [7, 0, 4.5], [9, 2.5, 5.5], "darkwood", {"x": -20}, [8, 0, 5.5]),
        box("pe_cunha_s", [7, 0, 10.5], [9, 2.5, 11.5], "darkwood", {"x": 20}, [8, 0, 10.5]),
        box("poste", [7, 0.5, 7], [9, 26, 9], "darkwood"),
        box("cinta1", [6.75, 4, 6.75], [9.25, 5, 9.25], "darkiron"),
        box("cinta2", [6.75, 18, 6.75], [9.25, 19, 9.25], "darkiron"),
        box("cruzeta", [2, 22, 7.25], [14, 23.5, 8.75], "mossy"),
        box("mao_francesa_o", [4.5, 17.5, 7.5], [5.5, 23, 8.5], "darkwood", {"z": -40}, [5, 23, 8]),
        box("mao_francesa_l", [10.5, 17.5, 7.5], [11.5, 23, 8.5], "darkwood", {"z": 40}, [11, 23, 8]),
        # Isoladores com bobininhas (as "antenas") nas pontas da cruzeta
        *terminal(3, 23.5, 8, "iso_o"),
        *terminal(13, 23.5, 8, "iso_l"),
        box("antena_o", [2.6, 26.75, 7.6], [3.4, 29, 8.4], "bobina"),
        box("antena_l", [12.6, 26.75, 7.6], [13.4, 29, 8.4], "bobina"),
        # Topo: prato de cobre + globo de vidro com o núcleo de energia
        box("prato", [5, 26, 5], [11, 26.75, 11], "cobre"),
        # Globo de vidro (4 paredes + tampo) com a haste de cobre que segura o núcleo
        box("globo_n", [5.75, 26.75, 5.75], [10.25, 31.25, 6], "vidro_claro"),
        box("globo_s", [5.75, 26.75, 10], [10.25, 31.25, 10.25], "vidro_claro"),
        box("globo_o", [5.75, 26.75, 6], [6, 31.25, 10], "vidro_claro"),
        box("globo_l", [10, 26.75, 6], [10.25, 31.25, 10], "vidro_claro"),
        box("globo_topo", [6, 31, 6], [10, 31.25, 10], "vidro_claro"),
        box("haste_nucleo", [7.6, 26.75, 7.6], [8.4, 27.5, 8.4], "cobre"),
        box("globo_tampa", [6.5, 31.25, 6.5], [9.5, 32, 9.5], "brass"),
        box("ponta", [7.6, 32, 7.6], [8.4, 34, 8.4], "cobre"),
        box("chapinha", [7.5, 12, 8.9], [8.5, 14, 9.05], "brass"),
        box("ferrugem", [6.9, 24, 6.9], [9.1, 25, 9.1], "corroded"),
    ]
    poste_luz = [box("nucleo", [6.75, 27.5, 6.75], [9.25, 30.5, 9.25], "luz")]
    # Anel de cobre que gira em volta do pé do globo (corre em cima do prato, como um trilho)
    poste_anel = []
    for i in range(8):
        poste_anel.append(box(f"anel{i}", [7.1, 26.75, 5.05], [8.9, 27.45, 5.75], "cobre", {"y": 45 * i} if i else None, [8, 26.75, 8] if i else None))

    return {
        "auto_roda": {
            "title": "Roda Geradora",
            "parts": {
                "base": {"label": "Base + dínamo (parada)", "elements": roda_base},
                "rotor": {"label": "Bobina do dínamo (gira)", "elements": roda_rotor},
                "roda": {"label": "Roda d'água (gira)", "elements": roda_roda},
            },
            "auto": {
                "cat": "energia", "agua": True,
                "desc": "Fonte de energia da água. Fica na beira do rio: a correnteza gira a roda, a caixa de engrenagens acelera e o dínamo de cobre gera energia, que sai pelo borne da frente. Gera sempre (dia e noite), pouco mas constante — mais se a água tiver correnteza. Lampadinha azul acesa = gerando. Receita: pedras, tábuas, cobre e engrenagem enferrujada.",
                "pivots": {"roda": WHEEL, "rotor": [8, 8.5, 8]},
                "modes": [["parado", "Sem água"], ["ligado", "Gerando"]],
                "anim": [{"part": "roda", "spin": "x", "speed": -1.3}, {"part": "rotor", "spin": "x", "speed": 6}],
                "fx": {"ligado": [{"type": "energy", "at": [4.5, 10, 13], "rate": 0.15}]},
                "light": {"at": [8, 14, 14]},
                "cam": {"pos": [3.4, 1.7, 2.7], "target": [0.8, 0.45, 0.5]},
            },
        },
        "auto_torre": {
            "title": "Torre de Tempestade",
            "parts": {
                "base": {"label": "Torre (parada)", "elements": torre_base},
                "turbina": {"label": "Turbininha de chuva (gira)", "elements": torre_turbina},
            },
            "auto": {
                "cat": "energia",
                "desc": "Fonte de energia do tempo. Tem 2 andares de altura. Quando chove, a água cai no funil de cobre e gira a turbininha (energia pouca e contínua). Quando tem tempestade, o para-raios atrai os raios que caem por perto e enche o garrafão de uma vez (muita energia!). Com sol não gera nada — por isso combina com bateria. Receita: cobre, tábuas, vidro e engrenagem enferrujada.",
                "pivots": {"turbina": [8, 9.75, 8]},
                "modes": [["sol", "Sol (parada)"], ["chuva", "Chuva"], ["raio", "Tempestade"]],
                "default": "raio",
                "anim": [{"part": "turbina", "spin": "y", "speed": 5}],
                "glow": ["chuva", "raio"],
                "show": {"garrafa_carga": ["raio"]},
                "fx": {"chuva": [{"type": "rain"}], "raio": [{"type": "rain"}, {"type": "lightning", "at": [8, 44, 8]}]},
                "light": {"at": [8, 6, 14], "intensity": 0.6, "when": ["raio"]},
                "cam": {"pos": [3.2, 2.6, 3.8], "target": [0.5, 1.2, 0.5]},
            },
        },
        "auto_bateria": {
            "title": "Bateria",
            "parts": {
                "base": {"label": "Caixote (parado)", "elements": bat_base},
                "jarros": {"label": "Jarros de carga", "elements": jarros},
                "carga": {"label": "Marcador de carga", "elements": bat_carga},
            },
            "auto": {
                "cat": "bateria",
                "desc": "Guarda energia pra quando a fonte para (noite sem chuva, rio congelado...). Caixote com 4 jarros de barro ligados em série; o marcador da frente mostra a carga em 4 barrinhas e o clique direito mostra o número. Várias baterias no alcance do mesmo poste somam a carga. Os bornes em cima são as antenas que recebem e mandam a energia. Receita: barro queimado, cobre e tábuas.",
                "modes": [["vazia", "Vazia"], ["meia", "Meia carga"], ["cheia", "Cheia"]],
                "default": "cheia",
                "glow": ["meia", "cheia"],
                "show": {"vela1": ["meia", "cheia"], "vela2": ["meia", "cheia"], "vela3": ["cheia"], "vela4": ["cheia"],
                         "brilho0": ["cheia"], "brilho1": ["cheia"], "brilho2": ["cheia"], "brilho3": ["cheia"]},
                "fx": {"cheia": [{"type": "energy", "at": [8, 13, 8], "rate": 0.12}]},
                "cam": {"pos": [1.9, 1.5, 2.3], "target": [0.5, 0.3, 0.5]},
            },
        },
        "auto_poste": {
            "title": "Poste de Energia",
            "parts": {
                "poste": {"label": "Poste com globo", "elements": poste},
                "luz": {"label": "Núcleo (com energia)", "elements": poste_luz},
                "anel": {"label": "Anel de cobre (gira)", "elements": poste_anel},
            },
            "auto": {
                "cat": "bateria",
                "desc": "SEM FIO: o poste manda a energia por alcance. Tudo que estiver dentro do quadrado dele (8 blocos pra cada lado) se liga sozinho — fontes, baterias e máquinas. Pra ir mais longe, coloque outro poste dentro do alcance do primeiro: eles se ligam em corrente. Nada aparece no mundo (sem fio, sem raio voando). Clique direito no poste abre a janelinha dele: mostra o alcance (o quadrado azul no chão), quanta energia passa e tem o botão 'Ver conexões', que desenha por alguns segundos o caminho da energia (poste → máquinas, poste → poste). Receita: tora, cobre, vidro e barro.",
                "pivots": {"anel": [8, 27.1, 8]},
                "modes": [["parado", "Sem energia"], ["ligado", "Passando energia"]],
                "show": {"luz": ["ligado"]},
                "anim": [{"part": "anel", "spin": "y", "speed": 1.6}],
                "ranges": [{"at": [0, 0], "r": 8}],
                "fx": {"ligado": [{"type": "energy", "at": [8, 31, 8], "rate": 0.15}]},
                "light": {"at": [8, 29, 8], "intensity": 0.7},
                "cam": {"pos": [3.6, 3.4, 5.4], "target": [0.5, 1.0, 0.5]},
            },
        },
    }
