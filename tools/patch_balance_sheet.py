from pathlib import Path

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

css = r'''
.balanceLaunch{grid-column:1/-1;border:0;color:#fff;border-radius:17px;padding:14px 8px;font-weight:bold;background:linear-gradient(135deg,#176c5d,#b48b24)}
.bsTop{display:grid;grid-template-columns:48px 1fr 48px;gap:8px;align-items:center;margin:2px 0 10px}.bsTop button{min-height:46px;border:1px solid var(--line);background:var(--card);color:var(--text);border-radius:14px;box-shadow:var(--shadow)}.bsMonth{font-weight:800;text-align:center}.bsSummary{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.bsStat{border:1px solid var(--line);background:var(--bg);border-radius:15px;padding:10px;text-align:center;min-width:0}.bsStat small{display:block;color:var(--muted);font-size:9px;margin-bottom:5px}.bsStat b{display:block;direction:ltr;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.bsStat.income b{color:var(--in)}.bsStat.expense b{color:var(--out)}.bsStat.net b{color:var(--p)}.bsWallet{padding:0;overflow:hidden}.bsWalletHead{padding:13px 14px;background:linear-gradient(135deg,rgba(17,107,94,.08),rgba(201,156,42,.05));border-bottom:1px solid var(--line)}.bsWalletTitle{display:flex;justify-content:space-between;gap:10px;align-items:center}.bsWalletTitle strong{font-size:15px}.bsWalletTitle span{font-size:11px;color:var(--muted)}.bsWalletSummary{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin-top:10px}.bsMini{border:1px solid var(--line);background:var(--card);border-radius:12px;padding:8px;text-align:center;min-width:0}.bsMini small{display:block;color:var(--muted);font-size:9px}.bsMini b{display:block;direction:ltr;margin-top:4px;font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.bsMini.income b{color:var(--in)}.bsMini.expense b{color:var(--out)}.bsMini.net b{color:var(--p)}.bsBody{padding:12px 14px}.bsCols{display:grid;grid-template-columns:1fr 1fr;gap:10px}.bsGroup{border:1px solid var(--line);border-radius:14px;overflow:hidden}.bsGroupHead{display:flex;justify-content:space-between;gap:8px;padding:9px 10px;background:var(--bg);font-size:11px;font-weight:bold}.bsRows{padding:2px 10px}.bsRow{display:flex;justify-content:space-between;gap:8px;align-items:center;padding:8px 0;border-bottom:1px solid var(--line);font-size:11px}.bsRow:last-child{border-bottom:0}.bsRow .name{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.bsRow .amt{direction:ltr;font-weight:bold;white-space:nowrap}.bsEmpty{color:var(--muted);font-size:10px;padding:10px 0;text-align:center}.bsGrand{border:2px solid rgba(17,107,94,.25)}.bsBalanceLine{margin-top:9px;padding-top:9px;border-top:1px dashed var(--line);display:flex;justify-content:space-between;gap:8px;color:var(--muted);font-size:10px}.bsBalanceLine b{color:var(--text);direction:ltr}.bsNote{font-size:10px;line-height:1.7;color:var(--muted);margin-top:8px}
@media(max-width:620px){.bsSummary{grid-template-columns:1fr 1fr}.bsWalletSummary{grid-template-columns:1fr 1fr}.bsCols{grid-template-columns:1fr}}
'''
if '.bsWallet{' not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

old_quick = '''<div class="quick"><button class="q out" onclick="openTx('expense')">− إضافة مصروف</button><button class="q in" onclick="openTx('income')">+ إضافة إيراد</button><button class="q tr" onclick="openTx('transfer')">⇄ نقل بين المحافظ</button><button class="q month" onclick="openMonthlyPage()">▦ الحركات الشهرية</button></div>'''
new_quick = '''<div class="quick"><button class="q out" onclick="openTx('expense')">− إضافة مصروف</button><button class="q in" onclick="openTx('income')">+ إضافة إيراد</button><button class="q tr" onclick="openTx('transfer')">⇄ نقل بين المحافظ</button><button class="q month" onclick="openMonthlyPage()">▦ الحركات الشهرية</button><button class="balanceLaunch" onclick="goPage('balanceSheet')">▤ الميزانية العمومية</button></div>'''
if old_quick not in s:
    raise SystemExit('Home quick actions not found')
s = s.replace(old_quick, new_quick, 1)

anchor = '''  <section id="monthly" class="page">'''
page = '''  <section id="balanceSheet" class="page"><div class="sectionTitle"><h2>الميزانية العمومية</h2><button class="pill" onclick="goPage('home')">رجوع</button></div><div class="bsTop"><button onclick="shiftMonth(-1)" aria-label="الشهر السابق">›</button><button id="bsMonthLabel" class="bsMonth" onclick="chooseMonth()">الشهر</button><button onclick="shiftMonth(1)" aria-label="الشهر التالي">‹</button></div><div class="card bsGrand"><div class="head"><div><h2>الإجمالي الكلي</h2><div class="small">جميع المحافظ للشهر المحدد</div></div></div><div id="bsGrandSummary" class="bsSummary"></div><div id="bsGrandBalance" class="bsBalanceLine"></div><div class="bsNote">التحويلات بين المحافظ لا تُحسب كإيراد أو مصروف حتى لا تتكرر المبالغ، لكنها تدخل ضمن الرصيد الفعلي لكل محفظة.</div></div><div id="bsWallets"></div></section>\n\n'''
if anchor not in s:
    raise SystemExit('Monthly section anchor not found')
