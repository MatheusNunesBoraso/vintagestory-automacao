"""
AUTOMAÇÃO — cena de exemplo "Rede ligada": uma base inteira com TODAS as peças da Automação nos seus lugares,
ligadas SEM FIO pelos Postes de Energia (alcance 8 blocos pra cada lado; postes no alcance um do outro se ligam).
Monta com os modelos dos outros auto_*.py (carregados antes, em ordem alfabética).
"""
import copy

R = 8  # alcance do poste (blocos pra cada lado)

# (modelo, x, z em blocos) — o rio fica a leste (x >= 1)
CENA = [
    # Beira do rio: o que precisa de água
    ("auto_pesca", 0, -5), ("auto_roda", 0, -2), ("auto_bomba", 0, 1),
    # Casa de força: torre de tempestade, baterias e o 1º poste
    ("auto_torre", -2, -5), ("auto_bateria", -2, -1), ("auto_bateria", -3, -1), ("auto_poste", -3, -3),
    # Oficina 1: fogo e fumaça
    ("auto_carvoeira", -6, -5), ("auto_defumador", -8, -5), ("auto_fornalha", -10, -5), ("auto_forja", -12, -5),
    # Oficina 2: moagem e madeira
    ("auto_moedor", -6, -2), ("auto_peneira", -8, -2), ("auto_serraria", -9, -2), ("auto_poste", -11, -2),
    ("auto_bancada", -14, -2), ("auto_olaria", -14, -5),
    # Casa: comida, calor, transporte, elevador, luz
    ("auto_geladeira", -6, 1), ("auto_aquecedor", -8, 1), ("auto_esteira", -10, 1), ("auto_elevador", -12, 1),
    ("auto_luz", -4, 2), ("auto_luz", -14, 2),
    # Defesa
    ("auto_sentinela", -16, -3), ("auto_vigia", -16, 1),
    # Roça (ao sul), com o 3º poste
    ("auto_poste", -9, 5), ("auto_colheitadeira", -5, 6), ("auto_cogumelos", -12, 6), ("auto_cocho", -14, 6),
    ("auto_colmeia", -9, 8), ("auto_acendedor", -2, 6),
    # Cerca elétrica em volta da roça, com o portão no meio
    *[("auto_cerca", x, 10) for x in range(-16, -10)], ("auto_portao", -10, 10),
    *[("auto_cerca", x, 10) for x in range(-8, -1)],
    # Mais energia, ao norte: cata-vento, painéis solares, gerador a lenha
    ("auto_catavento", -2, -9), ("auto_solar", -4, -8), ("auto_solar", -5, -8), ("auto_gerador", -7, -8),
    ("auto_estabilizador", -9, -11),
    # Oficina 3 (trabalhos chatos): curtume, tear, prensa, alambique
    ("auto_curtume", -12, -8), ("auto_tear", -14, -8), ("auto_prensa", -16, -8), ("auto_alambique", -17, -6),
    # Mineração na ponta oeste
    ("auto_pedreira", -18, -9), ("auto_sonda", -19, -5),
    # Casa: fogão e o painel da rede; chocadeira perto do cocho
    ("auto_fogao", -6, 3), ("auto_calendario", -8, 3), ("auto_painel", -10, 3), ("auto_chocadeira", -16, 7),
]
FONTES = ("auto_roda", "auto_torre", "auto_catavento", "auto_solar", "auto_gerador")
CORES = ["#6fe8ff", "#ffd36f", "#9cff8f", "#ff9ce0"]


def _mover(els, dx, dz, pre):
    out = []
    for e in copy.deepcopy(els):
        e["name"] = pre + e["name"]
        for key in ("from", "to", "rotationOrigin"):
            if key in e:
                v = e[key]
                e[key] = [v[0] + dx * 16, v[1], v[2] + dz * 16]
        out.append(e)
    return out


