"""
Gera os modelos 3D dos mods novos (Moedor Automático, Espantalho Vigia e Defumador)
e o visualizador modelos-3d.html para aprovar antes de virar mod.

Unidades: 16 = 1 bloco. Cada modelo tem partes: a parada (base) e as que se mexem.
Uso: py -I gen_modelos.py <pasta de texturas do jogo (assets/survival/textures)>
"""
import base64
import copy
import json
import os
import sys

TEXTURES = {
    # Tudo velho e gasto, no estilo das ruínas e máquinas antigas do jogo
    "cobble": "game:block/stone/cobblestone/andesite2",
    "brick": "game:block/stone/agedbrick/andesite1",
    "planks": "game:block/wood/planks/aged1",
    "darkwood": "game:block/wood/debarked/aged",
    "mossy": "game:block/wood/debarked/mossy",
    "iron": "game:block/metal/tarnished/rivets3x3/rusty-iron",
    "darkiron": "game:block/metal/tarnished/sheet/rusty-iron2",
    "corroded": "game:block/metal/corroded/rusty3",
    "quern": "game:block/stone/polishedrock-old/full/andesite1",
    "grooves": "game:block/stone/polishedrock/andesite",
    "grindtop": "game:block/stone/polishedrock-old/full/andesite2",
    "rags": "game:block/cloth/rags/rag2",
    "burlap": "game:block/cloth/burlap/sides-stiches",
    "rope": "game:block/cloth/reedrope",
    "hay": "game:block/hay/aged-side",
    "haytop": "game:block/hay/aged-top",
    "coal": "game:block/coal/charcoal",
    "ember": "game:block/coal/ember",
    "glass": "game:block/glass/leaded-brown",
    "flame": "game:block/fire-orange",
    "raw": "game:item/food/meat/raw",
    "smoked": "game:item/food/meat/smoked",
    "fishraw": "game:item/food/meat/fish-cured",
    "fishsmoked": "game:item/food/meat/fish-smoked",
    "panwood": "game:block/wood-generic",
    "gravel": "game:block/stone/gravel/andesite",
    "moss": "game:block/plant/moss",
    "kilnwall": "game:block/clay/bloomery/aged/base",
    "kilnfront": "game:block/clay/bloomery/aged/front",
    "chimney": "game:block/clay/bloomery/aged/chimney",
    "fired": "game:block/clay/hardened/brown1",
    "logbark": "game:block/wood/firewood/aged/bark",
    "logend": "game:block/wood/firewood/aged/north",
    "leather": "game:block/leather/aged1",
    "stonewheel": "game:block/stone/polishedrock/andesite",
    "skep": "game:block/reed/beehive/hive-reed",
    "honeycomb": "game:block/reed/beehive/honeycomb",
    "wax": "game:block/reed/beehive/beeswax",
    "bronze": "game:block/metal/tarnished/copper",
    "paper": "game:block/cloth/paper/blank-small",
    "feather": "game:item/resource/feather",
    "brass": "game:block/metal/tarnished/brass",
    "net": "game:item/resource/netold",
    "bark": "game:block/wood/bark/oak",
    "capfield": "game:block/plant/mushroom/fieldmushroomcap",
    "stipefield": "game:block/plant/mushroom/fieldmushroomstipe",
    "pores": "game:block/plant/mushroom/fieldmushroompores",
    "capbolete": "game:block/plant/mushroom/boletecap",
    "stipebolete": "game:block/plant/mushroom/boletestipe",
    "shelf": "game:block/plant/mushroom/chickenofthewoods",
    "wool": "game:block/cloth/basic/black",
    "cape": "game:block/cloth/aged/purple/top",
    "purple": "game:block/cloth/basic/purple",
    "basketside": "game:block/reed/basket/aged-northsouth",
    "basketlid": "game:block/reed/basket/aged-lid",
    "blueberry": "game:item/food/fruit/blueberry",
    "blackberry": "game:item/food/fruit/blackberry",
    "skin": "game:block/stone/polishedrock/chalk",
    "rag1": "game:block/cloth/rags/rag1",
    "rag3": "game:block/cloth/rags/rag3",
    "rag4": "game:block/cloth/rags/rag4",
    "linen": "game:block/linen",
    "burlapplain": "game:block/cloth/burlap/sides",
    "temporal": "game:block/machine/statictranslocator/rustyglow",
    "orangeskin": "game:block/cloth/basic/orange",
    "greenhair": "game:block/cloth/basic/green",
    "overall": "game:block/cloth/basic/brown",
    "shirt": "game:block/cloth/basic/normal",
    "white": "game:block/cloth/basic/white",
    "straw": "game:block/hay/normal-side",
    "boot": "game:block/leather/aged1",
    "chestside": "game:block/wood/chest/aged/sides",
    "chestlid": "game:block/wood/chest/aged/lid",
    "chestcorner": "game:block/wood/chest/aged/corners",
    "pumpkin": "game:block/clay/hardened/orange",
    "pumpkintop": "game:block/clay/hardened/orange",
    "cabbage": "game:block/plant/crop/cabbage/cabbage",
    "red": "game:block/cloth/basic/red",
    "enamel": "game:block/clay/hardened/red2",
    "bread": "game:item/food/grain/speltbread",
    "cheese": "game:block/food/pie/fill-cheddar",
    "yellow": "game:block/cloth/basic/yellow",
    "gray": "game:block/cloth/basic/gray",
    "blue": "game:block/cloth/basic/blue",
    "flour": "game:block/food/grain/flax-pile",
    "water": "game:block/liquid/water",
    "fishfresh": "game:item/food/meat/fish-cured",
    "couro": "game:block/leather/plain",
    "telha_vermelha": "game:block/clay/shingles/red",
    "telha_marrom": "game:block/clay/shingles/brown",
    "telha_cinza": "game:block/clay/shingles/gray",
    "tabuinha": "game:block/wood/shingles/aged-side",
    "flyagaric": "game:block/plant/mushroom/flyagariccap",
    "flyagaricpores": "game:block/plant/mushroom/flyagaricpores",
    "flyagaricstipe": "game:block/plant/mushroom/flyagaricstipe",
    "boletepores": "game:block/plant/mushroom/boletepores",
    "chanterelle": "game:block/plant/mushroom/chanterelle",
}


def box(name, frm, to, tex, rot=None, origin=None, glow=0, faces=None):
    w = [to[i] - frm[i] for i in range(3)]

    def uv(a, b):
        return [0, 0, max(0.5, min(16, a)), max(0.5, min(16, b))]

    sizes = {"north": (w[0], w[1]), "south": (w[0], w[1]), "east": (w[2], w[1]),
             "west": (w[2], w[1]), "up": (w[0], w[2]), "down": (w[0], w[2])}
    fs = {}
    for n, (a, b) in sizes.items():
        t = (faces or {}).get(n, tex)
        f = {"texture": "#" + t, "uv": uv(a, b)}
        if glow:
            f["glow"] = glow
        fs[n] = f
    e = {"name": name, "from": list(frm), "to": list(to), "faces": fs}
    if rot:
        e["rotationOrigin"] = list(origin or [(frm[i] + to[i]) / 2 for i in range(3)])
        for axis, deg in rot.items():
            e["rotation" + axis.upper()] = deg
    return e


def mirror_x(e, name):
    """Cópia espelhada no eixo X (lado esquerdo <-> direito)."""
    m = json.loads(json.dumps(e))
    m["name"] = name
    m["from"][0], m["to"][0] = 16 - e["to"][0], 16 - e["from"][0]
    if "rotationOrigin" in m:
        m["rotationOrigin"][0] = 16 - e["rotationOrigin"][0]
        for k in ("rotationY", "rotationZ"):
            if k in m:
                m[k] = -m[k]
    return m


def mirrored(elements, side="esq", other="dir"):
    out = list(elements)
    for e in elements:
        if side in e["name"]:
            out.append(mirror_x(e, e["name"].replace(side, other)))
    return out


# =====================================================================
# KIT DA AUTOMAÇÃO — peças comuns de todas as máquinas elétricas (mesma "família"):
# energia = brilho azul temporal; cobre velho nos fios/bobinas; carcaça de ferro enferrujado.
# Os modelos ficam em auto_*.py (cada um exporta modelos(kit) -> {chave: modelo}).
# =====================================================================
TEXTURES.update({
    "cobre": "game:block/metal/tarnished/tarnished-copper",
    "bobina": "game:block/metal/sheet/copper1",
    "isolador": "game:block/clay/hardened/cream",
    "luz": "game:block/machine/statictranslocator/rustyglow",
    "carcaca": "game:block/metal/tarnished/rusty-iron1",
    "rebite": "game:block/metal/tarnished/iron-riveted1",
    "engrenagens": "game:block/machine/statictranslocator/statictranslocator_gearboxa",
    "canos": "game:block/machine/statictranslocator/statictranslocator_pipes",
    "vidro": "game:block/glass/quartz",
})


def terminal(x, y, z, nome="terminal"):
    """Borne de ligação (onde o fio de cobre encaixa): base de ferro, isolador de barro e pino de cobre.
    (x, y, z) = centro da base, apoiado em cima de uma superfície."""
    return [
        box(nome + "_base", [x - 1.25, y, z - 1.25], [x + 1.25, y + 0.75, z + 1.25], "darkiron"),
        box(nome + "_isolador", [x - 0.75, y + 0.75, z - 0.75], [x + 0.75, y + 2.25, z + 0.75], "isolador"),
        box(nome + "_saia", [x - 1, y + 1.5, z - 1], [x + 1, y + 1.85, z + 1], "isolador"),
        box(nome + "_pino", [x - 0.3, y + 2.25, z - 0.3], [x + 0.3, y + 3.25, z + 0.3], "cobre"),
    ]


def lampada(x, y, z, nome="lampada"):
    """Lampadinha de aviso (acende azul quando tem energia): bocal de latão + bulbo de textura 'luz'.
    No visualizador a textura 'luz' só brilha nos modos listados em auto['glow']."""
    return [
        box(nome + "_bocal", [x - 0.9, y, z - 0.9], [x + 0.9, y + 0.8, z + 0.9], "brass"),
        box(nome + "_bulbo", [x - 0.65, y + 0.8, z - 0.65], [x + 0.65, y + 2.1, z + 0.65], "luz"),
        box(nome + "_grade", [x - 0.75, y + 1.4, z - 0.75], [x + 0.75, y + 1.6, z + 0.75], "darkiron"),
    ]


def motor(cx, cy, cz, comp=6, raio=2.5, eixo="x", nome="motor"):
    """Motor elétrico enferrujado deitado no eixo X ou Z, centro (cx, cy, cz): carcaça octogonal,
    cinta de bobina de cobre, tampas rebitadas, pé. O eixo sai pelo lado + (leste ou sul).
    Devolve (carcaça parada, eixo+polia que giram em volta de (cx, cy, cz) no mesmo eixo)."""
    r, h = raio, comp / 2

    def p(a, l, c):
        # (ao longo do eixo, altura, de lado) -> x, y, z
        return [a, l, c] if eixo == "x" else [c, l, a]

    def bx(n, a0, a1, l0, l1, c0, c1, t, rot=None):
        f, tt = p(a0, l0, c0), p(a1, l1, c1)
        return box(n, f, tt, t, {("x" if eixo == "x" else "z"): rot} if rot else None, [cx, cy, cz] if rot else None)

    a, c = (cx, cz) if eixo == "x" else (cz, cx)
    caixa = [
        bx(nome + "_corpo", a - h, a + h, cy - r, cy + r, c - r * 0.6, c + r * 0.6, "carcaca"),
        bx(nome + "_corpo2", a - h + 0.06, a + h - 0.06, cy - r * 0.6, cy + r * 0.6, c - r, c + r, "carcaca"),
        bx(nome + "_bobina", a - h * 0.45, a + h * 0.45, cy - r - 0.15, cy + r + 0.15, c - r * 0.6 - 0.15, c + r * 0.6 + 0.15, "bobina"),
        bx(nome + "_tampa_a", a - h - 0.5, a - h, cy - r * 0.8, cy + r * 0.8, c - r * 0.8, c + r * 0.8, "rebite"),
        bx(nome + "_tampa_b", a + h, a + h + 0.5, cy - r * 0.8, cy + r * 0.8, c - r * 0.8, c + r * 0.8, "rebite"),
        bx(nome + "_pe", a - h + 0.5, a + h - 0.5, cy - r - 0.75, cy - r + 0.25, c - r * 0.9, c + r * 0.9, "darkiron"),
    ]
    gira = [
        bx(nome + "_eixo", a + h + 0.5, a + h + 2.5, cy - 0.5, cy + 0.5, c - 0.5, c + 0.5, "iron"),
        bx(nome + "_polia", a + h + 1.25, a + h + 2, cy - 1.25, cy + 1.25, c - 1.25, c + 1.25, "corroded"),
        bx(nome + "_polia2", a + h + 1.25, a + h + 2, cy - 1.25, cy + 1.25, c - 1.25, c + 1.25, "corroded", 45),
    ]
    return caixa, gira


def fio(a, b, nome="fio", grossura=0.5):
    """Fio de cobre reto entre dois pontos que diferem em 1 coordenada só."""
    g = grossura / 2
    frm = [min(a[i], b[i]) - (g if a[i] == b[i] else 0) for i in range(3)]
    to = [max(a[i], b[i]) + (g if a[i] == b[i] else 0) for i in range(3)]
    return box(nome, frm, to, "cobre")


def carregar_automacao():
    """Lê os auto_*.py (energia, baterias, máquinas) desta pasta. Cada um tem
    TEX = {...} (texturas extras, opcional) e modelos(kit) -> {chave: modelo com 'auto'}."""
    import glob
    import importlib.util
    import types
    kit = types.SimpleNamespace(box=box, mirrored=mirrored, mirror_x=mirror_x, water_wheel=water_wheel,
                                terminal=terminal, lampada=lampada, motor=motor, fio=fio, copy=copy)
    out = {}
    kit.prontos = out  # modelos já carregados (o auto_rede.py monta a cena com eles)
    here = os.path.dirname(os.path.abspath(__file__))
    for path in sorted(glob.glob(os.path.join(here, "auto_*.py"))):
        spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            TEXTURES.update(getattr(mod, "TEX", {}))
            out.update(mod.modelos(kit))
        except Exception as e:  # um arquivo quebrado não derruba os outros
            print("ERRO em", os.path.basename(path), "->", repr(e))
    return out


# =====================================================================
# 1) MOEDOR AUTOMÁTICO — mói sozinho com uma roda d'água na lateral
# =====================================================================
WHEEL = [17.5, 8, 8]   # centro da roda (fica pra fora do bloco, no lado leste, dentro da água)

moedor_base = [
    # Alicerce de pedra com cinta de ferro
    box("alicerce", [1, 0, 1], [15, 4, 15], "cobble"),
    box("borda", [0.5, 3.5, 0.5], [15.5, 4.5, 15.5], "brick"),
    box("cinta", [0.75, 1.5, 0.75], [15.25, 2.25, 15.25], "darkiron"),
    # Mó de baixo (parada)
    box("mo_baixo", [3, 4.5, 3], [13, 7, 13], "quern", faces={"up": "grooves"}),
    # Postes do quadro de madeira
    box("poste_esq_n", [1, 4.5, 1], [3, 15, 3], "darkwood"),
    box("poste_esq_s", [1, 4.5, 13], [3, 15, 15], "mossy"),
    box("viga_n", [1, 15, 1], [15, 16.5, 3], "darkwood"),
    box("viga_s", [1, 15, 13], [15, 16.5, 15], "darkwood"),
    box("viga_meio", [1, 15.25, 7], [15, 16.25, 9], "planks"),
    # Chapas de ferro nas juntas
    box("chapa_esq_n", [0.75, 13.5, 0.75], [3.25, 14.5, 3.25], "iron"),
    box("chapa_esq_s", [0.75, 13.5, 12.75], [3.25, 14.5, 15.25], "iron"),
    # Funil de madeira em cima (onde entra o grão/minério)
    box("funil", [5, 16.5, 5], [11, 19, 11], "planks"),
    box("funil_boca", [6.5, 15, 6.5], [9.5, 16.5, 9.5], "darkwood"),
    box("funil_aro", [4.75, 18.5, 4.75], [11.25, 19.25, 11.25], "corroded"),
    # Bica de saída na frente (sul), inclinada
    box("bica", [6, 5, 13], [10, 6, 17], "planks", {"x": 20}, [8, 6, 13]),
    box("bica_lado_esq", [5.5, 5, 13], [6, 7, 17], "darkwood", {"x": 20}, [8, 6, 13]),
    # Mancal do eixo na parede leste
    box("mancal", [14, 6.5, 6.5], [16, 9.5, 9.5], "darkiron"),
]
moedor_base = mirrored(moedor_base)

moedor_mo = [
    # Mó de cima (gira em volta do centro do bloco)
    box("mo_cima", [3.5, 7, 3.5], [12.5, 10, 12.5], "quern", faces={"up": "grindtop", "down": "grooves"}),
    box("eixo_mo", [7.25, 10, 7.25], [8.75, 15, 8.75], "iron"),
    # Engrenagem enferrujada deitada em cima da mó
    box("engrenagem", [5, 10, 5], [11, 11, 11], "corroded"),
    box("dente_n", [7.25, 10, 4.25], [8.75, 11, 5], "corroded"),
    box("dente_s", [7.25, 10, 11], [8.75, 11, 11.75], "corroded"),
    box("dente_o", [4.25, 10, 7.25], [5, 11, 8.75], "corroded"),
    box("dente_l", [11, 10, 7.25], [11.75, 11, 8.75], "corroded"),
    box("dente_no", [5, 10, 5], [6, 11, 6], "corroded", {"y": 45}),
    box("dente_ne", [10, 10, 5], [11, 11, 6], "corroded", {"y": 45}),
    box("dente_so", [5, 10, 10], [6, 11, 11], "corroded", {"y": 45}),
    box("dente_se", [10, 10, 10], [11, 11, 11], "corroded", {"y": 45}),
]

