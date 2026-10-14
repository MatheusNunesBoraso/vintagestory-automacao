"""
AUTOMAÇÃO — Fornalha Elétrica: derrete minério / funde metal e cozinha sem lenha nem carvão.
"""

TEX = {
    "lingote": "game:block/metal/ingot/copper",
    "refratario": "game:block/clay/fireclay",
}


def modelos(k):
    box, terminal, lampada, motor = k.box, k.terminal, k.lampada, k.motor

    base = [
        box("alicerce", [0.5, 0, 0.5], [15.5, 2.5, 15.5], "cobble"),
        box("alicerce_borda", [0.25, 2.25, 0.25], [15.75, 3, 15.75], "brick"),
        # Corpo de tijolo de barro (como a fornalha do jogo), cintado de ferro
        box("corpo", [5, 3, 2], [15, 13, 13.5], "kilnwall"),
        box("corpo_topo", [4.75, 13, 1.75], [15.25, 14, 13.75], "brick"),
        box("cinta_baixo", [4.75, 4.5, 1.75], [15.25, 5.5, 13.75], "darkiron"),
        box("cinta_cima", [4.75, 10.5, 1.75], [15.25, 11.5, 13.75], "darkiron"),
        # Cantoneiras de ferro por fora das 4 quinas do corpo
        box("canto_no_a", [4.8, 3, 1.8], [6, 13, 2], "rebite"),
        box("canto_no_b", [4.8, 3, 2], [5, 13, 3.25], "rebite"),
        box("canto_ne_a", [14, 3, 1.8], [15.2, 13, 2], "rebite"),
        box("canto_ne_b", [15, 3, 2], [15.2, 13, 3.25], "rebite"),
        box("canto_so_a", [4.8, 3, 13.5], [6, 13, 13.7], "rebite"),
        box("canto_so_b", [4.8, 3, 12.25], [5, 13, 13.5], "rebite"),
        box("canto_se_a", [14, 3, 13.5], [15.2, 13, 13.7], "rebite"),
        box("canto_se_b", [15, 3, 12.25], [15.2, 13, 13.5], "rebite"),
        # Frente: porta de ferro com janela gradeada onde se vê as resistências
        box("porta_baixo", [6, 4, 13.5], [14, 6.5, 14.25], "carcaca"),
        box("porta_cima", [6, 10, 13.5], [14, 12, 14.25], "carcaca"),
        box("porta_esq", [6, 6.5, 13.5], [7.5, 10, 14.25], "carcaca"),
        box("porta_dir", [12.5, 6.5, 13.5], [14, 10, 14.25], "carcaca"),
        box("porta_moldura", [5.75, 11.75, 13.4], [14.25, 12.5, 14.4], "rebite"),
        box("trinco", [12.75, 7.5, 14.25], [13.5, 9, 15], "brass"),
        box("dobradica1", [5.5, 5, 13.55], [6.25, 6.25, 14.6], "darkiron"),
        box("dobradica2", [5.5, 9.5, 13.55], [6.25, 11, 14.6], "darkiron"),
        box("fundo_forno", [7.5, 6.5, 13.45], [12.5, 10, 13.55], "coal"),
        box("resist1", [7.5, 6.9, 13.55], [12.5, 7.4, 13.85], "ember"),
        box("resist2", [7.5, 8, 13.55], [12.5, 8.5, 13.85], "ember"),
        box("resist3", [7.5, 9.1, 13.55], [12.5, 9.6, 13.85], "ember"),
        box("grade1", [8.6, 6.5, 14], [9, 10, 14.2], "darkiron"),
        box("grade2", [10, 6.5, 14], [10.4, 10, 14.2], "darkiron"),
        box("grade3", [11.4, 6.5, 14], [11.8, 10, 14.2], "darkiron"),
        # Cadinho embutido em cima (onde vai o minério) + meia tampa levantada
        box("cadinho_n", [7, 14, 4.5], [13, 15.5, 5.25], "refratario"),
        box("cadinho_s", [7, 14, 9.75], [13, 15.5, 10.5], "refratario"),
        box("cadinho_o", [7, 14, 5.25], [7.75, 15.5, 9.75], "refratario"),
        box("cadinho_l", [12.25, 14, 5.25], [13, 15.5, 9.75], "refratario"),
        box("cadinho_fundo", [7.75, 14, 5.25], [12.25, 14.25, 9.75], "coal"),
        box("cadinho_tampa", [7, 15.5, 3.5], [10.5, 16, 5], "darkiron", {"x": -35}, [10, 15.5, 4.5]),
        # Chaminé de barro atrás (fora do caminho do cadinho)
        box("chamine", [11, 14, 1.9], [14, 20, 4.4], "chimney"),
        box("chamine_aro", [10.75, 19.5, 1.65], [14.25, 20.25, 4.65], "corroded"),
        # Bandeja de saída na frente com lingote pronto
        box("bandeja", [6, 3, 14.25], [14, 3.75, 15.75], "darkiron"),
        box("bandeja_borda", [6, 3.75, 15.25], [14, 4.5, 15.75], "darkiron"),
        box("lingote1", [7, 3.75, 14.5], [9.5, 4.5, 15.25], "lingote"),
        box("lingote2", [10, 3.75, 14.5], [12.5, 4.5, 15.25], "lingote"),
        # Duto: sai do bocal do soprador e entra na parede oeste da fornalha
        box("duto", [0.75, 4.6, 10.25], [5.04, 7.4, 12.75], "darkiron"),
        box("duto_cinta", [2.5, 4.4, 10.1], [3.25, 7.6, 12.9], "rebite"),
        *terminal(6.25, 14, 3, "borne"),
        *lampada(6.5, 14, 12.5),
        box("musgo1", [0.5, 3, 13], [4, 3.15, 15.25], "moss"),
        box("musgo2", [12, 14, 11], [15, 14.15, 13.5], "moss"),
    ]
    # Soprador: motor do kit deitado no lado oeste (eixo pro sul) e o ventilador dentro de um bocal
    # redondo; o pivô do giro é o centro do eixo
    CX, CY = 2.25, 5.65
    caixa, gira_motor = motor(CX, CY, 5, comp=5, raio=1.9, eixo="z", nome="soprador")
    for e in caixa:
        if e["name"].endswith("_corpo2"):  # as 2 caixas do corpo do motor não podem acabar no mesmo plano
            e["from"][2] += 0.05
            e["to"][2] -= 0.05
    base += caixa
    for i in range(8):
        base.append(box(f"bocal{i}", [CX - 0.85, CY + 1.95, 8.4], [CX + 0.85, CY + 2.25, 10.25], "carcaca",
                        {"z": 45 * i} if i else None, [CX, CY, 9.3] if i else None))
    gira = [e for e in gira_motor if e["name"].endswith("_eixo")]
    gira.append(box("ventilador_cubo", [CX - 0.6, CY - 0.6, 9.0], [CX + 0.6, CY + 0.6, 9.8], "rebite"))
    for i in range(4):
        gira.append(box(f"ventilador_pa{i}", [CX - 0.35, CY + 0.6, 9.15], [CX + 0.35, CY + 1.75, 9.65], "corroded",
                        {"z": 90 * i + 20}, [CX, CY, 9.4]))
    # Metal derretido no cadinho (só com energia e carga)
    fundido = [box("metal_fundido", [7.75, 14.25, 5.25], [12.25, 14.9, 9.75], "ember")]

    return {
        "auto_fornalha": {
            "title": "Fornalha Elétrica",
            "parts": {
                "base": {"label": "Fornalha (parada)", "elements": base},
                "soprador": {"label": "Soprador (gira)", "elements": gira},
                "fundido": {"label": "Metal derretendo", "elements": fundido},
            },
            "auto": {
                "cat": "maquina",
                "desc": "Fornalha de barro com resistências elétricas: faz o que a fogueira/forno faz, sem lenha nem carvão. Coloque minério ou metal no cadinho de cima (derrete e sai lingote na bandeja da frente, sem precisar de molde à mão) ou comida pra cozinhar. A temperatura sobe sozinha até o ponto certo e o soprador do lado mantém. Gasta MUITA energia (é a máquina mais gulosa) — boa pra ligar numa bateria cheia ou na Torre de Tempestade. Receita: tijolos refratários, cobre, chapa de ferro e engrenagem enferrujada.",
                "pivots": {"soprador": [2.25, 5.65, 9.3]},
                "modes": [["parado", "Sem energia"], ["ligado", "Esquentando"], ["derretendo", "Derretendo"]],
                "default": "derretendo",
                "anim": [{"part": "soprador", "spin": "z", "speed": 9}],
                "glowTex": ["luz", "ember"],
                "show": {"fundido": ["derretendo"]},
                "fx": {"ligado": [{"type": "smoke", "at": [12.5, 20.5, 3.15], "top": 2.4}],
                       "derretendo": [{"type": "smoke", "at": [12.5, 20.5, 3.15], "top": 2.4},
                                      {"type": "sparks", "at": [10, 15.5, 7.5], "rate": 0.25}]},
                "light": {"at": [10, 9, 16], "color": "#ff8a30", "intensity": 1.0},
                "cam": {"pos": [2.0, 1.6, 2.6], "target": [0.5, 0.5, 0.5]},
            },
        },
    }
