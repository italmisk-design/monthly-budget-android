from pathlib import Path
import re

p=Path('app/src/main/assets/index.html')
s=p.read_text(encoding='utf-8')

# CSS: 3 monthly types + transfer colors
s=s.replace(
    ".monthlyType.income{background:rgba(22,153,96,.10);color:var(--in)}",
    ".monthlyType.income{background:rgba(22,153,96,.10);color:var(--in)}.monthlyType.transfer{background:rgba(71,104,216,.10);color:var(--tr)}"
)
s=s.replace(
    ".monthlyModalType{display:grid;grid-template-columns:1fr 1fr;gap:6px",
    ".monthlyModalType{display:grid;grid-template-columns:repeat(3,1fr);gap:6px"
)
s=s.replace(
    ".monthlyModalType button.active.income{background:var(--in);color:#fff}",
    ".monthlyModalType button.active.income{background:var(--in);color:#fff}.monthlyModalType button.active.transfer{background:var(--tr);color:#fff}"
)

# Modal: add transfer type button
old_type='''<div class="monthlyModalType"><button id="mTypeExpense" class="expense" onclick="setMonthlyType('expense')">مصروف</button><button id="mTypeIncome" class="income" onclick="setMonthlyType('income')">إيراد</button></div>'''
new_type='''<div class="monthlyModalType"><button id="mTypeExpense" class="expense" onclick="setMonthlyType('expense')">مصروف</button><button id="mTypeIncome" class="income" onclick="setMonthlyType('income')">إيراد</button><button id="mTypeTransfer" class="transfer" onclick="setMonthlyType('transfer')">تحويل</button></div>'''
if old_type not in s:
    raise SystemExit('monthly type markup not found')
s=s.replace(old_type,new_type,1)

# Modal: normal wallet/category fields vs transfer from/to fields
old_fields='''<div class="grid2"><div class="field"><div class="label">المحفظة</div><select id="monthlyWallet" onchange="renderMonthlyCategorySelect()"></select></div><div class="field"><div class="label">التقسيم</div><select id="monthlyCategory"></select></div></div>'''
new_fields='''<div id="monthlyNormalFields"><div class="grid2"><div class="field"><div class="label">المحفظة</div><select id="monthlyWallet" onchange="renderMonthlyCategorySelect()"></select></div><div class="field"><div class="label">التقسيم</div><select id="monthlyCategory"></select></div></div></div><div id="monthlyTransferFields" style="display:none"><div class="grid2"><div class="field"><div class="label">من محفظة</div><select id="monthlyFromWallet"></select></div><div class="field"><div class="label">إلى محفظة</div><select id="monthlyToWallet"></select></div></div></div>'''
if old_fields not in s:
    raise SystemExit('monthly fields markup not found')
s=s.replace(old_fields,new_fields,1)

