from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

logo = '''<div class="logo" aria-label="شعار وفرلي"><img src="wafferli_logo.jpg" alt="وفرلي"></div>'''

s2, n = re.subn(r'<div class="logo" aria-label="شعار توفيري">.*?</div>', logo, s, count=1, flags=re.S)
if n != 1:
    s2, n = re.subn(r'<div class="logo"[^>]*>.*?</div>', logo, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Logo container not found')

css = '''\n.logo{width:64px!important;height:64px!important;border-radius:18px!important;background:transparent!important;box-shadow:none!important;display:flex!important;align-items:center!important;justify-content:center!important;overflow:hidden!important}.logo img{width:64px;height:64px;display:block;object-fit:cover;border-radius:18px}.brand{gap:8px!important}\n'''
if '.logo img{' not in s2:
    s2 = s2.replace('</style>', css + '</style>', 1)

p.write_text(s2, encoding='utf-8')
print('Official Wafferli logo applied')