def water_wheel():
    """Roda d'água padrão das máquinas (Moedor e Peneira): mesma peça nas duas."""
    r = [
        # Eixo que atravessa a parede e engrenagem de pé que puxa a máquina
        box("eixo_roda", [13, 7.5, 7.5], [19.5, 8.5, 8.5], "darkwood"),
        box("engrenagem_pe", [13.1, 5, 5], [14, 11, 11], "corroded"),
        box("cubo", [16, 6.5, 6.5], [19, 9.5, 9.5], "darkiron"),
    ]
    # Dois aros (octógono), raios finos e pás entre os aros
    for k in range(8):
        a = 45 * k + 22.5
        r.append(box(f"aro_a{k}", [16.25, 13.5, 5.55], [16.75, 14.25, 10.45], "darkwood", {"x": a}, WHEEL))
        r.append(box(f"aro_b{k}", [18.25, 13.5, 5.55], [18.75, 14.25, 10.45], "mossy" if k % 2 else "darkwood", {"x": a}, WHEEL))
        r.append(box(f"pa{k}", [16.75, 12, 7.65], [18.25, 15.5, 8.35], "planks", {"x": 45 * k}, WHEEL))
    for k in range(4):
        r.append(box(f"raio_a{k}", [16.3, 9, 7.7], [16.7, 13.5, 8.3], "darkwood", {"x": 90 * k + 45}, WHEEL))
        r.append(box(f"raio_b{k}", [18.3, 9, 7.7], [18.7, 13.5, 8.3], "darkwood", {"x": 90 * k + 45}, WHEEL))
    return r


moedor_roda = water_wheel()

# =====================================================================
# 2) PENEIRA AUTOMÁTICA (refeita) — mesma família do Moedor: na beira do rio,
#    alicerce de pedra, mesma roda d'água; a peneira chacoalha em cima da gaiola
# =====================================================================
peneira_base = [
    # Alicerce de pedra com cinta de ferro (igual ao do Moedor, mais baixo)
    box("alicerce", [1, 0, 1], [15, 2, 15], "cobble"),
    box("borda", [0.5, 1.75, 0.5], [15.5, 2.5, 15.5], "brick"),
    box("cinta", [0.75, 0.75, 0.75], [15.25, 1.5, 15.25], "darkiron"),
    # Topo da gaiola
    box("viga_topo_n", [1, 12, 1], [15, 13.25, 2.25], "darkwood"),
    box("viga_topo_s", [1, 12, 13.75], [15, 13.25, 15], "darkwood"),
    box("viga_topo_o", [1, 12, 2.25], [2.25, 13.25, 13.75], "darkwood"),
    box("viga_topo_l", [13.75, 12, 2.25], [15, 13.25, 13.75], "mossy"),
    # Postes dos cantos com cintas de ferro
    box("poste_no", [1, 2.5, 1], [2.5, 13.25, 2.5], "darkwood"),
    box("poste_ne", [13.5, 2.5, 1], [15, 13.25, 2.5], "darkwood"),
    box("poste_so", [1, 2.5, 13.5], [2.5, 13.25, 15], "mossy"),
    box("poste_se", [13.5, 2.5, 13.5], [15, 13.25, 15], "darkwood"),
    box("cinta_no", [0.75, 7, 0.75], [2.75, 8, 2.75], "iron"),
    box("cinta_ne", [13.25, 7, 0.75], [15.25, 8, 2.75], "iron"),
    box("cinta_so", [0.75, 7, 13.25], [2.75, 8, 15.25], "iron"),
    box("cinta_se", [13.25, 7, 13.25], [15.25, 8, 15.25], "iron"),
    # Bauzinho dentro da gaiola, onde caem os achados
    box("bauzinho", [4.5, 2.5, 4.5], [11.5, 7, 11.5], "planks"),
    box("bauzinho_tampa", [4.25, 7, 4.25], [11.75, 7.75, 11.75], "darkwood"),
    box("bauzinho_cinta1", [4.25, 2.5, 6.5], [11.75, 7.25, 7.25], "darkiron"),
    box("bauzinho_cinta2", [4.25, 2.5, 8.75], [11.75, 7.25, 9.5], "darkiron"),
    box("bauzinho_trava", [7.25, 5.5, 11.5], [8.75, 7, 12], "corroded"),
    # Calha que leva o que cai da peneira para o bauzinho
    box("calha", [5, 10.5, 5], [11, 11, 11], "darkiron", {"x": 8}),
    box("calha_bico", [7, 7.75, 7], [9, 10.5, 9], "darkiron"),
    # Berço onde a peneira se apoia
    box("berco1", [2.25, 12.75, 4.5], [13.75, 13.5, 5.5], "iron"),
    box("berco2", [2.25, 12.75, 10.5], [13.75, 13.5, 11.5], "iron"),
    # Mancal do eixo na parede leste (mesma altura da roda do Moedor)
    box("mancal", [14, 6.5, 6.5], [16, 9.5, 9.5], "darkiron"),
    # Amarrações de corda e musgo
    box("corda_no", [0.75, 11.25, 0.75], [2.75, 12, 2.75], "rope"),
    box("corda_so", [0.75, 11.25, 13.25], [2.75, 12, 15.25], "rope"),
    box("musgo1", [2.5, 2.5, 2.5], [6, 2.75, 4.5], "moss"),
    box("musgo2", [10, 2.5, 11.5], [13.5, 2.75, 13.5], "moss"),
]
for i, x in enumerate([4, 6.5, 9, 11.5]):
    peneira_base.append(box(f"ripa_n{i}", [x, 2.5, 1.25], [x + 0.9, 12, 1.85], "planks"))
    peneira_base.append(box(f"ripa_s{i}", [x, 2.5, 14.15], [x + 0.9, 12, 14.75], "planks"))
for i, z in enumerate([4, 6.5, 9, 11.5]):
    peneira_base.append(box(f"ripa_o{i}", [1.25, 2.5, z], [1.85, 12, z + 0.9], "planks"))
peneira_base.append(box("ripa_torta", [11.5, 2.5, 14.15], [12.4, 8.5, 14.75], "planks", {"z": 12}, [12, 2.5, 14.5]))

peneira_pan = [
    box("peneira_fundo", [3.5, 13.5, 3.5], [12.5, 14.25, 12.5], "panwood"),
    box("peneira_borda_n", [3, 13.5, 3], [13, 15.5, 3.75], "panwood"),
    box("peneira_borda_s", [3, 13.5, 12.25], [13, 15.5, 13], "panwood"),
    box("peneira_borda_o", [3, 13.5, 3.75], [3.75, 15.5, 12.25], "panwood"),
    box("peneira_borda_l", [12.25, 13.5, 3.75], [13, 15.5, 12.25], "panwood"),
    box("cascalho", [3.75, 14.25, 3.75], [12.25, 14.9, 12.25], "gravel"),
    box("cascalho_monte", [6, 14.9, 6], [10, 15.4, 10], "gravel"),
    # Biela: liga a peneira à engrenagem da roda (é ela que chacoalha)
    box("biela", [13, 9.5, 7.5], [13.75, 14.5, 8.5], "corroded", {"z": -10}, [13.4, 14.5, 8]),
    box("alca_peneira", [13, 14.25, 7.25], [14.5, 15, 8.75], "darkwood"),
]

# =====================================================================
# 3) ESPANTALHO VIGIA — protege a horta, lanterna acende quando vê bicho
# =====================================================================
espantalho_base = [
    box("pe_pedra", [5, 0, 5], [11, 2, 11], "cobble"),
    box("cunha_n", [7, 0, 4], [9, 3, 5], "darkwood", {"x": -20}, [8, 0, 5]),
    box("cunha_s", [7, 0, 11], [9, 3, 12], "darkwood", {"x": 20}, [8, 0, 11]),
    box("poste", [7, 0, 7], [9, 13, 9], "darkwood"),
    box("amarra", [6.75, 2, 6.75], [9.25, 3, 9.25], "rope"),
]

espantalho_corpo = [
    # Continua o poste e a trave dos braços
    box("poste_cima", [7, 13, 7], [9, 27, 9], "darkwood"),
    box("trave", [-1.5, 19, 7.25], [17.5, 20.5, 8.75], "mossy"),
    # Camisa de pano velho com cinto de corda
    box("camisa", [4, 11, 5.5], [12, 21, 10.5], "rags"),
    box("cinto", [3.75, 13.5, 5.25], [12.25, 14.5, 10.75], "rope"),
    box("remendo", [8.5, 16, 10.5], [11, 18.5, 10.75], "burlap"),
    # Mangas e palha saindo
    box("manga_esq", [-1, 18.25, 6.25], [4, 21.25, 9.75], "rags"),
    box("palha_esq", [-2.5, 18.75, 6.75], [-1, 20.75, 9.25], "hay"),
    box("palha_baixo", [5, 9.5, 6.5], [11, 11, 9.5], "hay"),
    # Cabeça de saco com cara costurada
    box("pescoco", [5.5, 21, 5.5], [10.5, 21.75, 10.5], "rope"),
    box("cabeca", [5, 21.5, 5], [11, 27, 11], "burlap"),
    box("olho_esq", [6, 24, 10.9], [7.25, 25.25, 11.2], "coal"),
    box("boca", [6.25, 22.5, 10.9], [9.75, 23, 11.15], "rope"),
    # Chapéu de palha meio torto
    box("aba", [3, 27, 3], [13, 27.75, 13], "haytop", {"z": 6}, [8, 27, 8]),
    box("copa", [5.5, 27.75, 5.5], [10.5, 30, 10.5], "hay", {"z": 6}, [8, 27, 8]),
    box("fita", [5.25, 27.75, 5.25], [10.75, 28.5, 10.75], "rope", {"z": 6}, [8, 27, 8]),
    # Gancho da lanterna na ponta do braço direito
    box("gancho", [16.25, 18, 7.75], [17, 19, 8.25], "corroded"),
]
espantalho_corpo = mirrored(espantalho_corpo)

LANTERN_HOOK = [16.6, 18, 8]
espantalho_lanterna = [
    box("corrente", [16.35, 16.5, 7.75], [16.85, 18, 8.25], "corroded"),
    box("tampa_lanterna", [14.6, 15.75, 6.5], [18.6, 16.5, 9.5], "darkiron"),
    box("alca_lanterna", [16.1, 16.5, 7.5], [17.1, 17, 8.5], "iron"),
    box("vidro_lanterna", [15.1, 12, 7], [18.1, 15.75, 9], "glass"),
    box("chama", [16.1, 12.75, 7.5], [17.1, 14.5, 8.5], "flame", glow=200),
    box("fundo_lanterna", [14.6, 11.25, 6.5], [18.6, 12, 9.5], "darkiron"),
    box("grade_n", [14.85, 12, 6.75], [18.35, 15.75, 7], "corroded"),
]

# =====================================================================
# 5) DEFUMADOR — varal sobre brasa, carne/peixe pendurado defuma sozinho
# =====================================================================
defumador_base = [
    # Buraco de fogo com mureta de pedra
    box("mureta_n", [2, 0, 2], [14, 3, 4], "cobble"),
    box("mureta_s", [2, 0, 12], [14, 3, 14], "cobble"),
    box("mureta_esq", [2, 0, 4], [4, 3, 12], "brick"),
    box("tora1", [4.5, 1.25, 6], [11.5, 2.75, 7.5], "darkwood", {"y": 20}),
    box("tora2", [4.5, 1.25, 8.5], [11.5, 2.75, 10], "mossy", {"y": -25}),
    # Postes e travessas
    box("poste_esq_n", [0.5, 0, 0.5], [2, 23, 2], "darkwood"),
    box("poste_esq_s", [0.5, 0, 14], [2, 23, 15.5], "mossy"),
    box("travessa", [0.5, 21, 7.25], [15.5, 22.5, 8.75], "darkwood"),
    box("trava_n", [0.5, 22.5, 0.5], [15.5, 23.5, 2], "darkwood"),
    box("trava_s", [0.5, 22.5, 14], [15.5, 23.5, 15.5], "darkwood"),
    box("amarra_esq", [0.25, 20.5, 7], [2.25, 23, 9], "rope"),
    # Telhadinho de tábuas pra segurar a fumaça
    box("telhado_esq", [-1.05, 25.25, -0.5], [8.55, 26.25, 16.5], "planks", {"z": 28}, [3.75, 25.75, 8]),
    box("cumeeira", [7, 27.75, -0.75], [9, 28.75, 16.75], "mossy"),
    # Ganchos de ferro na travessa
    box("gancho1", [3.75, 18.5, 7.75], [4.25, 21, 8.25], "corroded"),
    box("gancho2", [7.75, 18.5, 7.75], [8.25, 21, 8.25], "corroded"),
    box("gancho3", [11.75, 18.5, 7.75], [12.25, 21, 8.25], "corroded"),
]
defumador_base = mirrored(defumador_base)
# A mureta do leste é a cópia da esquerda
defumador_brasa = [
    box("brasa", [4, 0, 4], [12, 1.25, 12], "ember", glow=120),
    box("brasa_cima", [5.5, 1.25, 5.5], [10.5, 1.75, 10.5], "ember", glow=150),
]
defumador_carga = [
    box("carne1", [2.5, 12, 7.25], [5.5, 18.5, 8.75], "raw", {"y": 15}),
    box("peixe2", [6.75, 11, 7.5], [9.25, 18.5, 8.5], "fishraw"),
    box("carne3", [10.5, 13, 7.25], [13.5, 18.5, 8.75], "raw", {"y": -10}),
]


# =====================================================================
# CARVOEIRA — forno de barro: põe lenha, fecha a porta, sai carvão
# =====================================================================
carvoeira_base = [
    box("alicerce", [0.5, 0, 0.5], [15.5, 2, 15.5], "cobble"),
    box("borda", [0.25, 1.5, 0.25], [15.75, 2.25, 15.75], "brick"),
    # Cúpula de barro em degraus
    box("parede1", [1, 2, 1], [15, 7, 15], "kilnwall"),
    box("parede2", [2, 7, 2], [14, 10, 14], "kilnwall"),
    box("parede3", [3.5, 10, 3.5], [12.5, 12, 12.5], "fired"),
    box("topo", [5, 12, 5], [11, 13, 11], "fired"),
    # Cintas de ferro segurando o barro
    box("cinta1", [0.75, 4, 0.75], [15.25, 5, 15.25], "darkiron"),
    box("cinta2", [1.75, 8.25, 1.75], [14.25, 9, 14.25], "corroded"),
    # Chaminé
    box("chamine", [6.5, 13, 6.5], [9.5, 17, 9.5], "chimney"),
    box("chamine_aro", [6.25, 16.5, 6.25], [9.75, 17.25, 9.75], "corroded"),
    # Boca do forno na frente (sul) e respiros nas laterais
    box("boca", [4.5, 2.5, 14.9], [11.5, 8, 15.1], "kilnfront"),
    box("moldura_boca", [4, 8, 14.75], [12, 8.75, 15.25], "darkiron"),
    box("respiro_esq", [0.85, 5.25, 7], [1.1, 6.25, 9], "corroded"),
    # Lenha empilhada encostada do lado
    box("lenha_esq1", [0.25, 2.25, 11.5], [1.75, 3.75, 15.5], "logbark", faces={"north": "logend", "south": "logend"}),
]
carvoeira_base = mirrored(carvoeira_base)

carvoeira_brasa = [
    box("brasa", [5, 2.5, 14.8], [11, 4, 15], "ember", glow=150),
    box("brasa_cima", [6, 4, 14.8], [10, 5, 15], "ember", glow=120),
]

carvoeira_porta = [
    box("porta", [4.5, 2.5, 15.25], [11.5, 8, 15.75], "darkiron"),
    box("rebite_porta", [4.75, 6.75, 15.75], [11.25, 7.25, 15.9], "iron"),
    box("macaneta", [10, 4.75, 15.75], [10.75, 5.5, 16.5], "iron"),
    box("dobradica", [4.25, 3, 15.2], [4.75, 7.5, 15.8], "corroded"),
]

# =====================================================================
# BANCADA DE REMENDOS — conserta ferramentas e armaduras gastas
# =====================================================================
bancada_base = [
    box("tampo", [0, 11, 2], [16, 13, 14], "planks"),
    box("perna_esq_n", [1, 0, 3], [3, 11, 5], "darkwood"),
    box("perna_esq_s", [1, 0, 11], [3, 11, 13], "mossy"),
    box("travessa_n", [1, 3, 3.5], [15, 4, 4.5], "darkwood"),
    box("travessa_s", [1, 3, 11.5], [15, 4, 12.5], "darkwood"),
    box("prateleira", [3, 4, 4.5], [13, 4.75, 11.5], "planks"),
    box("couro", [4, 4.75, 5], [9, 5.25, 10], "leather"),
    box("cinta_tampo", [-0.1, 11.5, 1.9], [16.1, 12.25, 14.1], "darkiron"),
    # Morsa (torno de bancada) à esquerda
    box("morsa_base", [1.5, 13, 5], [4.5, 14, 9], "corroded"),
    box("morsa_mand1", [1.5, 14, 5], [2.5, 16, 9], "iron"),
    box("morsa_mand2", [3.5, 14, 5], [4.5, 16, 9], "iron"),
    box("morsa_rosca", [2.75, 14.75, 9], [3.25, 15.25, 11.5], "darkiron"),
    box("morsa_cabo", [1.75, 14.75, 11.25], [4.25, 15.25, 11.75], "darkwood"),
    # Bigorninha no meio
    box("bigorna_pe", [6.5, 13, 6], [9.5, 14, 10], "darkiron"),
    box("bigorna", [6, 14, 5.5], [10, 15.5, 10.5], "iron"),
    box("bigorna_bico", [10, 14.5, 7.25], [11.5, 15.25, 8.75], "iron"),
    # Suportes do rebolo à direita
    box("suporte_rebolo_n", [13, 13, 5.25], [14, 17.5, 5.75], "darkwood"),
    box("suporte_rebolo_s", [13, 13, 10.25], [14, 17.5, 10.75], "darkwood"),
    # Painel de trás com ferramentas penduradas
    box("painel", [0, 13, 1.5], [16, 21, 2], "planks"),
    box("painel_viga", [0, 20.5, 1.25], [16, 21.5, 2.25], "darkwood"),
    box("martelo_cabo", [3, 14.5, 2], [3.75, 19, 2.5], "darkwood"),
    box("martelo_cabeca", [2.25, 18.5, 2], [4.5, 19.75, 2.75], "iron"),
    box("tenaz1", [6, 15.5, 2], [6.5, 19.5, 2.4], "corroded", {"z": 6}),
    box("tenaz2", [6.75, 15.5, 2], [7.25, 19.5, 2.4], "corroded", {"z": -6}),
    box("lima", [9, 14.5, 2], [9.5, 19, 2.4], "darkiron"),
    box("rolo_couro", [10.5, 15, 2], [13.5, 17, 4], "leather"),
]
bancada_base = mirrored(bancada_base)

