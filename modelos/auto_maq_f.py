"""
AUTOMAÇÃO — Forja automática, Portão elétrico, Cerca elétrica e Aquecedor.
Energia sem fio (o borne é a antena que recebe do Poste de Energia).
"""

TEX = {
    "f_lingote": "game:block/metal/ingot/iron",
    "f_aviso": "game:block/cloth/paper/blank-small",
}


def _sem_zfight(caixa, eixo):
    """O motor do kit tem 2 caixas cruzadas com as pontas no mesmo plano: encurta uma delas."""
    i = 0 if eixo == "x" else 2
    for e in caixa:
        if e["name"].endswith("_corpo2"):
            e["from"][i] += 0.05
            e["to"][i] -= 0.05
    return caixa


def _engrenagem(box, nome, c, r, esp, tex, eixo="y", dentes=8):
    """Engrenagem redonda: miolo octogonal (2 caixas cruzadas) + dentes em volta.
    c = centro; eixo = eixo em volta do qual ela gira (y = deitada)."""
    cx, cy, cz = c
    h = esp / 2
    rot = {"y": "y", "x": "x", "z": "z"}[eixo]
    if eixo == "y":
        a = box(nome, [cx - r, cy - h, cz - r * 0.42], [cx + r, cy + h, cz + r * 0.42], tex)
        b = box(nome + "_b", [cx - r * 0.42, cy - h + 0.02, cz - r], [cx + r * 0.42, cy + h - 0.02, cz + r], tex)
        dente = lambda i: box(f"{nome}_dente{i}", [cx - 0.4, cy - h + 0.05, cz - r - 0.6], [cx + 0.4, cy + h - 0.05, cz - r * 0.85], tex,
                              {rot: 360 / dentes * i + 22.5}, [cx, cy, cz])
    elif eixo == "z":
        a = box(nome, [cx - r, cy - r * 0.42, cz - h], [cx + r, cy + r * 0.42, cz + h], tex)
        b = box(nome + "_b", [cx - r * 0.42, cy - r, cz - h + 0.02], [cx + r * 0.42, cy + r, cz + h - 0.02], tex)
        dente = lambda i: box(f"{nome}_dente{i}", [cx - 0.4, cy + r * 0.85, cz - h + 0.05], [cx + 0.4, cy + r + 0.6, cz + h - 0.05], tex,
                              {rot: 360 / dentes * i + 22.5}, [cx, cy, cz])
    else:
        a = box(nome, [cx - h, cy - r * 0.42, cz - r], [cx + h, cy + r * 0.42, cz + r], tex)
        b = box(nome + "_b", [cx - h + 0.02, cy - r, cz - r * 0.42], [cx + h - 0.02, cy + r, cz + r * 0.42], tex)
        dente = lambda i: box(f"{nome}_dente{i}", [cx - h + 0.05, cy + r * 0.85, cz - 0.4], [cx + h - 0.05, cy + r + 0.6, cz + 0.4], tex,
                              {rot: 360 / dentes * i + 22.5}, [cx, cy, cz])
    return [a, b] + [dente(i) for i in range(dentes)]


