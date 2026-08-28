from pathlib import Path

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

css = r'''
:root{
  --native-safe-top:env(safe-area-inset-top,0px);
  --native-safe-bottom:env(safe-area-inset-bottom,0px);
  --native-safe-left:env(safe-area-inset-left,0px);
  --native-safe-right:env(safe-area-inset-right,0px)
}
/* Keep the WebView full-screen; only keep interactive content clear of system bars. */
.app{
  padding-top:calc(10px + var(--native-safe-top))!important;
  padding-bottom:calc(92px + var(--native-safe-bottom))!important;
  padding-left:calc(13px + var(--native-safe-left))!important;
  padding-right:calc(13px + var(--native-safe-right))!important
}
.nav{
  bottom:0!important;
  padding:6px calc(6px + var(--native-safe-right)) calc(6px + var(--native-safe-bottom)) calc(6px + var(--native-safe-left))!important
}
.sheet{padding-bottom:calc(18px + var(--native-safe-bottom))!important}
.manageSelectionBar{bottom:calc(16px + var(--native-safe-bottom))!important}
.toast{bottom:calc(85px + var(--native-safe-bottom))!important}
@media(max-width:560px){
  .app{
    padding-left:calc(10px + var(--native-safe-left))!important;
    padding-right:calc(10px + var(--native-safe-right))!important
  }
}
'''

if '--native-safe-top' not in s:
    if '</style>' not in s:
        raise SystemExit('style closing tag not found')
    s = s.replace('</style>', css + '\n</style>', 1)

required = ['--native-safe-top', '--native-safe-bottom', '.nav{', '.app{']
missing = [x for x in required if x not in s]
if missing:
    raise SystemExit('safe-area patch validation failed: ' + ', '.join(missing))

p.write_text(s, encoding='utf-8')
print('Full-screen safe-area CSS applied')
