from pathlib import Path
import re

p=Path('app/src/main/assets/index.html')
s=p.read_text(encoding='utf-8')

# CSS / safe area and multicurrency UI
css='''
.app{padding-top:calc(10px + env(safe-area-inset-top))!important}.currency select{border:1px solid var(--line);background:var(--card);color:var(--text);border-radius:10px;padding:8px;min-width:92px;max-width:130px}.currencyChips{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}.currencyChip{display:inline-flex;align-items:center;gap:5px;border:1px solid var(--line);background:var(--bg);border-radius:999px;padding:6px 9px;font-size:10px}.currencyChip button{border:0;background:transparent;color:var(--out);font-weight:bold;padding:0}.walletCurrencies{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}.walletCurrencies span{direction:ltr;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:6px 8px;font-size:10px}.ratePair{direction:ltr;font-weight:bold}.rateTable td.rateVal{direction:ltr}.fxHint{font-size:10px;color:var(--muted);line-height:1.6;margin-top:5px}
'''
if '.currencyChips{' not in s:
    s=s.replace('</style>',css+'</style>',1)

s=s.replace('''<div class="currency"><button id="curIQD" onclick="setCurrency('IQD')">IQD</button><button id="curUSD" onclick="setCurrency('USD')">USD</button></div>''','''<div class="currency"><select id="currencySelect" onchange="setCurrency(this.value)"></select></div>''')
s=s.replace('''<div class="monthlyCurrency"><button id="mCurIQD" onclick="setMonthlyCurrency('IQD')">IQD</button><button id="mCurUSD" onclick="setMonthlyCurrency('USD')">USD</button></div>''','''<div class="monthlyCurrency"><select id="monthlyCurrencySelect" onchange="setMonthlyCurrency(this.value)"></select></div>''')

s=re.sub(r'<section id="rates" class="page">.*?</section>', '''<section id="rates" class="page"><div class="sectionTitle"><h2>أسعار الصرف</h2><button class="pill" onclick="addRate()">+ سعر جديد</button></div><div class="card"><div class="head"><div><h2>سجل أسعار الصرف اليدوي</h2><div class="small">حدد زوج العملات والسعر والتاريخ يدويًا. لا يوجد تحديث تلقائي.</div></div></div><div id="rateSummary" class="settingrow"></div><div style="overflow:auto"><table class="rateTable"><thead><tr><th>من تاريخ</th><th>الزوج</th><th>السعر</th><th>الحالة</th><th></th></tr></thead><tbody id="rateRows"></tbody></table></div></div></section>''',s,count=1,flags=re.S)

needle='<div class="settingrow"><div><b>الوضع الداكن</b>'
insert='''<div class="settingrow"><div><b>العملات المفعّلة</b><small>فعّل أي عدد من العملات، وكل حركة تختار عملتها</small><div id="activeCurrencyChips" class="currencyChips"></div></div><button class="normal" onclick="addActiveCurrency()">+ عملة</button></div>'''
if 'id="activeCurrencyChips"' not in s:
    s=s.replace(needle,insert+needle,1)

