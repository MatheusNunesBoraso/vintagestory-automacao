"""
AUTOMAÇÃO — Sentinela Elétrica: a Sentinela (mod separado até agora) entra pro mod de Automação.
Reaproveita as shapes do mod Sentinela (lidas direto da pasta) + peças elétricas no pedestal.
"""
import copy
import json
import os

SHAPES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "Sentinela", "assets", "sentinela", "shapes", "block")
if not os.path.isdir(SHAPES):  # cópia que vai junto no repositório da Automação
    SHAPES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sentinela")


def _ler(nome):
    with open(os.path.join(SHAPES, nome + ".json"), encoding="utf-8") as f:
        return json.load(f)


_base, _head = _ler("sentinela-base"), _ler("sentinela-head")
# Texturas da Sentinela com prefixo "s_" (não brigam com as do visualizador)
TEX = {"s_" + k: v for k, v in {**_base["textures"], **_head["textures"]}.items()}


def _prefixar(els):
    out = copy.deepcopy(els)

    def walk(es):
        for e in es:
            for f in e["faces"].values():
                t = f["texture"].lstrip("#")
                # Lente vira a textura que acende com energia
                f["texture"] = "#s_lensglow" if t in ("lens", "lensglow") else "#s_" + t
            walk(e.get("children") or [])
    walk(out)
    return out


def _mudar(els, nome, frm=None, to=None):
    for e in els:
        if e["name"] == nome:
            if frm:
                e["from"] = list(frm)
            if to:
                e["to"] = list(to)
            return e
    raise KeyError(nome)


def _polir_base(els):
    """Acabamento do pedestal: nada sobreposto nem no mesmo plano (as shapes do mod antigo tinham)."""
    out = []
    for e in els:
        n = e["name"]
        if n == "rebite_bl_esq3":
            continue
        if n.startswith("chapa_"):
            # Cinta do reforço vira 2 chapinhas por fora (antes atravessava o pedestal)
            f, t = e["from"], e["to"]
            oeste, norte = f[0] < 1, f[2] < 1
            ax = [f[0], f[0] + 0.25] if oeste else [t[0] - 0.25, t[0]]
            bx = [f[0] + 0.25, t[0]] if oeste else [f[0], t[0] - 0.25]
            bz = [f[2], f[2] + 0.25] if norte else [t[2] - 0.25, t[2]]
            a = copy.deepcopy(e); a["name"] = n + "_a"; a["from"] = [ax[0], f[1], f[2]]; a["to"] = [ax[1], t[1], t[2]]
            b = copy.deepcopy(e); b["name"] = n + "_b"; b["from"] = [bx[0], f[1], bz[0]]; b["to"] = [bx[1], t[1], bz[1]]
            out += [a, b]
            continue
        out.append(e)
    _mudar(out, "musgo_pedestal1", [1, 3.5, 1], [6, 3.75, 2.5])
    _mudar(out, "musgo_pedestal2", [10, 3.5, 13.5], [15, 3.75, 15])
    _mudar(out, "musgo_pedestal3", [0.8, 1.0, 9], [1.0, 2.45, 14])
    _mudar(out, "musgo_degrau", [11, 5.5, 2.5], [13.5, 5.75, 6])
    return out


