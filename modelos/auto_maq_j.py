"""
AUTOMAÇÃO — Prensa de Frutas e Fogão Elétrico (refeitos com mais capricho) + Calendário Elétrico.

Regras (do usuário): coerência mecânica (redondo engata em redondo, eixo no centro, nada quadrado
encaixando em redondo), nada sobreposto (sem faces no mesmo plano / peças se atravessando) e nada
flutuando. Peças redondas são feitas com disco()/anel() — fatias giradas com alturas levemente
escalonadas, pra as faces de cima não ficarem no mesmo plano (sem "piscar").
"""
import math

TEX = {
    "suco": "game:block/liquid/wine",
    "fruta_verm": "game:item/food/fruit/raspberry",
    "fruta_cereja": "game:item/food/fruit/cherry",
    "barril": "game:block/wood/barrel/sides",
    "balde": "game:block/wood/bucket/aged-sides",
    "panela_barro": "game:block/clay/hardened/brown1",
    "ensopado2": "game:block/food/meal/group6-spelt-onion-redcurrant-egg-redmeatstew",
    "alarme": "game:block/cloth/basic/red",
    "vidro_claro": "game:block/glass/plain",
}

T8 = math.tan(math.pi / 8)


def disco(box, nome, c, r, a0, a1, tex, eixo="y"):
    """Disco/cilindro octogonal: 4 fatias (0°, 45°, 90°, 135°) em volta do eixo.
    c = centro (x, y, z) — a coordenada do eixo é ignorada; a0..a1 = extensão ao longo do eixo.
    Cada fatia é um tiquinho mais curta que a anterior (0.02), pra não ter face no mesmo plano."""
    w = 2 * r * T8
    out = []
    for i in range(4):
        s = i * 0.02
        if eixo == "y":
            f, t = [c[0] - r, a0 + s, c[2] - w / 2], [c[0] + r, a1 - s, c[2] + w / 2]
            o = [c[0], a0, c[2]]
        elif eixo == "x":
            f, t = [a0 + s, c[1] - r, c[2] - w / 2], [a1 - s, c[1] + r, c[2] + w / 2]
            o = [a0, c[1], c[2]]
        else:
            f, t = [c[0] - r, c[1] - w / 2, a0 + s], [c[0] + r, c[1] + w / 2, a1 - s]
            o = [c[0], c[1], a0]
        out.append(box(f"{nome}{i}", f, t, tex, {eixo: 45 * i} if i else None, o if i else None))
    return out


def anel(box, nome, cx, cz, y0, y1, r, esp, tex, n=8, larg=None):
    """Anel deitado (eixo y): n pedaços em volta do centro; r = raio de fora, esp = espessura.
    Pedaços alternados um tiquinho mais baixos (sem faces no mesmo plano)."""
    lado = larg or 2 * r * math.tan(math.pi / n) + 0.1
    out = []
    for i in range(n):
        s = (i % 2) * 0.02
        out.append(box(f"{nome}{i}", [cx - lado / 2, y0 + s, cz - r], [cx + lado / 2, y1 - s, cz - r + esp], tex,
                       {"y": 360 / n * i} if i else None, [cx, y0, cz] if i else None))
    return out


def dentes(box, nome, cx, cz, y0, y1, r0, r1, larg, n, tex, giro0=0):
    """Dentes de engrenagem (coroa) em volta do eixo y: n dentes do raio r0 até r1."""
    out = []
    for i in range(n):
        a = giro0 + 360 / n * i
        out.append(box(f"{nome}{i}", [cx - larg / 2, y0, cz - r1], [cx + larg / 2, y1, cz - r0], tex,
                       {"y": a} if a else None, [cx, y0, cz] if a else None))
    return out


def arrumar_motor(els, eixo="x"):
    """Motor do kit: a 2ª metade da carcaça (cruzada) fica 0.05 mais curta no eixo do motor,
    senão as tampas das duas metades ficam no mesmo plano."""
    for e in els:
        if e["name"].endswith("_corpo2"):
            f, t = e["from"], e["to"]
            k = 0 if eixo == "x" else 2
            f[k] += 0.05
            t[k] -= 0.05
    return els


