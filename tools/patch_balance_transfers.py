from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

css = r'''
.bsTransfers{margin-top:10px;border:1px solid rgba(71,104,216,.22);border-radius:14px;overflow:hidden}.bsTransfersHead{display:flex;justify-content:space-between;gap:8px;padding:9px 10px;background:rgba(71,104,216,.07);font-size:11px;font-weight:bold}.bsTransferRow{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;padding:9px 10px;border-bottom:1px solid var(--line);font-size:10px}.bsTransferRow:last-child{border-bottom:0}.bsTransferMain{min-width:0}.bsTransferMain b{display:block;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.bsTransferMain small{display:block;color:var(--muted);margin-top:3px;line-height:1.5}.bsTransferAmt{direction:ltr;font-weight:bold;white-space:nowrap}.bsTransferAmt.in{color:var(--tr)}.bsTransferAmt.out{color:var(--out)}
'''
if '.bsTransfers{' not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

pattern_data = r"function bsWalletData\(wid\)\{.*?\}\nfunction bsCatRows"
replacement_data = r'''function bsWalletData(wid){const arr=bsMonthTx();let income=0,expense=0,transferIn=0,transferOut=0;const cats={income:{},expense:{}},transfers=[];for(const t of arr){if(t.type==='transfer'&&(t.fromWalletId===wid||t.toWalletId===wid)){const incoming=t.toWalletId===wid,v=eqBase(t);if(incoming)transferIn+=v;else transferOut+=v;transfers.push({tx:t,incoming,value:v});continue}if(t.walletId!==wid||(t.type!=='income'&&t.type!=='expense'))continue;const v=eqBase(t);if(t.type==='income')income+=v;else expense+=v;const cid=t.categoryId||'_none';if(!cats[t.type][cid])cats[t.type][cid]=0;cats[t.type][cid]+=v}transfers.sort((a,b)=>(b.tx.date||'').localeCompare(a.tx.date||'')||((b.tx.created||0)-(a.tx.created||0)));return{income,expense,net:income-expense,cats,balance:walletBalances(wid),transferIn,transferOut,transfers}}
function bsCatRows'''
s2,n = re.subn(pattern_data, lambda m: replacement_data, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('bsWalletData replacement failed')
s = s2

anchor = "function renderBalanceSheet(){"
helper = r'''function bsTransferRows(d,wid){if(!d.transfers.length)return '<div class="bsEmpty">لا توجد تحويلات لهذه المحفظة في هذا الشهر</div>';return d.transfers.map(x=>{const t=x.tx,otherId=x.incoming?t.fromWalletId:t.toWalletId,other=state.wallets.find(w=>w.id===otherId),direction=x.incoming?'تحويل داخل من':'تحويل خارج إلى',cls=x.incoming?'in':'out',sign=x.incoming?'+':'−',note=t.note?` • ${esc(t.note)}`:'';return `<div class="bsTransferRow"><div class="bsTransferMain"><b>${x.incoming?'↙':'↗'} ${direction} ${esc(other?other.name:'محفظة غير موجودة')}</b><small>${fmtDate(t.date)}${note}</small></div><span class="bsTransferAmt ${cls}">${sign} ${money(t.amount,t.currency)}</span></div>`}).join('')}
'''
if 'function bsTransferRows(' not in s:
    if anchor not in s:
        raise SystemExit('renderBalanceSheet anchor missing')
    s = s.replace(anchor, helper + anchor, 1)

pattern_render = r"function renderBalanceSheet\(\)\{.*?\}\nfunction renderRates\(\)\{"
replacement_render = r'''function renderBalanceSheet(){const month=state.selectedMonth||today().slice(0,7),label=document.getElementById('bsMonthLabel');if(!label)return;label.textContent=monthName(month);let grandIncome=0,grandExpense=0,totalTransfer=0;const cards=[];for(const w of state.wallets){const d=bsWalletData(w.id);grandIncome+=d.income;grandExpense+=d.expense;totalTransfer+=d.transferOut;cards.push(`<div class="card bsWallet"><div class="bsWalletHead"><div class="bsWalletTitle"><strong>${w.emoji||'💼'} ${esc(w.name)}</strong><span>${w.main?'المحفظة العامة':''}</span></div><div class="bsWalletSummary"><div class="bsMini income"><small>إجمالي الواردات</small><b>${baseMoney(d.income)}</b></div><div class="bsMini expense"><small>إجمالي الصرفيات</small><b>${baseMoney(d.expense)}</b></div><div class="bsMini net"><small>صافي الشهر</small><b>${baseMoney(d.net)}</b></div><div class="bsMini"><small>الرصيد الفعلي</small><b>${baseMoney(d.balance.equivalent)}</b></div></div><div class="bsBalanceLine"><span>الرصيد الأصلي حتى ${fmtDate(selectedCutoff())}</span><b>${money(d.balance.iqd,'IQD')} • ${money(d.balance.usd,'USD')}</b></div></div><div class="bsBody"><div class="bsCols"><div class="bsGroup"><div class="bsGroupHead"><span>تفاصيل الواردات</span><span>${baseMoney(d.income)}</span></div><div class="bsRows">${bsCatRows(d.cats.income,'income')}</div></div><div class="bsGroup"><div class="bsGroupHead"><span>تفاصيل الصرفيات</span><span>${baseMoney(d.expense)}</span></div><div class="bsRows">${bsCatRows(d.cats.expense,'expense')}</div></div></div><div class="bsTransfers"><div class="bsTransfersHead"><span>تفاصيل التحويلات</span><span>داخل ${baseMoney(d.transferIn)} • خارج ${baseMoney(d.transferOut)}</span></div>${bsTransferRows(d,w.id)}</div></div></div>`)}const grandNet=grandIncome-grandExpense,gb=generalBalances();document.getElementById('bsGrandSummary').innerHTML=`<div class="bsStat income"><small>إجمالي الواردات</small><b>${baseMoney(grandIncome)}</b></div><div class="bsStat expense"><small>إجمالي الصرفيات</small><b>${baseMoney(grandExpense)}</b></div><div class="bsStat net"><small>الصافي الكلي</small><b>${baseMoney(grandNet)}</b></div><div class="bsStat"><small>إجمالي أرصدة المحافظ</small><b>${baseMoney(gb.equivalent)}</b></div><div class="bsStat"><small>التحويلات الداخلية</small><b>${baseMoney(totalTransfer)}</b></div>`;document.getElementById('bsGrandBalance').innerHTML=`<span>الرصيد الكلي الأصلي حتى ${fmtDate(selectedCutoff())}</span><b>${money(gb.iqd,'IQD')} • ${money(gb.usd,'USD')}</b>`;document.getElementById('bsWallets').innerHTML=cards.join('')||'<div class="card empty">لا توجد محافظ.</div>'}
function renderRates(){'''
s2,n = re.subn(pattern_render, lambda m: replacement_render, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('renderBalanceSheet replacement failed')
s = s2

s = s.replace('التحويلات بين المحافظ لا تُحسب كإيراد أو مصروف حتى لا تتكرر المبالغ، لكنها تدخل ضمن الرصيد الفعلي لكل محفظة.','التحويلات بين المحافظ لا تُحسب كإيراد أو مصروف حتى لا تتكرر المبالغ. تظهر أدناه كتحويلات داخلة وخارجة مع المصدر والوجهة والتاريخ، وتدخل ضمن الرصيد الفعلي لكل محفظة.')

required=['bsTransferRows','تفاصيل التحويلات','التحويلات الداخلية','transferIn','transferOut']
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit('transfer balance validation failed: '+', '.join(missing))

p.write_text(s, encoding='utf-8')
print('Balance sheet transfer details applied')
