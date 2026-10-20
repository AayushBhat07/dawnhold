"""Build upload-ready browser versions of the game.

  python3 tools/build_web.py

Writes dist/<target>/ and dist/<target>.zip for each target:
  web         plain build, no portal SDK (itch.io, your own site)
  poki        adds the Poki SDK
  crazygames  adds the CrazyGames SDK
Three.js is bundled from lib/three, so nothing loads from a CDN except the portal SDK.
Rerun tools/pack_models.py first if you changed any assets.
"""
import pathlib, re, shutil, zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
SDKS = {
    'web': '',
    'poki': '<script src="https://game-cdn.poki.com/scripts/v2/poki-sdk.js"></script>',
    'crazygames': '<script src="https://sdk.crazygames.com/crazygames-sdk-v3.js"></script>',
}
IMPORTMAP = '''<script type="importmap">
  { "imports": {
    "three": "./lib/three/three.module.min.js",
    "three/addons/": "./lib/three/addons/"
  } }
</script>'''

src = (ROOT / 'index.html').read_text()
src, n = re.subn(r'<script type="importmap">.*?</script>', IMPORTMAP, src, count=1, flags=re.S)
assert n == 1, 'import map not found'
src = src.replace('debug: { showFps: true }', 'debug: { showFps: false }')

for target, tag in SDKS.items():
    out = DIST / target
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    html = src.replace('<script src="models.js"></script>', (tag + '\n' if tag else '') + '<script src="models.js"></script>')
    (out / 'index.html').write_text(html)
    shutil.copy(ROOT / 'models.js', out / 'models.js')
    shutil.copytree(ROOT / 'lib', out / 'lib')
    shutil.copy(ROOT / 'assets' / 'CREDITS.txt', out / 'CREDITS.txt')
    zpath = DIST / f'{target}.zip'
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(out.rglob('*')):
            if f.is_file(): z.write(f, f.relative_to(out))
    print(f'{target:11s} {zpath.stat().st_size / 1e6:.2f} MB  {zpath}')
