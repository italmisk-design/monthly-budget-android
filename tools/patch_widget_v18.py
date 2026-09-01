from pathlib import Path

ROOT=Path('.')
java=ROOT/'app/src/main/java/com/monthlybudget/app/MainActivity.java'
manifest=ROOT/'app/src/main/AndroidManifest.xml'
strings=ROOT/'app/src/main/res/values/strings.xml'

s=java.read_text(encoding='utf-8')
if 'pendingQuickAction' not in s:
    needle='    private boolean pageLoaded = false;'
    if needle not in s: raise SystemExit('pageLoaded marker not found')
    s=s.replace(needle, needle+'\n    private String pendingQuickAction = "";',1)

if 'dispatchQuickAction();' not in s:
    needle='                applySafeAreaToWeb();\n'
    pos=s.find(needle)
    if pos<0: raise SystemExit('onPageFinished marker not found')
    s=s[:pos]+needle+'                dispatchQuickAction();\n'+s[pos+len(needle):]

if 'handleQuickActionIntent(getIntent());' not in s:
    needle='        webView.addJavascriptInterface(new AndroidBridge(), "AndroidBudget");\n\n'
    if needle not in s: raise SystemExit('bridge marker not found')
    s=s.replace(needle, needle+'        handleQuickActionIntent(getIntent());\n',1)

if 'private void handleQuickActionIntent(Intent intent)' not in s:
    marker='    private void applySafeAreaToWeb() {'
    if marker not in s: raise SystemExit('safe area method marker not found')
    methods='''    private void handleQuickActionIntent(Intent intent) {\n        if (intent == null) return;\n        String action = intent.getStringExtra(WafferliQuickWidget.EXTRA_QUICK_ACTION);\n        if (WafferliQuickWidget.ACTION_INCOME.equals(action) || WafferliQuickWidget.ACTION_EXPENSE.equals(action)) {\n            pendingQuickAction = action;\n            if (pageLoaded) dispatchQuickAction();\n            intent.removeExtra(WafferliQuickWidget.EXTRA_QUICK_ACTION);\n        }\n    }\n\n    private void dispatchQuickAction() {\n        if (!pageLoaded || webView == null || pendingQuickAction == null || pendingQuickAction.isEmpty()) return;\n        final String action = pendingQuickAction;\n        pendingQuickAction = "";\n        final String js = "(function(){var a=" + JSONObject.quote(action) + ";" +\n                "function q(){if(typeof openTx==='function'){openTx(a);var e=document.getElementById('amountInput');if(e){setTimeout(function(){e.focus();},120);}return true;}return false;}" +\n                "if(!q()){setTimeout(q,250);}})();";\n        webView.post(() -> webView.evaluateJavascript(js, null));\n    }\n\n    @Override protected void onNewIntent(Intent intent) {\n        super.onNewIntent(intent);\n        setIntent(intent);\n        handleQuickActionIntent(intent);\n    }\n\n'''
    s=s.replace(marker,methods+marker,1)
java.write_text(s,encoding='utf-8')

m=manifest.read_text(encoding='utf-8')
if 'android:launchMode="singleTop"' not in m:
    m=m.replace('android:exported="true"\n            android:screenOrientation="unspecified"', 'android:exported="true"\n            android:launchMode="singleTop"\n            android:screenOrientation="unspecified"',1)
if '.WafferliQuickWidget' not in m:
    receiver='''\n        <receiver\n            android:name=".WafferliQuickWidget"\n            android:exported="false">\n            <intent-filter>\n                <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />\n            </intent-filter>\n            <meta-data\n                android:name="android.appwidget.provider"\n                android:resource="@xml/wafferli_quick_widget_info" />\n        </receiver>\n'''
    m=m.replace('    </application>',receiver+'    </application>',1)
manifest.write_text(m,encoding='utf-8')

st=strings.read_text(encoding='utf-8')
if 'widget_description' not in st:
    st=st.replace('</resources>','    <string name="widget_description">إضافة إيراد أو مصروف بسرعة</string>\n</resources>',1)
strings.write_text(st,encoding='utf-8')