core=r'''const CURRENCY_CATALOG={IQD:'الدينار العراقي',USD:'الدولار الأمريكي',EUR:'اليورو',GBP:'الجنيه الإسترليني',TRY:'الليرة التركية',SAR:'الريال السعودي',AED:'الدرهم الإماراتي',JOD:'الدينار الأردني',KWD:'الدينار الكويتي',QAR:'الريال القطري',BHD:'الدينار البحريني',OMR:'الريال العماني',EGP:'الجنيه المصري',SYP:'الليرة السورية',LBP:'الليرة اللبنانية',IRR:'الريال الإيراني',CNY:'اليوان الصيني',JPY:'الين الياباني',KRW:'الوون الكوري',INR:'الروبية الهندية',PKR:'الروبية الباكستانية',AUD:'الدولار الأسترالي',CAD:'الدولار الكندي',CHF:'الفرنك السويسري',SEK:'الكرونة السويدية',NOK:'الكرونة النرويجية',DKK:'الكرونة الدنماركية',RUB:'الروبل الروسي',UAH:'الهريفنيا الأوكرانية',PLN:'الزلوتي البولندي',CZK:'الكورونا التشيكية',HUF:'الفورنت المجري',RON:'الليو الروماني',BGN:'الليف البلغاري',GEL:'اللاري الجورجي',AZN:'المانات الأذربيجاني',AMD:'الدرام الأرمني',KZT:'التينغي الكازاخستاني',UZS:'السوم الأوزبكي',AFN:'الأفغاني',BDT:'التاكا البنغلاديشية',LKR:'الروبية السريلانكية',NPR:'الروبية النيبالية',IDR:'الروبية الإندونيسية',MYR:'الرينغيت الماليزي',SGD:'الدولار السنغافوري',THB:'البات التايلندي',VND:'الدونغ الفيتنامي',PHP:'البيزو الفلبيني',NZD:'الدولار النيوزيلندي',ZAR:'الراند الجنوب أفريقي',MAD:'الدرهم المغربي',DZD:'الدينار الجزائري',TND:'الدينار التونسي',LYD:'الدينار الليبي',SDG:'الجنيه السوداني',ETB:'البير الإثيوبي',KES:'الشلن الكيني',NGN:'النايرا النيجيرية',GHS:'السيدي الغاني',BRL:'الريال البرازيلي',ARS:'البيزو الأرجنتيني',MXN:'البيزو المكسيكي',CLP:'البيزو التشيلي',COP:'البيزو الكولومبي',PEN:'السول البيروفي'};
function ensureCurrencyState(){if(!Array.isArray(state.activeCurrencies)||!state.activeCurrencies.length)state.activeCurrencies=['IQD','USD'];if(!state.activeCurrencies.includes(state.baseCurrency||'IQD'))state.activeCurrencies.unshift(state.baseCurrency||'IQD');state.activeCurrencies=[...new Set(state.activeCurrencies)];if(!Array.isArray(state.fxRates))state.fxRates=[];if(!state.fxRates.length&&Array.isArray(state.rates)){for(const r of state.rates){if(Number(r.rate)>0)state.fxRates.push({id:r.id||uid(),from:'USD',to:'IQD',date:r.date,rate:Number(r.rate)})}}for(const w of state.wallets||[]){if(!w.openingBalances)w.openingBalances={IQD:Number(w.openingIQD||0),USD:Number(w.openingUSD||0)}}}
ensureCurrencyState();
function activeCurrencies(){ensureCurrencyState();return state.activeCurrencies.slice()}
function currencyName(c){return CURRENCY_CATALOG[c]||c}
function currencyLabel(c){return c+' - '+currencyName(c)}
function currencyOptions(selected){return activeCurrencies().map(c=>`<option value="${c}" ${c===selected?'selected':''}>${currencyLabel(c)}</option>`).join('')}
function money(n,c){const v=Number(n||0),dec=(c==='IQD'||Math.abs(v)>=1000)?0:2;return commas(v,dec)+' '+c}
function pairRate(from,to,date){if(from===to)return 1;ensureCurrencyState();const d=date||today(),direct=state.fxRates.filter(r=>r.from===from&&r.to===to&&r.date<=d).sort((a,b)=>a.date.localeCompare(b.date)).pop();if(direct&&Number(direct.rate)>0)return Number(direct.rate);const inv=state.fxRates.filter(r=>r.from===to&&r.to===from&&r.date<=d).sort((a,b)=>a.date.localeCompare(b.date)).pop();if(inv&&Number(inv.rate)>0)return 1/Number(inv.rate);return 0}
function convertCurrency(amount,from,to,date){amount=Number(amount||0);if(from===to)return amount;let r=pairRate(from,to,date);if(r>0)return amount*r;const base=state.baseCurrency||'IQD';if(from!==base&&to!==base){const a=pairRate(from,base,date),b=pairRate(base,to,date);if(a>0&&b>0)return amount*a*b}return 0}
function eqBase(t){return convertCurrency(Number(t.amount||0),t.currency||state.baseCurrency||'IQD',state.baseCurrency||'IQD',t.date||today())}
function baseMoney(v){return money(v,state.baseCurrency||'IQD')}
function walletBalances(id,asOf=selectedCutoff()){ensureCurrencyState();const w=wallet(id),amounts={};for(const c of activeCurrencies())amounts[c]=Number((w.openingBalances||{})[c]||0);for(const t of state.transactions){if((t.date||'')>asOf)continue;const c=t.currency||state.baseCurrency||'IQD',a=Number(t.amount||0);if(amounts[c]===undefined)amounts[c]=0;if(t.type==='income'&&t.walletId===id)amounts[c]+=a;else if(t.type==='expense'&&t.walletId===id)amounts[c]-=a;else if(t.type==='transfer'){if(t.fromWalletId===id)amounts[c]-=a;if(t.toWalletId===id)amounts[c]+=a}}let equivalent=0;for(const [c,a] of Object.entries(amounts)){const v=convertCurrency(a,c,state.baseCurrency||'IQD',asOf);if(c===(state.baseCurrency||'IQD')||v!==0)equivalent+=c===(state.baseCurrency||'IQD')?a:v}return{amounts,iqd:Number(amounts.IQD||0),usd:Number(amounts.USD||0),equivalent}}
function generalBalances(asOf=selectedCutoff()){const amounts={};for(const w of state.wallets){const b=walletBalances(w.id,asOf);for(const [c,a] of Object.entries(b.amounts)){amounts[c]=(amounts[c]||0)+a}}let equivalent=0;for(const [c,a] of Object.entries(amounts)){const v=convertCurrency(a,c,state.baseCurrency||'IQD',asOf);if(c===(state.baseCurrency||'IQD')||v!==0)equivalent+=c===(state.baseCurrency||'IQD')?a:v}return{amounts,iqd:Number(amounts.IQD||0),usd:Number(amounts.USD||0),equivalent}}
function currencyBalancesHtml(b){const rows=Object.entries(b.amounts||{}).filter(([,v])=>Math.abs(Number(v))>0.000001);return `<div class="walletCurrencies">${(rows.length?rows:[[state.baseCurrency||'IQD',0]]).map(([c,v])=>`<span>${money(v,c)}</span>`).join('')}</div>`}
'''
pat=r"function money\(n,c\)\{.*?function generalBalances\(asOf=selectedCutoff\(\)\)\{.*?\}\n(?=function monthTotals)"
s,n=re.subn(pat,lambda m:core+'\n',s,count=1,flags=re.S)
if n!=1: raise SystemExit('core accounting block not patched')