# Replace monthly template editor/rendering functions
pattern=r"function monthlyTemplateValid\(t\)\{.*?\}\nfunction deleteMonthlyItem"
replacement=r'''function monthlyTemplateValid(t){if(t.type==='transfer'){const f=state.wallets.find(x=>x.id===t.fromWalletId),to=state.wallets.find(x=>x.id===t.toWalletId);return !!(f&&to&&f.id!==to.id)}const w=state.wallets.find(x=>x.id===t.walletId),c=state.categories.find(x=>x.id===t.categoryId);return !!(w&&c&&c.walletId===t.walletId&&c.type===t.type)}
function renderMonthly(){const list=document.getElementById('monthlyList');if(!list)return;const arr=state.monthlyTemplates||[];list.innerHTML=arr.map(t=>{const valid=monthlyTemplateValid(t);if(t.type==='transfer'){const f=wallet(t.fromWalletId),to=wallet(t.toWalletId);return `<button class="monthlyItem ${valid?'':'monthlyInvalid'}" onclick="editMonthlyItem('${t.id}')"><span class="monthlyType transfer">تحويل</span><span class="monthlyMain"><b>تحويل بين المحافظ</b><small>${esc(f.name)} → ${esc(to.name)}${t.note?' • '+esc(t.note):''}</small></span><span class="monthlyAmt">${money(t.amount,t.currency)}</span></button>`}const w=wallet(t.walletId),c=category(t.categoryId);return `<button class="monthlyItem ${valid?'':'monthlyInvalid'}" onclick="editMonthlyItem('${t.id}')"><span class="monthlyType ${t.type}">${t.type==='income'?'إيراد':'مصروف'}</span><span class="monthlyMain"><b>${esc(c.name)}</b><small>${esc(w.name)}${t.note?' • '+esc(t.note):''}</small></span><span class="monthlyAmt">${money(t.amount,t.currency)}</span></button>`}).join('')||'<div class="empty">ما عندك حركات شهرية محفوظة بعد.</div>';const runs=(state.monthlyRuns||[]).slice().sort((a,b)=>(b.created||0)-(a.created||0)),info=document.getElementById('monthlyRunInfo');if(info){info.innerHTML=runs.length?`آخر تنفيذ: <b>${fmtDate(runs[0].date)}</b> • ${runs[0].count} حركة`:'لم يتم تنفيذ القائمة سابقًا.'}}
function openMonthlyItem(){monthlyModal={type:'expense',currency:state.baseCurrency||'IQD',editId:null};document.getElementById('monthlyModalTitle').textContent='إضافة بند شهري';document.getElementById('monthlyAmount').value='';document.getElementById('monthlyNote').value='';document.getElementById('deleteMonthlyBtn').classList.remove('show');fillMonthlyWallets();setMonthlyType('expense');setMonthlyCurrency(monthlyModal.currency);document.getElementById('monthlyModal').classList.add('show')}
function closeMonthlyItem(){document.getElementById('monthlyModal').classList.remove('show')}
function fillMonthlyWallets(){const opts=state.wallets.map(w=>`<option value="${w.id}">${w.emoji} ${esc(w.name)}</option>`).join('');document.getElementById('monthlyWallet').innerHTML=opts;document.getElementById('monthlyFromWallet').innerHTML=opts;document.getElementById('monthlyToWallet').innerHTML=opts;if(state.wallets.length>1)document.getElementById('monthlyToWallet').selectedIndex=1;renderMonthlyCategorySelect()}
function setMonthlyType(type){monthlyModal.type=type;document.getElementById('mTypeExpense').classList.toggle('active',type==='expense');document.getElementById('mTypeIncome').classList.toggle('active',type==='income');document.getElementById('mTypeTransfer').classList.toggle('active',type==='transfer');document.getElementById('monthlyNormalFields').style.display=type==='transfer'?'none':'block';document.getElementById('monthlyTransferFields').style.display=type==='transfer'?'block':'none';if(type!=='transfer')renderMonthlyCategorySelect()}
function setMonthlyCurrency(c){monthlyModal.currency=c;document.getElementById('mCurIQD').classList.toggle('active',c==='IQD');document.getElementById('mCurUSD').classList.toggle('active',c==='USD')}
function renderMonthlyCategorySelect(){if(monthlyModal.type==='transfer')return;const wid=document.getElementById('monthlyWallet').value,type=monthlyModal.type,arr=state.categories.filter(c=>c.walletId===wid&&c.type===type&&!c.archived);document.getElementById('monthlyCategory').innerHTML=arr.map(c=>`<option value="${c.id}">${c.emoji} ${esc(c.name)}</option>`).join('')||'<option value="">لا يوجد تقسيم مناسب</option>'}
function saveMonthlyItem(){const amount=nval(document.getElementById('monthlyAmount').value),note=document.getElementById('monthlyNote').value.trim();if(amount<=0){toast('اكتب مبلغًا أكبر من صفر');return}let data={type:monthlyModal.type,currency:monthlyModal.currency,amount,note};if(monthlyModal.type==='transfer'){const fromWalletId=document.getElementById('monthlyFromWallet').value,toWalletId=document.getElementById('monthlyToWallet').value;if(!fromWalletId||!toWalletId||fromWalletId===toWalletId){toast('اختر محفظتين مختلفتين للتحويل');return}Object.assign(data,{fromWalletId,toWalletId})}else{const walletId=document.getElementById('monthlyWallet').value,categoryId=document.getElementById('monthlyCategory').value;if(!walletId||!categoryId){toast('اختر المحفظة والتقسيم');return}Object.assign(data,{walletId,categoryId})}if(monthlyModal.editId){const x=state.monthlyTemplates.find(t=>t.id===monthlyModal.editId);if(x){for(const k of Object.keys(x))if(!['id','created'].includes(k))delete x[k];Object.assign(x,data)}}else state.monthlyTemplates.push({id:uid(),created:Date.now(),...data});persist();closeMonthlyItem();renderMonthly();toast(monthlyModal.editId?'تم تعديل البند':'تمت إضافة البند الشهري')}
function editMonthlyItem(id){const t=state.monthlyTemplates.find(x=>x.id===id);if(!t)return;monthlyModal={type:t.type,currency:t.currency,editId:id};document.getElementById('monthlyModalTitle').textContent='تعديل البند الشهري';fillMonthlyWallets();setMonthlyType(t.type);if(t.type==='transfer'){document.getElementById('monthlyFromWallet').value=t.fromWalletId;document.getElementById('monthlyToWallet').value=t.toWalletId}else{document.getElementById('monthlyWallet').value=t.walletId;renderMonthlyCategorySelect();document.getElementById('monthlyCategory').value=t.categoryId}setMonthlyCurrency(t.currency);document.getElementById('monthlyAmount').value=commas(t.amount,t.currency==='USD'?2:0);document.getElementById('monthlyNote').value=t.note||'';document.getElementById('deleteMonthlyBtn').classList.add('show');document.getElementById('monthlyModal').classList.add('show')}
function deleteMonthlyItem'''
s2,n=re.subn(pattern,lambda m: replacement,s,count=1,flags=re.S)
if n!=1:
    raise SystemExit(f'monthly functions patch failed: {n}')
