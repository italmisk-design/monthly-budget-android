(function(){
'use strict';

function applyPrimaryWalletHierarchy(){
  if(typeof state==='undefined'||!Array.isArray(state.wallets)) return;

  function ensurePrimaryWalletModel(){
    if(!state.wallets.length) return null;
    let main=state.wallets.find(w=>w.main)||state.wallets[0];
    let changed=false;
    state.wallets.forEach(w=>{const v=w.id===main.id;if(w.main!==v){w.main=v;changed=true}});
    if(main.name!=='المحفظة الرئيسية'){main.name='المحفظة الرئيسية';changed=true}
    if(!main.emoji){main.emoji='💰';changed=true}
    if(state.wallets[0].id!==main.id){state.wallets=[main,...state.wallets.filter(w=>w.id!==main.id)];changed=true}
    if(changed&&typeof persist==='function') persist();
    return main;
  }

  function primaryWallet(){return ensurePrimaryWalletModel()}
  window.primaryWallet=primaryWallet;


  const heroLabel=document.querySelector('#home .hero small');
  if(heroLabel) heroLabel.textContent='المحفظة الرئيسية • إجمالي جميع المحافظ';
  const homeWalletCard=document.getElementById('homeWallets')?.closest('.card');
  if(homeWalletCard){const h=homeWalletCard.querySelector('.head h2');if(h)h.textContent='المحافظ الفرعية'}
  const walletList=document.getElementById('walletList');
  if(walletList&&!walletList.previousElementSibling?.classList.contains('subWalletTitle')){
    const title=document.createElement('div');title.className='subWalletTitle';title.textContent='المحافظ الفرعية';walletList.before(title);
  }
  const bsHead=document.querySelector('#balanceSheet .bsGrand .head h2');if(bsHead)bsHead.textContent='المحفظة الرئيسية';
  const bsSub=document.querySelector('#balanceSheet .bsGrand .head .small');if(bsSub)bsSub.textContent='ملخص المحفظة الرئيسية وجميع المحافظ الفرعية للشهر المحدد';
  const bsNote=document.querySelector('#balanceSheet .bsNote');if(bsNote)bsNote.textContent='المحفظة الرئيسية تجمع واردات ومصروفات جميع المحافظ. التحويلات بين المحافظ توزيع داخلي، لذلك لا تُحسب كوارد أو مصروف، لكنها تظهر بالتفصيل وتؤثر على رصيد كل محفظة.';
  document.querySelectorAll('#settings .settingrow').forEach(row=>{const b=row.querySelector('b'),sm=row.querySelector('small');if(b&&b.textContent.includes('العملة الأساسية'))b.textContent='العملة الأساسية للمحفظة الرئيسية';if(sm&&sm.textContent.includes('الإجماليات'))sm.textContent='تغيّر طريقة عرض إجماليات المحفظة الرئيسية فقط ولا تغيّر عملة الحركات الأصلية'});

  const oldRenderHome=renderHome;
  renderHome=function(){
    ensurePrimaryWalletModel();
    oldRenderHome();
    const label=document.querySelector('#home .hero small');if(label)label.textContent='المحفظة الرئيسية • إجمالي جميع المحافظ';
    const box=document.getElementById('homeWallets');if(box)box.innerHTML=state.wallets.filter(w=>!w.main).slice(0,4).map(walletHtml).join('')||'<div class="empty">لا توجد محافظ فرعية.</div>';
  };

  window.openPrimaryTransfer=function(){
    const main=primaryWallet();openTx('transfer');if(!main)return;
    const from=document.getElementById('fromWallet'),to=document.getElementById('toWallet');
    if(from)from.value=main.id;
    if(to&&to.value===main.id){const child=state.wallets.find(w=>!w.main);if(child)to.value=child.id}
  };

  renderWallets=function(){
    const main=primaryWallet(),g=generalBalances(),mt=monthTotals(),direct=main?walletBalances(main.id):{iqd:0,usd:0,equivalent:0};
    const box=document.getElementById('generalWalletCard');
    if(main&&box)box.innerHTML=`<div class="primaryWalletCard"><div class="primaryWalletHead"><div class="primaryWalletName"><div class="primaryWalletIcon">${main.emoji||'💰'}</div><div><b>المحفظة الرئيسية</b><small>الحساب الأساسي • يشمل إجمالي جميع المحافظ</small></div></div><button class="primaryOpen" onclick="openWallet('${main.id}')">التفاصيل</button></div><div class="primaryTotal">${baseMoney(g.equivalent)}</div><div class="primaryStats"><div class="primaryStat"><small>إجمالي الواردات</small><b>${baseMoney(mt.income)}</b></div><div class="primaryStat"><small>إجمالي المصروفات</small><b>${baseMoney(mt.expense)}</b></div><div class="primaryStat"><small>الرصيد المباشر</small><b>${baseMoney(direct.equivalent)}</b></div></div><div class="primaryDirect"><span>الرصيد الموجود مباشرة في الرئيسية</span><b>${money(direct.iqd,'IQD')} • ${money(direct.usd,'USD')}</b></div><div class="primaryActions"><button class="pin" onclick="openTxForWallet('income','${main.id}')">+ وارد مباشر</button><button class="pout" onclick="openTxForWallet('expense','${main.id}')">− مصروف مباشر</button><button class="ptr" onclick="openPrimaryTransfer()">⇄ تحويل</button></div></div>`;
    if(walletList)walletList.innerHTML=state.wallets.filter(w=>!w.main).map(walletHtml).join('')||'<div class="empty">لا توجد محافظ فرعية.</div>';
    if(activeWalletId)renderWalletDetail();
  };

  const oldRenderWalletDetail=renderWalletDetail;
  renderWalletDetail=function(){
    const main=primaryWallet();
    if(!main||activeWalletId!==main.id){oldRenderWalletDetail();if(activeWalletId){const el=document.getElementById('wdMain');if(el)el.textContent='محفظة فرعية'}return}
    oldRenderWalletDetail();
    const b=walletBalances(main.id),g=generalBalances(),mt=monthTotals();
    const label=document.getElementById('wdMain');if(label)label.textContent='المحفظة الرئيسية • الحساب الأساسي وجميع المحافظ الفرعية';
    const balance=document.getElementById('wdBalance');if(balance)balance.innerHTML=`<div class="primaryDetailSummary"><div class="primaryDetailBox total"><small>إجمالي الرصيد بكل المحافظ</small><b>${baseMoney(g.equivalent)}</b></div><div class="primaryDetailBox"><small>الرصيد المباشر في الرئيسية</small><b>${baseMoney(b.equivalent)}</b></div><div class="primaryDetailBox"><small>إجمالي واردات الشهر</small><b>${baseMoney(mt.income)}</b></div><div class="primaryDetailBox"><small>إجمالي مصروفات الشهر</small><b>${baseMoney(mt.expense)}</b></div></div><div class="primaryDetailNote">المصروف أو الوارد المسجل مباشرة هنا يغيّر رصيد الرئيسية. ومصاريف وواردات المحافظ الفرعية تدخل أيضًا ضمن إجماليات الرئيسية. التحويل بين المحافظ توزيع داخلي وليس مصروفًا أو واردًا.</div><div class="walletAmount"><span>${money(b.iqd,'IQD')}</span><span>${money(b.usd,'USD')}</span><span>الرصيد المباشر</span></div>`;
    const tx=document.getElementById('wdTx');if(tx)tx.innerHTML=sortedTx().map(txHtml).join('')||'<div class="empty">لا توجد حركات في '+monthName(state.selectedMonth)+'</div>';
  };

  const oldWalletActions=walletActions;
  walletActions=function(){
    const w=state.wallets.find(x=>x.id===activeWalletId);
    if(!w||!w.main)return oldWalletActions();
    openActionModal('إعدادات المحفظة الرئيسية',[{id:'emoji',label:'الرمز',type:'text',value:w.emoji},{id:'openingIQD',label:'الرصيد الافتتاحي IQD',type:'number',value:w.openingIQD||0,inputmode:'decimal'},{id:'openingUSD',label:'الرصيد الافتتاحي USD',type:'number',value:w.openingUSD||0,inputmode:'decimal'}],v=>{w.name='المحفظة الرئيسية';w.emoji=(v.emoji||'💰').trim()||'💰';w.openingIQD=nval(v.openingIQD);w.openingUSD=nval(v.openingUSD);persist();renderAll();toast('تم حفظ إعدادات المحفظة الرئيسية');return true},{message:'هذه هي المحفظة الرئيسية الحقيقية: تستطيع تسجيل واردات ومصروفات مباشرة عليها والتحويل منها وإليها. وفي نفس الوقت تجمع أرقام جميع المحافظ الفرعية، ولا يمكن حذفها.'});
  };

  const oldTxMatchesWallet=txMatchesWallet;
  txMatchesWallet=function(t,wid){const main=primaryWallet();if(main&&wid===main.id)return true;return oldTxMatchesWallet(t,wid)};
  const oldRenderTransactions=renderTransactions;
  renderTransactions=function(){
    oldRenderTransactions();
    const main=primaryWallet(),sel=document.getElementById('txWalletFilter');
    if(sel&&main){const op=[...sel.options].find(o=>o.value===main.id);if(op)op.textContent=`${main.emoji} المحفظة الرئيسية (إجمالي)`}
    if(!main||txWalletFilter!==main.id)return;
    const arr=filteredTransactions();let income=0,expense=0,transfers=0;
    arr.forEach(t=>{if(t.type==='income')income+=eqBase(t);else if(t.type==='expense')expense+=eqBase(t);else if(t.type==='transfer')transfers+=eqBase(t)});
    const summary=document.getElementById('txFilterSummary');if(summary)summary.innerHTML=`<div class="txSummaryStat expense"><small>مصروفات الرئيسية</small><b>${baseMoney(expense)}</b></div><div class="txSummaryStat income"><small>واردات الرئيسية</small><b>${baseMoney(income)}</b></div><div class="txSummaryStat transfer"><small>التحويلات الداخلية</small><b>${baseMoney(transfers)}</b></div><div class="txSummaryStat"><small>عدد الحركات</small><b>${arr.length}</b></div>`;
  };

  const oldRenderBalanceSheet=renderBalanceSheet;
  renderBalanceSheet=function(){
    ensurePrimaryWalletModel();oldRenderBalanceSheet();
    const main=primaryWallet();
    const h=document.querySelector('#balanceSheet .bsGrand .head h2');if(h)h.textContent='المحفظة الرئيسية';
    const sm=document.querySelector('#balanceSheet .bsGrand .head .small');if(sm)sm.textContent='ملخص المحفظة الرئيسية وجميع المحافظ الفرعية للشهر المحدد';
    const note=document.querySelector('#balanceSheet .bsNote');if(note)note.textContent='المحفظة الرئيسية تجمع واردات ومصروفات جميع المحافظ. التحويلات بين المحافظ توزيع داخلي، لذلك لا تُحسب كوارد أو مصروف، لكنها تظهر بالتفصيل وتؤثر على رصيد كل محفظة.';
    const cards=[...document.querySelectorAll('#bsWallets .bsWallet')];
    if(main&&cards.length){const first=cards[0],strong=first.querySelector('.bsWalletTitle strong'),tag=first.querySelector('.bsWalletTitle span');first.classList.add('bsDirectMain');if(strong)strong.textContent=`${main.emoji||'💰'} المحفظة الرئيسية — حركات مباشرة`;if(tag)tag.textContent='هذا القسم مباشر فقط';const lbl=document.createElement('div');lbl.className='bsSectionLabel';lbl.textContent='الحركات المباشرة في المحفظة الرئيسية';first.before(lbl);if(cards.length>1){const lbl2=document.createElement('div');lbl2.className='bsSectionLabel';lbl2.textContent='تفاصيل المحافظ الفرعية';cards[1].before(lbl2)}}
    document.querySelectorAll('#bsWallets .bsWallet').forEach((card,i)=>{if(i>0){const tag=card.querySelector('.bsWalletTitle span');if(tag)tag.textContent='محفظة فرعية'}});
  };

  const oldRenderAll=renderAll;
  renderAll=function(){ensurePrimaryWalletModel();oldRenderAll()};
  ensurePrimaryWalletModel();
  renderAll();
}

window.addEventListener('load',applyPrimaryWalletHierarchy,{once:true});
})();
