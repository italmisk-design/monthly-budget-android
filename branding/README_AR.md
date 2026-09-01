# شعار وفرلي

ملف الشعار ليس مقفولاً للأبد؛ يمكن تغييره لاحقاً بشكل مقصود.

- الشعار داخل الواجهة: `app/src/main/assets/wafferli_logo.jpg`
- أيقونة Android: `app/src/main/res/drawable/wafferli_logo.jpg`
- البصمة المرجعية: `branding/wafferli_logo.sha256`

الـBuild لا يولّد الشعار ولا يعدّله. عند تغيير الشعار لاحقاً استخدم `python tools/update_logo.py path/to/new_logo.jpg` ثم راجع الشكل قبل البناء.
