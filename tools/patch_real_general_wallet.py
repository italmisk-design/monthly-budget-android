from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

# Fresh installs: the real primary wallet is the General Wallet.
s = s.replace("{id:'w-main',name:'المحفظة الرئيسية',emoji:'💰',main:true", "{id:'w-main',name:'المحفظة العامة',emoji:'💰',main:true", 1)

# Home summary is a total, not a wallet.
s = s.replace('المحفظة العامة • الحساب العام لجميع المحافظ', 'إجمالي أموالي • مجموع جميع المحافظ', 1)

# Main-wallet badge terminology.
css = '''\n.wallet.main:after{content:"العامة"!important}\n'''
if 'content:"العامة"!important' not in s:
    s = s.replace('</style>', css + '</style>', 1)

# Migrate existing data safely: keep the same primary-wallet id and all its history,
# but make it the real General Wallet. Never create a duplicate wallet.
marker = "function persist(){localStorage.setItem(KEY,JSON.stringify(state))}"
insert = marker + "\nfunction ensureRealGeneralWallet(){if(!Array.isArray(state.wallets)||!state.wallets.length)return;let main=state.wallets.find(w=>w.main);if(!main){main=state.wallets[0];main.main=true}state.wallets.forEach(w=>{if(w!==main)w.main=false});main.name='المحفظة العامة';if(!main.emoji)main.emoji='💰';persist()}\nensureRealGeneralWallet();"
if 'function ensureRealGeneralWallet()' not in s:
    if marker not in s:
        raise SystemExit('persist marker not found')
    s = s.replace(marker, insert, 1)

# The virtual card becomes a non-wallet grand total.
pat = r"function renderWallets\(\)\{.*?\}\n(?=function addWallet)"
replacement = r'''function renderWallets(){const g=generalBalances();document.getElementById('generalWalletCard').innerHTML=`<div class="wallet generalWallet"><div class="walletTop"><div class="wemoji">Σ</div><div><b>إجمالي أموالي</b><small>مجموع أرصدة جميع المحافظ حتى ${fmtDate(selectedCutoff())} • هذا ملخص فقط وليس محفظة</small></div></div><div class="walletAmount"><span>${money(g.iqd,'IQD')}</span><span>${money(g.usd,'USD')}</span><span>≈ ${baseMoney(g.equivalent)}</span></div></div>`;document.getElementById('walletList').innerHTML=state.wallets.map(walletHtml).join('')||'<div class="empty">لا توجد محافظ.</div>';if(activeWalletId)renderWalletDetail()}
'''
s, n = re.subn(pat, lambda m: replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('renderWallets patch failed')

# Additional wallets are always normal wallets; the General Wallet remains the one real primary wallet.
pat = r"function addWallet\(\)\{.*?\}\n(?=function openWallet)"
replacement = r'''function addWallet(){openActionModal('إضافة محفظة',[{id:'name',label:'اسم المحفظة',type:'text',placeholder:'مثال: البيت'},{id:'emoji',label:'رمز المحفظة',type:'text',value:'💼'}],v=>{const name=(v.name||'').trim();if(!name){toast('اكتب اسم المحفظة');return false}const w={id:uid(),name,emoji:(v.emoji||'💼').trim()||'💼',main:false,openingIQD:0,openingUSD:0};state.wallets.push(w);persist();renderAll();toast('تمت إضافة المحفظة');return true})}
'''
s, n = re.subn(pat, lambda m: replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('addWallet patch failed')

# Detail wording.
s = s.replace("document.getElementById('wdMain').textContent=w.main?'المحفظة الرئيسية':'محفظة عادية';", "document.getElementById('wdMain').textContent=w.main?'المحفظة العامة • المحفظة الأساسية':'محفظة عادية';", 1)

# Wallet settings: the General Wallet cannot be demoted or deleted; normal wallets cannot become General.
start = s.find('function walletActions()')
end = s.find('\nfunction addCategory', start)
if start < 0 or end < 0:
    raise SystemExit('walletActions block not found')
new_wallet_actions = r'''function walletActions(){const w=state.wallets.find(x=>x.id===activeWalletId);if(!w)return;if(w.main){openActionModal('إعدادات المحفظة العامة',[{id:'emoji',label:'الرمز',type:'text',value:w.emoji},{id:'openingIQD',label:'الرصيد الافتتاحي IQD',type:'number',value:w.openingIQD||0,inputmode:'decimal'},{id:'openingUSD',label:'الرصيد الافتتاحي USD',type:'number',value:w.openingUSD||0,inputmode:'decimal'}],v=>{w.name='المحفظة العامة';w.emoji=(v.emoji||'💰').trim()||'💰';w.openingIQD=nval(v.openingIQD);w.openingUSD=nval(v.openingUSD);persist();renderAll();toast('تم حفظ إعدادات المحفظة العامة');return true},{message:'هذه هي المحفظة الأساسية الحقيقية: يمكن إضافة الإيرادات والمصاريف عليها والتحويل منها وإليها، ولا يمكن حذفها.'});return}openActionModal('إعدادات المحفظة',[{id:'name',label:'اسم المحفظة',type:'text',value:w.name},{id:'emoji',label:'الرمز',type:'text',value:w.emoji},{id:'openingIQD',label:'الرصيد الافتتاحي IQD',type:'number',value:w.openingIQD||0,inputmode:'decimal'},{id:'openingUSD',label:'الرصيد الافتتاحي USD',type:'number',value:w.openingUSD||0,inputmode:'decimal'}],v=>{const name=(v.name||'').trim();if(!name){toast('اسم المحفظة مطلوب');return false}w.name=name;w.emoji=(v.emoji||'💼').trim()||'💼';w.openingIQD=nval(v.openingIQD);w.openingUSD=nval(v.openingUSD);persist();renderAll();toast('تم حفظ إعدادات المحفظة');return true},{onDelete:()=>{if(state.transactions.some(t=>t.walletId===w.id||t.fromWalletId===w.id||t.toWalletId===w.id)||(state.monthlyTemplates||[]).some(t=>t.walletId===w.id||t.fromWalletId===w.id||t.toWalletId===w.id)){toast('لا يمكن حذف محفظة مستخدمة في حركة أو بند شهري');return false}state.wallets=state.wallets.filter(x=>x.id!==w.id);state.categories=state.categories.filter(x=>x.walletId!==w.id);closeWalletDetail();persist();renderAll();toast('تم حذف المحفظة');return true},deleteText:'حذف المحفظة'})}'''
s = s[:start] + new_wallet_actions + s[end:]

required = ['إجمالي أموالي', 'function ensureRealGeneralWallet()', "main.name='المحفظة العامة'", 'إعدادات المحفظة العامة']
missing = [x for x in required if x not in s]
if missing:
    raise SystemExit('real general wallet validation failed: ' + ', '.join(missing))

p.write_text(s, encoding='utf-8')
print('Real General Wallet patch applied')
