from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

css = ".googleStatus{display:block;color:var(--muted);font-size:10px;margin-top:4px;direction:ltr;text-align:right;max-width:240px;overflow:hidden;text-overflow:ellipsis}.googleStatus.connected{color:var(--in);font-weight:700}.settingActions{display:flex;gap:7px;align-items:center;flex-wrap:wrap}.googleCloudBtn:disabled{opacity:.45;cursor:default}"
if '.googleStatus{' not in s:
    s = s.replace('</style>', '\n' + css + '\n</style>', 1)

if 'id="googleAccountStatus"' not in s:
    dark = '<div class="settingrow"><div><b>الوضع الداكن</b><small>تغيير مظهر التطبيق</small></div><button id="darkBtn" class="normal" onclick="toggleDark()">تشغيل</button></div>'
    google = '<div class="settingrow"><div><b>حساب Google</b><small>يحفظ بيانات وفرلي ويزامنها بين أجهزتك</small><span id="googleAccountStatus" class="googleStatus">غير مربوط</span></div><div class="settingActions"><button id="googleSyncBtn" class="normal googleCloudBtn" onclick="googleSyncNow()" disabled>مزامنة الآن</button><button id="googleAccountBtn" class="normal" onclick="googleAccountAction()">ربط</button></div></div>'
    if dark not in s:
        raise SystemExit('dark mode row not found')
    s = s.replace(dark, dark + google, 1)

s = s.replace("<button class=\"normal\" onclick=\"document.getElementById('importFile').click()\">استرجاع</button>",
              "<button class=\"normal\" onclick=\"requestImportData()\">استرجاع</button>", 1)

old_export = "function exportData(){const blob=new Blob([JSON.stringify({app:'وفرلي',version:6,data:state},null,2)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='Wafferli-Backup-'+today()+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}\nfunction importData(el){const f=el.files[0];if(!f)return;const r=new FileReader();r.onload=()=>{try{const o=JSON.parse(r.result),d=o.data||o;if(!Array.isArray(d.wallets)||!Array.isArray(d.transactions)||!Array.isArray(d.rates))throw 0;if(!Array.isArray(d.monthlyTemplates))d.monthlyTemplates=[];if(!Array.isArray(d.monthlyRuns))d.monthlyRuns=[];d.version=Math.max(Number(d.version)||5,6);state=d;persist();renderAll();toast('تم استرجاع النسخة')}catch(e){toast('الملف غير صالح')}el.value=''};r.readAsText(f,'utf-8')}"
new_export = r"""function backupPayload(){return JSON.stringify({app:'وفرلي',version:6,data:state},null,2)}
function exportData(){
  const name='Wafferli-Backup-'+today()+'.json',content=backupPayload();
  try{
    if(window.AndroidBudget&&typeof AndroidBudget.saveBudget==='function'){AndroidBudget.saveBudget(name,content);return}
    if(window.webkit&&window.webkit.messageHandlers&&window.webkit.messageHandlers.Wafferli){window.webkit.messageHandlers.Wafferli.postMessage({action:'savefile',payload:content,filename:name});return}
  }catch(e){}
  const blob=new Blob([content],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)
}
function applyImportedBackup(text){
  try{const o=JSON.parse(text),d=o.data||o;if(!Array.isArray(d.wallets)||!Array.isArray(d.transactions)||!Array.isArray(d.rates))throw 0;if(!Array.isArray(d.monthlyTemplates))d.monthlyTemplates=[];if(!Array.isArray(d.monthlyRuns))d.monthlyRuns=[];d.version=Math.max(Number(d.version)||5,6);state=d;persist();renderAll();toast('تم استرجاع النسخة');return true}catch(e){toast('الملف غير صالح');return false}
}
function requestImportData(){
  try{
    if(window.AndroidBudget&&typeof AndroidBudget.openBudget==='function'){AndroidBudget.openBudget();return}
    if(window.webkit&&window.webkit.messageHandlers&&window.webkit.messageHandlers.Wafferli){window.webkit.messageHandlers.Wafferli.postMessage({action:'openfile',payload:''});return}
  }catch(e){}
  document.getElementById('importFile').click()
}
function importData(el){const f=el.files[0];if(!f)return;const r=new FileReader();r.onload=()=>{applyImportedBackup(r.result);el.value=''};r.readAsText(f,'utf-8')}
window.loadBudgetFromAndroid=function(text){applyImportedBackup(text)};
window.loadBudgetFromNative=function(text){applyImportedBackup(text)};"""
if old_export in s:
    s = s.replace(old_export, new_export, 1)
