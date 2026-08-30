from pathlib import Path

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

style = r'''
/* WAFFERLI_TUTORIAL_V16 */
.tutorialRoot{position:fixed;inset:0;z-index:99990;direction:rtl;font-family:inherit;pointer-events:none}
.tutorialMask{position:fixed;background:rgba(0,0,0,.62);pointer-events:auto;transition:all .18s ease}
.tutorialFocus{position:fixed;border:3px solid #fff;border-radius:18px;box-shadow:0 0 0 3px rgba(17,107,94,.85),0 0 26px rgba(255,255,255,.42);pointer-events:none;transition:all .18s ease;animation:tutorialPulse 1.35s ease-in-out infinite}
.tutorialFocus::after{content:'هنا';position:absolute;top:-15px;right:12px;background:#116b5e;color:#fff;border:2px solid #fff;border-radius:999px;padding:4px 10px;font-size:12px;font-weight:800;box-shadow:0 5px 15px rgba(0,0,0,.18)}
.tutorialCard{position:fixed;left:14px;right:14px;max-width:560px;margin:auto;background:#fff;color:#17201f;border-radius:22px;padding:18px;box-shadow:0 18px 55px rgba(0,0,0,.34);pointer-events:auto;border:1px solid rgba(17,107,94,.14)}
.tutorialCard.atTop{top:calc(14px + env(safe-area-inset-top));bottom:auto}
.tutorialCard.atBottom{bottom:calc(88px + env(safe-area-inset-bottom));top:auto}
.tutorialCard.welcome{top:50%;bottom:auto;transform:translateY(-50%)}
.tutorialTopline{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:9px}
.tutorialCounter{font-size:12px;font-weight:800;color:#63716e;background:#f1f6f5;border-radius:999px;padding:5px 9px;white-space:nowrap}
.tutorialTitle{font-size:20px;font-weight:900;line-height:1.35;color:#0f5149;margin:0}
.tutorialText{font-size:15px;line-height:1.85;margin:0;color:#35413f}
.tutorialActions{display:flex;align-items:center;gap:8px;margin-top:15px}
.tutorialActions button{min-height:43px;border-radius:13px;font-family:inherit;font-weight:800;padding:9px 15px;cursor:pointer}
.tutorialNext{background:#116b5e;color:#fff;border:0;flex:1}
.tutorialPrev{background:#edf4f3;color:#155c53;border:0}
.tutorialSkip{background:transparent;color:#6a7472;border:1px solid #d7dfdd}
.tutorialProgress{height:5px;border-radius:99px;background:#e7eeec;overflow:hidden;margin-top:14px}
.tutorialProgress>span{display:block;height:100%;background:#116b5e;border-radius:99px;transition:width .2s ease}
body.dark .tutorialCard{background:#172321;color:#f3f6f5;border-color:#2d4641}
body.dark .tutorialTitle{color:#8cd5ca}
body.dark .tutorialText{color:#d8e1df}
body.dark .tutorialCounter{background:#253532;color:#cbd9d6}
body.dark .tutorialPrev{background:#263a36;color:#b9ded7}
body.dark .tutorialSkip{color:#c6cfcd;border-color:#40524f}
body.dark .tutorialProgress{background:#30423f}
@keyframes tutorialPulse{0%,100%{box-shadow:0 0 0 3px rgba(17,107,94,.85),0 0 20px rgba(255,255,255,.25)}50%{box-shadow:0 0 0 5px rgba(17,107,94,.55),0 0 32px rgba(255,255,255,.55)}}
@media(max-width:420px){.tutorialCard{padding:16px;border-radius:19px}.tutorialTitle{font-size:18px}.tutorialText{font-size:14px}.tutorialActions{flex-wrap:wrap}.tutorialNext{flex:1 1 45%}.tutorialSkip{order:3;flex:1 1 100%}}
'''

if 'WAFFERLI_TUTORIAL_V16' not in s:
    if '</style>' not in s:
        raise SystemExit('style closing tag not found')
    s = s.replace('</style>', style + '\n</style>', 1)

row = '<div id="tutorialSettingsRow" class="settingrow"><div><b>التدريب على استخدام وفرلي</b><small>إعادة عرض الشرح السريع لأجزاء التطبيق وطريقة تنظيم الأموال</small></div><button class="normal" onclick="startWafferliTutorial(true)">إعادة التدريب</button></div>'
if 'id="tutorialSettingsRow"' not in s:
    anchor = '<div class="settingrow"><div><b>حذف كل البيانات</b>'
    if anchor not in s:
        raise SystemExit('settings anchor not found')
    s = s.replace(anchor, row + anchor, 1)

if '<script src="tutorial.js"></script>' not in s:
    if '</body>' not in s:
        raise SystemExit('body closing tag not found')
    s = s.replace('</body>', '<script src="tutorial.js"></script>\n</body>', 1)

p.write_text(s, encoding='utf-8')
print('v16 tutorial injected')