def modelos(k):
    prontos = k.prontos
    parts, pivots, anim, show, fx = {}, {}, [], {}, []
    pinos, brilha = {}, {"luz"}
    for i, (key, dx, dz) in enumerate(CENA):
        m = prontos.get(key)
        if not m:
            continue
        a = m["auto"]
        pre = f"{i}_"
        modos = [x[0] for x in (a.get("modes") or [["parado"], ["ligado"]])]
        # Modo "ligado" de cada peça na cena: o padrão dela (noite pra luz, cheia pra bateria...)
        ativo = a.get("default") or modos[-1]
        brilha.update(a.get("glowTex") or [])
        for pk, p in m["parts"].items():
            parts[pre + pk] = {"label": f"{m['title']} · {p['label']}", "elements": _mover(p["elements"], dx, dz, pre)}
            if pk in (a.get("pivots") or {}):
                v = a["pivots"][pk]
                pivots[pre + pk] = [v[0] + dx * 16, v[1], v[2] + dz * 16]
            for e in p["elements"]:
                if e["name"].endswith("_pino"):
                    pinos.setdefault(i, [(e["from"][0] + e["to"][0]) / 2 + dx * 16, e["to"][1],
                                         (e["from"][2] + e["to"][2]) / 2 + dz * 16])
        for an in a.get("anim") or []:
            if an.get("when") and ativo not in an["when"]:
                continue
            anim.append({**{kk: vv for kk, vv in an.items() if kk != "when"}, "part": pre + an["part"]})
        for n, ms in (a.get("show") or {}).items():
            show[pre + n] = ["ligado"] if ativo in ms else ["nunca"]
            if modos[0] in ms:
                show[pre + n].append("parado")
        for f in (a.get("fx") or {}).get(ativo, []):
            if f["type"] in ("energy", "sparks", "dust", "smoke"):
                fx.append({**f, "at": [f["at"][0] + dx * 16, f["at"][1], f["at"][2] + dz * 16]})

    # Quem liga em qual poste (o mais perto que alcança); postes se ligam em corrente
    postes = [i for i, c in enumerate(CENA) if c[0] == "auto_poste"]

    def alcanca(p, i):
        return abs(CENA[p][1] - CENA[i][1]) <= R and abs(CENA[p][2] - CENA[i][2]) <= R

    def ponto(i):
        key, dx, dz = CENA[i]
        if key == "auto_poste":
            return [8 + dx * 16, 29, 8 + dz * 16]
        return pinos.get(i, [8 + dx * 16, 12, 8 + dz * 16])

    for n, p in enumerate(postes[1:], 1):
        ant = next((q for q in postes[:n] if alcanca(q, p)), None)
        if ant is not None:
            fx.append({"type": "beam", "from": ponto(ant), "to": ponto(p), "rate": 0.1})
    sem_energia = []
    for i, (key, dx, dz) in enumerate(CENA):
        if key == "auto_poste":
            continue
        perto = [p for p in postes if alcanca(p, i)]
        if not perto:
            sem_energia.append(key)
            continue
        p = min(perto, key=lambda q: abs(CENA[q][1] - dx) + abs(CENA[q][2] - dz))
        a_, b_ = (ponto(i), ponto(p)) if key in FONTES else (ponto(p), ponto(i))
        fx.append({"type": "beam", "from": a_, "to": b_, "rate": 0.05})
    if sem_energia:
        print("[rede] fora do alcance de poste:", sem_energia)
    ranges = [{"at": [CENA[p][1], CENA[p][2]], "r": R, "color": CORES[n % len(CORES)]} for n, p in enumerate(postes)]
    # Áreas de outras máquinas (ex.: Estabilizador Temporal)
    for key, dx, dz in CENA:
        if key != "auto_poste":
            for r in (prontos.get(key) or {}).get("auto", {}).get("ranges") or []:
                ranges.append({**r, "at": [r["at"][0] + dx, r["at"][1] + dz]})

    return {
        "auto_rede": {
            "title": "Rede ligada (exemplo)",
            "parts": parts,
            "auto": {
                "cat": "rede",
                "desc": "Uma base de exemplo com TUDO da Automação no lugar, só pra ter noção. Leste: o rio com a Pesca, a Roda Geradora e a Bomba. Do lado: a casa de força (Torre de Tempestade, 2 Baterias e o 1º poste). No meio: as oficinas (Carvoeira, Defumador, Fornalha, Forja, Olaria, Moedor, Peneira, Serraria, Bancada) com o 2º poste; a casa (Geladeira, Aquecedor, Esteira, Elevador, postes de luz); a defesa (Sentinela e Vigia). Ao norte: mais energia (Cata-vento, 2 Painéis Solares, Gerador a Lenha) e o Estabilizador Temporal (o quadrado roxo é a área protegida). Oeste: a oficina dos trabalhos chatos (Curtume, Tear, Prensa, Alambique) e a mineração (Pedreira, Sonda). Na casa ainda tem o Fogão, o Calendário e o Painel da Rede; a Chocadeira fica do lado do Cocho. Ao sul: a roça (Colheitadeira, Estufa de Cogumelos, Cocho, Colmeia, Acendedor) com o 3º poste, cercada pela Cerca Elétrica com o Portão. Cada quadrado colorido é o alcance de um poste; um poste dentro do alcance do outro passa a energia adiante. No jogo a energia é invisível — 'Ver conexões' mostra o caminho.",
                "pivots": pivots, "anim": anim, "show": show, "ranges": ranges, "glowTex": sorted(brilha),
                "rio": [1, -12, 5, 4], "gradeGrande": [-8, 0],
                "fx": {"ligado": fx},
                "cam": {"pos": [-8, 22, 28], "target": [-8, 0, -1]},
            },
        }
    }
