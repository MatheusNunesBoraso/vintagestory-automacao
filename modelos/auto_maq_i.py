"""
AUTOMAÇÃO — Chocadeira, Pedreira Automática, Sonda de Minério e Painel da Rede.
(O Fogão Elétrico foi refeito e mora em auto_maq_j.py.)

Regras (do usuário): coerência mecânica (redondo engata em redondo, cremalheira engata no pinhão,
eixo no centro), nada sobreposto (sem faces no mesmo plano / peças se atravessando), nada flutuando.
"""
import math

TEX = {
    "vidro_claro": "game:block/glass/plain",
    "ovo": "game:block/wood/henbox/egg",
    "pedra": "game:block/stone/rock/andesite1",
}

T8 = math.tan(math.pi / 8)


def disco(box, nome, c, r, a0, a1, tex, eixo="y"):
    """Disco/cilindro octogonal (4 fatias giradas, alturas escalonadas 0.02 pra não piscar)."""
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


def dentes(box, nome, cx, cz, y0, y1, r0, r1, larg, n, tex):
    """Dentes de coroa em volta do eixo y (do raio r0 até r1)."""
    return [box(f"{nome}{i}", [cx - larg / 2, y0, cz - r1], [cx + larg / 2, y1, cz - r0], tex,
                {"y": 360 / n * i} if i else None, [cx, y0, cz] if i else None) for i in range(n)]


def arrumar_motor(els, eixo="x", sem_pe=False):
    """Motor do kit sem faces no mesmo plano (2ª metade da carcaça 0.05 mais curta no eixo);
    sem_pe tira o pé (motor pendurado)."""
    out = []
    for e in els:
        if sem_pe and e["name"].endswith("_pe"):
            continue
        if e["name"].endswith("_corpo2"):
            k = 0 if eixo == "x" else 2
            e["from"][k] += 0.05
            e["to"][k] -= 0.05
        out.append(e)
    return out