REBOLO = [13.5, 17, 8]
bancada_rebolo = [
    box("rebolo", [11.5, 15, 6.5], [15.5, 19, 9.5], "stonewheel"),
    box("rebolo_b", [11.5, 15, 6.5], [15.5, 19, 9.5], "stonewheel", {"z": 45}, REBOLO),
    box("eixo_rebolo", [13.25, 16.75, 5], [13.75, 17.25, 11], "iron"),
    box("manivela", [13.25, 16.75, 4.5], [15, 17.25, 5], "corroded"),
]

# =====================================================================
# COLMEIA COLETORA — colmeia de palha em cima de uma bandeja com gaveta
# =====================================================================
colmeia_base = [
    box("perna_esq_n", [1.5, 0, 1.5], [3, 6, 3], "darkwood"),
    box("perna_esq_s", [1.5, 0, 13], [3, 6, 14.5], "mossy"),
    box("fundo_bandeja", [1, 5, 1], [15, 6, 15], "planks"),
    box("parede_n", [1, 6, 1], [15, 8, 1.75], "planks"),
    box("parede_esq", [1, 6, 1.75], [1.75, 8, 14.25], "darkwood"),
    box("gaveta", [1, 5.5, 14.25], [15, 8, 15], "darkwood"),
    box("puxador", [7, 6.25, 15], [9, 6.75, 15.75], "iron"),
    box("cinta_bandeja", [0.75, 6.5, 0.75], [15.25, 7, 15.25], "corroded"),
    # Colmeia de palha (cesto em degraus), mais pra trás pra mostrar o favo na frente
    box("cesto1", [2, 8, 1.75], [14, 11, 12.25], "skep"),
    box("cesto2", [3, 11, 2.75], [13, 13.5, 11.25], "skep"),
    box("cesto3", [4, 13.5, 3.75], [12, 15.5, 10.25], "skep"),
    box("cesto4", [5.5, 15.5, 5.25], [10.5, 16.5, 8.75], "skep"),
    box("pegador", [7, 16.5, 6], [9, 17.25, 8], "darkwood"),
    box("amarra1", [1.9, 10, 1.65], [14.1, 10.5, 12.35], "rope"),
    box("amarra2", [2.9, 13, 2.65], [13.1, 13.5, 11.35], "rope"),
    box("entrada", [7, 8, 12.2], [9, 9.5, 12.4], "coal"),
    box("tabua_pouso", [6.5, 8, 12.25], [9.5, 8.25, 13.5], "planks"),
]
colmeia_base = mirrored(colmeia_base)

colmeia_mel = [
    box("favo1", [2, 7, 12.75], [8, 7.75, 14.25], "honeycomb"),
    box("favo2", [8.25, 7, 12.75], [13.5, 7.6, 14.25], "honeycomb", {"y": 4}),
    box("cera", [10, 7.5, 13], [12.5, 8.5, 14], "wax"),
]


# =====================================================================
# SERRARIA D'ÁGUA — mesma família do Moedor: tora no funil, sai tábua
# =====================================================================
serraria_base = [
    box("alicerce", [1, 0, 1], [15, 4, 15], "cobble"),
    box("borda", [0.5, 3.5, 0.5], [15.5, 4.5, 15.5], "brick"),
    box("cinta", [0.75, 1.5, 0.75], [15.25, 2.25, 15.25], "darkiron"),
    box("poste_esq_n", [1, 4.5, 1], [3, 9, 3], "darkwood"),
    box("poste_esq_s", [1, 4.5, 13], [3, 9, 15], "mossy"),
    # Mesa com a fenda da serra no meio
    box("mesa_esq", [1, 9, 1], [7.5, 10, 15], "planks"),
    box("guia", [2, 10, 1], [2.75, 11.25, 15], "darkiron"),
    box("chapa_mesa_esq", [1, 9.75, 0.75], [7.5, 10.25, 1.25], "corroded"),
    # Tábuas prontas empilhadas do lado
    box("tabuas1", [10, 10, 11.5], [14.5, 10.75, 14.5], "planks"),
    box("tabuas2", [10.25, 10.75, 11.75], [14.25, 11.5, 14.25], "planks", {"y": 6}),
    # Mancal do eixo na parede leste
    box("mancal", [14, 6.5, 6.5], [16, 9.5, 9.5], "darkiron"),
    # Serragem no chão
    box("serragem", [5, 4.5, 4], [11, 4.75, 12], "haytop"),
]
serraria_base = mirrored(serraria_base)
# A guia e as tábuas só de um lado: remove as cópias espelhadas que não fazem sentido
serraria_base = [e for e in serraria_base if e["name"] not in ("guia_dir",)]

SERRA = [8, 8, 8]
serraria_serra = [
    box("disco", [7.75, 3.5, 3.5], [8.25, 12.5, 12.5], "iron"),
    box("disco_b", [7.75, 3.5, 3.5], [8.25, 12.5, 12.5], "iron", {"x": 45}, SERRA),
    box("eixo_serra", [6.5, 7.5, 7.5], [13, 8.5, 8.5], "darkwood"),
    box("cubo_serra", [7.25, 7, 7], [8.75, 9, 9], "corroded"),
]
for k in range(8):
    serraria_serra.append(box(f"dente{k}", [7.8, 12.5, 7.4], [8.2, 13.4, 8.6], "corroded", {"x": 45 * k + 22.5}, SERRA))

serraria_tora = [
    box("tora", [5.5, 10, -1], [10.5, 14, 6.5], "logbark", faces={"north": "logend", "south": "logend"}),
]

# =====================================================================
# SINO DE ALARME — toca sozinho quando chega drifter ou bicho bravo
# =====================================================================
sino_base = [
    box("pe_pedra", [4, 0, 4], [12, 2, 12], "cobble"),
    box("pe_borda", [3.75, 1.5, 3.75], [12.25, 2.25, 12.25], "brick"),
    box("poste", [7, 0, 7], [9, 28, 9], "darkwood"),
    box("cinta_poste1", [6.75, 6, 6.75], [9.25, 7, 9.25], "darkiron"),
    box("cinta_poste2", [6.75, 20, 6.75], [9.25, 21, 9.25], "corroded"),
    box("braco", [7, 24.5, 7.25], [15, 26, 8.75], "darkwood"),
    box("mao_francesa", [8.75, 21.5, 7.5], [9.75, 25, 8.5], "mossy", {"z": -45}, [9.25, 21.5, 8]),
    box("gancho_sino", [12.25, 23.5, 7.75], [12.75, 24.5, 8.25], "corroded"),
    # Telhadinho em cima do sino
    box("telhado", [9.5, 26.5, 4.5], [16, 27.25, 11.5], "planks", {"z": -12}, [12.75, 26.75, 8]),
    box("telhado_viga", [9.5, 27, 7.5], [16, 27.75, 8.5], "mossy", {"z": -12}, [12.75, 26.75, 8]),
    # Plaquinha de aviso
    box("placa", [5.5, 12, 9], [10.5, 15, 9.4], "planks"),
    box("placa_tinta", [6.25, 13, 9.4], [9.75, 14, 9.5], "corroded"),
]

SINO = [12.5, 24, 8]
sino_sino = [
    box("canga", [11.5, 23, 7.5], [13.5, 24, 8.5], "darkwood"),
    box("sino_topo", [11.75, 21.25, 6.75], [13.25, 23, 9.25], "bronze"),
    box("sino_meio", [11.25, 19.5, 6.25], [13.75, 21.25, 9.75], "bronze"),
    box("sino_boca", [10.75, 18.5, 5.75], [14.25, 19.5, 10.25], "bronze"),
    box("faixa_sino", [11.2, 20.75, 6.2], [13.8, 21.25, 9.8], "corroded"),
    box("badalo", [12.25, 17.5, 7.75], [12.75, 19.25, 8.25], "iron"),
    box("corda_sino", [12.4, 9, 7.9], [12.6, 17.5, 8.1], "rope"),
    box("puxador_corda", [12.25, 8.25, 7.75], [12.75, 9, 8.25], "darkwood"),
]


# =====================================================================
# ARMAZÉM CENTRAL (modelo próprio) — armário de registro velho:
# gavetinhas etiquetadas, livro de contas aberto e canos que "puxam" dos baús
# =====================================================================
armazem_base = [
    # Pés e corpo do armário
    box("pe_esq_n", [1, 0, 2], [3, 2, 4], "darkwood"),
    box("pe_esq_s", [1, 0, 12], [3, 2, 14], "mossy"),
    box("corpo", [1, 2, 2], [15, 13, 14], "planks"),
    box("rodape", [0.5, 2, 1.5], [15.5, 3, 14.5], "darkwood"),
    box("tampo", [0.5, 13, 1.5], [15.5, 14, 14.5], "darkwood"),
    box("cinta_esq", [0.75, 2, 13.75], [1.5, 13, 14.75], "darkiron"),
    box("cinta_tampo", [0.4, 12.25, 1.4], [15.6, 12.75, 14.6], "corroded"),
    # Tampo inclinado com o livro de contas aberto
    box("apoio_livro", [1.5, 14, 3], [14.5, 15, 13], "darkwood", {"x": 15}, [8, 14, 8]),
    box("capa_livro", [2.5, 15, 4.5], [13.5, 15.3, 11.5], "leather", {"x": 15}, [8, 14, 8]),
    box("pagina_esq", [3, 15.3, 5], [7.9, 15.7, 11], "paper", {"x": 15}, [8, 14, 8]),
    box("pagina_dir", [8.1, 15.3, 5], [13, 15.7, 11], "paper", {"x": 15}, [8, 14, 8]),
    box("fita_livro", [7.75, 15.25, 10.5], [8.25, 15.35, 13], "rags", {"x": 15}, [8, 14, 8]),
    # Tinteiro e pena
    box("tinteiro", [12, 14, 12.75], [13.5, 15.25, 14.25], "darkiron"),
    box("pena", [12.6, 15, 13.35], [12.9, 19, 13.65], "feather", {"z": 15}, [12.75, 15, 13.5]),
    # Canos enferrujados atrás, descendo pro chão (puxam dos baús)
    box("cano_esq", [3, 0, 0], [5, 12, 2], "corroded"),
    box("flange_esq", [2.75, 6, -0.25], [5.25, 6.75, 2.25], "brass"),
    box("cano_meio", [10.5, 0, 0], [12.5, 9, 2], "darkiron"),
    box("flange_meio", [10.25, 4, -0.25], [12.75, 4.75, 2.25], "brass"),
    box("joelho_meio", [10.5, 9, 0.5], [12.5, 11, 2], "corroded"),
    # Manômetro de latão do lado
    box("manometro", [15, 8, 6], [15.75, 10.5, 8.5], "brass"),
    box("visor", [15.75, 8.5, 6.5], [15.85, 10, 8], "glass"),
]
# Gavetinhas 3x3 na frente
for r, y in enumerate([3.5, 6.75, 10]):
    for c, x in enumerate([1.75, 6, 10.25]):
        armazem_base.append(box(f"gaveta{r}{c}", [x, y, 14], [x + 4, y + 2.75, 14.5], "darkwood"))
        armazem_base.append(box(f"puxador{r}{c}", [x + 1.5, y + 0.6, 14.5], [x + 2.5, y + 1.2, 15], "iron"))
        armazem_base.append(box(f"etiqueta{r}{c}", [x + 0.75, y + 1.6, 14.5], [x + 3.25, y + 2.35, 14.55], "paper"))
armazem_base = mirrored(armazem_base)



# =====================================================================
# PESCA AUTOMÁTICA — roda de pesca: a correnteza gira a roda, os cestos
# pegam os peixes e despejam na calha que leva até a caixa
# =====================================================================
def fish_wheel():
    """Roda de pesca: sem aros (silhueta limpa), 3 braços duplos com cestos-concha
    abertos pra frente (pegam o peixe) e 3 pás entre eles (a correnteza empurra)."""
    r = [
        box("eixo_roda", [13, 7.5, 7.5], [19.5, 8.5, 8.5], "darkwood"),
        box("engrenagem_pe", [13.1, 5, 5], [14, 11, 11], "corroded"),
        box("cubo", [15.75, 6.5, 6.5], [19.25, 9.5, 9.5], "darkiron"),
        box("cubo_aro_a", [15.6, 6.25, 6.25], [16, 9.75, 9.75], "corroded"),
        box("cubo_aro_b", [19, 6.25, 6.25], [19.4, 9.75, 9.75], "corroded"),
    ]
    for k in range(3):
        a = 120 * k
        rot = {"x": a}
        # Braços duplos
        r.append(box(f"braco_a{k}", [16.1, 9.5, 7.6], [16.6, 13.5, 8.4], "darkwood", rot, WHEEL))
        r.append(box(f"braco_b{k}", [18.4, 9.5, 7.6], [18.9, 13.5, 8.4], "darkwood", rot, WHEEL))
        # Cesto-concha: fundo (lado de fora), duas laterais e costas; aberto pra frente (+z)
        r.append(box(f"cesto_fundo{k}", [16, 16, 5.75], [19, 16.5, 10.25], "skep", rot, WHEEL))
        r.append(box(f"cesto_lado_a{k}", [16, 13.5, 5.75], [16.5, 16, 10.25], "skep", rot, WHEEL))
        r.append(box(f"cesto_lado_b{k}", [18.5, 13.5, 5.75], [19, 16, 10.25], "skep", rot, WHEEL))
        r.append(box(f"cesto_costas{k}", [16.5, 13.5, 5.75], [18.5, 16, 6.25], "skep", rot, WHEEL))
        r.append(box(f"cesto_borda{k}", [15.9, 15.75, 10], [19.1, 16.6, 10.5], "darkwood", rot, WHEEL))
        # Pá entre os cestos
        r.append(box(f"pa{k}", [16.6, 10, 7.7], [18.4, 15.25, 8.3], "planks", {"x": a + 60}, WHEEL))
        r.append(box(f"pa_ponta{k}", [16.4, 14.75, 7.55], [18.6, 15.5, 8.45], "corroded", {"x": a + 60}, WHEEL))
    # Um peixe no cesto de cima
    r.append(box("peixe_cesto", [16.75, 15.25, 6.75], [18.25, 16, 9.5], "fishraw"))
    return r


pesca_base = [
    # Pé de pedra e deque de tábuas com frestas
    box("alicerce", [0.5, 0, 0.5], [15.5, 2, 15.5], "cobble"),
    box("borda", [0.25, 1.75, 0.25], [15.75, 2.5, 15.75], "brick"),
    box("cinta", [0.4, 0.75, 0.4], [15.6, 1.4, 15.6], "darkiron"),
]
for i in range(6):
    x0 = 0.75 + i * 2.5
    pesca_base.append(box(f"tabua_deque{i}", [x0, 2.5, 0.75], [x0 + 2.25, 3.25, 15.25], "mossy" if i == 4 else "planks"))
pesca_base += [
    # Caixote de ripas (dá pra ver os peixes pelas frestas)
    box("caixote_fundo", [1.75, 3.25, 3.25], [9.25, 3.75, 12.75], "darkwood"),
    box("canto_no", [1.5, 3.25, 3], [2.5, 10, 4], "darkwood"),
    box("canto_ne", [8.5, 3.25, 3], [9.5, 10, 4], "darkwood"),
    box("canto_so", [1.5, 3.25, 12], [2.5, 10, 13], "darkwood"),
    box("canto_se", [8.5, 3.25, 12], [9.5, 10, 13], "darkwood"),
]
for j, y in enumerate([4, 6.25, 8.5]):
    pesca_base += [
        box(f"ripa_n{j}", [2.5, y, 3.1], [8.5, y + 1.25, 3.6], "planks"),
        box(f"ripa_s{j}", [2.5, y, 12.4], [8.5, y + 1.25, 12.9], "planks"),
        box(f"ripa_o{j}", [1.6, y, 4], [2.1, y + 1.25, 12], "planks"),
        box(f"ripa_l{j}", [8.9, y, 4], [9.4, y + 1.25, 12], "planks"),
    ]
pesca_base += [
    box("aro_caixote_n", [1.4, 9.75, 2.9], [9.6, 10.25, 3.7], "darkiron"),
    box("aro_caixote_s", [1.4, 9.75, 12.3], [9.6, 10.25, 13.1], "darkiron"),
    box("alca_o", [1.1, 6.5, 6.5], [1.6, 7.1, 9.5], "rope"),
    box("alca_l", [9.4, 6.5, 6.5], [9.9, 7.1, 9.5], "rope"),
    # Peixes dentro do caixote (só aparecem quando tem algo no bauzinho)
    box("peixes", [2.25, 3.75, 3.75], [8.75, 5.25, 12.25], "fishsmoked"),
    box("peixes_monte", [3, 5.25, 5], [8, 6.5, 11], "fishraw"),
    # Calha: desce do alto da roda até a boca do caixote, apoiada num poste
    box("calha_fundo", [5.9, 14.25, 6.75], [15.5, 14.75, 9.25], "planks", {"z": 28}, [15.5, 14.5, 8]),
    box("calha_lado_n", [5.9, 14.75, 6.5], [15.5, 15.75, 6.75], "darkwood", {"z": 28}, [15.5, 14.5, 8]),
    box("calha_lado_s", [5.9, 14.75, 9.25], [15.5, 15.75, 9.5], "darkwood", {"z": 28}, [15.5, 14.5, 8]),
    box("poste_calha", [11.5, 3.25, 7.5], [12.5, 12.4, 8.5], "darkwood"),
    box("pe_poste_calha", [11, 3.25, 7], [13, 4, 9], "corroded"),
    # Apoio do eixo da roda
    box("poste_mancal", [14.25, 3.25, 7], [15.75, 6.5, 9], "darkwood"),
    box("mancal", [14, 6.5, 6.5], [16, 9.5, 9.5], "darkiron"),
    # Balde com rabo de peixe saindo
    box("balde", [11, 3.25, 11.5], [14, 6.25, 14.5], "planks"),
    box("balde_cinta1", [10.9, 3.75, 11.4], [14.1, 4.25, 14.6], "darkiron"),
    box("balde_cinta2", [10.9, 5.5, 11.4], [14.1, 6, 14.6], "darkiron"),
    box("rabo_peixe", [12, 6.25, 12.5], [12.75, 8, 13.5], "fishraw", {"z": 15}, [12.4, 6.25, 13]),
    # Rolo de corda e vara de pescar encostada
    box("rolo_corda", [11, 3.25, 1.5], [14, 3.75, 4.5], "rope"),
    box("rolo_corda2", [11.5, 3.75, 2], [13.5, 4.25, 4], "rope"),
    box("vara", [2, 3.25, 14], [2.5, 18, 14.5], "darkwood", {"x": 20, "z": 12}, [2.25, 3.25, 14.25]),
    box("molinete", [1.75, 6, 14.25], [2.75, 7, 15], "corroded", {"x": 20, "z": 12}, [2.25, 3.25, 14.25]),
]


