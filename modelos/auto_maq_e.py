"""
AUTOMAÇÃO — máquinas (grupo E): Iluminação Elétrica, Bomba d'Água/Irrigador, Geladeira e Elevador.
Energia sem fio (alcance do Poste de Energia); o borne do kit é a antena que recebe.

Regras: coerência mecânica (redondo engata em redondo, correia de polia a polia, eixo no centro),
nada sobreposto (checa_sobreposto.py) e nada flutuando (checa_flutuando.py).
"""
import math

TEX = {
    "gelo": "game:block/liquid/ice/lake1",
    "escarcha": "game:block/liquid/ice/glacier1",
    "luzquente": "game:block/glass/yellow",
    "lanterna": "game:block/metal/lantern/rust",
}


# ---------------------------------------------------------------------------------------------
# Peças redondas "de bloco": miolo quadrado + 4 abas (oitavado), sem faces sobrepostas
# ---------------------------------------------------------------------------------------------
def cil(box, nome, c, r, a0, a1, tex, eixo="y", faces=None):
    """Cilindro no eixo dado. c = centro (a coordenada do eixo é ignorada); vai de a0 até a1 no eixo."""
    a, s = r * 0.7071, r * 0.4142
    out = []
    for suf, u0, u1, v0, v1 in (("", -a, a, -a, a), ("_l", a, r, -s, s), ("_o", -r, -a, -s, s),
                                ("_s", -s, s, a, r), ("_n", -s, s, -r, -a)):
        if eixo == "y":
            f, t = [c[0] + u0, a0, c[2] + v0], [c[0] + u1, a1, c[2] + v1]
        elif eixo == "x":
            f, t = [a0, c[1] + u0, c[2] + v0], [a1, c[1] + u1, c[2] + v1]
        else:
            f, t = [c[0] + u0, c[1] + v0, a0], [c[0] + u1, c[1] + v1, a1]
        out.append(box(nome + suf, f, t, tex, faces=faces))
    return out


def cinta(box, nome, c, r, d, a0, a1, tex, eixo="y"):
    """Cinta/anel abraçando um cil() de raio r (mesmo miolo, d mais grossa pra fora): encaixe limpo."""
    a, s = r * 0.7071, r * 0.4142
    out = []
    e = 0.02  # as abas começam um tiquinho dentro do miolo e são um tiquinho mais finas: sem face dupla
    for suf, u0, u1, v0, v1 in (("", -a - d, a + d, -a - d, a + d), ("_l", a - e, r + d, -s - d, s + d),
                                ("_o", -r - d, -a + e, -s - d, s + d), ("_s", -s - d, s + d, a - e, r + d),
                                ("_n", -s - d, s + d, -r - d, -a + e)):
        b0, b1 = (a0 + 0.03, a1 - 0.03) if suf else (a0, a1)
        if eixo == "y":
            f, t = [c[0] + u0, b0, c[2] + v0], [c[0] + u1, b1, c[2] + v1]
        elif eixo == "x":
            f, t = [b0, c[1] + u0, c[2] + v0], [b1, c[1] + u1, c[2] + v1]
        else:
            f, t = [c[0] + u0, c[1] + v0, b0], [c[0] + u1, c[1] + v1, b1]
        out.append(box(nome + suf, f, t, tex))
    return out


def aro(box, nome, c, r, esp, a0, a1, tex, eixo="y", n=8):
    """Anel oco (aduelas giradas em volta do centro); r = raio de fora, esp = grossura."""
    L = 2 * r * math.tan(math.pi / n) + 0.02
    out = []
    for i in range(n):
        ang = 360 / n * i + 180 / n
        if eixo == "y":
            f, t, o = [c[0] - L / 2, a0, c[2] - r], [c[0] + L / 2, a1, c[2] - r + esp], [c[0], a0, c[2]]
        elif eixo == "x":
            f, t, o = [a0, c[1] - r, c[2] - L / 2], [a1, c[1] - r + esp, c[2] + L / 2], [a0, c[1], c[2]]
        else:
            f, t, o = [c[0] - L / 2, c[1] - r, a0], [c[0] + L / 2, c[1] - r + esp, a1], [c[0], c[1], a0]
        out.append(box(f"{nome}{i}", f, t, tex, {eixo: round(ang, 3)}, o))
    return out


