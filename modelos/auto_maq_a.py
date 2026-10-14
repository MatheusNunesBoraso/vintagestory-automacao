"""
AUTOMAÇÃO — máquinas (grupo A): Colheitadeira, Moedor, Peneira, Pesca e Serraria elétricos.
Mesma família: base de pedra/madeira velha, carcaça enferrujada, motor do kit, antena (borne), lampadinha e saída.
Polidas com as regras: coerência mecânica (engrenagem redonda engata em redonda, correia de polia a polia,
pivô no centro do eixo), nada sobreposto e nada flutuando.
"""
import math

TEX = {
    "fruta_verm": "game:item/food/fruit/raspberry",
    "fruta_cereja": "game:item/food/fruit/cherry",
}


def modelos(k):
    box, motor, terminal, lampada = k.box, k.motor, k.terminal, k.lampada

    def mot(cx, cy, cz, **kw):
        """Motor do kit sem faces piscando: a 2ª carcaça (girada) fica um pouquinho mais curta no eixo."""
        caixa, gira = motor(cx, cy, cz, **kw)
        ax = 0 if kw.get("eixo", "x") == "x" else 2
        for e in caixa + gira:
            if e["name"].endswith("_corpo2") or e["name"].endswith("_polia2"):
                e["from"][ax] += 0.05
                e["to"][ax] -= 0.05
        return caixa, gira

    def cil(nome, c, r, a0, a1, tex, eixo="y", faces=None):
        """Cilindro octogonal: quadrado + quadrado girado 45° (um pouco mais curto, pra não piscar)."""
        if eixo == "y":
            f0, t0 = [c[0] - r, a0, c[2] - r], [c[0] + r, a1, c[2] + r]
            f1, t1 = [c[0] - r, a0 + 0.05, c[2] - r], [c[0] + r, a1 - 0.05, c[2] + r]
            o = [c[0], (a0 + a1) / 2, c[2]]
        elif eixo == "x":
            f0, t0 = [a0, c[1] - r, c[2] - r], [a1, c[1] + r, c[2] + r]
            f1, t1 = [a0 + 0.05, c[1] - r, c[2] - r], [a1 - 0.05, c[1] + r, c[2] + r]
            o = [(a0 + a1) / 2, c[1], c[2]]
        else:
            f0, t0 = [c[0] - r, c[1] - r, a0], [c[0] + r, c[1] + r, a1]
            f1, t1 = [c[0] - r, c[1] - r, a0 + 0.05], [c[0] + r, c[1] + r, a1 - 0.05]
            o = [c[0], c[1], (a0 + a1) / 2]
        return [box(nome, f0, t0, tex, faces=faces), box(nome + "_45", f1, t1, tex, {eixo: 45}, o, faces=faces)]

    def engrenagem(nome, c, r, a0, a1, tex, eixo="y", n=8, d=0.6, larg=0.8):
        """Engrenagem redonda: disco octogonal + n dentes em volta (girados no eixo dela)."""
        els = cil(nome, c, r, a0, a1, tex, eixo)
        o = [c[0], (a0 + a1) / 2, c[2]] if eixo == "y" else [(a0 + a1) / 2, c[1], c[2]] if eixo == "x" else [c[0], c[1], (a0 + a1) / 2]
        for i in range(n):
            ang = 360 / n * i + 180 / n
            if eixo == "y":
                f, t = [c[0] - larg / 2, a0 + 0.1, c[2] - r - d], [c[0] + larg / 2, a1 - 0.1, c[2] - r + 0.3]
            elif eixo == "x":
                f, t = [a0 + 0.1, c[1] - r - d, c[2] - larg / 2], [a1 - 0.1, c[1] - r + 0.3, c[2] + larg / 2]
            else:
                f, t = [c[0] - larg / 2, c[1] - r - d, a0 + 0.1], [c[0] + larg / 2, c[1] - r + 0.3, a1 - 0.1]
            els.append(box(f"{nome}_d{i}", f, t, tex, {eixo: round(ang, 3)}, o))
        return els

    def bauzinho(x0, y0, z0, x1, y1, z1, p="bau"):
        """Bauzinho de saída fechado: madeira velha, tampa escura, 2 cintas de ferro e trava."""
        return [
            box(p, [x0, y0 + 0.05, z0], [x1, y1, z1], "planks"),
            box(p + "_tampa", [x0 - 0.25, y1, z0 - 0.25], [x1 + 0.25, y1 + 0.75, z1 + 0.25], "darkwood"),
            box(p + "_cinta1", [x0 + (x1 - x0) * 0.25 - 0.4, y0, z0 - 0.15], [x0 + (x1 - x0) * 0.25 + 0.4, y1 + 0.85, z1 + 0.15], "darkiron"),
            box(p + "_cinta2", [x0 + (x1 - x0) * 0.75 - 0.4, y0, z0 - 0.15], [x0 + (x1 - x0) * 0.75 + 0.4, y1 + 0.85, z1 + 0.15], "darkiron"),
            box(p + "_trava", [(x0 + x1) / 2 - 0.75, y1 - 1.5, z1 + 0.15], [(x0 + x1) / 2 + 0.75, y1 + 0.25, z1 + 0.5], "corroded"),
        ]

    def caixote(x0, y0, z0, x1, y1, z1, recheio, p="caixote", cinta=True):
        """Caixote aberto de ripas com o produto aparecendo por cima, cinta de ferro no meio."""
        m = (y0 + y1) / 2
        return [
            box(p + "_fundo", [x0, y0, z0], [x1, y0 + 0.5, z1], "planks"),
            box(p + "_n", [x0, y0 + 0.5, z0], [x1, y1, z0 + 0.5], "planks"),
            box(p + "_s", [x0, y0 + 0.5, z1 - 0.5], [x1, y1, z1], "planks"),
            box(p + "_o", [x0, y0 + 0.5, z0 + 0.5], [x0 + 0.5, y1, z1 - 0.5], "darkwood"),
            box(p + "_l", [x1 - 0.5, y0 + 0.5, z0 + 0.5], [x1, y1, z1 - 0.5], "darkwood"),
            box(p + "_recheio", [x0 + 0.5, y0 + 0.5, z0 + 0.5], [x1 - 0.5, y1 - 0.6, z1 - 0.5], recheio),
        ] + ([box(p + "_cinta", [x0 - 0.1, m - 0.3, z0 - 0.1], [x1 + 0.1, m + 0.3, z1 + 0.1], "darkiron")] if cinta else [])

    def alicerce(h=3.0):
        return [
            box("alicerce", [1, 0, 1], [15, h, 15], "cobble"),
            box("borda", [0.5, h - 0.25, 0.5], [15.5, h + 0.5, 15.5], "brick"),
            box("cinta", [0.75, 1, 0.75], [15.25, 1.75, 15.25], "darkiron"),
        ]

    # =================================================================
    # COLHEITADEIRA — poste fixo; uma luva gira em volta dele levando o braço.
    # Motor -> caixa de engrenagem -> pinhão (deitado) -> coroa (deitada) presa na luva.
    # =================================================================
    col_m, col_g = mot(13.75, 5.85, 3.0, comp=3.5, raio=1.6, eixo="z", nome="motor")
    col_base = [
        *alicerce(),
        box("mancal_poste", [6.25, 3.5, 6.25], [9.75, 5, 9.75], "darkiron"),
        box("poste", [6.75, 5, 6.75], [9.25, 25, 9.25], "darkwood"),
        box("poste_topo", [6.5, 25, 6.5], [9.5, 25.75, 9.5], "rebite"),
        box("caixa_pinhao", [12.25, 3.5, 7], [15.25, 7.5, 10], "carcaca"),
        box("caixa_pinhao_tampa", [12, 7.5, 6.75], [15.5, 8, 10.25], "rebite"),
        box("caixa_pinhao_placa", [15.25, 4, 7.5], [15.4, 7, 9.5], "engrenagens"),
        *col_m,
        *caixote(2.5, 3.5, 11, 10, 7, 14.75, "fruta_verm"),
        box("frutas_monte", [4, 6.4, 12], [7.5, 6.9, 13.75], "fruta_cereja"),
        *terminal(2.75, 3.5, 2.75, "borne"),
        *lampada(2.75, 3.5, 7.25),
        box("musgo1", [11, 3.5, 11.5], [14.5, 3.7, 14.5], "moss"),
    ]
    col_pinhao = [
        box("eixo_pinhao", [13.3, 8, 8.1], [14.1, 11, 8.9], "iron"),
        *engrenagem("pinhao", (13.7, 0, 8.5), 1.2, 9, 10, "corroded", "y", n=6, d=0.5),
    ]
    col_braco = [
        *engrenagem("coroa", (8, 0, 8), 4, 9, 10, "corroded", "y", n=14, d=0.6),
        box("cubo", [6.25, 8.5, 6.25], [9.75, 10.5, 9.75], "darkiron"),
        box("luva", [6.5, 10.5, 6.5], [9.5, 18, 9.5], "darkwood"),
        box("luva_cinta", [6.3, 13, 6.3], [9.7, 13.75, 9.7], "darkiron"),
        box("colar", [6, 18, 6], [10, 20.5, 10], "carcaca"),
        box("braco", [10, 18.75, 7.25], [26, 20.25, 8.75], "darkwood"),
        box("contra", [-4.25, 18.75, 7.25], [6, 20.25, 8.75], "darkwood"),
        box("braco_cinta", [17, 18.5, 7], [18, 20.5, 9], "darkiron"),
        box("contrapeso", [-4, 15, 6.25], [0, 18.75, 9.75], "cobble"),
        box("contrapeso_cinta", [-4.25, 16.5, 6], [0.25, 17.25, 10], "darkiron"),
        box("mao_francesa", [9.1, 13, 7.6], [9.9, 20.3, 8.4], "mossy", {"z": -38}, [9.5, 13, 8]),
        box("mao_francesa2", [6.1, 13, 7.6], [6.9, 20.3, 8.4], "mossy", {"z": 38}, [6.5, 13, 8]),
        # Rastelo pendurado na ponta
        box("corda_rastelo", [23.75, 12, 7.75], [24.25, 18.75, 8.25], "rope"),
        box("rastelo", [20.5, 11, 6.75], [27.5, 12, 9.25], "darkwood"),
        box("rastelo_ferro", [20.6, 10.5, 7], [27.4, 11, 9], "corroded"),
        *[box(f"dente{i}", [21 + i * 1.5, 7.5, 7.6], [21.6 + i * 1.5, 10.5, 8.4], "iron") for i in range(5)],
        # Cestinho pendurado no meio do braço
        box("corda_cesto", [15.75, 15.9, 7.75], [16.25, 18.75, 8.25], "rope"),
        box("cestinho", [14, 12, 6], [18, 15.5, 10], "basketside"),
        box("cestinho_frutas", [14.5, 15.5, 6.5], [17.5, 15.9, 9.5], "fruta_cereja"),
    ]

    # =================================================================
    # MOEDOR ELÉTRICO — mó redonda sobre pedestal redondo; no eixo da mó, uma roda de pinos
    # (coroa); o pinhão do motor (de pé) engata nos pinos, como nos moinhos antigos.
    # =================================================================
    mo_m, _ = mot(2.4, 13.1, 8, comp=3, raio=1.2, eixo="x", nome="motor")
    mo_base = [
        *alicerce(3.0),
        box("poste_no", [1, 3.5, 1], [2.5, 14.5, 2.5], "darkwood"),
        box("poste_ne", [13.5, 3.5, 1], [15, 14.5, 2.5], "darkwood"),
        box("poste_so", [1, 3.5, 13.5], [2.5, 14.5, 15], "mossy"),
        box("poste_se", [13.5, 3.5, 13.5], [15, 14.5, 15], "darkwood"),
        box("viga_n", [1, 14.5, 1], [15, 16, 2.5], "darkwood"),
        box("viga_s", [1, 14.5, 13.5], [15, 16, 15], "darkwood"),
        box("viga_o", [1, 14.75, 2.5], [2.5, 15.75, 13.5], "darkwood"),
        box("viga_l", [13.5, 14.75, 2.5], [15, 15.75, 13.5], "mossy"),
        # Duas tábuas seguram o funil pelas bordas (a boca passa no meio delas)
        box("apoio_n", [2.5, 14.75, 4.5], [13.5, 15.5, 5.5], "planks"),
        box("apoio_s", [2.5, 14.75, 10.5], [13.5, 15.5, 11.5], "planks"),
        box("funil_fundo", [4.5, 15.5, 4.5], [11.5, 16, 11.5], "planks"),
        box("funil_n", [4.5, 16, 4.5], [11.5, 18.5, 5.25], "planks", {"x": -12}, [8, 16, 5]),
        box("funil_s", [4.5, 16, 10.75], [11.5, 18.5, 11.5], "planks", {"x": 12}, [8, 16, 11]),
        box("funil_o", [4.5, 16, 5.25], [5.25, 18.5, 10.75], "darkwood", {"z": 12}, [5, 16, 8]),
        box("funil_l", [10.75, 16, 5.25], [11.5, 18.5, 10.75], "darkwood", {"z": -12}, [11, 16, 8]),
        box("funil_boca", [6.5, 12.75, 6.5], [9.5, 15.5, 9.5], "darkwood"),
        box("funil_grao", [5.5, 16, 5.5], [10.5, 17.25, 10.5], "gravel"),
        # Pedestal e mó de baixo (fixos, redondos)
        *cil("pedestal", (8, 0, 8), 4, 3.5, 5, "cobble"),
        *cil("mo_baixo", (8, 0, 8), 3.6, 5, 7, "quern", faces={"up": "grooves"}),
        # Bica saindo da mó pro caixote de farinha
        box("bica", [7, 5.4, 11.4], [9, 5.8, 15], "planks", {"x": 15}, [8, 5.6, 11.4]),
        box("bica_lado_o", [6.75, 5.4, 11.4], [7, 6.4, 15], "darkwood", {"x": 15}, [8, 5.6, 11.4]),
        box("bica_lado_l", [9, 5.4, 11.4], [9.25, 6.4, 15], "darkwood", {"x": 15}, [8, 5.6, 11.4]),
        *caixote(4.75, 3.5, 13.25, 11.25, 4.9, 15.75, "flour", cinta=False),
        # Prateleira do motor (entre os postes de oeste)
        box("viga_motor", [1, 9.65, 2.5], [2.5, 10.4, 13.5], "darkwood"),
        box("prateleira", [1, 10.4, 6], [4.4, 11.15, 10], "planks"),
        *mo_m,
        *terminal(2.75, 3.5, 12.25, "borne"),
        *lampada(8, 16, 1.75),
        box("musgo1", [12.5, 3.5, 4], [14.5, 3.7, 6.5], "moss"),
    ]
    mo_motor = [
        box("eixo_motor", [4.4, 12.7, 7.6], [5.0, 13.5, 8.4], "iron"),
        *engrenagem("pinhao", (0, 13.1, 8), 1.1, 5.0, 5.7, "corroded", "x", n=8, d=0.5),
    ]
    mo_mo = [
        *cil("mo_cima", (8, 0, 8), 3.4, 7, 9, "quern", faces={"up": "grindtop", "down": "grooves"}),
        box("olho", [7.25, 9, 7.25], [8.75, 9.1, 8.75], "coal"),
        box("eixo_mo", [7.5, 9.1, 7.5], [8.5, 10.5, 8.5], "iron"),
        *cil("coroa", (8, 0, 8), 2.6, 10.5, 11.25, "corroded"),
        *[box(f"pino{i}", [7.75, 11.25, 5.45], [8.25, 12, 5.95], "iron", {"y": 36 * i + 18}, [8, 11.6, 8]) for i in range(10)],
    ]

    # =================================================================
    # PENEIRA ELÉTRICA — peneira redonda (aro de tábuas + tela) correndo em 2 trilhos;
    # a manivela do motor puxa a biela e a peneira vai e volta.
    # =================================================================
    pe_m, _ = mot(6.75, 4.75, 2.75, comp=3, raio=1.5, eixo="z", nome="motor")
    pe_base = [
        box("alicerce", [1, 0, 1], [15, 2, 15], "cobble"),
        box("borda", [0.5, 1.75, 0.5], [15.5, 2.5, 15.5], "brick"),
        box("poste_no", [1, 2.5, 1], [2.5, 11, 2.5], "darkwood"),
        box("poste_ne", [13.5, 2.5, 1], [15, 11, 2.5], "darkwood"),
        box("poste_so", [1, 2.5, 13.5], [2.5, 11, 15], "mossy"),
        box("poste_se", [13.5, 2.5, 13.5], [15, 11, 15], "darkwood"),
        box("viga_o", [1, 11, 1], [2.5, 12, 15], "darkwood"),
        box("viga_l", [13.5, 11, 1], [15, 12, 15], "darkwood"),
        box("trilho_n", [2.5, 11.25, 4], [13.5, 12, 5], "iron"),
        box("trilho_s", [2.5, 11.25, 11], [13.5, 12, 12], "iron"),
        box("cinta_no", [0.75, 7, 0.75], [2.75, 8, 2.75], "iron"),
        box("cinta_se", [13.25, 7, 13.25], [15.25, 8, 15.25], "iron"),
        # Calha pendurada no trilho, leva o que cai pro caixote
        box("calha", [5, 9.25, 7.75], [11, 9.75, 12.25], "darkiron", {"x": 15}, [8, 9.5, 7.75]),
        box("calha_corda", [7.75, 9.75, 11.25], [8.25, 11.25, 11.75], "rope"),
        *caixote(4.5, 2.5, 9.5, 11.5, 7, 14, "gravel"),
        box("achado1", [6, 6.4, 10.5], [6.8, 6.6, 11.3], "bronze"),
        box("achado2", [9, 6.4, 12], [9.6, 6.6, 12.6], "brass"),
        *pe_m,
        *terminal(13, 2.5, 7, "borne"),
        *lampada(14.25, 12, 1.75),
        box("musgo1", [2.5, 2.5, 12.75], [4.4, 2.7, 14.5], "moss"),
    ]
    pe_motor = [
        box("eixo_motor", [6.35, 4.35, 4.75], [7.15, 5.15, 5.5], "iron"),
        *cil("manivela", (6.75, 4.75, 0), 1.5, 5.5, 6.25, "darkiron", "z"),
        box("manivela_pino", [6.4, 5.6, 6.25], [7.1, 6.3, 6.85], "iron"),
    ]
    pe_pan = [
        *cil("tela", (8, 0, 8), 4.8, 12.05, 12.45, "net"),
        *cil("cascalho", (8, 0, 8), 4.2, 12.45, 13.05, "gravel"),
        box("cascalho_monte", [6, 13.05, 6], [10, 13.55, 10], "gravel"),
        *[box(f"aro{i}", [5.775, 12, 2.7], [10.225, 14.25, 3.3], "panwood" if i % 2 else "darkwood",
              {"y": 45 * i} if i else None, [8, 12, 8] if i else None) for i in range(8)],
        box("suporte_biela", [6.25, 11.4, 6.5], [7.25, 12.05, 7.5], "darkiron"),
        box("biela", [6.35, 5.85, 6.6], [7.15, 11.4, 7.4], "corroded"),
    ]

    # =================================================================
    # PESCA ELÉTRICA — guincho: o motor gira o tambor (de verdade, enrolando a corda);
    # a corda sobe pela roldana do mastro, corre na lança e desce até o cesto-rede na água.
    # =================================================================
    ps_m, _ = mot(4, 7, 5.25, comp=3.5, raio=1.75, eixo="z", nome="motor")
    ps_base = [
        box("pilar_no", [0.5, 0, 0.5], [3.5, 3, 3.5], "cobble"),
        box("pilar_so", [0.5, 0, 12.5], [3.5, 3, 15.5], "cobble"),
        box("pilar_ne", [12.5, 0, 0.5], [15.5, 3, 3.5], "cobble"),
        box("pilar_se", [12.5, 0, 12.5], [15.5, 3, 15.5], "cobble"),
        box("deque", [0, 3, 0], [16, 4, 16], "planks"),
        box("deque_viga1", [0, 2.25, 4], [16, 3, 5], "darkwood"),
        box("deque_viga2", [0, 2.25, 11], [16, 3, 12], "mossy"),
        box("base_motor", [2, 4, 3.5], [6, 4.5, 7.5], "darkiron"),
        *ps_m,
        box("mancal_tambor", [3, 4, 13.75], [5, 8, 14.75], "darkiron"),
        # Mastro e lança sobre a água
        box("mastro_a", [7.5, 4, 11.75], [9, 21, 13.25], "darkwood"),
        box("mastro_b", [13, 4, 11.75], [14.5, 21, 13.25], "mossy"),
        box("mastro_cinta", [7.25, 12, 11.5], [14.75, 13, 13.5], "darkiron"),
        box("lanca", [6, 21, 11.75], [27, 22.5, 13.25], "darkwood"),
        box("lanca_escora", [13, 17, 12], [22.5, 18, 13], "darkwood", {"z": 47}, [17.75, 17.5, 12.5]),
        box("lanca_cinta", [19.5, 20.75, 11.5], [20.5, 22.75, 13.5], "darkiron"),
        *cil("roldana_raiz", (7.7, 20.5, 0), 1.25, 10.75, 11.75, "darkiron", "z"),
        *cil("roldana_ponta", (25, 20.5, 0), 1.25, 10.75, 11.75, "darkiron", "z"),
        box("corda_sobe", [6.2, 7, 11], [6.7, 20.5, 11.5], "rope"),
        box("corda_lanca", [7.7, 21.55, 11], [25, 21.95, 11.5], "rope"),
        box("corda_fixa", [26, 13, 11], [26.5, 20.5, 11.5], "rope"),
        *caixote(8.5, 4, 2, 14.5, 8, 6.5, "fishfresh"),
        *terminal(1.75, 4, 1.75, "borne"),
        *lampada(14.75, 4, 14.75),
        box("musgo1", [9, 4, 8], [12.5, 4.2, 10.5], "moss"),
    ]
    ps_tambor = [
        box("eixo_tambor", [3.6, 6.6, 7.5], [4.4, 7.4, 14.25], "iron"),
        *cil("tambor", (4, 7, 0), 2.1, 9.25, 12.75, "darkwood", "z"),
        *cil("tambor_corda", (4, 7, 0), 2.2, 9.75, 12.25, "rope", "z"),
        *cil("aba_a", (4, 7, 0), 2.9, 8.75, 9.25, "darkiron", "z"),
        *cil("aba_b", (4, 7, 0), 2.9, 12.75, 13.25, "darkiron", "z"),
        box("marca_a", [3.75, 4.4, 8.6], [4.25, 9.6, 8.75], "corroded"),
        box("marca_b", [1.4, 6.75, 8.55], [6.6, 7.25, 8.7], "corroded"),
    ]
    ps_cesto = [
        box("aro_n", [23, 4.5, 8.5], [29.5, 5.25, 9.25], "darkwood"),
        box("aro_s", [23, 4.5, 13.25], [29.5, 5.25, 14], "darkwood"),
        box("aro_o", [23, 4.5, 9.25], [23.75, 5.25, 13.25], "darkwood"),
        box("aro_l", [28.75, 4.5, 9.25], [29.5, 5.25, 13.25], "darkwood"),
        box("travessa", [23.75, 4.6, 11], [28.75, 5.25, 11.5], "darkwood"),
        box("rede_n", [23.5, 1, 9], [29, 4.5, 9.5], "net"),
        box("rede_s", [23.5, 1, 13], [29, 4.5, 13.5], "net"),
        box("rede_o", [23.5, 1, 9.5], [24, 4.5, 13], "net"),
        box("rede_l", [28.5, 1, 9.5], [29, 4.5, 13], "net"),
        box("cesto_fundo", [23.5, 0.5, 9], [29, 1, 13.5], "basketside"),
        box("corda_cesto", [26.05, 5.25, 11.05], [26.45, 13, 11.45], "rope"),
        box("peixe1", [24.5, 1, 10], [28, 2.25, 11.25], "fishfresh"),
        box("peixe2", [25, 1, 11.75], [27.75, 2, 12.75], "fishfresh", {"y": 20}),
    ]

    # =================================================================
    # SERRARIA ELÉTRICA — bancada com serra circular redonda; o motor embaixo, de lado,
    # gira a serra por uma correia de polia a polia (mesmo plano). A tora vai sendo cortada ao meio.
    # =================================================================
    se_m, se_g = mot(5.25, 4.75, 2.5, comp=4, raio=1.75, eixo="x", nome="motor")
    # Correias: tangentes de cima e de baixo entre a polia do motor (y 4.75, z 2.5) e a da serra (y 7.6, z 8)
    p1, p2, rp = (4.75, 2.5), (7.6, 8.0), 1.25
    dy, dz = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dy, dz)
    th = math.degrees(math.atan2(dy, dz))
    ny, nz = dz / L, -dy / L
    correias = []
    for nome, s in (("correia_a", 1), ("correia_b", -1)):
        cy, cz = (p1[0] + p2[0]) / 2 + s * rp * ny, (p1[1] + p2[1]) / 2 + s * rp * nz
        correias.append(box(nome, [8.6, cy - 0.15, cz - L / 2], [9.15, cy + 0.15, cz + L / 2], "leather",
                            {"x": round(-th, 3)}, [8.875, cy, cz]))
    se_base = [
        box("alicerce", [0.5, 0, 0.5], [15.5, 2, 15.5], "cobble"),
        box("borda", [0.25, 1.75, 0.25], [15.75, 2.25, 15.75], "brick"),
        box("perna_no", [3, 2.25, 4.5], [4, 9, 5.5], "darkwood"),
        box("perna_ne", [12, 2.25, 4.5], [13, 9, 5.5], "darkwood"),
        box("perna_so", [3, 2.25, 10.5], [4, 9, 11.5], "mossy"),
        box("perna_se", [12, 2.25, 10.5], [13, 9, 11.5], "darkwood"),
        box("mesa_o", [3, 9, 0], [7.5, 10, 16], "planks"),
        box("mesa_l", [8.5, 9, 0], [13, 10, 16], "planks"),
        box("mesa_n", [7.5, 9, 0], [8.5, 10, 3], "planks"),
        box("mesa_s", [7.5, 9, 13], [8.5, 10, 16], "planks"),
        box("guia_o", [3, 10, 0], [4, 11.5, 16], "darkiron"),
        box("guia_l", [12, 10, 0], [13, 11.5, 16], "darkiron"),
        box("chapa_o", [5, 10, 3.5], [7.5, 10.1, 12.5], "rebite"),
        box("chapa_l", [8.5, 10, 3.5], [11, 10.1, 12.5], "rebite"),
        box("mancal_serra", [9.75, 7.1, 7.5], [10.75, 9, 8.5], "darkiron"),
        # Capô por cima da lâmina, preso num braço na guia (não atrapalha a tora)
        box("capo", [6.5, 15.5, 4.5], [9.5, 16.25, 11.5], "carcaca"),
        box("capo_braco", [9.5, 15.5, 7.5], [12, 16.25, 8.5], "darkiron"),
        box("capo_poste", [12, 11.5, 7.5], [13, 16.25, 8.5], "darkiron"),
        *correias,
        *se_m,
        *bauzinho(10, 2.25, 12, 15, 6.5, 15.25),
        box("tabuas_pilha", [4.5, 10, 13.5], [11.5, 11.5, 15.75], "planks"),
        *terminal(14.25, 2.25, 2.5, "borne"),
        *lampada(8, 16.25, 9.5),
        box("musgo1", [1, 2.25, 10], [3, 2.45, 14], "moss"),
    ]
    se_serra = [box(f"lamina{i}", [7.8 + 0.03 * i, 3.85, 7.0], [8.2 - 0.03 * i, 11.35, 9.0], "iron",
                    {"x": 30 * i} if i else None, [8, 7.6, 8] if i else None) for i in range(6)]
    se_serra += [box(f"dente{i}", [7.85, 11.35, 7.7], [8.15, 11.9, 8.3], "corroded", {"x": 30 * i + 15}, [8, 7.6, 8]) for i in range(12)]
    se_serra += [
        box("lamina_cubo", [7.5, 6.95, 7.35], [8.5, 8.25, 8.65], "darkiron"),
        box("eixo_serra", [7, 7.2, 7.6], [10, 8.0, 8.4], "iron"),
        *cil("polia_serra", (0, 7.6, 8), 1.25, 8.5, 9.25, "corroded", "x"),
    ]
    se_tora = [
        box("tora_a", [5.5, 10.1, 0], [7.65, 15.1, 4], "logbark", faces={"north": "logend", "south": "logend"}),
        box("tora_b", [8.35, 10.1, 0], [10.5, 15.1, 4], "logbark", faces={"north": "logend", "south": "logend"}),
    ]

    maq = [["parado", "Sem energia"], ["ligado", "Ligado"]]
    return {
        "auto_colheitadeira": {
            "title": "Colheitadeira",
            "parts": {
                "base": {"label": "Base + poste (parada)", "elements": col_base},
                "motor": {"label": "Eixo do motor (gira)", "elements": col_g},
                "pinhao": {"label": "Pinhão (gira)", "elements": col_pinhao},
                "braco": {"label": "Coroa + braço com rastelo (gira)", "elements": col_braco},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Versão elétrica do Colhedor. Coloca no meio da horta: o motor gira o pinhão, que gira a coroa presa na luva do poste, e o braço dá a volta devagar. O rastelo pendurado colhe frutinhas e plantas maduras numa roda em volta (raio configurável), replanta com a semente e joga tudo no caixote. Gasta pouca energia (só quando tem algo pra colher). Receita: tábuas, pedras, cobre e engrenagem enferrujada.",
                "pivots": {"motor": [13.75, 5.85, 3.0], "pinhao": [13.7, 9.5, 8.5], "braco": [8, 0, 8]},
                "modes": maq,
                "anim": [{"part": "motor", "spin": "z", "speed": 6}, {"part": "pinhao", "spin": "y", "speed": -1.78},
                         {"part": "braco", "spin": "y", "speed": 0.6}],
                "fx": {"ligado": [{"type": "energy", "at": [2.75, 6.75, 2.75], "rate": 0.1}]},
                "light": {"at": [2.75, 6, 7.25], "intensity": 0.5},
                "cam": {"pos": [3.6, 2.6, 3.8], "target": [0.6, 0.7, 0.5]},
            },
        },
        "auto_moedor": {
            "title": "Moedor Elétrico",
            "parts": {
                "base": {"label": "Base, pedestal, mó de baixo e funil (parados)", "elements": mo_base},
                "motor": {"label": "Pinhão do motor (gira)", "elements": mo_motor},
                "mo": {"label": "Mó de cima + roda de pinos (gira deitada)", "elements": mo_mo},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Versão elétrica do Moleiro. Bota grão ou minério no funil: ele cai no olho da mó; o pinhão do motor engata nos pinos da roda de cima e gira a mó (igual moinho antigo). A farinha / minério moído sai pela bica pro caixote. Não precisa de rio. Gasta energia média enquanto mói. Receita: pedras, tábuas, cobre e engrenagem enferrujada.",
                "pivots": {"motor": [2.4, 13.1, 8], "mo": [8, 0, 8]},
                "modes": maq,
                "anim": [{"part": "motor", "spin": "x", "speed": 2.1}, {"part": "mo", "spin": "y", "speed": 1.2}],
                "fx": {"ligado": [{"type": "dust", "at": [8, 5.2, 14.5], "rate": 0.35}]},
                "light": {"at": [8, 18, 3], "intensity": 0.5},
                "cam": {"pos": [2.5, 1.9, 2.9], "target": [0.5, 0.6, 0.5]},
            },
        },
        "auto_peneira": {
            "title": "Peneira Elétrica",
            "parts": {
                "base": {"label": "Gaiola, trilhos e caixote (parados)", "elements": pe_base},
                "motor": {"label": "Manivela do motor (gira)", "elements": pe_motor},
                "pan": {"label": "Peneira redonda (vai e volta)", "elements": pe_pan},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Versão elétrica do Garimpeiro. Bota cascalho, areia ou terra na peneira redonda: a manivela do motor puxa a biela e a peneira corre pra lá e pra cá nos trilhos; os achados (mesma tabela da bateia do jogo) caem na calha e vão pro caixote. Não precisa de água. Gasta energia média. Receita: peneira de madeira, tábuas, cobre e engrenagem enferrujada.",
                "pivots": {"motor": [6.75, 4.75, 2.75], "pan": [8, 13, 8]},
                "modes": maq,
                "anim": [{"part": "motor", "spin": "z", "speed": 5}, {"part": "pan", "shake": "x", "amp": 0.6, "freq": 0.8}],
                "fx": {"ligado": [{"type": "dust", "at": [8, 13, 8], "rate": 0.4}]},
                "light": {"at": [14.25, 14.5, 1.75], "intensity": 0.5},
                "cam": {"pos": [2.5, 1.8, 2.9], "target": [0.5, 0.5, 0.5]},
            },
        },
        "auto_pesca": {
            "title": "Pesca Elétrica",
            "parts": {
                "base": {"label": "Deque, mastro, lança e roldanas (parados)", "elements": ps_base},
                "tambor": {"label": "Tambor do guincho (gira enrolando a corda)", "elements": ps_tambor},
                "cesto": {"label": "Cesto-rede (sobe e desce)", "elements": ps_cesto},
            },
            "auto": {
                "cat": "maquina", "agua": True,
                "desc": "Versão elétrica do Pescador. Fica na beira do rio ou lago com a lança por cima da água: o motor gira o tambor, que solta a corda e desce o cesto-rede; espera um pouco e enrola de volta, despejando os peixes no caixote do deque. Precisa de água funda (rio/lago, não poça). Gasta pouca energia (só no puxão). Receita: tábuas, corda, cobre e engrenagem enferrujada.",
                "pivots": {"tambor": [4, 7, 11], "cesto": [26.25, 0, 11.25]},
                "modes": maq,
                "anim": [{"part": "tambor", "swing": "z", "amp": 1.7, "freq": 0.25}, {"part": "cesto", "bob": "y", "amp": 7.5, "freq": 0.25}],
                "light": {"at": [14.75, 7, 14.75], "intensity": 0.5},
                "cam": {"pos": [3.6, 2.4, 3.6], "target": [1.0, 0.6, 0.6]},
            },
        },
        "auto_serraria": {
            "title": "Serraria Elétrica",
            "parts": {
                "base": {"label": "Bancada, capô e correias (parados)", "elements": se_base},
                "motor": {"label": "Eixo + polia do motor (gira)", "elements": se_g},
                "serra": {"label": "Serra circular + polia (gira)", "elements": se_serra},
                "tora": {"label": "Tora sendo cortada (passa)", "elements": se_tora},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Versão elétrica do Lenhador. A tora vai empurrada pela bancada contra a serra circular (o motor de baixo gira a serra pela correia) e sai cortada; 12 tábuas por tora caem no bauzinho (sem gastar serrote). Gasta muita energia enquanto serra. Receita: tábuas, pedras, cobre, uma lâmina de ferro e engrenagem enferrujada.",
                "pivots": {"motor": [5.25, 4.75, 2.5], "serra": [8, 7.6, 8], "tora": [8, 12, 0]},
                "modes": maq,
                "anim": [{"part": "motor", "spin": "x", "speed": 9}, {"part": "serra", "spin": "x", "speed": 9},
                         {"part": "tora", "slide": "z", "dist": 8, "speed": 0.2}],
                "fx": {"ligado": [{"type": "dust", "at": [8, 11.5, 6.5], "rate": 0.5}]},
                "light": {"at": [8, 18.5, 9.5], "intensity": 0.5},
                "cam": {"pos": [2.6, 1.9, 2.8], "target": [0.5, 0.6, 0.5]},
            },
        },
    }
