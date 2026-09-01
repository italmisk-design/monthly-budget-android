package com.monthlybudget.app;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.content.Intent;
import android.widget.RemoteViews;

public class WafferliQuickWidget extends AppWidgetProvider {
    public static final String EXTRA_QUICK_ACTION = "wafferli_quick_action";
    public static final String ACTION_INCOME = "income";
    public static final String ACTION_EXPENSE = "expense";

    private PendingIntent actionIntent(Context context, String action, int requestCode) {
        Intent intent = new Intent(context, MainActivity.class);
        intent.putExtra(EXTRA_QUICK_ACTION, action);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        return PendingIntent.getActivity(
                context,
                requestCode,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );
    }

    @Override
    public void onUpdate(Context context, AppWidgetManager appWidgetManager, int[] appWidgetIds) {
        for (int appWidgetId : appWidgetIds) {
            RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.wafferli_quick_widget);
            views.setOnClickPendingIntent(R.id.widgetIncome, actionIntent(context, ACTION_INCOME, 1801));
            views.setOnClickPendingIntent(R.id.widgetExpense, actionIntent(context, ACTION_EXPENSE, 1802));
            appWidgetManager.updateAppWidget(appWidgetId, views);
        }
    }
}
