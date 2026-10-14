"""
AUTOMAÇÃO — máquinas (grupo H): Curtume Automático, Tear Elétrico e Alambique.
(A Prensa de Frutas foi refeita no auto_maq_j.py.)
Energia sem fio (alcance do Poste de Energia); o borne do kit é a antena que recebe.

Regras: coerência mecânica (redondo engata em redondo, correia de polia a polia, eixo no centro),
nada sobreposto (checa_sobreposto.py) e nada flutuando (checa_flutuando.py).
"""
import math

TEX = {
    "barril": "game:block/wood/barrel/sides",
    "barril_fundo": "game:block/wood/barrel/bottom",
    "cal": "game:block/liquid/limewater",
    "tanino": "game:block/liquid/strongtannin",
    "vinho": "game:block/liquid/wine",
    "aguardente": "game:block/liquid/whiskey",
    "pele_crua": "game:item/resource/hide/raw",
    "pele_pronta": "game:item/resource/hide/prepared",
    "balde": "game:block/wood/bucket/aged-sides",
    "vidro_fino": "game:block/glass/plain",
}


# ---------------------------------------------------------------------------------------------
# Peças redondas "de bloco" (mesmas do auto_maq_e.py)
# ---------------------------------------------------------------------------------------------
def _pos(eixo, c, u0, u1, v0, v1, a0, a1):
    if eixo == "y":
        return [c[0] + u0, a0, c[2] + v0], [c[0] + u1, a1, c[2] + v1]
    if eixo == "x":
        return [a0, c[1] + u0, c[2] + v0], [a1, c[1] + u1, c[2] + v1]
    return [c[0] + u0, c[1] + v0, a0], [c[0] + u1, c[1] + v1, a1]


def cil(box, nome, c, r, a0, a1, tex, eixo="y", faces=None):
    """Cilindro oitavado (miolo + 4 abas encostadas, sem face dupla). c = centro; vai de a0 a a1 no eixo."""
    a, s = r * 0.7071, r * 0.4142
    out = []
    for suf, u0, u1, v0, v1 in (("", -a, a, -a, a), ("_l", a, r, -s, s), ("_o", -r, -a, -s, s),
                                ("_s", -s, s, a, r), ("_n", -s, s, -r, -a)):
        f, t = _pos(eixo, c, u0, u1, v0, v1, a0, a1)
        out.append(box(nome + suf, f, t, tex, faces=faces))
    return out


def cinta(box, nome, c, r, d, a0, a1, tex, eixo="y"):
    """Cinta abraçando um cil() de raio r (d mais grossa pra fora), encaixe limpo."""
    a, s, e = r * 0.7071, r * 0.4142, 0.02
    out = []
    for suf, u0, u1, v0, v1 in (("", -a - d, a + d, -a - d, a + d), ("_l", a - e, r + d, -s - d, s + d),
                                ("_o", -r - d, -a + e, -s - d, s + d), ("_s", -s - d, s + d, a - e, r + d),
                                ("_n", -s - d, s + d, -r - d, -a + e)):
        b0, b1 = (a0 + 0.03, a1 - 0.03) if suf else (a0, a1)
        f, t = _pos(eixo, c, u0, u1, v0, v1, b0, b1)
        out.append(box(nome + suf, f, t, tex))
    return out


def aro(box, nome, c, r, esp, a0, a1, tex, eixo="y", n=8):
    """Anel oco (aduelas giradas em volta do centro); r = raio de fora, esp = grossura."""
    L = 2 * r * math.tan(math.pi / n) + 0.02
    out = []
    for i in range(n):
        ang = round(360 / n * i + 180 / n, 3)
        if eixo == "y":
            f, t, o = [c[0] - L / 2, a0, c[2] - r], [c[0] + L / 2, a1, c[2] - r + esp], [c[0], a0, c[2]]
        elif eixo == "x":
            f, t, o = [a0, c[1] - r, c[2] - L / 2], [a1, c[1] - r + esp, c[2] + L / 2], [a0, c[1], c[2]]
        else:
            f, t, o = [c[0] - L / 2, c[1] - r, a0], [c[0] + L / 2, c[1] - r + esp, a1], [c[0], c[1], a0]
        out.append(box(f"{nome}{i}", f, t, tex, {eixo: ang}, o))
    return out