# =====================================================================
# TRONCO DE COGUMELOS — tora velha semeada: solta cogumelos numa bandejinha
# =====================================================================
cogumelo_base = [
    # Pedras que seguram a tora
    box("pedra_esq", [1, 0, 4], [4.5, 2.5, 12], "cobble"),
    box("pedra_dir", [11.5, 0, 4], [15, 2.5, 12], "brick"),
    # Tora deitada (casca nas laterais, anéis nas pontas)
    box("tora", [0, 3.5, 4.5], [16, 8, 11.5], "bark", faces={"east": "logend", "west": "logend"}),
    box("tora_cima", [0, 8, 5.5], [16, 9, 10.5], "bark", faces={"east": "logend", "west": "logend"}),
    box("tora_baixo", [0, 2.5, 5.5], [16, 3.5, 10.5], "bark", faces={"east": "logend", "west": "logend"}),
    # Amarras de corda
    box("amarra_esq", [4.5, 3.4, 4.35], [5.25, 8.1, 11.65], "rope"),
    box("amarra_esq_cima", [4.5, 8, 5.4], [5.25, 9.1, 10.6], "rope"),
    box("amarra_dir", [10.75, 3.4, 4.35], [11.5, 8.1, 11.65], "rope"),
    box("amarra_dir_cima", [10.75, 8, 5.4], [11.5, 9.1, 10.6], "rope"),
    # Musgo crescendo na tora
    box("musgo_cima1", [1, 9, 5.75], [4.5, 9.2, 9], "moss"),
    box("musgo_cima2", [12, 9, 7], [15.5, 9.2, 10.25], "moss"),
    box("musgo_lado", [1.5, 3, 4.4], [7, 6, 4.5], "moss"),
    # Furinhos onde os cogumelos foram semeados
    box("furo1", [2, 9, 9.25], [2.75, 9.1, 10], "coal"),
    box("furo2", [7.5, 9, 5.75], [8.25, 9.1, 6.5], "coal"),
    box("furo3", [13, 9, 5.75], [13.75, 9.1, 6.5], "coal"),
    # Bandejinha na frente, onde caem os cogumelos colhidos
    box("bandeja_fundo", [2, 0, 12.25], [14, 0.75, 15.75], "planks"),
    box("bandeja_frente", [2, 0.75, 15.25], [14, 2.25, 15.75], "darkwood"),
    box("bandeja_lado_esq", [2, 0.75, 12.25], [2.5, 2.25, 15.25], "darkwood"),
    box("bandeja_lado_dir", [13.5, 0.75, 12.25], [14, 2.25, 15.25], "darkwood"),
    box("bandeja_tras", [2.5, 0.75, 12.25], [13.5, 1.75, 12.75], "darkwood"),
]

cogumelo_cogumelos = [
    # Cogumelos do campo em cima da tora
    box("cog1_pe", [4.5, 9, 7], [5.5, 10.75, 8], "stipefield"),
    box("cog1_chapeu", [3.25, 10.75, 5.75], [6.75, 11.75, 9.25], "capfield", faces={"down": "pores"}),
    box("cog2_pe", [6.75, 9, 8.75], [7.5, 10.25, 9.5], "stipefield"),
    box("cog2_chapeu", [5.9, 10.25, 7.9], [8.35, 11, 10.35], "capfield", faces={"down": "pores"}),
    # Boleto mais gordo
    box("cog3_pe", [9.25, 9, 6.25], [10.75, 11.25, 7.75], "stipebolete"),
    box("cog3_chapeu", [8, 11.25, 5], [12, 12.75, 9], "capbolete", faces={"down": "pores"}),
    # Orelhas de pau na lateral da tora
    box("orelha1", [6.5, 4, 11.5], [10, 4.75, 13], "shelf"),
    box("orelha2", [7.5, 5.5, 11.5], [10.5, 6.25, 12.75], "shelf"),
    box("orelha3", [6, 6.9, 11.5], [8.25, 7.5, 12.4], "shelf"),
]

cogumelo_bandeja = [
    box("colhido1", [3, 0.75, 12.75], [6.25, 1.9, 14.75], "capbolete"),
    box("colhido2", [6.75, 0.75, 13], [9.25, 1.5, 15], "capfield"),
    box("colhido3", [9.75, 0.75, 12.9], [12.75, 1.6, 14.9], "capfield", {"y": 20}),
]


# =====================================================================
# BRUXA COLHEDORA — espantalho-bruxa que colhe frutinhas e a horta numa área
# =====================================================================
bruxa_base = [
    box("pe_pedra", [5, 0, 5], [11, 2, 11], "cobble"),
    box("pe_borda", [4.75, 1.5, 4.75], [11.25, 2.25, 11.25], "brick"),
    box("poste", [7, 0, 7], [9, 7, 9], "darkwood"),
    box("amarra", [6.75, 2, 6.75], [9.25, 3, 9.25], "rope"),
]

bruxa_corpo = [
    box("poste_cima", [7, 7, 7], [9, 27, 9], "darkwood"),
    box("trave", [-0.5, 19, 7.25], [16.5, 20.5, 8.75], "mossy"),
    # Vestido longo escuro, com a barra mais larga
    box("vestido", [4, 7, 5], [12, 20, 11], "wool"),
    box("barra", [3.5, 6, 4.5], [12.5, 8.5, 11.5], "wool"),
    box("barra_rasgada", [4.5, 5.25, 4.4], [6, 6, 5], "wool"),
    box("cinto", [3.75, 13.5, 4.75], [12.25, 14.5, 11.25], "rope"),
    box("fivela", [7.25, 13.25, 4.5], [8.75, 14.75, 4.8], "corroded"),
    # Capa roxa velha nas costas e nos ombros
    box("capa", [3.5, 8, 10.75], [12.5, 21, 11.6], "cape"),
    box("capa_ombros", [3.25, 19.5, 4.75], [12.75, 21.5, 11.6], "cape"),
    # Mangas e mãos de palha
    box("manga_esq", [0.5, 18.25, 6.25], [4, 21.25, 9.75], "wool"),
    box("mao_esq", [-0.75, 18.75, 6.75], [0.5, 20.75, 9.25], "hay"),
    box("manga_dir", [12, 18.25, 6.25], [15.5, 21.25, 9.75], "wool"),
    box("mao_dir", [15.5, 18.75, 6.75], [16.75, 20.75, 9.25], "hay"),
    # Cabeça de saco, nariz comprido e torto, olhos e boca costurados
    box("pescoco", [5.5, 21, 5.5], [10.5, 21.75, 10.5], "rope"),
    box("cabeca", [5, 21.5, 5], [11, 27, 11], "burlap"),
    box("nariz", [7.5, 23.25, 11], [8.5, 24.25, 13.25], "burlap", {"x": 15}, [8, 23.75, 11]),
    box("verruga", [7.6, 23.1, 12.6], [8.1, 23.6, 13.1], "mossy"),
    box("olho_esq", [5.75, 24.75, 10.9], [7, 25.75, 11.2], "coal"),
    box("olho_dir", [9, 24.75, 10.9], [10.25, 25.75, 11.2], "coal"),
    box("boca", [6.25, 22.25, 10.9], [9.75, 22.75, 11.15], "rope"),
    # Cabelo de palha saindo do chapéu
    box("cabelo_esq", [4.6, 21.5, 5.5], [5.25, 26, 10.75], "hay"),
    box("cabelo_dir", [10.75, 21.5, 5.5], [11.4, 26, 10.75], "hay"),
    box("cabelo_tras", [5.25, 20, 10.75], [10.75, 26, 11.4], "hay"),
    # Chapéu de bruxa pontudo e torto
    box("aba", [2.5, 27, 2.5], [13.5, 27.75, 13.5], "wool"),
    box("cone1", [4.5, 27.75, 4.5], [11.5, 30, 11.5], "wool"),
    box("faixa", [4.4, 27.75, 4.4], [11.6, 28.75, 11.6], "purple"),
    box("cone2", [5.5, 30, 5.5], [10.5, 32, 10.5], "wool", {"z": 6}, [8, 30, 8]),
    box("cone3", [6.5, 31.75, 6.5], [9.5, 33.5, 9.5], "wool", {"z": 14}, [8, 30, 8]),
    box("ponta", [7, 33, 7], [9, 34.5, 9], "wool", {"z": 30}, [8, 30, 8]),
]

BRUXA_VASSOURA = [16.1, 19.75, 8]
bruxa_vassoura = [
    box("cabo", [15.75, 8, 7.6], [16.5, 25, 8.4], "darkwood", {"z": -12}, BRUXA_VASSOURA),
    box("amarra_palha", [15.25, 7.5, 7.1], [17, 8.5, 8.9], "rope", {"z": -12}, BRUXA_VASSOURA),
    box("palha", [14.75, 3.5, 6.5], [17.5, 7.5, 9.5], "hay", {"z": -12}, BRUXA_VASSOURA),
]

bruxa_cesto = [
    box("alca_cesto", [-0.4, 15.5, 7.6], [0.1, 18.75, 8.4], "rope"),
    box("cesto", [-2.25, 11.5, 5.75], [1.75, 15.5, 10.25], "basketside", faces={"up": "basketlid"}),
    box("frutas1", [-1.75, 15.5, 6.25], [0.25, 16.25, 8.25], "blueberry"),
    box("frutas2", [-0.5, 15.5, 8], [1.25, 16, 9.75], "blackberry"),
]


# =====================================================================
# MINION COLHEDOR — "lufinho": trabalhador pequenininho (tipo Oompa-Loompa) com a cara do jogo.
# Pele de barro laranja, cabelo de musgo, sobrancelha branca, macacão marrom de uniforme,
# chapéu de palha (uniforme da colheita) e cestinho nas costas. Um por casa.
# Casa temática da colheita (cabaninha de palha) com o bauzinho do lado.
# =====================================================================
def _gable(prefix, z0, z1):
    """Oitão (parede triangular) feito em degraus."""
    out = []
    # Cada degrau fica embaixo da inclinação do telhado (36°), sem furar a palha
    for i, (x0, x1) in enumerate([(2.75, 10.25), (4.25, 8.75), (5.75, 7.25)]):
        out.append(box(f"{prefix}{i}", [x0, 8 + i, z0], [x1, 9 + i, z1], "planks"))
    return out


def _gable_t(prefix, z0, z1, tex):
    return [box(f"{prefix}{i}", [x0, 8 + i, z0], [x1, 9 + i, z1], tex)
            for i, (x0, x1) in enumerate([(2.75, 10.25), (4.25, 8.75), (5.75, 7.25)])]


def casinha(parede="planks", canto="darkwood", telhado="straw", cume="hay", alicerce="cobble",
            porta="darkwood", batente="mossy", placa="paper", chamine="brick"):
    """A mesma cabaninha do colhedor (porta do tamanho dele, telhado de duas águas), com outros materiais."""
    out = [
        box("alicerce", [0.75, 0, 2.25], [12.25, 1, 12.75], alicerce),
        box("parede", [1.5, 1, 3], [11.5, 8, 12], parede),
        box("canto1", [1, 1, 2.5], [2.25, 8, 3.75], canto),
        box("canto2", [10.75, 1, 2.5], [12, 8, 3.75], canto),
        box("canto3", [1, 1, 11.25], [2.25, 8, 12.5], canto),
        box("canto4", [10.75, 1, 11.25], [12, 8, 12.5], canto),
        *_gable_t("oitao_f", 11.5, 12, parede), *_gable_t("oitao_t", 3, 3.5, parede),
        box("porta", [4.5, 1, 12], [8.5, 6, 12.3], porta),
        box("porta_arco", [5, 6, 12], [8, 6.75, 12.3], porta),
        box("batente_esq", [4, 1, 12], [4.5, 6.5, 12.45], batente),
        box("batente_dir", [8.5, 1, 12], [9, 6.5, 12.45], batente),
        box("batente_cima", [4.5, 6.5, 12], [8.5, 7.25, 12.45], batente),
        box("macaneta", [7.6, 3.2, 12.3], [8.1, 3.7, 12.6], "brass"),
        box("janela", [5.5, 8.5, 12], [7.5, 10.5, 12.15], "glass"),
        box("janela_moldura", [5.25, 8.25, 11.95], [7.75, 8.6, 12.2], "darkwood"),
        box("placa", [3.25, 7.25, 12.3], [9.75, 8.25, 12.5], placa),
        box("telhado_esq", [-0.75, 11.4, 1.75], [6.9, 12.9, 13.25], telhado, {"z": 36}, [6.5, 12.5, 7.5]),
        box("telhado_dir", [6.1, 11.4, 1.75], [13.75, 12.9, 13.25], telhado, {"z": -36}, [6.5, 12.5, 7.5]),
        box("cumeeira", [5.75, 12.6, 1.5], [7.25, 13.6, 13.5], cume),
    ]
    if chamine:
        out.append(box("chamine", [8.6, 9, 4], [10.4, 15, 5.8], chamine))
    return out


def bauzinho():
    return [
        box("bau", [12.25, 0, 7.5], [16, 3.75, 12.5], "chestside"),
        box("bau_tampa", [12.1, 3.75, 7.35], [16, 5, 12.65], "darkwood"),
        box("bau_fecho", [13.6, 2.6, 12.5], [14.6, 4.1, 12.8], "corroded"),
        box("bau_cinta", [12.1, 0, 9.6], [16, 5.1, 10.4], "darkiron"),
    ]


minion_casa = [
    # Cabaninha: alicerce de pedra, paredes de tábua, cantos de tora
    box("alicerce", [0.75, 0, 2.25], [12.25, 1, 12.75], "cobble"),
    box("parede", [1.5, 1, 3], [11.5, 8, 12], "planks"),
    box("canto1", [1, 1, 2.5], [2.25, 8, 3.75], "darkwood"),
    box("canto2", [10.75, 1, 2.5], [12, 8, 3.75], "darkwood"),
    box("canto3", [1, 1, 11.25], [2.25, 8, 12.5], "darkwood"),
    box("canto4", [10.75, 1, 11.25], [12, 8, 12.5], "darkwood"),
    *_gable("oitao_f", 11.5, 12), *_gable("oitao_t", 3, 3.5),
    # Porta redondinha (do tamanho dele) com batente e maçaneta
    box("porta", [4.5, 1, 12], [8.5, 6, 12.3], "darkwood"),
    box("porta_arco", [5, 6, 12], [8, 6.75, 12.3], "darkwood"),
    box("batente_esq", [4, 1, 12], [4.5, 6.5, 12.45], "mossy"),
    box("batente_dir", [8.5, 1, 12], [9, 6.5, 12.45], "mossy"),
    box("batente_cima", [4.5, 6.5, 12], [8.5, 7.25, 12.45], "mossy"),
    box("macaneta", [7.6, 3.2, 12.3], [8.1, 3.7, 12.6], "brass"),
    # Janelinha redonda no oitão e plaquinha da profissão (cesto) acima da porta
    box("janela", [5.5, 8.5, 12], [7.5, 10.5, 12.15], "glass"),
    box("janela_moldura", [5.25, 8.25, 11.95], [7.75, 8.6, 12.2], "darkwood"),
    box("placa", [3.25, 7.25, 12.3], [9.75, 8.25, 12.5], "paper"),
    # Telhado de palha (duas águas) com cumeeira de corda
    box("telhado_esq", [-0.75, 11.4, 1.75], [6.9, 12.9, 13.25], "straw", {"z": 36}, [6.5, 12.5, 7.5]),
    box("telhado_dir", [6.1, 11.4, 1.75], [13.75, 12.9, 13.25], "straw", {"z": -36}, [6.5, 12.5, 7.5]),
    box("cumeeira", [5.75, 12.6, 1.5], [7.25, 13.6, 13.5], "hay"),
    box("chamine", [8.6, 9, 4], [10.4, 15, 5.8], "brick"),
    # Decoração da colheita: abóbora, repolho e um feixe de palha
    box("abobora", [0.25, 0, 13], [3.75, 3, 16], "pumpkin", faces={"up": "pumpkintop", "down": "pumpkintop"}),
    box("abobora_cabo", [1.75, 3, 14.25], [2.25, 3.75, 14.75], "mossy"),
    box("repolho", [9.5, 0, 13.5], [11.5, 1.8, 15.5], "cabbage"),
    box("feixe", [0.25, 0, 3.5], [1.5, 4.5, 6], "hay", {"z": 8}, [0.9, 0, 4.75]),
    box("feixe_amarra", [0.1, 2, 3.4], [1.65, 2.6, 6.1], "rope", {"z": 8}, [0.9, 0, 4.75]),
    # Bauzinho do lado da casa
    box("bau", [12.25, 0, 7.5], [16, 3.75, 12.5], "chestside"),
    box("bau_tampa", [12.1, 3.75, 7.35], [16, 5, 12.65], "darkwood"),
    box("bau_fecho", [13.6, 2.6, 12.5], [14.6, 4.1, 12.8], "corroded"),
    box("bau_cinta", [12.1, 0, 9.6], [16, 5.1, 10.4], "darkiron"),
]


