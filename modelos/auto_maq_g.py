"""
AUTOMAÇÃO — mais fontes de energia (cata-vento, gerador a lenha, painel solar) e o Estabilizador Temporal.
"""

TEX = {
    "vidro_escuro": "game:block/glass/smoky",
    "estrutura": "game:block/machine/statictranslocator/statictranslocator_structure",
    "engrenagens_b": "game:block/machine/statictranslocator/statictranslocator_gearboxb",
}


def modelos(k):
    box, terminal, lampada = k.box, k.terminal, k.lampada

    # =================================================================
    # CATA-VENTO GERADOR — torre de madeira, hélice de lona velha, dínamo de cobre no cubo, leme atrás
    # =================================================================
    cv_base = [
        box("pe", [1.5, 0, 1.5], [14.5, 2, 14.5], "cobble"),
        box("pe_borda", [1, 1.75, 1], [15, 2.5, 15], "brick"),
        # 4 pernas inclinadas pro centro
        box("perna_no", [2.5, 2.5, 2.5], [4, 30, 4], "darkwood", {"x": 4, "z": -4}, [3.25, 2.5, 3.25]),
        box("perna_ne", [12, 2.5, 2.5], [13.5, 30, 4], "darkwood", {"x": 4, "z": 4}, [12.75, 2.5, 3.25]),
        box("perna_so", [2.5, 2.5, 12], [4, 30, 13.5], "mossy", {"x": -4, "z": -4}, [3.25, 2.5, 12.75]),
        box("perna_se", [12, 2.5, 12], [13.5, 30, 13.5], "darkwood", {"x": -4, "z": 4}, [12.75, 2.5, 12.75]),
        # Travessas
        box("trav_n1", [3, 11, 3.2], [13, 12, 4.2], "planks"),
        box("trav_s1", [3, 11, 11.8], [13, 12, 12.8], "planks"),
        box("trav_o1", [3.2, 11, 4.2], [4.2, 12, 11.8], "planks"),
        box("trav_l1", [11.8, 11, 4.2], [12.8, 12, 11.8], "planks"),
        box("trav_n2", [4, 21, 4], [12, 22, 5], "planks"),
        box("trav_s2", [4, 21, 11], [12, 22, 12], "planks"),
        box("cinta", [4.5, 28, 4.5], [11.5, 29, 11.5], "darkiron"),
        # Plataforma no topo e o giro (o cata-vento vira pro vento)
        box("plataforma", [4, 29, 4], [12, 30.5, 12], "planks"),
        box("giro", [6, 30.5, 6], [10, 31.5, 10], "corroded"),
        # Dínamo deitado (eixo pro sul)
        box("dinamo", [5.5, 31.5, 4], [10.5, 36, 12], "carcaca"),
        box("dinamo_bobina", [5.25, 31.25, 6.5], [10.75, 36.25, 9.5], "bobina"),
        box("dinamo_tampa", [5.75, 32, 12], [10.25, 35.5, 12.5], "rebite"),
        box("eixo", [7.5, 33.25, 12.5], [8.5, 34.25, 15], "iron"),
        # Leme atrás (vira a hélice pro vento)
        box("leme_haste", [7.6, 33.35, -1.5], [8.4, 34.15, 4], "darkwood"),
        box("leme", [7.8, 31, -6.5], [8.2, 37.5, -1.5], "planks"),
        box("leme_remendo", [7.75, 33, -5], [8.25, 35, -3], "rags"),
        # Escadinha numa perna
        *[box(f"degrau{i}", [12.6, 4 + i * 4, 6.5], [13.6, 4.6 + i * 4, 9.5], "darkwood") for i in range(6)],
        box("escada_trilho", [12.9, 2.5, 6.25], [13.4, 27, 6.75], "darkwood"),
        # Antena e lampadinha embaixo
        *terminal(5.5, 2.5, 13.5, "antena"),
        *lampada(10.5, 2.5, 13.5),
        box("musgo", [2, 2.4, 2], [6, 2.6, 5], "moss"),
    ]
    HUB = [8, 33.75, 15.25]
    cv_helice = [box("cubo", [6.75, 32.5, 14.5], [9.25, 35, 16], "cobre")]
    for i in range(4):
        rot = {"z": 90 * i}
        cv_helice += [
            box(f"pa{i}_haste", [7.6, 35, 15], [8.4, 47, 15.5], "darkwood", rot, HUB),
            box(f"pa{i}_lona", [8.4, 37, 15.05], [11.25, 46.5, 15.45], "rags" if i % 2 else "burlap", rot, HUB),
            box(f"pa{i}_ripa", [8.3, 41.5, 14.95], [11.4, 42.25, 15.55], "planks", rot, HUB),
        ]

    # =================================================================
    # GERADOR A LENHA — caldeirinha a vapor rebitada, fornalha embaixo, chaminé,
    # volante girando que puxa o dínamo de cobre, manômetro em cima
    # =================================================================
    ger_base = [
        box("alicerce", [0.5, 0, 0.5], [15.5, 2, 15.5], "cobble"),
        box("borda", [0.25, 1.75, 0.25], [15.75, 2.5, 15.75], "brick"),
        # Berços da caldeira
        box("berco_a", [3, 2.5, 4.5], [4.5, 5, 11.5], "darkiron"),
        box("berco_b", [9.4, 2.5, 4.5], [10.9, 5, 11.5], "darkiron"),
        # Caldeira deitada (octógono)
        box("caldeira", [2, 5, 4.5], [11, 12, 11.5], "carcaca"),
        box("caldeira2", [2.05, 5.75, 3.75], [10.95, 11.25, 12.25], "carcaca"),
        box("cinta1", [3.5, 4.75, 3.5], [4.25, 12.25, 12.5], "rebite"),
        box("cinta2", [8.5, 4.75, 3.5], [9.25, 12.25, 12.5], "rebite"),
        box("tampa_o", [1.5, 6, 5], [2, 11, 11], "rebite"),
        box("faixa_cobre", [5.5, 4.9, 3.6], [7, 12.1, 12.4], "cobre"),
        # Fornalha na frente, embaixo da caldeira (porta aberta mostrando a brasa)
        box("fornalha", [3, 2.5, 12.25], [9, 6.5, 14.5], "darkiron"),
        box("fornalha_brasa", [4, 3, 14.45], [8, 5.5, 14.55], "ember"),
        box("fornalha_grade1", [5.2, 2.9, 14.5], [5.6, 5.6, 14.75], "iron"),
        box("fornalha_grade2", [6.4, 2.9, 14.5], [6.8, 5.6, 14.75], "iron"),
        box("porta", [8.9, 2.75, 14.5], [9.4, 6.25, 16], "carcaca"),
        box("lenha1", [10, 2.5, 13], [15, 3.75, 14.25], "logbark", faces={"east": "logend", "west": "logend"}),
        box("lenha2", [10.5, 3.75, 13.25], [14.5, 5, 14.5], "logbark", faces={"east": "logend", "west": "logend"}),
        # Chaminé
        box("chamine", [3.6, 12, 6.5], [6, 21, 9], "carcaca"),
        box("chamine_aro", [3.25, 20.5, 6.25], [6.25, 21.25, 9.25], "corroded"),
        box("chamine_cinta", [3.25, 15, 6.25], [6.25, 15.75, 9.25], "darkiron"),
        # Manômetro
        box("mano_cano", [8, 12, 7.5], [8.75, 13.5, 8.25], "brass"),
        box("mano", [7, 13.5, 7.25], [9.75, 16, 8.5], "brass"),
        box("mano_mostrador", [7.25, 13.75, 8.5], [9.5, 15.75, 8.6], "paper"),
        box("mano_ponteiro", [8.25, 14.6, 8.6], [9.2, 14.9, 8.65], "red"),
        # Eixo do volante e dínamo
        box("eixo", [10.9, 8, 7.5], [13.8, 9, 8.5], "iron"),
        box("mancal", [11, 2.5, 6.5], [12, 9.5, 9.5], "darkiron"),
        box("dinamo_pe", [13.75, 2.5, 6], [15.75, 6, 10], "darkiron"),
        box("dinamo", [13.75, 6, 6], [15.75, 11, 10], "bobina"),
        box("dinamo_cinta", [13.6, 9.5, 5.85], [15.9, 10.25, 10.15], "darkiron"),
        *terminal(2, 2.5, 2, "antena"),
        *lampada(13.75, 2.5, 2),
        box("musgo", [10, 2.4, 1], [13, 2.6, 4], "moss"),
    ]
    VOL = [13, 8.5, 8]
    ger_volante = [box("vol_cubo", [12.25, 7.75, 7.25], [13.6, 9.25, 8.75], "darkiron")]
    for i in range(8):
        ger_volante.append(box(f"vol_aro{i}", [12.5, 12.6, 6.05], [13.5, 13.3, 9.95], "corroded", {"x": 45 * i}, VOL))
    for i in range(4):
        ger_volante.append(box(f"vol_raio{i}", [12.6, 9.25, 7.6], [13.4, 12.6, 8.4], "darkiron", {"x": 90 * i + 45}, VOL))

    # =================================================================
    # PAINEL SOLAR — placas de vidro escuro com moldura de cobre velho num cavalete de madeira,
    # vira devagar seguindo o sol
    # =================================================================
    sol_base = [
        box("pe", [4.5, 0, 4.5], [11.5, 1.5, 11.5], "cobble"),
        box("pe_chapa_n", [7, 0, 3], [9, 0.75, 4.5], "darkiron"),
        box("pe_chapa_s", [7, 0, 11.5], [9, 0.75, 13], "darkiron"),
        box("pe_chapa_o", [3, 0, 7], [4.5, 0.75, 9], "darkiron"),
        box("pe_chapa_l", [11.5, 0, 7], [13, 0.75, 9], "darkiron"),
        box("poste", [7, 1.5, 7], [9, 9.5, 9], "darkwood"),
        box("poste_cinta", [6.75, 4, 6.75], [9.25, 5, 9.25], "darkiron"),
        *terminal(5.75, 1.5, 10.25, "antena"),
        *lampada(10.25, 1.5, 5.75),
    ]
    SOL = [8, 10.5, 8]
    r30 = {"x": -30}
    sol_painel = [
        box("giro", [6.5, 9.5, 6.5], [9.5, 10.5, 9.5], "corroded"),
        box("dobradica", [6, 10.25, 7.25], [10, 11.25, 8.75], "iron"),
        box("tabua", [0.5, 10.75, 1.5], [15.5, 11.5, 14.5], "darkwood", r30, SOL, faces={"up": "coal"}),
        box("moldura_n", [0.5, 11.5, 1.5], [15.5, 12, 2], "cobre", r30, SOL),
        box("moldura_s", [0.5, 11.5, 14], [15.5, 12, 14.5], "cobre", r30, SOL),
        box("moldura_o", [0.5, 11.5, 2], [1, 12, 14], "cobre", r30, SOL),
        box("moldura_l", [15, 11.5, 2], [15.5, 12, 14], "cobre", r30, SOL),
        box("moldura_meio", [0.5, 11.5, 7.75], [15.5, 12, 8.25], "cobre", r30, SOL),
        box("ferrugem", [12, 11.52, 9], [14.5, 11.6, 12], "corroded", r30, SOL),
    ]
    for ix, x in enumerate([1, 5.75, 10.5]):
        for iz, z in enumerate([2, 8.25]):
            sol_painel.append(box(f"placa{ix}{iz}", [x + 0.1, 11.5, z + 0.1], [x + 4.4, 11.85, z + 5.65], "vidro_escuro", r30, SOL))
        sol_painel.append(box(f"divisoria{ix}", [x + 4.5, 11.5, 2], [x + 4.75, 12, 14], "cobre", r30, SOL))

    # =================================================================
    # ESTABILIZADOR TEMPORAL — base de pedra, 4 colunas de engrenagens/canos, núcleo azul preso entre
    # dois cálices de ferro, anéis girando em volta
    # =================================================================
    est_base = [
        box("base", [0, 0, 0], [16, 3, 16], "cobble"),
        box("degrau", [3.25, 3, 3.25], [12.75, 5, 12.75], "brick"),
        box("cinta", [-0.25, 1.5, -0.25], [16.25, 2.25, 16.25], "darkiron"),
        # Colunas nos cantos
        *[box(f"coluna{i}", [x, 3, z], [x + 2.5, 27, z + 2.5], "canos")
          for i, (x, z) in enumerate([(0.5, 0.5), (13, 0.5), (0.5, 13), (13, 13)])],
        *[box(f"coluna{i}_eng", [x - 0.25, 10, z - 0.25], [x + 2.75, 14, z + 2.75], "engrenagens")
          for i, (x, z) in enumerate([(0.5, 0.5), (13, 0.5), (0.5, 13), (13, 13)])],
        # Tampa de cima
        box("tampa", [0, 27, 0], [16, 29, 16], "estrutura"),
        box("tampa_borda", [-0.25, 28.5, -0.25], [16.25, 29.25, 16.25], "darkiron"),
        # Pedestal e cálices do núcleo
        box("pedestal", [5, 5, 5], [11, 8, 11], "engrenagens_b"),
        box("calice_baixo", [5, 8, 5], [11, 10, 11], "darkiron"),
        box("calice_cima", [5, 20, 5], [11, 22, 11], "darkiron"),
        box("haste", [7, 22, 7], [9, 27, 9], "iron"),
        box("nucleo", [6, 10, 6], [10, 20, 10], "luz"),
        box("nucleo_veio1", [5.9, 12, 7.5], [10.1, 12.5, 8.5], "darkiron"),
        box("nucleo_veio2", [7.5, 18.25, 5.9], [8.5, 18.75, 10.1], "darkiron"),
        *terminal(4, 29.25, 12, "antena"),
        *lampada(12, 29.25, 12),
        box("musgo", [1, 3, 5], [2, 3.2, 10], "moss"),
    ]
    C = [8, 15, 8]
    # Anel de cobre (gira pra um lado) e anel de latão (pro outro), os dois deitados em volta do núcleo.
    # Os raios param antes do núcleo (2,9 do centro): girando não encostam nas quinas dele.
    est_anel1 = [box(f"a1_{i}", [5.5, 13, 2], [10.5, 14, 2.8], "cobre", {"y": 45 * i} if i else None, [8, 13.5, 8] if i else None) for i in range(8)]
    # Colar de ferro que abraça o núcleo e segura os raios (o anel gira nele)
    est_anel1 += [box("a1_colar", [5.1, 13.05, 5.1], [10.9, 13.95, 10.9], "darkiron")]
    est_anel1 += [box("a1_raio_n", [7.6, 13.1, 2.8], [8.4, 13.9, 5.1], "iron"),
                  box("a1_raio_s", [7.6, 13.1, 10.9], [8.4, 13.9, 13.2], "iron")]
    est_anel2 = [box(f"a2_{i}", [5.85, 16.5, 2.6], [10.15, 17.3, 3.3], "brass", {"y": 45 * i} if i else None, [8, 16.9, 8] if i else None) for i in range(8)]
    est_anel2 += [box("a2_colar", [5.1, 16.55, 5.1], [10.9, 17.25, 10.9], "darkiron")]
    est_anel2 += [box("a2_raio_o", [3.3, 16.6, 7.6], [5.1, 17.2, 8.4], "iron"),
                  box("a2_raio_l", [10.9, 16.6, 7.6], [12.7, 17.2, 8.4], "iron")]

    return {
        "auto_catavento": {
            "title": "Cata-vento Gerador",
            "parts": {
                "torre": {"label": "Torre + dínamo (parada)", "elements": cv_base},
                "helice": {"label": "Hélice de lona (gira)", "elements": cv_helice},
            },
            "auto": {
                "cat": "energia",
                "desc": "Fonte de energia do vento — pra quem não mora perto de rio. Torre de madeira com hélice de lona velha e dínamo de cobre no cubo; o leme vira ela pro vento sozinho. Gera mais quanto mais alto estiver e quanto mais forte o vento (tempestade = muito, calmaria = quase nada). Dia e noite. Receita: tábuas, toras, pano (lona), cobre e engrenagem enferrujada.",
                "pivots": {"helice": HUB},
                "modes": [["parado", "Sem vento"], ["ligado", "Ventando"]],
                "anim": [{"part": "helice", "spin": "z", "speed": 2.2}],
                "fx": {"ligado": [{"type": "energy", "at": [5.5, 6, 13.5], "rate": 0.1}]},
                "cam": {"pos": [3.6, 2.8, 4.6], "target": [0.5, 1.45, 0.5]},
            },
        },
        "auto_gerador": {
            "title": "Gerador a Lenha",
            "parts": {
                "base": {"label": "Caldeira + fornalha (parada)", "elements": ger_base},
                "volante": {"label": "Volante (gira)", "elements": ger_volante},
            },
            "auto": {
                "cat": "energia",
                "desc": "Energia de emergência, em qualquer lugar: caldeirinha a vapor. Bota lenha, tábua ou carvão na fornalha (carvão dura mais), a água ferve, o vapor gira o volante e o volante puxa o dínamo. Gera bastante enquanto tiver combustível; o manômetro mostra a pressão. Precisa de alguém (ou da Esteira) pra pôr lenha. Receita: chapa de ferro, cobre, tijolos e engrenagem enferrujada.",
                "pivots": {"volante": VOL},
                "modes": [["parado", "Apagado"], ["ligado", "Queimando"]],
                "anim": [{"part": "volante", "spin": "x", "speed": 4}],
                "glowTex": ["luz", "ember"],
                "fx": {"ligado": [{"type": "smoke", "at": [4.75, 21.5, 7.75], "top": 2.6}]},
                "light": {"at": [6, 4, 16], "color": "#ff8a30", "intensity": 0.9},
                "cam": {"pos": [2.4, 1.7, 2.9], "target": [0.5, 0.5, 0.5]},
            },
        },
        "auto_solar": {
            "title": "Painel Solar",
            "parts": {
                "base": {"label": "Cavalete (parado)", "elements": sol_base},
                "painel": {"label": "Placas (seguem o sol)", "elements": sol_painel},
            },
            "auto": {
                "cat": "energia",
                "desc": "Placas de vidro escuro com moldura de cobre velho num cavalete de madeira: viram devagar seguindo o sol. Gera de dia — mais no verão e ao meio-dia, pouco nublado, nada à noite ou com chuva. Silencioso e sem manutenção; combina com bateria pra noite. Receita: vidro, cobre, tábuas e gravetos.",
                "pivots": {"painel": [8, 9.5, 8]},
                "modes": [["parado", "Noite"], ["nublado", "Nublado"], ["ligado", "Sol"]],
                "default": "ligado",
                "glow": ["nublado", "ligado"],
                "anim": [{"part": "painel", "swing": "y", "amp": 0.6, "freq": 0.04, "when": ["ligado", "nublado"]}],
                "fx": {"ligado": [{"type": "energy", "at": [8, 13, 8], "rate": 0.12}]},
                "cam": {"pos": [2.4, 1.8, 2.8], "target": [0.5, 0.5, 0.5]},
            },
        },
        "auto_estabilizador": {
            "title": "Estabilizador Temporal",
            "parts": {
                "base": {"label": "Base + colunas + núcleo (parado)", "elements": est_base},
                "anel1": {"label": "Anel de cobre (gira)", "elements": est_anel1},
                "anel2": {"label": "Anel de latão (gira)", "elements": est_anel2},
            },
            "auto": {
                "cat": "maquina",
                "desc": "A máquina grande: núcleo temporal azul preso entre dois cálices de ferro, com anéis girando em volta e engrenagens nas colunas. Mantém a estabilidade temporal num raio de 16 blocos em volta (o quadrado roxo): lá dentro você não perde estabilidade, nem em tempestade temporal. Gasta MUITA energia — precisa de várias fontes e baterias. Receita: engrenagens temporais, cobre, vidro, chapa de ferro e pedras.",
                "pivots": {"anel1": [8, 13.5, 8], "anel2": [8, 16.9, 8]},
                "anim": [{"part": "anel1", "spin": "y", "speed": 1.5}, {"part": "anel2", "spin": "y", "speed": -1}],
                "ranges": [{"at": [0, 0], "r": 16, "color": "#b46cff"}],
                "fx": {"ligado": [{"type": "energy", "at": [8, 20, 8], "rate": 0.3}]},
                "light": {"at": [8, 15, 8], "intensity": 1.2},
                "cam": {"pos": [3.0, 2.6, 4.0], "target": [0.5, 0.85, 0.5]},
            },
        },
    }
