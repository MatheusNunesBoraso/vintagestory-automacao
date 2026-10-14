"""
Fotos bonitas de cada peça da Automação pro README (docs/img/<chave>.png) + o ícone do mod.

Uso: py -I gen_imagens.py [chave ...]   (sem chave = todas, + a cena da rede + modicon)
"""
import base64
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "_modelos3d"))
import gen_modelos as g  # noqa: E402

TEX_DIR = os.path.join(os.environ["APPDATA"], "Vintagestory", "assets", "survival", "textures")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = os.path.join(HERE, "img")


def tex_data(loc):
    path = os.path.join(TEX_DIR, loc.split(":", 1)[-1] + ".png")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def used(elements, acc):
    for e in elements:
        for fc in e["faces"].values():
            acc.add(fc["texture"].lstrip("#"))
        used(e.get("children") or [], acc)
    return acc


def elementos(key):
    m = g.AUTO_MODELS[key]
    a = m["auto"]
    modes = [x[0] for x in a.get("modes") or [["parado"], ["ligado"]]]
    mode = a.get("default") or modes[-1]
    show = a.get("show") or {}
    els = []
    for pk, p in m["parts"].items():
        if pk in show and mode not in show[pk]:
            continue
        els += [e for e in p["elements"] if e["name"] not in show or mode in show[e["name"]]]
    glow = set(a.get("glowTex") or ["luz"])
    return els, glow, a


HTML = """<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:radial-gradient(circle at 50%% 42%%,#2c3f52 0%%,#141b24 70%%,#0d1218 100%%)}canvas{display:block}</style></head><body>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const ELS = %(els)s, TEX = %(tex)s, GLOW = %(glow)s, CAM = %(cam)s, ALVO = %(alvo)s, W = %(w)d, H = %(h)d, CHAO = %(chao)s, ICONE = %(icone)s, AGUA = %(agua)s;
const r = new THREE.WebGLRenderer({antialias:true, alpha:true, preserveDrawingBuffer:true});
r.setSize(W, H); r.setPixelRatio(1); document.body.appendChild(r.domElement);
const scene = new THREE.Scene();
scene.add(new THREE.HemisphereLight(0xfff4e0, 0x404858, 0.85));
const sun = new THREE.DirectionalLight(0xffffff, 0.75); sun.position.set(3, 6, 4); scene.add(sun);
const fill = new THREE.DirectionalLight(0x9fc4ff, 0.25); fill.position.set(-4, 2, -3); scene.add(fill);
const cam = new THREE.PerspectiveCamera(30, W / H, 0.02, 200); cam.position.set(...CAM); cam.lookAt(...ALVO);
const imgs = {}; let n = 0; const total = Object.keys(TEX).length;
for (const [k, v] of Object.entries(TEX)) { const i = new Image(); i.onload = i.onerror = () => { if (++n === total) build(); }; i.src = v; imgs[k] = i; }
function tex(code, uv, rep) {
  const t = new THREE.Texture(imgs[code]); t.needsUpdate = true;
  t.magFilter = t.minFilter = THREE.NearestFilter; t.wrapS = t.wrapT = THREE.RepeatWrapping;
  uv = uv || [0, 0, 16, 16]; t.repeat.set((uv[2] - uv[0]) / 16 * (rep || 1), (uv[3] - uv[1]) / 16 * (rep || 1)); t.offset.set(uv[0] / 16, 1 - uv[3] / 16); return t;
}
const ORDER = ['east', 'west', 'up', 'down', 'south', 'north'];
const D = THREE.MathUtils.degToRad;
function addEl(el, parent, base) {
  const f = el.from.map((v, i) => v + base[i]), t = el.to.map((v, i) => v + base[i]);
  const w = Math.max(0.01, t[0] - f[0]), h = Math.max(0.01, t[1] - f[1]), d = Math.max(0.01, t[2] - f[2]);
  const mats = ORDER.map(k => { const fc = el.faces[k]; if (!fc || !imgs[fc.texture.slice(1)]) return new THREE.MeshBasicMaterial({visible: false});
    const code = fc.texture.slice(1); const M = GLOW.includes(code) ? THREE.MeshBasicMaterial : THREE.MeshLambertMaterial;
    return new M({map: tex(code, fc.uv), transparent: true, alphaTest: 0.1}); });
  const o = el.rotationOrigin ? el.rotationOrigin.map((v, i) => v + base[i]) : [f[0] + w / 2, f[1] + h / 2, f[2] + d / 2];
  const p = new THREE.Group(); p.position.set(o[0] / 16, o[1] / 16, o[2] / 16);
  p.rotation.set(D(el.rotationX || 0), D(el.rotationY || 0), D(el.rotationZ || 0));
  const holder = new THREE.Group(); holder.position.set(-o[0] / 16, -o[1] / 16, -o[2] / 16); p.add(holder);
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w / 16, h / 16, d / 16), mats);
  mesh.position.set((f[0] + w / 2) / 16, (f[1] + h / 2) / 16, (f[2] + d / 2) / 16); holder.add(mesh);
  parent.add(p);
  for (const c of el.children || []) addEl(c, holder, f);
}
function build() {
  for (const el of ELS) addEl(el, scene, [0, 0, 0]);
  if (CHAO) {
    const gt = tex(CHAO, null, CHAO_N * 1.5);
    const ground = new THREE.Mesh(new THREE.BoxGeometry(CHAO_N, 0.1, CHAO_N), new THREE.MeshLambertMaterial({map: gt}));
    ground.position.set(ALVO[0], -0.05, ALVO[2]); scene.add(ground);
  }
  if (AGUA) {
    const w = new THREE.Mesh(new THREE.BoxGeometry(AGUA[2] - AGUA[0], 5 / 16, AGUA[3] - AGUA[1]), new THREE.MeshLambertMaterial({color: 0x2f6e9e, transparent: true, opacity: 0.6}));
    w.position.set((AGUA[0] + AGUA[2]) / 2, 2.5 / 16, (AGUA[1] + AGUA[3]) / 2); scene.add(w);
  }
  r.render(scene, cam);
  if (ICONE) {
    const c = document.createElement('canvas'); c.width = 256; c.height = 256; document.body.innerHTML = ''; document.body.appendChild(c);
    const x = c.getContext('2d');
    const rr = (a, b, w, h, rad) => { x.beginPath(); x.moveTo(a + rad, b); x.arcTo(a + w, b, a + w, b + h, rad); x.arcTo(a + w, b + h, a, b + h, rad); x.arcTo(a, b + h, a, b, rad); x.arcTo(a, b, a + w, b, rad); x.closePath(); };
    rr(4, 4, 248, 248, 28); x.save(); x.clip();
    const bg = x.createRadialGradient(128, 110, 20, 128, 128, 190); bg.addColorStop(0, '#24465a'); bg.addColorStop(1, '#0b141c');
    x.fillStyle = bg; x.fillRect(0, 0, 256, 256); x.drawImage(r.domElement, 0, 0, 256, 256); x.restore();
    rr(4, 4, 248, 248, 28); x.lineWidth = 5; x.strokeStyle = '#6fe8ff'; x.stroke();
    rr(8, 8, 240, 240, 24); x.lineWidth = 1.5; x.strokeStyle = 'rgba(200,250,255,0.35)'; x.stroke();
  }
  document.title = 'pronto';
}
const CHAO_N = %(chao_n)s;
</script></body></html>"""


