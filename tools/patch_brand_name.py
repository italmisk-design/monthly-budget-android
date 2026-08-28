from pathlib import Path

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')
s = s.replace('توفيري', 'وفرلي')
s = s.replace('Tofeeri', 'Wafferli')
p.write_text(s, encoding='utf-8')
print('Wafferli brand name applied')
