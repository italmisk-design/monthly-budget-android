let wafferliGoogleState={signedIn:false,email:'',name:''};
let wafferliGoogleApplying=false,wafferliGoogleTimer=null,wafferliGoogleChecked=false,wafferliGoogleManual=false;
let wafferliSyncMeta=null,wafferliSyncLastState=null,wafferliSyncRoundInFlight=false,wafferliSyncPending=false;
const WAFFERLI_CLOUD_TS='wafferli_cloud_updated_at_v1';
const WAFFERLI_SYNC_META='wafferli_sync_meta_v2';
const WAFFERLI_DEVICE_ID='wafferli_device_id_v2';
const WAFFERLI_LOGICAL_CLOCK='wafferli_sync_clock_v2';
function syncObserveClock(value){const v=Math.max(1,Number(value)||1),old=Number(localStorage.getItem(WAFFERLI_LOGICAL_CLOCK)||0);if(v>old)localStorage.setItem(WAFFERLI_LOGICAL_CLOCK,String(v));return Math.max(v,old)}
function syncNow(){const old=Number(localStorage.getItem(WAFFERLI_LOGICAL_CLOCK)||0),remote=wafferliSyncMeta?syncMaxTs(wafferliSyncMeta):0,next=Math.max(Date.now(),old+1,remote+1);localStorage.setItem(WAFFERLI_LOGICAL_CLOCK,String(next));return next}
const SYNC_COLLECTIONS=['wallets','categories','transactions','rates','monthlyTemplates','monthlyRuns'];
const SYNC_FIELDS=['baseCurrency','onboarded'];
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
  if(!t&&hasMeaningfulLocalData()){t=syncNow();localStorage.setItem(WAFFERLI_CLOUD_TS,String(t))}
  return t||0
}
function syncCopy(v){return JSON.parse(JSON.stringify(v))}
function syncDeviceId(){
  let id=localStorage.getItem(WAFFERLI_DEVICE_ID)||'';
  if(!id){id='dev-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,10);localStorage.setItem(WAFFERLI_DEVICE_ID,id)}
  return id
}
function syncEmptyMeta(deviceId){
  const m={version:2,deviceId:deviceId||syncDeviceId(),updatedAt:1,records:{},tombstones:{},fields:{}};
  SYNC_COLLECTIONS.forEach(c=>{m.records[c]={};m.tombstones[c]={}});
  return m
}
function syncMetaFromState(data,ts,deviceId){
  const m=syncEmptyMeta(deviceId),t=Math.max(1,Number(ts)||1);
  SYNC_COLLECTIONS.forEach(c=>(Array.isArray(data[c])?data[c]:[]).forEach(x=>{if(x&&x.id!=null)m.records[c][String(x.id)]=t}));
  SYNC_FIELDS.forEach(f=>{if(Object.prototype.hasOwnProperty.call(data,f))m.fields[f]=t});
  m.updatedAt=t;return m
}
function syncNormalizeMeta(m,data,ts,deviceId){
  const out=(m&&typeof m==='object')?syncCopy(m):syncMetaFromState(data,ts,deviceId);
  out.version=2;out.deviceId=out.deviceId||deviceId||syncDeviceId();out.records=out.records||{};out.tombstones=out.tombstones||{};out.fields=out.fields||{};
  SYNC_COLLECTIONS.forEach(c=>{out.records[c]=out.records[c]||{};out.tombstones[c]=out.tombstones[c]||{}});
  const base=Math.max(1,Number(ts)||1);
  SYNC_COLLECTIONS.forEach(c=>(Array.isArray(data[c])?data[c]:[]).forEach(x=>{if(x&&x.id!=null&&!out.records[c][String(x.id)])out.records[c][String(x.id)]=base}));
  SYNC_FIELDS.forEach(f=>{if(Object.prototype.hasOwnProperty.call(data,f)&&!out.fields[f])out.fields[f]=base});
  out.updatedAt=Math.max(Number(out.updatedAt)||1,base);return out
}
function syncSaveMeta(){try{localStorage.setItem(WAFFERLI_SYNC_META,JSON.stringify(wafferliSyncMeta))}catch(e){}}
function syncEnsureMeta(){
  if(wafferliSyncMeta)return wafferliSyncMeta;
  let loaded=null;try{loaded=JSON.parse(localStorage.getItem(WAFFERLI_SYNC_META)||'null')}catch(e){}
  let base=cloudLocalTs();if(!base)base=hasMeaningfulLocalData()?syncNow():1;
  wafferliSyncMeta=syncNormalizeMeta(loaded,state,base,syncDeviceId());
  wafferliSyncMeta.deviceId=syncDeviceId();syncSaveMeta();
  wafferliSyncLastState=syncCopy(state);
  return wafferliSyncMeta
}
function syncSame(a,b){try{return JSON.stringify(a)===JSON.stringify(b)}catch(e){return false}}
function syncTrackLocalChanges(){
  const m=syncEnsureMeta(),prev=wafferliSyncLastState||syncCopy(state),now=syncNow();let changed=false;
  SYNC_COLLECTIONS.forEach(c=>{
    const before=new Map((Array.isArray(prev[c])?prev[c]:[]).filter(x=>x&&x.id!=null).map(x=>[String(x.id),x]));
    const after=new Map((Array.isArray(state[c])?state[c]:[]).filter(x=>x&&x.id!=null).map(x=>[String(x.id),x]));
    after.forEach((v,id)=>{
      const old=before.get(id);
      if(!old||!syncSame(old,v)){m.records[c][id]=now;delete m.tombstones[c][id];changed=true}
    });
    before.forEach((v,id)=>{
      if(!after.has(id)){m.tombstones[c][id]=now;delete m.records[c][id];changed=true}
    });
  });
  SYNC_FIELDS.forEach(f=>{if(!syncSame(prev[f],state[f])){m.fields[f]=now;changed=true}});
  if(changed){m.updatedAt=now;localStorage.setItem(WAFFERLI_CLOUD_TS,String(now));syncSaveMeta()}
  wafferliSyncLastState=syncCopy(state);return changed
}
function syncMaxTs(m){
  let t=Number(m&&m.updatedAt)||1;
  if(m){SYNC_COLLECTIONS.forEach(c=>{Object.values(m.records[c]||{}).forEach(v=>t=Math.max(t,Number(v)||0));Object.values(m.tombstones[c]||{}).forEach(v=>t=Math.max(t,Number(v)||0))});Object.values(m.fields||{}).forEach(v=>t=Math.max(t,Number(v)||0))}
  return t
}
function cloudSnapshotObject(){
  const m=syncEnsureMeta();m.updatedAt=Math.max(Number(m.updatedAt)||1,syncMaxTs(m));syncSaveMeta();
  return{format:'wafferli-cloud-v2',schemaVersion:2,deviceId:m.deviceId,updatedAt:m.updatedAt,data:state,meta:m}
}
function cloudSnapshot(){return JSON.stringify(cloudSnapshotObject())}
function syncNormalizeSnapshot(o,index){
  if(!o||typeof o!=='object')return null;
  const d=(o.data&&typeof o.data==='object')?o.data:o;
  if(!d||!Array.isArray(d.wallets)||!Array.isArray(d.transactions)||!Array.isArray(d.rates))return null;
  if(!Array.isArray(d.categories))d.categories=[];
  if(!Array.isArray(d.monthlyTemplates))d.monthlyTemplates=[];
  if(!Array.isArray(d.monthlyRuns))d.monthlyRuns=[];
  const ts=Math.max(1,Number(o.updatedAt)||1),dev=String(o.deviceId||('legacy-'+(index||0)));
  return{format:o.format||'legacy',deviceId:dev,updatedAt:ts,data:d,meta:syncNormalizeMeta(o.meta,d,ts,dev)}
}
function syncCandidateBetter(a,b){
  if(!a)return true;
  if(Number(b.ts)!==Number(a.ts))return Number(b.ts)>Number(a.ts);
  if(!!b.deleted!==!!a.deleted)return !!b.deleted;
  return String(b.origin||'')>String(a.origin||'')
}
function syncMergeSnapshots(remoteObjects){
  const local=syncNormalizeSnapshot(cloudSnapshotObject(),-1),snaps=[local];
  (remoteObjects||[]).forEach((o,i)=>{const n=syncNormalizeSnapshot(o,i);if(n)snaps.push(n)});
  const merged=syncCopy(state),meta=syncEmptyMeta(syncDeviceId());
  const localOrder={};SYNC_COLLECTIONS.forEach(c=>localOrder[c]=(Array.isArray(state[c])?state[c]:[]).map(x=>String(x.id)));
  SYNC_COLLECTIONS.forEach(c=>{
    const winners={};
    snaps.forEach(s=>{
      const recMap=s.meta.records[c]||{},delMap=s.meta.tombstones[c]||{};
      (Array.isArray(s.data[c])?s.data[c]:[]).forEach(v=>{if(!v||v.id==null)return;const id=String(v.id),cand={deleted:false,ts:Number(recMap[id])||s.updatedAt||1,origin:s.deviceId,value:v};if(syncCandidateBetter(winners[id],cand))winners[id]=cand});
      Object.keys(delMap).forEach(id=>{const cand={deleted:true,ts:Number(delMap[id])||s.updatedAt||1,origin:s.deviceId,value:null};if(syncCandidateBetter(winners[id],cand))winners[id]=cand});
    });
    const allOrder=[...localOrder[c]],seenOrder=new Set(allOrder);
    snaps.forEach(s=>(Array.isArray(s.data[c])?s.data[c]:[]).forEach(v=>{const id=v&&v.id!=null?String(v.id):'';if(id&&!seenOrder.has(id)){seenOrder.add(id);allOrder.push(id)}}));
    const alive=[];allOrder.forEach(id=>{const w=winners[id];if(w&&!w.deleted){alive.push(syncCopy(w.value));meta.records[c][id]=w.ts}else if(w&&w.deleted)meta.tombstones[c][id]=w.ts});
    Object.keys(winners).forEach(id=>{if(seenOrder.has(id))return;const w=winners[id];if(!w.deleted){alive.push(syncCopy(w.value));meta.records[c][id]=w.ts}else meta.tombstones[c][id]=w.ts});
    merged[c]=alive;
  });
  SYNC_FIELDS.forEach(f=>{
    let best=null;
    snaps.forEach(s=>{if(!Object.prototype.hasOwnProperty.call(s.data,f))return;const cand={ts:Number(s.meta.fields[f])||s.updatedAt||1,origin:s.deviceId,value:s.data[f]};if(syncCandidateBetter(best,cand))best=cand});
    if(best){merged[f]=syncCopy(best.value);meta.fields[f]=best.ts}
  });
  merged.version=Math.max(...snaps.map(s=>Number(s.data.version)||0),Number(merged.version)||6,6);
  if(!merged.selectedMonth)merged.selectedMonth=today().slice(0,7);
  meta.updatedAt=Math.max(1,...snaps.map(s=>syncMaxTs(s.meta)));
  return{data:merged,meta}
}
function googleAccountAction(){googleNative(wafferliGoogleState.signedIn?'signout':'signin','')}
function googleSyncNow(){
  if(!wafferliGoogleState.signedIn){toast('اربط حساب Google أولاً');return}
  wafferliGoogleManual=true;
  const b=document.getElementById('googleSyncBtn');if(b){b.disabled=true;b.textContent='جاري المزامنة...'}
  syncStartRound(true)
}
function syncStartRound(immediate){
  if(wafferliGoogleApplying||!wafferliGoogleState.signedIn)return;
  if(wafferliSyncRoundInFlight){wafferliSyncPending=true;return}
  wafferliSyncRoundInFlight=true;wafferliSyncPending=false;
  googleNative('restore','')
}
function scheduleGoogleSync(){
  if(wafferliGoogleApplying||!wafferliGoogleState.signedIn)return;
  clearTimeout(wafferliGoogleTimer);
  wafferliGoogleTimer=setTimeout(()=>syncStartRound(false),1200)
}
function installGooglePersistHook(){
  if(typeof persist!=='function'||persist.__googleWrapped)return;
  syncEnsureMeta();
  const original=persist;
  const wrapped=function(){
    let changed=false;
    if(!wafferliGoogleApplying)changed=syncTrackLocalChanges();
    const r=original.apply(this,arguments);
    if(changed)scheduleGoogleSync();
    return r
  };
  wrapped.__googleWrapped=true;window.persist=wrapped
}
window.wafferliGoogleStatus=function(info){
  info=info||{};wafferliGoogleState={signedIn:!!info.signedIn,email:info.email||'',name:info.name||''};
  const st=document.getElementById('googleAccountStatus'),acc=document.getElementById('googleAccountBtn'),sync=document.getElementById('googleSyncBtn');
  if(st){st.textContent=wafferliGoogleState.signedIn?(wafferliGoogleState.email||wafferliGoogleState.name||'تم ربط حساب Google'):'غير مربوط';st.classList.toggle('connected',wafferliGoogleState.signedIn)}
  if(acc)acc.textContent=wafferliGoogleState.signedIn?'تسجيل خروج':'ربط';
  if(sync)sync.disabled=!wafferliGoogleState.signedIn;
  if(wafferliGoogleState.signedIn&&!wafferliGoogleChecked){wafferliGoogleChecked=true;setTimeout(()=>syncStartRound(true),350)}
  if(!wafferliGoogleState.signedIn){wafferliGoogleChecked=false;wafferliSyncRoundInFlight=false;wafferliSyncPending=false}
};
window.loadBudgetFromGoogle=function(text){
  try{
    const o=JSON.parse(text);let remotes=[];
    if(o&&o.format==='wafferli-cloud-bundle-v2'&&Array.isArray(o.snapshots))remotes=o.snapshots;
    else remotes=[o];
    const result=syncMergeSnapshots(remotes);
    wafferliGoogleApplying=true;
    state=result.data;wafferliSyncMeta=result.meta;wafferliSyncMeta.deviceId=syncDeviceId();syncSaveMeta();
    localStorage.setItem(WAFFERLI_CLOUD_TS,String(syncMaxTs(wafferliSyncMeta)));syncObserveClock(syncMaxTs(wafferliSyncMeta));
    persist();wafferliSyncLastState=syncCopy(state);wafferliGoogleApplying=false;
    renderAll();
    googleNative('backup',cloudSnapshot());
    if(wafferliGoogleManual)toast('تم دمج أحدث بيانات أجهزتك')
  }catch(e){
    wafferliGoogleApplying=false;
    wafferliSyncRoundInFlight=false;
    if(wafferliGoogleManual)toast('تعذر قراءة بيانات Google')
  }
};
window.wafferliGoogleDone=function(action,ok,message){
  const b=document.getElementById('googleSyncBtn');
  if(action==='signin'||action==='signout')setTimeout(()=>googleNative('status',''),250);
  if(action==='restore'&&!ok&&wafferliGoogleState.signedIn&&String(message||'').includes('لا توجد نسخة')){
    googleNative('backup',cloudSnapshot());ok=true;if(wafferliGoogleManual)toast('تم إنشاء أول نسخة على Google')
  }else if(action==='restore'&&!ok){
    wafferliSyncRoundInFlight=false;
    if(!wafferliGoogleManual&&hasMeaningfulLocalData())googleNative('backup',cloudSnapshot());
    else if(wafferliGoogleManual&&message)toast(message)
  }
  if(action==='backup'){
    wafferliSyncRoundInFlight=false;
    if(wafferliGoogleManual&&ok)toast('تمت المزامنة مع Google');
    if(!ok&&wafferliGoogleManual&&message)toast(message);
    wafferliGoogleManual=false;
    if(wafferliSyncPending){wafferliSyncPending=false;setTimeout(()=>syncStartRound(false),150)}
  }
  if(action==='restore'&&!ok)wafferliGoogleManual=false;
  if(b){b.textContent='مزامنة الآن';b.disabled=!wafferliGoogleState.signedIn}
};
window.wafferliAppBackgrounded=function(){
  if(!wafferliGoogleState.signedIn)return;
  clearTimeout(wafferliGoogleTimer);
  try{googleNative('backup',cloudSnapshot())}catch(e){}
};
window.wafferliAppForegrounded=function(){
  if(!wafferliGoogleState.signedIn)return;
  setTimeout(()=>syncStartRound(true),180)
};
setTimeout(()=>{installGooglePersistHook();googleNative('status','')},650);
