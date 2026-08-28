from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

css = '''
#categoryManagerModal{z-index:90}
#actionModal{z-index:120}
#toast{z-index:140}
.manageSelectionBar{display:none;position:fixed;z-index:115;left:50%;transform:translateX(-50%);bottom:calc(16px + env(safe-area-inset-bottom));width:min(calc(100% - 28px),792px);background:var(--card);border:1px solid rgba(217,75,83,.35);box-shadow:0 12px 32px rgba(0,0,0,.22);border-radius:16px;padding:9px 10px;align-items:center;justify-content:space-between;gap:10px}
.manageSelectionBar.show{display:flex}
.manageSelectionBar span{font-size:12px;font-weight:bold;color:var(--text)}
.manageSelectionBar button{border:0;background:var(--out);color:#fff;border-radius:12px;padding:11px 14px;font-weight:bold;min-height:44px}
#categoryManagerModal .sheet{padding-bottom:90px}
'''
if '#categoryManagerModal{z-index:90}' not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

old_html = '<div id="categoryManagerList" class="manageList"></div><button class="manageDanger" onclick="deleteSelectedCategories()">حذف التقسيمات المحددة</button><div id="archivedCategories" class="archiveBox"></div>'
new_html = '<div id="categoryManagerList" class="manageList"></div><div id="manageSelectionBar" class="manageSelectionBar"><span id="manageSelectionCount">0 محدد</span><button type="button" onclick="deleteSelectedCategories()">حذف المحدد</button></div><div id="archivedCategories" class="archiveBox"></div>'
if old_html in s:
    s = s.replace(old_html, new_html, 1)

