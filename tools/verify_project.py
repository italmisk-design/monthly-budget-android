from pathlib import Path
import hashlib, sys
ROOT=Path(__file__).resolve().parents[1]
expected=(ROOT/'branding/wafferli_logo.sha256').read_text().strip().lower()
files=[ROOT/'app/src/main/assets/wafferli_logo.jpg',ROOT/'app/src/main/res/drawable/wafferli_logo.jpg']
for p in files:
    if not p.exists(): raise SystemExit(f'Missing brand asset: {p}')
    got=hashlib.sha256(p.read_bytes()).hexdigest()
    if got!=expected: raise SystemExit(f'Brand asset hash mismatch: {p}\nexpected={expected}\nactual={got}')
if files[0].read_bytes()!=files[1].read_bytes(): raise SystemExit('Android logo copies are not byte-identical')
index=(ROOT/'app/src/main/assets/index.html').read_text(encoding='utf-8')
for name in ('style.css','primary_wallet.js','app.js','sync.js','tutorial.js'):
    if name not in index: raise SystemExit(f'index.html does not reference {name}')
for old in ('app1.js','app2a.js','app2b.js'):
    if (ROOT/'app/src/main/assets'/old).exists(): raise SystemExit(f'Legacy asset still exists: {old}')
print('Wafferli project verification OK')
