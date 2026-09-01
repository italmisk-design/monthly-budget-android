from pathlib import Path
import hashlib, shutil, sys
ROOT=Path(__file__).resolve().parents[1]
if len(sys.argv)!=2: raise SystemExit('Usage: python tools/update_logo.py new_logo.jpg')
src=Path(sys.argv[1]).expanduser().resolve()
if not src.is_file(): raise SystemExit('Logo file not found')
if src.suffix.lower() not in ('.jpg','.jpeg'): raise SystemExit('Use a JPEG logo file so the packaged extension matches the content')
data=src.read_bytes()
if not data.startswith(b'\xff\xd8'): raise SystemExit('The supplied file is not a valid JPEG signature')
for dst in [ROOT/'app/src/main/assets/wafferli_logo.jpg',ROOT/'app/src/main/res/drawable/wafferli_logo.jpg']:
    dst.write_bytes(data)
h=hashlib.sha256(data).hexdigest()
(ROOT/'branding/wafferli_logo.sha256').write_text(h+'\n',encoding='ascii')
print('Logo updated intentionally. New SHA-256:',h)