def modelos(k):
    box, terminal, lampada, motor = k.box, k.terminal, k.lampada, k.motor

    # =================================================================
    # FORJA E BIGORNA AUTOMÁTICAS — martinete movido a motor bate no metal em brasa
    # =================================================================
    forja = [
        box("alicerce", [0.5, 0, 0.5], [15.5, 2.5, 15.5], "cobble"),
        box("alicerce_borda", [0.25, 2.25, 0.25], [15.75, 3, 15.75], "brick"),
        # Bigorna sobre o cepo de ferro
        box("bigorna_base", [4.5, 3, 5], [11.5, 4, 11], "darkiron"),
        box("bigorna_pe", [5.5, 4, 6], [10.5, 7, 10], "darkiron"),
        box("bigorna_corpo", [3.5, 7, 5.5], [12.5, 9.5, 10.5], "iron"),
        box("bigorna_chifre", [12.5, 7.75, 7], [15, 9, 9], "iron"),
        box("bigorna_chifre_ponta", [15, 8, 7.4], [15.6, 8.75, 8.6], "iron"),
        box("bigorna_rabo", [1.5, 8, 6.5], [3.5, 9.5, 9.5], "iron"),
        box("metal_quente", [6.5, 9.5, 7], [9.5, 10, 9], "ember"),
        # Coluna do martinete (atrás) com o pino onde o braço balança
        box("coluna", [7, 3, 1], [9, 17, 3], "darkwood"),
        box("coluna_cinta1", [6.75, 6, 0.75], [9.25, 7, 3.25], "darkiron"),
        box("coluna_cinta2", [6.75, 12, 0.75], [9.25, 13, 3.25], "darkiron"),
        box("coluna_topo", [6.5, 17, 0.5], [9.5, 17.75, 3.5], "rebite"),
        box("pino_braco", [6.6, 14.6, 1.6], [9.4, 15.4, 2.4], "iron"),
        # Mancal do eixo de came na ponta direita
        box("mancal_came", [15.4, 3, 1.25], [15.9, 15.75, 2.75], "darkwood"),
        box("mancal_came_topo", [15.3, 15.75, 1], [16, 16.5, 3], "darkiron"),
        box("mancal_came_cinta", [15.3, 4.5, 1.1], [16, 6.5, 2.9], "darkiron"),
        # Correia: polia do motor (embaixo) até a polia do came (em cima), as duas no mesmo plano
        box("correia_frente", [14.55, 5.5, 3.25], [15.2, 15, 3.5], "leather"),
        box("correia_tras", [14.55, 5.5, 0.5], [15.2, 15, 0.75], "leather"),
        # Braseiro elétrico do lado (esquenta o lingote antes)
        box("braseiro", [0.75, 3, 10.5], [4.25, 6, 14.5], "darkiron"),
        box("braseiro_brasa", [1.25, 6, 11], [3.75, 6.4, 14], "ember"),
        box("braseiro_grade1", [0.75, 6.4, 11.75], [4.25, 6.7, 12.25], "corroded"),
        box("braseiro_grade2", [0.75, 6.4, 13], [4.25, 6.7, 13.5], "corroded"),
        box("lingote_esquentando", [1.5, 6.7, 11.9], [3.5, 7.2, 13.4], "f_lingote"),
        # Bauzinho de saída com peças prontas (cinta abraçando caixa e tampa)
        box("bau", [11, 3, 11], [15, 6.5, 15], "chestside"),
        box("bau_tampa", [10.85, 6.5, 10.85], [15.15, 7.1, 15.15], "chestlid"),
        box("bau_cinta", [10.75, 2.95, 12.75], [15.25, 7.2, 13.25], "darkiron"),
        *terminal(2, 3, 2.5, "borne"),
        *lampada(13, 7.2, 12),
        box("musgo", [0.6, 3, 4.5], [3, 3.1, 9], "moss"),
    ]
    caixa, gira = motor(11.5, 5.5, 2, comp=3.5, raio=1.75, eixo="x", nome="motor")
    forja += _sem_zfight(caixa, "x")
    forja_polia = gira  # polia do motor: x 14.5..15.25, centro (y 5.5, z 2), raio 1.25
    # Eixo de came: atravessa do pino da coluna até o mancal, com a polia de cima (mesmo x da de baixo)
    forja_came = [
        box("came_eixo", [9.4, 14.6, 1.6], [15.6, 15.4, 2.4], "iron"),
        box("came_polia", [14.5, 13.75, 0.75], [15.25, 16.25, 3.25], "corroded"),
        box("came_polia2", [14.52, 13.75, 0.75], [15.23, 16.25, 3.25], "corroded", {"x": 45}, [14.875, 15, 2]),
        box("came_ressalto", [9.6, 15.4, 1.5], [10.6, 16.75, 2.5], "darkiron"),
    ]
    martelo = [
        box("braco", [7.5, 14.5, 2.4], [8.5, 15.5, 8.5], "darkiron"),
        box("braco_reforco", [7.25, 14.25, 2.6], [8.75, 15.75, 3.6], "corroded"),
        box("martelo", [6.5, 11.5, 6.5], [9.5, 14.5, 9.5], "carcaca"),
        box("martelo_cinta", [6.25, 13, 6.25], [9.75, 13.75, 9.75], "rebite"),
        box("martelo_face", [7, 10.9, 7], [9, 11.5, 9], "iron"),
    ]

    # =================================================================
    # PORTÃO ELÉTRICO — 2 blocos de largura, folha de madeira com ferro, motor no pilar
    # =================================================================
    pilares = [
        box("pilar_esq", [0, 0, 5.5], [3.5, 24, 10.5], "cobble"),
        box("pilar_esq_capa", [-0.25, 24, 5.25], [3.75, 25, 10.75], "brick"),
        box("pilar_dir", [28.5, 0, 5.5], [32, 24, 10.5], "cobble"),
        box("pilar_dir_capa", [28.25, 24, 5.25], [32.25, 25, 10.75], "brick"),
        box("trilho_chao", [3.5, 0, 7.25], [28.5, 0.5, 8.75], "darkiron"),
        # Dobradiças presas no pilar (abraçam o pino da folha)
        box("dobradica_cima", [3.5, 17, 7.1], [4.75, 18.5, 8.9], "darkiron"),
        box("dobradica_baixo", [3.5, 3, 7.1], [4.75, 4.5, 8.9], "darkiron"),
        # Fecho no pilar da direita (a argola da folha encaixa aqui)
        box("fecho", [27.9, 10, 8.85], [28.5, 12, 9.35], "darkiron"),
        # Motor em pé em cima do pilar, num suporte: o pinhão dele engata na coroa do pino do portão
        box("suporte_pe_a", [0.25, 25, 5.75], [1, 27, 6.25], "darkiron"),
        box("suporte_pe_b", [0.25, 25, 9.75], [1, 27, 10.25], "darkiron"),
        box("suporte_chapa", [0, 27, 5.75], [3, 27.5, 10.25], "rebite"),
        box("motor_corpo", [0.25, 27.5, 6.75], [2.75, 31.5, 9.25], "carcaca"),
        box("motor_corpo2", [-0.25, 27.55, 7.25], [3.25, 31.45, 8.75], "carcaca"),
        box("motor_bobina", [0.1, 28.75, 6.6], [2.9, 30.25, 9.4], "bobina"),
        box("motor_tampa", [0.5, 31.5, 7], [2.5, 32, 9], "rebite"),
        box("motor_eixo", [1.1, 25.75, 7.6], [1.9, 27, 8.4], "iron"),
        *terminal(30.25, 25, 6.75, "borne"),
        *lampada(30.25, 25, 9.25),
        box("musgo_pilar", [0.1, 0.1, 10.45], [3.4, 5, 10.6], "moss"),
    ]
    # Pinhão (gira junto com a folha, mais rápido) embaixo do motor
    pinhao = _engrenagem(box, "pinhao", [1.5, 25.6, 8], 0.9, 0.6, "corroded", "y", 6)
    folha = [
        # Pino da dobradiça (eixo do portão) subindo até a coroa
        box("pino", [3.75, 0.5, 7.75], [4.25, 25.25, 8.25], "iron"),
        box("folha_borda_esq", [3.6, 1, 7.25], [4.6, 20.5, 8.75], "darkwood"),
        box("ferro_baixo", [4.55, 3.25, 7.15], [28.45, 4.25, 8.85], "darkiron"),
        box("ferro_cima", [4.55, 17.25, 7.15], [28.45, 18.25, 8.85], "darkiron"),
        box("ferro_diagonal", [6, 9.5, 7.2], [27, 10.5, 8.8], "corroded", {"z": 30}, [16.5, 10, 8]),
        box("argola", [26, 10.25, 8.6], [27.5, 11.75, 9.0], "iron"),
        *_engrenagem(box, "coroa", [4, 25.6, 8], 1.6, 0.7, "corroded", "y", 10),
    ]
    larg = (28.4 - 4.6) / 8
    for i in range(8):
        x0 = 4.6 + i * larg
        folha.append(box(f"tabua{i}", [x0, 1.25, 7.4], [x0 + larg, 20 - (i % 2) * 0.75, 8.6], "planks" if i % 3 else "mossy"))

    # =================================================================
    # CERCA ELÉTRICA — mourão com isoladores e 3 fios; emenda com as vizinhas
    # =================================================================
    cerca = [
        box("pe_pedra", [5, 0, 5], [11, 1.5, 11], "cobble"),
        box("mourao", [6.5, 1.5, 6.5], [9.5, 22, 9.5], "darkwood"),
        box("mourao_ponta", [7, 22, 7], [9, 22.5, 9], "mossy"),
        box("cinta", [6.25, 1.45, 6.25], [9.75, 2.5, 9.75], "darkiron"),
    ]
    for i, y in enumerate([5, 11, 18.5]):
        cerca += [
            box(f"isolador_o{i}", [5.25, y - 0.75, 7], [6.5, y + 1.25, 9], "isolador"),
            box(f"isolador_l{i}", [9.5, y - 0.75, 7], [10.75, y + 1.25, 9], "isolador"),
            box(f"arame_o{i}", [0, y, 7.85], [5.25, y + 0.4, 8.15], "cobre"),
            box(f"arame_l{i}", [10.75, y, 7.85], [16, y + 0.4, 8.15], "cobre"),
        ]
    cerca += [
        # Placa de perigo pregada na frente
        box("placa", [5, 13, 9.5], [11, 17, 9.85], "f_aviso"),
        box("placa_faixa", [5, 15.75, 9.8], [11, 16.5, 9.95], "red"),
        box("placa_raio", [7.5, 13.75, 9.8], [8.5, 15.5, 9.95], "red", {"z": 20}),
        box("prego", [7.75, 16.5, 9.85], [8.25, 16.9, 10.05], "corroded"),
        # Suporte da lampadinha atrás
        box("suporte_lamp", [7, 7.5, 3.5], [9, 8, 6.5], "darkiron"),
        *lampada(8, 8, 4.5),
        *terminal(8, 22.5, 8, "borne"),
    ]
    cerca_faisca = [box("faisca", [12.5, 10.6, 7.5], [13.5, 11.8, 8.5], "luz")]

    # =================================================================
    # AQUECEDOR — estufa de ferro fundido com resistências em brasa e aletas de radiador
    # =================================================================
    aquec = [
        box("laje", [1, 0, 2], [15, 1, 14], "cobble"),
        box("pe_no", [3, 1, 4], [4.5, 2.5, 5.5], "darkiron"),
        box("pe_ne", [11.5, 1, 4], [13, 2.5, 5.5], "darkiron"),
        box("pe_so", [3, 1, 10.5], [4.5, 2.5, 12], "darkiron"),
        box("pe_se", [11.5, 1, 10.5], [13, 2.5, 12], "darkiron"),
        box("corpo", [3, 2.5, 4], [13, 12, 12], "carcaca"),
        box("corpo_tampo", [2.5, 12, 3.5], [13.5, 13, 12.5], "rebite"),
        box("corpo_saia", [2.75, 2.4, 3.75], [13.25, 3.5, 12.25], "darkiron"),
        # Janela da frente com grade e resistências em brasa
        box("janela_fundo", [4.5, 4.5, 11.95], [11.5, 10, 12.05], "coal"),
        box("resist1", [4.75, 5.25, 12.05], [11.25, 5.75, 12.35], "ember"),
        box("resist2", [4.75, 6.75, 12.05], [11.25, 7.25, 12.35], "ember"),
        box("resist3", [4.75, 8.25, 12.05], [11.25, 8.75, 12.35], "ember"),
        box("grade_moldura_b", [4.25, 4.25, 12], [11.75, 4.75, 12.6], "darkiron"),
        box("grade_moldura_c", [4.25, 9.75, 12], [11.75, 10.25, 12.6], "darkiron"),
        box("grade1", [5.75, 4.75, 12.35], [6.25, 9.75, 12.6], "darkiron"),
        box("grade2", [7.75, 4.75, 12.35], [8.25, 9.75, 12.6], "darkiron"),
        box("grade3", [9.75, 4.75, 12.35], [10.25, 9.75, 12.6], "darkiron"),
        box("puxador", [7, 10.5, 12], [9, 11, 12.9], "brass"),
        # Tubos de radiador em cima (soltam o calor)
        box("tubo_o", [4.75, 13, 7.25], [6.25, 15.5, 8.75], "iron"),
        box("tubo_l", [9.75, 13, 7.25], [11.25, 15.5, 8.75], "iron"),
        box("tubo_cima", [4.75, 15.5, 7.25], [11.25, 17, 8.75], "iron"),
        box("tubo_flange_o", [4.5, 12.95, 7], [6.5, 13.5, 9], "darkiron"),
        box("tubo_flange_l", [9.5, 12.95, 7], [11.5, 13.5, 9], "darkiron"),
        box("tubo_cinta", [7.5, 15.25, 7], [8.5, 17.25, 9], "corroded"),
        box("valvula", [7.6, 17.25, 7.6], [8.4, 18, 8.4], "brass"),
        box("valvula_volante", [7, 18, 7], [9, 18.4, 9], "red"),
        *terminal(6.25, 13, 4.5, "borne"),
        *lampada(9.75, 13, 4.5),
        box("ferrugem", [12.9, 4, 6], [13.05, 7, 9], "corroded"),
        box("musgo", [1.1, 1, 2.1], [4, 1.1, 4], "moss"),
    ]
    aletas = []
    for i, z in enumerate([4.5, 6.5, 8.5, 10.5]):
        aletas.append(box(f"aleta_o{i}", [1.5, 3.5, z], [3, 11, z + 1], "darkiron"))
        aletas.append(box(f"aleta_l{i}", [13, 3.5, z], [14.5, 11, z + 1], "darkiron"))

    return {
        "auto_forja": {
            "title": "Forja Automática",
            "parts": {
                "base": {"label": "Bigorna + braseiro (parada)", "elements": forja},
                "polia": {"label": "Polia do motor (gira)", "elements": forja_polia},
                "came": {"label": "Eixo de came + polia (gira)", "elements": forja_came},
                "martelo": {"label": "Martinete (bate)", "elements": martelo},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Forja e bigorna automáticas: o braseiro elétrico esquenta o lingote ou a placa e o martinete (martelo movido a motor) bate sozinho na bigorna, fazendo a receita simples que você escolher no clique direito — placa, pregos, cabeças de ferramenta, rebites. Pega o metal do bauzinho e guarda as peças prontas nele. Combina com a Fornalha Elétrica. Gasta MUITA energia. Receita: bigorna, pedras, tábuas, cobre e engrenagem enferrujada.",
                "pivots": {"martelo": [8, 15, 2], "polia": [11.5, 5.5, 2], "came": [12, 15, 2]},
                "anim": [{"part": "martelo", "swing": "x", "amp": 0.14, "freq": 1.4},
                         {"part": "polia", "spin": "x", "speed": 8.8},
                         {"part": "came", "spin": "x", "speed": 8.8}],
                "glowTex": ["luz", "ember"],
                "fx": {"ligado": [{"type": "sparks", "at": [8, 10.2, 8], "rate": 0.4}]},
                "light": {"at": [5, 9, 12], "color": "#ff8a30", "intensity": 0.9},
                "cam": {"pos": [2.2, 1.7, 2.7], "target": [0.5, 0.5, 0.5]},
            },
        },
        "auto_portao": {
            "title": "Portão Elétrico",
            "parts": {
                "pilares": {"label": "Pilares + motor (parados)", "elements": pilares},
                "pinhao": {"label": "Pinhão do motor (gira)", "elements": pinhao},
                "folha": {"label": "Folha do portão + coroa (abre)", "elements": folha},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Portão de 2 blocos de largura que abre sozinho quando você (ou alguém da sua lista de amigos) chega perto e fecha depois que passou. À noite fica trancado, e nunca abre pra drifter nem bicho. Clique direito: quem pode passar, distância e horário. Só gasta energia quando mexe (quase nada). Receita: tábuas, pedras, chapa de ferro, cobre e engrenagem enferrujada.",
                "pivots": {"folha": [4, 0, 8], "pinhao": [1.5, 25.6, 8]},
                "modes": [["parado", "Sem energia"], ["fechado", "Fechado"], ["abrindo", "Abrindo/fechando"]],
                "default": "abrindo",
                "glow": ["fechado", "abrindo"],
                "anim": [{"part": "folha", "swing": "y", "amp": 1.4, "freq": 0.15, "when": ["abrindo"]},
                         {"part": "pinhao", "swing": "y", "amp": -2.49, "freq": 0.15, "when": ["abrindo"]}],
                "cam": {"pos": [3.0, 2.4, 4.6], "target": [1.0, 0.7, 0.5]},
            },
        },
        "auto_cerca": {
            "title": "Cerca Elétrica",
            "parts": {
                "cerca": {"label": "Mourão com fios", "elements": cerca},
                "faisca": {"label": "Faísca", "elements": cerca_faisca},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Mourão com isoladores de barro e 3 fios de arame de cobre — coloque um do lado do outro e os fios emendam sozinhos. Bicho ou drifter que encostar leva um choquinho e é empurrado pra longe (lobo desiste da criação, coelho larga a horta). Em jogador não machuca: só dá um susto. Gasta pouca energia. Receita: tora, barro (isolador) e cobre.",
                "show": {"faisca": ["ligado"]},
                "fx": {"ligado": [{"type": "sparks", "at": [13, 11.2, 8], "rate": 0.06}]},
                "cam": {"pos": [2.0, 1.7, 3.0], "target": [0.5, 0.6, 0.5]},
            },
        },
        "auto_aquecedor": {
            "title": "Aquecedor",
            "parts": {
                "corpo": {"label": "Estufa (parada)", "elements": aquec},
                "aletas": {"label": "Aletas do radiador", "elements": aletas},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Estufa de ferro fundido com resistências em brasa atrás da grade e aletas de radiador: mantém a casa quente num raio (8 blocos) sem fogueira — dentro do alcance a temperatura do corpo não cai no inverno. Gasta energia média, mais quando está muito frio lá fora. Receita: chapa de ferro, cobre, pedra e engrenagem enferrujada.",
                "glowTex": ["luz", "ember"],
                "light": {"at": [8, 7, 15], "color": "#ff8a30", "intensity": 1.1},
                "cam": {"pos": [1.9, 1.4, 2.6], "target": [0.5, 0.45, 0.5]},
            },
        },
    }
