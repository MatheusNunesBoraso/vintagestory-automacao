"""
Prévia rápida (PNG com 3 ângulos) de um modelo da Automação, sem gerar o visualizador inteiro.

Uso: py -I previa_auto.py <chave do modelo> <saida.png> [modo]
  - modo: escolhe o que aparece (auto['show']) e se a textura 'luz' brilha (auto['glow']).
Precisa do Edge (headless) instalado.
"""
import base64
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_modelos as g  # noqa: E402

TEX_DIR = os.path.join(os.environ["APPDATA"], "Vintagestory", "assets", "survival", "textures")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def tex_data(loc):
    path = os.path.join(TEX_DIR, loc.split(":", 1)[-1] + ".png")
    if not os.path.exists(path):
        print("textura não encontrada:", loc)
        return None
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def used(elements, acc):
    for e in elements:
        for fc in e["faces"].values():
            acc.add(fc["texture"].lstrip("#"))
        used(e.get("children") or [], acc)
    return acc


def main():
    key, out = sys.argv[1], os.path.abspath(sys.argv[2])
    model = g.AUTO_MODELS[key]
    a = model["auto"]
    modes = [m[0] for m in a.get("modes") or [["parado"], ["ligado"]]]
    mode = sys.argv[3] if len(sys.argv) > 3 else (a.get("default") or modes[-1])
    on = mode in a["glow"] if a.get("glow") else mode != modes[0]
    glow = set(a.get("glowTex") or ["luz"]) if on else set()
    hidden = set()
    for n, ms in (a.get("show") or {}).items():
        if mode in ms:
            continue
        if n in model["parts"]:
            hidden.update(e["name"] for e in model["parts"][n]["elements"])
        else:
            hidden.add(n)
    els = [e for p in model["parts"].values() for e in p["elements"] if e["name"] not in hidden]
    codes = used(els, set()) | {"cobble"}
    textures = {}
    for c in codes:
        if c not in g.TEXTURES:
            print("código de textura sem TEXTURES:", c)
            continue
        d = tex_data(g.TEXTURES[c])
        if d:
            textures[c] = d
    # Enquadra pelo tamanho do modelo
    lo = [min(min(e["from"][i], e["to"][i]) for e in els) / 16 for i in range(3)]
    hi = [max(max(e["from"][i], e["to"][i]) for e in els) / 16 for i in range(3)]
    c = [(lo[i] + hi[i]) / 2 for i in range(3)]
    r = max(hi[i] - lo[i] for i in range(3))
    cams = [[c[0] + r * 1.6, c[1] + r * 1.0, c[2] + r * 2.0], [c[0] - r * 1.9, c[1] + r * 0.9, c[2] - r * 1.4],
            [c[0] + 0.01, c[1] + r * 2.6, c[2] + r * 0.6]]
    html = """<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#1b1d22}canvas{display:block}</style></head><body>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const ELS = %s, TEX = %s, GLOW = %s, CAMS = %s, C = %s, LABEL = %s;
const r = new THREE.WebGLRenderer({antialias:true, preserveDrawingBuffer:true});
r.setSize(1500, 560); r.setScissorTest(true); document.body.appendChild(r.domElement);
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x1b1d22);
scene.add(new THREE.HemisphereLight(0xffffff,0x404050,0.8));
const sun = new THREE.DirectionalLight(0xffffff,0.7); sun.position.set(3,5,2); scene.add(sun);
const grid = new THREE.GridHelper(6, 6, 0x555b66, 0x33373f); grid.position.set(0.5, 0, 0.5); scene.add(grid);
const box = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1,1,1)), new THREE.LineBasicMaterial({color:0xe0a64a}));
box.position.set(0.5,0.5,0.5); scene.add(box);
const imgs = {}; let n = 0; const total = Object.keys(TEX).length;
for (const [k,v] of Object.entries(TEX)) { const i = new Image(); i.onload = i.onerror = () => { if (++n === total) build(); }; i.src = v; imgs[k] = i; }
function tex(code, uv) {
  const t = new THREE.Texture(imgs[code]); t.needsUpdate = true;
  t.magFilter = t.minFilter = THREE.NearestFilter; t.wrapS = t.wrapT = THREE.RepeatWrapping;
  uv = uv || [0,0,16,16]; t.repeat.set((uv[2]-uv[0])/16,(uv[3]-uv[1])/16); t.offset.set(uv[0]/16,1-uv[3]/16); return t;
}
const ORDER = ['east','west','up','down','south','north'];
const D = THREE.MathUtils.degToRad;
function addEl(el, parent, base) {
  const f = el.from.map((v,i) => v + base[i]), t = el.to.map((v,i) => v + base[i]);
  const w = Math.max(0.01,t[0]-f[0]), h = Math.max(0.01,t[1]-f[1]), d = Math.max(0.01,t[2]-f[2]);
  const mats = ORDER.map(k => { const fc = el.faces[k]; if (!fc || !imgs[fc.texture.slice(1)]) return new THREE.MeshBasicMaterial({visible:false});
    const code = fc.texture.slice(1); const M = (fc.glow || GLOW.includes(code)) ? THREE.MeshBasicMaterial : THREE.MeshLambertMaterial;
    return new M({map: tex(code, fc.uv), transparent:true, alphaTest:0.1}); });
  const o = el.rotationOrigin ? el.rotationOrigin.map((v,i) => v + base[i]) : [f[0]+w/2,f[1]+h/2,f[2]+d/2];
  const p = new THREE.Group(); p.position.set(o[0]/16,o[1]/16,o[2]/16);
  p.rotation.set(D(el.rotationX||0),D(el.rotationY||0),D(el.rotationZ||0));
  const holder = new THREE.Group(); holder.position.set(-o[0]/16,-o[1]/16,-o[2]/16); p.add(holder);
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w/16,h/16,d/16), mats);
  mesh.position.set((f[0]+w/2)/16,(f[1]+h/2)/16,(f[2]+d/2)/16); holder.add(mesh);
  parent.add(p);
  for (const c of el.children || []) addEl(c, holder, f);
}
function build() {
  for (const el of ELS) addEl(el, scene, [0,0,0]);
  CAMS.forEach((p, i) => {
    const cam = new THREE.PerspectiveCamera(35, 500/560, 0.02, 100);
    cam.position.set(...p); cam.lookAt(...C);
    r.setViewport(i*500, 0, 500, 560); r.setScissor(i*500, 0, 500, 560); r.render(scene, cam);
  });
  document.title = 'pronto';
}
</script></body></html>""" % (json.dumps(els), json.dumps(textures), json.dumps(sorted(glow)), json.dumps(cams), json.dumps(c), json.dumps(key))
    tmp = os.path.join(tempfile.gettempdir(), f"previa_{key}.html")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(html)
    prof = os.path.join(tempfile.gettempdir(), f"previa_edge_{key}")
    subprocess.run([EDGE, "--headless=new", "--disable-gpu-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                    f"--user-data-dir={prof}", "--hide-scrollbars", "--window-size=1500,560",
                    "--virtual-time-budget=8000", f"--screenshot={out}", "file:///" + tmp.replace("\\", "/")],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    print("ok ->", out, "| modo:", mode, "| peças:", len(els))


if __name__ == "__main__":
    main()