def raios(box, nome, c, r, larg, a0, a1, tex, eixo="y", n=4):
    """Raios/pás saindo do centro (n pares cruzados, cada um numa espessura um tiquinho diferente)."""
    out = []
    for i in range(n):
        ang = round(180 / n * i + 90 / n, 3)
        d = 0.03 * i
        if eixo == "y":
            f, t, o = [c[0] - r, a0 + d, c[2] - larg / 2], [c[0] + r, a1 - d, c[2] + larg / 2], [c[0], a0, c[2]]
        elif eixo == "x":
            f, t, o = [a0 + d, c[1] - r, c[2] - larg / 2], [a1 - d, c[1] + r, c[2] + larg / 2], [a0, c[1], c[2]]
        else:
            f, t, o = [c[0] - r, c[1] - larg / 2, a0 + d], [c[0] + r, c[1] + larg / 2, a1 - d], [c[0], c[1], a0]
        out.append(box(f"{nome}{i}", f, t, tex, {eixo: ang}, o))
    return out


def dentes(box, nome, c, r0, r1, larg, a0, a1, tex, eixo="y", n=8):
    """Dentes de engrenagem (de r0 até r1 do centro), todos girados."""
    out = []
    for i in range(n):
        ang = round(360 / n * i + 180 / n, 3)
        if eixo == "y":
            f, t, o = [c[0] - larg / 2, a0, c[2] - r1], [c[0] + larg / 2, a1, c[2] - r0], [c[0], a0, c[2]]
        elif eixo == "x":
            f, t, o = [a0, c[1] - r1, c[2] - larg / 2], [a1, c[1] - r0, c[2] + larg / 2], [a0, c[1], c[2]]
        else:
            f, t, o = [c[0] - larg / 2, c[1] - r1, a0], [c[0] + larg / 2, c[1] - r0, a1], [c[0], c[1], a0]
        out.append(box(f"{nome}{i}", f, t, tex, {eixo: ang}, o))
    return out


def engrenagem(box, nome, c, r, a0, a1, tex, eixo="y", n=8):
    """Engrenagem redonda: disco oitavado + n dentes (os dentes um tiquinho mais finos que o disco)."""
    return cil(box, nome, c, r, a0, a1, tex, eixo) + dentes(box, nome + "_dente", c, r - 0.3, r + 0.7, 0.7,
                                                           a0 + 0.06, a1 - 0.06, tex, eixo, n)


def barra(box, nome, a, b, g, tex):
    """Barra de a até b (os dois pontos num plano x, y ou z constante), girando num eixo só."""
    d = [b[i] - a[i] for i in range(3)]
    L = math.sqrt(sum(x * x for x in d))
    h = g / 2
    if abs(d[0]) < 1e-6:   # plano x: caixa ao longo de z, gira em x
        ang = math.degrees(math.atan2(-d[1], d[2]))
        return box(nome, [a[0] - h, a[1] - h, a[2]], [a[0] + h, a[1] + h, a[2] + L], tex, {"x": round(ang, 3)}, list(a))
    if abs(d[2]) < 1e-6:   # plano z: caixa ao longo de x, gira em z
        ang = math.degrees(math.atan2(d[1], d[0]))
        return box(nome, [a[0], a[1] - h, a[2] - h], [a[0] + L, a[1] + h, a[2] + h], tex, {"z": round(ang, 3)}, list(a))
    ang = math.degrees(math.atan2(-d[2], d[0]))  # plano y
    return box(nome, [a[0], a[1] - h, a[2] - h], [a[0] + L, a[1] + h, a[2] + h], tex, {"y": round(ang, 3)}, list(a))