s = s.replace(anchor, page + anchor, 1)

s = s.replace(
    'function renderAll(){renderHome();renderWallets();renderTransactions();renderRates();renderMonthly();renderSettings()}',
    'function renderAll(){renderHome();renderWallets();renderTransactions();renderBalanceSheet();renderRates();renderMonthly();renderSettings()}',
    1,
)

insert_before = 'function renderRates(){'
functions = r'''function bsMonthTx(){const m=state.selectedMonth||today().slice(0,7);return state.transactions.filter(t=>(t.date||'').slice(0,7)===m)}
function bsWalletData(wid){const arr=bsMonthTx();let income=0,expense=0;const cats={income:{},expense:{}};for(const t of arr){if(t.walletId!==wid||(t.type!=='income'&&t.type!=='expense'))continue;const v=eqBase(t);if(t.type==='income')income+=v;else expense+=v;const cid=t.categoryId||'_none';if(!cats[t.type][cid])cats[t.type][cid]=0;cats[t.type][cid]+=v}return{income,expense,net:income-expense,cats,balance:walletBalances(wid)}}
function bsCatRows(map,type){const rows=Object.entries(map).sort((a,b)=>b[1]-a[1]);if(!rows.length)return '<div class="bsEmpty">لا توجد '+(type==='income'?'واردات':'صرفيات')+' في هذا الشهر</div>';return rows.map(([cid,val])=>{const c=cid==='_none'?{name:'بدون تقسيم',emoji:'📌'}:category(cid);return `<div class="bsRow"><span class="name">${c.emoji||'📌'} ${esc(c.name)}</span><span class="amt">${baseMoney(val)}</span></div>`}).join('')}
function renderBalanceSheet(){const month=state.selectedMonth||today().slice(0,7),label=document.getElementById('bsMonthLabel');if(!label)return;label.textContent=monthName(month);let grandIncome=0,grandExpense=0;const cards=[];for(const w of state.wallets){const d=bsWalletData(w.id);grandIncome+=d.income;grandExpense+=d.expense;cards.push(`<div class="card bsWallet"><div class="bsWalletHead"><div class="bsWalletTitle"><strong>${w.emoji||'💼'} ${esc(w.name)}</strong><span>${w.main?'المحفظة الرئيسية':''}</span></div><div class="bsWalletSummary"><div class="bsMini income"><small>إجمالي الواردات</small><b>${baseMoney(d.income)}</b></div><div class="bsMini expense"><small>إجمالي الصرفيات</small><b>${baseMoney(d.expense)}</b></div><div class="bsMini net"><small>صافي الشهر</small><b>${baseMoney(d.net)}</b></div><div class="bsMini"><small>الرصيد الفعلي</small><b>${baseMoney(d.balance.equivalent)}</b></div></div><div class="bsBalanceLine"><span>الرصيد الأصلي حتى ${fmtDate(selectedCutoff())}</span><b>${money(d.balance.iqd,'IQD')} • ${money(d.balance.usd,'USD')}</b></div></div><div class="bsBody"><div class="bsCols"><div class="bsGroup"><div class="bsGroupHead"><span>تفاصيل الواردات</span><span>${baseMoney(d.income)}</span></div><div class="bsRows">${bsCatRows(d.cats.income,'income')}</div></div><div class="bsGroup"><div class="bsGroupHead"><span>تفاصيل الصرفيات</span><span>${baseMoney(d.expense)}</span></div><div class="bsRows">${bsCatRows(d.cats.expense,'expense')}</div></div></div></div></div>`)}const grandNet=grandIncome-grandExpense,gb=generalBalances();document.getElementById('bsGrandSummary').innerHTML=`<div class="bsStat income"><small>إجمالي الواردات</small><b>${baseMoney(grandIncome)}</b></div><div class="bsStat expense"><small>إجمالي الصرفيات</small><b>${baseMoney(grandExpense)}</b></div><div class="bsStat net"><small>الصافي الكلي</small><b>${baseMoney(grandNet)}</b></div><div class="bsStat"><small>إجمالي أرصدة المحافظ</small><b>${baseMoney(gb.equivalent)}</b></div>`;document.getElementById('bsGrandBalance').innerHTML=`<span>الرصيد الكلي الأصلي حتى ${fmtDate(selectedCutoff())}</span><b>${money(gb.iqd,'IQD')} • ${money(gb.usd,'USD')}</b>`;document.getElementById('bsWallets').innerHTML=cards.join('')||'<div class="card empty">لا توجد محافظ.</div>'}
'''
if insert_before not in s:
    raise SystemExit('renderRates anchor not found')
s = s.replace(insert_before, functions + insert_before, 1)

s = s.replace(
    "if(p==='monthly')renderMonthly();window.scrollTo(0,0)",
    "if(p==='monthly')renderMonthly();if(p==='balanceSheet')renderBalanceSheet();window.scrollTo(0,0)",
    1,
)

required = ['balanceSheet','renderBalanceSheet','bsGrandSummary','إجمالي الواردات','إجمالي الصرفيات','الصافي الكلي']
missing=[x for x in required if x not in s]
if missing: raise SystemExit('Balance sheet validation failed: '+', '.join(missing))
p.write_text(s, encoding='utf-8')
print('Balance sheet patch applied')