def raios(box, nome, c, r, larg, a0, a1, tex, eixo="y", n=4):
    """Raios/pás saindo do centro (todos girados, n pares cruzados)."""
    out = []
    for i in range(n):
        ang = 180 / n * i + 90 / n
        d = 0.03 * i  # cada par numa espessura um tiquinho diferente: sem face no mesmo plano
        if eixo == "y":
            f, t, o = [c[0] - r, a0 + d, c[2] - larg / 2], [c[0] + r, a1 - d, c[2] + larg / 2], [c[0], a0, c[2]]
        elif eixo == "x":
            f, t, o = [a0 + d, c[1] - r, c[2] - larg / 2], [a1 - d, c[1] + r, c[2] + larg / 2], [a0, c[1], c[2]]
        else:
            f, t, o = [c[0] - r, c[1] - larg / 2, a0 + d], [c[0] + r, c[1] + larg / 2, a1 - d], [c[0], c[1], a0]
        out.append(box(f"{nome}{i}", f, t, tex, {eixo: round(ang, 3)}, o))
    return out


def motor_kit(k, *a, **kw):
    """Motor do kit sem a face da cruz no mesmo plano (corpo2 um tiquinho mais curto no eixo)."""
    caixa, gira = k.motor(*a, **kw)
    eixo = kw.get("eixo", "x")
    i = 0 if eixo == "x" else 2
    for e in caixa:
        if e["name"].endswith("_corpo2"):
            e["from"][i] += 0.06
            e["to"][i] -= 0.06
    return caixa, gira