def correia(box, nome, c1, c2, r, g, x, tex):
    """Correia (2 lados retos) entre duas polias de raio r no mesmo plano x (centros c1, c2 = (y, z))."""
    dy, dz = c2[0] - c1[0], c2[1] - c1[1]
    L = math.hypot(dy, dz)
    ny, nz = dz / L, -dy / L
    out = []
    for i, sgn in enumerate((1, -1)):
        a = [x, c1[0] + sgn * (r + g / 2) * ny, c1[1] + sgn * (r + g / 2) * nz]
        b = [x, c2[0] + sgn * (r + g / 2) * ny, c2[1] + sgn * (r + g / 2) * nz]
        out.append(barra(box, f"{nome}{i}", a, b, g, tex))
    return out


def motor_kit(k, *a, **kw):
    """Motor do kit sem a face da cruz no mesmo plano (corpo2 um tiquinho mais curto no eixo)."""
    caixa, gira = k.motor(*a, **kw)
    i = 0 if kw.get("eixo", "x") == "x" else 2
    for e in caixa:
        if e["name"].endswith("_corpo2"):
            e["from"][i] += 0.06
            e["to"][i] -= 0.06
    return caixa, gira


def barril(box, nome, c, r, y0, y1, liquido):
    """Barril redondo aberto: corpo com o líquido em cima, beirada de aduelas e 2 cintas de ferro."""
    return [
        *cil(box, nome, c, r, y0, y1 - 0.75, "barril", faces={"up": liquido, "down": "barril_fundo"}),
        *aro(box, nome + "_beira", c, r, 0.5, y1 - 0.75, y1, "barril"),
        *cinta(box, nome + "_cinta1", c, r, 0.2, y0 + 1.5, y0 + 2.1, "darkiron"),
        *cinta(box, nome + "_cinta2", c, r, 0.2, y1 - 2.75, y1 - 2.15, "darkiron"),
    ]


