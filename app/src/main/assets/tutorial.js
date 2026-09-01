(function(){
'use strict';

const TUTORIAL_KEY='wafferli_tutorial_completed_v3';
let tutorialIndex=0;
let tutorialActive=false;
let tutorialOrigin='home';
let tutorialRoot=null;
let refreshTimer=null;

const tutorialSteps=[
  {
    title:'مرحبًا بك في وفرلي',
    text:'هذا تدريب سريع من 12 خطوة يعرّفك على أهم أجزاء التطبيق وطريقة تنظيم أموالك. لن نطلب منك إدخال أي بيانات أثناء الشرح.'
  },
  {
    page:'wallets',
    selector:'#generalWalletCard .primaryWalletCard',
    title:'ابدأ من الحساب الرئيسي',
    text:'المحفظة الرئيسية الظاهرة هنا هي حسابك الرئيسي ونقطة البداية. عند استلام راتبك أو أي دخل، أضف المبلغ كاملًا هنا أولًا، ثم وزّعه على المحافظ بحسب احتياجاتك.'
  },
  {
    page:'wallets',
    selector:'#walletList .wallet',
    fallback:'.subWalletTitle',
    title:'قسّم أموالك على المحافظ',
    text:'المحافظ هي التقسيمات التي توزّع عليها أموالك عادةً، مثل المنزل والسيارة والطعام والادخار. أنشئ ما يناسبك وعدّلها متى شئت.'
  },
  {
    page:'wallets',
    selector:'#generalWalletCard .ptr',
    title:'التحويل ليس مصروفًا',
    text:'عندما تنقل مبلغًا من الحساب الرئيسي إلى إحدى المحافظ، فأنت تعيد توزيع أموالك فقط. إجمالي أموالك لا ينقص بسبب التحويل.'
  },
  {
    page:'home',
    selector:'#home .q.out',
    title:'سجّل المصروف عند إنفاقه',
    text:'عندما تدفع مبلغًا فعليًا من إحدى المحافظ، سجّله من هنا كمصروف واختر المحفظة التي خرج منها المبلغ.'
  },
  {
    page:'monthly',
    selector:'#monthly .monthlyActions .normal',
    title:'أنشئ البنود الشهرية المتكررة',
    text:'الحركات الشهرية تسهّل عليك تسجيل البنود التي تتكرر كل شهر، مثل الراتب والإيجار والاشتراكات. عند الضغط على «إضافة بند» وحفظه، يُحفظ كقالب شهري فقط ولا يُضاف إلى كشف الحركات الفعلي.'
  },
  {
    page:'monthly',
    selector:'#monthly .monthlyActions .save',
    title:'أضف الحركات الشهرية عندما تريد',
    text:'لن تتحول البنود الشهرية إلى حركات فعلية إلا عندما تضغط «إضافة الحركات الآن». بعدها تختار التاريخ وتراجع البنود قبل إضافتها، حتى تنجز حركات الشهر بسرعة من دون إدخالها واحدةً واحدة.'
  },
  {
    page:'rates',
    selector:'#rateRows .normal',
    fallback:'#rates .sectionTitle .pill',
    title:'عدّل سعر الصرف من قسم الصرف',
    text:'من قسم «الصرف» يمكنك تعديل أي سعر مسجل بالضغط على «تعديل»، أو إضافة سعر جديد وتحديد تاريخ بدء العمل به. يستخدم وفرلي السعر المناسب بحسب تاريخ كل حركة.'
  },
  {
    page:'transactions',
    selector:'#transactions .txFilterCard',
    title:'كشف الحركات',
    text:'صفحة «الحركات» هي كشف حركاتك التفصيلي. تستطيع عرض المصروفات أو الإيرادات أو التحويلات، والتصفية حسب المحفظة والفترة أو تحديد نطاق زمني خاص.'
  },
  {
    page:'home',
    selector:'#home .balanceLaunch',
    title:'الكشف الكلي',
    text:'من هنا تفتح «الميزانية العمومية»، وهي الكشف الكلي لجميع المحافظ للشهر المحدد، لتراجع الإيرادات والمصروفات والتحويلات والأرصدة في مكان واحد.'
  },
  {
    page:'home',
    selector:'#home .hero',
    title:'تابع وضعك المالي بسرعة',
    text:'في الصفحة الرئيسية ترى إجمالي أموالك، ودخل الشهر، ومصروف الشهر، وسعر الصرف الساري وفق العملة الأساسية التي اخترتها.'
  },
  {
    page:'settings',
    selector:'#tutorialSettingsRow',
    title:'يمكنك العودة إلى التدريب',
    text:'إذا نسيت طريقة الاستخدام، افتح الإعدادات واختر «إعادة التدريب» لتشاهد هذا الشرح مرة أخرى في أي وقت.'
  }
];

function activePageId(){const p=document.querySelector('.page.active');return p?p.id:'home'}

function buildTutorialRoot(){
  if(tutorialRoot)return tutorialRoot;
  const root=document.createElement('div');
  root.id='wafferliTutorialRoot';
  root.className='tutorialRoot';
  root.innerHTML=`
    <div class="tutorialMask tutorialMaskTop"></div>
    <div class="tutorialMask tutorialMaskLeft"></div>
    <div class="tutorialMask tutorialMaskRight"></div>
    <div class="tutorialMask tutorialMaskBottom"></div>
    <div class="tutorialFocus"></div>
    <div class="tutorialCard" role="dialog" aria-modal="true" aria-labelledby="tutorialTitle">
      <div class="tutorialTopline"><h3 id="tutorialTitle" class="tutorialTitle"></h3><span class="tutorialCounter"></span></div>
      <p class="tutorialText"></p>
      <div class="tutorialProgress"><span></span></div>
      <div class="tutorialActions">
        <button type="button" class="tutorialPrev" onclick="wafferliTutorialPrevious()">السابق</button>
        <button type="button" class="tutorialNext" onclick="wafferliTutorialNext()">التالي</button>
        <button type="button" class="tutorialSkip" onclick="skipWafferliTutorial()">تخطي التدريب</button>
      </div>
    </div>`;
  document.body.appendChild(root);
  tutorialRoot=root;
  return root;
}

function masks(){return {
  top:tutorialRoot.querySelector('.tutorialMaskTop'),
  left:tutorialRoot.querySelector('.tutorialMaskLeft'),
  right:tutorialRoot.querySelector('.tutorialMaskRight'),
  bottom:tutorialRoot.querySelector('.tutorialMaskBottom'),
  focus:tutorialRoot.querySelector('.tutorialFocus')
}}

function setRect(el,l,t,w,h){el.style.left=l+'px';el.style.top=t+'px';el.style.width=Math.max(0,w)+'px';el.style.height=Math.max(0,h)+'px'}

function coverAll(){
  const m=masks(),vw=window.innerWidth,vh=window.innerHeight;
  setRect(m.top,0,0,vw,vh);setRect(m.left,0,0,0,0);setRect(m.right,0,0,0,0);setRect(m.bottom,0,0,0,0);
  m.focus.style.display='none';
}

function focusElement(target){
  if(!target){coverAll();return}
  const pad=8,vw=window.innerWidth,vh=window.innerHeight;
  const r=target.getBoundingClientRect();
  const left=Math.max(6,r.left-pad),top=Math.max(6,r.top-pad),right=Math.min(vw-6,r.right+pad),bottom=Math.min(vh-6,r.bottom+pad);
  const width=Math.max(0,right-left),height=Math.max(0,bottom-top),m=masks();
  setRect(m.top,0,0,vw,top);
  setRect(m.left,0,top,left,height);
  setRect(m.right,right,top,vw-right,height);
  setRect(m.bottom,0,bottom,vw,vh-bottom);
  m.focus.style.display='block';setRect(m.focus,left,top,width,height);
  const card=tutorialRoot.querySelector('.tutorialCard');
  card.classList.remove('welcome','atTop','atBottom');
  const center=top+height/2;
  card.classList.add(center<vh*.52?'atBottom':'atTop');
}

function resolveTarget(step){
  let target=step.selector?document.querySelector(step.selector):null;
  if(!target&&step.fallback)target=document.querySelector(step.fallback);
  return target;
}

function renderTutorialStep(){
  if(!tutorialActive)return;
  const step=tutorialSteps[tutorialIndex],root=buildTutorialRoot();
  root.style.display='block';
  if(step.page&&typeof goPage==='function')goPage(step.page);
  const card=root.querySelector('.tutorialCard');
  card.querySelector('.tutorialTitle').textContent=step.title;
  card.querySelector('.tutorialText').textContent=step.text;
  card.querySelector('.tutorialCounter').textContent=(tutorialIndex+1)+' من '+tutorialSteps.length;
  card.querySelector('.tutorialProgress span').style.width=((tutorialIndex+1)/tutorialSteps.length*100)+'%';
  const prev=card.querySelector('.tutorialPrev'),next=card.querySelector('.tutorialNext');
  prev.style.visibility=tutorialIndex===0?'hidden':'visible';
  next.textContent=tutorialIndex===tutorialSteps.length-1?'إنهاء':'التالي';
  clearTimeout(refreshTimer);
  refreshTimer=setTimeout(()=>{
    if(!tutorialActive)return;
    if(!step.selector){coverAll();card.classList.remove('atTop','atBottom');card.classList.add('welcome');return}
    const target=resolveTarget(step);
    if(target){
      try{target.scrollIntoView({behavior:'auto',block:'center',inline:'nearest'})}catch(e){}
      setTimeout(()=>focusElement(resolveTarget(step)),60);
    }else focusElement(null);
  },80);
}

function finishTutorial(markComplete){
  if(!tutorialActive)return;
  tutorialActive=false;
  clearTimeout(refreshTimer);
  if(markComplete)localStorage.setItem(TUTORIAL_KEY,'1');
  if(tutorialRoot)tutorialRoot.style.display='none';
  if(typeof goPage==='function'&&document.getElementById(tutorialOrigin))goPage(tutorialOrigin);
}

window.startWafferliTutorial=function(manual){
  if(tutorialActive)return;
  tutorialOrigin=activePageId();
  tutorialIndex=0;
  tutorialActive=true;
  buildTutorialRoot();
  renderTutorialStep();
};
window.wafferliTutorialNext=function(){if(!tutorialActive)return;if(tutorialIndex>=tutorialSteps.length-1){finishTutorial(true);return}tutorialIndex++;renderTutorialStep()};
window.wafferliTutorialPrevious=function(){if(!tutorialActive)return;if(tutorialIndex>0){tutorialIndex--;renderTutorialStep()}};
window.skipWafferliTutorial=function(){finishTutorial(true)};
window.isWafferliTutorialActive=function(){return tutorialActive};

const previousBack=window.wafferliHandleBack;
window.wafferliHandleBack=function(){
  if(tutorialActive){if(tutorialIndex>0)window.wafferliTutorialPrevious();return true}
  return typeof previousBack==='function'?previousBack():false;
};

window.addEventListener('resize',()=>{if(tutorialActive)renderTutorialStep()});
window.addEventListener('orientationchange',()=>{if(tutorialActive)setTimeout(renderTutorialStep,120)});

function autoStartWhenReady(){
  if(localStorage.getItem(TUTORIAL_KEY)==='1')return;
  let attempts=0;
  const timer=setInterval(()=>{
    attempts++;
    const modal=document.querySelector('.modal.show');
    const ready=typeof state!=='undefined'&&state&&state.onboarded&&state.baseCurrency&&!modal;
    if(ready){clearInterval(timer);setTimeout(()=>window.startWafferliTutorial(false),220)}
    else if(attempts>1200)clearInterval(timer);
  },250);
}
window.addEventListener('load',()=>setTimeout(autoStartWhenReady,250),{once:true});
})();