def modelos(k):
    box, terminal, lampada = k.box, k.terminal, k.lampada

    # =================================================================
    # ILUMINAÇÃO ELÉTRICA — poste de rua de ferro fundido: pé de pedra, base oitavada, coluna
    # redonda com anéis, braço com mão-francesa e lanterna pendurada (2 blocos)
    # =================================================================
    luz_base = [
        box("pe", [2.5, 0, 2.5], [13.5, 2, 13.5], "cobble"),
        box("pe_cinta", [2.25, 0.5, 2.25], [13.75, 1.25, 13.75], "darkiron"),
        *cil(box, "base", [8, 0, 8], 2.75, 2, 4.75, "carcaca"),
        *cil(box, "base_tampa", [8, 0, 8], 2.25, 4.75, 5.5, "rebite"),
        *cil(box, "haste", [8, 0, 8], 1, 5.5, 26.5, "carcaca"),
        *cil(box, "anel1", [8, 0, 8], 1.45, 9.5, 10.25, "darkiron"),
        *cil(box, "anel2", [8, 0, 8], 1.45, 17.5, 18.25, "darkiron"),
        *cil(box, "remate", [8, 0, 8], 1.45, 26.5, 27.25, "rebite"),
        *cil(box, "ponta", [8, 0, 8], 0.6, 27.25, 28.5, "corroded"),
        box("ferrugem", [8.75, 12, 7.6], [9.05, 15, 8.4], "corroded"),
        # Braço pro sul + mão-francesa (sai da coluna e encosta no braço)
        box("braco", [7.25, 24.5, 9], [8.75, 25.75, 14.25], "darkiron"),
        box("braco_ponta", [7, 24.25, 14.25], [9, 26, 14.75], "rebite"),
        box("mao_francesa", [7.5, 23.3, 8.75], [8.5, 25.2, 9.6], "corroded", {"x": 40}, [8, 23.3, 9.1]),
        # Gancho e lanterna pendurada
        box("pendural", [7.6, 23.25, 12.25], [8.4, 24.5, 13.05], "iron"),
        box("chapeu_topo", [6.5, 22.75, 10.75], [9.5, 23.25, 14.5], "rebite"),
        box("chapeu", [5.25, 22.25, 9.75], [10.75, 22.75, 15.5], "darkiron"),
        box("lum_canto1", [5.75, 17.75, 10.25], [6.25, 22.25, 10.75], "lanterna"),
        box("lum_canto2", [9.75, 17.75, 10.25], [10.25, 22.25, 10.75], "lanterna"),
        box("lum_canto3", [5.75, 17.75, 14.5], [6.25, 22.25, 15], "lanterna"),
        box("lum_canto4", [9.75, 17.75, 14.5], [10.25, 22.25, 15], "lanterna"),
        box("lum_fundo", [5.5, 17.25, 10], [10.5, 17.75, 15.25], "darkiron"),
        box("lum_vidro", [6.25, 17.75, 10.75], [9.75, 22.25, 14.5], "luzquente"),
        box("lum_ponta", [7.5, 16.5, 12.25], [8.5, 17.25, 13.25], "brass"),
        *terminal(3.75, 2, 3.75, "antena"),
        *lampada(12.25, 2, 3.75),
        box("musgo", [3, 2, 10.5], [6, 2.15, 13], "moss"),
        box("musgo2", [10.75, 2, 11.5], [13, 2.12, 13.25], "moss"),
    ]

    # =================================================================
    # BOMBA D'ÁGUA E IRRIGADOR — "cavalo de pau": o motor gira a caixa de engrenagens, que balança
    # o balancim; o balancim puxa o pistão do cilindro (que tira água do rio pelo cano) e a água
    # sobe pelo cano até o aspersor, que gira molhando a horta
    # =================================================================
    b_m, b_g = motor_kit(k, 5, 5.75, 2, comp=3, raio=1.5, eixo="z", nome="motor")
    bomba_base = [
        box("alicerce", [1, 0, 1], [15, 3, 15], "cobble"),
        box("borda", [0.5, 2.75, 0.5], [15.5, 3.5, 15.5], "brick"),
        box("cinta", [0.75, 1, 0.75], [15.25, 1.75, 15.25], "darkiron"),
        # Cilindro redondo da bomba (lado leste, perto da água)
        *cil(box, "cilindro", [12, 0, 8], 2.5, 3.5, 12, "carcaca"),
        *cinta(box, "cilindro_cinta1", [12, 0, 8], 2.5, 0.25, 6, 6.75, "darkiron"),
        *cinta(box, "cilindro_cinta2", [12, 0, 8], 2.5, 0.25, 10, 10.75, "darkiron"),
        *cil(box, "cilindro_tampa", [12, 0, 8], 3, 12, 12.75, "rebite"),
        # Cano que desce no rio
        box("cano_rio", [14.5, 4, 7.25], [18, 5.5, 8.75], "darkiron"),
        box("cano_rio_desce", [16.5, 0.5, 7.25], [18, 4, 8.75], "darkiron"),
        box("cano_rio_boca", [16.25, 0, 7], [18.25, 0.5, 9], "corroded"),
        # Guias do pistão (a cruzeta corre entre elas)
        box("guia_a", [10, 12.75, 7.6], [10.75, 19, 8.4], "iron"),
        box("guia_b", [13.25, 12.75, 7.6], [14, 19, 8.4], "iron"),
        box("guia_topo", [10, 19, 7.5], [14, 19.75, 8.5], "darkiron"),
        # Poste do balancim
        box("poste", [7.25, 3.5, 7.25], [8.75, 20.5, 8.75], "darkwood"),
        box("poste_cinta", [7, 10, 7], [9, 10.75, 9], "darkiron"),
        box("mancal_balancim", [7, 20.5, 7.1], [9, 21, 8.9], "darkiron"),
        # Caixa de engrenagens (o motor entra nela pelo lado norte) e a biela sai por cima
        box("caixa_eng", [3, 3.5, 6], [7, 9, 10], "carcaca"),
        box("caixa_eng_tampa", [2.75, 9, 5.75], [7.25, 9.5, 10.25], "rebite"),
        box("caixa_eng_vista", [3.25, 4, 10], [6.75, 8.5, 10.15], "engrenagens"),
        *b_m,
        # Cano até o aspersor (sai pelo sul do cilindro, vai pro oeste e sobe no canto sudoeste)
        box("cano_saida", [11.25, 4, 10.5], [12.75, 5.5, 12], "darkiron"),
        box("cano_horiz", [4.5, 4, 12], [12.75, 5.5, 13.5], "darkiron"),
        box("cano_sobe", [3, 3.5, 12], [4.5, 22, 13.5], "darkiron"),
        box("cano_cinta1", [2.75, 9, 11.75], [4.75, 9.75, 13.75], "corroded"),
        box("cano_cinta2", [2.75, 16, 11.75], [4.75, 16.75, 13.75], "corroded"),
        box("valvula", [2.25, 6.5, 12.25], [3, 8.5, 13.25], "brass"),
        *cil(box, "valvula_volante", [0, 7.5, 12.75], 1.4, 1.75, 2.25, "corroded", eixo="x"),
        *terminal(14, 3.5, 13.75, "antena"),
        *lampada(10, 3.5, 2.75),
        box("musgo1", [1.25, 3.5, 13.75], [2.75, 3.65, 15.25], "moss"),
        box("musgo2", [9, 3.5, 13.75], [12, 3.65, 15], "moss"),
    ]
    # Eixo do motor girando dentro do acoplamento (a polia do kit vira o acoplamento na caixa)
    bomba_motor = list(b_g)
    bomba_balancim = [
        box("balancim", [3.75, 21, 7.4], [13, 22, 8.6], "darkwood"),
        box("balancim_cinta", [7.5, 20.85, 7.25], [8.5, 22.15, 8.75], "darkiron"),
        box("biela", [4.6, 9.5, 7.6], [5.4, 21, 8.4], "iron"),
        box("biela_olhal", [4.35, 20.4, 7.5], [5.65, 20.9, 8.5], "corroded"),
    ]
    bomba_pistao = [
        box("pistao_haste", [11.6, 12.75, 7.65], [12.4, 21, 8.35], "iron"),
        box("pistao_cruzeta", [10.75, 15, 7.55], [13.25, 16, 8.45], "corroded"),
    ]
    bomba_aspersor = [
        *cil(box, "asp_eixo", [3.75, 0, 12.75], 0.5, 22, 23.5, "brass"),
        *cil(box, "asp_cubo", [3.75, 0, 12.75], 1, 23.5, 24.5, "cobre"),
        box("asp_braco_a", [-1, 23.75, 12.5], [8.5, 24.25, 13], "cobre"),
        box("asp_bico_a", [-1.5, 22.75, 12.25], [-0.5, 23.75, 13.25], "brass"),
        box("asp_bico_b", [8, 22.75, 12.25], [9, 23.75, 13.25], "brass"),
        box("gota1", [-1.25, 22, 12.5], [-0.75, 22.75, 13], "water"),
        box("gota2", [8.25, 22, 12.5], [8.75, 22.75, 13], "water"),
    ]

    # =================================================================
    # GELADEIRA — geladeira antiga "de motor em cima": armário de tábua forrado de chapa com
    # cantoneiras, 2 portas (congelador e geladeira) vedadas com couro, serpentina de cobre atrás
    # e, em cima, o motor girando a ventoinha da caixa redonda do compressor
    # =================================================================
    g_m, g_g = motor_kit(k, 4.5, 17.5, 8, comp=3, raio=1.25, eixo="x", nome="motor")
    gel_base = [
        *[box(f"pe{i}", [x, 0, z], [x + 1.5, 1.5, z + 1.5], "darkwood")
          for i, (x, z) in enumerate([(2, 3), (12.5, 3), (2, 11.5), (12.5, 11.5)])],
        box("corpo", [2, 1.5, 3], [14, 15, 13], "planks"),
        box("forro_cima", [1.75, 15, 2.75], [14.25, 15.75, 13.25], "darkiron"),
        # Cantoneiras de ferro nas quinas de trás
        box("cant_no_o", [1.75, 1.5, 3], [2, 15, 4], "rebite"),
        box("cant_no_n", [2, 1.5, 2.75], [3, 15, 3], "rebite"),
        box("cant_no_q", [1.75, 1.5, 2.75], [2, 15, 3], "rebite"),
        box("cant_ne_l", [14, 1.5, 3], [14.25, 15, 4], "rebite"),
        box("cant_ne_n", [13, 1.5, 2.75], [14, 15, 3], "rebite"),
        box("cant_ne_q", [14, 1.5, 2.75], [14.25, 15, 3], "rebite"),
        box("cant_so", [1.75, 1.5, 12], [2, 15, 13], "rebite"),
        box("cant_se", [14, 1.5, 12], [14.25, 15, 13], "rebite"),
        # Cintas de ferro nos lados e atrás (entre as cantoneiras)
        *[box(f"cinta_o{i}", [1.8, y, 4], [2, y + 0.75, 12], "darkiron") for i, y in enumerate([4.5, 11])],
        *[box(f"cinta_l{i}", [14, y, 4], [14.2, y + 0.75, 12], "darkiron") for i, y in enumerate([4.5, 11])],
        *[box(f"cinta_n{i}", [3, y, 2.8], [13, y + 0.75, 3], "darkiron") for i, y in enumerate([4.5, 11])],
        # Vedação de couro + 2 portas (congelador em cima, geladeira embaixo)
        box("vedacao", [2.25, 1.75, 13], [13.75, 14.75, 13.2], "leather"),
        box("porta", [2.5, 2, 13.2], [13.5, 10.5, 14.5], "darkwood"),
        box("porta_chapa", [3, 2.5, 14.5], [13, 10, 14.75], "carcaca"),
        box("porta_cima", [2.5, 10.75, 13.2], [13.5, 14.5, 14.5], "darkwood"),
        box("porta_cima_chapa", [3, 11.25, 14.5], [13, 14, 14.75], "carcaca"),
        # Dobradiças (lado oeste) e trincos de latão (lado leste)
        *[box(f"dobradica{i}", [2.1, y, 13.4], [2.6, y + 1.5, 14.9], "darkiron") for i, y in enumerate([3, 8, 11.5])],
        box("trinco", [11.25, 5, 14.75], [12, 8, 15.25], "brass"),
        box("trinco_alavanca", [10.75, 7.5, 15.25], [12.5, 8.25, 15.75], "corroded"),
        box("trinco_cima", [11.25, 11.75, 14.75], [12, 13.5, 15.25], "brass"),
        # Escarcha nas portas e no compressor (só ligada)
        box("escarcha1", [3.5, 12.25, 14.75], [9, 13.75, 14.85], "escarcha"),
        box("escarcha2", [3.25, 2.75, 14.75], [6, 6, 14.85], "escarcha"),
        box("gelinho", [6, 15.75, 3.25], [9, 15.85, 5.5], "gelo"),
        # Caixa redonda do compressor em cima (motor gira a ventoinha dela)
        *cil(box, "compressor", [10.5, 0, 8], 3.5, 15.75, 19, "carcaca"),
        *cinta(box, "comp_anel1", [10.5, 0, 8], 3.5, 0.25, 16, 16.5, "bobina"),
        *cinta(box, "comp_anel2", [10.5, 0, 8], 3.5, 0.25, 18.25, 18.75, "bobina"),
        *aro(box, "comp_borda", [10.5, 0, 8], 3.5, 0.4, 19, 19.75, "rebite"),
        *cil(box, "vent_cubo_base", [10.5, 0, 8], 0.9, 19, 19.25, "darkiron"),
        *g_m,
        box("motor_acopla", [6.5, 17, 7.5], [7.5, 18, 8.5], "iron"),
        # Serpentina de cobre atrás (zigue-zague) presa com grampos
        *[box(f"serp_h{i}", [3.5, 3 + i * 3, 1.75], [11.5, 3.75 + i * 3, 2.5], "cobre") for i in range(4)],
        *[box(f"serp_v{i}", [3.55 if i % 2 else 10.8, 3.05 + i * 3, 1.85], [4.2 if i % 2 else 11.45, 6.7 + i * 3, 2.4], "cobre")
          for i in range(3)],
        *[box(f"serp_grampo{i}", [7, 3.1 + i * 3, 2.5], [7.75, 3.65 + i * 3, 3], "darkiron") for i in range(4)],
        box("serp_gelo", [5, 6, 1.65], [8, 6.75, 1.75], "escarcha"),
        *terminal(3.5, 15.75, 4.25, "antena"),
        *lampada(3.5, 15.75, 11.75),
        box("musgo", [11, 15.75, 11.6], [13.75, 15.9, 13], "moss"),
    ]
    # Ventoinha em cima do compressor (gira em volta do eixo vertical)
    gel_vent = [
        *cil(box, "vent_cubo", [10.5, 0, 8], 0.75, 19.25, 20, "brass"),
        *raios(box, "vent_pa", [10.5, 0, 8], 2.8, 0.9, 19.35, 19.6, "corroded", n=2),
    ]

    # =================================================================
    # ELEVADOR — gaiola de 2 blocos e pouco com a plataforma livre na frente. No teto: o motor gira
    # o tambor que enrola a corda; a corda passa por cima da roldana e desce pelos fundos até a
    # travessa da plataforma.
    # =================================================================
    e_m, e_g = motor_kit(k, 12, 37.75, 2.75, comp=3, raio=2, eixo="x", nome="motor")
    elev_base = [
        box("chao", [0, 0, 0], [16, 1, 16], "cobble"),
        box("soleira", [2, 1, 15], [14, 1.25, 16], "darkiron"),
        # 4 colunas da gaiola
        box("col_no", [0, 1, 0], [2, 34, 2], "darkwood"),
        box("col_ne", [14, 1, 0], [16, 34, 2], "darkwood"),
        box("col_so", [0, 1, 14], [2, 34, 16], "mossy"),
        box("col_se", [14, 1, 14], [16, 34, 16], "darkwood"),
        # Grade de ferro nos fundos e nos lados (frente aberta pra entrar)
        *[box(f"grade_n{i}", [3 + i * 2.5, 1, 0.5], [3.6 + i * 2.5, 34, 1.1], "darkiron") for i in range(5)],
        *[box(f"grade_o{i}", [0.5, 1, 3 + i * 2.5], [1.1, 34, 3.6 + i * 2.5], "darkiron") for i in range(5)],
        *[box(f"grade_l{i}", [14.9, 1, 3 + i * 2.5], [15.5, 34, 3.6 + i * 2.5], "darkiron") for i in range(5)],
        box("trav_n", [2, 17, 0.25], [14, 18, 1.25], "carcaca"),
        box("trav_o", [0.25, 17, 2], [1.25, 18, 14], "carcaca"),
        box("trav_l", [14.75, 17, 2], [15.75, 18, 14], "carcaca"),
        # Teto
        box("teto", [0, 34, 0], [16, 35, 16], "planks"),
        box("teto_cinta", [-0.1, 34.25, -0.1], [16.1, 34.75, 16.1], "darkiron"),
        # Mancal da roldana (atrás dela) e o eixo
        box("mancal", [7.25, 35, 1], [8.75, 38.25, 2.1], "darkiron"),
        *cil(box, "roldana_eixo", [8, 37.5, 0], 0.4, 2.1, 3.6, "iron", eixo="z"),
        *e_m,
        # Corda: desce da roldana pelos fundos até a plataforma, e por cima vai até o tambor
        box("cabo", [5.5, 4.5, 2.5], [6, 37.5, 3], "rope"),
        box("cabo_cima", [8, 39.75, 2.5], [15, 40.2, 3], "rope"),
        # Alavanca de chamar, presa na coluna da frente
        box("alavanca_base", [13.25, 8, 14.5], [14, 10, 15.5], "darkiron"),
        box("alavanca", [12.85, 9.5, 14.75], [13.6, 13, 15.25], "iron", {"z": 25}, [13.25, 9.5, 15]),
        box("alavanca_bola", [11.6, 12.4, 14.6], [12.6, 13.4, 15.4], "red"),
        *terminal(13, 35, 9, "antena"),
        *lampada(13, 35, 13),
        box("musgo", [2.25, 1, 12], [6, 1.15, 14], "moss"),
    ]
    elev_plat = [
        box("plat", [2, 1.5, 2], [14, 2.5, 14], "planks"),
        box("plat_aro", [1.75, 1.75, 1.75], [14.25, 2.25, 14.25], "darkiron"),
        box("plat_travessa", [2, 2.5, 2], [14, 4, 3.25], "carcaca"),
        box("plat_gancho", [5.25, 4, 2.35], [6.25, 5.25, 3.15], "iron"),
    ]
    # Roldana (gira no eixo z) e tambor do motor (gira no eixo x)
    elev_roldana = [
        *cil(box, "roldana", [8, 37.5, 0], 2.25, 2.25, 3.25, "corroded", eixo="z"),
        *cil(box, "roldana_cubo", [8, 37.5, 0], 0.8, 3.25, 3.5, "darkiron", eixo="z"),
    ]
    elev_tambor = [
        *[e for e in e_g if e["name"].endswith("_eixo")],
        *cil(box, "tambor", [0, 37.75, 2.75], 2, 14.25, 15.75, "darkwood", eixo="x"),
        *cinta(box, "tambor_corda", [0, 37.75, 2.75], 2, 0.2, 14.5, 15.5, "rope", eixo="x"),
    ]
    for e in elev_tambor:  # eixo do kit: do motor até dentro do tambor
        if e["name"].endswith("_eixo"):
            e["to"][0] = 14.75

    return {
        "auto_luz": {
            "title": "Iluminação Elétrica",
            "parts": {"base": {"label": "Poste de luz", "elements": luz_base}},
            "auto": {
                "cat": "maquina",
                "desc": "Poste de rua velho de ferro fundido, com 2 blocos de altura: pé de pedra, coluna redonda com anéis e uma lanterna pendurada no braço. Acende sozinho quando escurece e apaga quando amanhece, sem óleo nem vela. Ilumina bem a rua e a base, e drifter não nasce perto. Gasta pouquinho, só à noite. Receita: barras de ferro (ou chapa enferrujada), vidro e cobre.",
                "modes": [["parado", "Sem energia"], ["dia", "Dia (apagada)"], ["noite", "Noite (acesa)"]],
                "default": "noite",
                "glow": ["noite"],
                "glowTex": ["luz", "luzquente"],
                "light": {"at": [8, 20, 12.6], "color": "#ffc070", "intensity": 1.6, "when": ["noite"]},
                "cam": {"pos": [2.7, 2.4, 4.0], "target": [0.5, 1.0, 0.6]},
            },
        },
        "auto_bomba": {
            "title": "Bomba d'Água e Irrigador",
            "parts": {
                "base": {"label": "Bomba + cano (parada)", "elements": bomba_base},
                "motor": {"label": "Eixo do motor (gira)", "elements": bomba_motor},
                "balancim": {"label": "Balancim (balança)", "elements": bomba_balancim},
                "pistao": {"label": "Pistão (sobe e desce)", "elements": bomba_pistao},
                "aspersor": {"label": "Aspersor (gira)", "elements": bomba_aspersor},
            },
            "auto": {
                "cat": "maquina", "agua": True,
                "desc": "Bomba de balancim (\"cavalo de pau\") na beira da água: o motor gira a caixa de engrenagens, que balança o balancim; ele puxa o pistão do cilindro, que tira água do rio pelo cano. A água sobe pelo cano do canto até o aspersor, que gira e molha a horta numa área em volta. Rega lavoura e vasos (a terra nunca seca) e as plantas crescem um pouco mais rápido. Sem água do lado, não funciona. Gasta pouco. Receita: pedras, cobre, cano de ferro enferrujado e engrenagem enferrujada.",
                "pivots": {"motor": [5, 5.75, 2], "balancim": [8, 21.5, 8], "pistao": [12, 15, 8], "aspersor": [3.75, 23, 12.75]},
                "anim": [{"part": "motor", "spin": "z", "speed": 6},
                         {"part": "balancim", "swing": "z", "amp": 0.14, "freq": 0.6},
                         {"part": "pistao", "bob": "y", "amp": 1.3, "freq": 0.6},
                         {"part": "aspersor", "spin": "y", "speed": 3}],
                "show": {"gota1": ["ligado"], "gota2": ["ligado"]},
                "fx": {"ligado": [{"type": "rain"}]},
                "cam": {"pos": [3.3, 2.3, 3.4], "target": [0.6, 0.7, 0.6]},
            },
        },
        "auto_geladeira": {
            "title": "Geladeira",
            "parts": {
                "base": {"label": "Armário + compressor (parado)", "elements": gel_base},
                "ventoinha": {"label": "Ventoinha (gira)", "elements": gel_vent},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Geladeira antiga \"de motor em cima\": armário de tábua forrado de chapa, com 2 portas grossas vedadas com couro (congelador em cima, geladeira embaixo), serpentina de cobre atrás e a caixa redonda do compressor em cima, com a ventoinha girando. Funciona como um baú, só que a comida guardada estraga MUITO mais devagar (melhor que porão); no congelador quase não estraga. Sem energia vira baú comum. Gasta energia média o tempo todo. Receita: tábuas, chapa de ferro, cobre, couro e engrenagem enferrujada.",
                "pivots": {"ventoinha": [10.5, 19.5, 8]},
                "anim": [{"part": "ventoinha", "spin": "y", "speed": 9}],
                "show": {"escarcha1": ["ligado"], "escarcha2": ["ligado"], "gelinho": ["ligado"], "serp_gelo": ["ligado"]},
                "cam": {"pos": [2.4, 1.8, 2.9], "target": [0.5, 0.6, 0.5]},
            },
        },
        "auto_elevador": {
            "title": "Elevador",
            "parts": {
                "base": {"label": "Gaiola + motor (parada)", "elements": elev_base},
                "plataforma": {"label": "Plataforma (sobe/desce)", "elements": elev_plat},
                "roldana": {"label": "Roldana (gira)", "elements": elev_roldana},
                "tambor": {"label": "Tambor da corda (gira)", "elements": elev_tambor},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Substitui o mod Dumbwaiter (o dele vai ser removido, então tire os baús das estações antigas antes, porque elas somem). Coloque uma Estação do Elevador em cada andar (mina, porão, torre) e ligue as duas com a Chave do Elevador: clique numa e depois na outra. Entrou na plataforma e puxou a alavanca: o motor do teto enrola a corda no tambor, faz barulho de corrente, a tela escurece e você aparece na outra estação. Também dá pra mandar um baú, cesto ou vaso sozinho pra outra estação, sem ir junto. Gasta energia em cada viagem (mais quanto maior a altura). Receita: tábuas, corda, chapa de ferro, cobre e engrenagem enferrujada.",
                "pivots": {"plataforma": [8, 0, 8], "roldana": [8, 37.5, 2.75], "tambor": [15, 37.75, 2.75]},
                "modes": [["parado", "Sem energia"], ["ligado", "Parado no andar"], ["subindo", "Subindo/descendo"]],
                "default": "ligado",
                "anim": [{"part": "plataforma", "viagem": "y", "amp": 16, "periodo": 10, "when": ["subindo"]},
                         {"part": "roldana", "spin": "z", "speed": -2, "when": ["subindo"]},
                         {"part": "tambor", "spin": "x", "speed": 2.2, "when": ["subindo"]}],
                "cam": {"pos": [3.0, 2.4, 4.2], "target": [0.5, 0.9, 0.5]},
            },
        },
    }
