const KEY='masroofi_wallets_v5';
const today=()=>{const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')};const uid=()=>Date.now().toString(36)+Math.random().toString(36).slice(2,7);
function fresh(){
  const presets=[
    {id:'w-main',name:'المحفظة الرئيسية',emoji:'💰',main:true,expense:[['مصروف عام','🧾'],['سحب نقدي','💵'],['رسوم وتحويلات','🔄'],['مصاريف طارئة','🚨']],income:[['راتب','💼'],['دخل إضافي','➕'],['مكافأة','🎁'],['استرجاع مبلغ','↩️']]},
    {id:'w-home',name:'المنزل والمعيشة',emoji:'🏠',expense:[['إيجار / قسط المنزل','🏡'],['كهرباء','⚡'],['ماء','💧'],['غاز','🔥'],['إنترنت','🌐'],['موبايل واتصالات','📱'],['مواد غذائية','🛒'],['احتياجات منزلية','🧴'],['صيانة المنزل','🛠️'],['أثاث وأجهزة','🛋️']],income:[['إيجار مستلم','🏘️'],['تعويضات منزلية','💵']]},
    {id:'w-car',name:'السيارة',emoji:'🚗',expense:[['بانزين','⛽'],['صيانة دورية','🛠️'],['تصليح','🔧'],['تنظيف','🧽'],['زيوت وفلاتر','🛢️'],['إطارات وبطارية','🛞'],['تسجيل وتأمين','📄'],['مواقف ورسوم طريق','🅿️'],['مخالفات','🚦']],income:[['بيع قطع / مسترجعات','↩️'],['تعويض تأمين','🛡️']]},
    {id:'w-food',name:'الطعام والمطاعم',emoji:'🍽️',expense:[['مطاعم','🍴'],['مقاهي','☕'],['طلبات وتوصيل','🛵'],['وجبات عمل','🥪'],['حلويات وسناكات','🍰']],income:[['استرجاع طلب','↩️']]},
    {id:'w-health',name:'الصحة',emoji:'❤️',expense:[['طبيب','🩺'],['أدوية وصيدلية','💊'],['تحاليل وأشعة','🧪'],['أسنان','🦷'],['نظارات وعيون','👓'],['مستشفى','🏥'],['تأمين صحي','🛡️']],income:[['تعويض تأمين صحي','↩️']]},
    {id:'w-shopping',name:'التسوق والشخصي',emoji:'🛍️',expense:[['ملابس','👕'],['أحذية','👟'],['عناية شخصية','🧴'],['إلكترونيات','🎧'],['هدايا','🎁'],['إكسسوارات','⌚'],['احتياجات شخصية أخرى','🧺']],income:[['بيع أغراض','💵'],['استرجاع مشتريات','↩️']]},
    {id:'w-family',name:'العائلة والأطفال',emoji:'👨‍👩‍👧‍👦',expense:[['مصروف أطفال','🧒'],['مدرسة وحضانة','🏫'],['ملابس أطفال','👕'],['دروس ونشاطات','🎨'],['مساعدة العائلة','🤝'],['مناسبات عائلية','🎊']],income:[['مساهمات عائلية','🤲']]},
    {id:'w-education',name:'التعليم والتطوير',emoji:'📚',expense:[['أقساط دراسية','🎓'],['كتب','📚'],['دورات','🧑‍🏫'],['قرطاسية','✏️'],['برامج واشتراكات تعليمية','💻']],income:[['منحة / دعم','🏅']]},
    {id:'w-entertainment',name:'الترفيه والاشتراكات',emoji:'🎬',expense:[['سينما وفعاليات','🎟️'],['ألعاب','🎮'],['اشتراكات رقمية','📺'],['رياضة ونادي','🏋️'],['طلعات ونزهات','🌳'],['هوايات','🎨']],income:[['بيع تذاكر / استرجاع','↩️']]},
    {id:'w-travel',name:'السفر',emoji:'✈️',expense:[['تذاكر','🎫'],['فندق','🏨'],['مواصلات','🚕'],['طعام أثناء السفر','🍽️'],['تأشيرة ورسوم','🛂'],['تسوق السفر','🛍️'],['أنشطة سياحية','🗺️']],income:[['استرجاع حجز','↩️'],['بدل سفر','💵']]},
    {id:'w-debt',name:'الأقساط والديون',emoji:'📆',expense:[['قسط قرض','🏦'],['قسط شراء','🧾'],['بطاقة ائتمان','💳'],['تسديد دين','🤝']],income:[['مبلغ مقترض','💵'],['استرداد دين','↩️']]},
    {id:'w-work',name:'العمل',emoji:'💼',expense:[['تنقل للعمل','🚕'],['طعام العمل','🥪'],['أدوات ومعدات','🧰'],['قرطاسية ومكتب','🗂️'],['ضيافة عمل','☕'],['اشتراكات وبرامج','💻']],income:[['عمل إضافي','➕'],['عمولة','💰'],['استرداد مصروف عمل','↩️']]},
    {id:'w-savings',name:'الادخار والاستثمار',emoji:'🏦',expense:[['رسوم مصرفية','🏧'],['رسوم استثمار','📉']],income:[['أرباح / فائدة','📈'],['توزيعات','💹']]}
  ];
  const wallets=presets.map(p=>({id:p.id,name:p.name,emoji:p.emoji,main:!!p.main,openingIQD:0,openingUSD:0}));
  const categories=[];let ci=0;
  for(const p of presets){for(const [name,emoji] of p.expense)categories.push({id:'c'+(++ci),walletId:p.id,type:'expense',name,emoji,archived:false});for(const [name,emoji] of p.income)categories.push({id:'c'+(++ci),walletId:p.id,type:'income',name,emoji,archived:false})}
  return{dark:false,baseCurrency:null,onboarded:false,selectedMonth:today().slice(0,7),wallets,categories,transactions:[],rates:[],version:5}
}
let state=load(),filter='all',modal={type:'expense',currency:(state.baseCurrency||'IQD'),editId:null},activeWalletId=null;
let actionHandler=null,actionDeleteHandler=null;
function openActionModal(title,fields,onSubmit,opts={}){actionHandler=onSubmit||null;actionDeleteHandler=opts.onDelete||null;document.getElementById('actionTitle').textContent=title;const box=document.getElementById('actionFields');box.innerHTML='';for(const f of (fields||[])){const wrap=document.createElement('div');wrap.className='field';const lab=document.createElement('div');lab.className='label';lab.textContent=f.label||'';wrap.appendChild(lab);let el;if(f.type==='select'){el=document.createElement('select');for(const o of (f.options||[])){const op=document.createElement('option');op.value=o.value;op.textContent=o.label;if(String(o.value)===String(f.value??''))op.selected=true;el.appendChild(op)}}else{el=document.createElement('input');el.type=f.type||'text';el.value=f.value??'';if(f.placeholder)el.placeholder=f.placeholder;if(f.inputmode)el.inputMode=f.inputmode;if(f.type==='number'){el.step=f.step||'any'}}el.dataset.actionField=f.id;wrap.appendChild(el);box.appendChild(wrap)}const msg=document.getElementById('actionMessage');msg.textContent=opts.message||'';msg.style.display=opts.message?'block':'none';const save=document.getElementById('actionSave');save.textContent=opts.submitText||'حفظ';save.style.display=opts.hideSubmit?'none':'block';const del=document.getElementById('actionDelete');del.style.display=actionDeleteHandler?'block':'none';del.textContent=opts.deleteText||'حذف';document.getElementById('actionModal').classList.add('show');setTimeout(()=>{const first=box.querySelector('input,select');if(first)first.focus()},50)}
function closeActionModal(){document.getElementById('actionModal').classList.remove('show');actionHandler=null;actionDeleteHandler=null}
function actionValues(){const v={};document.querySelectorAll('#actionFields [data-action-field]').forEach(el=>v[el.dataset.actionField]=el.value);return v}
function submitActionModal(){if(!actionHandler){closeActionModal();return}const fn=actionHandler,vals=actionValues();const result=fn(vals);if(result!==false)closeActionModal()}
function runActionDelete(){if(!actionDeleteHandler)return;const fn=actionDeleteHandler;const result=fn();if(result!==false)closeActionModal()}
function confirmAction(title,message,onYes,yesText='تأكيد'){openActionModal(title,[],()=>{onYes();return true},{message,submitText:yesText})}
function load(){try{const x=JSON.parse(localStorage.getItem(KEY));if(x&&Array.isArray(x.wallets)&&Array.isArray(x.transactions)&&Array.isArray(x.rates)){if(!x.selectedMonth)x.selectedMonth=today().slice(0,7);if(!('baseCurrency' in x))x.baseCurrency=null;if(!('onboarded' in x))x.onboarded=!!x.baseCurrency;return x}}catch(e){}return fresh()}
function persist(){localStorage.setItem(KEY,JSON.stringify(state))}
function digits(s){const a='٠١٢٣٤٥٦٧٨٩',b='۰۱۲۳۴۵۶۷۸۹';return String(s??'').replace(/[٠-٩]/g,c=>a.indexOf(c)).replace(/[۰-۹]/g,c=>b.indexOf(c))}
function nval(s){const n=Number(digits(s).replace(/[\s,٬]/g,'').replace(/٫/g,'.'));return Number.isFinite(n)?n:0}
function commas(n,dec=0){return Number(n||0).toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec})}
function money(amount,c){return c==='USD'?'$'+commas(amount,2):commas(amount)+' د.ع'}
function formatAmount(el){let s=digits(el.value).replace(/[^0-9.]/g,'');const p=s.split('.');if(p.length>2)s=p.shift()+'.'+p.join('');const [i,d]=s.split('.');el.value=(i?Number(i).toLocaleString('en-US'):'')+(d!==undefined?'.'+d.slice(0,2):'')}
function esc(s){return String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}
function wallet(id){return state.wallets.find(w=>w.id===id)||{name:'محفظة محذوفة',emoji:'💼'}}
function category(id){return state.categories.find(c=>c.id===id)||{name:'بدون تقسيم',emoji:'📌'}}
function rateFor(date){const arr=state.rates.slice().sort((a,b)=>a.date.localeCompare(b.date));let r=0;for(const x of arr){if(x.date<=date)r=Number(x.rate)||r;else break}return Number(r)||0}
function currentRate(){return rateFor(today())}
function monthEndDate(m){const [y,mo]=m.split('-').map(Number),d=new Date(y,mo,0);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}
function selectedCutoff(){const m=state.selectedMonth||today().slice(0,7),cm=today().slice(0,7);return m===cm?today():monthEndDate(m)}
function monthName(m){const names=['كانون الثاني','شباط','آذار','نيسان','أيار','حزيران','تموز','آب','أيلول','تشرين الأول','تشرين الثاني','كانون الأول'];const [y,mo]=m.split('-').map(Number);return names[mo-1]+' '+y}
function valueInBase(iqd,usd,date){const base=state.baseCurrency||'IQD',r=rateFor(date);if(base==='USD')return Number(usd||0)+(r>0?Number(iqd||0)/r:0);return Number(iqd||0)+(r>0?Number(usd||0)*r:0)}
function eqBase(t){const a=Number(t.amount||0),r=rateFor(t.date);if((state.baseCurrency||'IQD')==='USD')return t.currency==='USD'?a:(r>0?a/r:0);return t.currency==='IQD'?a:(r>0?a*r:0)}
function baseMoney(v){return money(v,state.baseCurrency||'IQD')}
function walletBalances(id,asOf=selectedCutoff()){const w=wallet(id);let iq=Number(w.openingIQD||0),usd=Number(w.openingUSD||0);for(const t of state.transactions){if((t.date||'')>asOf)continue;const a=Number(t.amount||0);if(t.type==='income'&&t.walletId===id){t.currency==='USD'?usd+=a:iq+=a}else if(t.type==='expense'&&t.walletId===id){t.currency==='USD'?usd-=a:iq-=a}else if(t.type==='transfer'){if(t.fromWalletId===id){t.currency==='USD'?usd-=a:iq-=a}if(t.toWalletId===id){t.currency==='USD'?usd+=a:iq+=a}}}return{iqd:iq,usd,equivalent:valueInBase(iq,usd,asOf)}}
function generalBalances(asOf=selectedCutoff()){let iqd=0,usd=0;for(const w of state.wallets){const b=walletBalances(w.id,asOf);iqd+=b.iqd;usd+=b.usd}return{iqd,usd,equivalent:valueInBase(iqd,usd,asOf)}}