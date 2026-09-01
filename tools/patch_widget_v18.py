from pathlib import Path

root = Path('app/src/main')
java = root / 'java/com/monthlybudget/app/MainActivity.java'
manifest = root / 'AndroidManifest.xml'
strings = root / 'res/values/strings.xml'

s = java.read_text(encoding='utf-8')
if 'pendingQuickAddType' not in s:
    s = s.replace('    private String pendingGooglePayload = "";\n', '    private String pendingGooglePayload = "";\n    private String pendingQuickAddType = "";\n')
    s = s.replace('                pageLoaded = true;\n                applySafeAreaToWeb();\n', '                pageLoaded = true;\n                applySafeAreaToWeb();\n                dispatchQuickAdd();\n')
    s = s.replace('        if (savedInstanceState == null) webView.loadUrl("file:///android_asset/index.html");\n        else webView.restoreState(savedInstanceState);\n    }\n', '''        captureQuickAdd(getIntent());\n        if (savedInstanceState == null) webView.loadUrl("file:///android_asset/index.html");\n        else {\n            webView.restoreState(savedInstanceState);\n            webView.postDelayed(this::dispatchQuickAdd, 350);\n        }\n    }\n\n    @Override\n    protected void onNewIntent(Intent intent) {\n        super.onNewIntent(intent);\n        setIntent(intent);\n        captureQuickAdd(intent);\n    }\n\n    private void captureQuickAdd(Intent intent) {\n        if (intent == null) return;\n        String type = intent.getStringExtra("quick_add");\n        if ("income".equals(type) || "expense".equals(type)) {\n            pendingQuickAddType = type;\n            if (pageLoaded) dispatchQuickAdd();\n        }\n    }\n\n    private void dispatchQuickAdd() {\n        if (!pageLoaded || webView == null || pendingQuickAddType.isEmpty()) return;\n        final String type = pendingQuickAddType;\n        pendingQuickAddType = "";\n        final String js = "setTimeout(function(){if(window.openTx){window.openTx(" + JSONObject.quote(type) + ");}},120);";\n        webView.post(() -> webView.evaluateJavascript(js, null));\n    }\n''')
    java.write_text(s, encoding='utf-8')

widget_java = root / 'java/com/monthlybudget/app/QuickAddWidget.java'
widget_java.parent.mkdir(parents=True, exist_ok=True)
widget_java.write_text('''package com.monthlybudget.app;\n\nimport android.app.PendingIntent;\nimport android.appwidget.AppWidgetManager;\nimport android.appwidget.AppWidgetProvider;\nimport android.content.Context;\nimport android.content.Intent;\nimport android.widget.RemoteViews;\n\npublic class QuickAddWidget extends AppWidgetProvider {\n    @Override\n    public void onUpdate(Context context, AppWidgetManager appWidgetManager, int[] appWidgetIds) {\n        for (int appWidgetId : appWidgetIds) {\n            RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.widget_quick_add);\n            views.setOnClickPendingIntent(R.id.widgetIncome, quickIntent(context, "income", 1801));\n            views.setOnClickPendingIntent(R.id.widgetExpense, quickIntent(context, "expense", 1802));\n            appWidgetManager.updateAppWidget(appWidgetId, views);\n        }\n    }\n\n    private PendingIntent quickIntent(Context context, String type, int requestCode) {\n        Intent intent = new Intent(context, MainActivity.class);\n        intent.setAction("com.monthlybudget.app.QUICK_ADD_" + type.toUpperCase());\n        intent.putExtra("quick_add", type);\n        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);\n        return PendingIntent.getActivity(context, requestCode, intent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);\n    }\n}\n''', encoding='utf-8')

layout = root / 'res/layout/widget_quick_add.xml'
layout.parent.mkdir(parents=True, exist_ok=True)
layout.write_text('''<?xml version="1.0" encoding="utf-8"?>\n<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android" android:layout_width="match_parent" android:layout_height="match_parent" android:orientation="vertical" android:gravity="center" android:padding="10dp" android:background="@drawable/widget_background">\n    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="وفرلي" android:textStyle="bold" android:textSize="16sp" android:textColor="#26352F" android:layout_marginBottom="8dp" />\n    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:gravity="center">\n        <TextView android:id="@+id/widgetIncome" android:layout_width="0dp" android:layout_height="44dp" android:layout_weight="1" android:gravity="center" android:text="+ إيراد" android:textStyle="bold" android:textSize="15sp" android:textColor="#FFFFFF" android:background="@drawable/widget_income_button" />\n        <Space android:layout_width="8dp" android:layout_height="1dp" />\n        <TextView android:id="@+id/widgetExpense" android:layout_width="0dp" android:layout_height="44dp" android:layout_weight="1" android:gravity="center" android:text="− مصروف" android:textStyle="bold" android:textSize="15sp" android:textColor="#FFFFFF" android:background="@drawable/widget_expense_button" />\n    </LinearLayout>\n</LinearLayout>\n''', encoding='utf-8')

for name, color in [('widget_background', '#F7FAF8'), ('widget_income_button', '#4F765E'), ('widget_expense_button', '#8B5D55')]:
    p = root / f'res/drawable/{name}.xml'
    p.parent.mkdir(parents=True, exist_ok=True)
    stroke = '<stroke android:width="1dp" android:color="#DDE6E1" />' if name == 'widget_background' else ''
    radius = '20dp' if name == 'widget_background' else '14dp'
    p.write_text(f'''<?xml version="1.0" encoding="utf-8"?>\n<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">\n    <solid android:color="{color}" />\n    <corners android:radius="{radius}" />\n    {stroke}\n</shape>\n''', encoding='utf-8')

info = root / 'res/xml/quick_add_widget_info.xml'
info.parent.mkdir(parents=True, exist_ok=True)
info.write_text('''<?xml version="1.0" encoding="utf-8"?>\n<appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android" android:minWidth="180dp" android:minHeight="80dp" android:targetCellWidth="3" android:targetCellHeight="1" android:updatePeriodMillis="0" android:initialLayout="@layout/widget_quick_add" android:resizeMode="horizontal" android:widgetCategory="home_screen" android:description="@string/widget_description" />\n''', encoding='utf-8')

m = manifest.read_text(encoding='utf-8')
if '.QuickAddWidget' not in m:
    m = m.replace('        </activity>\n    </application>', '''        </activity>\n        <receiver android:name=".QuickAddWidget" android:exported="false">\n            <intent-filter>\n                <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />\n            </intent-filter>\n            <meta-data android:name="android.appwidget.provider" android:resource="@xml/quick_add_widget_info" />\n        </receiver>\n    </application>''')
    manifest.write_text(m, encoding='utf-8')

st = strings.read_text(encoding='utf-8')
if 'widget_description' not in st:
    st = st.replace('</resources>', '    <string name="widget_description">إضافة إيراد أو مصروف بسرعة</string>\n</resources>')
    strings.write_text(st, encoding='utf-8')

print('Wafferli v18 Android quick-add widget applied')
