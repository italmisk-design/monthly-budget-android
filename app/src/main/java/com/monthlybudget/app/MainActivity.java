package com.monthlybudget.app;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.WindowInsets;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.Toast;

import com.google.android.gms.auth.api.identity.AuthorizationClient;
import com.google.android.gms.auth.api.identity.AuthorizationRequest;
import com.google.android.gms.auth.api.identity.AuthorizationResult;
import com.google.android.gms.auth.api.identity.Identity;
import com.google.android.gms.auth.api.signin.GoogleSignInAccount;
import com.google.android.gms.common.Scopes;
import com.google.android.gms.common.api.ApiException;
import com.google.android.gms.common.api.Scope;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {
    private static final int REQ_SAVE = 1001;
    private static final int REQ_OPEN = 1002;
    private static final int REQ_GOOGLE_AUTH = 1901;
    private static final String GOOGLE_PREFS = "wafferli_google";
    private static final String DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.appdata";
    private static final String BACKUP_NAME = "Wafferli-Backup.json";

    private WebView webView;
    private String pendingSaveContent = "";
    private int safeTop = 0, safeBottom = 0, safeLeft = 0, safeRight = 0;
    private boolean pageLoaded = false;
    private final ExecutorService io = Executors.newSingleThreadExecutor();
    private SharedPreferences googlePrefs;
    private AuthorizationClient authorizationClient;
    private String currentAccessToken = "";
    private String pendingGoogleAction = "";
    private String pendingGooglePayload = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        googlePrefs = getSharedPreferences(GOOGLE_PREFS, MODE_PRIVATE);
        authorizationClient = Identity.getAuthorizationClient(this);

        getWindow().getDecorView().setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) getWindow().setDecorFitsSystemWindows(false);
        getWindow().setStatusBarColor(Color.TRANSPARENT);
        getWindow().setNavigationBarColor(Color.TRANSPARENT);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);

        final FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.rgb(243, 246, 245));
        root.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);

        webView = new WebView(this);
        webView.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        webView.setBackgroundColor(Color.TRANSPARENT);
        root.addView(webView, new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));
        setContentView(root);

        root.setOnApplyWindowInsetsListener((v, insets) -> {
            int topPx, bottomPx, leftPx, rightPx;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                android.graphics.Insets bars = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
                topPx = bars.top; bottomPx = bars.bottom; leftPx = bars.left; rightPx = bars.right;
            } else {
                topPx = insets.getSystemWindowInsetTop(); bottomPx = insets.getSystemWindowInsetBottom();
                leftPx = insets.getSystemWindowInsetLeft(); rightPx = insets.getSystemWindowInsetRight();
            }
            float density = getResources().getDisplayMetrics().density;
            if (density <= 0f) density = 1f;
            safeTop = Math.round(topPx / density); safeBottom = Math.round(bottomPx / density);
            safeLeft = Math.round(leftPx / density); safeRight = Math.round(rightPx / density);
            applySafeAreaToWeb();
            return insets;
        });
        root.requestApplyInsets();

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setTextZoom(100);

        webView.setWebViewClient(new WebViewClient() {
            @Override public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                pageLoaded = true;
                applySafeAreaToWeb();
            }
        });
        webView.setWebChromeClient(new WebChromeClient());
        webView.addJavascriptInterface(new AndroidBridge(), "AndroidBudget");

        if (savedInstanceState == null) webView.loadUrl("file:///android_asset/index.html");
        else webView.restoreState(savedInstanceState);
    }

    private void applySafeAreaToWeb() {
        if (!pageLoaded || webView == null) return;
        final String js = "(function(){var r=document.documentElement;" +
                "r.style.setProperty('--native-safe-top','" + safeTop + "px');" +
                "r.style.setProperty('--native-safe-bottom','" + safeBottom + "px');" +
                "r.style.setProperty('--native-safe-left','" + safeLeft + "px');" +
                "r.style.setProperty('--native-safe-right','" + safeRight + "px');" +
                "})();";
        webView.post(() -> webView.evaluateJavascript(js, null));
    }

    private void eval(String js) {
        runOnUiThread(() -> { if (webView != null) webView.evaluateJavascript(js, null); });
    }

    private List<Scope> googleScopes() {
        return Arrays.asList(new Scope(DRIVE_SCOPE), new Scope(Scopes.EMAIL), new Scope(Scopes.PROFILE));
    }

    private AuthorizationRequest googleRequest(boolean selectAccount) {
        AuthorizationRequest.Builder b = AuthorizationRequest.builder().setRequestedScopes(googleScopes());
        if (selectAccount) b.setPrompt(AuthorizationRequest.Prompt.SELECT_ACCOUNT);
        return b.build();
    }

    private void sendGoogleStatus() {
        try {
            JSONObject j = new JSONObject();
            boolean signed = googlePrefs.getBoolean("linked", false);
            j.put("signedIn", signed);
            j.put("email", googlePrefs.getString("email", ""));
            j.put("name", googlePrefs.getString("name", ""));
            eval("window.wafferliGoogleStatus&&window.wafferliGoogleStatus(" + j + ");");
        } catch (Exception ignored) {}
    }

    private void googleDone(String action, boolean ok, String message) {
        eval("window.wafferliGoogleDone&&window.wafferliGoogleDone(" + JSONObject.quote(action) + "," + ok + "," + JSONObject.quote(message == null ? "" : message) + ");");
    }

    private void requestAuthorization(boolean selectAccount, String afterAction, String payload) {
        pendingGoogleAction = afterAction == null ? "" : afterAction;
        pendingGooglePayload = payload == null ? "" : payload;
        authorizationClient.authorize(googleRequest(selectAccount))
                .addOnSuccessListener(this, result -> handleAuthorizationResult(result, pendingGoogleAction, pendingGooglePayload))
                .addOnFailureListener(this, e -> googleDone(afterAction, false, cleanError(e)));
    }

    private void handleAuthorizationResult(AuthorizationResult result, String afterAction, String payload) {
        if (result == null) { googleDone(afterAction, false, "لم يصل رد من Google"); return; }
        if (result.hasResolution()) {
            try {
                pendingGoogleAction = afterAction == null ? "" : afterAction;
                pendingGooglePayload = payload == null ? "" : payload;
                startIntentSenderForResult(result.getPendingIntent().getIntentSender(), REQ_GOOGLE_AUTH, null, 0, 0, 0);
            } catch (Exception e) { googleDone(afterAction, false, cleanError(e)); }
            return;
        }
        finishAuthorization(result, afterAction, payload);
    }

    private void finishAuthorization(AuthorizationResult result, String afterAction, String payload) {
        String token = result.getAccessToken();
        if (token == null || token.isEmpty()) { googleDone(afterAction, false, "لم يمنح Google صلاحية الوصول"); return; }
        currentAccessToken = token;
        String email = "", name = "";
        try {
            GoogleSignInAccount a = result.toGoogleSignInAccount();
            if (a != null) {
                email = a.getEmail() == null ? "" : a.getEmail();
                name = a.getDisplayName() == null ? "" : a.getDisplayName();
            }
        } catch (Exception ignored) {}
        googlePrefs.edit().putBoolean("linked", true).putString("email", email).putString("name", name).apply();
        sendGoogleStatus();

        if ("backup".equals(afterAction)) {
            final String content = payload == null ? "" : payload;
            io.execute(() -> { try { uploadBackup(content); googleDone("backup", true, "تم حفظ النسخة على Google Drive"); } catch (Exception e) { googleDone("backup", false, cleanError(e)); } });
        } else if ("restore".equals(afterAction)) {
            io.execute(() -> { try { String data = downloadBackup(); eval("window.loadBudgetFromGoogle&&window.loadBudgetFromGoogle(" + JSONObject.quote(data) + ");"); googleDone("restore", true, "تم تحميل النسخة من Google Drive"); } catch (Exception e) { googleDone("restore", false, cleanError(e)); } });
        } else {
            googleDone("signin", true, "تم ربط حساب Google بنجاح");
        }
    }

    private String enc(String s) throws Exception { return URLEncoder.encode(s, "UTF-8"); }

    private String readAll(InputStream input) throws Exception {
        if (input == null) return "";
        StringBuilder sb = new StringBuilder();
        try (BufferedReader r = new BufferedReader(new InputStreamReader(input, StandardCharsets.UTF_8))) {
            String line; while ((line = r.readLine()) != null) sb.append(line).append('\n');
        }
        return sb.toString();
    }

    private String response(HttpURLConnection c) throws Exception {
        int code = c.getResponseCode();
        String body = readAll(code >= 200 && code < 300 ? c.getInputStream() : c.getErrorStream());
        if (code < 200 || code >= 300) throw new Exception("Google HTTP " + code + (body.isEmpty() ? "" : ": " + body));
        return body;
    }

    private String accessToken() throws Exception {
        if (currentAccessToken == null || currentAccessToken.isEmpty()) throw new Exception("سجّل الدخول بحساب Google أولاً");
        return currentAccessToken;
    }

    private String authedGet(String endpoint) throws Exception {
        HttpURLConnection c = (HttpURLConnection) new URL(endpoint).openConnection();
        c.setConnectTimeout(20000); c.setReadTimeout(30000);
        c.setRequestProperty("Authorization", "Bearer " + accessToken());
        return response(c);
    }

    private String latestBackupId() throws Exception {
        String q = "name='" + BACKUP_NAME + "' and trashed=false";
        String url = "https://www.googleapis.com/drive/v3/files?spaces=appDataFolder&q=" + enc(q) +
                "&fields=" + enc("files(id,name,modifiedTime)") + "&orderBy=" + enc("modifiedTime desc") + "&pageSize=1";
        JSONObject obj = new JSONObject(authedGet(url));
        JSONArray files = obj.optJSONArray("files");
        return files != null && files.length() > 0 ? files.getJSONObject(0).optString("id", "") : "";
    }

    private void uploadBackup(String content) throws Exception {
        String id = latestBackupId();
        if (!id.isEmpty()) {
            HttpURLConnection c = (HttpURLConnection) new URL("https://www.googleapis.com/upload/drive/v3/files/" + enc(id) + "?uploadType=media").openConnection();
            c.setConnectTimeout(20000); c.setReadTimeout(30000); c.setRequestMethod("POST"); c.setDoOutput(true);
            c.setRequestProperty("X-HTTP-Method-Override", "PATCH");
            c.setRequestProperty("Authorization", "Bearer " + accessToken());
            c.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
            try (OutputStream out = c.getOutputStream()) { out.write(content.getBytes(StandardCharsets.UTF_8)); }
            response(c); return;
        }
        String boundary = "wafferli_" + System.currentTimeMillis();
        JSONObject meta = new JSONObject(); meta.put("name", BACKUP_NAME); meta.put("parents", new JSONArray().put("appDataFolder"));
        String body = "--" + boundary + "\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n" + meta +
                "\r\n--" + boundary + "\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n" + content + "\r\n--" + boundary + "--\r\n";
        HttpURLConnection c = (HttpURLConnection) new URL("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart").openConnection();
        c.setConnectTimeout(20000); c.setReadTimeout(30000); c.setRequestMethod("POST"); c.setDoOutput(true);
        c.setRequestProperty("Authorization", "Bearer " + accessToken());
        c.setRequestProperty("Content-Type", "multipart/related; boundary=" + boundary);
        try (OutputStream out = c.getOutputStream()) { out.write(body.getBytes(StandardCharsets.UTF_8)); }
        response(c);
    }

    private String downloadBackup() throws Exception {
        String id = latestBackupId();
        if (id.isEmpty()) throw new Exception("لا توجد نسخة احتياطية على Google Drive");
        return authedGet("https://www.googleapis.com/drive/v3/files/" + enc(id) + "?alt=media");
    }

    private String cleanError(Exception e) {
        String m = e == null ? null : e.getMessage();
        if (m == null || m.trim().isEmpty()) m = "حدث خطأ غير معروف";
        if (m.length() > 300) m = m.substring(0, 300);
        return m;
    }

    @Override protected void onSaveInstanceState(Bundle outState) { webView.saveState(outState); super.onSaveInstanceState(outState); }

    @Override public void onBackPressed() {
        webView.evaluateJavascript("document.getElementById('txModal').classList.contains('show')", value -> {
            if ("true".equals(value)) webView.evaluateJavascript("closeTx()", null); else super.onBackPressed();
        });
    }

    public class AndroidBridge {
        @JavascriptInterface public void saveBudget(String defaultFileName, String content) {
            pendingSaveContent = content == null ? "" : content;
            runOnUiThread(() -> {
                Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("application/json");
                intent.putExtra(Intent.EXTRA_TITLE, (defaultFileName == null || defaultFileName.trim().isEmpty()) ? BACKUP_NAME : defaultFileName);
                startActivityForResult(intent, REQ_SAVE);
            });
        }

        @JavascriptInterface public void openBudget() {
            runOnUiThread(() -> {
                Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("application/json");
                startActivityForResult(intent, REQ_OPEN);
            });
        }

        @JavascriptInterface public void toast(String message) {
            runOnUiThread(() -> Toast.makeText(MainActivity.this, message == null ? "" : message, Toast.LENGTH_SHORT).show());
        }

        @JavascriptInterface public void googleAction(String action, String payload) {
            if (action == null) return;
            switch (action) {
                case "status": sendGoogleStatus(); break;
                case "signin": requestAuthorization(true, "signin", ""); break;
                case "signout":
                    currentAccessToken = "";
                    googlePrefs.edit().clear().apply();
                    sendGoogleStatus(); googleDone("signout", true, "تم تسجيل الخروج من Google");
                    break;
                case "backup": requestAuthorization(false, "backup", payload); break;
                case "restore": requestAuthorization(false, "restore", ""); break;
            }
        }
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == REQ_GOOGLE_AUTH) {
            if (resultCode != RESULT_OK || data == null) { googleDone(pendingGoogleAction, false, "تم إلغاء ربط Google"); return; }
            try {
                AuthorizationResult result = authorizationClient.getAuthorizationResultFromIntent(data);
                finishAuthorization(result, pendingGoogleAction, pendingGooglePayload);
            } catch (ApiException e) { googleDone(pendingGoogleAction, false, cleanError(e)); }
            return;
        }

        if (resultCode != RESULT_OK || data == null || data.getData() == null) return;
        Uri uri = data.getData();
        if (requestCode == REQ_SAVE) {
            try (OutputStream out = getContentResolver().openOutputStream(uri, "wt")) {
                if (out == null) throw new Exception("تعذر فتح الملف للحفظ");
                out.write(pendingSaveContent.getBytes(StandardCharsets.UTF_8)); out.flush();
                Toast.makeText(this, "تم حفظ النسخة الاحتياطية", Toast.LENGTH_SHORT).show();
            } catch (Exception e) { Toast.makeText(this, "خطأ في الحفظ: " + e.getMessage(), Toast.LENGTH_LONG).show(); }
            return;
        }
        if (requestCode == REQ_OPEN) {
            try {
                StringBuilder sb = new StringBuilder();
                try (InputStream in = getContentResolver().openInputStream(uri); BufferedReader reader = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8))) {
                    String line; while ((line = reader.readLine()) != null) sb.append(line).append('\n');
                }
                eval("window.loadBudgetFromAndroid&&window.loadBudgetFromAndroid(" + JSONObject.quote(sb.toString()) + ");");
            } catch (Exception e) { Toast.makeText(this, "خطأ في فتح الملف: " + e.getMessage(), Toast.LENGTH_LONG).show(); }
        }
    }

    @Override protected void onDestroy() {
        io.shutdownNow();
        super.onDestroy();
    }
}
