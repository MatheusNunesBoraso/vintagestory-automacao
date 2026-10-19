"""
AUTOMAÇÃO — Pedestal do Raio: toco de tora com uma coluna de madeira, rodela de tora em cima e um
berço com pino onde se encaixa a Engrenagem Enferrujada (em pé, virada pra frente). Tudo de lenha
e sílex (é a receita): atrás, uma vara de ponta de sílex; um braço de madeira sai dela e uma
lasca de sílex encosta no dente de cima da engrenagem. Em tempestade o pedestal puxa os raios
que caem por perto: o raio desce pela vara, passa pela lasca e a enferrujada vira Temporal.

Cabe em 1 bloco: o raio do jogo cai no topo do bloco (y = 16), que é onde fica a ponta/braço.
Regras do usuário: nada flutuando, nada sobreposto, coerência mecânica (pino no centro da
engrenagem, apoiado nos 2 calços; lasca encostando no dente; braço indo da vara até a lasca).
"""
import math

TEX = {
    "ferrugem": "game:block/metal/tarnished/rusty-iron",
    "temporal": "game:item/resource/temporalgear",
    "silex": "game:block/stone/flint",
}

T8 = math.tan(math.pi / 8)

# Medidas (16 = 1 bloco)
CX, CZ = 8, 8
TOCO_Y = 2.5
COL_Y = 8
TAMPO_Y = 9.25
CY = 12.6              # centro da engrenagem / eixo
GZ0, GZ1 = 7.5, 8.5    # espessura da engrenagem
R_CORPO, R_DENTE0, R_DENTE1 = 2.3, 2.1, 3.0


def oct_y(box, nome, r, y0, y1, tex, faces=None):
    """Cilindro octogonal em pé (4 fatias giradas de 45°)."""
    w = 2 * r * T8
    out = []
    for i in range(4):
        s = i * 0.02
        out.append(box(f"{nome}{i}", [CX - r, y0 + s, CZ - w / 2], [CX + r, y1 - s, CZ + w / 2], tex,
                       {"y": 45 * i} if i else None, [CX, y0, CZ] if i else None, faces=faces))
    return out


def engrenagem(box, nome, tex, glow=0):
    """Engrenagem em pé (eixo Z) no centro (CX, CY): disco octogonal + cubo + 8 dentes."""
    w = 2 * R_CORPO * T8
    out = []
    for i in range(4):
        s = i * 0.02
        out.append(box(f"{nome}_corpo{i}", [CX - R_CORPO, CY - w / 2, GZ0 + s], [CX + R_CORPO, CY + w / 2, GZ1 - s], tex,
                       {"z": 45 * i} if i else None, [CX, CY, GZ0] if i else None, glow=glow))
    out.append(box(f"{nome}_cubo", [CX - 0.9, CY - 0.9, GZ0 - 0.4], [CX + 0.9, CY + 0.9, GZ1 + 0.4], tex, glow=glow))
    for i in range(8):
        a = 45 * i
        out.append(box(f"{nome}_dente{i}", [CX - 0.55, CY + R_DENTE0, GZ0 + 0.1], [CX + 0.55, CY + R_DENTE1, GZ1 - 0.1], tex,
                       {"z": a} if a else None, [CX, CY, GZ0] if a else None, glow=glow))
    return out