s=re.sub(r"function walletHtml\(w\)\{.*?\}\n(?=function renderWallets)",lambda m:r'''function walletHtml(w){const b=walletBalances(w.id);return `<button class="wallet ${w.main?'main':''}" onclick="openWallet('${w.id}')"><div class="walletTop"><div class="wemoji">${w.emoji}</div><div><b>${esc(w.name)}</b><small>الرصيد حتى ${fmtDate(selectedCutoff())}</small></div></div>${currencyBalancesHtml(b)}<div class="walletAmount"><span>≈ ${baseMoney(b.equivalent)}</span></div></button>`}
''',s,count=1,flags=re.S)
s=re.sub(r"function renderWallets\(\)\{.*?\}\n(?=function addWallet)",lambda m:r'''function renderWallets(){const g=generalBalances();document.getElementById('generalWalletCard').innerHTML=`<div class="wallet generalWallet"><div class="walletTop"><div class="wemoji">🌐</div><div><b>المحفظة العامة</b><small>الحساب العام حتى ${fmtDate(selectedCutoff())} • العملة الأساسية ${state.baseCurrency||'—'}</small></div></div>${currencyBalancesHtml(g)}<div class="walletAmount"><span>≈ ${baseMoney(g.equivalent)}</span></div></div>`;document.getElementById('walletList').innerHTML=state.wallets.map(walletHtml).join('')||'<div class="empty">لا توجد محافظ.</div>';if(activeWalletId)renderWalletDetail()}
''',s,count=1,flags=re.S)
s=s.replace("document.getElementById('wdBalance').innerHTML=`<div class=\"walletAmount\"><span>${money(b.iqd,'IQD')}</span><span>${money(b.usd,'USD')}</span><span>≈ ${baseMoney(b.equivalent)}</span></div>`;","document.getElementById('wdBalance').innerHTML=currencyBalancesHtml(b)+`<div class=\"walletAmount\"><span>≈ ${baseMoney(b.equivalent)}</span></div>`;")