def modelos(k):
    box, terminal, lampada, motor = k.box, k.terminal, k.lampada, k.motor

    # =================================================================
    # CHOCADEIRA — caixote de madeira com cantoneiras, tampa de vidro com moldura, ovos (formato de
    # ovo) na palha, lâmpada de calor com cúpula pendurada num braço, caixinha de controle do lado.
    # =================================================================
    choca = [
        *[box(f"canto{i}", [x, 0, z], [x + 1.25, 7.75, z + 1.25], "darkiron")
          for i, (x, z) in enumerate([(0.75, 1.75), (14, 1.75), (0.75, 13), (14, 13)])],
        box("parede_n", [2, 0, 2], [14, 7, 3], "planks"),
        box("parede_s", [2, 0, 13], [14, 7, 14], "planks"),
        box("parede_o", [2, 0, 3], [3, 7, 13], "darkwood"),
        box("parede_l", [13, 0, 3], [14, 7, 13], "darkwood"),
        box("fundo", [3, 0, 3], [13, 1.5, 13], "planks"),
        box("palha", [3, 1.5, 3], [13, 3, 13], "hay"),
        # Tampa: moldura, vidro, travessa do meio, dobradiças atrás
        box("tampa_n", [2, 7, 2], [14, 7.75, 3], "darkwood"),
        box("tampa_s", [2, 7, 13], [14, 7.75, 14], "darkwood"),
        box("tampa_o", [2, 7, 3], [3, 7.75, 13], "darkwood"),
        box("tampa_l", [13, 7, 3], [14, 7.75, 13], "darkwood"),
        box("tampa_vidro", [3, 7.3, 3], [13, 7.45, 13], "vidro_claro"),
        box("tampa_travessa", [7.9, 7.45, 3], [8.1, 7.6, 13], "darkwood"),
        box("dobradica1", [4.5, 7.1, 1.6], [6, 7.65, 2], "darkiron"),
        box("dobradica2", [10, 7.1, 1.6], [11.5, 7.65, 2], "darkiron"),
        # Lâmpada de calor: poste atrás, braço, cúpula de latão e bulbo
        box("braco_poste", [7.25, 7.75, 2], [8.75, 13, 3], "darkiron"),
        box("braco", [7.25, 12, 3], [8.75, 13, 6.75], "darkiron"),
        *disco(box, "cupula", (8, 0, 6), 1.4, 10.75, 12, "brass"),
        *disco(box, "bulbo", (8, 0, 6), 0.85, 10.0, 10.75, "luz"),
        # Termômetro na frente
        box("termometro", [11, 2, 14], [12.5, 6.5, 14.4], "brass"),
        box("termometro_linha", [11.5, 2.5, 14.4], [12, 5, 14.5], "red"),
        # Caixinha de controle do lado (antena + lampadinha em cima)
        box("controle", [14, 0, 7], [16.5, 4, 12], "carcaca"),
        box("controle_tampa", [13.9, 4, 6.9], [16.6, 4.25, 12.1], "rebite"),
        *terminal(15.25, 4.25, 8.25, "antena"),
        *lampada(15.25, 4.25, 10.9),
        box("musgo", [3, 0, 14], [8, 0.15, 15.5], "moss"),
    ]

    def ovo(nome, x, z):
        return [box(nome, [x, 3, z], [x + 1.6, 4.7, z + 1.6], "ovo"),
                box(nome + "_ponta", [x + 0.25, 4.7, z + 0.25], [x + 1.35, 5.3, z + 1.35], "ovo")]
    for i, (x, z) in enumerate([(4, 4.5), (7, 4.5), (10, 5), (8.5, 8.5), (11, 9.5)]):
        choca += ovo(f"ovo{i}", x, z)
    ovo_chocando = ovo("ovo5", 5.6, 7.2)
    pintinho = [
        # Saiu do ovo (as cascas ficam onde o ovo estava) e deu uns passinhos
        box("pinto_corpo", [3.5, 3, 7.4], [5.1, 4.4, 8.9], "yellow"),
        box("pinto_cabeca", [3.8, 4.4, 8.2], [4.8, 5.4, 9.2], "yellow"),
        box("pinto_bico", [4.1, 4.7, 9.2], [4.5, 5.0, 9.6], "pumpkin"),
        box("casca1", [7.25, 3, 7.3], [8.2, 3.6, 8.2], "ovo"),
        box("casca2", [5.6, 3, 8.85], [6.4, 3.4, 9.6], "ovo"),
    ]

    # =================================================================
    # PEDREIRA AUTOMÁTICA — bate-estaca: o martelo corre entre 2 guias; uma CREMALHEIRA presa no
    # martelo sobe pelo meio do cavalete e engata no PINHÃO do motor (lá em cima), que levanta o
    # martelo e solta. Quebra a pedra do buraco; as pedras vão pro bauzinho.
    # =================================================================
    PZ = 5.95          # eixo do motor/pinhão (z)
    PY = 27.85         # altura do eixo do motor
    pm, pg = motor(3.2, PY, PZ, comp=3, raio=1.6, eixo="x", nome="motor")
    pm = arrumar_motor(pm, "x")
    pedreira = [
        # Chão de pedra com o buraco no meio
        box("chao_n", [0, 0, 0], [16, 2, 4], "cobble"),
        box("chao_s", [0, 0, 12], [16, 2, 16], "cobble"),
        box("chao_o", [0, 0, 4], [4, 2, 12], "cobble"),
        box("chao_l", [12, 0, 4], [16, 2, 12], "cobble"),
        box("buraco", [4, 0, 4], [12, 0.5, 12], "pedra"),
        box("cascalho1", [4.25, 0.5, 4.25], [6, 1.1, 6], "gravel"),
        box("cascalho2", [10, 0.5, 10.6], [11.75, 0.9, 11.75], "gravel"),
        # Cavalete: 4 pernas e moldura de cima
        box("perna_no", [1, 2, 1], [2.5, 24, 2.5], "darkwood"),
        box("perna_ne", [13.5, 2, 1], [15, 24, 2.5], "darkwood"),
        box("perna_so", [1, 2, 13.5], [2.5, 24, 15], "mossy"),
        box("perna_se", [13.5, 2, 13.5], [15, 24, 15], "darkwood"),
        box("topo_o", [1, 24, 1], [2.5, 25.5, 15], "darkwood"),
        box("topo_l", [13.5, 24, 1], [15, 25.5, 15], "darkwood"),
        box("topo_n", [2.5, 24, 1], [13.5, 25.5, 2.5], "planks"),
        box("topo_s", [2.5, 24, 13.5], [13.5, 25.5, 15], "planks"),
        box("prateleira_motor", [2.5, 24, 3], [5.5, 25.5, 9], "planks"),
        box("prancha", [10, 24, 2.5], [13.5, 25.5, 9], "planks"),
        box("travessa_guias", [2.5, 24, 9], [13.5, 25.5, 10.5], "darkwood"),
        box("mao_no", [2.5, 19, 1.25], [3.5, 24, 2.25], "darkwood", {"z": 40}, [2.5, 24, 1.75]),
        box("mao_ne", [12.5, 19, 1.25], [13.5, 24, 2.25], "darkwood", {"z": -40}, [13.5, 24, 1.75]),
        # 2 guias de ferro (o martelo corre encostado nelas), do fundo do buraco até a travessa
        box("guia_o", [4.9, 0.5, 8.6], [5.9, 24, 10.4], "iron"),
        box("guia_l", [10.1, 0.5, 8.6], [11.1, 24, 10.4], "iron"),
        # Motor em cima da prateleira
        *pm,
        # Bauzinho com pedra quebrada e montinho do lado
        box("bau", [12.5, 2, 4.5], [15.5, 6, 11.5], "chestside"),
        box("bau_tampa", [12.35, 6, 4.35], [15.65, 6.6, 11.65], "chestlid"),
        box("bau_pedra", [13, 6.6, 6], [15, 7.4, 9], "pedra"),
        box("monte_pedra", [4.5, 2, 12.5], [7, 3, 14.5], "gravel"),
        *terminal(11.75, 25.5, 5.25, "antena"),
        *lampada(11.75, 25.5, 7.9),
        box("musgo", [0.2, 2, 4.5], [3.5, 2.15, 8], "moss"),
    ]
    # Martelo (desenhado na posição mais baixa) + cremalheira com dentes virados pro pinhão
    martelo = [
        box("martelo_ponta", [7, 0.5, 7], [9, 2.5, 9], "iron"),
        box("martelo", [5.9, 2.5, 6], [10.1, 8.5, 10], "darkiron"),
        box("martelo_tampa", [6.3, 8.5, 6.4], [9.7, 9, 9.6], "corroded"),
        box("cremalheira", [5.95, 9, 7.6], [6.7, 30, 8.4], "iron"),
    ]
    for i in range(21):
        y = 9.5 + i
        martelo.append(box(f"crem_dente{i}", [5.95, y, 7.2], [6.7, y + 0.5, 7.6], "corroded"))
    pinhao = pg

    # =================================================================
    # SONDA DE MINÉRIO — tripé com caixa de engrenagens em cima; o motor fica pendurado embaixo da
    # caixa e o pinhão dele engata na coroa da broca (ângulo reto). Mostrador, lente e rolo de papel.
    # =================================================================
    SX, SZ = 7, 8
    sm, sg = motor(2.075, 17.45, SZ, comp=3, raio=1.4, eixo="x", nome="motor")
    sm = arrumar_motor(sm, "x", sem_pe=True)
    sonda = [
        box("chao", [1, 0, 0.5], [13, 0.75, 14.5], "gravel"),
        # Pernas do tripé (sapata no chão, encontram a caixa embaixo)
        box("pe_a", [5.75, 0.75, 0.5], [8.25, 1.5, 3], "carcaca"),
        box("pe_b", [1.25, 0.75, 11.75], [3.25, 1.5, 14.25], "carcaca"),
        box("pe_c", [10.75, 0.75, 11.75], [12.75, 1.5, 14.25], "carcaca"),
        box("perna_a", [6.25, 1.5, 1.0], [7.75, 19.4, 2.5], "darkiron", {"x": 12.1}, [7, 1.5, 1.75]),
        box("perna_b", [1.5, 1.5, 12.25], [3, 19.2, 13.75], "darkiron", {"x": -8.1, "z": -2.5}, [2.25, 1.5, 13]),
        box("perna_c", [11, 1.5, 12.25], [12.5, 19.2, 13.75], "darkiron", {"x": -8.1, "z": 2.5}, [11.75, 1.5, 13]),
        # Caixa de engrenagens
        box("cabeca", [2, 19, 5], [12, 23, 11], "carcaca"),
        box("cabeca_tampa", [1.75, 23, 4.75], [12.25, 23.75, 11.25], "rebite"),
        box("suporte_motor_o", [0.6, 18.85, 7.25], [1.35, 19, 8.75], "darkiron"),
        box("suporte_motor_l", [2.8, 18.85, 7.25], [3.55, 19, 8.75], "darkiron"),
        *sm,
        # Mostrador com moldura, ponteiro e pino
        box("mostrador", [6, 19.5, 11], [10, 22.5, 11.4], "paper"),
        box("mostrador_aro_b", [5.75, 19, 11], [10.25, 19.5, 11.55], "brass"),
        box("mostrador_aro_c", [5.75, 22.5, 11], [10.25, 23, 11.55], "brass"),
        box("mostrador_aro_o", [5.75, 19.5, 11], [6, 22.5, 11.55], "brass"),
        box("mostrador_aro_l", [10, 19.5, 11], [10.25, 22.5, 11.55], "brass"),
        box("ponteiro", [7.8, 20.2, 11.4], [8.2, 22, 11.5], "red", {"z": 30}, [8, 20.2, 11.45]),
        box("ponteiro_pino", [7.7, 19.9, 11.4], [8.3, 20.5, 11.6], "brass"),
        # Lente que acende quando acha minério
        box("lente_aro", [2.5, 20.25, 11], [5, 22.25, 11.3], "brass"),
        box("lente", [2.75, 20.5, 11.3], [4.75, 22, 11.5], "luz"),
        # Rolo de papel do lado (imprime o resultado)
        box("rolo_braco1", [12, 19.5, 6], [13.6, 20.75, 6.5], "darkiron"),
        box("rolo_braco2", [12, 19.5, 9.5], [13.6, 20.75, 10], "darkiron"),
        box("rolo_eixo", [12.4, 19.75, 6.5], [13.1, 20.5, 9.5], "iron"),
        box("rolo", [12.1, 19.25, 7], [13.6, 21, 9], "paper"),
        box("papel_saindo", [13.35, 15.5, 7.25], [13.6, 19.25, 8.75], "paper"),
        *terminal(9.5, 23.75, 8, "antena"),
        *lampada(4.5, 23.75, 8),
        box("musgo", [8.5, 0.75, 9.5], [10.5, 0.9, 11.5], "moss"),
    ]
    broca = [
        box("haste", [SX - 0.75, 0.75, SZ - 0.75], [SX + 0.75, 19, SZ + 0.75], "iron"),
        *disco(box, "coroa", (SX, 0, SZ), 2.2, 15, 15.7, "corroded"),
        *dentes(box, "coroa_dente", SX, SZ, 15.7, 16.2, 1.4, 2.2, 0.55, 8, "corroded"),
        *disco(box, "mandril", (SX, 0, SZ), 1.25, 13.6, 14.6, "darkiron"),
    ]
    for i in range(6):
        broca += disco(box, f"rosca{i}_", (SX, 0, SZ), 1.3, 2.5 + i * 2, 3.1 + i * 2, "corroded")
    sonda_pinhao = sg

    # =================================================================
    # PAINEL DA REDE — quadro de parede (lado norte do bloco): relógios de entra/sai com moldura,
    # barrinhas de carga, plaquinhas das máquinas com luzinhas e a alavanca geral.
    # =================================================================
    painel = [
        box("moldura_cima", [0, 15, 0], [16, 16, 2.5], "darkwood"),
        box("moldura_baixo", [0, 0, 0], [16, 2, 2.5], "darkwood"),
        box("moldura_o", [0, 2, 0], [1, 15, 2.5], "darkwood"),
        box("moldura_l", [15, 2, 0], [16, 15, 2.5], "mossy"),
        box("fundo", [1, 2, 0.25], [15, 15, 1.5], "planks"),
        *[box(f"prego{i}", [x, y, 2.5], [x + 0.5, y + 0.5, 2.7], "darkiron")
          for i, (x, y) in enumerate([(0.25, 0.75), (15.25, 0.75), (0.25, 15.25), (15.25, 15.25)])],
        box("placa_latao", [1.5, 11, 1.5], [14.5, 14.5, 2], "brass"),
        box("placa_nome", [7, 12.5, 2], [9, 13.5, 2.2], "paper"),
        box("ferrugem", [1.5, 2.5, 1.5], [3, 3, 1.55], "corroded"),
        # Barrinhas de carga das baterias
        box("barras_fundo", [2.5, 8, 1.5], [13.5, 10.5, 2], "darkiron"),
        box("barra1", [3, 8.5, 2], [5, 10, 2.3], "luz"),
        box("barra2", [5.5, 8.5, 2], [7.5, 10, 2.3], "luz"),
        box("barra3", [8, 8.5, 2], [10, 10, 2.3], "luz"),
        box("barra4_vazia", [10.5, 8.5, 2], [12.5, 10, 2.3], "coal"),
        # Plaquinhas das máquinas com lampadinhas (uma vermelha = parada)
        box("plaquinhas", [2, 3, 1.5], [12, 7.5, 2], "darkwood"),
        box("plaq1", [2.5, 5.5, 2], [6, 7, 2.2], "paper"),
        box("plaq2", [2.5, 3.5, 2], [6, 5, 2.2], "paper"),
        box("plaq3", [7, 5.5, 2], [10.5, 7, 2.2], "paper"),
        box("plaq4", [7, 3.5, 2], [10.5, 5, 2.2], "paper"),
        box("luzinha1", [6.2, 5.9, 2], [6.9, 6.6, 2.5], "luz"),
        box("luzinha2", [6.2, 3.9, 2], [6.9, 4.6, 2.5], "luz"),
        box("luzinha3", [10.7, 5.9, 2], [11.4, 6.6, 2.5], "luz"),
        box("luzinha_vermelha", [10.7, 3.9, 2], [11.4, 4.6, 2.5], "red", glow=200),
        # Alavanca geral
        box("alavanca_base", [12.5, 3, 1.5], [14.5, 6, 2.25], "darkiron"),
        box("alavanca", [13.1, 4.5, 2.25], [13.9, 8.5, 2.9], "iron", {"x": 20}, [13.5, 4.5, 2.5]),
        box("alavanca_bola", [12.9, 7.8, 3.4], [14.1, 8.8, 4.4], "red"),
        *terminal(3, 16, 1.25, "antena"),
        *lampada(13, 16, 1.25),
    ]
    # Relógios de ponteiro (entra / sai) com moldura de ferro
    for nome, x0 in (("entra", 2.5), ("sai", 9.5)):
        painel += [
            box(f"relogio_{nome}", [x0, 11.5, 2], [x0 + 4, 14, 2.4], "paper"),
            box(f"bisel_{nome}_c", [x0 - 0.25, 14, 2], [x0 + 4.25, 14.25, 2.5], "darkiron"),
            box(f"bisel_{nome}_b", [x0 - 0.25, 11.25, 2], [x0 + 4.25, 11.5, 2.5], "darkiron"),
            box(f"bisel_{nome}_o", [x0 - 0.25, 11.5, 2], [x0, 14, 2.5], "darkiron"),
            box(f"bisel_{nome}_l", [x0 + 4, 11.5, 2], [x0 + 4.25, 14, 2.5], "darkiron"),
        ]
    painel += [
        box("ponteiro_entra", [4.3, 12, 2.4], [4.7, 13.75, 2.5], "red", {"z": -35}, [4.5, 12, 2.45]),
        box("ponteiro_sai", [11.3, 12, 2.4], [11.7, 13.75, 2.5], "red", {"z": 20}, [11.5, 12, 2.45]),
    ]

    return {
        "auto_chocadeira": {
            "title": "Chocadeira",
            "parts": {
                "base": {"label": "Caixa com ovos", "elements": choca},
                "ovo_chocando": {"label": "Ovo chocando", "elements": ovo_chocando},
                "pintinho": {"label": "Pintinho nascendo", "elements": pintinho},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Caixa de madeira com tampa de vidro e lâmpada de calor: põe os ovos (galados) na palha e ela mantém a temperatura certa, igual a galinha chocando. O pintinho sai sozinho e fica do lado. O termômetro da frente mostra se está quente o suficiente. Gasta pouco. Receita: tábuas, vidro, palha e cobre.",
                "modes": [["parado", "Sem energia"], ["ligado", "Chocando"], ["nasceu", "Nasceu!"]],
                "default": "ligado",
                "show": {"pintinho": ["nasceu"], "ovo_chocando": ["parado", "ligado"]},
                "light": {"at": [8, 9.5, 6], "color": "#ffa040", "intensity": 1.0},
                "cam": {"pos": [1.9, 1.5, 2.3], "target": [0.5, 0.25, 0.5]},
            },
        },
        "auto_pedreira": {
            "title": "Pedreira Automática",
            "parts": {
                "base": {"label": "Cavalete, guias e motor (parados)", "elements": pedreira},
                "martelo": {"label": "Martelo + cremalheira (sobe e cai)", "elements": martelo},
                "pinhao": {"label": "Pinhão do motor (vai e volta)", "elements": pinhao},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Bate-estaca de pedreira: o motor lá em cima gira o pinhão, que puxa a cremalheira presa no martelo; o martelo sobe correndo entre as 2 guias de ferro e cai com tudo no buraco. Vai quebrando a pedra numa área embaixo (camada por camada, até onde você mandar) e as pedras soltas vão pro bauzinho. Não pega minério nem quebra baú/construção — só pedra, cascalho e terra. Gasta muito. Receita: tábuas, ferro, pedras e engrenagem enferrujada.",
                "pivots": {"martelo": [8, 0, 8], "pinhao": [3.2, PY, PZ]},
                "anim": [{"part": "martelo", "bob": "y", "amp": 5, "freq": 1.1},
                         {"part": "pinhao", "swing": "x", "amp": -2.0, "freq": 1.1}],
                "fx": {"ligado": [{"type": "dust", "at": [8, 1.5, 8], "rate": 0.5}]},
                "cam": {"pos": [2.6, 2.2, 3.2], "target": [0.5, 0.8, 0.5]},
            },
        },
        "auto_sonda": {
            "title": "Sonda de Minério",
            "parts": {
                "base": {"label": "Tripé, caixa e motor (parados)", "elements": sonda},
                "broca": {"label": "Broca + coroa (gira)", "elements": broca},
                "motor": {"label": "Pinhão do motor (gira)", "elements": sonda_pinhao},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Tripé de ferro com uma broca fininha que gira entrando no chão — é a picareta de prospecção, só que sozinha e no chunk inteiro: o motor pendurado embaixo da caixa gira a coroa da broca pelo pinhão. Depois de um tempo marca no mapa os minérios que tem embaixo (o que é e a quantidade, tipo 'cobre — bastante'), a lente acende quando acha e o rolinho de papel do lado imprime o resultado. Gasta médio enquanto sonda, depois desliga. Receita: barras de ferro, cobre, papel e engrenagem enferrujada.",
                "pivots": {"broca": [SX, 0, SZ], "motor": [2.075, 17.45, SZ]},
                "modes": [["parado", "Sem energia"], ["ligado", "Sondando"]],
                "anim": [{"part": "broca", "spin": "y", "speed": 3}, {"part": "motor", "spin": "x", "speed": -4.32}],
                "fx": {"ligado": [{"type": "energy", "at": [3.75, 21.25, 11.6], "rate": 0.15},
                                  {"type": "dust", "at": [7, 1, 8], "rate": 0.3}]},
                "cam": {"pos": [2.3, 2.0, 3.0], "target": [0.5, 0.65, 0.5]},
            },
        },
        "auto_painel": {
            "title": "Painel da Rede",
            "parts": {"base": {"label": "Quadro de parede", "elements": painel}},
            "auto": {
                "cat": "maquina",
                "desc": "Quadro de madeira e latão pra pendurar na parede: mostra a rede toda de um jeito fácil. O relógio da esquerda é quanto entra (fontes), o da direita quanto sai (máquinas), as barrinhas são a carga das baterias e cada plaquinha é uma máquina — luz azul trabalhando, luz vermelha parada por falta de energia. Clique numa plaquinha pra ligar/desligar aquela máquina; a alavanca desliga tudo. Gasta quase nada. Receita: tábuas, latão/cobre, papel e vidro.",
                "cam": {"pos": [0.9, 1.0, 2.6], "target": [0.5, 0.5, 0.1]},
            },
        },
    }