def nest(parent, kids):
    """Converte peças em coordenada absoluta pra filhas (relativas ao 'from' do pai)."""
    pf = parent["from"]
    for k in kids:
        sub = k.pop("_kids", [])
        if sub:
            nest(k, sub)
        k["from"] = [k["from"][i] - pf[i] for i in range(3)]
        k["to"] = [k["to"][i] - pf[i] for i in range(3)]
        if "rotationOrigin" in k:
            k["rotationOrigin"] = [k["rotationOrigin"][i] - pf[i] for i in range(3)]
    parent.setdefault("children", []).extend(kids)
    return parent


def joint(name, frm, to, tex, origin, kids=(), **kw):
    e = box(name, frm, to, tex, **kw)
    e["rotationOrigin"] = list(origin)
    e["_kids"] = list(kids)
    return e


def chapeu_palha():
    return [
        box("chapeu_aba", [3.5, 13.4, 3.75], [12.5, 13.9, 12.25], "straw"),
        box("chapeu_copa", [5.5, 13.9, 5.75], [10.5, 15.6, 10.25], "straw"),
        box("chapeu_fita", [5.4, 13.9, 5.65], [10.6, 14.5, 10.35], "red"),
    ]


def cesto_colhedor():
    cesto = box("cesto", [5.75, 4.25, 4.25], [10.25, 8, 6.25], "basketside", faces={"up": "basketlid"})
    cesto["_kids"] = [
        box("cesto_frutas", [6.1, 8, 4.5], [9.9, 8.6, 6], "blueberry"),
        box("cesto_cenoura", [8.3, 8, 4.7], [8.9, 9.8, 5.3], "cabbage", {"z": -12}, [8.6, 8, 5]),
    ]
    return cesto


def lufinho(u=None):
    """Trabalhador pequenininho. Frente = +z (sul). Esqueleto: quadril > (pernas, tronco > (cabeça, braços, cesto)).
    u = uniforme da profissão: chapeu, rosto, camisa, macacao, bota, costas, mao (ferramenta), peito (avental etc.)."""
    u = u or {}
    camisa, macacao, bota = u.get("camisa", "shirt"), u.get("macacao", "overall"), u.get("bota", "boot")
    cabeca = joint("cabeca", [5, 8, 5.5], [11, 13.25, 10.5], "orangeskin", [8, 8, 8], [
        # Olhos grandes, sobrancelhas brancas e sorriso
        box("olho_esq", [6, 10.25, 10.45], [7.5, 11.75, 10.6], "white"),
        box("pupila_esq", [6.6, 10.4, 10.55], [7.3, 11.3, 10.7], "coal"),
        box("olho_dir", [8.5, 10.25, 10.45], [10, 11.75, 10.6], "white"),
        box("pupila_dir", [8.7, 10.4, 10.55], [9.4, 11.3, 10.7], "coal"),
        box("sobrancelha_esq", [5.75, 12, 10.45], [7.6, 12.6, 10.7], "white"),
        box("sobrancelha_dir", [8.4, 12, 10.45], [10.25, 12.6, 10.7], "white"),
        box("nariz", [7.4, 9.6, 10.5], [8.6, 10.6, 11.2], "orangeskin"),
        box("boca", [6.75, 8.75, 10.45], [9.25, 9.15, 10.6], "red"),
        box("boca_esq", [6.4, 9.05, 10.45], [6.9, 9.45, 10.6], "red"),
        box("boca_dir", [9.1, 9.05, 10.45], [9.6, 9.45, 10.6], "red"),
        box("orelha_esq", [4.5, 9.75, 7.5], [5, 11, 8.75], "orangeskin"),
        box("orelha_dir", [11, 9.75, 7.5], [11.5, 11, 8.75], "orangeskin"),
        # Cabelo de musgo verde saindo do chapéu
        box("cabelo_tras", [4.75, 9, 5.25], [11.25, 13.4, 6], "greenhair"),
        box("cabelo_esq", [4.75, 11, 6], [5.3, 13.4, 9.5], "greenhair"),
        box("cabelo_dir", [10.7, 11, 6], [11.25, 13.4, 9.5], "greenhair"),
        box("topete", [6, 13.25, 9.25], [9.5, 13.75, 10.9], "greenhair"),
        # Chapéu de palha da colheita
        *u.get("chapeu", chapeu_palha()),
        *u.get("rosto", []),
    ])

    def braco(lado, x0, x1, extra=()):
        mid = (x0 + x1) / 2
        return joint(f"braco_{lado}", [x0, 5, 7.25], [x1, 8, 8.75], camisa, [mid, 7.75, 8], [
            box(f"mao_{lado}", [x0 + 0.05, 3.75, 7.35], [x1 - 0.05, 5, 8.65], "orangeskin"),
            *extra,
        ])

    costas = u.get("costas", cesto_colhedor())
    peito = u.get("peito", [
        box("peitilho", [6.25, 4, 9.75], [9.75, 7, 9.95], macacao),
        box("bolso", [7.1, 4.75, 9.95], [8.9, 6, 10.05], macacao),
        box("alca_esq", [6.25, 7, 6.15], [7, 8.1, 9.95], macacao),
        box("alca_dir", [9, 7, 6.15], [9.75, 8.1, 9.95], macacao),
        box("botao_esq", [6.4, 6.4, 9.95], [6.9, 6.9, 10.1], "bronze"),
        box("botao_dir", [9.1, 6.4, 9.95], [9.6, 6.9, 10.1], "bronze"),
    ])
    tronco = joint("tronco", [5.25, 4, 6.25], [10.75, 8, 9.75], camisa, [8, 4, 8], [
        *peito,
        cabeca, braco("esq", 4, 5.25), braco("dir", 10.75, 12, u.get("mao", [])),
        *([costas] if costas else []),
    ])

    def perna(lado, x0, x1):
        mid = (x0 + x1) / 2
        return joint(f"perna_{lado}", [x0, 1, 7.25], [x1, 2.75, 8.75], macacao, [mid, 2.75, 8], [
            box(f"bota_{lado}", [x0 - 0.2, 0, 7], [x1 + 0.2, 1.25, 9.4], bota),
        ])

    quadril = joint("quadril", [5.5, 2.5, 6.5], [10.5, 4, 9.5], macacao, [8, 2.5, 8], [
        perna("esq", 5.75, 7.75), perna("dir", 8.25, 10.25), tronco,
    ])
    kids = quadril.pop("_kids")
    nest(quadril, kids)
    return [quadril]


def kf(frame, **els):
    return {"frame": frame, "elements": els}


LUFINHO_ANIMS = [
    # Andar: passinho rápido e pulado
    {"code": "andar", "quantityframes": 20, "keyframes": [
        kf(0, perna_esq={"rotationX": 32}, perna_dir={"rotationX": -32}, braco_esq={"rotationX": -30}, braco_dir={"rotationX": 30},
           tronco={"rotationZ": 4}, quadril={"offsetY": 0}),
        kf(5, quadril={"offsetY": 0.7}),
        kf(10, perna_esq={"rotationX": -32}, perna_dir={"rotationX": 32}, braco_esq={"rotationX": 30}, braco_dir={"rotationX": -30},
           tronco={"rotationZ": -4}, quadril={"offsetY": 0}),
        kf(15, quadril={"offsetY": 0.7}),
    ]},
    # Parado: balança de leve
    {"code": "parado", "quantityframes": 60, "keyframes": [
        kf(0, tronco={"rotationZ": -3}, cabeca={"rotationZ": 5}),
        kf(30, tronco={"rotationZ": 3}, cabeca={"rotationZ": -5}),
    ]},
    # Dancinha de quando termina o serviço (braços pra cima alternando, pulinho)
    {"code": "dancar", "quantityframes": 24, "keyframes": [
        kf(0, braco_esq={"rotationZ": -150}, braco_dir={"rotationZ": 40}, quadril={"offsetY": 0, "rotationY": 20},
           perna_esq={"rotationZ": -10}, cabeca={"rotationZ": 10}),
        kf(6, quadril={"offsetY": 1.5}),
        kf(12, braco_esq={"rotationZ": -40}, braco_dir={"rotationZ": 150}, quadril={"offsetY": 0, "rotationY": -20},
           perna_dir={"rotationZ": 10}, cabeca={"rotationZ": -10}),
        kf(18, quadril={"offsetY": 1.5}),
    ]},
    # Acenando com o braço direito
    {"code": "acenar", "quantityframes": 20, "keyframes": [
        kf(0, braco_dir={"rotationZ": 150}, cabeca={"rotationZ": -8}),
        kf(5, braco_dir={"rotationZ": 170}),
        kf(10, braco_dir={"rotationZ": 150}),
        kf(15, braco_dir={"rotationZ": 170}),
    ]},
    # Colhendo: abaixa e puxa
    {"code": "colher", "quantityframes": 30, "keyframes": [
        kf(0, tronco={"rotationX": 40}, cabeca={"rotationX": -10}, braco_esq={"rotationX": -70}, braco_dir={"rotationX": -50},
           perna_esq={"rotationX": -15}, perna_dir={"rotationX": -15}, quadril={"offsetY": -0.4}),
        kf(15, tronco={"rotationX": 25}, cabeca={"rotationX": -5}, braco_esq={"rotationX": -40}, braco_dir={"rotationX": -80},
           perna_esq={"rotationX": -10}, perna_dir={"rotationX": -10}, quadril={"offsetY": 0}),
    ]},
]

MINION_ELEMENTS, MINION_ANIMS = lufinho(), LUFINHO_ANIMS

# =====================================================================
# MINIONS DAS MÁQUINAS — cada profissão com seu uniforme, sua casinha e o bauzinho do lado
# =====================================================================
def ferramenta(*els):
    """Peças presas na mão direita (acompanham o braço)."""
    return list(els)


PROFISSOES = {}

# 1) MOLEIRO (Moedor): avental e chapéu de padeiro, saco de farinha nas costas. Casa de pedra com moinho de vento.
saco = box("saco", [5.9, 4.2, 4.3], [10.1, 8.4, 6.25], "linen")
saco["_kids"] = [box("saco_boca", [6.6, 8.4, 4.7], [9.4, 9.2, 5.9], "rope")]
PROFISSOES["moleiro"] = {
    "title": "Minion Moleiro", "mod": "Moedor Automático",
    "desc": "Moleiro (versão minion do Moedor): de avental e chapéu de padeiro, com saco de farinha nas costas. Mora numa casa de pedra com moinho de vento. Pega o grão do bauzinho, mói na mó do lado da casa e guarda a farinha.",
    "uni": {
        "camisa": "white", "macacao": "linen",
        "chapeu": [box("touca", [5.25, 13.2, 5.75], [10.75, 15.4, 10.25], "white"),
                   box("touca_topo", [4.75, 15.2, 5.25], [11.25, 16.8, 10.75], "white"),
                   box("touca_faixa", [5.15, 13.2, 5.65], [10.85, 13.9, 10.35], "linen")],
        "rosto": [box("farinha_bochecha", [9.6, 9.6, 10.47], [10.4, 10.2, 10.62], "white")],
        "peito": [box("avental", [5.9, 1.5, 9.75], [10.1, 7.4, 9.95], "linen"),
                  box("avental_fita", [5.25, 6.6, 6.15], [10.75, 7.1, 9.8], "linen")],
        "costas": saco,
    },
    "casa": casinha(parede="cobble", canto="darkwood", telhado="telha_vermelha", cume="darkwood", placa="linen") + [
        box("mo", [0.4, 0, 12.6], [3.6, 1.6, 15.8], "quern", faces={"up": "grindtop"}),
        box("mo_cabo", [1.7, 1.6, 13.9], [2.3, 3, 14.5], "darkwood"),
        box("saca1", [9.3, 0, 13], [11.6, 2.6, 15.2], "linen"),
        box("saca1_boca", [9.8, 2.6, 13.5], [11.1, 3.1, 14.7], "rope"),
        box("eixo_moinho", [6.25, 13.95, 11.8], [6.75, 14.45, 13.35], "darkwood"),
    ] + bauzinho(),
    "extras": {"pas": {"label": "Pás do moinho (giram)", "pivot": [6.5, 14.2, 13.4], "spin": "z", "els": [
        box("pa_eixo", [6.05, 13.75, 13.3], [6.95, 14.65, 13.75], "darkiron"),
        box("pa_v", [6.28, 10.6, 13.35], [6.72, 17.8, 13.5], "darkwood"),
        box("pa_h", [2.9, 13.98, 13.35], [10.1, 14.42, 13.5], "darkwood"),
        box("vela_c", [6.72, 14.7, 13.38], [7.9, 17.6, 13.46], "linen"),
        box("vela_b", [5.1, 10.8, 13.38], [6.28, 13.7, 13.46], "linen"),
        box("vela_d", [7.2, 12.8, 13.38], [10.1, 13.98, 13.46], "linen"),
        box("vela_e", [2.9, 14.42, 13.38], [5.8, 15.6, 13.46], "linen"),
    ]}},
}

# 2) GARIMPEIRO (Peneira): chapelão de couro, lenço, bateia na mão. Barraco de tábua com calha d'água e cascalho.
PROFISSOES["garimpeiro"] = {
    "title": "Minion Garimpeiro", "mod": "Peneira Automática",
    "desc": "Garimpeiro (versão minion da Peneira): chapelão de couro, lenço no pescoço e a bateia na mão. Mora num barraco de tábua com calha d'água. Leva cascalho, areia e terra do bauzinho até a água, peneira e guarda o que achar.",
    "uni": {
        "camisa": "blue", "macacao": "overall",
        "chapeu": [box("chapelao_aba", [2.8, 13.3, 3.2], [13.2, 13.8, 12.8], "couro"),
                   box("chapelao_copa", [5.3, 13.8, 5.6], [10.7, 16, 10.4], "couro"),
                   box("chapelao_fita", [5.2, 13.8, 5.5], [10.8, 14.4, 10.5], "darkwood")],
        "peito": [box("lenco", [6, 7.2, 9.7], [10, 8.1, 10.05], "red"),
                  box("lenco_ponta", [7.4, 6.2, 9.8], [8.6, 7.2, 10.05], "red"),
                  box("suspensorio_e", [6.4, 4, 9.75], [7.1, 7.2, 9.9], "couro"),
                  box("suspensorio_d", [8.9, 4, 9.75], [9.6, 7.2, 9.9], "couro")],
        "costas": None,
        "mao": ferramenta(box("bateia", [9.6, 3.3, 7.2], [13.4, 3.9, 11], "panwood"),
                          box("bateia_borda", [9.4, 3.9, 7], [13.6, 4.3, 11.2], "darkwood"),
                          box("bateia_cascalho", [10.4, 3.9, 8], [12.6, 4.2, 10.2], "gravel")),
    },
    "casa": casinha(parede="planks", canto="mossy", telhado="tabuinha", cume="darkwood", chamine=None) + [
        box("calha", [-0.6, 5, 6], [1.5, 6, 9], "darkwood"),
        box("calha_agua", [-0.5, 5.6, 6.3], [1.5, 5.9, 8.7], "water"),
        box("pilha_cascalho", [0.4, 0, 12.8], [4, 1.4, 15.8], "gravel"),
        box("pilha_cascalho2", [1, 1.4, 13.4], [3.2, 2.2, 15.2], "gravel"),
        box("bateia_parede", [9.2, 3.2, 12.3], [11.4, 5.4, 12.6], "panwood"),
        box("pa", [9.6, 0, 13.2], [10.1, 5.5, 13.7], "darkwood", {"x": -14}, [9.85, 0, 13.45]),
    ] + bauzinho(),
}

# 3) PESCADOR (Pesca): capa e chapéu de chuva amarelos, galochas, vara de pesca. Cabana com rede e peixe pendurado.
PROFISSOES["pescador"] = {
    "title": "Minion Pescador", "mod": "Pesca Automática",
    "desc": "Pescador (versão minion da Pesca): chapéu e capa de chuva amarelos, galochas e a vara na mão. Mora numa cabana de tábua com rede e peixe secando. Vai até a água, pesca um tempo e volta com o cesto cheio pro bauzinho.",
    "uni": {
        "camisa": "yellow", "macacao": "blue", "bota": "yellow",
        "chapeu": [box("sueste_copa", [5.2, 13.2, 5.4], [10.8, 15.3, 10.6], "yellow"),
                   box("sueste_aba", [4, 13, 3.8], [12, 13.5, 11.4], "yellow"),
                   box("sueste_nuca", [4.3, 11.2, 3.6], [11.7, 13.3, 4.4], "yellow")],
        "costas": cesto_colhedor() | {"_kids": [box("cesto_peixe", [6.1, 8, 4.5], [9.9, 8.7, 6], "fishfresh")]},
        # Vara erguida pra frente (sai da mão) e a linha caindo da ponta, com a boia
        "mao": ferramenta(box("vara", [11.2, 4, 7.8], [11.55, 15, 8.15], "darkwood", {"x": 38}, [11.4, 4.2, 8]),
                          box("vara_carretel", [11, 5, 7.6], [11.75, 5.9, 8.35], "darkiron", {"x": 38}, [11.4, 4.2, 8]),
                          box("linha", [11.33, 2, 14.75], [11.42, 12.8, 14.84], "rope"),
                          box("boia", [11.1, 1.6, 14.5], [11.65, 2.3, 15.1], "red")),
    },
    "casa": casinha(parede="planks", canto="darkwood", telhado="straw", cume="darkwood", alicerce="darkwood", chamine=None) + [
        box("rede", [0.3, 2, 4], [1, 7.5, 10.5], "net"),
        box("vara_rede", [0.1, 7.3, 3.5], [0.6, 7.8, 11], "darkwood"),
        box("peixe1", [9.4, 3.6, 12.4], [10.4, 6.4, 12.7], "fishfresh"),
        box("peixe2", [10.6, 3.2, 12.4], [11.6, 6, 12.7], "fishfresh"),
        box("varal_peixe", [9, 6.4, 12.3], [12, 6.7, 12.7], "rope"),
        box("barril", [0.4, 0, 12.8], [3.4, 3.6, 15.8], "logbark", faces={"up": "logend"}),
        box("remo", [9.6, 0, 13.6], [10.2, 7, 14.1], "planks", {"z": 12}, [9.9, 0, 13.85]),
    ] + bauzinho(),
}

