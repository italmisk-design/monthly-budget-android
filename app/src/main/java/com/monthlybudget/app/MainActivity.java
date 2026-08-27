package com.monthlybudget.app;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

public class MainActivity extends Activity {

    private static final int REQ_SAVE = 1001;
    private static final int REQ_OPEN = 1002;

    private WebView webView;
    private String pendingSaveContent = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        getWindow().getDecorView().setLayoutDirection(android.view.View.LAYOUT_DIRECTION_RTL);

        webView = new WebView(this);
        webView.setLayoutDirection(android.view.View.LAYOUT_DIRECTION_RTL);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setTextZoom(100);

        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient());
        webView.addJavascriptInterface(new AndroidBridge(), "AndroidBudget");

        if (savedInstanceState == null) {
            webView.loadUrl("file:///android_asset/index.html");
        } else {
            webView.restoreState(savedInstanceState);
        }
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        webView.saveState(outState);
        super.onSaveInstanceState(outState);
    }

    public class AndroidBridge {
        @JavascriptInterface
        public void saveBudget(String defaultFileName, String content) {
            pendingSaveContent = content == null ? "" : content;
            runOnUiThread(() -> {
                Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("text/plain");
                intent.putExtra(Intent.EXTRA_TITLE,
                        (defaultFileName == null || defaultFileName.trim().isEmpty())
                                ? "ميزانية.txt" : defaultFileName);
                startActivityForResult(intent, REQ_SAVE);
            });
        }

        @JavascriptInterface
        public void openBudget() {
            runOnUiThread(() -> {
                Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("text/*");
                startActivityForResult(intent, REQ_OPEN);
            });
        }

        @JavascriptInterface
        public void toast(String message) {
            runOnUiThread(() ->
                    Toast.makeText(MainActivity.this,
                            message == null ? "" : message,
                            Toast.LENGTH_SHORT).show()
            );
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (resultCode != RESULT_OK || data == null || data.getData() == null) {
            return;
        }

        Uri uri = data.getData();

        if (requestCode == REQ_SAVE) {
            try (OutputStream out = getContentResolver().openOutputStream(uri, "wt")) {
                if (out == null) throw new Exception("تعذر فتح الملف للحفظ");
                out.write(pendingSaveContent.getBytes(StandardCharsets.UTF_8));
                out.flush();
                Toast.makeText(this, "تم حفظ الميزانية بنجاح", Toast.LENGTH_SHORT).show();
            } catch (Exception e) {
                Toast.makeText(this, "خطأ في الحفظ: " + e.getMessage(), Toast.LENGTH_LONG).show();
            }
            return;
        }

        if (requestCode == REQ_OPEN) {
            try {
                StringBuilder sb = new StringBuilder();
                try (InputStream in = getContentResolver().openInputStream(uri);
                     BufferedReader reader = new BufferedReader(
                             new InputStreamReader(in, StandardCharsets.UTF_8))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        sb.append(line).append('\n');
                    }
                }

                final String quoted = JSONObject.quote(sb.toString());
                webView.evaluateJavascript(
                        "window.loadBudgetFromAndroid(" + quoted + ");", null
                );
            } catch (Exception e) {
                Toast.makeText(this, "خطأ في فتح الملف: " + e.getMessage(), Toast.LENGTH_LONG).show();
            }
        }
    }
}