def modelos(k):
    box, terminal, lampada = k.box, k.terminal, k.lampada

    # =================================================================
    # CURTUME AUTOMÁTICO — 2 barris redondos de molho (cal e tanino) com pás. Um motor em cima
    # do pórtico puxa por correia o eixo de transmissão; nele, 2 engrenagens de pé engatam nas
    # engrenagens deitadas no topo de cada pá. Na frente: rolo raspador sobre a mesa e o varal.
    # =================================================================
    cm_m, cm_g = motor_kit(k, 4.75, 20.5, 5, comp=3, raio=1.25, eixo="x", nome="motor")
    cur_base = [
        box("chao", [0, 0, 0], [16, 2, 16], "cobble"),
        *barril(box, "tonel_cal", [4.5, 0, 5], 3, 2, 11, "cal"),
        *barril(box, "tonel_tanino", [11.5, 0, 5], 3, 2, 11, "tanino"),
        # Pórtico (2 postes + viga) com 2 mancais pendurados segurando o eixo de transmissão
        box("portico_o", [0, 2, 4.25], [1.25, 17, 5.75], "darkwood"),
        box("portico_l", [14.75, 2, 4.25], [16, 17, 5.75], "mossy"),
        box("portico_viga", [0, 17, 4.25], [16, 18.5, 5.75], "darkwood"),
        box("viga_cinta_o", [0.9, 16.8, 4.1], [1.6, 18.7, 5.9], "darkiron"),
        box("viga_cinta_l", [14.4, 16.8, 4.1], [15.1, 18.7, 5.9], "darkiron"),
        box("mancal_o", [1.75, 14.25, 4.6], [2.5, 17, 5.4], "darkiron"),
        box("mancal_l", [13.5, 14.25, 4.6], [14.25, 17, 5.4], "darkiron"),
        *cm_m,
        *correia(box, "correia", (14.75, 5), (20.5, 5), 1.25, 0.25, 7.875, "leather"),
        # Mesa com couro esticado, suportes e eixo do rolo raspador
        box("mesa", [4.75, 2, 9], [15.25, 4.5, 12.5], "planks"),
        box("mesa_cinta", [4.6, 3.25, 8.85], [15.4, 3.75, 12.65], "darkiron"),
        box("couro_mesa", [6.1, 4.5, 9.25], [13.9, 4.75, 12.25], "pele_crua"),
        box("rolo_sup_o", [5.25, 4.5, 10.25], [6, 7.25, 11.25], "darkwood"),
        box("rolo_sup_l", [14, 4.5, 10.25], [14.75, 7.25, 11.25], "darkwood"),
        *cil(box, "rolo_eixo", [0, 5.75, 10.75], 0.3, 5.5, 14.5, "iron", eixo="x"),
        # Varal com couro pendurado (frente)
        box("varal_o", [0.25, 2, 13.5], [1.25, 14, 14.5], "darkwood"),
        box("varal_l", [14.75, 2, 13.5], [15.75, 14, 14.5], "darkwood"),
        box("varal", [1.25, 12.75, 13.65], [14.75, 13.5, 14.35], "mossy"),
        box("couro1", [2.5, 7, 13.8], [7.5, 12.75, 14.2], "pele_crua"),
        box("couro2", [8.5, 8, 13.8], [13.5, 12.75, 14.2], "pele_pronta"),
        box("prendedor1", [4.5, 12.5, 13.55], [5.5, 13.75, 14.45], "iron"),
        box("prendedor2", [10.5, 12.5, 13.55], [11.5, 13.75, 14.45], "iron"),
        # Bauzinho de saída (couro pronto)
        box("bau", [0.5, 2, 9], [4.25, 5, 12.25], "chestside"),
        box("bau_tampa", [0.35, 5, 8.85], [4.4, 5.5, 12.4], "chestlid"),
        box("bau_trava", [2, 3.75, 12.25], [2.75, 4.75, 12.6], "corroded"),
        *terminal(13.5, 18.5, 5, "antena"),
        *lampada(11, 18.5, 5),
        box("musgo", [12.5, 2, 8.4], [15, 2.15, 8.85], "moss"),
        box("musgo2", [5, 2, 13], [7.5, 2.15, 13.4], "moss"),
    ]
    # Pás (giram deitadas) com a engrenagem deitada no topo de cada uma
    def pa(nome, xs):
        return [
            *cil(box, nome + "_eixo", [xs, 0, 5], 0.35, 9.75, 12.5, "iron"),
            *raios(box, nome, [xs, 0, 5], 2, 0.8, 9.8, 10.7, "planks", n=2),
            *engrenagem(box, nome + "_eng", [xs, 0, 5], 1.5, 12.5, 13, "corroded"),
        ]
    cur_pa_a, cur_pa_b = pa("pa_a", 4.5), pa("pa_b", 11.5)
    # Eixo de transmissão (gira em x): polia da correia + 2 engrenagens de pé
    cur_linha = [
        *cil(box, "linha_eixo", [0, 14.75, 5], 0.35, 2, 14, "iron", eixo="x"),
        *cil(box, "linha_polia", [0, 14.75, 5], 1.25, 7.5, 8.25, "corroded", eixo="x"),
        *engrenagem(box, "linha_eng_a", [0, 14.75, 5], 1.25, 2.65, 3.15, "corroded", eixo="x"),
        *engrenagem(box, "linha_eng_b", [0, 14.75, 5], 1.25, 9.65, 10.15, "corroded", eixo="x"),
    ]
    cur_rolo = cil(box, "rolo", [0, 5.75, 10.75], 1, 6.25, 13.75, "darkiron", eixo="x") + \
        cinta(box, "rolo_estria", [0, 5.75, 10.75], 1, 0.12, 9.5, 10.5, "corroded", eixo="x")

    # =================================================================
    # TEAR ELÉTRICO — tear de pente: rolo dos fios atrás, rolo do pano na frente, os fios esticados
    # passam pelo liço (sobe e desce) e pelo pente (bate); a lançadeira corre entre os fios.
    # Do lado, a roda de fiar, puxada por correia pelo motor.
    # =================================================================
    t_m, t_g = motor_kit(k, 3.25, 3.5, 9.75, comp=3, raio=1.25, eixo="x", nome="motor")
    tear_base = [
        box("chao", [0, 0, 0], [16, 1.5, 16], "cobble"),
        box("poste_no", [1, 1.5, 3], [2, 20.5, 4], "darkwood"),
        box("poste_ne", [14, 1.5, 3], [15, 20.5, 4], "darkwood"),
        box("poste_so", [1, 1.5, 11], [2, 20.5, 12], "mossy"),
        box("poste_se", [14, 1.5, 11], [15, 20.5, 12], "darkwood"),
        box("viga_n", [2, 19, 3], [14, 20.5, 4], "darkwood"),
        box("viga_s", [2, 19, 11], [14, 20.5, 12], "darkwood"),
        box("viga_o", [1, 19, 4], [2, 20.5, 11], "planks"),
        box("viga_l", [14, 19, 4], [15, 20.5, 11], "planks"),
        box("viga_meio", [2, 19, 6.75], [14, 20.5, 7.75], "darkwood"),
        box("trilho_o", [1, 6, 4], [2, 7, 11], "planks"),
        box("trilho_l", [14, 6, 4], [15, 7, 11], "planks"),
        # Mancais dos rolos em cima dos trilhos
        box("mancal_fios_o", [1, 7, 4.75], [2, 10, 5.75], "darkwood"),
        box("mancal_fios_l", [14, 7, 4.75], [15, 10, 5.75], "darkwood"),
        box("mancal_pano_o", [1, 7, 10], [2, 10, 11], "darkwood"),
        box("mancal_pano_l", [14, 7, 10], [15, 10, 11], "darkwood"),
        # Rolos redondos (fios atrás, pano na frente) com o fio/pano enrolado
        *cil(box, "rolo_fios_eixo", [0, 9, 5.25], 0.3, 1.25, 14.75, "iron", eixo="x"),
        *cil(box, "rolo_fios", [0, 9, 5.25], 1.25, 2.5, 13.5, "darkwood", eixo="x"),
        *cinta(box, "rolo_fios_fio", [0, 9, 5.25], 1.25, 0.2, 3.2, 12.8, "linen", eixo="x"),
        *cil(box, "rolo_pano_eixo", [0, 9, 10.5], 0.3, 1.25, 14.75, "iron", eixo="x"),
        *cil(box, "rolo_pano", [0, 9, 10.5], 1.25, 2.5, 13.5, "darkwood", eixo="x"),
        *cinta(box, "rolo_pano_tecido", [0, 9, 10.5], 1.25, 0.2, 3.2, 12.8, "linen", eixo="x"),
        # Fios esticados entre os rolos (por cima)
        box("fios", [3.3, 10.45, 5.25], [12.7, 10.6, 10.5], "linen"),
        # Pedais
        box("pedal_a", [6, 1.5, 4.5], [7, 2, 11.5], "planks"),
        box("pedal_b", [9, 1.5, 4.5], [10, 2, 11.5], "planks"),
        box("pedal_barra", [5.5, 1.5, 11.5], [10.5, 2.25, 12], "darkwood"),
        # Roda de fiar: 2 montantes e o eixo
        box("roda_mont_o", [3, 1.5, 13.25], [3.75, 6, 14.25], "darkwood"),
        box("roda_mont_l", [5.25, 1.5, 13.25], [6, 6, 14.25], "darkwood"),
        *cil(box, "roda_eixo", [0, 5.5, 13.75], 0.25, 3.2, 6.65, "iron", eixo="x"),
        *t_m,
        # Bauzinho com o pano pronto
        box("bau", [9.5, 1.5, 12.75], [15, 5.5, 15.75], "chestside"),
        box("bau_tampa", [9.35, 5.5, 12.6], [15.15, 6.1, 15.9], "chestlid"),
        box("pano_dobrado", [10, 6.1, 13.25], [13, 7, 15.25], "linen"),
        box("meada", [13.25, 6.1, 13.5], [14.5, 6.75, 15], "rope"),
        *terminal(13, 20.5, 3.5, "antena"),
        *lampada(3, 20.5, 11.5),
        box("musgo", [10.5, 1.5, 5], [13, 1.65, 6.5], "moss"),
    ]
    tear_lico = [
        box("lico_quadro_cima", [3, 14.5, 7], [13, 15, 7.5], "darkwood"),
        box("lico_quadro_baixo", [3, 9.25, 7], [13, 9.75, 7.5], "darkwood"),
        box("lico_lado_o", [3, 9.75, 7], [3.5, 14.5, 7.5], "darkwood"),
        box("lico_lado_l", [12.5, 9.75, 7], [13, 14.5, 7.5], "darkwood"),
        *[box(f"lico_fio{i}", [4.5 + i * 1.5, 9.75, 7.15], [4.7 + i * 1.5, 14.5, 7.35], "linen") for i in range(6)],
        box("lico_corda_o", [4.25, 15, 7.1], [4.6, 19, 7.4], "rope"),
        box("lico_corda_l", [11.4, 15, 7.1], [11.75, 19, 7.4], "rope"),
    ]
    tear_pente = [
        box("pente_braco_o", [2, 6.5, 9], [2.5, 12, 9.5], "darkwood"),
        box("pente_braco_l", [13.5, 6.5, 9], [14, 12, 9.5], "darkwood"),
        box("pente_baixo", [2.5, 9.5, 9], [13.5, 10.2, 9.5], "darkwood"),
        box("pente_cima", [2.5, 11, 9], [13.5, 11.75, 9.5], "darkwood"),
        *[box(f"pente_dente{i}", [3.5 + i * 1.25, 10.2, 9.15], [3.65 + i * 1.25, 11, 9.35], "iron") for i in range(8)],
    ]
    tear_lanc = [
        box("lancadeira", [3, 10.4, 8.1], [6, 11, 8.9], "darkwood"),
        box("lancadeira_ponta", [6, 10.5, 8.3], [6.75, 10.9, 8.7], "iron"),
        box("lancadeira_fio", [3.75, 11, 8.3], [5.25, 11.3, 8.7], "linen"),
    ]
    # Roda de fiar (gira em x) + a polia dela, puxada pela correia do motor
    tear_roda = [
        *aro(box, "roda_aro", [0, 5.5, 13.75], 2.25, 0.45, 4.25, 4.75, "darkwood", eixo="x"),
        *raios(box, "roda_raio", [0, 5.5, 13.75], 1.95, 0.3, 4.4, 4.6, "planks", eixo="x", n=2),
        *cil(box, "roda_cubo", [0, 5.5, 13.75], 0.55, 4, 5, "darkiron", eixo="x"),
        *cil(box, "roda_polia", [0, 5.5, 13.75], 1.25, 6, 6.75, "corroded", eixo="x"),
    ]
    tear_base += correia(box, "correia", (3.5, 9.75), (5.5, 13.75), 1.25, 0.25, 6.375, "leather")

    # =================================================================
    # ALAMBIQUE — alambique de cobre de verdade: panela redonda sobre a fornalha, capitel em
    # cebola, pescoço de cisne descendo até o barril de água (com a serpentina dentro) e a bica
    # pingando nas garrafas. Um soprador (motor + hélice) atiça a fornalha por trás.
    # =================================================================
    a_m, a_g = motor_kit(k, 5, 3.95, 1.5, comp=2.5, raio=1.2, eixo="z", nome="motor")
    alam_base = [
        box("chao", [0, 0, 0], [16, 2, 16], "cobble"),
        # Fornalha elétrica de tijolo, resistências na boca da frente
        box("fornalha", [1, 2, 4], [9, 7, 12.5], "kilnwall"),
        box("fornalha_topo", [0.75, 7, 3.75], [9.25, 7.5, 12.75], "brick"),
        box("fornalha_boca", [2.5, 3, 12.5], [7.5, 6, 12.6], "coal"),
        box("resist1", [2.5, 3.5, 12.6], [7.5, 3.9, 12.8], "ember"),
        box("resist2", [2.5, 4.3, 12.6], [7.5, 4.7, 12.8], "ember"),
        box("resist3", [2.5, 5.1, 12.6], [7.5, 5.5, 12.8], "ember"),
        box("grade1", [3.5, 3, 12.8], [3.9, 6, 13], "darkiron"),
        box("grade2", [5, 3, 12.8], [5.4, 6, 13], "darkiron"),
        box("grade3", [6.5, 3, 12.8], [6.9, 6, 13], "darkiron"),
        *a_m,
        # Panela de cobre redonda + capitel em cebola
        *cil(box, "panela", [5, 0, 8.25], 3.75, 7.5, 12.5, "bobina"),
        *cinta(box, "panela_cinta", [5, 0, 8.25], 3.75, 0.2, 9.5, 10, "cobre"),
        *cil(box, "capitel", [5, 0, 8.25], 2.75, 12.5, 15, "bobina"),
        *cinta(box, "capitel_rebite", [5, 0, 8.25], 2.75, 0.15, 13.5, 13.9, "darkiron"),
        *cil(box, "capitel2", [5, 0, 8.25], 1.75, 15, 16.5, "bobina"),
        *cil(box, "capitel_topo", [5, 0, 8.25], 0.9, 16.5, 17.25, "cobre"),
        # Pescoço de cisne até o barril de água
        barra(box, "pescoco", [6.25, 15.9, 8.25], [12.25, 14.1, 8.25], 1, "bobina"),
        *cil(box, "pescoco_desce", [12.25, 0, 8.25], 0.5, 11.25, 14.6, "bobina"),
        # Barril de água (condensador) redondo
        *barril(box, "condensador", [12.25, 0, 8.25], 2.75, 2, 12, "water"),
        # Bica da serpentina e as garrafas
        box("bica", [11.75, 4.75, 11], [12.75, 5.5, 12.75], "bobina"),
        box("bica_pingo", [12.15, 4.5, 12.3], [12.35, 4.75, 12.5], "aguardente"),
        *cil(box, "garrafa1", [12.25, 0, 12.75], 0.9, 2, 3.5, "aguardente"),
        *cil(box, "garrafa1_vidro", [12.25, 0, 12.75], 0.9, 3.5, 4.1, "vidro_fino"),
        *cil(box, "garrafa1_gargalo", [12.25, 0, 12.75], 0.35, 4.1, 4.5, "vidro_fino"),
        *cil(box, "garrafa2", [14.5, 0, 13.5], 0.8, 2, 3.25, "aguardente"),
        *cil(box, "garrafa2_vidro", [14.5, 0, 13.5], 0.8, 3.25, 3.9, "vidro_fino"),
        *cil(box, "garrafa2_rolha", [14.5, 0, 13.5], 0.35, 3.9, 4.5, "darkwood"),
        # Bauzinho atrás com antena e lampadinha
        box("bau", [9.5, 2, 0.5], [15.5, 6, 3.5], "chestside"),
        box("bau_tampa", [9.35, 6, 0.35], [15.65, 6.6, 3.65], "chestlid"),
        *terminal(11, 6.6, 2, "antena"),
        *lampada(14, 6.6, 2),
        box("musgo", [0.5, 2, 13], [3.5, 2.15, 15.5], "moss"),
    ]
    # Soprador: eixo do motor + hélice girando entre o motor e a fornalha
    alam_vent = [
        *[e for e in a_g if e["name"].endswith("_eixo")],
        *cil(box, "vent_cubo", [5, 3.95, 0], 0.85, 3.3, 3.7, "darkiron", eixo="z"),
        *raios(box, "vent_pa", [5, 3.95, 0], 1.6, 0.5, 3.35, 3.6, "corroded", eixo="z", n=2),
    ]

    return {
        "auto_curtume": {
            "title": "Curtume Automático",
            "parts": {
                "base": {"label": "Barris + varal (parado)", "elements": cur_base},
                "pa_a": {"label": "Pá do barril de cal (gira)", "elements": cur_pa_a},
                "pa_b": {"label": "Pá do barril de tanino (gira)", "elements": cur_pa_b},
                "linha": {"label": "Eixo de transmissão (gira)", "elements": cur_linha},
                "rolo": {"label": "Rolo raspador (gira)", "elements": cur_rolo},
                "motor": {"label": "Eixo do motor (gira)", "elements": cm_g},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Faz todo o trabalho chato do couro sozinho: bota a pele crua no bauzinho e ela passa pelo barril de cal (solta o pelo), pelo rolo raspador (raspa) e pelo barril de tanino (curte), até sair couro pronto. O motor em cima do pórtico puxa por correia o eixo de transmissão, e as engrenagens dele giram as pás dos barris. Você só repõe cal, casca/tanino e água de vez em quando. Gasta pouco, mas o tempo todo enquanto tem pele. Receita: 2 barris, tábuas, pedras, cobre e engrenagem enferrujada.",
                "pivots": {"pa_a": [4.5, 10, 5], "pa_b": [11.5, 10, 5], "linha": [8, 14.75, 5],
                           "rolo": [10, 5.75, 10.75], "motor": [4.75, 20.5, 5]},
                "anim": [{"part": "pa_a", "spin": "y", "speed": 1.5}, {"part": "pa_b", "spin": "y", "speed": 1.5},
                         {"part": "linha", "spin": "x", "speed": 3}, {"part": "motor", "spin": "x", "speed": 3},
                         {"part": "rolo", "spin": "x", "speed": -2.5}],
                "cam": {"pos": [2.4, 1.9, 2.9], "target": [0.5, 0.6, 0.5]},
            },
        },
        "auto_tear": {
            "title": "Tear Elétrico",
            "parts": {
                "base": {"label": "Tear (parado)", "elements": tear_base},
                "lico": {"label": "Liço (sobe e desce)", "elements": tear_lico},
                "pente": {"label": "Pente (bate)", "elements": tear_pente},
                "lancadeira": {"label": "Lançadeira (vai e vem)", "elements": tear_lanc},
                "roda": {"label": "Roda de fiar (gira)", "elements": tear_roda},
                "motor": {"label": "Eixo do motor (gira)", "elements": t_g},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Linho vira pano sozinho: o motor puxa por correia a roda de fiar, que fia o linho, e o tear tece — o liço sobe e desce abrindo os fios, a lançadeira passa no meio e o pente bate a trama. Bota linho (ou fio) no bauzinho e sai pano/tecido pronto, pra roupa, cama, sacos e bandeiras. Gasta pouco. Receita: tábuas, gravetos, corda, cobre e engrenagem enferrujada.",
                "pivots": {"lico": [8, 12, 7.25], "pente": [8, 6.5, 9.25], "lancadeira": [4.5, 10.7, 8.5],
                           "roda": [4.5, 5.5, 13.75], "motor": [3.25, 3.5, 9.75]},
                "anim": [{"part": "lico", "bob": "y", "amp": 1.5, "freq": 0.8},
                         {"part": "pente", "swing": "x", "amp": 0.12, "freq": 0.8},
                         {"part": "lancadeira", "shake": "x", "amp": 3.5, "freq": 0.4},
                         {"part": "roda", "spin": "x", "speed": 3},
                         {"part": "motor", "spin": "x", "speed": 3}],
                "cam": {"pos": [2.4, 1.8, 3.0], "target": [0.5, 0.6, 0.5]},
            },
        },
        "auto_alambique": {
            "title": "Alambique",
            "parts": {
                "base": {"label": "Alambique (parado)", "elements": alam_base},
                "ventoinha": {"label": "Soprador (gira)", "elements": alam_vent},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Destila sozinho: bota vinho, cidra, cerveja ou fermentado na panela de cobre e a fornalha elétrica esquenta (o soprador de trás atiça). O vapor sobe pelo capitel, desce pelo pescoço de cisne até a serpentina dentro do barril d'água e pinga destilado (as bebidas fortes do jogo) nas garrafas. Também faz vinagre. Gasta médio enquanto esquenta. Receita: cobre, tijolos, barril e engrenagem enferrujada.",
                "pivots": {"ventoinha": [5, 3.95, 1.5]},
                "anim": [{"part": "ventoinha", "spin": "z", "speed": 8}],
                "glowTex": ["luz", "ember"],
                "fx": {"ligado": [{"type": "smoke", "at": [5, 17.5, 8.25], "top": 1.6}]},
                "light": {"at": [5, 4.5, 14], "color": "#ff8a30", "intensity": 0.8},
                "cam": {"pos": [2.4, 1.6, 2.9], "target": [0.5, 0.45, 0.5]},
            },
        },
    }
