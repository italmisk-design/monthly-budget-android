from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

s = re.sub(
    r"function openActionModal\(title,fields,onSubmit,opts=\{\}\)\{.*?\}\nfunction closeActionModal",
    """function openActionModal(title,fields,onSubmit,opts={}){actionHandler=onSubmit||null;actionDeleteHandler=opts.onDelete||null;document.getElementById('actionTitle').textContent=title;const box=document.getElementById('actionFields');box.innerHTML='';for(const f of (fields||[])){const wrap=document.createElement('div');wrap.className=f.type==='checkbox'?'field confirmCheck':'field';let el;if(f.type==='checkbox'){el=document.createElement('input');el.type='checkbox';el.checked=!!f.value;if(f.confirmGate)el.dataset.confirmGate='1';const text=document.createElement('span');text.textContent=f.label||'';wrap.appendChild(el);wrap.appendChild(text)}else{const lab=document.createElement('div');lab.className='label';lab.textContent=f.label||'';wrap.appendChild(lab);if(f.type==='select'){el=document.createElement('select');for(const o of (f.options||[])){const op=document.createElement('option');op.value=o.value;op.textContent=o.label;if(String(o.value)===String(f.value??''))op.selected=true;el.appendChild(op)}}else{el=document.createElement('input');el.type=f.type||'text';el.value=f.value??'';if(f.placeholder)el.placeholder=f.placeholder;if(f.inputmode)el.inputMode=f.inputmode;if(f.type==='number'){el.step=f.step||'any'}}wrap.appendChild(el)}el.dataset.actionField=f.id;box.appendChild(wrap)}const msg=document.getElementById('actionMessage');msg.textContent=opts.message||'';msg.style.display=opts.message?'block':'none';const save=document.getElementById('actionSave');save.textContent=opts.submitText||'حفظ';save.style.display=opts.hideSubmit?'none':'block';save.disabled=false;const gate=box.querySelector('input[type=checkbox][data-confirm-gate=\"1\"]');if(gate){save.disabled=!gate.checked;gate.addEventListener('change',()=>save.disabled=!gate.checked)}const del=document.getElementById('actionDelete');del.style.display=actionDeleteHandler?'block':'none';del.textContent=opts.deleteText||'حذف';document.getElementById('actionModal').classList.add('show');setTimeout(()=>{const first=box.querySelector('input:not([type=checkbox]),select');if(first)first.focus()},50)}\nfunction closeActionModal""",
    s,
    count=1,
    flags=re.S,
)

s = s.replace(
    "function actionValues(){const v={};document.querySelectorAll('#actionFields [data-action-field]').forEach(el=>v[el.dataset.actionField]=el.value);return v}",
    "function actionValues(){const v={};document.querySelectorAll('#actionFields [data-action-field]').forEach(el=>v[el.dataset.actionField]=el.type==='checkbox'?el.checked:el.value);return v}",
)

s = re.sub(
    r"function prepareMonthlyRun\(\)\{.*?\}\nfunction executeMonthlyRun\(date\)\{.*?\}\nfunction openTx",
    """function prepareMonthlyRun(){const all=(state.monthlyTemplates||[]),invalid=all.filter(t=>!monthlyTemplateValid(t));if(!all.length){toast('أضف بنودًا شهرية أولًا');return}if(invalid.length){openActionModal('توجد بنود تحتاج تعديل',[],null,{message:`عندك ${invalid.length} بند مرتبط بمحفظة أو تقسيم غير متاح. عدّل هذه البنود قبل التنفيذ.`,hideSubmit:true});return}openActionModal('إضافة الحركات الشهرية',[{id:'date',label:'تاريخ إضافة جميع الحركات',type:'date',value:today()}],v=>{const date=v.date||today();setTimeout(()=>openMonthlyFinalReview(date),0);return true},{message:'اختر التاريخ أولًا، وبعدها راح تشوف المراجعة النهائية.',submitText:'مراجعة الحركات'})}\nfunction openMonthlyFinalReview(date){const all=(state.monthlyTemplates||[]).filter(monthlyTemplateValid),month=date.slice(0,7),prev=(state.monthlyRuns||[]).filter(r=>(r.date||'').slice(0,7)===month),sum=monthlySummary(date,all);let msg=`سيتم إنشاء ${all.length} حركة فعلية بتاريخ ${fmtDate(date)}.\\nإجمالي الإيرادات: ${baseMoney(sum.income)}\\nإجمالي المصروفات: ${baseMoney(sum.expense)}.`;if(prev.length)msg=`تنبيه: سبق تنفيذ القائمة ${prev.length} مرة خلال ${monthName(month)}.\\n\\n`+msg;openActionModal('المراجعة النهائية',[{id:'confirmed',label:'راجعت الحركات وأنا متأكد وموافق على الإضافة',type:'checkbox',value:false,confirmGate:true}],v=>{if(!v.confirmed)return false;executeMonthlyRun(date);return true},{message:msg,submitText:'إضافة الحركات'})}\nfunction executeMonthlyRun(date){const items=(state.monthlyTemplates||[]).filter(monthlyTemplateValid),batchId=uid();for(const t of items)state.transactions.push({id:uid(),created:Date.now(),type:t.type,currency:t.currency,amount:Number(t.amount)||0,date,note:t.note||'',walletId:t.walletId,categoryId:t.categoryId,monthlyTemplateId:t.id,monthlyBatchId:batchId});if(!Array.isArray(state.monthlyRuns))state.monthlyRuns=[];state.monthlyRuns.push({id:batchId,date,created:Date.now(),count:items.length});state.selectedMonth=date.slice(0,7);persist();renderAll();goPage('home');toast(`تمت إضافة ${items.length} حركة شهرية بنجاح`)}\nfunction openTx""",
    s,
    count=1,
    flags=re.S,
)

needle = ".monthlyInvalid{opacity:.6}.monthlyInvalid .monthlyMain small:after{content:' • يحتاج تعديل';color:var(--out);font-weight:bold}"
if needle in s and '.confirmCheck{' not in s:
    s = s.replace(
        needle,
        needle + " .confirmCheck{display:flex;align-items:center;gap:10px;background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:12px;margin-top:12px;font-weight:bold;line-height:1.6}.confirmCheck input{width:22px;height:22px;flex:0 0 22px;accent-color:var(--p)}#actionSave:disabled{opacity:.45;cursor:not-allowed;filter:grayscale(.35)}",
    )

required = ["openMonthlyFinalReview", "confirmCheck", "el.type==='checkbox'", "goPage('home')"]
missing = [x for x in required if x not in s]
if missing:
    raise SystemExit('Patch validation failed: ' + ', '.join(missing))

p.write_text(s, encoding='utf-8')
print('Monthly confirmation patch applied')