def modelos(k):
    box, terminal, lampada, motor = k.box, k.terminal, k.lampada, k.motor

    # =================================================================
    # PRENSA DE FRUTAS — prensa de fuso: cesto REDONDO de 12 aduelas com 2 aros, frutas por dentro,
    # disco de prensar REDONDO. A engrenagem-coroa (porca) gira em cima da viga e o fuso desce
    # sem girar; o pinhão do motor engata por cima nos dentes da coroa (ângulo reto).
    # =================================================================
    CX, CZ = 8, 7.5          # eixo do fuso
    R = 3.6                  # raio de dentro do cesto
    pre_base = [
        box("laje", [0, 0, 0], [16, 2, 16], "cobble"),
        # Bacia rasa de madeira (quadrada, o cesto só fica apoiado nela) com suco no fundo
        box("bacia_fundo", [2.75, 2, 3], [13.25, 2.75, 12], "planks"),
        box("bacia_n", [2.75, 2, 2.25], [13.25, 4.5, 3], "darkwood"),
        box("bacia_s", [2.75, 2, 12], [13.25, 4.5, 12.75], "darkwood"),
        box("bacia_o", [2.75, 2.75, 3], [3.5, 4.5, 12], "darkwood"),
        box("bacia_l", [12.5, 2.75, 3], [13.25, 4.5, 12], "darkwood"),
        box("suco_bacia", [3.5, 2.78, 3], [12.5, 3.55, 12], "suco"),
        # Calços que seguram o cesto acima do suco
        *[box(f"calco{i}", [x - 0.5, 2.75, z - 0.5], [x + 0.5, 3.65, z + 0.5], "darkwood")
          for i, (x, z) in enumerate([(CX - 2.4, CZ - 2.4), (CX + 2.4, CZ - 2.4), (CX - 2.4, CZ + 2.4), (CX + 2.4, CZ + 2.4)])],
        # Fundo do cesto (disco de ripas) e frutas lá dentro
        *disco(box, "cesto_fundo", (CX, 0, CZ), R + 0.55, 3.65, 4.15, "planks"),
        *disco(box, "frutas", (CX, 0, CZ), R - 0.35, 4.15, 9.0, "fruta_verm"),
        *disco(box, "frutas_monte", (CX, 0, CZ), R - 1.1, 9.0, 9.5, "fruta_cereja"),
        # Pórtico: 2 postes grossos e a viga com o furo do fuso no meio
        box("poste_o", [0.5, 3.25, 6.25], [2.75, 22, 8.75], "darkwood"),
        box("poste_l", [13.25, 3.25, 6.25], [15.5, 22, 8.75], "mossy"),
        box("sapata_o", [0.25, 2, 5.75], [2.75, 3.25, 9.25], "darkiron"),
        box("sapata_l", [13.25, 2, 5.75], [15.75, 3.25, 9.25], "darkiron"),
        box("viga_o", [0.5, 22, 5], [6.6, 25, 10], "darkwood"),
        box("viga_l", [9.4, 22, 5], [15.5, 25, 10], "darkwood"),
        box("viga_ponte_n", [6.6, 22, 5], [9.4, 25, 5.8], "darkwood"),
        box("viga_ponte_s", [6.6, 22, 9.2], [9.4, 25, 10], "darkwood"),
        box("viga_cinta_o", [2.5, 21.75, 4.75], [3.5, 25.25, 10.25], "darkiron"),
        box("viga_cinta_l", [12.5, 21.75, 4.75], [13.5, 25.25, 10.25], "darkiron"),
        box("mao_o", [2.75, 16.5, 7], [3.75, 22.75, 8], "darkwood", {"z": -35}, [2.75, 22, 7.5]),
        box("mao_l", [12.25, 16.5, 7], [13.25, 22.75, 8], "darkwood", {"z": 35}, [13.25, 22, 7.5]),
        # Mancal (anel de ferro) onde a coroa gira, em volta do furo
        *anel(box, "mancal", CX, CZ, 25, 25.3, 2.0, 0.8, "darkiron"),
        # Bica de madeira saindo da bacia + balde redondo de suco na frente
        box("bica", [7.25, 3.0, 12.75], [8.75, 3.4, 14.0], "planks", {"x": 15}, [8, 3.4, 12.75]),
        *disco(box, "balde", (8, 0, 14.4), 1.45, 2, 5.4, "balde"),
        *disco(box, "balde_suco", (8, 0, 14.4), 1.2, 5.4, 5.65, "suco"),
        *anel(box, "balde_aro", 8, 14.4, 4.6, 5.1, 1.65, 0.2, "darkiron"),
        box("balde_alca_o", [6.25, 5.1, 14.2], [6.6, 7.2, 14.6], "darkiron"),
        box("balde_alca_l", [9.4, 5.1, 14.2], [9.75, 7.2, 14.6], "darkiron"),
        box("balde_alca", [6.25, 7.2, 14.2], [9.75, 7.6, 14.6], "darkiron"),
        # Cestinho de frutas esperando
        box("cestinho", [12.75, 2, 12.75], [15.75, 4.5, 15.75], "basketside"),
        box("cestinho_frutas", [13, 4.5, 13], [15.5, 5.2, 15.5], "fruta_cereja"),
        box("frutinha_solta", [11.25, 2, 14.75], [11.75, 2.5, 15.25], "fruta_verm"),
        *terminal(14.6, 2, 1.9, "antena"),
        *lampada(1.6, 2, 13.8),
        box("musgo", [0.4, 2, 10], [2.6, 2.15, 12.4], "moss"),
    ]
    # Cesto: 12 aduelas (vão entre elas, dá pra ver as frutas) e 2 aros encostados por fora
    for i in range(12):
        a = 30 * i
        pre_base.append(box(f"aduela{i}", [CX - 0.85, 4.15, CZ - R - 0.6], [CX + 0.85, 12, CZ - R], "planks" if i % 2 else "darkwood",
                            {"y": a} if a else None, [CX, 4.15, CZ] if a else None))
    for nome, y0 in (("aro_baixo", 5.25), ("aro_cima", 10.25)):
        lado = 2 * (R + 0.6) * math.tan(math.pi / 12) + 0.05
        for i in range(12):
            a = 30 * i
            s = (i % 2) * 0.02
            pre_base.append(box(f"{nome}{i}", [CX - lado / 2, y0 + s, CZ - R - 1.0], [CX + lado / 2, y0 + 0.75 - s, CZ - R - 0.6],
                                "darkiron", {"y": a} if a else None, [CX, y0, CZ] if a else None))
    # Motor deitado em cima da viga, eixo pro leste; a polia dele é o pinhão que engata na coroa
    TOPO_DENTE = 25.3 + 0.7 + 0.6
    m_cy = TOPO_DENTE + 1.25
    m_caixa, m_gira = motor(2.8, m_cy, CZ, comp=3, raio=1.5, eixo="x", nome="motor")
    arrumar_motor(m_caixa)
    pe_baixo = m_cy - 1.5 - 0.75
    pre_base += [box("motor_base", [1.75, 25, 6.1], [3.85, pe_baixo, 8.9], "darkiron"), *m_caixa]
    pre_motor = m_gira
    # Coroa (porca do fuso): anel com dentes pra cima, gira deitada em cima do mancal
    pre_coroa = [
        *anel(box, "coroa", CX, CZ, 25.3, 26.0, 2.6, 1.45, "corroded"),
        *dentes(box, "coroa_dente", CX, CZ, 26.0, 26.6, 1.7, 2.5, 0.6, 8, "corroded"),
    ]
    # Fuso + disco de prensar: desce e sobe SEM girar (quem gira é a coroa)
    pre_fuso = [
        *disco(box, "disco_prensa", (CX, 0, CZ), R - 0.35, 11.0, 12.0, "planks"),
        *disco(box, "disco_calco", (CX, 0, CZ), 1.6, 12.0, 13.0, "darkwood"),
        box("fuso", [CX - 0.6, 13.0, CZ - 0.6], [CX + 0.6, 28.5, CZ + 0.6], "iron"),
        box("fuso_tampa", [CX - 0.9, 28.5, CZ - 0.9], [CX + 0.9, 29.0, CZ + 0.9], "corroded"),
    ]
    for i in range(12):
        pre_fuso += disco(box, f"rosca{i}_", (CX, 0, CZ), 0.95, 13.6 + i * 1.25, 14.0 + i * 1.25, "corroded")

    # =================================================================
    # FOGÃO ELÉTRICO — fogão de ferro fundido de 2 bocas: grelhas redondas com a brasa só no miolo,
    # panela de barro redonda (tampa de lado, treme fervendo), chaleira de cobre, forninho com
    # janelinha de vidro mostrando a brasa, cano da chaminé atrás.
    # =================================================================
    fog_base = [
        *[box(f"pe{i}", [x, 0, z], [x + 1.5, 2, z + 1.5], "darkiron")
          for i, (x, z) in enumerate([(1.25, 3), (13.25, 3), (1.25, 11.5), (13.25, 11.5)])],
        box("corpo", [1, 2, 2.5], [15, 11, 13], "carcaca"),
        # Frente (chapa rebitada) com o buraco do forno
        box("frente_o", [1, 2, 13], [3, 11, 13.5], "rebite"),
        box("frente_l", [8, 2, 13], [15, 11, 13.5], "rebite"),
        box("frente_baixo", [3, 2, 13], [8, 4.5, 13.5], "rebite"),
        box("frente_cima", [3, 7.5, 13], [8, 11, 13.5], "rebite"),
        box("forno_fundo", [3, 4.5, 13], [8, 7.5, 13.05], "coal"),
        box("forno_brasa", [3, 4.5, 13.05], [8, 5.0, 13.5], "ember"),
        # Porta do forno: moldura + vidro + puxador
        box("porta_o", [2, 3.5, 13.5], [3, 8.5, 14], "darkiron"),
        box("porta_l", [8, 3.5, 13.5], [9, 8.5, 14], "darkiron"),
        box("porta_cima", [3, 7.5, 13.5], [8, 8.5, 14], "darkiron"),
        box("porta_baixo", [3, 3.5, 13.5], [8, 4.5, 14], "darkiron"),
        box("porta_vidro", [3, 4.5, 13.65], [8, 7.5, 13.75], "vidro_claro"),
        box("puxador_pe_o", [3.4, 8.75, 13.5], [3.9, 9.25, 14], "brass"),
        box("puxador_pe_l", [7.1, 8.75, 13.5], [7.6, 9.25, 14], "brass"),
        box("puxador", [3.2, 8.75, 14], [7.8, 9.25, 14.4], "brass"),
        # Gaveta da cinza, botões, varão com pano de prato
        box("gaveta", [10, 2.75, 13.5], [14, 4.75, 14], "darkiron"),
        box("gaveta_puxador", [11.5, 3.5, 14], [12.5, 4, 14.3], "brass"),
        *[box(f"botao{i}", [10.25 + i * 1.5, 9.6, 13.5], [11.25 + i * 1.5, 10.6, 14.1], "brass") for i in range(3)],
        box("varao_sup_o", [9.6, 6.75, 13.5], [10.0, 7.25, 14.5], "brass"),
        box("varao_sup_l", [14.25, 6.75, 13.5], [14.65, 7.25, 14.5], "brass"),
        box("varao", [9.6, 6.75, 14.5], [14.65, 7.25, 14.9], "brass"),
        box("pano_frente", [10.5, 3.6, 14.9], [13.5, 7.25, 15.1], "rags"),
        box("pano_tras", [10.5, 5.0, 14.3], [13.5, 6.75, 14.5], "rags"),
        box("pano_dobra", [10.5, 7.25, 14.3], [13.5, 7.45, 15.1], "rags"),
        # Chapa de cima e espelho de trás
        box("chapa", [0.5, 11, 2.5], [15.5, 12, 14], "darkiron"),
        box("espelho", [0.5, 12, 2.5], [11.5, 14, 3.25], "darkiron"),
        # Cano da chaminé atrás (encosta no corpo), com colar e chapéu
        box("cano", [11.75, 8, 0], [14.25, 26, 2.5], "darkiron"),
        box("cano_colar", [11.5, 18, -0.25], [14.5, 18.75, 2.75], "corroded"),
        box("cano_chapeu", [11.25, 26, -0.5], [14.75, 26.5, 3.0], "corroded"),
        *terminal(3, 12, 4.5, "antena"),
        *lampada(8.25, 12, 4.25),
    ]
    # 2 bocas redondas: brasa no miolo, aro de ferro, grelha em cruz (barras em alturas diferentes)
    for nome, cx, cz in (("boca1", 5, 8.75), ("boca2", 11.5, 8.75)):
        fog_base += [
            *disco(box, nome + "_brasa", (cx, 0, cz), 1.8, 12, 12.1, "ember"),
            *anel(box, nome + "_aro", cx, cz, 12, 12.5, 2.4, 0.5, "darkiron"),
            box(nome + "_grelha1", [cx - 2.0, 12.5, cz - 0.25], [cx + 2.0, 12.8, cz + 0.25], "iron"),
            box(nome + "_grelha2", [cx - 0.25, 12.55, cz - 2.0], [cx + 0.25, 12.85, cz + 2.0], "iron"),
        ]
    # Panela de barro redonda na boca 1, ensopado aparecendo do lado da tampa
    fog_base += [
        *disco(box, "panela", (5, 0, 8.75), 2.6, 12.85, 16.5, "panela_barro"),
        *anel(box, "panela_borda", 5, 8.75, 16.5, 17.0, 2.75, 0.45, "panela_barro"),
        *disco(box, "ensopado", (5, 0, 8.75), 2.1, 16.5, 16.85, "ensopado2"),
        box("alca_o", [1.65, 15.0, 8.25], [2.4, 15.8, 9.25], "panela_barro"),
        box("alca_l", [7.6, 15.0, 8.25], [8.35, 15.8, 9.25], "panela_barro"),
        # Chaleira de cobre na boca 2: bojo, ombro, tampinha, bico, alça
        *disco(box, "chaleira", (11.5, 0, 8.75), 1.9, 12.85, 15.6, "bobina"),
        *disco(box, "chaleira_ombro", (11.5, 0, 8.75), 1.4, 15.6, 16.2, "bobina"),
        *disco(box, "chaleira_tampa", (11.5, 0, 8.75), 0.9, 16.2, 16.5, "cobre"),
        box("chaleira_bico", [13.4, 13.8, 8.4], [15.2, 14.5, 9.1], "bobina", {"z": 30}, [13.4, 13.8, 8.75]),
        box("chaleira_alca_o", [10.1, 16.2, 8.5], [10.5, 18, 9.0], "darkiron"),
        box("chaleira_alca_l", [12.5, 16.2, 8.5], [12.9, 18, 9.0], "darkiron"),
        box("chaleira_alca", [10.1, 18, 8.5], [12.9, 18.4, 9.0], "darkiron"),
    ]
    # Tampa da panela meio de lado (treme quando ferve)
    fog_tampa = [
        *disco(box, "tampa", (5.8, 0, 8.75), 2.4, 17.0, 17.35, "panela_barro"),
        *disco(box, "tampa_pegador", (5.8, 0, 8.75), 0.55, 17.35, 18.0, "panela_barro"),
    ]

    # =================================================================
    # CALENDÁRIO ELÉTRICO — armário de relógio: relógio, dia e mês, previsão do tempo
    # (hoje / amanhã / depois), mostrador das estações e o medidor da tempestade temporal.
    # =================================================================
    cal_base = [
        *[box(f"pe{i}", [x, 0, z], [x + 1.5, 1.5, z + 1.5], "darkwood")
          for i, (x, z) in enumerate([(1.5, 9.5), (13, 9.5), (1.5, 13.25), (13, 13.25)])],
        box("rodape", [0.75, 1.5, 9], [15.25, 3.5, 15.25], "darkwood"),
        box("fundo", [1, 3.5, 9.25], [15, 30, 10], "planks"),
        box("lado_o", [1, 3.5, 10], [2, 30, 14.5], "darkwood"),
        box("lado_l", [14, 3.5, 10], [15, 30, 14.5], "darkwood"),
        box("frente", [2, 3.5, 14], [14, 30, 14.5], "planks"),
        box("cornija", [0.5, 30, 8.75], [15.5, 31.5, 15.25], "darkwood"),
        box("friso", [2, 19.25, 14.5], [14, 19.75, 14.75], "brass"),
        box("friso2", [2, 10.25, 14.5], [14, 10.75, 14.75], "brass"),
        # Relógio: mostrador de papel com aro de latão e marquinhas
        box("mostrador", [4.5, 21, 14.5], [11.5, 28, 14.75], "paper"),
        box("aro_c", [4, 28, 14.5], [12, 28.5, 15], "brass"),
        box("aro_b", [4, 20.5, 14.5], [12, 21, 15], "brass"),
        box("aro_o", [4, 21, 14.5], [4.5, 28, 15], "brass"),
        box("aro_l", [11.5, 21, 14.5], [12, 28, 15], "brass"),
        *[box(f"marca{i}", [7.75 + dx, 24.25 + dy, 14.75], [8.25 + dx, 24.75 + dy, 14.85], "coal")
          for i, (dx, dy) in enumerate([(0, 3), (3, 0), (0, -3), (-3, 0), (2.1, 2.1), (2.1, -2.1), (-2.1, 2.1), (-2.1, -2.1)])],
        # Dia e mês: tambores de papel com os números (dia "14", mês em faixa)
        box("moldura_dia", [2.75, 15.25, 14.5], [7.5, 18.75, 14.6], "darkiron"),
        box("janela_dia", [3, 15.5, 14.6], [7.25, 18.5, 14.7], "paper"),
        box("num1", [3.7, 16, 14.7], [4.2, 18, 14.8], "coal"),
        box("num4_pe", [6.1, 16, 14.7], [6.6, 18, 14.8], "coal"),
        box("num4_meio", [5.0, 16.8, 14.7], [6.1, 17.2, 14.8], "coal"),
        box("num4_bra", [5.0, 17.2, 14.7], [5.4, 18, 14.8], "coal"),
        box("moldura_mes", [8.5, 15.25, 14.5], [13.25, 18.75, 14.6], "darkiron"),
        box("janela_mes", [8.75, 15.5, 14.6], [13, 18.5, 14.7], "paper"),
        box("mes_faixa", [9.25, 16.75, 14.7], [12.5, 17.25, 14.8], "coal"),
        # Previsão: hoje / amanhã / depois (sol, nublado, chuva)
        *[box(f"prev_moldura{i}", [2.75 + i * 3.75, 11.25, 14.5], [6 + i * 3.75, 14.5, 14.6], "darkiron") for i in range(3)],
        box("prev_sol_fundo", [3, 11.5, 14.6], [5.75, 14.25, 14.7], "white"),
        box("prev_sol", [3.75, 12.25, 14.7], [5, 13.5, 14.8], "yellow"),
        box("prev_nuvem_fundo", [6.75, 11.5, 14.6], [9.5, 14.25, 14.7], "white"),
        box("prev_nuvem", [7.1, 12.5, 14.7], [9.15, 13.5, 14.8], "gray"),
        box("prev_chuva_fundo", [10.5, 11.5, 14.6], [13.25, 14.25, 14.7], "white"),
        box("prev_chuva_nuvem", [10.85, 13, 14.7], [12.9, 13.9, 14.8], "gray"),
        *[box(f"prev_gota{i}", [11.1 + i * 0.7, 11.8, 14.7], [11.4 + i * 0.7, 12.6, 14.8], "blue") for i in range(3)],
        # Estações: mostrador de 4 cores (primavera, verão, outono, inverno)
        box("est_moldura", [2.75, 4.25, 14.5], [7.75, 9.5, 14.6], "brass"),
        box("est_primavera", [3, 7, 14.6], [5.25, 9.25, 14.7], "greenhair"),
        box("est_verao", [5.25, 7, 14.6], [7.5, 9.25, 14.7], "yellow"),
        box("est_outono", [5.25, 4.5, 14.6], [7.5, 7, 14.7], "orangeskin"),
        box("est_inverno", [3, 4.5, 14.6], [5.25, 7, 14.7], "white"),
        # Tempestade temporal: tubo de vidro (oco: paredes finas) que enche de azul + lâmpada de alarme
        box("tor_base", [9.75, 3.75, 14.5], [12.25, 4.5, 15.25], "darkiron"),
        box("tor_parede_o", [10.25, 4.5, 14.5], [10.4, 8.5, 15.1], "vidro_claro"),
        box("tor_parede_l", [11.6, 4.5, 14.5], [11.75, 8.5, 15.1], "vidro_claro"),
        box("tor_vidro", [10.4, 4.5, 14.95], [11.6, 8.5, 15.1], "vidro_claro"),
        box("tor_nivel", [10.4, 4.5, 14.5], [11.6, 6, 14.95], "luz"),
        box("tor_tampa", [9.75, 8.5, 14.5], [12.25, 9.0, 15.25], "darkiron"),
        box("tor_lamp_bocal", [10.5, 9.0, 14.6], [11.5, 9.5, 15.1], "brass"),
        box("tor_engrenagem", [12.5, 5, 14.5], [13.5, 8, 14.75], "corroded"),
        *terminal(8, 31.5, 12, "antena"),
        *lampada(3, 31.5, 12),
    ]
    cal_tormenta = [
        box("tor_cheio", [10.4, 6, 14.5], [11.6, 8.5, 14.95], "luz"),
        box("tor_alarme", [10.65, 9.5, 14.65], [11.35, 10.15, 15.05], "alarme"),
    ]
    # Ponteiros (giram no pino do centro) e o ponteiro das estações
    cal_ponteiros = [
        box("centro", [7.6, 24.1, 14.75], [8.4, 24.9, 15.1], "brass"),
        box("ponteiro_hora", [7.75, 24.9, 14.85], [8.25, 26.25, 14.95], "darkiron"),
        box("ponteiro_min", [7.85, 21.8, 14.85], [8.15, 24.1, 14.95], "darkiron"),
    ]
    cal_estacao = [box("est_pino", [4.9, 6.5, 14.7], [5.6, 7.2, 14.95], "brass"),
                   box("est_ponteiro", [5.1, 7.2, 14.75], [5.4, 9, 14.9], "darkiron", {"z": -40}, [5.25, 6.85, 14.8])]

    return {
        "auto_prensa": {
            "title": "Prensa de Frutas",
            "parts": {
                "base": {"label": "Pórtico, cesto e bacia (parados)", "elements": pre_base},
                "parafuso": {"label": "Fuso + disco de prensar (desce e sobe)", "elements": pre_fuso},
                "coroa": {"label": "Coroa / porca do fuso (gira)", "elements": pre_coroa},
                "motor": {"label": "Pinhão do motor (gira)", "elements": pre_motor},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Prensa de fuso de verdade: o cesto redondo de aduelas (com 2 aros de ferro) fica apoiado na bacia; o motor lá em cima gira a coroa (a porca do fuso) pelo pinhão, e o fuso desce sem girar, empurrando o disco redondo de prensar contra as frutas. O suco escorre entre as aduelas pra bacia e sai pela bica direto no balde (ou jarro/barril encostado). Bota frutinha, uva, maçã, pera... no cestinho do lado. Pronto pra virar vinho/cidra nos barris ou ir pro Alambique. Gasta pouco. Receita: tábuas, barras de ferro, pedras, cobre e engrenagem enferrujada.",
                "pivots": {"parafuso": [CX, 0, CZ], "coroa": [CX, 25.3, CZ], "motor": [2.8, m_cy, CZ]},
                "anim": [{"part": "parafuso", "bob": "y", "amp": -1.5, "freq": 0.12},
                         {"part": "coroa", "spin": "y", "speed": 0.8},
                         {"part": "motor", "spin": "x", "speed": -1.35}],
                "fx": {"ligado": [{"type": "dust", "at": [8, 10.5, 7.5], "rate": 0.05}]},
                "cam": {"pos": [2.3, 2.1, 3.0], "target": [0.5, 0.8, 0.5]},
            },
        },
        "auto_fogao": {
            "title": "Fogão Elétrico",
            "parts": {
                "base": {"label": "Fogão, panela e chaleira", "elements": fog_base},
                "tampa": {"label": "Tampa da panela (treme fervendo)", "elements": fog_tampa},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Fogão de ferro fundido de 2 bocas: a panela de barro (cozinha a receita da panela do jogo sozinho, no ponto, e a tampa treme quando ferve) e a chaleira de cobre (ferve água). Embaixo, o forninho com janelinha assa pão e torta. Não precisa de lenha nem de ficar vigiando: quando fica pronto ele desliga e guarda quente. Cano de chaminé atrás, pano de prato no varão. Gasta energia média enquanto cozinha. Receita: chapa de ferro, tijolos, cobre e engrenagem enferrujada.",
                "pivots": {"tampa": [5.8, 17, 8.75]},
                "glowTex": ["luz", "ember"],
                "anim": [{"part": "tampa", "bob": "y", "amp": 0.35, "freq": 3.5}],
                "fx": {"ligado": [{"type": "smoke", "at": [3.2, 17.5, 8.75], "top": 1.6, "rate": 0.6},
                                  {"type": "smoke", "at": [15, 15, 8.75], "top": 1.4, "rate": 0.3}]},
                "light": {"at": [5.5, 6, 16], "color": "#ff8a30", "intensity": 0.5},
                "cam": {"pos": [2.0, 1.7, 2.5], "target": [0.5, 0.6, 0.5]},
            },
        },
        "auto_calendario": {
            "title": "Calendário Elétrico",
            "parts": {
                "base": {"label": "Armário com mostradores", "elements": cal_base},
                "ponteiros": {"label": "Ponteiros do relógio (giram)", "elements": cal_ponteiros},
                "estacao": {"label": "Ponteiro das estações", "elements": cal_estacao},
                "tormenta": {"label": "Tempestade chegando (alarme)", "elements": cal_tormenta},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Armário de relógio velho que sabe tudo do tempo. Em cima: o relógio com a hora do jogo. Embaixo: o dia e o mês. A fileira do meio é a previsão — hoje / amanhã / depois de amanhã (sol, nublado ou chuva; neve no inverno). Embaixo à esquerda, o mostrador das estações com o ponteiro andando (primavera, verão, outono, inverno) e quantos dias faltam pra próxima. Embaixo à direita, o medidor da TEMPESTADE TEMPORAL (aquela que spawna um monte de drifter): o tubo vai enchendo de azul conforme ela chega; quando está perto a luz vermelha acende e avisa no chat. Clique direito: a mesma coisa escrita, com os dias certinhos. Gasta quase nada. Receita: tábuas, papel, vidro, latão, cobre e engrenagem enferrujada.",
                "pivots": {"ponteiros": [8, 24.5, 14.9], "estacao": [5.25, 6.85, 14.8]},
                "modes": [["parado", "Sem energia"], ["ligado", "Funcionando"], ["tormenta", "Tempestade chegando!"]],
                "show": {"tormenta": ["tormenta"]},
                "glowTex": ["luz", "alarme"],
                "anim": [{"part": "ponteiros", "spin": "z", "speed": -0.5}],
                "light": {"at": [11, 9.8, 17], "color": "#ff4030", "intensity": 1.0, "when": ["tormenta"]},
                "fx": {"tormenta": [{"type": "energy", "at": [11, 9.5, 15], "rate": 0.15}]},
                "cam": {"pos": [1.6, 1.6, 3.4], "target": [0.5, 0.95, 0.8]},
            },
        },
    }
