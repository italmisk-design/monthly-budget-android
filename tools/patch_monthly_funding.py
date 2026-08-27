from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

pattern = r"function openMonthlyFinalReview\(date\)\{.*?\}\nfunction executeMonthlyRun\(date\)\{.*?\}\nfunction openTx"
replacement = r'''function openMonthlyFinalReview(date){const all=(state.monthlyTemplates||[]).filter(monthlyTemplateValid),month=date.slice(0,7),prev=(state.monthlyRuns||[]).filter(r=>(r.date||'').slice(0,7)===month),sum=monthlySummary(date,all),main=state.wallets.find(w=>w.main);const expenseTargets={};for(const t of all){if(t.type!=='expense'||!main||t.walletId===main.id)continue;const key=t.walletId+'|'+t.currency;expenseTargets[key]=(expenseTargets[key]||0)+(Number(t.amount)||0)}const fundingLines=Object.entries(expenseTargets).map(([key,amount])=>{const [wid,cur]=key.split('|'),w=state.wallets.find(x=>x.id===wid);return `${w?w.name:'محفظة'}: ${money(amount,cur)}`});let msg=`سيتم إنشاء ${all.length} حركة فعلية بتاريخ ${fmtDate(date)}.\nإجمالي الإيرادات: ${baseMoney(sum.income)}\nإجمالي المصروفات: ${baseMoney(sum.expense)}.`;if(fundingLines.length)msg+=`\n\nعند تفعيل تمويل المصروفات، سيتم التحويل من المحفظة الرئيسية قبل تسجيل المصروفات:\n${fundingLines.join('\n')}`;if(prev.length)msg=`تنبيه: سبق تنفيذ القائمة ${prev.length} مرة خلال ${monthName(month)}.\n\n`+msg;openActionModal('المراجعة النهائية',[{id:'fundExpenses',label:'نعم، موّل المصروفات أولًا من المحفظة الرئيسية إلى المحافظ الفرعية',type:'checkbox',value:false},{id:'confirmed',label:'راجعت الحركات وأنا متأكد وموافق على الإضافة',type:'checkbox',value:false,confirmGate:true}],v=>{if(!v.confirmed)return false;if(v.fundExpenses&&!main){toast('حدد محفظة رئيسية أولًا');return false}executeMonthlyRun(date,!!v.fundExpenses);return true},{message:msg,submitText:'إضافة الحركات'})}
function executeMonthlyRun(date,fundExpenses=false){const items=(state.monthlyTemplates||[]).filter(monthlyTemplateValid),batchId=uid(),main=state.wallets.find(w=>w.main);let fundingCount=0;if(fundExpenses&&main){const grouped={};for(const t of items){if(t.type!=='expense'||t.walletId===main.id)continue;const key=t.walletId+'|'+t.currency;if(!grouped[key])grouped[key]={walletId:t.walletId,currency:t.currency,amount:0};grouped[key].amount+=Number(t.amount)||0}for(const g of Object.values(grouped)){if(g.amount<=0)continue;state.transactions.push({id:uid(),created:Date.now(),type:'transfer',currency:g.currency,amount:g.amount,date,note:'تمويل المصروفات الشهرية',fromWalletId:main.id,toWalletId:g.walletId,monthlyBatchId:batchId,monthlyFunding:true});fundingCount++}}for(const t of items)state.transactions.push({id:uid(),created:Date.now(),type:t.type,currency:t.currency,amount:Number(t.amount)||0,date,note:t.note||'',walletId:t.walletId,categoryId:t.categoryId,monthlyTemplateId:t.id,monthlyBatchId:batchId});if(!Array.isArray(state.monthlyRuns))state.monthlyRuns=[];state.monthlyRuns.push({id:batchId,date,created:Date.now(),count:items.length,funded:!!fundExpenses,fundingTransfers:fundingCount});state.selectedMonth=date.slice(0,7);persist();renderAll();goPage('home');toast(fundingCount?`تمت إضافة ${items.length} حركة و${fundingCount} تحويل تمويل`:`تمت إضافة ${items.length} حركة شهرية بنجاح`)}
function openTx'''

s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Could not patch monthly funding functions')

required = ['fundExpenses', 'monthlyFunding:true', "t.type!=='expense'", 'fromWalletId:main.id', 'walletId:t.walletId']
missing = [x for x in required if x not in s2]
if missing:
    raise SystemExit('Funding patch validation failed: ' + ', '.join(missing))

p.write_text(s2, encoding='utf-8')
print('Monthly funding patch applied')
