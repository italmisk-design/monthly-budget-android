from pathlib import Path
from PIL import Image
import json

src_path = Path('app/src/main/assets/wafferli_logo.jpg')
base = Path('ios/Tofeeri/Assets.xcassets/AppIcon.appiconset')
contents = base / 'Contents.json'

if not src_path.exists():
    raise SystemExit('Official Wafferli logo not found')
if not contents.exists():
    raise SystemExit('AppIcon Contents.json not found')

src = Image.open(src_path).convert('RGB')
data = json.loads(contents.read_text(encoding='utf-8'))

for item in data.get('images', []):
    filename = item.get('filename')
    size = item.get('size')
    scale = item.get('scale')
    if not filename or not size or not scale:
        continue
    points = float(size.split('x')[0])
    multiplier = float(scale.rstrip('x'))
    px = max(1, round(points * multiplier))
    icon = src.resize((px, px), Image.Resampling.LANCZOS)
    icon.save(base / filename, 'PNG', optimize=True)

print('Official Wafferli iOS icons generated')