s=re.sub(r"function addWallet\(\)\{.*?\}\n(?=function openWallet)",lambda m:r'''function addWallet(){openActionModal('إضافة محفظة',[{id:'name',label:'اسم المحفظة',type:'text',placeholder:'مثال: البيت'},{id:'emoji',label:'رمز المحفظة',type:'text',value:'💼'}],v=>{const name=(v.name||'').trim();if(!name){toast('اكتب اسم المحفظة');return false}const w={id:uid(),name,emoji:(v.emoji||'💼').trim()||'💼',main:state.wallets.length===0,openingIQD:0,openingUSD:0,openingBalances:{}};for(const c of activeCurrencies())w.openingBalances[c]=0;state.wallets.push(w);persist();renderAll();toast('تمت إضافة المحفظة');return true})}
''',s,count=1,flags=re.S)
start=s.find('function walletActions()')
end=s.find('\nfunction addCategory',start)
if start<0 or end<0: raise SystemExit('walletActions not found')
new_wallet_actions=r'''function walletActions(){const w=state.wallets.find(x=>x.id===activeWalletId);if(!w)return;ensureCurrencyState();const fields=[{id:'name',label:'اسم المحفظة',type:'text',value:w.name},{id:'emoji',label:'الرمز',type:'text',value:w.emoji},...activeCurrencies().map(c=>({id:'opening_'+c,label:'الرصيد الافتتاحي '+currencyLabel(c),type:'number',value:Number((w.openingBalances||{})[c]||0),inputmode:'decimal'})),{id:'main',label:'نوع المحفظة',type:'select',value:w.main?'yes':'no',options:[{value:'no',label:'محفظة عادية'},{value:'yes',label:'المحفظة الرئيسية'}]}];openActionModal('إعدادات المحفظة',fields,v=>{const name=(v.name||'').trim();if(!name){toast('اسم المحفظة مطلوب');return false}w.name=name;w.emoji=(v.emoji||'💼').trim()||'💼';if(!w.openingBalances)w.openingBalances={};for(const c of activeCurrencies())w.openingBalances[c]=nval(v['opening_'+c]);w.openingIQD=Number(w.openingBalances.IQD||0);w.openingUSD=Number(w.openingBalances.USD||0);if(v.main==='yes')state.wallets.forEach(x=>x.main=x.id===w.id);persist();renderAll();toast('تم حفظ إعدادات المحفظة');return true},{onDelete:()=>{if(state.wallets.length===1){toast('لا يمكن حذف آخر محفظة');return false}if(state.transactions.some(t=>t.walletId===w.id||t.fromWalletId===w.id||t.toWalletId===w.id)||(state.monthlyTemplates||[]).some(t=>t.walletId===w.id||t.fromWalletId===w.id||t.toWalletId===w.id)){toast('لا يمكن حذف محفظة مستخدمة في حركة أو بند شهري');return false}state.wallets=state.wallets.filter(x=>x.id!==w.id);state.categories=state.categories.filter(x=>x.walletId!==w.id);if(w.main&&state.wallets[0])state.wallets[0].main=true;closeWalletDetail();persist();renderAll();toast('تم حذف المحفظة');return true},deleteText:'حذف المحفظة'})}'''
s=s[:start]+new_wallet_actions+s[end:]

s=re.sub(r"function setCurrency\(c\)\{.*?\}\n",lambda m:r'''function fillCurrencySelects(){const a=document.getElementById('currencySelect');if(a)a.innerHTML=currencyOptions(modal.currency);const b=document.getElementById('monthlyCurrencySelect');if(b)b.innerHTML=currencyOptions(monthlyModal.currency)}
function setCurrency(c){modal.currency=c||state.baseCurrency||'IQD';fillCurrencySelects();const e=document.getElementById('currencySelect');if(e)e.value=modal.currency;updateRatePreview()}
''',s,count=1,flags=re.S)
s=re.sub(r"function setMonthlyCurrency\(c\)\{.*?\}\n",lambda m:r'''function setMonthlyCurrency(c){monthlyModal.currency=c||state.baseCurrency||'IQD';fillCurrencySelects();const e=document.getElementById('monthlyCurrencySelect');if(e)e.value=monthlyModal.currency}
''',s,count=1,flags=re.S)
s=s.replace("commas(t.amount,t.currency==='USD'?2:0)","commas(t.amount,(t.currency==='IQD'||Number(t.amount)>=1000)?0:2)")

s=re.sub(r"function updateRatePreview\(\)\{.*?\}\n",lambda m:r'''function updateRatePreview(){const d=document.getElementById('dateInput').value||today(),c=modal.currency||state.baseCurrency||'IQD',base=state.baseCurrency||'IQD',v=convertCurrency(1,c,base,d);document.getElementById('ratePreview').value=c===base?'نفس العملة':(v?`1 ${c} = ${commas(v,4)} ${base}`:'لا يوجد سعر مسجل لهذا الزوج والتاريخ')}
''',s,count=1,flags=re.S)