rename_func = '''function renameCategory(id){const c=state.categories.find(x=>x.id===id);if(!c)return;const oldWalletId=c.walletId,walletOptions=state.wallets.map(w=>({value:w.id,label:w.emoji+' '+w.name}));openActionModal('تعديل التقسيم',[{id:'name',label:'اسم التقسيم',type:'text',value:c.name},{id:'emoji',label:'الرمز',type:'text',value:c.emoji},{id:'walletId',label:'المحفظة التابعة لها',type:'select',value:c.walletId,options:walletOptions}],v=>{const name=(v.name||'').trim(),emoji=(v.emoji||'📌').trim()||'📌',newWalletId=v.walletId;if(!name){toast('اكتب اسم التقسيم');return false}if(!state.wallets.some(w=>w.id===newWalletId)){toast('اختر محفظة صحيحة');return false}const applyChanges=()=>{const moved=newWalletId!==oldWalletId;c.name=name;c.emoji=emoji;c.walletId=newWalletId;if(moved){for(const mt of (state.monthlyTemplates||[])){if(mt.categoryId===id&&mt.type===c.type)mt.walletId=newWalletId}}persist();renderAll();if(document.getElementById('categoryManagerModal').classList.contains('show'))renderCategoryManager();toast(moved?'تم نقل التقسيم وحفظ التعديل':'تم تعديل التقسيم')};if(newWalletId!==oldWalletId){const oldW=wallet(oldWalletId),newW=wallet(newWalletId),oldTx=state.transactions.filter(t=>t.categoryId===id).length,monthly=(state.monthlyTemplates||[]).filter(t=>t.categoryId===id).length;let msg=`سيتم نقل التقسيم «${name}» من ${oldW.name} إلى ${newW.name}.`;msg+=`\\n\\nالحركات القديمة (${oldTx}) ستبقى مرتبطة بمحافظها الأصلية ولن تتغير.`;if(monthly)msg+=`\\nوسيتم نقل ${monthly} بند شهري مرتبط بهذا التقسيم إلى المحفظة الجديدة.`;msg+='\\n\\nهل تريد متابعة النقل؟';confirmAction('تأكيد نقل التقسيم',msg,applyChanges,'نقل التقسيم');return false}applyChanges();return true},{onDelete:()=>{const txCount=state.transactions.filter(t=>t.categoryId===id).length,monthlyCount=(state.monthlyTemplates||[]).filter(t=>t.categoryId===id).length;if(monthlyCount){openActionModal('لا يمكن حذف التقسيم',[],null,{message:`هذا التقسيم مرتبط بـ ${monthlyCount} بند شهري.\\n\\nعدّل أو احذف البند الشهري المرتبط به أولًا حتى لا تتعطل قائمتك الشهرية.`,hideSubmit:true});return false}if(txCount){confirmAction('إخفاء التقسيم من الاستخدام',`هذا التقسيم مستخدم في ${txCount} حركة قديمة.\\n\\nلن نحذف السجل التاريخي؛ سيتم إخفاء التقسيم من الاستخدام الجديد فقط.`,()=>{c.archived=true;persist();renderAll();if(document.getElementById('categoryManagerModal').classList.contains('show'))renderCategoryManager();toast('تم إخفاء التقسيم من الاستخدام')},'إخفاء التقسيم');return false}confirmAction('حذف التقسيم',`سيتم حذف التقسيم «${c.name}» نهائيًا لأنه غير مستخدم في أي حركة أو بند شهري.\\n\\nهل أنت متأكد؟`,()=>{state.categories=state.categories.filter(x=>x.id!==id);persist();renderAll();if(document.getElementById('categoryManagerModal').classList.contains('show'))renderCategoryManager();toast('تم حذف التقسيم')},'حذف التقسيم');return false},deleteText:'حذف التقسيم'})}
function deleteCategory'''
s, n = re.subn(r"function renameCategory\(id\)\{.*?\}\nfunction deleteCategory", lambda m: rename_func, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Could not patch renameCategory')

s = s.replace(
    "function closeCategoryManager(){document.getElementById('categoryManagerModal').classList.remove('show')}",
    "function closeCategoryManager(){document.getElementById('categoryManagerModal').classList.remove('show');const bar=document.getElementById('manageSelectionBar');if(bar)bar.classList.remove('show')}"
)

manager_func = '''function renderCategoryManager(){const list=document.getElementById('categoryManagerList'),arch=document.getElementById('archivedCategories');const active=state.categories.filter(c=>c.walletId===activeWalletId&&!c.archived);list.innerHTML=active.map(c=>`<label class="manageCatRow"><input class="managedCatCheck" type="checkbox" value="${c.id}" onchange="updateManagedSelection()"><div class="manageCatMain"><div class="manageCatEmoji">${c.emoji}</div><div><b>${esc(c.name)}</b><small>${c.type==='expense'?'مصروف':'إيراد'}</small></div></div><button type="button" class="manageEdit" onclick="event.preventDefault();event.stopPropagation();renameCategory('${c.id}')">تعديل</button></label>`).join('')||'<div class="empty">لا توجد تقسيمات فعالة.</div>';const old=state.categories.filter(c=>c.walletId===activeWalletId&&c.archived);arch.innerHTML=old.length?`<div class="head"><div><h2>تقسيمات محذوفة من الاستخدام</h2><div class="small">تبقى محفوظة فقط للحركات القديمة.</div></div></div>`+old.map(c=>`<div class="archiveRow"><span>${c.emoji} ${esc(c.name)}</span><button onclick="restoreCategory('${c.id}')">استرجاع</button></div>`).join(''):'';updateManagedSelection()}
function updateManagedSelection(){const checks=[...document.querySelectorAll('.managedCatCheck:checked')],bar=document.getElementById('manageSelectionBar'),count=document.getElementById('manageSelectionCount');if(count)count.textContent=checks.length+' محدد';if(bar)bar.classList.toggle('show',checks.length>0)}
function selectAllManagedCategories(on){document.querySelectorAll('.managedCatCheck').forEach(x=>x.checked=!!on);updateManagedSelection()}
function deleteSelectedCategories'''
s, n = re.subn(r"function renderCategoryManager\(\)\{.*?\}\nfunction selectAllManagedCategories\(on\)\{.*?\}\nfunction deleteSelectedCategories", lambda m: manager_func, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Could not patch category manager rendering')

bulk_func = '''function deleteSelectedCategories(){const ids=[...document.querySelectorAll('.managedCatCheck:checked')].map(x=>x.value);if(!ids.length){toast('حدد تقسيمًا واحدًا على الأقل');return}const blocked=ids.filter(id=>(state.monthlyTemplates||[]).some(t=>t.categoryId===id)),archivable=ids.filter(id=>!blocked.includes(id)&&state.transactions.some(t=>t.categoryId===id)),removable=ids.filter(id=>!blocked.includes(id)&&!state.transactions.some(t=>t.categoryId===id));let msg=`أنت محدد ${ids.length} تقسيم.`;if(removable.length)msg+=`\\n• ${removable.length} سيتم حذفها نهائيًا.`;if(archivable.length)msg+=`\\n• ${archivable.length} مستخدمة بحركات قديمة وسيتم إخفاؤها فقط مع بقاء السجل.`;if(blocked.length)msg+=`\\n• ${blocked.length} مرتبطة ببنود شهرية ولن يتم حذفها حتى تعدّل تلك البنود.`;msg+='\\n\\nهل تريد تنفيذ الممكن الآن؟';confirmAction('تأكيد حذف التقسيمات',msg,()=>{let archived=0,deleted=0;for(const id of archivable){const c=state.categories.find(x=>x.id===id);if(c){c.archived=true;archived++}}if(removable.length){state.categories=state.categories.filter(c=>!removable.includes(c.id));deleted=removable.length}persist();renderAll();renderCategoryManager();toast(`تم حذف ${deleted} وإخفاء ${archived}${blocked.length?' • تعذر '+blocked.length:''}`)},'تنفيذ الحذف')}
function restoreCategory'''
s, n = re.subn(r"function deleteSelectedCategories\(\)\{.*?\}\nfunction restoreCategory", lambda m: bulk_func, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Could not patch bulk category deletion')

required = [
    '#actionModal{z-index:120}',
    'manageSelectionBar',
    'updateManagedSelection',
    'تأكيد نقل التقسيم',
    'mt.walletId=newWalletId',
    'تأكيد حذف التقسيمات',
]
missing = [x for x in required if x not in s]
if missing:
    raise SystemExit('Category manager patch validation failed: ' + ', '.join(missing))

p.write_text(s, encoding='utf-8')
print('Category manager patch applied')