# 4) CARVOEIRO (Carvoeira): boné preto, cara suja de fuligem, pá; saco de carvão. Casa de barro com chaminé larga.
saco_carvao = box("saco_carvao", [5.9, 4.2, 4.3], [10.1, 8.2, 6.25], "burlap")
saco_carvao["_kids"] = [box("saco_carvao_topo", [6.4, 8.2, 4.7], [9.6, 8.8, 5.9], "coal")]
PROFISSOES["carvoeiro"] = {
    "title": "Minion Carvoeiro", "mod": "Carvoeira",
    "desc": "Carvoeiro (versão minion da Carvoeira): boné preto, cara suja de fuligem e uma pá na mão, com saco de carvão nas costas. Mora numa casa de barro com chaminé larga. Empilha as toras do bauzinho no forninho, queima e guarda o carvão.",
    "uni": {
        "camisa": "gray", "macacao": "wool",
        "chapeu": [box("bone", [5.1, 13.2, 5.4], [10.9, 14.8, 10.6], "wool"),
                   box("bone_aba", [5.6, 13.2, 10.4], [10.4, 13.6, 12.6], "wool")],
        "rosto": [box("fuligem1", [5.4, 9.2, 10.47], [6.6, 10, 10.62], "coal"),
                  box("fuligem2", [9.2, 11.9, 10.47], [10.4, 12.4, 10.62], "coal"),
                  box("fuligem3", [7.6, 9.2, 10.47], [8.4, 9.6, 10.62], "coal")],
        "costas": saco_carvao,
        "mao": ferramenta(box("pa_cabo", [11.15, -1, 7.75], [11.6, 6.5, 8.2], "darkwood"),
                          box("pa_lamina", [10.6, -3, 7.2], [12.2, -0.8, 8.8], "iron")),
    },
    "casa": casinha(parede="kilnwall", canto="brick", telhado="darkiron", cume="darkiron", chamine=None,
                    batente="brick", placa="coal") + [
        box("chamine_larga", [8, 8, 3.5], [11, 17, 6.5], "chimney"),
        box("chamine_boca", [7.7, 17, 3.2], [11.3, 17.6, 6.8], "brick"),
        box("toras1", [0.3, 0, 12.8], [4.3, 1.5, 15.6], "logbark", faces={"east": "logend", "west": "logend"}),
        box("toras2", [0.8, 1.5, 13.2], [3.8, 3, 15.2], "logbark", faces={"east": "logend", "west": "logend"}),
        box("carvao_monte", [9.2, 0, 13.2], [11.8, 1.6, 15.6], "coal"),
        box("brasa", [9.6, 1.6, 13.8], [11.2, 1.9, 15], "ember", glow=180),
    ] + bauzinho(),
}

# 5) APICULTOR (Colmeia): roupa branca, chapéu com véu, fumegador. Casa com colmeias de palha na frente.
PROFISSOES["apicultor"] = {
    "title": "Minion Apicultor", "mod": "Colmeia Coletora",
    "desc": "Apicultor (versão minion da Colmeia): macacão branco, chapéu com véu e o fumegador na mão. Mora numa casa com colmeias de palha na frente. Visita as colmeias da área, acalma as abelhas com fumaça, colhe o favo sem matar o enxame e guarda mel e cera no bauzinho.",
    "uni": {
        "camisa": "white", "macacao": "white",
        "chapeu": [box("veu_aba", [3.6, 13.6, 3.8], [12.4, 14, 12.2], "straw"),
                   box("veu_copa", [5.5, 14, 5.8], [10.5, 15.6, 10.2], "straw"),
                   box("veu_frente", [4.3, 8.4, 11.1], [11.7, 13.6, 11.3], "net"),
                   box("veu_esq", [4.1, 8.4, 4.6], [4.3, 13.6, 11.2], "net"),
                   box("veu_dir", [11.7, 8.4, 4.6], [11.9, 13.6, 11.2], "net"),
                   box("veu_tras", [4.3, 8.4, 4.4], [11.7, 13.6, 4.6], "net")],
        "costas": None,
        "mao": ferramenta(box("fumegador", [10.7, 1.4, 8.5], [12.1, 3.8, 10.1], "bronze"),
                          box("fumegador_bico", [11, 3.8, 8.9], [11.8, 4.6, 9.7], "bronze"),
                          box("fumegador_fole", [10.8, 1.6, 7.4], [12, 3.4, 8.5], "couro")),
    },
    "casa": casinha(parede="planks", canto="mossy", telhado="straw", cume="hay", placa="wax") + [
        box("banco", [0.2, 1.6, 12.8], [5, 2.2, 15.8], "planks"),
        box("banco_pe1", [0.5, 0, 13.2], [1.1, 1.6, 15.4], "darkwood"),
        box("banco_pe2", [4.1, 0, 13.2], [4.7, 1.6, 15.4], "darkwood"),
        box("skep1", [0.6, 2.2, 13.2], [2.6, 4.6, 15.4], "skep"),
        box("skep1_topo", [1, 4.6, 13.6], [2.2, 5.4, 15], "skep"),
        box("skep2", [2.8, 2.2, 13.2], [4.8, 4.4, 15.4], "skep"),
        box("skep2_topo", [3.2, 4.4, 13.6], [4.4, 5.1, 15], "skep"),
        box("favo", [9.4, 0, 13.4], [11.4, 1.4, 15.2], "honeycomb"),
    ] + bauzinho(),
}

# 6) LENHADOR (Serraria): camisa xadrez vermelha, gorro, barba verde, machado. Cabana de toras com cepo e lenha.
PROFISSOES["lenhador"] = {
    "title": "Minion Lenhador", "mod": "Serraria d'Água",
    "desc": "Lenhador (versão minion da Serraria): camisa vermelha, gorro, barba verde e machado na mão. Mora numa cabana de toras com cepo e lenha empilhada. Corta as árvores grandes da área, replanta a muda no lugar, serra as toras em tábuas e guarda tudo no bauzinho.",
    "uni": {
        "camisa": "red", "macacao": "blue",
        "chapeu": [box("gorro", [5.1, 13, 5.4], [10.9, 14.9, 10.6], "red"),
                   box("gorro_barra", [4.9, 12.8, 5.2], [11.1, 13.6, 10.8], "white"),
                   box("gorro_pompom", [7.3, 14.9, 7.3], [8.7, 16.1, 8.7], "white")],
        "rosto": [box("barba", [5.6, 7.4, 10.4], [10.4, 9.3, 11], "greenhair"),
                  box("bigode", [6.4, 9.1, 10.55], [9.6, 9.6, 10.9], "greenhair")],
        "costas": None,
        "mao": ferramenta(box("machado_cabo", [11.15, -1.5, 7.75], [11.6, 6, 8.2], "darkwood"),
                          box("machado_lamina", [11, -1.6, 8.2], [11.75, 0.4, 10.4], "iron")),
    },
    "casa": casinha(parede="logbark", canto="logend", telhado="mossy", cume="darkwood", batente="darkwood") + [
        box("cepo", [0.6, 0, 12.8], [3.8, 2.4, 15.8], "logbark", faces={"up": "logend"}),
        box("machado_cepo_cabo", [2, 2.4, 14], [2.5, 6, 14.5], "darkwood", {"z": -20}, [2.25, 2.4, 14.25]),
        box("machado_cepo_lamina", [1.4, 2.2, 13.9], [2.9, 2.9, 14.6], "iron", {"z": -20}, [2.25, 2.4, 14.25]),
        box("lenha1", [9, 0, 13], [11.8, 1.2, 15.8], "logbark", faces={"north": "logend", "south": "logend"}),
        box("lenha2", [9.3, 1.2, 13.2], [11.5, 2.4, 15.6], "logbark", faces={"north": "logend", "south": "logend"}),
        box("muda", [0.2, 0, 4], [1.2, 2.8, 5], "moss"),
    ] + bauzinho(),
}

# 7) DEFUMADOR (Defumador automático): lenço na cabeça, avental de couro, faca. Casa de tijolo com varal de defumar.
PROFISSOES["defumador"] = {
    "title": "Minion Defumador", "mod": "Defumador",
    "desc": "Defumador (versão minion do Defumador — o defumador automático): lenço na cabeça, avental de couro e uma faquinha. Mora numa casa de tijolo com varal sobre a brasa. Pega carne e peixe crus do bauzinho, pendura no varal, cuida do fogo e guarda o defumado.",
    "uni": {
        "camisa": "shirt", "macacao": "overall",
        "chapeu": [box("lenco_cabeca", [4.9, 12, 5.3], [11.1, 13.9, 10.7], "red"),
                   box("lenco_no", [7.4, 11.6, 4.5], [8.6, 12.8, 5.4], "red")],
        "peito": [box("avental_couro", [5.9, 1.4, 9.75], [10.1, 7.6, 10], "couro"),
                  box("avental_cordao", [5.25, 6.8, 6.15], [10.75, 7.2, 9.8], "rope")],
        "costas": None,
        "mao": ferramenta(box("faca_cabo", [11.15, 2.6, 7.75], [11.6, 4, 8.2], "darkwood"),
                          box("faca_lamina", [11.2, 0.6, 7.85], [11.55, 2.6, 8.1], "iron")),
    },
    "casa": casinha(parede="brick", canto="darkwood", telhado="telha_marrom", cume="darkwood", placa="couro") + [
        box("poste_v1", [0.3, 0, 13], [0.9, 7, 13.6], "darkwood"),
        box("poste_v2", [0.3, 0, 15.3], [0.9, 7, 15.9], "darkwood"),
        box("trave_v", [0.2, 6.6, 12.8], [1, 7.2, 16], "darkwood"),
        box("carne1", [0.35, 3.6, 13.8], [0.85, 6.6, 14.5], "smoked"),
        box("peixe_d", [0.35, 3.9, 14.7], [0.85, 6.6, 15.2], "fishsmoked"),
        box("brasa_d", [0, 0, 13.4], [1.2, 0.5, 15.5], "ember", glow=180),
        box("lenha_d", [9.4, 0, 13.2], [11.8, 1.4, 15.6], "logbark", faces={"north": "logend", "south": "logend"}),
    ] + bauzinho(),
}

# 8) VIGIA (Sino): capacete de ferro, colete de couro, lanterna. Casa de pedra com campanário e sino.
PROFISSOES["vigia"] = {
    "title": "Minion Vigia", "mod": "Sino de Alarme",
    "desc": "Vigia (versão minion do Sino): capacete de ferro, colete de couro e lanterna na mão. Mora numa casa de pedra com um sino em cima. Fica de olho na área: quando chega drifter, lobo ou urso, toca o sino, avisa no chat de onde veio e corre pra dentro. De noite faz a ronda com a lanterna.",
    "uni": {
        "camisa": "gray", "macacao": "overall",
        "chapeu": [box("capacete", [4.9, 12.6, 5.3], [11.1, 14.8, 10.7], "darkiron"),
                   box("capacete_aba", [4.3, 12.5, 4.7], [11.7, 12.9, 11.3], "darkiron"),
                   box("capacete_crista", [7.6, 14.8, 5.6], [8.4, 15.4, 10.4], "corroded")],
        "peito": [box("colete", [5.15, 4, 9.7], [10.85, 7.9, 9.95], "couro"),
                  box("colete_fivela", [7.6, 5, 9.95], [8.4, 5.8, 10.05], "brass")],
        "costas": None,
        "mao": ferramenta(box("lanterna_alca", [11.15, 2.4, 7.75], [11.6, 3.8, 8.2], "darkiron"),
                          box("lanterna_vidro", [10.6, 0.4, 7.2], [12.2, 2.4, 8.8], "glass"),
                          box("lanterna_chama", [11.1, 0.8, 7.7], [11.7, 1.8, 8.3], "flame", glow=220)),
    },
    "casa": casinha(parede="cobble", canto="brick", telhado="telha_cinza", cume="darkiron", chamine=None, placa="corroded") + [
        # Campanário em cima da cumeeira (o sino fica todo acima do telhado)
        box("torre_base", [5.2, 13.4, 6], [7.8, 14, 9.2], "darkwood"),
        box("torre_p1", [5.4, 14, 6.2], [6, 20, 6.8], "darkwood"),
        box("torre_p2", [7, 14, 6.2], [7.6, 20, 6.8], "darkwood"),
        box("torre_p3", [5.4, 14, 8.4], [6, 20, 9], "darkwood"),
        box("torre_p4", [7, 14, 8.4], [7.6, 20, 9], "darkwood"),
        box("torre_teto", [4.8, 20, 5.6], [8.2, 20.7, 9.6], "telha_cinza"),
        box("torre_ponta", [6, 20.7, 7], [7, 21.9, 8.2], "corroded"),
        box("lanterna_porta", [9.4, 5, 12.4], [10.6, 6.6, 13.4], "glass"),
        box("lanterna_porta_luz", [9.7, 5.3, 12.7], [10.3, 6.2, 13.1], "flame", glow=220),
        box("corda_sino", [6.35, 4, 12.5], [6.55, 12.4, 12.7], "rope"),  # corda até a porta
    ] + bauzinho(),
    "extras": {"sino": {"label": "Sino (balança)", "pivot": [6.5, 19.7, 7.6], "swing": "z", "els": [
        box("sino_alca", [6.3, 19.2, 7.4], [6.7, 19.9, 7.8], "darkiron"),
        box("sino_topo", [6, 18.2, 7.1], [7, 19.2, 8.1], "bronze"),
        box("sino_corpo", [5.7, 16.6, 6.8], [7.3, 18.2, 8.4], "bronze"),
        box("sino_boca", [5.5, 16.1, 6.6], [7.5, 16.7, 8.6], "bronze"),
        box("sino_badalo", [6.35, 15.4, 7.45], [6.65, 16.3, 7.75], "darkiron"),
    ]}},
}

# 9) COGUMELEIRO (Tronco de Cogumelos): chapeuzinho de cogumelo, avental de juta, cesto de vime e faquinha.
#    Mora num toco oco de árvore com um chapéu de cogumelo vermelho de telhado.
cesto_cog = box("cesto", [5.75, 4.25, 4.25], [10.25, 8, 6.25], "basketside", faces={"up": "basketlid"})
cesto_cog["_kids"] = [
    box("cesto_cog1", [6.1, 8, 4.5], [7.9, 8.9, 6], "capbolete"),
    box("cesto_cog2", [8.1, 8, 4.6], [9.9, 8.7, 5.9], "capfield"),
    box("cesto_cog3", [7.4, 8.6, 4.9], [8.6, 9.4, 5.6], "chanterelle"),
]


def _toco():
    out = [
        # Toco oco (mesma planta da casinha, porta no mesmo lugar), com raízes saindo pro chão
        box("toco", [1.5, 0, 3], [11.5, 9.5, 12], "bark", faces={"up": "logend", "down": "logend"}),
        box("toco_l1", [1, 0, 3.75], [1.5, 9, 11.25], "bark"),
        box("toco_l2", [11.5, 0, 3.75], [12, 9, 11.25], "bark"),
        box("toco_l3", [2.25, 0, 2.5], [10.75, 9, 3], "bark"),
        box("toco_l4", [2.25, 0, 12], [10.75, 1, 12.5], "bark"),
        box("raiz1", [0, 0, 5], [1.5, 1.6, 6.6], "bark", {"z": -25}, [1.5, 0, 5.8]),
        box("raiz2", [-0.4, 0, 9], [1.2, 1.3, 10.4], "bark", {"y": 20}, [1.2, 0, 9.7]),
        box("raiz3", [11.6, 0, 4.4], [13, 1.4, 5.8], "bark", {"z": 25}, [11.6, 0, 5.1]),
        box("raiz4", [2.6, 0, 12.2], [4, 1.5, 13.6], "bark", {"x": 25}, [3.3, 0, 12.2]),
        box("raiz5", [9.6, 0, 12.2], [10.8, 1.2, 13.4], "bark", {"x": 25}, [10.2, 0, 12.2]),
        box("raiz6", [5, 0, 1.6], [6.6, 1.4, 3], "bark", {"x": -25}, [5.8, 0, 3]),
        # Porta redondinha do tamanho dele
        box("porta", [4.5, 1, 12], [8.5, 6, 12.3], "darkwood"),
        box("porta_arco", [5, 6, 12], [8, 6.75, 12.3], "darkwood"),
        box("batente_esq", [4, 1, 12], [4.5, 6.5, 12.45], "mossy"),
        box("batente_dir", [8.5, 1, 12], [9, 6.5, 12.45], "mossy"),
        box("batente_cima", [4.5, 6.5, 12], [8.5, 7.25, 12.45], "mossy"),
        box("macaneta", [7.6, 3.2, 12.3], [8.1, 3.7, 12.6], "brass"),
        box("degrau", [4, 0, 12.3], [9, 0.8, 13.3], "cobble"),
        # Janelinha redonda e plaquinha
        box("janela", [9.6, 4, 12], [11, 5.6, 12.15], "glass"),
        box("janela_moldura", [9.4, 3.8, 11.95], [11.2, 4.1, 12.2], "darkwood"),
        box("placa", [3.25, 7.4, 12.3], [9.75, 8.4, 12.5], "paper"),
        # Orelhas-de-pau crescendo no toco
        box("orelha1", [0.3, 3.5, 5], [1.1, 3.9, 7.5], "shelf"),
        box("orelha2", [0.3, 5.2, 6], [1.1, 5.6, 8], "shelf"),
        box("orelha3", [11.9, 6, 7], [12.6, 6.4, 9.4], "shelf"),
        # Telhado: chapéu de cogumelo vermelho de bolinha, com as lamelas embaixo
        box("chapeu_aba", [-1, 9.5, 0.75], [14, 11, 14.25], "flyagaric", faces={"down": "flyagaricpores"}),
        box("chapeu_meio", [0.5, 11, 2.25], [12.5, 12.6, 12.75], "flyagaric"),
        box("chapeu_topo", [2.75, 12.6, 4.5], [10.25, 13.6, 10.5], "flyagaric"),
        box("chapeu_ponta", [4.75, 13.6, 6], [8.25, 14.1, 9], "flyagaric"),
        # Chaminé: um cogumelinho saindo do chapéu
        box("chamine_pe", [9.4, 12.6, 4.6], [10.4, 15.2, 5.6], "flyagaricstipe"),
        box("chamine_chapeu", [8.8, 15.2, 4], [11, 16, 6.2], "capbolete", faces={"down": "boletepores"}),
        # Na frente: tronco de cogumelos deitado e uns cogumelos do mato
        box("tronquinho", [0.2, 0, 13], [4.6, 1.6, 15.4], "logbark", faces={"east": "logend", "west": "logend"}),
        box("tronquinho_c1", [0.8, 1.6, 13.4], [2.2, 2.4, 14.8], "capbolete", faces={"down": "boletepores"}),
        box("tronquinho_c2", [2.6, 1.6, 13.7], [3.6, 2.2, 14.7], "capfield"),
        box("cog_pe1", [9.9, 0, 13.9], [10.5, 1.4, 14.5], "stipefield"),
        box("cog_chapeu1", [9.3, 1.4, 13.3], [11.1, 2.2, 15.1], "capfield", faces={"down": "pores"}),
        box("cog_pe2", [11.4, 0, 14.6], [11.8, 0.9, 15], "flyagaricstipe"),
        box("cog_chapeu2", [11, 0.9, 14.2], [12.2, 1.5, 15.4], "flyagaric", faces={"down": "flyagaricpores"}),
    ]
    return out


