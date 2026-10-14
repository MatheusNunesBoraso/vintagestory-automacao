"""
AUTOMAÇÃO — máquinas (grupo C): Esteira (Tropeiro), Cocho Automático (Pastor), Bancada Elétrica (Ferreiro),
Acendedor (Lamparineiro) e Olaria Elétrica (Oleiro).
Mesma família: base velha, carcaça de ferro enferrujado, motor do kit, antena e lampadinha azul.
Polido: tudo que gira é redondo e gira em volta do próprio eixo; correia de polia a polia alinhadas;
nada sobreposto (checa_sobreposto.py) e nada flutuando (checa_flutuando.py).
"""

TEX = {
    "barro": "game:block/clay/hardened/earthyorange",
    "ceramica": "game:block/clay/aged-ceramic2",
    "lona": "game:block/leather/poor",
    "ovo": "game:block/wood/henbox/egg",
}


def _p(eixo, al, u, v):
    """(ao longo do eixo, u, v) -> [x, y, z]."""
    if eixo == "y":
        return [u, al, v]
    if eixo == "x":
        return [al, v, u]
    return [u, v, al]


def disco(box, nome, eixo, cu, cv, a0, a1, r, tex, n=8, tex_miolo=None):
    """Disco/rolo redondo em volta de um eixo: anel de n tábuas + miolo (2 quadrados, um girado 45°).
    (cu, cv) = centro no plano do disco (eixo y: x,z; eixo x: z,y; eixo z: x,y); a0..a1 = espessura no eixo."""
    import math
    aro = 0.3 * r
    s = r - aro
    lado = 2 * r * math.tan(math.pi / n)
    c = _p(eixo, (a0 + a1) / 2, cu, cv)
    els = []
    for i in range(n):
        f = _p(eixo, a0, cu - lado / 2, cv - r)
        t = _p(eixo, a1, cu + lado / 2, cv - r + aro)
        els.append(box(f"{nome}_aro{i}", [min(f[j], t[j]) for j in range(3)], [max(f[j], t[j]) for j in range(3)], tex,
                       {eixo: 360 / n * i} if i else None, c if i else None))
    f, t = _p(eixo, a0, cu - s, cv - s), _p(eixo, a1, cu + s, cv + s)
    lo, hi = [min(f[j], t[j]) for j in range(3)], [max(f[j], t[j]) for j in range(3)]
    els.append(box(f"{nome}_miolo", lo, hi, tex_miolo or tex))
    els.append(box(f"{nome}_miolo2", lo, hi, tex_miolo or tex, {eixo: 45}, c))
    return els


