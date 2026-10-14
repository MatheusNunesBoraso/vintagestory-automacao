"""
REGRA: nada flutuando. Acha peças (ou grupos de peças) que não encostam no chão nem em nada ligado ao chão.

Uso: py -I checa_flutuando.py [chave ...]   (sem chave = todos os modelos da Automação, menos a cena da rede)
Considera todas as partes juntas (peça que gira presa pelo eixo conta como apoiada).
Peças com nome contendo "faisca", "brilho", "arco", "fumaca" são efeito e podem flutuar.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_modelos as g  # noqa: E402

TOL = 0.06
EFEITO = ("faisca", "brilho", "arco", "fumaca", "nevoa", "gota", "raio_")


def _rot(p, o, e):
    x, y, z = (p[i] - o[i] for i in range(3))
    # Mesma ordem do visualizador (Euler XYZ do three.js: aplica Z, depois Y, depois X)
    rz, ry, rx = (math.radians(e.get("rotation" + a, 0)) for a in "ZYX")
    x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
    x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    return [x + o[0], y + o[1], z + o[2]]


def caixa(e):
    f, t = e["from"], e["to"]
    cantos = [[(f, t)[i][0], (f, t)[j][1], (f, t)[k][2]] for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    if any(e.get("rotation" + a) for a in "XYZ"):
        o = e.get("rotationOrigin") or [(f[i] + t[i]) / 2 for i in range(3)]
        cantos = [_rot(c, o, e) for c in cantos]
    lo = [min(c[i] for c in cantos) for i in range(3)]
    hi = [max(c[i] for c in cantos) for i in range(3)]
    return lo, hi


def encosta(a, b):
    return all(a[0][i] <= b[1][i] + TOL and b[0][i] <= a[1][i] + TOL for i in range(3))


def checar(key, m):
    els = [e for p in m["parts"].values() for e in p["elements"]]
    cx = [caixa(e) for e in els]
    n = len(els)
    apoiado = [cx[i][0][1] <= TOL for i in range(n)]
    fila = [i for i in range(n) if apoiado[i]]
    while fila:
        i = fila.pop()
        for j in range(n):
            if not apoiado[j] and encosta(cx[i], cx[j]):
                apoiado[j] = True
                fila.append(j)
    soltos = [els[i]["name"] for i in range(n) if not apoiado[i] and not any(w in els[i]["name"] for w in EFEITO)]
    return soltos


def main():
    chaves = sys.argv[1:] or [k for k in g.AUTO_MODELS if k != "auto_rede"]
    total = 0
    for k in chaves:
        soltos = checar(k, g.AUTO_MODELS[k])
        total += len(soltos)
        print(f"{k}: " + ("ok" if not soltos else f"{len(soltos)} flutuando -> " + ", ".join(soltos)))
    print("TOTAL flutuando:", total)


if __name__ == "__main__":
    main()
