"""
REGRA: nada sobreposto. Acha:
  - ZFIGHT: duas peças com face no MESMO plano, virada pro mesmo lado, se cobrindo (pisca / "um asset por cima do outro");
  - ATRAVESSA: duas peças se cruzando "de qualquer jeito" (não é encaixe de pino, cinta abraçando nem cruz);
  - ESCONDIDA: peça inteira dentro de outra (não aparece; tirar).
Peças giradas são comparadas pela caixa delas só se as duas estiverem sem giro (as giradas ficam de fora).

Uso: py -I checa_sobreposto.py [chave ...]   (sem chave = todos os modelos da Automação, menos a cena da rede)
     -v mostra cada problema; sem -v só a contagem por modelo.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_modelos as g  # noqa: E402

EPS = 0.01
FUNDO = 0.3   # quanto uma peça pode "entrar" na outra (encaixe) antes de contar como atravessando


def girada(e):
    return any(e.get("rotation" + a) for a in "XYZ")


def caixa(e):
    f, t = e["from"], e["to"]
    return [min(f[i], t[i]) for i in range(3)], [max(f[i], t[i]) for i in range(3)]


def checar(m):
    els = [e for p in m["parts"].values() for e in p["elements"] if not girada(e)]
    cx = [caixa(e) for e in els]
    probs = []
    for i in range(len(els)):
        a0, a1 = cx[i]
        for j in range(i + 1, len(els)):
            b0, b1 = cx[j]
            ov = [min(a1[k], b1[k]) - max(a0[k], b0[k]) for k in range(3)]
            na, nb = els[i]["name"], els[j]["name"]
            # Faces no mesmo plano, mesmo sentido, se cobrindo
            for k in range(3):
                outros = [x for x in range(3) if x != k]
                if any(ov[x] <= 0.05 for x in outros):
                    continue
                if abs(a0[k] - b0[k]) < EPS or abs(a1[k] - b1[k]) < EPS:
                    # só pisca se a face estiver pra fora (as duas peças acabam no mesmo plano)
                    probs.append(("ZFIGHT", na, nb, "xyz"[k]))
                    break
            if all(x > 0 for x in ov):
                dentro_a = all(a0[k] >= b0[k] - EPS and a1[k] <= b1[k] + EPS for k in range(3))
                dentro_b = all(b0[k] >= a0[k] - EPS and b1[k] <= a1[k] + EPS for k in range(3))
                if dentro_a or dentro_b:
                    probs.append(("ESCONDIDA", na if dentro_a else nb, nb if dentro_a else na, ""))
                elif min(ov) > FUNDO:
                    # Encaixe (pino entrando, cinta abraçando, cruz de 2 caixas) é normal:
                    # uma peça cabe dentro da outra em 2 eixos, ou as duas têm o mesmo tamanho num eixo.
                    a_em_b = sum(a0[k] >= b0[k] - EPS and a1[k] <= b1[k] + EPS for k in range(3))
                    b_em_a = sum(b0[k] >= a0[k] - EPS and b1[k] <= a1[k] + EPS for k in range(3))
                    cruz = any(abs(a0[k] - b0[k]) < EPS and abs(a1[k] - b1[k]) < EPS for k in range(3))
                    if a_em_b < 2 and b_em_a < 2 and not cruz:
                        probs.append(("ATRAVESSA", na, nb, f"{min(ov):.2f}"))
    # ZFIGHT de peça escondida não importa (já vai sair)
    return probs


def main():
    args = [a for a in sys.argv[1:] if a != "-v"]
    verbose = "-v" in sys.argv
    chaves = args or [k for k in g.AUTO_MODELS if k != "auto_rede"]
    total = 0
    for k in chaves:
        p = checar(g.AUTO_MODELS[k])
        total += len(p)
        cont = {}
        for t, *_ in p:
            cont[t] = cont.get(t, 0) + 1
        print(f"{k}: " + ("ok" if not p else ", ".join(f"{n} {t}" for t, n in cont.items())))
        if verbose:
            for t, a, b, x in p:
                print(f"   {t:9s} {a}  x  {b}  {x}")
    print("TOTAL sobreposto:", total)


if __name__ == "__main__":
    main()