s=s2

# Transfers do not count as income or expense totals
old_summary="function monthlySummary(date,items){let income=0,expense=0;for(const t of items){const fake={amount:t.amount,currency:t.currency,date};if(t.type==='income')income+=eqBase(fake);else expense+=eqBase(fake)}return{income,expense}}"
new_summary="function monthlySummary(date,items){let income=0,expense=0;for(const t of items){const fake={amount:t.amount,currency:t.currency,date};if(t.type==='income')income+=eqBase(fake);else if(t.type==='expense')expense+=eqBase(fake)}return{income,expense}}"
if old_summary not in s:
    raise SystemExit('monthly summary not found')
s=s.replace(old_summary,new_summary,1)

# Do not allow deleting a wallet referenced by a saved monthly transfer
s=s.replace(
    "(state.monthlyTemplates||[]).some(t=>t.walletId===w.id)",
    "(state.monthlyTemplates||[]).some(t=>t.walletId===w.id||t.fromWalletId===w.id||t.toWalletId===w.id)",
    1
)

# Replace final review/execution after funding patch: income -> explicit transfers -> optional funding -> expenses
pattern2=r"function openMonthlyFinalReview\(date\)\{.*?\}\nfunction executeMonthlyRun\(date,fundExpenses=false\)\{.*?\}\nfunction openTx"
replacement2=r'''function openMonthlyFinalReview(date){const all=(state.monthlyTemplates||[]).filter(monthlyTemplateValid),month=date.slice(0,7),prev=(state.monthlyRuns||[]).filter(r=>(r.date||'').slice(0,7)===month),sum=monthlySummary(date,all),main=state.wallets.find(w=>w.main),explicitTransfers=all.filter(t=>t.type==='transfer');const expenseTargets={};for(const t of all){if(t.type!=='expense'||!main||t.walletId===main.id)continue;const key=t.walletId+'|'+t.currency;expenseTargets[key]=(expenseTargets[key]||0)+(Number(t.amount)||0)}const fundingLines=Object.entries(expenseTargets).map(([key,amount])=>{const [wid,cur]=key.split('|'),w=state.wallets.find(x=>x.id===wid);return `${w?w.name:'محفظة'}: ${money(amount,cur)}`});let msg=`سيتم تنفيذ ${all.length} بند بتاريخ ${fmtDate(date)} بالترتيب: الإيرادات ← التحويلات ← المصروفات.\nإجمالي الإيرادات: ${baseMoney(sum.income)}\nالتحويلات المحفوظة: ${explicitTransfers.length}\nإجمالي المصروفات: ${baseMoney(sum.expense)}.`;if(fundingLines.length)msg+=`\n\nخيار التمويل التلقائي اختياري ويضاف بعد التحويلات المحفوظة وقبل المصروفات. إذا فعلته سيتم التحويل من المحفظة الرئيسية إلى:\n${fundingLines.join('\n')}\nإذا كنت موزع هذه المبالغ أصلًا بتحويلات محفوظة، اترك خيار التمويل غير محدد حتى لا يتكرر التحويل.`;if(prev.length)msg=`تنبيه: سبق تنفيذ القائمة ${prev.length} مرة خلال ${monthName(month)}.\n\n`+msg;openActionModal('المراجعة النهائية',[{id:'fundExpenses',label:'موّل المصروفات تلقائيًا من المحفظة الرئيسية إلى المحافظ الفرعية',type:'checkbox',value:false},{id:'confirmed',label:'راجعت الحركات وأنا متأكد وموافق على الإضافة',type:'checkbox',value:false,confirmGate:true}],v=>{if(!v.confirmed)return false;if(v.fundExpenses&&!main){toast('حدد محفظة رئيسية أولًا');return false}executeMonthlyRun(date,!!v.fundExpenses);return true},{message:msg,submitText:'إضافة الحركات'})}
function executeMonthlyRun(date,fundExpenses=false){const items=(state.monthlyTemplates||[]).filter(monthlyTemplateValid),batchId=uid(),main=state.wallets.find(w=>w.main),incomes=items.filter(t=>t.type==='income'),transfers=items.filter(t=>t.type==='transfer'),expenses=items.filter(t=>t.type==='expense');let fundingCount=0,seq=0;const baseCreated=Date.now();const pushTemplate=t=>{const common={id:uid(),created:baseCreated+(seq++),type:t.type,currency:t.currency,amount:Number(t.amount)||0,date,note:t.note||'',monthlyTemplateId:t.id,monthlyBatchId:batchId};if(t.type==='transfer')state.transactions.push({...common,fromWalletId:t.fromWalletId,toWalletId:t.toWalletId});else state.transactions.push({...common,walletId:t.walletId,categoryId:t.categoryId})};for(const t of incomes)pushTemplate(t);for(const t of transfers)pushTemplate(t);if(fundExpenses&&main){const grouped={};for(const t of expenses){if(t.walletId===main.id)continue;const key=t.walletId+'|'+t.currency;if(!grouped[key])grouped[key]={walletId:t.walletId,currency:t.currency,amount:0};grouped[key].amount+=Number(t.amount)||0}for(const g of Object.values(grouped)){if(g.amount<=0)continue;state.transactions.push({id:uid(),created:baseCreated+(seq++),type:'transfer',currency:g.currency,amount:g.amount,date,note:'تمويل المصروفات الشهرية',fromWalletId:main.id,toWalletId:g.walletId,monthlyBatchId:batchId,monthlyFunding:true});fundingCount++}}for(const t of expenses)pushTemplate(t);if(!Array.isArray(state.monthlyRuns))state.monthlyRuns=[];state.monthlyRuns.push({id:batchId,date,created:Date.now(),count:items.length,funded:!!fundExpenses,fundingTransfers:fundingCount,explicitTransfers:transfers.length});state.selectedMonth=date.slice(0,7);persist();renderAll();goPage('home');toast(fundingCount?`تمت إضافة ${items.length} حركة و${fundingCount} تحويل تمويل`:`تمت إضافة ${items.length} حركة شهرية بنجاح`)}
function openTx'''
s2,n=re.subn(pattern2,lambda m: replacement2,s,count=1,flags=re.S)
if n!=1:
    raise SystemExit(f'final review/execution patch failed: {n}')
s=s2

required=[
    'mTypeTransfer','monthlyFromWallet','monthlyToWallet',"t.type==='transfer'",
    "for(const t of incomes)pushTemplate(t);for(const t of transfers)pushTemplate(t)",
    'explicitTransfers=all.filter', '.monthlyType.transfer', '.active.transfer'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit('validation failed: '+', '.join(missing))

p.write_text(s,encoding='utf-8')
print('monthly transfer patch applied')
