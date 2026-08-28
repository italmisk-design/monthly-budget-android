from pathlib import Path

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')
tag = '<script src="primary_wallet.js"></script>\n'
if tag not in s:
    anchor = '<script>\nconst KEY='
    if anchor not in s:
        raise SystemExit('main script anchor not found')
    s = s.replace(anchor, tag + anchor, 1)
p.write_text(s, encoding='utf-8')
print('Primary wallet hierarchy loader applied')