PROFISSOES["cogumeleiro"] = {
    "title": "Minion Cogumeleiro", "mod": "Tronco de Cogumelos",
    "desc": "Cogumeleiro (versão minion do Tronco de Cogumelos): chapeuzinho de cogumelo, avental de juta, cesto de vime nas costas e faquinha. Mora num toco oco de árvore com um chapéu de cogumelo vermelho de telhado. Cuida dos troncos de cogumelo da área: colhe, ressemeia os vazios com cogumelo do bauzinho e (opcional) monta troncos novos e cata cogumelo do mato.",
    "uni": {
        "camisa": "shirt", "macacao": "overall",
        "chapeu": [box("chapeuzinho", [4.4, 13.1, 4.7], [11.6, 14.3, 11.3], "capbolete", faces={"down": "boletepores"}),
                   box("chapeuzinho_topo", [5.6, 14.3, 5.9], [10.4, 15.1, 10.1], "capbolete")],
        "peito": [box("avental", [5.9, 1.4, 9.75], [10.1, 7.6, 10], "burlapplain"),
                  box("avental_bolso", [6.9, 2.4, 10], [9.1, 4, 10.1], "burlap"),
                  box("avental_cordao", [5.25, 6.8, 6.15], [10.75, 7.2, 9.8], "rope")],
        "costas": cesto_cog,
        "mao": ferramenta(box("faca_cabo", [11.15, 2.6, 7.75], [11.6, 4, 8.2], "darkwood"),
                          box("faca_lamina", [11.2, 0.6, 7.85], [11.55, 2.6, 8.1], "iron")),
    },
    "casa": _toco() + bauzinho(),
}


# ---------------------------------------------------------------------
# IDEIAS NOVAS (só desenho; "novo": True = ainda não vai pro mod)
# ---------------------------------------------------------------------

# 10) TROPEIRO: chapelão, poncho listrado, alforje nas costas e cajado. Casa com estrebaria e carrocinha.
alforje = box("alforje", [5.6, 4.4, 4.4], [10.4, 7.6, 6.25], "couro")
alforje["_kids"] = [box("alforje_tampa", [5.5, 6.8, 4.3], [10.5, 7.8, 6.35], "couro"),
                    box("alforje_fivela", [7.6, 5.6, 4.2], [8.4, 6.4, 4.4], "brass"),
                    box("alforje_rolo", [5.2, 7.6, 4.8], [10.8, 8.6, 5.9], "burlap")]
PROFISSOES["tropeiro"] = {
    "title": "Minion Tropeiro", "mod": "Armazém Central",
    "desc": "Tropeiro: chapelão de couro, poncho listrado, alforje nas costas e cajado. Mora numa casa com estrebaria e carrocinha. Passa nas casinhas dos outros minions, recolhe o que tem nos bauzinhos e leva pros baús do Armazém Central.",
    "uni": {
        "camisa": "red", "macacao": "overall",
        "chapeu": [box("chapelao_aba", [2.8, 13.3, 3.2], [13.2, 13.8, 12.8], "couro"),
                   box("chapelao_copa", [5.3, 13.8, 5.6], [10.7, 15.6, 10.4], "couro"),
                   box("chapelao_fita", [5.2, 13.8, 5.5], [10.8, 14.3, 10.5], "rope")],
        "peito": [box("poncho", [4.9, 5.6, 6], [11.1, 8.1, 10.1], "red"),
                  box("poncho_listra", [4.85, 6.2, 5.95], [11.15, 6.7, 10.15], "yellow"),
                  box("poncho_franja", [4.9, 5.1, 9.9], [11.1, 5.6, 10.15], "burlap")],
        "costas": alforje,
        "mao": ferramenta(box("cajado", [11.15, -0.2, 7.75], [11.6, 9.5, 8.2], "darkwood"),
                          box("cajado_ponta", [11.05, 9.5, 7.65], [11.7, 10.2, 8.3], "corroded")),
    },
    "casa": casinha(parede="planks", canto="darkwood", telhado="tabuinha", cume="darkwood", placa="couro") + [
        # Estrebaria encostada do lado esquerdo: telhadinho e cocho com feno
        box("estreb_poste1", [-2.6, 0, 3.4], [-2, 7, 4], "darkwood"),
        box("estreb_poste2", [-2.6, 0, 10.8], [-2, 7, 11.4], "darkwood"),
        box("estreb_teto", [-3.2, 7, 2.8], [1.2, 7.6, 12], "tabuinha", {"z": -14}, [1.2, 7.3, 7.4]),
        box("cocho", [-2.4, 0, 5], [0.6, 1.6, 9.6], "planks"),
        box("cocho_feno", [-2.1, 1.6, 5.3], [0.3, 2.2, 9.3], "haytop"),
        # Carrocinha na frente com saco e caixote
        box("carroca", [0.4, 1.4, 12.8], [5.4, 2, 15.8], "planks"),
        box("carroca_roda1", [1.6, 0, 12.4], [3.4, 1.8, 12.8], "darkwood"),
        box("carroca_roda2", [1.6, 0, 15.8], [3.4, 1.8, 16.2], "darkwood"),
        box("carroca_eixo", [2.3, 0.7, 12.4], [2.7, 1.1, 16.2], "darkiron"),
        box("carroca_varal", [5.4, 1.5, 13.8], [8.2, 1.9, 14.2], "darkwood"),
        box("carroca_saco", [0.8, 2, 13.2], [2.8, 3.8, 15.2], "linen"),
        box("carroca_caixote", [3, 2, 13.4], [5, 3.6, 15.4], "chestside"),
        box("ferradura", [9.6, 7.3, 12.3], [10.6, 7.5, 12.6], "darkiron"),
    ] + bauzinho(),
}

# 11) PASTOR: gorro de lã, colete de lã, cajado curvo. Casa com cerquinha, cocho, balde de leite e ovos.
PROFISSOES["pastor"] = {
    "title": "Minion Pastor", "mod": "-",
    "desc": "Pastor: gorro de lã, colete de lã e cajado curvo. Mora numa casa com cerquinha, cocho, balde de leite e cesta de ovos. Enche os cochos da área com a ração do bauzinho, recolhe os ovos dos ninhos (deixa os que estão chocando), avisa quando nasce filhote e fecha as porteiras de noite.",
    "uni": {
        "camisa": "shirt", "macacao": "overall",
        "chapeu": [box("gorro_la", [5, 12.8, 5.4], [11, 14.6, 10.6], "linen"),
                   box("gorro_barra", [4.8, 12.6, 5.2], [11.2, 13.3, 10.8], "gray"),
                   box("gorro_pompom", [7.3, 14.6, 7.3], [8.7, 15.6, 8.7], "linen")],
        "peito": [box("colete_la", [5.15, 4, 9.7], [10.85, 7.9, 10], "linen"),
                  box("colete_la_e", [5.1, 4, 6.2], [5.4, 7.9, 9.7], "linen"),
                  box("colete_la_d", [10.6, 4, 6.2], [10.9, 7.9, 9.7], "linen")],
        "costas": None,
        "mao": ferramenta(box("cajado", [11.15, -0.2, 7.75], [11.6, 10.5, 8.2], "darkwood"),
                          box("cajado_curva1", [11.15, 10.5, 7.75], [11.6, 11, 9.6], "darkwood"),
                          box("cajado_curva2", [11.15, 9.4, 9.2], [11.6, 10.5, 9.65], "darkwood")),
    },
    "casa": casinha(parede="planks", canto="mossy", telhado="straw", cume="hay", placa="linen") + [
        # Cerquinha na frente com porteira
        box("cerca_p1", [0.2, 0, 15.2], [0.8, 3.4, 15.8], "darkwood"),
        box("cerca_p2", [3.4, 0, 15.2], [4, 3.4, 15.8], "darkwood"),
        box("cerca_r1", [0.2, 1.2, 15.35], [4, 1.7, 15.65], "planks"),
        box("cerca_r2", [0.2, 2.5, 15.35], [4, 3, 15.65], "planks"),
        box("cerca_p3", [0.2, 0, 12.8], [0.8, 3.4, 13.4], "darkwood"),
        box("cerca_r3", [0.35, 1.2, 13.4], [0.65, 1.7, 15.2], "planks"),
        box("cerca_r4", [0.35, 2.5, 13.4], [0.65, 3, 15.2], "planks"),
        box("porteira", [4, 0.6, 15.3], [6.6, 3, 15.7], "planks", {"y": -30}, [4, 1, 15.5]),
        # Cocho com feno, balde de leite e cesta de ovos
        box("cocho", [1.2, 0, 13.2], [3.8, 1.4, 14.8], "planks"),
        box("cocho_feno", [1.4, 1.4, 13.4], [3.6, 1.9, 14.6], "haytop"),
        box("balde", [9.6, 0, 13.4], [11.4, 2, 15.2], "planks"),
        box("balde_aro", [9.5, 1.4, 13.3], [11.5, 1.8, 15.3], "darkiron"),
        box("balde_leite", [9.8, 1.9, 13.6], [11.2, 2, 15], "white"),
        box("cesta_ovos", [6.6, 0, 13.4], [8.6, 1.2, 15], "basketside"),
        box("ovo1", [6.9, 1.2, 13.7], [7.6, 1.8, 14.4], "white"),
        box("ovo2", [7.7, 1.2, 14.1], [8.3, 1.7, 14.7], "white"),
        box("la", [-0.6, 0, 4], [1, 1.6, 7], "linen"),
    ] + bauzinho(),
}

# 12) FERREIRO: bandana, avental de couro grosso e martelo. Casa de pedra com forja acesa e bigorna.
PROFISSOES["ferreiro"] = {
    "title": "Minion Ferreiro", "mod": "Bancada de Remendos",
    "desc": "Ferreiro: bandana, avental de couro grosso, cara suja de fuligem e martelo. Mora numa casa de pedra com forja acesa do lado e bigorna na frente. Conserta as ferramentas e armaduras que você deixa no bauzinho, gastando um pouco de metal e carvão.",
    "uni": {
        "camisa": "gray", "macacao": "overall",
        "chapeu": [box("bandana", [4.9, 12, 5.3], [11.1, 13.6, 10.7], "wool"),
                   box("bandana_no", [7.4, 11.6, 4.5], [8.6, 12.8, 5.4], "wool")],
        "rosto": [box("fuligem", [5.8, 9.4, 10.45], [6.8, 9.9, 10.55], "coal")],
        "peito": [box("avental", [5.7, 1.2, 9.75], [10.3, 7.8, 10.05], "couro"),
                  box("avental_cordao", [5.25, 6.8, 6.15], [10.75, 7.2, 9.8], "couro"),
                  box("avental_bolso", [6.6, 2.6, 10.05], [9.4, 4, 10.15], "couro")],
        "costas": None,
        "mao": ferramenta(box("martelo_cabo", [11.15, 0.6, 7.75], [11.6, 5, 8.2], "darkwood"),
                          box("martelo_cabeca", [10.6, -0.4, 7.2], [12.15, 0.8, 8.75], "darkiron")),
    },
    "casa": casinha(parede="cobble", canto="brick", telhado="telha_cinza", cume="darkiron", placa="darkiron", chamine=None) + [
        # Forja encostada do lado esquerdo, com chaminé alta e fole
        box("forja", [-2.4, 0, 4], [1, 3.4, 9.6], "brick"),
        box("forja_brasa", [-2, 3.4, 4.4], [0.6, 3.8, 9.2], "ember", glow=200),
        box("forja_chamine", [-2, 3.8, 4.8], [0.4, 15, 7.2], "brick"),
        box("forja_fole", [-2.6, 0.6, 9.6], [0.2, 2.2, 11.4], "couro"),
        # Bigorna no cepo, na frente
        box("cepo", [0.8, 0, 13], [3.8, 2, 15.6], "logbark", faces={"up": "logend"}),
        box("bigorna_pe", [1.6, 2, 13.8], [3, 2.9, 14.8], "darkiron"),
        box("bigorna_topo", [0.9, 2.9, 13.6], [3.6, 3.7, 15], "darkiron"),
        box("bigorna_bico", [3.6, 3.1, 13.9], [4.6, 3.6, 14.7], "darkiron"),
        box("lingote", [1.4, 3.7, 14], [2.4, 4, 14.5], "corroded"),
        # Barril de água e ferramentas penduradas
        box("barril", [9.4, 0, 13.2], [11.6, 2.8, 15.4], "planks"),
        box("barril_aro", [9.3, 1.8, 13.1], [11.7, 2.2, 15.5], "darkiron"),
        box("barril_agua", [9.6, 2.6, 13.4], [11.4, 2.75, 15.2], "water"),
        box("pinca", [9.4, 2.4, 12.3], [9.8, 6, 12.5], "darkiron"),
        box("ferradura", [10.2, 5.6, 12.3], [11.2, 5.8, 12.6], "darkiron"),
    ] + bauzinho(),
}

# 13) LAMPARINEIRO: cartola, casaco azul, cachecol e vara comprida com lanterna acesa. Casa com poste de lampião.
PROFISSOES["lamparineiro"] = {
    "title": "Minion Lamparineiro", "mod": "-",
    "desc": "Lamparineiro: cartola, casaco azul com botões de latão, cachecol vermelho e uma vara comprida com a lanterna acesa. Mora numa casa de pedra com poste de lampião na frente. De noite faz a ronda acendendo as tochas e lanternas apagadas da área e troca as que acabaram, com as do bauzinho.",
    "uni": {
        "camisa": "blue", "macacao": "wool",
        "chapeu": [box("cartola_aba", [4.2, 13.3, 4.5], [11.8, 13.7, 11.5], "wool"),
                   box("cartola_copa", [5.4, 13.7, 5.7], [10.6, 17.2, 10.3], "wool"),
                   box("cartola_fita", [5.35, 13.7, 5.65], [10.65, 14.4, 10.35], "red")],
        "peito": [box("casaco", [5.15, 2.4, 9.7], [10.85, 8, 10], "blue"),
                  box("casaco_botao1", [7.75, 6.2, 10], [8.25, 6.7, 10.1], "brass"),
                  box("casaco_botao2", [7.75, 4.6, 10], [8.25, 5.1, 10.1], "brass"),
                  box("cachecol", [5.6, 7.4, 6.2], [10.4, 8.2, 10.1], "red")],
        "costas": None,
        "mao": ferramenta(box("vara", [11.15, -1, 7.75], [11.6, 12, 8.2], "darkwood"),
                          box("vara_gancho", [11.15, 12, 7.75], [11.6, 12.5, 9.6], "darkiron"),
                          box("vara_lanterna", [10.7, 10, 8.9], [12, 11.9, 10.2], "glass"),
                          box("vara_chama", [11.1, 10.4, 9.3], [11.6, 11.3, 9.8], "flame", glow=220)),
    },
    "casa": casinha(parede="cobble", canto="darkwood", telhado="telha_marrom", cume="darkwood", placa="brass") + [
        # Poste de lampião na frente
        box("poste_base", [0.8, 0, 13.2], [2.6, 0.8, 15], "cobble"),
        box("poste", [1.4, 0.8, 13.8], [2, 10.5, 14.4], "darkiron"),
        box("poste_braco", [1.4, 10.5, 13.8], [4.2, 10.9, 14.4], "darkiron"),
        box("lampiao", [3, 8.4, 13.4], [4.8, 10.5, 14.8], "glass"),
        box("lampiao_topo", [2.8, 10.5, 13.2], [5, 10.9, 15], "darkiron"),
        box("lampiao_luz", [3.5, 8.9, 13.8], [4.3, 10, 14.4], "flame", glow=230),
        box("escada", [5.6, 0, 14.6], [6.4, 6, 14.9], "planks", {"x": -18}, [6, 0, 14.75]),
        # Caixote de velas e tochas
        box("caixote", [9.4, 0, 13.2], [11.6, 1.8, 15.4], "chestside"),
        box("tocha1", [9.8, 1.8, 13.6], [10.2, 3.4, 14], "darkwood"),
        box("tocha2", [10.6, 1.8, 14.2], [11, 3.2, 14.6], "darkwood"),
        box("vela", [10.4, 1.8, 13.5], [10.8, 2.8, 13.9], "wax"),
    ] + bauzinho(),
}

