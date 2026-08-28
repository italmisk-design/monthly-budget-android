from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

logo = '''<div class="logo" aria-label="شعار توفيري"><svg viewBox="0 0 120 92" aria-hidden="true"><defs><linearGradient id="walletG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0F6B59"/><stop offset="1" stop-color="#064E42"/></linearGradient><linearGradient id="coinG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F4D776"/><stop offset="1" stop-color="#C99C35"/></linearGradient></defs><circle cx="39" cy="27" r="22" fill="url(#coinG)"/><circle cx="39" cy="27" r="14" fill="none" stroke="#E7BF56" stroke-width="3" opacity=".9"/><path d="M38 15c-6 1-9 5-8 10 1 4 4 6 9 7 4 1 6 2 6 4 0 2-2 3-5 3-4 0-7-1-10-3l-3 6c3 2 7 4 11 4v6h6v-6c7-1 11-5 11-11 0-6-4-9-11-11-4-1-6-2-6-4 0-2 2-3 5-3 3 0 6 1 9 2l3-6c-3-2-6-3-10-3v-5h-6v5z" fill="#FFF6D9"/><rect x="24" y="36" width="82" height="48" rx="15" fill="url(#walletG)"/><path d="M30 36h59c9 0 16 7 16 16v3H34c-9 0-15-4-15-9 0-6 5-10 11-10z" fill="#12806A"/><rect x="77" y="55" width="35" height="24" rx="10" fill="#D9A53A"/><circle cx="91" cy="67" r="4" fill="#0A5A4B"/><path d="M38 50h29" stroke="#E6C36C" stroke-width="4" stroke-linecap="round" opacity=".65"/></svg></div>'''

s2, n = re.subn(r'<div class="logo" aria-label="شعار توفيري">.*?</div>', logo, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Logo container not found')

css = '''\n.logo{width:62px!important;height:52px!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;display:flex!important;align-items:center!important;justify-content:center!important;overflow:visible!important}.logo svg{width:62px;height:52px;display:block}.brand{gap:7px!important}\n'''
if css.strip() not in s2:
    s2 = s2.replace('</style>', css + '</style>', 1)

p.write_text(s2, encoding='utf-8')

icon = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp" android:height="108dp"
    android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#F7F5EE" android:pathData="M0,0h108v108h-108z"/>
    <path android:fillColor="#D6A83B" android:pathData="M34,14m-21,0a21,21 0,1 0,42 0a21,21 0,1 0,-42 0"/>
    <path android:fillColor="#F8E5A6" android:pathData="M34,14m-14,0a14,14 0,1 0,28 0a14,14 0,1 0,-28 0"/>
    <path android:fillColor="#0E6F5D" android:pathData="M22,38h63c8,0 14,6 14,14v34c0,7 -6,13 -13,13h-64c-7,0 -13,-6 -13,-13v-35c0,-7 6,-13 13,-13z"/>
    <path android:fillColor="#16836D" android:pathData="M22,38h56c11,0 20,8 20,19v3H27c-11,0 -18,-5 -18,-11s6,-11 13,-11z"/>
    <path android:fillColor="#D6A83B" android:pathData="M72,61h27c5,0 9,4 9,9v9c0,5 -4,9 -9,9H72c-8,0 -14,-6 -14,-14s6,-13 14,-13z"/>
    <path android:fillColor="#0B5F4F" android:pathData="M82,74m-4,0a4,4 0,1 0,8 0a4,4 0,1 0,-8 0"/>
    <path android:fillColor="#E8C66B" android:pathData="M29,49h28v5H29z"/>
</vector>'''
Path('app/src/main/res/drawable/ic_launcher.xml').write_text(icon, encoding='utf-8')
print('Tofeeri logo applied')