def render(nome, els, glow, cam, alvo, w=720, h=720, chao="cobble", icone=False, agua=None, chao_n=1.8):
    codes = used(els, set()) | ({chao} if chao else set())
    textures = {}
    for c in codes:
        if c in g.TEXTURES:
            d = tex_data(g.TEXTURES[c])
            if d:
                textures[c] = d
    html = HTML % {"els": json.dumps(els), "tex": json.dumps(textures), "glow": json.dumps(sorted(glow)), "cam": json.dumps(cam),
                   "alvo": json.dumps(alvo), "w": w, "h": h, "chao": json.dumps(chao), "icone": json.dumps(icone),
                   "agua": json.dumps(agua), "chao_n": chao_n}
    tmp = os.path.join(tempfile.gettempdir(), f"img_{nome}.html")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(html)
    out = os.path.join(OUT, nome + ".png")
    prof = os.path.join(tempfile.gettempdir(), "img_edge_prof")
    size = (256, 256) if icone else (w, h)
    subprocess.run([EDGE, "--headless=new", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", f"--user-data-dir={prof}",
                    "--hide-scrollbars", "--default-background-color=00000000", f"--window-size={size[0]},{size[1]}",
                    "--virtual-time-budget=15000", f"--screenshot={out}", "file:///" + tmp.replace("\\", "/")],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=900)
    print("ok", nome)


def enquadrar(els):
    lo = [min(min(e["from"][i], e["to"][i]) for e in els) / 16 for i in range(3)]
    hi = [max(max(e["from"][i], e["to"][i]) for e in els) / 16 for i in range(3)]
    c = [(lo[i] + hi[i]) / 2 for i in range(3)]
    r = max(hi[i] - lo[i] for i in range(3))
    r = max(r, 1.0)
    return [c[0] + r * 1.95, c[1] + r * 1.25, c[2] + r * 2.55], c


def main():
    os.makedirs(OUT, exist_ok=True)
    chaves = sys.argv[1:] or [k for k in g.AUTO_MODELS if k != "auto_rede"] + ["auto_rede", "modicon"]
    for k in chaves:
        if k == "modicon":
            els, glow, a = elementos("auto_poste")
            render("modicon", els, glow, [2.6, 2.0, 4.3], [0.5, 1.08, 0.5], 512, 512, chao=None, icone=True)
            continue
        els, glow, a = elementos(k)
        if k == "auto_rede":
            glow = set()
            for m in g.AUTO_MODELS.values():
                glow |= set(m["auto"].get("glowTex") or ["luz"])
            render("rede", els, glow, [-8, 17, 22], [-8, 0, 0], 1600, 900, chao="cobble", agua=[1, -12, 5, 4], chao_n=34)
            continue
        cam, alvo = enquadrar(els)
        render(k[len("auto_"):], els, glow, cam, alvo, agua=[1, -0.5, 3, 1.5] if a.get("agua") else None)


if __name__ == "__main__":
    main()
