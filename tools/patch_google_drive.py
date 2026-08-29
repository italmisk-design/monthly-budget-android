from pathlib import Path

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

css = '''
.googleStatus{display:block;color:var(--muted);font-size:10px;margin-top:4px;direction:ltr;text-align:right}.googleCloudBtn:disabled{opacity:.45;cursor:default}.googleConnected{color:var(--in)!important;font-weight:bold}
'''
if '.googleStatus{' not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

marker = '<div class="settingrow"><div><b>حذف كل البيانات</b>'
block = '''<div class="settingrow"><div><b>حساب Google</b><small>اربط حسابك لحفظ نسخة احتياطية خاصة بــ وفرلي على Google Drive</small><span id="googleAccountStatus" class="googleStatus">غير مربوط</span></div><button id="googleAccountBtn" class="normal" onclick="googleAccountAction()">ربط</button></div><div class="settingrow"><div><b>نسخة احتياطية على Google Drive</b><small>يحفظ أحدث بيانات المحافظ والحركات والأسعار والحركات الشهرية في مساحة التطبيق الخاصة</small></div><button id="googleBackupBtn" class="normal googleCloudBtn" onclick="googleBackupToDrive()" disabled>رفع الآن</button></div><div class="settingrow"><div><b>استرجاع من Google Drive</b><small>يستبدل بيانات هذا الجهاز بآخر نسخة محفوظة على حساب Google</small></div><button id="googleRestoreBtn" class="normal googleCloudBtn" onclick="googleRestoreFromDrive()" disabled>استرجاع</button></div>'''
if 'id="googleAccountStatus"' not in s:
    if marker not in s:
        raise SystemExit('Settings delete row marker not found')
    s = s.replace(marker, block + marker, 1)

js = r'''
let wafferliGoogleState={signedIn:false,email:'',name:''};
function googleSetStatus(text){const st=document.getElementById('googleAccountStatus');if(st)st.textContent=text}
function googleNativeSend(action,payload=''){
  try{
    if(window.AndroidBudget && AndroidBudget.googleAction){
      AndroidBudget.googleAction(String(action),String(payload||''));return true;
    }
    if(window.webkit&&window.webkit.messageHandlers&&window.webkit.messageHandlers.Wafferli){
      window.webkit.messageHandlers.Wafferli.postMessage({action:String(action),payload:String(payload||'')});return true;
    }
  }catch(e){googleSetStatus('خطأ بالربط');toast('تعذر الاتصال بخدمة Google: '+e.message);return false}
  googleSetStatus('خدمة Google غير متاحة');toast('خدمة Google متاحة داخل تطبيق Android أو iPhone فقط');return false;
}
function requestGoogleStatus(){googleNativeSend('status','')}
function googleAccountAction(){
  if(wafferliGoogleState.signedIn){googleNativeSend('signout','');return}
  const b=document.getElementById('googleAccountBtn');if(b){b.disabled=true;b.textContent='جاري الفتح...'}
  googleSetStatus('جاري فتح تسجيل Google...');
  if(!googleNativeSend('signin','')){if(b){b.disabled=false;b.textContent='ربط'}}
}
function googleBackupToDrive(){
  if(!wafferliGoogleState.signedIn){toast('اربط حساب Google أولاً');return}
  const payload=JSON.stringify(state);
  const b=document.getElementById('googleBackupBtn');if(b){b.disabled=true;b.textContent='جاري الحفظ...'}
  googleNativeSend('backup',payload)
}
function googleRestoreFromDrive(){
  if(!wafferliGoogleState.signedIn){toast('اربط حساب Google أولاً');return}
  if(!confirm('سيتم استبدال بيانات وفرلي الموجودة على هذا الجهاز بآخر نسخة محفوظة على Google Drive. هل تريد الاستمرار؟'))return;
  const b=document.getElementById('googleRestoreBtn');if(b){b.disabled=true;b.textContent='جاري الاسترجاع...'}
  googleNativeSend('restore','')
}
window.wafferliGoogleStatus=function(info){
  info=info||{};wafferliGoogleState={signedIn:!!info.signedIn,email:info.email||'',name:info.name||''};
  const st=document.getElementById('googleAccountStatus'),acc=document.getElementById('googleAccountBtn'),up=document.getElementById('googleBackupBtn'),down=document.getElementById('googleRestoreBtn');
  if(st){st.textContent=wafferliGoogleState.signedIn?(wafferliGoogleState.email||wafferliGoogleState.name||'تم ربط حساب Google'):'غير مربوط';st.classList.toggle('googleConnected',wafferliGoogleState.signedIn)}
  if(acc){acc.disabled=false;acc.textContent=wafferliGoogleState.signedIn?'تسجيل خروج':'ربط'}
  if(up)up.disabled=!wafferliGoogleState.signedIn;if(down)down.disabled=!wafferliGoogleState.signedIn;
}
window.wafferliGoogleDone=function(action,ok,message){
  const acc=document.getElementById('googleAccountBtn'),up=document.getElementById('googleBackupBtn'),down=document.getElementById('googleRestoreBtn');
  if(acc){acc.disabled=false;acc.textContent=wafferliGoogleState.signedIn?'تسجيل خروج':'ربط'}
  if(up){up.textContent='رفع الآن';up.disabled=!wafferliGoogleState.signedIn}
  if(down){down.textContent='استرجاع';down.disabled=!wafferliGoogleState.signedIn}
  if(!ok && action==='signin')googleSetStatus('فشل تسجيل Google');
  if(message)toast(message);if(action==='signin'||action==='signout')setTimeout(requestGoogleStatus,250)
}
window.loadBudgetFromGoogle=function(text){
  try{
    const parsed=JSON.parse(text),data=(parsed&&parsed.data)||(parsed&&parsed.state)||parsed;
    if(!data||!Array.isArray(data.wallets)||!Array.isArray(data.transactions)||!Array.isArray(data.categories))throw new Error('ملف النسخة الاحتياطية غير صالح');
    Object.keys(state).forEach(k=>delete state[k]);Object.assign(state,data);
    if(!Array.isArray(state.rates))state.rates=[];
    if(!Array.isArray(state.monthlyTemplates))state.monthlyTemplates=[];
    if(!Array.isArray(state.monthlyRuns))state.monthlyRuns=[];
    if(!state.selectedMonth)state.selectedMonth=today().slice(0,7);
    persist();toast('تم استرجاع بيانات وفرلي من Google Drive');setTimeout(()=>location.reload(),450);
  }catch(e){toast('تعذر استرجاع النسخة: '+e.message)}
}
setTimeout(requestGoogleStatus,600);
'''

# IMPORTANT: never inject inline JS inside a <script src="..."> tag.
# A browser ignores inline script content when src is present.
if 'window.wafferliGoogleStatus=' not in s:
    if '</body>' not in s:
        raise SystemExit('Body closing tag not found')
    s = s.replace('</body>', '<script>\n' + js + '\n</script>\n</body>', 1)

required=['googleAccountStatus','googleBackupToDrive','googleRestoreFromDrive','loadBudgetFromGoogle','wafferliGoogleStatus']
missing=[x for x in required if x not in s]
if missing: raise SystemExit('Google Drive patch validation failed: '+', '.join(missing))
if '<script src="primary_wallet.js"></script>' not in s:
    raise SystemExit('Google patch corrupted primary_wallet.js script tag')

p.write_text(s, encoding='utf-8')
print('Google Drive UI patch applied safely')