rate_start=s.find('function addRate()')
rate_end=s.find('\nfunction bsMonthTx',rate_start)
if rate_start<0 or rate_end<0: raise SystemExit('rate block not found')
rate_code=r'''function addRate(){ensureCurrencyState();const all=activeCurrencies();if(all.length<2){toast('فعّل عملتين على الأقل');return}openActionModal('إضافة سعر صرف',[{id:'from',label:'من عملة',type:'select',value:all[0],options:all.map(c=>({value:c,label:currencyLabel(c)}))},{id:'to',label:'إلى عملة',type:'select',value:all[1]||all[0],options:all.map(c=>({value:c,label:currencyLabel(c)}))},{id:'date',label:'من تاريخ',type:'date',value:today()},{id:'rate',label:'قيمة 1 من العملة الأولى بالعملة الثانية',type:'number',placeholder:'مثال: 1320',inputmode:'decimal'}],v=>{const from=v.from,to=v.to,date=v.date,rate=nval(v.rate);if(from===to){toast('اختر عملتين مختلفتين');return false}if(!date||rate<=0){toast('أدخل تاريخًا وسعرًا صحيحين');return false}const same=state.fxRates.find(r=>r.from===from&&r.to===to&&r.date===date);if(same)same.rate=rate;else state.fxRates.push({id:uid(),from,to,date,rate});state.fxRates.sort((a,b)=>a.date.localeCompare(b.date));persist();renderAll();toast(same?'تم تحديث سعر الصرف':'تم حفظ سعر الصرف');return true},{message:'السعر يدوي بالكامل: مثال إذا اخترت USD → IQD وكتبت 1320 فهذا يعني 1 USD = 1320 IQD.'})}
function renderRates(){ensureCurrencyState();const base=state.baseCurrency||'IQD',pairs=state.fxRates.filter(r=>r.date<=today());document.getElementById('rateSummary').innerHTML=`<div><b>العملة الأساسية: ${base}</b><small>الأسعار تدخل يدويًا، ويمكن تسجيل أي زوج من العملات المفعّلة.</small></div><div class="rateCurrent">${pairs.length} سعر مسجل</div>`;const arr=state.fxRates.slice().sort((a,b)=>b.date.localeCompare(a.date));document.getElementById('rateRows').innerHTML=arr.map(r=>{const current=state.fxRates.filter(x=>x.from===r.from&&x.to===r.to&&x.date<=today()).sort((a,b)=>a.date.localeCompare(b.date)).pop()?.id===r.id;return `<tr><td>${fmtDate(r.date)}</td><td class="ratePair">${r.from} → ${r.to}</td><td class="rateVal">${commas(r.rate,6)}</td><td>${current?'<span class="rateCurrent">ساري</span>':'تاريخي'}</td><td><button class="normal" onclick="editRate('${r.id}')">تعديل</button></td></tr>`}).join('')||'<tr><td colspan="5" class="empty">لا توجد أسعار صرف بعد.</td></tr>'}
function editRate(id){const r=state.fxRates.find(x=>x.id===id);if(!r)return;const all=activeCurrencies();openActionModal('تعديل سعر الصرف',[{id:'from',label:'من عملة',type:'select',value:r.from,options:all.map(c=>({value:c,label:currencyLabel(c)}))},{id:'to',label:'إلى عملة',type:'select',value:r.to,options:all.map(c=>({value:c,label:currencyLabel(c)}))},{id:'date',label:'من تاريخ',type:'date',value:r.date},{id:'rate',label:'السعر',type:'number',value:r.rate,inputmode:'decimal'}],v=>{const rate=nval(v.rate);if(v.from===v.to||!v.date||rate<=0){toast('تحقق من زوج العملات والتاريخ والسعر');return false}r.from=v.from;r.to=v.to;r.date=v.date;r.rate=rate;persist();renderAll();toast('تم تعديل السعر');return true},{onDelete:()=>{state.fxRates=state.fxRates.filter(x=>x.id!==id);persist();renderAll();toast('تم حذف سعر الصرف');return true},deleteText:'حذف هذا السعر'})}'''
s=s[:rate_start]+rate_code+s[rate_end:]

