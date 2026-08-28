from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

css = '''
.txFilterCard{padding:12px;margin-top:8px}.txFilterGrid{display:grid;grid-template-columns:1fr 1fr auto;gap:8px;align-items:end}.txFilterGrid .field{min-width:0}.txFilterGrid select,.txCustomRange input{width:100%;border:1px solid var(--line);background:var(--bg);color:var(--text);border-radius:12px;padding:10px;min-height:44px}.txCustomRange{display:none;grid-template-columns:1fr 1fr;gap:8px;margin-top:9px}.txCustomRange.show{display:grid}.txSummary{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:10px}.txSummary.walletSelected{grid-template-columns:repeat(5,1fr)}.txSummaryStat{background:var(--bg);border:1px solid var(--line);border-radius:13px;padding:9px 6px;text-align:center;min-width:0}.txSummaryStat small{display:block;color:var(--muted);font-size:9px;margin-bottom:4px}.txSummaryStat b{display:block;direction:ltr;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.txSummaryStat.expense b{color:var(--out)}.txSummaryStat.income b{color:var(--in)}.txSummaryStat.transfer b{color:var(--tr)}.txReset{border:1px solid var(--line);background:var(--card);color:var(--muted);border-radius:12px;padding:10px 11px;min-height:44px;white-space:nowrap}@media(max-width:620px){.txFilterGrid{grid-template-columns:1fr 1fr}.txFilterGrid .txReset{grid-column:1/-1}.txSummary.walletSelected{grid-template-columns:repeat(2,1fr)}.txSummary.walletSelected .txSummaryStat:last-child{grid-column:1/-1}.txSummary{grid-template-columns:repeat(3,1fr)}}
'''
if '.txFilterCard{' not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

old = '''<section id="transactions" class="page"><div class="sectionTitle"><h2 id="transactionsTitle">الحركات</h2><button class="pill" onclick="openTx('expense')">+ حركة</button></div><div class="filters"><button class="filter active" data-filter="all" onclick="setFilter('all',this)">الكل</button><button class="filter" data-filter="expense" onclick="setFilter('expense',this)">مصاريف</button><button class="filter" data-filter="income" onclick="setFilter('income',this)">إيرادات</button><button class="filter" data-filter="transfer" onclick="setFilter('transfer',this)">تحويلات</button></div><div class="card"><div id="txList"></div></div></section>'''
new = '''<section id="transactions" class="page"><div class="sectionTitle"><h2 id="transactionsTitle">الحركات</h2><button class="pill" onclick="openTx('expense')">+ حركة</button></div><div class="filters"><button class="filter active" data-filter="all" onclick="setFilter('all',this)">الكل</button><button class="filter" data-filter="expense" onclick="setFilter('expense',this)">مصاريف</button><button class="filter" data-filter="income" onclick="setFilter('income',this)">إيرادات</button><button class="filter" data-filter="transfer" onclick="setFilter('transfer',this)">تحويلات</button></div><div class="card txFilterCard"><div class="txFilterGrid"><div class="field"><div class="label">المحفظة</div><select id="txWalletFilter" onchange="setTxWalletFilter(this.value)"></select></div><div class="field"><div class="label">الفترة</div><select id="txPeriodFilter" onchange="setTxPeriodFilter(this.value)"><option value="displayedMonth">الشهر المعروض</option><option value="week">هذا الأسبوع</option><option value="month">هذا الشهر</option><option value="custom">نطاق تاريخ محدد</option><option value="all">كل الوقت</option></select></div><button class="txReset" onclick="resetTxFilters()">مسح الفلاتر</button></div><div id="txCustomRange" class="txCustomRange"><div class="field"><div class="label">من تاريخ</div><input id="txDateFrom" type="date" onchange="updateTxCustomRange()"></div><div class="field"><div class="label">إلى تاريخ</div><input id="txDateTo" type="date" onchange="updateTxCustomRange()"></div></div><div id="txFilterSummary" class="txSummary"></div></div><div class="card"><div id="txList"></div></div></section>'''
if old not in s:
    raise SystemExit('Transactions section not found')
s = s.replace(old, new, 1)

s = s.replace(
    "let state=load(),filter='all',modal={type:'expense'",
    "let state=load(),filter='all',txWalletFilter='all',txPeriodFilter='displayedMonth',txCustomFrom='',txCustomTo='',modal={type:'expense'",
    1,
)