# 14) OLEIRO: lenço azul, avental sujo de barro e um vaso na mão. Casa de barro com forno de olaria redondo.
PROFISSOES["oleiro"] = {
    "title": "Minion Oleiro", "mod": "-",
    "desc": "Oleiro: lenço azul na cabeça, avental sujo de barro e um vaso na mão. Mora numa casa de barro com telhado de telha e um forno de olaria redondo do lado. Pega o barro do bauzinho, faz vasos, potes e telhas e queima no forno; trabalha dentro de casa, como o Carvoeiro.",
    "uni": {
        "camisa": "shirt", "macacao": "overall",
        "chapeu": [box("lenco_cabeca", [4.9, 12, 5.3], [11.1, 13.9, 10.7], "blue"),
                   box("lenco_no", [7.4, 11.6, 4.5], [8.6, 12.8, 5.4], "blue")],
        "peito": [box("avental", [5.9, 1.4, 9.75], [10.1, 7.6, 10], "burlapplain"),
                  box("avental_barro1", [6.4, 2.2, 10], [7.8, 3.4, 10.05], "fired"),
                  box("avental_barro2", [8.4, 4.4, 10], [9.4, 5.2, 10.05], "fired"),
                  box("avental_cordao", [5.25, 6.8, 6.15], [10.75, 7.2, 9.8], "rope")],
        "costas": None,
        "mao": ferramenta(box("vaso", [10.5, 0.8, 7.3], [12.3, 3.6, 9.1], "fired"),
                          box("vaso_boca", [10.8, 3.6, 7.6], [12, 4.1, 8.8], "fired")),
    },
    "casa": casinha(parede="kilnwall", canto="darkwood", telhado="telha_vermelha", cume="fired", placa="fired", chamine="chimney") + [
        # Forno de olaria redondo (em degraus) do lado esquerdo, com a boca acesa
        box("forno_base", [-3, 0, 4], [1.2, 2.4, 10], "kilnwall"),
        box("forno_meio", [-2.6, 2.4, 4.6], [0.8, 4.2, 9.4], "kilnwall"),
        box("forno_topo", [-2, 4.2, 5.4], [0.2, 5.4, 8.6], "kilnwall"),
        box("forno_chamine", [-1.3, 5.4, 6.3], [-0.5, 6.6, 7.7], "chimney"),
        box("forno_boca", [-3.1, 0.4, 6], [-2.9, 1.9, 8], "ember", glow=180),
        # Vasos, pote, telhas, barro cru e a roda de oleiro na frente
        box("vaso1", [0.6, 0, 13.2], [2.6, 2.6, 15.2], "fired"),
        box("vaso1_boca", [0.9, 2.6, 13.5], [2.3, 3, 14.9], "fired"),
        box("pote", [3, 0, 13.6], [4.6, 1.6, 15.2], "pumpkin"),
        box("telhas", [9.4, 0, 13.2], [11.8, 1.2, 15.6], "telha_vermelha"),
        box("barro_cru", [6.8, 0, 13.6], [8.4, 1, 15.2], "kilnfront"),
        box("roda_oleiro", [5, 0, 13.4], [6.4, 1.4, 14.8], "darkwood"),
    ] + bauzinho(),
}

PROF_MODELS = {}
for _k, _p in PROFISSOES.items():
    _parts = {"casa": {"label": "Casinha + bauzinho", "elements": _p["casa"]},
              "minion": {"label": _p["title"].replace("Minion ", ""), "elements": lufinho(copy.deepcopy(_p["uni"]))}}
    for _ek, _e in _p.get("extras", {}).items():
        _parts[_ek] = {"label": _e["label"], "elements": _e["els"]}
    PROF_MODELS["minion_" + _k] = {
        "title": _p["title"], "parts": _parts, "animations": LUFINHO_ANIMS,
        "profissao": {"desc": _p["desc"], "extras": {k: {"pivot": e["pivot"], "spin": e.get("spin"), "swing": e.get("swing")}
                                                       for k, e in _p.get("extras", {}).items()}},
    }


# =====================================================================
# LANCHEIRA — marmita de lata velha (item): pintura vermelha desbotada, cantos de ferro enferrujado,
# alça de couro, fecho de latão, dobradiça atrás e um adesivo velho na frente. A tampa abre (pivô na dobradiça).
# =====================================================================
lancheira_base = [
    # Lata oca (dá pra ver a comida com a tampa aberta)
    box("chao", [3, 0.5, 5], [13, 1, 11], "darkiron"),
    box("parede_frente", [3, 0.5, 10.4], [13, 6, 11], "enamel"),
    box("parede_tras", [3, 0.5, 5], [13, 6, 5.6], "enamel"),
    box("parede_esq", [3, 0.5, 5.6], [3.6, 6, 10.4], "enamel"),
    box("parede_dir", [12.4, 0.5, 5.6], [13, 6, 10.4], "enamel"),
    box("fundo", [2.8, 0, 4.8], [13.2, 0.6, 11.2], "darkiron"),
    box("borda_f", [2.85, 5.6, 10.55], [13.15, 6, 11.15], "darkiron"),
    box("borda_t", [2.85, 5.6, 4.85], [13.15, 6, 5.45], "darkiron"),
    box("borda_e", [2.85, 5.6, 5.45], [3.45, 6, 10.55], "darkiron"),
    box("borda_d", [12.55, 5.6, 5.45], [13.15, 6, 10.55], "darkiron"),
    box("canto_fe", [2.75, 0, 10.75], [3.35, 6, 11.25], "darkiron"),
    box("canto_fd", [12.65, 0, 10.75], [13.25, 6, 11.25], "darkiron"),
    box("canto_te", [2.75, 0, 4.75], [3.35, 6, 5.25], "darkiron"),
    box("canto_td", [12.65, 0, 4.75], [13.25, 6, 5.25], "darkiron"),
    box("ferrugem1", [9.5, 0.6, 10.98], [11.5, 2.2, 11.06], "corroded"),
    box("ferrugem2", [3.2, 3.2, 10.98], [4.4, 4.6, 11.06], "corroded"),
    box("adesivo", [3.9, 1.4, 11], [6.7, 4.2, 11.08], "paper"),
    box("adesivo_faixa", [3.9, 3.2, 11.02], [6.7, 3.7, 11.1], "purple"),
    box("trava_baixo", [7.3, 3.8, 11], [8.7, 4.8, 11.35], "brass"),
    box("dobradica", [4, 5.5, 4.55], [12, 6.3, 5.05], "darkiron"),
    box("rebite1", [3.6, 1, 10.98], [4.1, 1.5, 11.12], "corroded"),
    box("rebite2", [11.9, 1, 10.98], [12.4, 1.5, 11.12], "corroded"),
]

LANCHEIRA_TAMPA = [8, 6.1, 4.8]
lancheira_tampa = [
    box("tampa", [2.8, 6, 4.8], [13.2, 7.8, 11.2], "enamel"),
    box("tampa_borda", [2.75, 6, 4.75], [13.25, 6.5, 11.25], "darkiron"),
    box("tampa_topo", [3.4, 7.8, 5.4], [12.6, 8.3, 10.6], "enamel"),
    box("trava_cima", [7.3, 6.3, 11.2], [8.7, 7.6, 11.5], "brass"),
    box("alca_pe1", [5.6, 8.3, 7.4], [6.4, 9.6, 8.6], "darkiron"),
    box("alca_pe2", [9.6, 8.3, 7.4], [10.4, 9.6, 8.6], "darkiron"),
    box("alca", [5.4, 9.6, 7.5], [10.6, 10.4, 8.5], "leather"),
    box("tampa_ferrugem", [9.8, 7.82, 8.5], [11.8, 7.9, 10.2], "corroded"),
]

# Comida guardada (aparece com a tampa aberta): 3 espaços, como na lancheira do jogo
lancheira_comida = [
    box("pao", [3.9, 1, 5.9], [7, 4.8, 10.1], "bread"),
    box("frutinhas", [7.3, 1, 5.9], [10, 4.2, 7.9], "blueberry"),
    box("carne", [7.3, 1, 8.2], [12.1, 3.8, 10.1], "smoked"),
    box("queijo", [10.3, 1, 5.9], [12.1, 4.5, 7.9], "cheese"),
]

MODELS = {
    **PROF_MODELS,
    "moedor": {
        "title": "Moedor Automático",
        "parts": {
            "base": {"label": "Base (parada)", "elements": moedor_base},
            "mo": {"label": "Mó (gira deitada)", "elements": moedor_mo},
            "roda": {"label": "Roda d'água (gira)", "elements": moedor_roda},
        },
    },
    "peneira": {
        "title": "Peneira Automática",
        "parts": {
            "base": {"label": "Base (parada)", "elements": peneira_base},
            "pan": {"label": "Peneira (chacoalha)", "elements": peneira_pan},
            "roda": {"label": "Roda d'água (gira)", "elements": water_wheel()},
        },
    },
    "pesca": {
        "title": "Pesca Automática",
        "parts": {
            "base": {"label": "Base (parada)", "elements": pesca_base},
            "roda": {"label": "Roda de pesca (gira)", "elements": fish_wheel()},
        },
    },
    "cogumelos": {
        "title": "Tronco de Cogumelos",
        "parts": {
            "base": {"label": "Tora (parada)", "elements": cogumelo_base},
            "cogumelos": {"label": "Cogumelos nascendo", "elements": cogumelo_cogumelos},
            "bandeja": {"label": "Bandeja com colhidos", "elements": cogumelo_bandeja},
        },
    },
    "minion": {
        "title": "Minion Colhedor",
        "parts": {
            "casa": {"label": "Casinha da colheita + bauzinho", "elements": minion_casa},
            "minion": {"label": "Colhedor (pequenininho)", "elements": MINION_ELEMENTS},
        },
        "animations": MINION_ANIMS,
    },
    "lancheira": {
        "title": "Lancheira",
        "parts": {
            "base": {"label": "Lata (corpo)", "elements": lancheira_base},
            "tampa": {"label": "Tampa (abre)", "elements": lancheira_tampa},
            "comida": {"label": "Comida dentro", "elements": lancheira_comida},
        },
    },
    "espantalho": {
        "title": "Espantalho Vigia",
        "parts": {
            "base": {"label": "Base (parada)", "elements": espantalho_base},
            "corpo": {"label": "Corpo (balança)", "elements": espantalho_corpo},
            "lanterna": {"label": "Lanterna (pendurada)", "elements": espantalho_lanterna},
        },
    },
    "carvoeira": {
        "title": "Carvoeira",
        "parts": {
            "base": {"label": "Forno (parado)", "elements": carvoeira_base},
            "brasa": {"label": "Brasa", "elements": carvoeira_brasa},
            "porta": {"label": "Porta (abre)", "elements": carvoeira_porta},
        },
    },
    "bancada": {
        "title": "Bancada de Remendos",
        "parts": {
            "base": {"label": "Bancada (parada)", "elements": bancada_base},
            "rebolo": {"label": "Rebolo (gira)", "elements": bancada_rebolo},
        },
    },
    "colmeia": {
        "title": "Colmeia Coletora",
        "parts": {
            "base": {"label": "Colmeia (parada)", "elements": colmeia_base},
            "mel": {"label": "Favo na gaveta", "elements": colmeia_mel},
        },
    },
    "serraria": {
        "title": "Serraria d'Água",
        "parts": {
            "base": {"label": "Base (parada)", "elements": serraria_base},
            "serra": {"label": "Serra (gira)", "elements": serraria_serra},
            "tora": {"label": "Tora (passa)", "elements": serraria_tora},
            "roda": {"label": "Roda d'água (gira)", "elements": water_wheel()},
        },
    },
    "sino": {
        "title": "Sino de Alarme",
        "parts": {
            "base": {"label": "Poste (parado)", "elements": sino_base},
            "sino": {"label": "Sino (balança)", "elements": sino_sino},
        },
    },
    "armazem": {
        "title": "Armazém Central",
        "parts": {
            "base": {"label": "Armário (parado)", "elements": armazem_base},
        },
    },
    "defumador": {
        "title": "Defumador",
        "parts": {
            "base": {"label": "Base (parada)", "elements": defumador_base},
            "brasa": {"label": "Brasa", "elements": defumador_brasa},
            "carga": {"label": "Carne/peixe pendurado", "elements": defumador_carga},
        },
    },
}


AUTO_MODELS = carregar_automacao()


def shape(elements):
    return {"textureWidth": 16, "textureHeight": 16, "textures": TEXTURES, "elements": elements}


VSMODS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_SHAPES = os.path.join(os.environ.get("APPDATA", ""), "Vintagestory", "assets", "survival", "shapes")


def tex_path(loc):
    """'game:block/x' ou 'block/x' -> 'block/x' (texturas do jogo)."""
    return loc.split(":", 1)[1] if ":" in loc else loc


def scale_uv(elements, sw, sh):
    """Converte UV de shapes com textura maior que 16 para a escala 16 do visualizador."""
    for e in elements:
        for f in (e.get("faces") or {}).values():
            if "uv" in f:
                u = f["uv"]
                f["uv"] = [u[0] * 16 / sw, u[1] * 16 / sh, u[2] * 16 / sw, u[3] * 16 / sh]
        scale_uv(e.get("children") or [], sw, sh)


def load_shape(path, overrides=None):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    tw, th = data.get("textureWidth", 16), data.get("textureHeight", 16)
    if tw != 16 or th != 16:
        scale_uv(data["elements"], tw, th)
    texs = {k: tex_path(v) for k, v in (data.get("textures") or {}).items()}
    for k, v in (overrides or {}).items():
        texs[k] = tex_path(v)
    return data["elements"], texs


def done_models():
    """Mods que já existem, lidos direto das pastas dos projetos."""
    out = {}

    sh = os.path.join(VSMODS, "Sentinela", "assets", "sentinela", "shapes", "block")
    base, t1 = load_shape(os.path.join(sh, "sentinela-base.json"))
    head, t2 = load_shape(os.path.join(sh, "sentinela-head.json"))
    out["sentinela"] = {"title": "Sentinela", "group": "feito", "textures": {**t1, **t2,
                        "lensglow": "block/machine/statictranslocator/rustyglow"},
                        "parts": {"base": {"label": "Base (parada)", "elements": base},
                                  "head": {"label": "Cabeça (gira)", "elements": head}}}

    return out


# Mods trocados pelos minions (zips em ModsRemovidos): fora do visualizador e da galeria de ícones
REMOVIDOS = {"moedor": "MoedorAutomatico", "peneira": "PeneiraAutomatica", "pesca": "PescaAutomatica",
             "carvoeira": "Carvoeira", "colmeia": "ColmeiaColetora", "serraria": "SerrariaAgua",
             "defumador": "Defumador", "sino": "SinoAlarme"}


def main():
    tex_dir = sys.argv[1]
    here = os.path.dirname(os.path.abspath(__file__))

    # Formas no formato do jogo (só dos modelos novos; vão pros mods quando aprovar)
    out_shapes = os.path.join(here, "shapes")
    os.makedirs(out_shapes, exist_ok=True)
    for key, m in {**MODELS, **AUTO_MODELS}.items():
        for part, p in m["parts"].items():
            with open(os.path.join(out_shapes, f"{key}-{part}.json"), "w", encoding="utf-8") as f:
                json.dump(shape(p["elements"]), f, indent=1)

    # Modelos desenhados aqui: viram "já feito" quando a pasta do mod existe
    MOD_FOLDERS = {"moedor": "MoedorAutomatico", "peneira": "PeneiraAutomatica", "espantalho": "EspantalhoVigia",
                   "defumador": "Defumador", "carvoeira": "Carvoeira", "bancada": "BancadaRemendos",
                   "colmeia": "ColmeiaColetora", "serraria": "SerrariaAgua", "sino": "SinoAlarme", "armazem": "ArmazemCentral", "pesca": "PescaAutomatica", "cogumelos": "TroncoCogumelos", "bruxa": "BruxaColhedora", "minion": "MinionColhedor", "lancheira": "Lancheira", **{k: "MinionsOficios" for k in PROF_MODELS
                                                                         if not PROFISSOES[k[7:]].get("novo")}}
    ordered = {}
    for key, m in AUTO_MODELS.items():
        texs = {k: tex_path(v) for k, v in TEXTURES.items()}
        ordered[key] = {**m, "group": "auto", "textures": texs}
    for key, m in MODELS.items():
        if key in REMOVIDOS:
            continue
        feito = os.path.isdir(os.path.join(VSMODS, MOD_FOLDERS.get(key, "-")))
        texs = {k: tex_path(v) for k, v in TEXTURES.items()}
        texs.update(m.get("extraTextures", {}))
        ordered[key] = {**m, "group": "feito" if feito else "novo", "textures": texs}
    ordered.update(done_models())

    # Texturas do jogo embutidas no visualizador (por caminho, sem repetir)
    textures = {}
    for m in ordered.values():
        for path in m["textures"].values():
            if path in textures:
                continue
            if path.startswith("custom/"):
                file = os.path.join(here, "tex", path.split("/", 1)[1] + ".png")
            else:
                file = os.path.join(tex_dir, path.replace("/", os.sep) + ".png")
            if not os.path.exists(file):
                print("textura não encontrada:", path)
                continue
            with open(file, "rb") as f:
                textures[path] = "data:image/png;base64," + base64.b64encode(f.read()).decode()

    with open(os.path.join(here, "template.html"), encoding="utf-8") as f:
        html = f.read()
    # Ícones de todos os mods (modicon.png de cada pasta), pra aba "Ícones"
    icons = {}
    for d in sorted(os.listdir(VSMODS)):
        ic = os.path.join(VSMODS, d, "modicon.png")
        if d.startswith("_") or d in REMOVIDOS.values() or not os.path.exists(ic):
            continue
        name = d
        try:
            with open(os.path.join(VSMODS, d, "modinfo.json"), encoding="utf-8") as f:
                name = json.load(f).get("name", d)
        except Exception:
            pass
        with open(ic, "rb") as f:
            icons[name] = "data:image/png;base64," + base64.b64encode(f.read()).decode()
    html = html.replace("/*MODELS*/null", json.dumps(ordered)).replace("/*TEXTURES*/null", json.dumps(textures))
    html = html.replace("/*ICONS*/null", json.dumps(icons))
    out = os.path.join(here, "modelos-3d.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    for key, m in ordered.items():
        print(key, {p: len(v["elements"]) for p, v in m["parts"].items()})
    print("ok ->", out)


if __name__ == "__main__":
    main()