def modelos(k):
    box, terminal, lampada = k.box, k.terminal, k.lampada

    def motor(*a, polia=True, **kw):
        """Motor do kit; a 2ª caixa da carcaça fica 0.05 mais curta nas pontas (sem face no mesmo plano)."""
        caixa, gira = k.motor(*a, **kw)
        ix = 0 if kw.get("eixo", "x") == "x" else 2
        for e in caixa:
            if e["name"].endswith("_corpo2"):
                e["from"][ix] += 0.05
                e["to"][ix] -= 0.05
        if not polia:
            gira = [e for e in gira if not e["name"].endswith(("_polia", "_polia2"))]
        return caixa, gira

    # =================================================================
    # ESTEIRA (Tropeiro) — lona sobre 2 rolos redondos entre trilhos de ferro; o motor embaixo
    # puxa o rolo da ponta por uma correia (polia do motor e polia do rolo no mesmo plano).
    # =================================================================
    RY, RA, RB = 7, 2.25, 13.75          # altura dos rolos e x dos dois rolos
    est_base = [
        # Pernas debaixo dos trilhos + travas
        box("perna_no", [1, 0, 3], [2, 6, 3.75], "darkwood"),
        box("perna_ne", [14.75, 0, 3], [15.75, 6, 3.75], "darkwood"),
        box("perna_so", [1, 0, 12.25], [2, 6, 13], "mossy"),
        box("perna_se", [14.75, 0, 12.25], [15.75, 6, 13], "darkwood"),
        box("trava_n", [2, 1.5, 3.1], [14.75, 2.25, 3.65], "planks"),
        box("trava_s", [2, 1.5, 12.35], [14.75, 2.25, 12.9], "planks"),
        # Trilhos laterais de ferro (os eixos dos rolos passam por eles)
        box("trilho_n", [0.25, 6, 3], [15.75, 8.5, 3.75], "carcaca"),
        box("trilho_s", [0.25, 6, 12.25], [15.75, 8.5, 13], "carcaca"),
        box("rebite_n1", [4, 7, 2.75], [4.75, 7.75, 3], "rebite"),
        box("rebite_n2", [11, 7, 2.75], [11.75, 7.75, 3], "rebite"),
        box("rebite_s1", [4, 7, 13], [4.75, 7.75, 13.25], "rebite"),
        box("rebite_s2", [9.5, 7, 13], [10.25, 7.75, 13.25], "rebite"),
        # Lona: em cima, embaixo e dando a volta nas pontas, apoiada nos rolos
        box("lona_cima", [RA, RY + 1.2, 4.25], [RB, RY + 1.65, 11.75], "lona"),
        box("lona_baixo", [RA, RY - 1.65, 4.25], [RB, RY - 1.2, 11.75], "lona"),
        box("lona_ponta_a", [RA - 1.65, RY - 1.65, 4.25], [RA - 1.2, RY + 1.65, 11.75], "lona"),
        box("lona_ponta_b", [RB + 1.2, RY - 1.65, 4.25], [RB + 1.65, RY + 1.65, 11.75], "lona"),
        # Estrado do motor + correia (laço em volta das 2 polias, por fora das pontas que giram)
        box("estrado_motor", [11.5, 0, 6.5], [15.75, 0.25, 12.25], "planks"),
        box("correia_o", [RB - 2.08, 0.72, 13.15], [RB - 1.78, RY + 1.78, 13.6], "lona"),
        box("correia_l", [RB + 1.78, 0.72, 13.15], [RB + 2.08, RY + 1.78, 13.6], "lona"),
        box("correia_cima", [RB - 2.08, RY + 1.78, 13.15], [RB + 2.08, RY + 2.08, 13.6], "lona"),
        box("correia_baixo", [RB - 2.08, 0.42, 13.15], [RB + 2.08, 0.72, 13.6], "lona"),
        # Antena num tablado e lampadinha num suporte preso no trilho
        box("tabua_antena", [1, 0, 13.5], [5, 0.5, 15.75], "planks"),
        *terminal(3, 0.5, 14.6, "antena"),
        box("suporte_lampada", [6, 7.25, 13], [8, 8, 14.8], "darkiron"),
        *lampada(7, 8, 13.9),
        box("musgo", [2, 8.5, 12.25], [4.5, 8.6, 13], "moss"),
    ]
    m_caixa, m_gira = motor(RB, 2.5, 9.5, comp=4.5, raio=1.5, eixo="z", nome="motor")
    est_base += m_caixa
    est_motor = m_gira

    def rolo(n, x, polia=False):
        els = disco(box, n, "z", x, RY, 3.75, 12.25, 1.15, "corroded", tex_miolo="darkiron")
        els.append(box(n + "_eixo", [x - 0.35, RY - 0.35, 2.6], [x + 0.35, RY + 0.35, 14.0 if polia else 13.4], "iron"))
        els.append(box(n + "_porca_n", [x - 0.6, RY - 0.6, 2.4], [x + 0.6, RY + 0.6, 3.0], "rebite"))
        if polia:
            els.append(box(n + "_polia", [x - 1.25, RY - 1.25, 13.0], [x + 1.25, RY + 1.25, 13.75], "corroded"))
            els.append(box(n + "_polia2", [x - 1.25, RY - 1.25, 13.0], [x + 1.25, RY + 1.25, 13.75], "corroded", {"z": 45}, [x, RY, 13.4]))
        else:
            els.append(box(n + "_porca_s", [x - 0.6, RY - 0.6, 13.0], [x + 0.6, RY + 0.6, 13.6], "rebite"))
        return els

    est_rol_a = rolo("rolete_a", RA)
    est_rol_b = rolo("rolete_b", RB, polia=True)
    est_caixa = [
        box("caixinha", [2.75, RY + 1.65, 5.75], [5.75, RY + 4.25, 10.25], "chestside"),
        box("caixinha_tampa", [2.6, RY + 4.25, 5.6], [5.9, RY + 4.75, 10.4], "chestlid"),
        box("caixinha_cinta", [4, RY + 1.6, 5.55], [4.5, RY + 4.8, 10.45], "darkiron"),
    ]

    # =================================================================
    # COCHO AUTOMÁTICO (Pastor) — silo sobre pernas despeja na calha; a rosca dosadora (helicoidal)
    # é tocada direto pelo motor (acoplamento redondo) e solta a ração pela bica no cocho.
    # =================================================================
    cocho_base = [
        box("chao", [0.5, 0, 0.5], [15.5, 1.5, 15.5], "cobble"),
        box("chao_borda", [0.25, 1.25, 0.25], [15.75, 1.75, 15.75], "brick"),
        # Pernas do silo
        box("perna_no", [4, 1.75, 5.25], [5, 9, 6.25], "darkwood"),
        box("perna_ne", [11, 1.75, 5.25], [12, 9, 6.25], "darkwood"),
        box("perna_so", [4, 1.75, 11.75], [5, 9, 12.75], "mossy"),
        box("perna_se", [11, 1.75, 11.75], [12, 9, 12.75], "darkwood"),
        box("trava_o", [4.1, 3, 6.25], [4.9, 3.75, 11.75], "planks"),
        box("trava_l", [11.1, 3, 6.25], [11.9, 3.75, 11.75], "planks"),
        # Silo de chapa rebitada com cintas, tampa e feno saindo
        box("silo", [4, 9, 5], [12, 15, 13], "rebite"),
        box("silo_cinta", [3.75, 11.5, 4.75], [12.25, 12.25, 13.25], "darkiron"),
        box("silo_ferrugem", [6, 9.5, 13], [8.5, 11, 13.1], "corroded"),
        box("silo_tampa", [3.75, 15, 4.75], [12.25, 15.75, 13.25], "planks"),
        box("silo_feno", [5.5, 15.75, 6.5], [10.5, 16.5, 11.5], "haytop", faces={"north": "hay", "south": "hay", "east": "hay", "west": "hay"}),
        box("funil", [5.5, 7.5, 7.5], [10.5, 9, 11.5], "carcaca"),
        # Calha da rosca (aberta em cima, a rosca gira dentro sem encostar)
        box("calha_fundo", [6.5, 5, 7], [9.5, 5.5, 14.5], "darkiron"),
        box("calha_o", [6.5, 5.5, 7], [7, 7.5, 14.5], "carcaca"),
        box("calha_l", [9, 5.5, 7], [9.5, 7.5, 14.5], "carcaca"),
        box("calha_pe", [7, 1.75, 9.5], [9, 5, 11], "darkwood"),
        box("bica", [7.25, 4, 13.75], [8.75, 5, 14.5], "darkiron"),
        # Cocho de tábua na frente com ração
        box("cocho_fundo", [2, 1.75, 13], [14, 2.25, 15.75], "planks"),
        box("cocho_n", [2, 2.25, 13], [14, 3.75, 13.5], "darkwood"),
        box("cocho_s", [2, 2.25, 15.25], [14, 3.75, 15.75], "darkwood"),
        box("cocho_o", [2, 2.25, 13.5], [2.5, 3.75, 15.25], "darkwood"),
        box("cocho_l", [13.5, 2.25, 13.5], [14, 3.75, 15.25], "darkwood"),
        box("racao", [2.5, 2.25, 13.5], [13.5, 3.25, 15.25], "hay"),
        # Suporte do motor atrás
        box("suporte_motor", [6, 1.75, 1], [10, 4, 5], "planks"),
        # Cestinho de ovos (ovos de verdade, meio enterrados na palha do cesto)
        box("cesto", [0.75, 1.75, 6.5], [3.5, 3.75, 10], "basketside"),
        box("cesto_palha", [1, 3.75, 6.75], [3.25, 3.9, 9.75], "haytop"),
        box("ovo1", [1.2, 3.5, 7.1], [2, 4.6, 7.9], "ovo"),
        box("ovo2", [2.3, 3.5, 8.1], [3.1, 4.6, 8.9], "ovo"),
        box("ovo3", [1.3, 3.5, 8.75], [2.1, 4.5, 9.55], "ovo"),
        *terminal(13, 1.75, 3, "antena"),
        *lampada(11.5, 15.75, 12.4),
        box("musgo", [12.5, 1.75, 8], [15, 1.9, 11], "moss"),
    ]
    c_caixa, c_gira = motor(8, 6.5, 3, comp=4, raio=1.75, eixo="z", nome="motor", polia=False)
    cocho_base += c_caixa
    cocho_rosca = list(c_gira) + disco(box, "acoplamento", "z", 8, 6.5, 6.25, 7.0, 1.1, "corroded") + [
        box("rosca_eixo", [7.65, 6.15, 7], [8.35, 6.85, 14.25], "iron")]
    for i in range(9):
        z = 7.45 + i * 0.8
        cocho_rosca.append(box(f"rosca_pa{i}", [7.1, 6.3, z], [8.9, 6.7, z + 0.35], "corroded",
                               {"z": 40 * i} if i else None, [8, 6.5, z] if i else None))

    # =================================================================
    # BANCADA ELÉTRICA (Ferreiro) — esmeril: o rebolo redondo fica direto no eixo do motor, com capa
    # de proteção e apoio de ferramenta; morsa com a espada gasta; bauzinho embaixo.
    # =================================================================
    banc_base = [
        box("perna_no", [1, 0, 2.5], [2.5, 9, 4], "darkwood"),
        box("perna_ne", [13.5, 0, 2.5], [15, 9, 4], "darkwood"),
        box("perna_so", [1, 0, 12], [2.5, 9, 13.5], "mossy"),
        box("perna_se", [13.5, 0, 12], [15, 9, 13.5], "darkwood"),
        box("prateleira", [1, 1, 4], [15, 2, 12], "planks"),
        box("tampo", [0.5, 9, 2], [15.5, 10, 14], "planks"),
        box("tampo_chapa", [7, 10, 5.5], [11.5, 10.1, 10.5], "darkiron"),
        # Bauzinho embaixo
        box("bau", [3, 2, 4.5], [10, 6.5, 11.5], "chestside"),
        box("bau_tampa", [2.85, 6.5, 4.35], [10.15, 7.25, 11.65], "chestlid"),
        box("bau_trava", [6, 4.5, 11.5], [7, 6.6, 11.85], "corroded"),
        # Pedestal do motor do esmeril
        box("pedestal", [7.25, 10.1, 6], [10.75, 10.75, 10], "darkiron"),
        # Capa de proteção do rebolo (por cima e atrás), presa no tampo
        box("capa_pe", [12, 10, 4.25], [13.85, 12, 4.75], "darkiron"),
        box("capa_tras", [12, 12, 4.25], [13.85, 17.25, 4.75], "corroded"),
        box("capa_cima", [12, 16.75, 4.75], [13.85, 17.25, 11.5], "corroded"),
        box("capa_lado", [13.85, 12, 4.25], [14.35, 17.25, 9], "carcaca"),
        # Apoio da ferramenta na frente do rebolo
        box("apoio_pe", [12.6, 10, 11.9], [13.25, 12.25, 12.5], "darkiron"),
        box("apoio", [12, 12.25, 11.3], [13.85, 12.75, 12.5], "iron"),
        # Morsa com a espada gasta presa
        box("morsa_base", [2, 10, 5], [6, 11, 9], "darkiron"),
        box("morsa_queixo_a", [2.25, 11, 6], [3.25, 13.5, 8], "carcaca"),
        box("morsa_queixo_b", [4.75, 11, 6], [5.75, 13.5, 8], "carcaca"),
        box("morsa_fuso", [0.75, 11.75, 6.6], [2.25, 12.55, 7.4], "iron"),
        box("morsa_manivela", [0.25, 10.75, 6.75], [0.75, 13.5, 7.25], "corroded"),
        box("espada_lamina", [3.25, 12, 2.5], [4.75, 12.8, 11], "iron"),
        box("espada_guarda", [3.1, 11.8, 11], [4.9, 13, 11.5], "brass"),
        box("espada_cabo", [3.6, 12.05, 11.5], [4.4, 12.75, 14], "leather"),
        box("espada_ferrugem", [3.3, 12.8, 4], [4.7, 12.86, 6], "corroded"),
        *terminal(14.25, 10, 2.75, "antena"),
        *lampada(6, 10, 3),
        box("musgo", [9, 10, 12], [12, 10.15, 13.75], "moss"),
    ]
    b_caixa, b_gira = motor(9, 13.5, 8, comp=4, raio=2, eixo="x", nome="motor", polia=False)
    banc_base += b_caixa
    banc_rebolo = list(b_gira) + disco(box, "rebolo", "x", 8, 13.5, 12.25, 13.6, 3, "grindtop", n=12) + [
        box("rebolo_cubo", [11.9, 12.75, 7.25], [12.25, 14.25, 8.75], "darkiron")]

    # =================================================================
    # ACENDEDOR (Lamparineiro) — poste alto com lampião de verdade (4 vidros entre cantoneiras,
    # pavio e chama), bobina de faísca no topo e caixa de comando.
    # =================================================================
    ac_base = [
        box("pe_pedra", [3, 0, 3], [13, 2, 13], "cobble"),
        box("pe_borda", [2.75, 1.75, 2.75], [13.25, 2.5, 13.25], "brick"),
        box("cunha_n", [7, 2, 5.5], [9, 5, 6.5], "darkwood", {"x": -20}, [8, 2, 6.5]),
        box("cunha_s", [7, 2, 9.5], [9, 5, 10.5], "darkwood", {"x": 20}, [8, 2, 9.5]),
        box("poste", [7, 2.5, 7], [9, 28, 9], "darkwood"),
        box("cinta1", [6.75, 6, 6.75], [9.25, 7, 9.25], "darkiron"),
        box("cinta2", [6.75, 20, 6.75], [9.25, 21, 9.25], "darkiron"),
        # Caixa de comando no poste + fio subindo pra bobina (preso pelas cintas)
        box("caixa", [9, 9, 6], [12, 14, 10], "carcaca"),
        box("caixa_tampa", [12, 9.5, 6.5], [12.3, 13.5, 9.5], "rebite"),
        box("caixa_ferrugem", [12.3, 10, 8], [12.38, 11.5, 9.25], "corroded"),
        box("fio_poste", [7.75, 13.5, 9], [8.25, 28, 9.35], "cobre"),
        box("fio_caixa", [8.25, 13.5, 9], [9, 14, 9.35], "cobre"),
        # Braço do lampião
        box("braco", [9, 26, 7.25], [14.5, 27.5, 8.75], "mossy"),
        box("mao_francesa", [9.5, 22, 7.5], [10.5, 27, 8.5], "darkwood", {"z": -35}, [10, 27, 8]),
        box("gancho", [12.25, 24.5, 7.75], [12.75, 26, 8.25], "corroded"),
        # Bobina de faísca no topo do poste
        box("bobina_base", [6.25, 28, 6.25], [9.75, 28.75, 9.75], "isolador"),
        box("bobina", [6.75, 28.75, 6.75], [9.25, 31.25, 9.25], "bobina"),
        box("bobina_anel", [6.5, 29.75, 6.5], [9.5, 30.25, 9.5], "darkiron"),
        box("bobina_esfera", [7.25, 31.25, 7.25], [8.75, 32, 8.75], "cobre"),
        *terminal(11, 2.5, 11, "antena"),
        *lampada(10.5, 14, 8),
        box("musgo", [3.25, 2.5, 3.25], [6.5, 2.65, 6.5], "moss"),
    ]
    ac_lampiao = [
        box("lamp_alca", [12.25, 23.5, 7.75], [12.75, 24.5, 8.25], "darkiron"),
        box("lamp_teto", [10.75, 22.75, 6.5], [14.25, 23.5, 9.5], "darkiron"),
        box("lamp_fundo", [10.75, 18, 6.5], [14.25, 18.5, 9.5], "corroded"),
        box("lamp_canto1", [10.75, 18.5, 6.5], [11.25, 22.75, 7], "darkiron"),
        box("lamp_canto2", [13.75, 18.5, 6.5], [14.25, 22.75, 7], "darkiron"),
        box("lamp_canto3", [10.75, 18.5, 9], [11.25, 22.75, 9.5], "darkiron"),
        box("lamp_canto4", [13.75, 18.5, 9], [14.25, 22.75, 9.5], "darkiron"),
        box("lamp_vidro_n", [11.25, 18.5, 6.6], [13.75, 22.75, 6.8], "glass"),
        box("lamp_vidro_s", [11.25, 18.5, 9.2], [13.75, 22.75, 9.4], "glass"),
        box("lamp_vidro_o", [10.85, 18.5, 7], [11.05, 22.75, 9], "glass"),
        box("lamp_vidro_l", [13.95, 18.5, 7], [14.15, 22.75, 9], "glass"),
        box("lamp_pavio", [12.25, 18.5, 7.75], [12.75, 19.5, 8.25], "coal"),
        box("chama", [11.9, 19.5, 7.4], [13.1, 21.5, 8.6], "flame"),
    ]
    ac_arco = [
        box("arco1", [8.5, 31.5, 7.75], [10.5, 31.9, 8.15], "luz", {"z": -25}, [8.5, 31.7, 8]),
        box("arco2", [10.2, 29.6, 7.8], [11, 31, 8.2], "luz", {"z": 15}, [10.6, 30.3, 8]),
        box("arco3", [10.6, 27.6, 7.85], [12.4, 28, 8.25], "luz", {"z": -40}, [11.5, 27.8, 8]),
    ]

    # =================================================================
    # OLARIA ELÉTRICA (Oleiro) — torno de oleiro de verdade: volante redondo embaixo da mesa,
    # o motor encosta uma roda de atrito em cima do volante (eixo do motor apontando pro centro),
    # o eixo sobe pelo furo da mesa até a cabeça redonda com o vaso; fornalhinha e bauzinho.
    # =================================================================
    TX, TZ = 9.5, 5          # centro do torno
    ol_base = [
        box("chao", [0.5, 0, 0.5], [15.5, 1.5, 15.5], "cobble"),
        box("chao_borda", [0.25, 1.25, 0.25], [15.75, 1.75, 15.75], "brick"),
        box("mancal", [8.9, 1.75, 4.4], [10.1, 2, 5.6], "darkiron"),
        # Mesa do torno (furo no meio pro eixo)
        box("mesa_perna_no", [6, 1.75, 2], [6.75, 5.5, 2.75], "darkwood"),
        box("mesa_perna_ne", [12.25, 1.75, 2], [13, 5.5, 2.75], "darkwood"),
        box("mesa_perna_so", [6, 1.75, 7.25], [6.75, 5.5, 8], "mossy"),
        box("mesa_perna_se", [12.25, 1.75, 7.25], [13, 5.5, 8], "darkwood"),
        box("mesa_o", [6, 5.5, 2], [9, 6.25, 8], "planks"),
        box("mesa_l", [10, 5.5, 2], [13, 6.25, 8], "planks"),
        box("mesa_n", [9, 5.5, 2], [10, 6.25, 4.5], "planks"),
        box("mesa_s", [9, 5.5, 5.5], [10, 6.25, 8], "planks"),
        box("barro_bolo", [11.75, 6.25, 7], [12.75, 7.1, 7.9], "barro"),
        # Estrado do motor
        box("estrado_motor", [1.5, 1.75, 3.25], [5.75, 2, 6.75], "planks"),
        # Fornalhinha de barro (boca virada pro torno) com cintas de resistência de cobre
        box("forno", [9.5, 1.75, 9.5], [15, 9, 15], "kilnwall", faces={"west": "kilnfront"}),
        box("forno_boca", [9.4, 2.25, 10.75], [9.5, 4.25, 13.75], "ember"),
        box("resistencia1", [9.25, 4.5, 9.25], [15.25, 5.25, 15.25], "bobina"),
        box("resistencia2", [9.25, 6.75, 9.25], [15.25, 7.5, 15.25], "bobina"),
        box("chamine", [11, 9, 11], [13, 14, 13], "chimney"),
        box("chamine_aro", [10.75, 13.5, 10.75], [13.25, 14.25, 13.25], "corroded"),
        # Bauzinho com tigela e telha prontas
        box("bau", [1, 1.75, 10], [6.5, 6, 15], "chestside"),
        box("bau_tampa", [0.85, 6, 9.85], [6.65, 6.6, 15.15], "chestlid"),
        box("bau_trava", [3.25, 4.5, 15], [4.25, 6.1, 15.35], "corroded"),
        box("tigela", [2, 6.6, 11], [4, 7.6, 13], "fired"),
        box("tigela_borda", [1.75, 7.6, 10.75], [4.25, 7.9, 13.25], "fired"),
        box("telha", [4.5, 6.6, 10.5], [6.25, 7.1, 14], "telha_vermelha"),
        *terminal(14, 1.75, 4, "antena"),
        *lampada(14.2, 9, 14.2),
        box("musgo", [6.75, 1.75, 0.75], [9.5, 1.9, 2], "moss"),
    ]
    o_caixa, o_gira = motor(3.65, 4.25, 5, comp=4, raio=1.5, eixo="x", nome="motor", polia=False)
    ol_base += o_caixa
    o_gira = [e for e in o_gira if not e["name"].endswith("_eixo")]
    ol_motor = o_gira + [box("motor_eixo", [6.15, 3.9, 4.65], [7.55, 4.6, 5.35], "iron")] + \
        disco(box, "roda_atrito", "x", 5, 4.25, 6.9, 7.6, 1.15, "leather", tex_miolo="darkiron")
    ol_torno = disco(box, "volante", "y", TX, TZ, 2.0, 3.0, 3, "darkwood", n=12, tex_miolo="planks") + [
        box("torno_eixo", [TX - 0.4, 3.0, TZ - 0.4], [TX + 0.4, 6.35, TZ + 0.4], "iron"),
        *disco(box, "cabeca", "y", TX, TZ, 6.35, 7.05, 2.75, "darkwood", n=12, tex_miolo="planks"),
        # Vaso redondinho (cruz de 2 caixas, uma 0.05 mais baixa)
        box("vaso", [TX - 1.25, 7.05, TZ - 1], [TX + 1.25, 9.55, TZ + 1], "barro"),
        box("vaso2", [TX - 1, 7.1, TZ - 1.25], [TX + 1, 9.5, TZ + 1.25], "barro"),
        box("vaso_marca", [TX - 1.3, 8, TZ - 1.3], [TX + 1.3, 8.35, TZ + 1.3], "ceramica"),
        box("vaso_pescoco", [TX - 0.75, 9.55, TZ - 0.75], [TX + 0.75, 10.3, TZ + 0.75], "barro"),
        box("vaso_boca", [TX - 1, 10.3, TZ - 1], [TX + 1, 10.75, TZ + 1], "barro"),
    ]

    MAQ = [["parado", "Sem energia"], ["ligado", "Trabalhando"]]
    return {
        "auto_esteira": {
            "title": "Esteira Transportadora",
            "parts": {
                "base": {"label": "Estrutura + motor (parada)", "elements": est_base},
                "motor": {"label": "Polia do motor (gira)", "elements": est_motor},
                "rolete_a": {"label": "Rolo de trás (gira)", "elements": est_rol_a},
                "rolete_b": {"label": "Rolo da correia (gira)", "elements": est_rol_b},
                "caixa": {"label": "Caixinha (passa)", "elements": est_caixa},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Versão elétrica do Tropeiro. Esteira de lona velha sobre rolos, entre trilhos de ferro: leva sozinha o que as máquinas produzem (bauzinho de cada uma) pros baús do armazém — respeitando o que cada máquina precisa de insumo. O motor embaixo puxa o rolo da ponta pela correia. Encoste uma na outra pra fazer o caminho; faz curva sozinha. Gasta pouca energia (só quando tem item andando). Receita: tábuas, couro, cobre e engrenagem enferrujada.",
                "pivots": {"motor": [RB, 2.5, 9.5], "rolete_a": [RA, RY, 8], "rolete_b": [RB, RY, 8], "caixa": [0, 0, 0]},
                "modes": MAQ,
                "anim": [{"part": "motor", "spin": "z", "speed": -4}, {"part": "rolete_a", "spin": "z", "speed": -4},
                         {"part": "rolete_b", "spin": "z", "speed": -4},
                         {"part": "caixa", "slide": "x", "dist": 8, "speed": 0.25}],
                "fx": {"ligado": [{"type": "energy", "at": [3, 4, 14.6], "rate": 0.08}]},
                "light": {"at": [7, 11, 14.5], "intensity": 0.5},
                "cam": {"pos": [2.1, 1.5, 2.4], "target": [0.5, 0.35, 0.5]},
            },
        },
        "auto_cocho": {
            "title": "Cocho Automático",
            "parts": {
                "base": {"label": "Silo + cocho (parado)", "elements": cocho_base},
                "rosca": {"label": "Rosca dosadora (gira)", "elements": cocho_rosca},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Versão elétrica do Pastor. Bote ração (grão, feno) no silo: a rosca vai soltando no cocho e enche os cochos dos bichos na área sem passar do limite. Também junta os ovos dos ninhos que não vão virar pintinho (cestinho do lado), fecha as porteiras à noite e avisa quando nasce filhote. Gasta pouca energia. Receita: tábuas, chapa de ferro, cobre e engrenagem enferrujada.",
                "pivots": {"rosca": [8, 6.5, 3]},
                "modes": MAQ,
                "anim": [{"part": "rosca", "spin": "z", "speed": 3}],
                "fx": {"ligado": [{"type": "dust", "at": [8, 3.75, 14.1], "rate": 0.35}]},
                "light": {"at": [11.5, 18, 12.4], "intensity": 0.5},
                "cam": {"pos": [2.2, 1.6, 2.6], "target": [0.5, 0.45, 0.5]},
            },
        },
        "auto_bancada": {
            "title": "Bancada Elétrica",
            "parts": {
                "base": {"label": "Bancada + motor (parada)", "elements": banc_base},
                "rebolo": {"label": "Rebolo do esmeril (gira)", "elements": banc_rebolo},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Versão elétrica do Ferreiro. Bote no bauzinho de baixo as ferramentas e armaduras gastas e o material barato do mesmo tipo (sílex pras de pedra, pepitas pras de metal, couro pras de couro): o esmeril vai consertando uma por uma e devolve no bauzinho. Gasta média energia (só enquanto conserta). Receita: tábuas, pedra de amolar, cobre e engrenagem enferrujada.",
                "pivots": {"rebolo": [9, 13.5, 8]},
                "modes": MAQ,
                "anim": [{"part": "rebolo", "spin": "x", "speed": -14}],
                "fx": {"ligado": [{"type": "sparks", "at": [13, 12.9, 11.1], "rate": 0.6}]},
                "light": {"at": [13, 12, 12], "color": "#ffb040", "intensity": 0.6},
                "cam": {"pos": [2.2, 1.8, 2.7], "target": [0.5, 0.65, 0.5]},
            },
        },
        "auto_acendedor": {
            "title": "Acendedor de Lampiões",
            "parts": {
                "base": {"label": "Poste + bobina (parado)", "elements": ac_base},
                "lampiao": {"label": "Lampião (balança)", "elements": ac_lampiao},
                "arco": {"label": "Arco elétrico", "elements": ac_arco},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Versão elétrica do Lamparineiro. Poste alto (2 blocos) com lampião: de dia fica esperando; quando escurece, a bobina do topo solta um arco e acende (ou reacende) as tochas apagadas/queimadas e os lampiões na área, e repõe tocha nos suportes vazios com o que tiver no bauzinho. O próprio lampião ilumina em volta. Gasta pouca energia (só à noite). Receita: tora, cobre, vidro e engrenagem enferrujada.",
                "pivots": {"lampiao": [12.5, 26, 8]},
                "modes": [["parado", "Sem energia"], ["dia", "Dia (esperando)"], ["noite", "Noite (acendendo)"]],
                "default": "noite",
                "glow": ["dia", "noite"],
                "glowTex": ["luz", "flame"],
                "show": {"chama": ["noite"], "arco": ["noite"]},
                "anim": [{"part": "lampiao", "swing": "z", "amp": 0.06, "freq": 0.5}],
                "fx": {"noite": [{"type": "energy", "at": [8, 32, 8], "rate": 0.4}, {"type": "sparks", "at": [12, 27.5, 8], "rate": 0.25}]},
                "light": {"at": [12.5, 20, 8], "color": "#ffa040", "intensity": 1.3, "when": ["noite"]},
                "cam": {"pos": [3.0, 2.4, 3.6], "target": [0.6, 1.1, 0.5]},
            },
        },
        "auto_olaria": {
            "title": "Olaria Elétrica",
            "parts": {
                "base": {"label": "Mesa, forno e bauzinho (parados)", "elements": ol_base},
                "motor": {"label": "Roda de atrito do motor (gira)", "elements": ol_motor},
                "torno": {"label": "Torno com vaso (gira)", "elements": ol_torno},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Versão elétrica do Oleiro. Torno de oleiro de verdade: o motor encosta uma roda de atrito no volante embaixo da mesa e o vaso gira lá em cima. Bote barro no bauzinho e escolha o que fazer (telha, tigela, pote ou vaso): o torno modela e a fornalhinha com resistência de cobre queima sozinha, sem lenha. O que fica pronto volta pro bauzinho. Gasta muita energia (o forno esquenta com eletricidade). Receita: barro, tijolos, cobre e engrenagem enferrujada.",
                "pivots": {"motor": [3.65, 4.25, 5], "torno": [TX, 0, TZ]},
                "modes": MAQ,
                "glowTex": ["luz", "ember"],
                # Roda de atrito (r 1.15) encostada a 2.25 do centro do volante: gira ~2x mais rápido
                "anim": [{"part": "torno", "spin": "y", "speed": 2.5}, {"part": "motor", "spin": "x", "speed": -4.9}],
                "fx": {"ligado": [{"type": "smoke", "at": [12, 14.25, 12], "top": 2.0}]},
                "light": {"at": [8.5, 3.5, 12.25], "color": "#ff8030", "intensity": 0.8},
                "cam": {"pos": [2.2, 1.6, 2.6], "target": [0.5, 0.35, 0.5]},
            },
        },
    }