def _polir_cabeca(els):
    els = [e for e in els if e["name"] != "rebite_bl_esq3"]
    # Quinas viram cantoneiras em L por fora do corpo (antes entravam meio bloco dentro dele)
    out = []
    for e in els:
        n = e["name"]
        if n in ("quina_fe", "quina_fd", "quina_te", "quina_td"):
            f, t = e["from"], e["to"]
            cx = 4 if n[-1] == "e" else 12
            cz = 11 if n[-2] == "f" else 3
            oeste, frente = cx == 4, cz == 11
            a = copy.deepcopy(e); a["name"] = n + "_a"
            a["from"] = [cx - 0.25 if oeste else cx + 0.02, f[1], f[2]]
            a["to"] = [cx - 0.02 if oeste else cx + 0.25, t[1], t[2]]
            b = copy.deepcopy(e); b["name"] = n + "_b"
            b["from"] = [cx if oeste else f[0], f[1], cz + 0.03 if frente else f[2]]
            b["to"] = [t[0] if oeste else cx, t[1], t[2] if frente else cz - 0.03]
            out += [a, b]
        else:
            out.append(e)
    els = out
    _mudar(els, "faixa_corpo", [3.72, 17.45, 2.72], [12.2, 18.2, 11.28])
    _mudar(els, "moldura_lente", [6, 17.4, 11], [10, 21, 11.5])
    for c in ("caixa_cinta1", "caixa_cinta2"):
        _mudar(els, c)["from"][0] = 11.93
    _mudar(els, "caixa_cinta2")["from"][2] = 3.03
    _mudar(els, "contrapeso", [5, 15.5, 0.5], [11, 19.5, 2.95])
    _mudar(els, "cinta_contrapeso", [4.75, 17, 0.25], [11.25, 18, 3.0])
    return els


def modelos(k):
    box, terminal, lampada, fio = k.box, k.terminal, k.lampada, k.fio
    base = _polir_base(_prefixar(_base["elements"]))
    head = _polir_cabeca(_prefixar(_head["elements"]))
    # Peças elétricas no pedestal: bobina de cobre na coluna, borne/antena, lampadinha, fio subindo pro garfo
    base += [
        box("bobina", [4.75, 7.5, 4.75], [11.25, 10.5, 11.25], "bobina"),
        box("bobina_faixa", [4.6, 8.75, 4.6], [11.4, 9.25, 11.4], "darkiron"),
        *terminal(1.75, 6, 1.75, "borne"),
        *lampada(14.25, 6, 1.75),
        fio([1.75, 6.25, 3], [1.75, 6.25, 5]),
        box("fio_pedestal", [1.5, 5.5, 4.75], [5, 6, 5.25], "cobre"),
        box("capacitor", [11.75, 5.5, 11.75], [14.25, 9, 14.25], "fired"),
        box("capacitor_tampa", [11.5, 9, 11.5], [14.5, 9.75, 14.5], "cobre"),
    ]
    return {
        "auto_sentinela": {
            "title": "Sentinela Elétrica",
            "parts": {
                "base": {"label": "Pedestal + bobina (parado)", "elements": base},
                "head": {"label": "Cabeça (gira)", "elements": head},
            },
            "auto": {
                "cat": "maquina",
                "desc": "A Sentinela agora faz parte da Automação (um mod a menos): a mesma torre de ferro enferrujado que vigia girando e atira virotes em drifters, lobos, ursos, hienas e criaturas temporais — munição infinita, mas cada disparo gasta energia. Sem energia ela fica parada e apagada. Clique direito: configura alcance, cadência, dano, alvos e som (só nesta ou em todas). Gasta pouco vigiando e médio atirando. Receita: corda, tábuas, sílex, gravetos, engrenagem enferrujada e cobre. (Sentinelas antigas do mundo viram a elétrica.)",
                "pivots": {"head": [8, 0, 8]},
                "modes": [["parado", "Sem energia"], ["vigiando", "Vigiando"], ["alerta", "Viu um inimigo!"]],
                "default": "vigiando",
                "glowTex": ["luz", "s_lensglow"],
                "anim": [{"part": "head", "swing": "y", "amp": 0.9, "freq": 0.13, "when": ["vigiando"]},
                         {"part": "head", "spin": "y", "speed": 0.9, "when": ["alerta"]}],
                "fx": {"vigiando": [{"type": "energy", "at": [8, 10.5, 8], "rate": 0.06}],
                       "alerta": [{"type": "energy", "at": [8, 10.5, 8], "rate": 0.2},
                                  {"type": "sparks", "at": [8, 9, 8], "rate": 0.15}]},
                "light": {"at": [8, 20, 14], "color": "#ff5040", "intensity": 1.0, "when": ["alerta"]},
                "cam": {"pos": [2.6, 1.9, 3.0], "target": [0.5, 0.7, 0.5]},
            },
        },
    }