elif 'function backupPayload()' not in s:
    raise SystemExit('export/import block not found')

google_js = r"""
let wafferliGoogleState={signedIn:false,email:'',name:''};
let wafferliGoogleApplying=false,wafferliGoogleTimer=null,wafferliGoogleChecked=false,wafferliGoogleManual=false;
const WAFFERLI_CLOUD_TS='wafferli_cloud_updated_at_v1';
function googleNative(action,payload=''){
  try{
    if(window.AndroidBudget&&typeof AndroidBudget.googleAction==='function'){AndroidBudget.googleAction(String(action),String(payload||''));return true}
    if(window.webkit&&window.webkit.messageHandlers&&window.webkit.messageHandlers.Wafferli){window.webkit.messageHandlers.Wafferli.postMessage({action:String(action),payload:String(payload||'')});return true}
  }catch(e){toast('تعذر الاتصال بخدمة Google');return false}
  toast('خدمة Google متاحة داخل تطبيق Android أو iPhone فقط');return false
}
function hasMeaningfulLocalData(){
  try{return !!(state.onboarded||(state.transactions||[]).length||(state.rates||[]).length||(state.monthlyTemplates||[]).length||(state.monthlyRuns||[]).length||(state.wallets||[]).some(w=>Number(w.openingIQD||0)!==0||Number(w.openingUSD||0)!==0))}catch(e){return false}
}
function cloudLocalTs(){
  let t=Number(localStorage.getItem(WAFFERLI_CLOUD_TS)||0);
  if(!t&&hasMeaningfulLocalData()){t=Date.now();localStorage.setItem(WAFFERLI_CLOUD_TS,String(t))}
  return t||0
}
function cloudSnapshot(){return JSON.stringify({format:'wafferli-cloud-v1',updatedAt:cloudLocalTs(),data:state})}
function googleAccountAction(){googleNative(wafferliGoogleState.signedIn?'signout':'signin','')}
function googleSyncNow(){
  if(!wafferliGoogleState.signedIn){toast('اربط حساب Google أولاً');return}
  wafferliGoogleManual=true;
  const b=document.getElementById('googleSyncBtn');if(b){b.disabled=true;b.textContent='جاري المزامنة...'}
  googleNative('restore','')
}
function scheduleGooglePush(){
  if(wafferliGoogleApplying||!wafferliGoogleState.signedIn)return;
  clearTimeout(wafferliGoogleTimer);
  wafferliGoogleTimer=setTimeout(()=>googleNative('backup',cloudSnapshot()),1400)
}
function installGooglePersistHook(){
  if(typeof persist!=='function'||persist.__googleWrapped)return;
  const original=persist;
  const wrapped=function(){const r=original.apply(this,arguments);if(!wafferliGoogleApplying){localStorage.setItem(WAFFERLI_CLOUD_TS,String(Date.now()));scheduleGooglePush()}return r};
  wrapped.__googleWrapped=true;window.persist=wrapped
}
window.wafferliGoogleStatus=function(info){
  info=info||{};wafferliGoogleState={signedIn:!!info.signedIn,email:info.email||'',name:info.name||''};
  const st=document.getElementById('googleAccountStatus'),acc=document.getElementById('googleAccountBtn'),sync=document.getElementById('googleSyncBtn');
  if(st){st.textContent=wafferliGoogleState.signedIn?(wafferliGoogleState.email||wafferliGoogleState.name||'تم ربط حساب Google'):'غير مربوط';st.classList.toggle('connected',wafferliGoogleState.signedIn)}
  if(acc)acc.textContent=wafferliGoogleState.signedIn?'تسجيل خروج':'ربط';
  if(sync)sync.disabled=!wafferliGoogleState.signedIn;
  if(wafferliGoogleState.signedIn&&!wafferliGoogleChecked){wafferliGoogleChecked=true;setTimeout(()=>googleNative('restore',''),450)}
  if(!wafferliGoogleState.signedIn)wafferliGoogleChecked=false
};
window.loadBudgetFromGoogle=function(text){
  try{
    const o=JSON.parse(text),d=(o&&o.data)||o;
    if(!d||!Array.isArray(d.wallets)||!Array.isArray(d.transactions)||!Array.isArray(d.rates))throw new Error('نسخة Google غير صالحة');
    const remoteTs=Number(o&&o.updatedAt)||1,localTs=cloudLocalTs();
    if(remoteTs>localTs||!hasMeaningfulLocalData()){
      wafferliGoogleApplying=true;
      state=d;
      if(!Array.isArray(state.monthlyTemplates))state.monthlyTemplates=[];
      if(!Array.isArray(state.monthlyRuns))state.monthlyRuns=[];
      if(!state.selectedMonth)state.selectedMonth=today().slice(0,7);
      localStorage.setItem(WAFFERLI_CLOUD_TS,String(remoteTs));
      persist();
      wafferliGoogleApplying=false;
      renderAll();
      if(wafferliGoogleManual)toast('تم جلب أحدث البيانات من Google')
    }else if(localTs>remoteTs){
      googleNative('backup',cloudSnapshot());
      if(wafferliGoogleManual)toast('تم إرسال أحدث البيانات إلى Google')
    }else if(wafferliGoogleManual)toast('بياناتك متزامنة')
  }catch(e){if(wafferliGoogleManual)toast('تعذر قراءة نسخة Google')}
  wafferliGoogleManual=false;
  const b=document.getElementById('googleSyncBtn');if(b){b.textContent='مزامنة الآن';b.disabled=!wafferliGoogleState.signedIn}
};
window.wafferliGoogleDone=function(action,ok,message){
  const b=document.getElementById('googleSyncBtn');
  if(action==='signin'||action==='signout')setTimeout(()=>googleNative('status',''),250);
  if(action==='restore'&&!ok&&wafferliGoogleState.signedIn&&hasMeaningfulLocalData()&&String(message||'').includes('لا توجد نسخة')){googleNative('backup',cloudSnapshot());ok=true;if(wafferliGoogleManual)toast('تم إنشاء أول نسخة على Google')}
  else if(!ok&&wafferliGoogleManual&&message)toast(message);
  if(action==='backup'&&wafferliGoogleManual&&ok)toast('تمت المزامنة مع Google');
  if(action==='restore'&&!ok)wafferliGoogleManual=false;
  if(b){b.textContent='مزامنة الآن';b.disabled=!wafferliGoogleState.signedIn}
};
setTimeout(()=>{installGooglePersistHook();googleNative('status','')},650);
"""
if 'let wafferliGoogleState=' not in s:
    marker='setTimeout(ensureOnboarding,80);'
    if marker not in s:
        raise SystemExit('onboarding marker not found')
    s=s.replace(marker, marker+'\n'+google_js,1)

required=['googleAccountStatus','googleSyncNow','loadBudgetFromGoogle','requestImportData','loadBudgetFromAndroid']
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit('missing after patch: '+', '.join(missing))

p.write_text(s,encoding='utf-8')
print('Wafferli v13.1 Google/native backup patch applied')