settings_start=s.find('function currencyLabel(c)', s.find('function goPage(p)'))
if settings_start>=0:
    settings_end=s.find('function renderSettings()',settings_start)
    if settings_end<0: raise SystemExit('renderSettings anchor missing')
    settings_code=r'''function addActiveCurrency(){ensureCurrencyState();const choices=Object.keys(CURRENCY_CATALOG).filter(c=>!state.activeCurrencies.includes(c)).map(c=>({value:c,label:currencyLabel(c)}));if(!choices.length){toast('كل العملات المتاحة مفعّلة');return}openActionModal('إضافة عملة',[{id:'currency',label:'اختر العملة',type:'select',value:choices[0].value,options:choices}],v=>{if(!v.currency)return false;state.activeCurrencies.push(v.currency);persist();renderAll();toast('تمت إضافة '+v.currency);return true})}
function removeActiveCurrency(c){ensureCurrencyState();if(c===state.baseCurrency){toast('لا يمكن حذف العملة الأساسية');return}if(state.transactions.some(t=>t.currency===c)||(state.monthlyTemplates||[]).some(t=>t.currency===c)){toast('لا يمكن حذف عملة مستخدمة في حركات أو بنود شهرية');return}state.activeCurrencies=state.activeCurrencies.filter(x=>x!==c);for(const w of state.wallets)if(w.openingBalances)delete w.openingBalances[c];persist();renderAll();toast('تم حذف '+c+' من العملات المفعّلة')}
function changeBaseCurrency(){ensureCurrencyState();openActionModal('العملة الأساسية',[{id:'base',label:'اختر العملة الأساسية للحساب العام',type:'select',value:state.baseCurrency||'IQD',options:activeCurrencies().map(c=>({value:c,label:currencyLabel(c)}))}],v=>{if(!v.base)return false;state.baseCurrency=v.base;state.onboarded=true;persist();renderAll();toast('تم تغيير العملة الأساسية');return true},{message:'لتظهر إجماليات العملات الأخرى بشكل صحيح، سجّل سعر صرف بينها وبين العملة الأساسية أو مسار تحويل متاح.'})}
function ensureOnboarding(){ensureCurrencyState();if(state.onboarded&&state.baseCurrency)return;state.baseCurrency='IQD';state.onboarded=true;persist();renderAll()}
'''
    s=s[:settings_start]+settings_code+s[settings_end:]

s=re.sub(r"function renderSettings\(\)\{.*?\}\n(?=function exportData)",lambda m:r'''function renderSettings(){ensureCurrencyState();document.body.classList.toggle('dark',!!state.dark);document.getElementById('darkBtn').textContent=state.dark?'إيقاف':'تشغيل';document.getElementById('baseCurrencyBtn').textContent=state.baseCurrency?currencyLabel(state.baseCurrency):'اختيار';const chips=document.getElementById('activeCurrencyChips');if(chips)chips.innerHTML=activeCurrencies().map(c=>`<span class="currencyChip"><b>${c}</b>${c===state.baseCurrency?'<small>أساسية</small>':`<button onclick="removeActiveCurrency('${c}')">×</button>`}</span>`).join('')}
''',s,count=1,flags=re.S)

s=re.sub(r"const rr=rateFor\(cut\);document\.getElementById\('rateStatLabel'\)\.textContent=.*?document\.getElementById\('todayRate'\)\.textContent=rr\?commas\(rr\):'غير مسجل';", "document.getElementById('rateStatLabel').textContent='أسعار الصرف اليدوية';document.getElementById('todayRate').textContent=(state.fxRates||[]).filter(r=>r.date<=cut).length+' مسجل';", s, count=1, flags=re.S)

if 'function rateFor(date)' not in s:
    idx=s.find('function selectedCutoff')
    s=s[:idx]+"function rateFor(date){return pairRate('USD','IQD',date)}\nfunction currentRate(){return rateFor(today())}\n"+s[idx:]

# Remove the old USD/IQD-only renderer that appears later in the original source.
first=s.find('function renderRates()')
second=s.find('function renderRates()', first+1)
if second>=0:
    end=s.find('function goPage', second)
    if end<0: raise SystemExit('legacy renderRates end not found')
    s=s[:second]+s[end:]

p.write_text(s,encoding='utf-8')
print('Multi-currency and safe-area patch applied')
