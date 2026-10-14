"""
Gera os assets do mod Automação a partir dos modelos do visualizador (_modelos3d/auto_*.py):
shapes (parte parada + partes que mexem/acendem), blocktypes, lang, receitas e o Manual.

Uso: py -I gen_mod.py
"""
import copy
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Modelos: a pasta de trabalho (../_modelos3d) se existir; senão a cópia que vai junto no repositório (modelos/)
_trabalho = os.path.join(os.path.dirname(HERE), "_modelos3d")
sys.path.insert(0, _trabalho if os.path.isdir(_trabalho) else os.path.join(HERE, "modelos"))
import gen_modelos as g  # noqa: E402

ASSETS = os.path.join(HERE, "assets", "automacao")
MODS = g.AUTO_MODELS

# ---------------------------------------------------------------------
# Extras por peça (o que o visualizador não diz)
# ---------------------------------------------------------------------
# estado: variante extra (luz acende de verdade / portão abre de verdade)
ESTADOS = {
    "luz": {"estados": ["apagado", "aceso"], "luzHsv": [7, 4, 18]},
    "acendedor": {"estados": ["apagado", "aceso"], "luzHsv": [7, 5, 14]},
    "fornalha": {"estados": ["apagado", "aceso"], "luzHsv": [4, 6, 9]},
    "aquecedor": {"estados": ["apagado", "aceso"], "luzHsv": [4, 6, 8]},
    "portao": {"estados": ["fechado", "aberto"]},
}
# Máquinas que trabalham numa área (mostra "Área" na janela)
USA_AREA = {"colheitadeira", "pesca", "colmeia", "cogumelos", "esteira", "cocho", "acendedor", "bomba", "vigia",
            "cerca", "pedreira", "sonda", "sentinela", "aquecedor", "estabilizador", "peneira"}
SEM_BAU = {"poste", "bateria", "luz", "cerca", "portao", "calendario", "painel", "estabilizador", "aquecedor",
           "torre", "catavento", "solar", "roda", "vigia"}

# Receitas baratas (3x3). Letras:
ING = {
    "P": {"type": "item", "code": "game:plank-*"},
    "G": {"type": "item", "code": "game:gear-rusty"},
    "F": {"type": "item", "code": "game:flint"},
    "S": {"type": "block", "code": "game:cobblestone-*"},
    "K": {"type": "item", "code": "game:stick"},
    "I": {"type": "item", "code": "game:ingot-copper"},
    "R": {"type": "item", "code": "game:rope"},
    "L": {"type": "block", "code": "game:glass-plain"},
    "C": {"type": "item", "code": "game:clay-*"},
    "H": {"type": "item", "code": "game:paper-parchment"},
    "E": {"type": "item", "code": "game:leather-normal-plain"},
    "M": {"type": "item", "code": "game:metalplate-iron"},
    "N": {"type": "item", "code": "game:metalnailsandstrips-iron"},
    "B": {"type": "item", "code": "game:burnedbrick-*"},
    "T": {"type": "item", "code": "game:gear-temporal"},
}
RECEITAS = {
    "roda": ["PGP", "PIP", "SSS"],
    "torre": [" I ", "PGP", "SLS"],
    "catavento": ["RPR", "PGP", "KIK"],
    "solar": ["LLL", "IGI", "PKP"],
    "gerador": ["SIS", "SGS", "SFS"],
    "bateria": ["CIC", "CIC", "PPP"],
    "poste": [" L ", " I ", " P "],
    "estabilizador": ["ITI", "LGL", "SSS"],
    "sentinela": ["RPR", "FGF", "KIK"],
    "elevador": ["PRP", "PGP", "PIP"],
    "luz": [" L ", " I ", " K "],
    "cerca": ["KIK", "KIK"],
    "portao": ["PIP", "PGP"],
    "calendario": ["PHP", "LGL", "PIP"],
    "painel": ["PHP", "IGI"],
    "fornalha": ["BIB", "BGB", "SSS"],
    "forja": ["MIM", "SGS", "SSS"],
    "geladeira": ["PMP", "IGI", "PMP"],
    "aquecedor": ["MIM", "MGM"],
    "alambique": ["III", "PGP", "BBB"],
}
RECEITA_PADRAO = ["PGP", "PFP", "SIS"]