widget_java=ROOT/'app/src/main/java/com/monthlybudget/app/WafferliQuickWidget.java'
widget_java.write_text('''package com.monthlybudget.app;\n\nimport android.app.PendingIntent;\nimport android.appwidget.AppWidgetManager;\nimport android.appwidget.AppWidgetProvider;\nimport android.content.Context;\nimport android.content.Intent;\nimport android.widget.RemoteViews;\n\npublic class WafferliQuickWidget extends AppWidgetProvider {\n    public static final String EXTRA_QUICK_ACTION = "wafferli_quick_action";\n    public static final String ACTION_INCOME = "income";\n    public static final String ACTION_EXPENSE = "expense";\n\n    private PendingIntent actionIntent(Context context, String action, int requestCode) {\n        Intent intent = new Intent(context, MainActivity.class);\n        intent.putExtra(EXTRA_QUICK_ACTION, action);\n        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);\n        return PendingIntent.getActivity(context, requestCode, intent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);\n    }\n\n    @Override public void onUpdate(Context context, AppWidgetManager appWidgetManager, int[] appWidgetIds) {\n        for (int appWidgetId : appWidgetIds) {\n            RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.wafferli_quick_widget);\n            views.setOnClickPendingIntent(R.id.widgetIncome, actionIntent(context, ACTION_INCOME, 1801));\n            views.setOnClickPendingIntent(R.id.widgetExpense, actionIntent(context, ACTION_EXPENSE, 1802));\n            appWidgetManager.updateAppWidget(appWidgetId, views);\n        }\n    }\n}\n''',encoding='utf-8')

for d in ['app/src/main/res/layout','app/src/main/res/xml','app/src/main/res/drawable']:
    (ROOT/d).mkdir(parents=True,exist_ok=True)
(ROOT/'app/src/main/res/drawable/widget_bg.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>\n<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle"><solid android:color="#F7F9F8"/><corners android:radius="20dp"/><stroke android:width="1dp" android:color="#DCE4E0"/><padding android:left="10dp" android:top="8dp" android:right="10dp" android:bottom="8dp"/></shape>\n''',encoding='utf-8')
(ROOT/'app/src/main/res/drawable/widget_income_bg.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>\n<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle"><solid android:color="#169960"/><corners android:radius="14dp"/></shape>\n''',encoding='utf-8')
(ROOT/'app/src/main/res/drawable/widget_expense_bg.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>\n<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle"><solid android:color="#D94B53"/><corners android:radius="14dp"/></shape>\n''',encoding='utf-8')
(ROOT/'app/src/main/res/layout/wafferli_quick_widget.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>\n<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android" android:layout_width="match_parent" android:layout_height="match_parent" android:orientation="vertical" android:gravity="center" android:padding="8dp" android:background="@drawable/widget_bg">\n<TextView android:id="@+id/widgetTitle" android:layout_width="match_parent" android:layout_height="wrap_content" android:text="وفرلي" android:textColor="#18211E" android:textStyle="bold" android:textSize="14sp" android:gravity="center" android:includeFontPadding="false" android:layout_marginBottom="7dp"/>\n<LinearLayout android:layout_width="match_parent" android:layout_height="0dp" android:layout_weight="1" android:orientation="horizontal" android:gravity="center">\n<TextView android:id="@+id/widgetIncome" android:layout_width="0dp" android:layout_height="match_parent" android:layout_weight="1" android:layout_marginEnd="4dp" android:background="@drawable/widget_income_bg" android:gravity="center" android:text="+  إيراد" android:textColor="#FFFFFF" android:textStyle="bold" android:textSize="15sp"/>\n<TextView android:id="@+id/widgetExpense" android:layout_width="0dp" android:layout_height="match_parent" android:layout_weight="1" android:layout_marginStart="4dp" android:background="@drawable/widget_expense_bg" android:gravity="center" android:text="−  مصروف" android:textColor="#FFFFFF" android:textStyle="bold" android:textSize="15sp"/>\n</LinearLayout></LinearLayout>\n''',encoding='utf-8')
(ROOT/'app/src/main/res/xml/wafferli_quick_widget_info.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>\n<appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android" android:minWidth="180dp" android:minHeight="78dp" android:minResizeWidth="140dp" android:minResizeHeight="70dp" android:updatePeriodMillis="0" android:initialLayout="@layout/wafferli_quick_widget" android:resizeMode="horizontal|vertical" android:widgetCategory="home_screen" android:description="@string/widget_description"/>\n''',encoding='utf-8')

print('Wafferli v18 quick widget patch applied')
