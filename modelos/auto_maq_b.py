"""
AUTOMAÇÃO — máquinas elétricas (grupo B): Carvoeira, Colmeia, Defumador, Vigia e Cogumelos.
Mesma família: base velha, carcaça enferrujada, motor do kit, antena (borne), lampadinha e gaveta de saída.
Polido: peças redondas onde a coisa é redonda (centrífuga, sino, skep, barril, engrenagens), engrenagens
encostando dente com dente, nada sobreposto (sem faces no mesmo plano) e nada flutuando.
"""
import math

TEX = {
    "barril": "game:block/wood/barrel/sides",
}

_T = math.tan(math.pi / 8)


def modelos(k):
    box, terminal, lampada, motor = k.box, k.terminal, k.lampada, k.motor

    # ---------- peças redondas (octógonos) ----------
    def disco_y(nome, cx, cz, y0, y1, ap, tex):
        """Disco/cilindro em pé (eixo y): quadrado + quadrado girado 45° (um pouquinho mais baixo, sem piscar)."""
        return [box(nome, [cx - ap, y0, cz - ap], [cx + ap, y1, cz + ap], tex),
                box(nome + "_r", [cx - ap, y0 + 0.03, cz - ap], [cx + ap, y1 - 0.03, cz + ap], tex, {"y": 45}, [cx, y0, cz])]

    def anel_y(nome, cx, cz, y0, y1, ap, esp, tex):
        """Anel/aduelas em pé (eixo y): 8 tábuas em volta do centro (apótema ap, espessura esp)."""
        L = ap * _T + 0.03
        return [box(f"{nome}{i}", [cx - L, y0, cz - ap], [cx + L, y1, cz - ap + esp], tex,
                    {"y": 45 * i} if i else None, [cx, y0, cz] if i else None) for i in range(8)]

    def disco_x(nome, cy, cz, x0, x1, ap, tex):
        """Disco de pé virado pro eixo x (polia, carcaça de bomba)."""
        return [box(nome, [x0, cy - ap, cz - ap], [x1, cy + ap, cz + ap], tex),
                box(nome + "_r", [x0 + 0.03, cy - ap, cz - ap], [x1 - 0.03, cy + ap, cz + ap], tex, {"x": 45}, [x0, cy, cz])]

    def anel_x(nome, cy, cz, x0, x1, ap, esp, tex):
        L = ap * _T + 0.03
        return [box(f"{nome}{i}", [x0, cy - L, cz - ap], [x1, cy + L, cz - ap + esp], tex,
                    {"x": 45 * i} if i else None, [x0, cy, cz] if i else None) for i in range(8)]

    def motor_ok(*a, sem_polia=False, **kw):
        """Motor do kit sem faces piscando (as 2 caixas da carcaça tinham as pontas no mesmo plano)."""
        caixa, gira = motor(*a, **kw)
        i = 0 if kw.get("eixo", "x") == "x" else 2
        for e in caixa:
            if e["name"].endswith("_corpo2"):
                e["from"][i] += 0.06
                e["to"][i] -= 0.06
        if sem_polia:
            gira = [e for e in gira if e["name"].endswith("_eixo")]
        return caixa, gira

    # =================================================================
    # CARVOEIRA ELÉTRICA — forno de barro cintado de ferro, porta com janelinha mostrando as
    # resistências em brasa; do lado oeste, o soprador: motor -> eixo -> ventoinha numa carcaça
    # redonda que sopra direto na parede do forno. Chaminé atrás, gaveta de carvão na frente.
    # =================================================================
    carv_motor, carv_eixo = motor_ok(2.25, 6, 7.25, comp=3, raio=1.75, eixo="x", nome="motor", sem_polia=True)
    carv_base = [
        box("alicerce", [0, 0, 0], [16, 2, 16], "cobble"),
        box("alicerce_cinta", [-0.2, 0.6, -0.2], [16.2, 1.3, 16.2], "darkiron"),
        # Forno
        box("forno", [6.5, 2, 1.5], [15.5, 12, 13], "kilnwall"),
        box("forno_topo", [7, 12, 2], [15, 13, 12.5], "kilnwall"),
        box("cinta1", [6.25, 4, 1.25], [15.75, 5, 13.25], "darkiron"),
        box("cinta2", [6.25, 9.75, 1.25], [15.75, 10.75, 13.25], "darkiron"),
        # Porta de ferro com janelinha gradeada (resistências em brasa atrás)
        box("porta", [7.5, 3, 13.25], [14.5, 11.5, 13.75], "carcaca"),
        box("janela_fundo", [9, 6.25, 13.75], [13, 9.75, 13.85], "coal"),
        box("resist1", [9.25, 6.75, 13.85], [12.75, 7.25, 13.95], "ember"),
        box("resist2", [9.25, 7.75, 13.85], [12.75, 8.25, 13.95], "ember"),
        box("resist3", [9.25, 8.75, 13.85], [12.75, 9.25, 13.95], "ember"),
        box("grade1", [10.4, 6.25, 13.95], [10.6, 9.75, 14.05], "darkiron"),
        box("grade2", [11.4, 6.25, 13.95], [11.6, 9.75, 14.05], "darkiron"),
        box("moldura_c", [8.75, 9.75, 13.75], [13.25, 10.1, 14.05], "rebite"),
        box("moldura_b", [8.75, 5.9, 13.75], [13.25, 6.25, 14.05], "rebite"),
        box("moldura_o", [8.75, 6.25, 13.75], [9, 9.75, 14.05], "rebite"),
        box("moldura_l", [13, 6.25, 13.75], [13.25, 9.75, 14.05], "rebite"),
        box("trinco", [13.6, 7, 13.75], [14.2, 9, 14.35], "corroded"),
        box("dobradica1", [7, 4.25, 13.25], [7.5, 5.5, 13.9], "darkiron"),
        box("dobradica2", [7, 9, 13.25], [7.5, 10.25, 13.9], "darkiron"),
        # Chaminé de barro com chapéu de ferro
        box("chamine", [11.5, 13, 3], [14.5, 17, 6], "chimney"),
        box("chamine_aro", [11.3, 15.5, 2.8], [14.7, 16, 6.2], "darkiron"),
        box("chamine_chapeu", [11, 17.5, 2.5], [15, 18, 6.5], "corroded"),
        box("chamine_pe_a", [11.25, 17, 2.75], [11.75, 17.5, 3.25], "darkiron"),
        box("chamine_pe_b", [14.25, 17, 5.75], [14.75, 17.5, 6.25], "darkiron"),
        # Gaveta de carvão puxada pra fora, embaixo da porta
        box("gaveta_fundo", [8, 2, 13.85], [14, 2.5, 15.75], "darkwood"),
        box("gaveta_frente", [8, 2.5, 15.25], [14, 3.6, 15.75], "darkwood"),
        box("gaveta_lado_o", [8, 2.5, 13.85], [8.5, 3.3, 15.25], "darkwood"),
        box("gaveta_lado_l", [13.5, 2.5, 13.85], [14, 3.3, 15.25], "darkwood"),
        box("gaveta_carvao", [8.5, 2.5, 13.85], [13.5, 3.1, 15.25], "coal"),
        box("gaveta_puxador", [10.5, 2.8, 15.75], [11.5, 3.3, 16.15], "brass"),
        # Soprador: pé do motor, carcaça redonda da ventoinha encostada no forno
        box("motor_suporte", [1, 2, 5.5], [3.5, 3.5, 9], "darkiron"),
        *anel_x("soprador_aro", 6, 7.25, 4.5, 6.25, 2.5, 0.4, "carcaca"),
        box("soprador_colar", [6.25, 5, 5.75], [6.5, 7.5, 8.75], "darkiron"),
        box("soprador_grade1", [4.4, 5.85, 5.2], [4.5, 6.15, 9.3], "darkiron"),
        box("soprador_grade2", [4.35, 3.95, 7.1], [4.45, 8.05, 7.4], "darkiron"),
        # Lenha esperando (canto sudoeste)
        box("lenha1", [0.5, 2, 10.75], [5.5, 3.5, 12.25], "logbark", faces={"east": "logend", "west": "logend"}),
        box("lenha2", [0.5, 2, 12.5], [5.5, 3.5, 14], "logbark", faces={"east": "logend", "west": "logend"}),
        box("lenha3", [0.5, 3.5, 11.6], [5.5, 5, 13.1], "logbark", faces={"east": "logend", "west": "logend"}),
        *terminal(8.75, 13, 4, "borne"),
        *lampada(9, 13, 10.5),
        box("musgo1", [0.5, 2, 0.5], [4, 2.2, 3.5], "moss"),
        box("musgo2", [12.25, 13, 9], [14.5, 13.15, 12], "moss"),
        *carv_motor,
    ]
    carv_vento = list(carv_eixo)
    carv_vento.append(box("ventoinha_cubo", [4.9, 5.35, 6.6], [5.8, 6.65, 7.9], "brass"))
    for i in range(4):
        carv_vento.append(box(f"pa{i}", [5.1, 5.7, 7.9], [5.6, 6.3, 9.25], "corroded",
                              {"x": 90 * i} if i else None, [5.35, 6, 7.25] if i else None))

    # =================================================================
    # COLMEIA ELÉTRICA — skep redondinho num banco, fumegador elétrico redondo soprando na porta,
    # centrífuga REDONDA (barril de aduelas de ferro com aros) e o motor em pé numa ponte em cima,
    # tocando o eixo dos quadros direto (acoplamento). Mel e cera saem na gaveta da frente.
    # =================================================================
    col_base = [
        box("viga1", [0.5, 0, 2.5], [15.5, 0.75, 3.75], "darkwood"),
        box("viga2", [0.5, 0, 12.25], [15.5, 0.75, 13.5], "darkwood"),
        box("estrado", [0.5, 0.75, 0.5], [15.5, 1.5, 15.5], "planks"),
        # Banquinho com o skep (camadas redondas de palha)
        box("banco_tampo", [0.75, 4, 1], [6.75, 4.75, 7], "darkwood"),
        box("banco_pe1", [1.25, 1.5, 1.5], [2, 4, 2.25], "darkwood"),
        box("banco_pe2", [5.5, 1.5, 1.5], [6.25, 4, 2.25], "mossy"),
        box("banco_pe3", [1.25, 1.5, 5.75], [2, 4, 6.5], "darkwood"),
        box("banco_pe4", [5.5, 1.5, 5.75], [6.25, 4, 6.5], "darkwood"),
        *disco_y("skep1", 3.75, 4, 4.75, 7.25, 2.75, "skep"),
        *disco_y("skep2", 3.75, 4, 7.25, 9, 2.25, "skep"),
        *disco_y("skep3", 3.75, 4, 9, 10.25, 1.6, "skep"),
        *disco_y("skep4", 3.75, 4, 10.25, 11, 0.85, "skep"),
        box("skep_porta", [3.25, 4.75, 6.75], [4.25, 5.5, 6.85], "coal"),
        # Fumegador redondo com bico apontando pra porta do skep
        *disco_y("fumeg", 3.5, 11.5, 1.5, 5.5, 1.4, "corroded"),
        *disco_y("fumeg_tampa", 3.5, 11.5, 5.5, 6, 1.55, "rebite"),
        box("fumeg_bico_base", [3.1, 6, 10.9], [3.9, 6.6, 11.7], "darkiron"),
        box("fumeg_bico", [3.15, 6.3, 9.3], [3.85, 6.9, 10.9], "darkiron", {"x": 25}, [3.5, 6.6, 10.9]),
        box("fumeg_janela", [3, 2.5, 12.9], [4, 3.5, 13], "ember"),
        box("fumeg_alca", [4.9, 3, 11.25], [5.4, 5, 11.75], "darkiron"),
        # Centrífuga redonda: aduelas de ferro, 2 aros, fundo
        *anel_y("centr", 11.5, 8, 1.5, 9, 3.4, 0.5, "carcaca"),
        *anel_y("centr_aro1", 11.5, 8, 3, 3.75, 3.6, 0.2, "rebite"),
        *anel_y("centr_aro2", 11.5, 8, 7, 7.75, 3.6, 0.2, "rebite"),
        *disco_y("centr_fundo", 11.5, 8, 1.5, 2.25, 2.85, "darkiron"),
        # Ponte por cima da centrífuga com o motor em pé
        box("ponte_pe_o", [7, 1.5, 7.4], [7.8, 11, 8.6], "darkiron"),
        box("ponte_pe_l", [15.15, 1.5, 7.4], [15.95, 11, 8.6], "darkiron"),
        box("ponte", [7, 11, 7.25], [15.95, 12.25, 8.75], "darkiron"),
        box("motor_flange", [10.25, 12.25, 6.75], [12.75, 12.75, 9.25], "darkiron"),
        box("motor_corpo", [10.4, 12.75, 6.9], [12.6, 16.25, 9.1], "carcaca"),
        box("motor_corpo2", [10, 12.81, 7.3], [13, 16.19, 8.7], "carcaca"),
        box("motor_bobina", [10.2, 13.75, 6.7], [12.8, 15.25, 9.3], "bobina"),
        box("motor_tampa", [10.6, 16.25, 7.1], [12.4, 16.75, 8.9], "rebite"),
        box("motor_aleta1", [10.9, 16.75, 7.75], [12.1, 17.25, 8.25], "corroded"),
        # Bica de mel e gaveta com pote e cera
        box("bica", [11, 2, 11.6], [12, 2.75, 12.75], "darkiron"),
        box("gaveta", [8.5, 1.5, 12.75], [15.5, 3.5, 15.5], "darkwood"),
        box("gaveta_puxador", [11.5, 2, 15.5], [12.5, 2.75, 15.9], "brass"),
        *disco_y("pote", 10.25, 14.1, 3.5, 5.5, 0.9, "fired"),
        box("pote_mel", [9.5, 5.5, 13.35], [11, 5.75, 14.85], "honeycomb"),
        box("cera1", [12.25, 3.5, 13.5], [14, 4.5, 15], "wax"),
        box("cera2", [12.75, 4.5, 13.9], [13.75, 5.1, 14.6], "wax"),
        *terminal(14, 12.25, 8, "borne"),
        *lampada(8.6, 12.25, 8),
        box("musgo1", [0.75, 1.5, 13.25], [4.75, 1.7, 15.25], "moss"),
    ]
    col_rotor = [
        box("rotor_eixo", [11.1, 2.25, 7.6], [11.9, 10.4, 8.4], "iron"),
        box("quadro1", [9, 3, 7.75], [14, 8, 8.25], "honeycomb"),
        box("quadro2", [11.25, 3.05, 5.5], [11.75, 7.95, 10.5], "honeycomb"),
        box("quadro_aro1", [9, 8, 7.7], [14, 8.4, 8.3], "darkwood"),
        box("quadro_aro2", [11.2, 8.4, 5.5], [11.8, 8.8, 10.5], "darkwood"),
    ]
    col_polia = [
        box("acoplamento", [10.9, 10.4, 7.4], [12.1, 11, 8.6], "corroded"),
        box("eixo_motor", [11.15, 10.95, 7.65], [11.85, 12.8, 8.35], "iron"),
    ]

    # =================================================================
    # DEFUMADOR ELÉTRICO — armário de tábua aberto na frente; dentro, carrossel REDONDO (aro de
    # ferro com 4 ganchos) girando sobre a grelha elétrica. Em cima do teto: engrenagem de coroa no
    # eixo do carrossel e o motor com o pinhão encostado nos dentes dela.
    # =================================================================
    def_motor, def_pinhao = motor_ok(2.5, 16.5, 8, comp=3.5, raio=1.25, eixo="x", nome="motor")
    def_base = [
        box("alicerce", [0, 0, 0], [16, 2, 16], "cobble"),
        box("alicerce_cinta", [-0.2, 0.6, -0.2], [16.2, 1.2, 16.2], "darkiron"),
        # Armário
        box("fundo", [1, 2, 1], [15, 12.75, 2], "planks"),
        box("lado_esq", [1, 2, 2], [2, 12.75, 13.5], "planks"),
        box("lado_dir", [14, 2, 2], [15, 12.75, 13.5], "planks"),
        box("poste_esq", [0.75, 2, 13.5], [2.25, 12.75, 15], "darkwood"),
        box("poste_dir", [13.75, 2, 13.5], [15.25, 12.75, 15], "mossy"),
        box("teto", [0.5, 12.75, 0.5], [15.5, 13.25, 15.5], "darkwood"),
        box("teto_chapa", [1, 13.25, 1], [15, 13.5, 15], "carcaca"),
        box("canto_ferro1", [0.6, 10.75, 13.35], [2.4, 11.75, 15.15], "rebite"),
        box("canto_ferro2", [13.6, 10.75, 13.35], [15.4, 11.75, 15.15], "rebite"),
        box("trilho_porta", [2.25, 12, 13.6], [13.75, 12.5, 14.1], "corroded"),
        box("soleira", [2.25, 2, 13.5], [13.75, 3.25, 14], "darkwood"),
        # Grelha elétrica: resistências em brasa sob a grade
        box("brasa_caixa", [2, 2, 2], [14, 3, 13.5], "darkiron"),
        box("brasa1", [3, 3, 3.5], [13, 3.3, 4.5], "ember"),
        box("brasa2", [3, 3, 6.5], [13, 3.3, 7.5], "ember"),
        box("brasa3", [3, 3, 9.5], [13, 3.3, 10.5], "ember"),
        box("grade_z", [7.8, 3.3, 3], [8.2, 3.6, 13], "darkiron"),
        box("grade_x1", [2.5, 3.6, 3], [13.5, 3.85, 3.4], "darkiron"),
        box("grade_x2", [2.5, 3.6, 12.6], [13.5, 3.85, 13], "darkiron"),
        # Respiro no teto e o pé do motor
        box("respiro", [11.5, 13.5, 11.5], [13.5, 14.75, 13.5], "corroded"),
        box("respiro_chapeu", [11.25, 14.75, 11.25], [13.75, 15.1, 13.75], "darkiron"),
        box("motor_suporte", [1, 13.5, 6.5], [4, 14.5, 9.5], "darkiron"),
        box("mancal_teto", [7, 13.5, 7], [9, 14, 9], "rebite"),
        # Gaveta puxada pra fora com os defumados
        box("gaveta", [4.5, 2, 14], [11.5, 3, 16], "darkwood"),
        box("gaveta_frente", [4.5, 3, 15.5], [11.5, 3.6, 16], "darkwood"),
        box("gaveta_carne", [5, 3, 14.25], [7.75, 3.6, 15.5], "smoked"),
        box("gaveta_peixe", [8.25, 3, 14.25], [11, 3.6, 15.5], "fishsmoked"),
        *terminal(13, 13.5, 3.5, "borne"),
        *lampada(3, 13.5, 12.5),
        box("musgo1", [9.5, 13.5, 1.25], [11.25, 13.65, 4], "moss"),
        *def_motor,
    ]
    def_carrossel = [
        box("eixo", [7.5, 3.85, 7.5], [8.5, 14.1, 8.5], "iron"),
        box("braco_x", [3, 11.25, 7.6], [13, 11.75, 8.4], "corroded"),
        box("braco_z", [7.6, 11.3, 3], [8.4, 11.7, 13], "corroded"),
        *anel_y("aro", 8, 8, 11.25, 11.75, 5.2, 0.25, "darkiron"),
        # Engrenagem de coroa em cima do teto (dentes pra cima, o pinhão do motor encosta neles)
        *disco_y("coroa", 8, 8, 14, 14.75, 2.5, "corroded"),
    ]
    for i in range(8):
        def_carrossel.append(box(f"coroa_dente{i}", [7.6, 14.75, 5.5], [8.4, 15.25, 6.3], "corroded",
                                 {"y": 45 * i} if i else None, [8, 14.75, 8] if i else None))
    for i, (x, z, t) in enumerate([(3.6, 8, "raw"), (12.4, 8, "raw"), (8, 3.6, "fishraw"), (8, 12.4, "fishraw")]):
        def_carrossel += [
            box(f"gancho{i}", [x - 0.2, 9.75, z - 0.2], [x + 0.2, 11.25, z + 0.2], "darkiron"),
            box(f"carne{i}", [x - 1, 6.5, z - 1], [x + 1, 9.75, z + 1], t),
        ]

    # =================================================================
    # VIGIA ELÉTRICO — poste de ferro; em cima, o holofote numa engrenagem de giro (dentes pra baixo)
    # tocada pelo pinhão do motor preso numa prateleira no poste. Do lado, o sino REDONDO no braço,
    # com o martelo elétrico (solenoide) encostado na saia do sino.
    # =================================================================
    vig_motor, vig_pinhao = motor_ok(2.75, 20.35, 8, comp=3, raio=1.25, eixo="x", nome="motor")
    vig_base = [
        box("alicerce", [1.5, 0, 1.5], [14.5, 3, 14.5], "cobble"),
        box("alicerce_cinta", [1.25, 1.5, 1.25], [14.75, 2.25, 14.75], "brick"),
        box("poste_pe", [5.5, 3, 5.5], [10.5, 5, 10.5], "darkiron"),
        box("poste", [6.5, 5, 6.5], [9.5, 22, 9.5], "carcaca"),
        box("poste_cinta1", [6.25, 8, 6.25], [9.75, 9, 9.75], "rebite"),
        box("poste_cinta2", [6.25, 12, 6.25], [9.75, 13, 9.75], "rebite"),
        box("escora_o", [3.5, 3, 7.5], [4.5, 12, 8.5], "darkwood", {"z": -18}, [4, 3, 8]),
        box("escora_s", [7.5, 3, 11.5], [8.5, 12, 12.5], "mossy", {"x": 18}, [8, 3, 12]),
        # Prateleira do motor
        box("prateleira", [1.25, 17.6, 6.75], [6.5, 18.35, 9.25], "darkiron"),
        box("prateleira_mao", [5.75, 15, 7.5], [6.5, 17.6, 8.5], "darkiron"),
        # Braço do sino + solenoide
        box("braco", [9.5, 20, 7.25], [14.5, 21.25, 8.75], "darkwood"),
        box("braco_mao", [9.5, 17, 7.5], [10.5, 20, 8.5], "darkwood", {"z": -35}, [10, 20, 8]),
        box("solenoide", [9.5, 15, 7], [10.3, 16.75, 9], "bobina"),
        box("solenoide_tampa", [9.5, 16.75, 7.25], [10.2, 17, 8.75], "darkiron"),
        box("solenoide_pino", [10.3, 15.6, 7.75], [10.45, 16.1, 8.25], "iron"),
        # Caixinha do registro
        box("caixa", [10.5, 3, 11], [14, 5.5, 14], "darkwood"),
        box("caixa_tampa", [10.25, 5.5, 10.75], [14.25, 6, 14.25], "rebite"),
        box("caixa_trava", [11.75, 4, 14], [12.75, 5, 14.3], "brass"),
        *terminal(3.5, 3, 10, "borne"),
        *lampada(3.5, 3, 13),
        box("musgo1", [1.75, 3, 1.75], [5.25, 3.2, 4], "moss"),
        *vig_motor,
    ]
    vig_sino = [
        box("sino_alca", [12, 19.25, 7.5], [13, 20, 8.5], "darkiron"),
        *disco_y("sino_topo", 12.5, 8, 18.5, 19.25, 1.25, "bronze"),
        *disco_y("sino_meio", 12.5, 8, 16.5, 18.5, 1.75, "bronze"),
        *disco_y("sino_baixo", 12.5, 8, 14.75, 16.5, 2.05, "bronze"),
        *anel_y("sino_boca", 12.5, 8, 14.25, 14.75, 2.4, 0.45, "bronze"),
        box("sino_badalo", [12.15, 13.4, 7.65], [12.85, 14.75, 8.35], "iron"),
    ]
    vig_holofote = [
        *disco_y("holo_giro", 8, 8, 22, 22.75, 2.5, "darkiron"),
        box("holo_garfo_o", [5.75, 22.75, 7.25], [6.5, 26, 8.75], "darkiron"),
        box("holo_garfo_l", [9.5, 22.75, 7.25], [10.25, 26, 8.75], "darkiron"),
        box("holo_corpo", [6.5, 23.25, 5], [9.5, 26.75, 10.5], "carcaca"),
        box("holo_aro", [6.25, 23, 10.5], [9.75, 27, 10.9], "brass"),
        box("holo_lente", [6.6, 23.4, 10.9], [9.4, 26.6, 11.05], "luz"),
        box("holo_tampa", [6.75, 26.75, 5.5], [9.25, 27.25, 9.5], "rebite"),
        box("holo_aleta1", [6.9, 27.25, 6], [9.1, 27.75, 6.5], "corroded"),
        box("holo_aleta2", [6.9, 27.25, 8], [9.1, 27.75, 8.5], "corroded"),
    ]
    for i in range(8):
        vig_holofote.append(box(f"giro_dente{i}", [7.6, 21.6, 5.5], [8.4, 22, 6.3], "darkiron",
                                {"y": 45 * i} if i else None, [8, 22, 8] if i else None))

    # =================================================================
    # ESTUFA DE COGUMELOS — tora com cogumelos redondinhos sobre pedras; atrás, barril d'água redondo
    # e a bomba (motor -> carcaça redonda); o cano sobe, passa por cima e desce no aspersor que gira
    # sobre a tora. Bandeja com a colheita na frente.
    # =================================================================
    cog_motor, cog_eixo = motor_ok(10.75, 2.5, 2.5, comp=3.5, raio=1.5, eixo="x", nome="motor", sem_polia=True)
    cog_base = [
        box("pedra1", [2, 0, 5.5], [5, 2, 10.5], "cobble"),
        box("pedra2", [11, 0, 5.5], [14, 2, 10.5], "cobble"),
        box("tora", [1, 2, 5.75], [15, 7, 10.25], "bark", faces={"east": "logend", "west": "logend"}),
        box("tora_musgo", [9.5, 7, 8.75], [13.5, 7.2, 10.1], "moss"),
        box("tora_musgo_lado", [10, 4, 10.25], [14, 6.5, 10.45], "moss"),
        # Cogumelos (chapéu redondo)
        box("cog1_pe", [3.75, 7, 7.25], [4.75, 8.75, 8.25], "stipefield"),
        *disco_y("cog1_chapeu", 4.25, 7.75, 8.75, 9.5, 1.6, "capfield"),
        *disco_y("cog1_topo", 4.25, 7.75, 9.5, 9.9, 1.0, "capfield"),
        box("cog2_pe", [8.1, 7, 7.6], [8.9, 9.25, 8.4], "flyagaricstipe"),
        *disco_y("cog2_chapeu", 8.5, 8, 9.25, 10.25, 2.0, "flyagaric"),
        *disco_y("cog2_topo", 8.5, 8, 10.25, 10.75, 1.3, "flyagaric"),
        box("cog3_pe", [12, 7, 7], [12.75, 8.25, 7.75], "stipebolete"),
        *disco_y("cog3_chapeu", 12.375, 7.375, 8.25, 9, 1.25, "capbolete"),
        *disco_y("cog3_topo", 12.375, 7.375, 9, 9.35, 0.75, "capbolete"),
        box("orelha1", [6, 4, 10.25], [8.5, 4.5, 11.75], "shelf"),
        box("orelha2", [6.5, 5.25, 10.25], [8, 5.75, 11.25], "shelf"),
        # Barril d'água redondo
        *anel_y("barril", 3.25, 2.6, 0, 7.5, 2.2, 0.5, "barril"),
        *anel_y("barril_aro1", 3.25, 2.6, 1.5, 2, 2.35, 0.15, "darkiron"),
        *anel_y("barril_aro2", 3.25, 2.6, 5.5, 6, 2.35, 0.15, "darkiron"),
        *disco_y("barril_fundo", 3.25, 2.6, 0, 0.5, 1.65, "darkwood"),
        *disco_y("barril_agua", 3.25, 2.6, 6.75, 6.85, 1.65, "water"),
        # Bomba: base do motor, carcaça redonda da bomba, canos
        box("motor_base", [9.25, 0, 1.15], [12.25, 0.25, 3.85], "darkiron"),
        box("bomba_flange", [13.05, 1.25, 1.25], [13.25, 3.75, 3.75], "corroded"),
        *disco_x("bomba", 2.5, 2.5, 13.25, 14.75, 1.75, "carcaca"),
        box("bomba_pe", [13.5, 0, 1.5], [14.5, 0.75, 3.5], "darkiron"),
        box("cano_entrada", [4.5, 0.5, 0.1], [13.5, 1.25, 0.85], "darkiron"),
        box("cano_sobe", [13.65, 4.25, 2.1], [14.35, 13.25, 2.9], "darkiron"),
        box("cano_x", [8.4, 12.5, 2.1], [13.65, 13.25, 2.9], "darkiron"),
        box("cano_z", [7.6, 12.5, 2.1], [8.4, 13.25, 8.4], "darkiron"),
        box("cano_desce", [7.7, 11.75, 7.7], [8.3, 12.5, 8.3], "darkiron"),
        box("cano_apoio", [7.5, 0, 2.1], [8.5, 12.5, 2.9], "darkwood"),
        box("cano_abraco", [7.4, 9, 2], [8.6, 9.5, 3], "darkiron"),
        # Bandeja de colheita na frente
        box("bandeja", [3, 0, 12], [13, 1, 15.5], "darkwood"),
        box("bandeja_s", [3, 1, 15], [13, 2, 15.5], "darkwood"),
        box("bandeja_n", [3.5, 1, 12], [12.5, 1.5, 12.5], "darkwood"),
        box("bandeja_o", [3, 1, 12], [3.5, 2, 15], "darkwood"),
        box("bandeja_l", [12.5, 1, 12], [13, 2, 15], "darkwood"),
        box("colhido1_pe", [4.75, 1, 13.5], [5.25, 1.75, 14], "stipefield"),
        *disco_y("colhido1", 5, 13.75, 1.75, 2.4, 0.9, "capfield"),
        box("colhido2_pe", [8.25, 1, 13.5], [8.75, 1.6, 14], "stipebolete"),
        *disco_y("colhido2", 8.5, 13.75, 1.6, 2.2, 0.85, "capbolete"),
        box("colhido3", [10.25, 1, 13], [11.75, 1.8, 14.5], "chanterelle"),
        # Postinho da lâmpada e antena
        box("poste_lamp", [13.75, 0, 11.25], [15.25, 3, 12.75], "darkwood"),
        *lampada(14.5, 3, 12),
        *terminal(14.5, 0, 14.25, "borne"),
        *cog_motor,
    ]
    cog_aspersor = [
        box("asp_cubo", [7.4, 11, 7.4], [8.6, 11.75, 8.6], "brass"),
        box("asp_braco1", [5, 11.15, 7.75], [11, 11.6, 8.25], "darkiron"),
        box("asp_braco2", [7.75, 11.2, 5], [8.25, 11.55, 11], "darkiron"),
        box("asp_bico1", [4.6, 10.9, 7.6], [5, 11.6, 8.4], "cobre"),
        box("asp_bico2", [11, 10.9, 7.6], [11.4, 11.6, 8.4], "cobre"),
        box("asp_bico3", [7.6, 10.9, 4.6], [8.4, 11.6, 5], "cobre"),
        box("asp_bico4", [7.6, 10.9, 11], [8.4, 11.6, 11.4], "cobre"),
    ]
    cog_polia = cog_eixo

    MODOS = [["parado", "Sem energia"], ["ligado", "Ligado"]]
    return {
        "auto_carvoeira": {
            "title": "Carvoeira Elétrica",
            "parts": {
                "base": {"label": "Forno (parado)", "elements": carv_base},
                "ventoinha": {"label": "Ventoinha do soprador (gira)", "elements": carv_vento},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Versão elétrica do Carvoeiro: bota lenha (ou toras) e ela vira carvão sozinha, sem montar poço de carvão. As resistências ficam em brasa atrás da janelinha gradeada, o soprador do lado (motor + ventoinha numa carcaça redonda) sopra ar direto no forno, a fumaça sai pela chaminé e o carvão cai na gaveta de baixo. Gasta MUITA energia (esquentar é caro). Receita: barro, pedras, cobre e engrenagem enferrujada.",
                "pivots": {"ventoinha": [5.35, 6, 7.25]},
                "modes": MODOS,
                "anim": [{"part": "ventoinha", "spin": "x", "speed": 9}],
                "glowTex": ["luz", "ember"],
                "fx": {"ligado": [{"type": "smoke", "at": [13, 18.5, 4.5], "top": 2.2}, {"type": "sparks", "at": [11, 8, 14.2], "rate": 0.05}]},
                "light": {"at": [11, 8, 15.5], "color": 0xff7a30, "intensity": 0.9},
                "cam": {"pos": [2.3, 1.6, 3.0], "target": [0.5, 0.5, 0.5]},
            },
        },
        "auto_colmeia": {
            "title": "Colmeia Elétrica",
            "parts": {
                "base": {"label": "Colmeia + centrífuga (parada)", "elements": col_base},
                "rotor": {"label": "Quadros da centrífuga (giram)", "elements": col_rotor},
                "polia": {"label": "Eixo do motor (gira)", "elements": col_polia},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Versão elétrica do Apicultor: o fumegador elétrico acalma as abelhas, a máquina tira os favos das colmeias e skeps da área (sem picada!) e a centrífuga redonda gira os quadros — o motor em pé em cima da ponte toca o eixo direto — separando o mel da cera. Mel e cera saem na gaveta da frente. Gasta pouca energia. Receita: tábuas, ferro, cobre e engrenagem enferrujada.",
                "pivots": {"rotor": [11.5, 0, 8], "polia": [11.5, 0, 8]},
                "modes": MODOS,
                "anim": [{"part": "rotor", "spin": "y", "speed": 7}, {"part": "polia", "spin": "y", "speed": 7}],
                "glowTex": ["luz", "ember"],
                "fx": {"ligado": [{"type": "smoke", "at": [3.5, 7.2, 9.2], "top": 0.9}]},
                "cam": {"pos": [2.4, 1.6, 2.9], "target": [0.5, 0.45, 0.5]},
            },
        },
        "auto_defumador": {
            "title": "Defumador Elétrico",
            "parts": {
                "base": {"label": "Armário (parado)", "elements": def_base},
                "carrossel": {"label": "Carrossel redondo + coroa (gira)", "elements": def_carrossel},
                "polia": {"label": "Pinhão do motor (gira)", "elements": def_pinhao},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Versão elétrica do Defumador: pendura carne e peixe nos ganchos do carrossel redondo, a grelha elétrica esquenta e solta a fumaça, e o carrossel vai girando pra defumar tudo por igual — em cima do teto o pinhão do motor toca a engrenagem de coroa do eixo. Pronto, cai na gaveta da frente. Dura bem mais pra estragar. Gasta energia média. Receita: tábuas, pedras, cobre e engrenagem enferrujada.",
                "pivots": {"carrossel": [8, 0, 8], "polia": [2.5, 16.5, 8]},
                "modes": MODOS,
                "anim": [{"part": "carrossel", "spin": "y", "speed": 0.8}, {"part": "polia", "spin": "x", "speed": 3.2}],
                "glowTex": ["luz", "ember"],
                "fx": {"ligado": [{"type": "smoke", "at": [8, 4, 8], "top": 0.85}, {"type": "smoke", "at": [12.5, 15.2, 12.5], "top": 1.8}]},
                "light": {"at": [8, 4, 8], "color": 0xff7a30, "intensity": 0.9},
                "cam": {"pos": [2.3, 1.6, 3.1], "target": [0.5, 0.5, 0.5]},
            },
        },
        "auto_vigia": {
            "title": "Vigia Elétrico",
            "parts": {
                "base": {"label": "Torre (parada)", "elements": vig_base},
                "holofote": {"label": "Holofote na engrenagem de giro", "elements": vig_holofote},
                "sino": {"label": "Sino (balança)", "elements": vig_sino},
                "polia": {"label": "Pinhão do motor (gira)", "elements": vig_pinhao},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Versão elétrica do Vigia: o pinhão do motor gira a engrenagem do holofote, que varre a área de noite. Quando chega drifter, lobo, urso ou outro bicho bravo, o martelo elétrico bate no sino redondo sem parar e avisa no chat de onde veio (raio configurável). O registro do que viu fica na caixinha. Gasta pouca energia (só o holofote; o sino é rapidinho). Receita: cobre, ferro, tábuas e engrenagem enferrujada.",
                "pivots": {"holofote": [8, 22, 8], "sino": [12.5, 20, 8], "polia": [2.75, 20.35, 8]},
                "modes": [["parado", "Sem energia"], ["ligado", "Vigiando"], ["alerta", "Alerta!"]],
                "default": "alerta",
                "anim": [
                    {"part": "holofote", "spin": "y", "speed": 0.9},
                    {"part": "sino", "swing": "x", "amp": 0.5, "freq": 0.9, "when": ["alerta"]},
                    {"part": "polia", "spin": "x", "speed": -1.8},
                ],
                "glow": ["ligado", "alerta"],
                "light": {"at": [8, 25, 13], "color": 0xfff0b0, "intensity": 1.2, "when": ["ligado", "alerta"]},
                "cam": {"pos": [2.6, 2.3, 3.6], "target": [0.5, 1.0, 0.5]},
            },
        },
        "auto_cogumelos": {
            "title": "Estufa de Cogumelos",
            "parts": {
                "base": {"label": "Tora + barril d'água (parada)", "elements": cog_base},
                "aspersor": {"label": "Aspersor (gira)", "elements": cog_aspersor},
                "polia": {"label": "Eixo da bomba (gira)", "elements": cog_polia},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Versão elétrica do Cogumeleiro: o motor toca a bomba, que puxa água do barril, sobe pelo cano e o aspersor gira soltando névoa nos troncos de cogumelo da área — nascem mais rápido e mesmo fora da sombra. Colhe sozinha e põe na bandeja da frente (ignora os venenosos se você quiser). Gasta pouca energia. Receita: tora, barril, cobre e engrenagem enferrujada.",
                "pivots": {"aspersor": [8, 11.375, 8], "polia": [10.75, 2.5, 2.5]},
                "modes": MODOS,
                "anim": [{"part": "aspersor", "spin": "y", "speed": 3}, {"part": "polia", "spin": "x", "speed": 8}],
                "fx": {"ligado": [{"type": "smoke", "at": [8, 10.8, 8], "top": 0.85, "rate": 0.6}]},
                "cam": {"pos": [2.3, 1.5, 2.9], "target": [0.5, 0.35, 0.5]},
            },
        },
    }