def chave(k):
    return k[len("auto_"):]


def mods():
    return {chave(k): m for k, m in MODS.items() if k != "auto_rede"}


# ---------------------------------------------------------------------
def textures_usadas(els, acc=None):
    acc = set() if acc is None else acc
    for e in els:
        for f in e["faces"].values():
            acc.add(f["texture"].lstrip("#"))
        textures_usadas(e.get("children") or [], acc)
    return acc


def shape_json(els, glow_tex=(), glow=False):
    els = copy.deepcopy(els)

    def walk(es):
        for e in es:
            for f in e["faces"].values():
                f.pop("glow", None)
                if glow and f["texture"].lstrip("#") in glow_tex:
                    f["glow"] = 220
            walk(e.get("children") or [])
    walk(els)
    texs = {c: g.TEXTURES[c] for c in textures_usadas(els) if c in g.TEXTURES}
    return {"textureWidth": 16, "textureHeight": 16, "textures": texs, "elements": els}


def gravar(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def caixa(els):
    lo = [min(min(e["from"][i], e["to"][i]) for e in els) / 16 for i in range(3)]
    hi = [max(max(e["from"][i], e["to"][i]) for e in els) / 16 for i in range(3)]
    return lo, hi


def gerar_bloco(k, m, lang):
    a = m["auto"]
    modos = [x[0] for x in (a.get("modes") or [["parado", "Sem energia"], ["ligado", "Ligado"]])]
    glow_tex = set(a.get("glowTex") or ["luz"])
    anims = a.get("anim") or []
    show = a.get("show") or {}
    pivots = a.get("pivots") or {}
    animadas = {an["part"] for an in anims}

    estaticos, partes = [], []
    luz_estatica = []
    for pk, p in m["parts"].items():
        els = p["elements"]
        show_parte = show.get(pk)
        # elementos com 'show' individual viram parte própria
        sozinhos = [e for e in els if e["name"] in show]
        resto = [e for e in els if e["name"] not in show]
        if pk in animadas or show_parte:
            partes.append({"nome": pk, "els": resto + sozinhos if not show_parte else els, "show": show_parte,
                           "anim": [ {kk: vv for kk, vv in an.items() if kk != "part"} for an in anims if an["part"] == pk],
                           "pivo": pivots.get(pk, [8, 0, 8])})
            continue
        for e in sozinhos:
            partes.append({"nome": "s_" + e["name"], "els": [e], "show": show[e["name"]], "anim": [], "pivo": [8, 0, 8]})
        for e in resto:
            usa = {f["texture"].lstrip("#") for f in e["faces"].values()}
            (luz_estatica if usa & glow_tex else estaticos).append(e)
    if luz_estatica:
        partes.append({"nome": "luzes", "els": luz_estatica, "show": None, "anim": [], "pivo": [8, 0, 8]})

    pasta = os.path.join(ASSETS, "shapes", "block", k)
    if os.path.isdir(pasta):
        shutil.rmtree(pasta)
    gravar(os.path.join(pasta, "base.json"), shape_json(estaticos or [g.box("vazio", [7.9, 0, 7.9], [8.1, 0.01, 8.1], "darkiron")]))
    attr_partes = []
    for p in partes:
        tem_luz = bool(textures_usadas(p["els"]) & glow_tex)
        gravar(os.path.join(pasta, p["nome"] + ".json"), shape_json(p["els"]))
        if tem_luz:
            gravar(os.path.join(pasta, p["nome"] + "-on.json"), shape_json(p["els"], glow_tex, True))
        d = {"nome": p["nome"], "pivo": p["pivo"], "luz": tem_luz, "anim": p["anim"]}
        if p["show"]:
            d["show"] = p["show"]
        attr_partes.append(d)
    # Modelo do inventário: tudo junto (no modo "trabalhando")
    ativo = a.get("default") or modos[-1]
    todos = []
    for pk, p in m["parts"].items():
        if show.get(pk) and ativo not in show[pk]:
            continue
        todos += [e for e in p["elements"] if e["name"] not in show or ativo in show[e["name"]]]
    gravar(os.path.join(pasta, "full.json"), shape_json(todos, glow_tex, True))

    # ---------------- blocktype ----------------
    lo, hi = caixa(todos)
    altura = min(2.0, max(0.25, hi[1]))
    sel = {"x1": max(0, lo[0]), "y1": 0, "z1": max(0, lo[2]), "x2": min(1, hi[0]), "y2": altura, "z2": min(1, hi[2])}
    coll = dict(sel)
    if k == "elevador":
        coll = {"x1": 0, "y1": 0, "z1": 0, "x2": 1, "y2": 0.16, "z2": 1}
    if k in ("cerca",):
        coll["y2"] = 1.5
    if k == "portao":
        sel["x2"] = coll["x2"] = min(2, hi[0])
    est = ESTADOS.get(k)
    variantes = [{"code": "side", "states": ["south", "east", "north", "west"]}]
    if est:
        variantes.insert(0, {"code": "estado", "states": est["estados"]})
    rot = {"south": 0, "east": 90, "north": 180, "west": 270}
    tex_bloco = {c: {"base": g.TEXTURES[c]} for c in textures_usadas(todos) if c in g.TEXTURES}
    for p in partes:
        for c in textures_usadas(p["els"]):
            if c in g.TEXTURES:
                tex_bloco[c] = {"base": g.TEXTURES[c]}
    inv = "*-" + (est["estados"][0] + "-" if est else "") + "south"
    bt = {
        "code": k,
        "class": "BlockMaquina",
        "entityClass": "BEMaquina",
        "variantgroups": variantes,
        "attributes": {
            "trabalho": k, "chave": k, "modos": modos, "modoTrabalhando": ativo,
            "partes": attr_partes, "usaArea": k in USA_AREA, "bau": k not in SEM_BAU,
            **({"glowModos": a["glow"]} if a.get("glow") else {}),
            **({"estados": est["estados"]} if est else {}),
        },
        "behaviors": [{"name": "AutomacaoGirarChave"}],
        "creativeinventory": {"general": [inv], "mechanics": [inv]},
        "shapeByType": {f"*-{s}": {"base": f"automacao:block/{k}/base", "rotateY": r} for s, r in rot.items()},
        "shapeInventory": {"base": f"automacao:block/{k}/full"},
        "textures": tex_bloco,
        "drawtype": "json",
        "blockmaterial": "Metal",
        "sidesolid": {"all": False},
        "sideopaque": {"all": False},
        "lightAbsorption": 0,
        "resistance": 3,
        "replaceable": 500,
        "collisionbox": coll,
        "selectionbox": sel,
        "sounds": {"place": "game:block/anvil", "break": "game:block/anvil", "hit": "game:block/anvil", "walk": "game:walk/stone"},
        "guiTransform": {"rotation": {"x": -22, "y": -30, "z": 0}, "origin": {"x": 0.5, "y": altura / 2, "z": 0.5},
                         "scale": round(min(1.0, 1.15 / max(1, altura, hi[0] - lo[0], hi[2] - lo[2])), 2)},
        "groundTransform": {"origin": {"x": 0.5, "y": 0, "z": 0.5}, "scale": 2.2},
        "tpHandTransform": {"translation": {"x": -0.9, "y": -0.3, "z": -0.5}, "rotation": {"x": 0, "y": -90, "z": 0}, "scale": 0.4},
    }
    if est and est.get("luzHsv"):
        bt["lightHsvByType"] = {f"*-{est['estados'][1]}-*": est["luzHsv"], "*": [0, 0, 0]}
    if k == "portao":
        bt["collisionboxByType"] = {"*-aberto-*": {"x1": 0, "y1": 0, "z1": 0, "x2": 0.0001, "y2": 0.0001, "z2": 0.0001}, "*": coll}
        bt.pop("collisionbox")
    gravar(os.path.join(ASSETS, "blocktypes", k + ".json"), bt)

    # ---------------- receita ----------------
    padrao = RECEITAS.get(k, RECEITA_PADRAO)
    letras = sorted({c for linha in padrao for c in linha if c != " "})
    rec = {
        "ingredientPattern": ",".join(linha.replace(" ", "_") for linha in padrao),
        "ingredients": {c: {**ING[c], "quantity": 1} for c in letras},
        "width": max(len(x) for x in padrao), "height": len(padrao),
        "output": {"type": "block", "code": f"automacao:{k}-" + (est["estados"][0] + "-" if est else "") + "south", "quantity": 1},
    }
    gravar(os.path.join(ASSETS, "recipes", "grid", k + ".json"), [rec])

    # ---------------- lang ----------------
    titulo = m["title"]
    desc = a["desc"]
    lang[f"block-{k}"] = titulo
    lang[f"block-{k}-*"] = titulo
    lang[f"blockdesc-{k}-*"] = desc + "\n\nMod de @mtnunes"
    lang[f"resumo-{k}"] = desc
    return {"chave": k, "titulo": titulo, "desc": desc, "cat": a.get("cat"), "receita": padrao, "letras": letras}


NOMES_ING = {
    "P": "tábua", "G": "engrenagem enferrujada", "F": "sílex", "S": "pedra (cascalho/cobblestone)", "K": "graveto",
    "I": "lingote de cobre", "R": "corda", "L": "vidro", "C": "barro", "H": "papel", "E": "couro", "M": "chapa de ferro",
    "N": "pregos e tiras de ferro", "B": "tijolo queimado", "T": "engrenagem temporal",
}

CATS = {"energia": "Energia", "bateria": "Baterias e postes", "maquina": "Máquinas"}


def capitulo_peca(info):
    grade = "<br>".join("<font color=\"#e0a64a\">[" + "][".join((c if c != " " else "  ") for c in linha.ljust(3)) + "]</font>"
                        for linha in info["receita"])
    legenda = "<br>".join(f"• <strong>{c}</strong> = {NOMES_ING[c]}" for c in info["letras"])
    texto = (f"<strong>{info['titulo']}</strong><br><br>{info['desc']}<br><br>"
             f"<strong>Como fazer</strong> (bancada de criação, 3x3):<br>{grade}<br><br>{legenda}")
    return {"Grupo": CATS.get(info["cat"], "Máquinas"), "Titulo": info["titulo"], "Texto": texto}


def main():
    lang = {
        "manual-titulo": "Manual da Automação",
        "manual-ganhou": "Você ganhou o <strong>Manual da Automação</strong>! Clique com o botão direito com ele na mão pra ler.",
        "item-manual": "Manual da Automação",
        "itemdesc-manual": "Tudo da Automação (como fazer cada máquina, energia, postes) e o guia dos primeiros 100 dias: inverno, tempestade temporal, comida, perigos e dicas de veterano. Clique direito pra ler.\n\nMod de @mtnunes",
        "itemgroup-automacao": "Automação",
        "girar-chave": "Girar",
        "girar-chave-info": "Gire com a chave inglesa",
        "bauzinho": "Bauzinho",
        "btn-ligar": "Ligar", "btn-desligar": "Desligar", "btn-pegartudo": "Pegar tudo",
        "btn-alcance": "Mostrar alcance", "btn-conexoes": "Ver conexões", "btn-ver": "Ver",
        "area": "Área: {0}x{0}", "dono": "Dono: {0}",
        "st-gerando": "Gerando {0} de energia por segundo",
        "st-fonte-parada": "Parada (sem água / vento / sol / chuva / combustível)",
        "st-fonte-semposte": "Sem Poste de Energia por perto! (geraria {0}/s)",
        "st-bateria": "Carga: {0} de {1} ({2}%)",
        "st-poste-ok": "Passando energia", "st-poste-sem": "Sem energia na rede",
        "st-desligada": "Desligada", "st-semposte": "Sem Poste de Energia por perto (8 blocos pra cada lado)",
        "st-trabalhando": "Trabalhando ({0}% de energia)", "st-semenergia": "Parada: falta energia na rede",
        "st-baucheio": "Bauzinho cheio", "st-esperando": "Esperando serviço",
        "info-poste": "Rede: gerando {0}/s, gastando {1}/s<br>Baterias: {2} de {3}<br>{4} poste(s), {5} peça(s) ligadas",
        "info-roda-semagua": "Precisa de água encostada (rio ou lago)",
        "info-gerador": "Queimando: uns {0} min de combustível", "info-gerador-vazio": "Coloque lenha, carvão ou tábua no bauzinho",
    }
    pecas = []
    for k, m in mods().items():
        pecas.append(gerar_bloco(k, m, lang))

    # Manual: guia escrito + um capítulo por peça
    guia = []
    p = os.path.join(HERE, "manual", "guia-pt-br.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            guia = json.load(f)
    ordem = {"energia": 0, "bateria": 1, "maquina": 2}
    caps = [x for x in guia if x.get("Grupo") == "Comece aqui"]
    caps += [capitulo_peca(i) for i in sorted(pecas, key=lambda i: (ordem.get(i["cat"], 3), i["titulo"]))]
    caps += [x for x in guia if x.get("Grupo") != "Comece aqui"]
    gravar(os.path.join(ASSETS, "config", "manual-pt-br.json"), caps)
    gravar(os.path.join(ASSETS, "config", "manual-en.json"), caps)

    # Item do manual + receita (papel + couro + graveto)
    gravar(os.path.join(ASSETS, "itemtypes", "manual.json"), {
        "code": "manual", "class": "ItemManualAutomacao", "maxstacksize": 1,
        "creativeinventory": {"general": ["*"], "items": ["*"]},
        "shape": {"base": "game:item/lore/book"},
        "textures": {"book": {"base": "game:item/lore/aged-orangebrown"}},
        "guiTransform": {"rotation": {"x": -30, "y": 40, "z": 0}, "origin": {"x": 0.5, "y": 0.1, "z": 0.5}, "scale": 2.4},
        "fpHandTransform": {"translation": {"x": 0, "y": 0.1, "z": 0.3}, "rotation": {"x": 0, "y": 90, "z": -20}, "scale": 1.8},
        "tpHandTransform": {"translation": {"x": -0.8, "y": -0.1, "z": -0.6}, "rotation": {"x": 0, "y": 90, "z": 0}, "scale": 0.7},
        "groundTransform": {"origin": {"x": 0.5, "y": 0, "z": 0.5}, "scale": 3},
    })
    gravar(os.path.join(ASSETS, "recipes", "grid", "manual.json"), [{
        "ingredientPattern": "HHE", "width": 3, "height": 1, "shapeless": True,
        "ingredients": {"H": {**ING["H"], "quantity": 1}, "E": {**ING["E"], "quantity": 1}},
        "output": {"type": "item", "code": "automacao:manual", "quantity": 1},
    }])

    # Falas e textos dos trabalhos (cada Trabalho .cs pode precisar de mais; ficam em lang-extra.json)
    import glob
    for extra in sorted(glob.glob(os.path.join(HERE, "manual", "lang-extra-*.json"))):
        with open(extra, encoding="utf-8") as f:
            lang.update(json.load(f))
    gravar(os.path.join(ASSETS, "lang", "pt-br.json"), lang)
    gravar(os.path.join(ASSETS, "lang", "en.json"), lang)
    print("ok:", len(pecas), "peças,", len(caps), "capítulos no manual")


if __name__ == "__main__":
    main()