replacement = r'''function setFilter(f,btn){filter=f;document.querySelectorAll('#transactions .filter').forEach(x=>x.classList.remove('active'));btn.classList.add('active');renderTransactions()}
function txLocalDate(s){const [y,m,d]=String(s||today()).split('-').map(Number);return new Date(y,m-1,d)}
function txDateText(d){return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}
function txCurrentWeekRange(){const d=txLocalDate(today()),daysFromSaturday=(d.getDay()+1)%7,start=new Date(d);start.setDate(d.getDate()-daysFromSaturday);const end=new Date(start);end.setDate(start.getDate()+6);return{from:txDateText(start),to:txDateText(end)}}
function txCurrentMonthRange(){const t=today().slice(0,7);return{from:t+'-01',to:monthEndDate(t)}}
function txDisplayedMonthRange(){const m=state.selectedMonth||today().slice(0,7);return{from:m+'-01',to:monthEndDate(m)}}
function txActiveRange(){if(txPeriodFilter==='week')return txCurrentWeekRange();if(txPeriodFilter==='month')return txCurrentMonthRange();if(txPeriodFilter==='displayedMonth')return txDisplayedMonthRange();if(txPeriodFilter==='custom')return{from:txCustomFrom||'',to:txCustomTo||''};return{from:'',to:''}}
function setTxWalletFilter(v){txWalletFilter=v||'all';renderTransactions()}
function setTxPeriodFilter(v){txPeriodFilter=v||'displayedMonth';if(txPeriodFilter==='custom'&&!txCustomFrom&&!txCustomTo){txCustomFrom=today();txCustomTo=today()}renderTransactions()}
function updateTxCustomRange(){const f=document.getElementById('txDateFrom'),t=document.getElementById('txDateTo');txCustomFrom=f?f.value:'';txCustomTo=t?t.value:'';if(txCustomFrom&&txCustomTo&&txCustomFrom>txCustomTo){toast('تاريخ البداية يجب أن يكون قبل تاريخ النهاية');return}renderTransactions()}
function resetTxFilters(){filter='all';txWalletFilter='all';txPeriodFilter='displayedMonth';txCustomFrom='';txCustomTo='';document.querySelectorAll('#transactions .filter').forEach(x=>x.classList.toggle('active',x.dataset.filter==='all'));renderTransactions()}
function txMatchesWallet(t,wid){if(wid==='all')return true;if(t.type==='transfer')return t.fromWalletId===wid||t.toWalletId===wid;return t.walletId===wid}
function filteredTransactions(){const range=txActiveRange();return state.transactions.filter(t=>{if(filter!=='all'&&t.type!==filter)return false;if(!txMatchesWallet(t,txWalletFilter))return false;const d=t.date||'';if(range.from&&d<range.from)return false;if(range.to&&d>range.to)return false;return true}).slice().sort((a,b)=>(b.date||'').localeCompare(a.date||'')||(b.created||0)-(a.created||0))}
function txPeriodLabel(){if(txPeriodFilter==='week'){const r=txCurrentWeekRange();return `هذا الأسبوع ${fmtDate(r.from)} - ${fmtDate(r.to)}`}if(txPeriodFilter==='month')return 'هذا الشهر';if(txPeriodFilter==='displayedMonth')return monthName(state.selectedMonth||today().slice(0,7));if(txPeriodFilter==='custom'){if(txCustomFrom&&txCustomTo)return `${fmtDate(txCustomFrom)} - ${fmtDate(txCustomTo)}`;return 'نطاق مخصص'}return 'كل الوقت'}
function renderTransactions(){const title=document.getElementById('transactionsTitle');if(title)title.innerHTML='الحركات <span class="monthInline">'+esc(txPeriodLabel())+'</span>';const walletSel=document.getElementById('txWalletFilter');if(walletSel){walletSel.innerHTML='<option value="all">كل المحافظ</option>'+state.wallets.map(w=>`<option value="${w.id}">${w.emoji} ${esc(w.name)}</option>`).join('');if(state.wallets.some(w=>w.id===txWalletFilter)||txWalletFilter==='all')walletSel.value=txWalletFilter;else txWalletFilter='all'}const periodSel=document.getElementById('txPeriodFilter');if(periodSel)periodSel.value=txPeriodFilter;const custom=document.getElementById('txCustomRange');if(custom)custom.classList.toggle('show',txPeriodFilter==='custom');const fromEl=document.getElementById('txDateFrom'),toEl=document.getElementById('txDateTo');if(fromEl)fromEl.value=txCustomFrom;if(toEl)toEl.value=txCustomTo;const arr=filteredTransactions();let income=0,expense=0,transferIn=0,transferOut=0;for(const t of arr){if(t.type==='income')income+=eqBase(t);else if(t.type==='expense')expense+=eqBase(t);else if(t.type==='transfer'&&txWalletFilter!=='all'){if(t.toWalletId===txWalletFilter)transferIn+=eqBase(t);if(t.fromWalletId===txWalletFilter)transferOut+=eqBase(t)}}const summary=document.getElementById('txFilterSummary');if(summary){summary.classList.toggle('walletSelected',txWalletFilter!=='all');let html=`<div class="txSummaryStat expense"><small>المصروفات</small><b>${baseMoney(expense)}</b></div><div class="txSummaryStat income"><small>الإيرادات</small><b>${baseMoney(income)}</b></div>`;if(txWalletFilter!=='all')html+=`<div class="txSummaryStat transfer"><small>تحويل داخل</small><b>${baseMoney(transferIn)}</b></div><div class="txSummaryStat transfer"><small>تحويل خارج</small><b>${baseMoney(transferOut)}</b></div>`;html+=`<div class="txSummaryStat"><small>عدد الحركات</small><b>${arr.length}</b></div>`;summary.innerHTML=html}document.getElementById('txList').innerHTML=arr.map(txHtml).join('')||'<div class="empty">لا توجد حركات ضمن الفلاتر المحددة.</div>'}
function openMonthlyPage'''
s, n = re.subn(r"function setFilter\(f,btn\)\{.*?\}\nfunction renderTransactions\(\)\{.*?\}\nfunction openMonthlyPage", lambda m: replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Could not patch transaction filter functions')

required = ['txWalletFilter', 'txPeriodFilter', 'txCurrentWeekRange', 'نطاق تاريخ محدد', 'txFilterSummary', 'filteredTransactions']
missing = [x for x in required if x not in s]
if missing:
    raise SystemExit('Transaction filter patch validation failed: ' + ', '.join(missing))

p.write_text(s, encoding='utf-8')
print('Transaction filters patch applied')