def modelos(k):
    box = k.box

    base = []
    # Toco de tora (casca nas laterais, anel da madeira em cima) com 3 raízes e musgo
    base += oct_y(box, "toco", 6, 0, TOCO_Y, "bark", faces={"up": "logend", "down": "logend"})
    base += [
        box("raiz_l", [12.5, 0.02, 6.75], [15.5, 1.25, 8.75], "bark", faces={"east": "logend"}),
        box("raiz_o", [0.75, 0.02, 7.5], [3.5, 1, 9.25], "bark", faces={"west": "logend"}),
        box("raiz_s", [6.5, 0.02, 12.5], [8.25, 1.1, 15.25], "bark", faces={"south": "logend"}),
        box("musgo_toco", [9.5, TOCO_Y, 9.5], [12, TOCO_Y + 0.08, 11.5], "moss"),
    ]
    # Coluna octogonal com 2 anéis de casca e 4 lascas de sílex cravadas no meio
    base += oct_y(box, "coluna", 2.5, TOCO_Y, COL_Y, "darkwood")
    base += oct_y(box, "anel_baixo", 2.75, 3.5, 4.1, "bark")
    base += oct_y(box, "anel_cima", 2.75, 6.6, 7.2, "bark")
    base += [
        box("lasca_s", [7.4, 4.9, 10.3], [8.6, 5.8, 10.85], "silex"),
        box("lasca_n", [7.4, 4.9, 5.15], [8.6, 5.8, 5.7], "silex"),
        box("lasca_l", [10.3, 4.9, 7.4], [10.85, 5.8, 8.6], "silex"),
        box("lasca_o", [5.15, 4.9, 7.4], [5.7, 5.8, 8.6], "silex"),
    ]
    # Tampo = rodela de tora (anel da madeira em cima e embaixo), chamuscado no meio (onde o raio já caiu)
    base += oct_y(box, "tampo", 5.5, COL_Y, TAMPO_Y, "logbark", faces={"up": "logend", "down": "logend"})
    base += oct_y(box, "chamuscado", 2.6, TAMPO_Y, TAMPO_Y + 0.25, "coal")
    base += [
        box("musgo_tampo", [3.5, TAMPO_Y, 9.5], [5, TAMPO_Y + 0.06, 11.25], "moss"),
    ]
    # Berço: 2 montantes com calço de madeira; o pino de madeira passa pelo centro da engrenagem
    for lado, x0, x1, mx0, mx1 in (("o", 3, 4.5, 2.6, 3), ("l", 11.5, 13, 13, 13.4)):
        base += [
            box(f"montante_{lado}", [x0, TAMPO_Y, 7], [x1, 14.25, 9], "mossy" if lado == "o" else "darkwood"),
            box(f"calco_{lado}", [mx0, CY - 0.8, 7.2], [mx1, CY + 0.8, 8.8], "logbark", faces={"east": "logend", "west": "logend"}),
        ]
    base.append(box("pino", [3.5, CY - 0.4, CZ - 0.4], [12.5, CY + 0.4, CZ + 0.4], "darkwood", faces={"east": "logend", "west": "logend"}))
    # Para-raios atrás: vara de madeira num calço, ponta de sílex lascado (a ponta é o topo do bloco)
    base += [
        box("vara_pe", [6.75, TAMPO_Y, 2.75], [9.25, 10, 4.75], "logbark", faces={"up": "logend"}),
        box("vara", [7.5, 10, 3.25], [8.5, 16.25, 4.25], "mossy"),
        box("ponta_silex", [7.6, 16.25, 3.35], [8.4, 17.25, 4.15], "silex"),
        box("ponta_silex2", [7.8, 17.25, 3.55], [8.2, 17.9, 3.95], "silex"),
        # Braço de madeira da vara até em cima da engrenagem; lasca de sílex encosta no dente de cima
        box("braco", [7.75, 15.85, 4.25], [8.25, 16.25, 8.3], "darkwood"),
        box("lasca_garra", [7.7, CY + R_DENTE1, 7.6], [8.3, 15.85, 8.4], "silex"),
    ]

    return {
        "auto_pedestal_raio": {
            "title": "Pedestal do Raio",
            "parts": {
                "base": {"label": "Pedestal (parado)", "elements": base},
                "engr_ferrugem": {"label": "Engrenagem Enferrujada", "elements": engrenagem(box, "ferrugem", "ferrugem")},
                "engr_temporal": {"label": "Engrenagem Temporal", "elements": engrenagem(box, "temporal", "temporal", glow=200)},
            },
            "auto": {
                "cat": "pedestal",
                "desc": "Pedestal de madeira com uma vara de ponta de sílex que puxa raio. Clique direito com uma Engrenagem Enferrujada pra encaixar ela no berço (clique de novo com a mão vazia pra tirar). Deixe a céu aberto: quando tem tempestade, o pedestal puxa pra ele os raios que caem por perto. O raio desce pela vara, passa pela lasca de sílex que encosta nela e a engrenagem enferrujada vira uma Engrenagem Temporal. Uma engrenagem por raio. Não precisa de energia. Cuidado: o raio machuca quem estiver perto! Receita: lenha e sílex.",
                "modes": [["vazio", "Vazio"], ["enferrujada", "Com engrenagem enferrujada"],
                          ["tempestade", "Tempestade (raio!)"], ["temporal", "Virou temporal"]],
                "default": "tempestade",
                "show": {"engr_ferrugem": ["enferrujada", "tempestade"], "engr_temporal": ["temporal"]},
                "glowTex": ["temporal"],
                "glow": ["temporal"],
                "fx": {"tempestade": [{"type": "rain"}, {"type": "lightning", "at": [8, 17.9, 3.75]}],
                       "temporal": [{"type": "energy", "at": [8, CY, 8]}]},
                "light": {"at": [8, CY, 10], "intensity": 0.5, "when": ["temporal"]},
                "cam": {"pos": [2.0, 1.5, 2.4], "target": [0.5, 0.55, 0.5]},
            },
        },
    }
