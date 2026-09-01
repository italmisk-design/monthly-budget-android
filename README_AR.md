# Wafferli v16 Training

نسخة مصدر منظفة مبنية مباشرة من السورس بدون patching أثناء الـBuild.

## هيكل الواجهة
- `assets/index.html`: HTML فقط
- `assets/style.css`: التنسيق
- `assets/app.js`: منطق التطبيق
- `assets/sync.js`: مزامنة Google
- `assets/primary_wallet.js`: منطق المحفظة الرئيسية
- `assets/tutorial.js`: التدريب التفاعلي السريع باللغة العربية الفصحى

## الشعار
الـBuild لا يغيّر الشعار. يمكن تغييره لاحقاً بشكل مقصود بواسطة `tools/update_logo.py` ثم `tools/verify_project.py`.

## فحص سريع
```bash
python tools/verify_project.py
node --check app/src/main/assets/app.js
node --check app/src/main/assets/sync.js
node --check app/src/main/assets/primary_wallet.js
node --check app/src/main/assets/tutorial.js
```
