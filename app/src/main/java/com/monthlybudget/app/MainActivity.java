package com.monthlybudget.app;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.util.Base64;
import android.view.View;
import android.view.WindowInsets;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {
    private static final int REQ_SAVE = 1001;
    private static final int REQ_OPEN = 1002;
    private static final String GOOGLE_PREFS = "wafferli_google";
    private static final String DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.appdata";
    private static final String BACKUP_NAME = "Wafferli-Backup.json";

    private WebView webView;
    private String pendingSaveContent = "";
    private int safeTop = 0;
    private int safeBottom = 0;
    private int safeLeft = 0;
    private int safeRight = 0;
    private boolean pageLoaded = false;
    private final ExecutorService io = Executors.newSingleThreadExecutor();
    private SharedPreferences googlePrefs;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        googlePrefs = getSharedPreferences(GOOGLE_PREFS, MODE_PRIVATE);

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

    private void sendGoogleStatus() {
        try {
            JSONObject j = new JSONObject();
            boolean signed = googlePrefs.contains("refresh_token") || googlePrefs.contains("access_token");
            j.put("signedIn", signed);
            j.put("email", googlePrefs.getString("email", ""));
            j.put("name", googlePrefs.getString("name", ""));
            eval("window.wafferliGoogleStatus&&window.wafferliGoogleStatus(" + j.toString() + ");");
        } catch (Exception ignored) {}
    }

    private void googleDone(String action, boolean ok, String message) {
        try {
            eval("window.wafferliGoogleDone&&window.wafferliGoogleDone(" + JSONObject.quote(action) + "," + ok + "," + JSONObject.quote(message == null ? "" : message) + ");");
        } catch (Exception ignored) {}
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

    private JSONObject postForm(String endpoint, String form) throws Exception {
        HttpURLConnection c = (HttpURLConnection) new URL(endpoint).openConnection();
        c.setConnectTimeout(20000); c.setReadTimeout(30000); c.setRequestMethod("POST"); c.setDoOutput(true);
        c.setRequestProperty("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
        try (OutputStream out = c.getOutputStream()) { out.write(form.getBytes(StandardCharsets.UTF_8)); }
        return new JSONObject(response(c));
    }

    private String randomVerifier() {
        byte[] b = new byte[48]; new SecureRandom().nextBytes(b);
        return Base64.encodeToString(b, Base64.URL_SAFE | Base64.NO_WRAP | Base64.NO_PADDING);
    }

    private String challenge(String verifier) throws Exception {
        byte[] hash = MessageDigest.getInstance("SHA-256").digest(verifier.getBytes(StandardCharsets.US_ASCII));
        return Base64.encodeToString(hash, Base64.URL_SAFE | Base64.NO_WRAP | Base64.NO_PADDING);
    }

    private void startGoogleSignIn() {
        io.execute(() -> {
            ServerSocket server = null;
            try {
                server = new ServerSocket(0, 1, InetAddress.getByName("127.0.0.1"));
                server.setSoTimeout(180000);
                int port = server.getLocalPort();
                String redirect = "http://127.0.0.1:" + port;
                String state = UUID.randomUUID().toString();
                String verifier = randomVerifier();
                String scope = "openid email profile " + DRIVE_SCOPE;
                String clientId = getString(R.string.google_oauth_client_id);
                String auth = "https://accounts.google.com/o/oauth2/v2/auth?response_type=code" +
                        "&client_id=" + enc(clientId) + "&redirect_uri=" + enc(redirect) +
                        "&scope=" + enc(scope) + "&access_type=offline&prompt=consent" +
                        "&code_challenge=" + enc(challenge(verifier)) + "&code_challenge_method=S256&state=" + enc(state);
                runOnUiThread(() -> {
                    try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(auth))); }
                    catch (Exception e) { googleDone("signin", false, "تعذر فتح المتصفح"); }
                });

                try (Socket socket = server.accept()) {
                    BufferedReader r = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
                    String first = r.readLine();
                    if (first == null || !first.startsWith("GET ")) throw new Exception("لم يصل رد تسجيل الدخول");
                    String path = first.split(" ")[1];
                    Uri callback = Uri.parse("http://127.0.0.1" + path);
                    String code = callback.getQueryParameter("code");
                    String gotState = callback.getQueryParameter("state");
                    String oauthError = callback.getQueryParameter("error");
                    String html = "<!doctype html><meta charset='utf-8'><meta name='viewport' content='width=device-width'><body style='font-family:sans-serif;text-align:center;padding:40px;direction:rtl'><h2>تم الرجوع إلى وفرلي</h2><p>يمكنك إغلاق هذه الصفحة والعودة إلى التطبيق.</p></body>";
                    byte[] bytes = html.getBytes(StandardCharsets.UTF_8);
                    String head = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: " + bytes.length + "\r\nConnection: close\r\n\r\n";
                    socket.getOutputStream().write(head.getBytes(StandardCharsets.US_ASCII));
                    socket.getOutputStream().write(bytes); socket.getOutputStream().flush();
                    if (oauthError != null) throw new Exception("رفض Google تسجيل الدخول: " + oauthError);
                    if (code == null || !state.equals(gotState)) throw new Exception("رد Google غير صالح");

                    String form = "code=" + enc(code) + "&client_id=" + enc(clientId) + "&redirect_uri=" + enc(redirect) +
                            "&grant_type=authorization_code&code_verifier=" + enc(verifier);
                    JSONObject token = postForm("https://oauth2.googleapis.com/token", form);
                    saveTokens(token);
                    fetchProfile();
                    sendGoogleStatus();
                    googleDone("signin", true, "تم ربط حساب Google بنجاح");
                }
            } catch (Exception e) {
                googleDone("signin", false, cleanError(e));
            } finally {
                try { if (server != null) server.close(); } catch (Exception ignored) {}
            }
        });
    }

    private void saveTokens(JSONObject token) throws Exception {
        SharedPreferences.Editor e = googlePrefs.edit();
        if (token.has("access_token")) e.putString("access_token", token.getString("access_token"));
        if (token.has("refresh_token")) e.putString("refresh_token", token.getString("refresh_token"));
        long expires = token.optLong("expires_in", 3600);
        e.putLong("expires_at", System.currentTimeMillis() + Math.max(60, expires - 60) * 1000L).apply();
    }

    private String accessToken() throws Exception {
        String current = googlePrefs.getString("access_token", "");
        if (!current.isEmpty() && System.currentTimeMillis() < googlePrefs.getLong("expires_at", 0)) return current;
        String refresh = googlePrefs.getString("refresh_token", "");
        if (refresh.isEmpty()) throw new Exception("سجّل الدخول بحساب Google أولاً");
        String clientId = getString(R.string.google_oauth_client_id);
        JSONObject token = postForm("https://oauth2.googleapis.com/token", "client_id=" + enc(clientId) + "&refresh_token=" + enc(refresh) + "&grant_type=refresh_token");
        saveTokens(token);
        return googlePrefs.getString("access_token", "");
    }

    private String authedGet(String endpoint) throws Exception {
        HttpURLConnection c = (HttpURLConnection) new URL(endpoint).openConnection();
        c.setConnectTimeout(20000); c.setReadTimeout(30000); c.setRequestProperty("Authorization", "Bearer " + accessToken());
        return response(c);
    }

    private void fetchProfile() throws Exception {
        JSONObject p = new JSONObject(authedGet("https://www.googleapis.com/oauth2/v3/userinfo"));
        googlePrefs.edit().putString("email", p.optString("email", "")).putString("name", p.optString("name", "")).apply();
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
            response(c);
            return;
        }
        String boundary = "wafferli_" + System.currentTimeMillis();
        JSONObject meta = new JSONObject(); meta.put("name", BACKUP_NAME); meta.put("parents", new JSONArray().put("appDataFolder"));
        String body = "--" + boundary + "\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n" + meta.toString() +
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
        String m = e.getMessage();
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
                Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT); intent.addCategory(Intent.CATEGORY_OPENABLE); intent.setType("application/json");
                intent.putExtra(Intent.EXTRA_TITLE, (defaultFileName == null || defaultFileName.trim().isEmpty()) ? BACKUP_NAME : defaultFileName);
                startActivityForResult(intent, REQ_SAVE);
            });
        }

        @JavascriptInterface public void openBudget() {
            runOnUiThread(() -> {
                Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT); intent.addCategory(Intent.CATEGORY_OPENABLE); intent.setType("application/json"); startActivityForResult(intent, REQ_OPEN);
            });
        }

        @JavascriptInterface public void toast(String message) {
            runOnUiThread(() -> Toast.makeText(MainActivity.this, message == null ? "" : message, Toast.LENGTH_SHORT).show());
        }

        @JavascriptInterface public void googleAction(String action, String payload) {
            if (action == null) return;
            switch (action) {
                case "status": sendGoogleStatus(); break;
                case "signin": startGoogleSignIn(); break;
                case "signout":
                    googlePrefs.edit().clear().apply(); sendGoogleStatus(); googleDone("signout", true, "تم تسجيل الخروج من Google"); break;
                case "backup":
                    final String content = payload == null ? "" : payload;
                    io.execute(() -> { try { uploadBackup(content); googleDone("backup", true, "تم حفظ النسخة على Google Drive"); } catch (Exception e) { googleDone("backup", false, cleanError(e)); } });
                    break;
                case "restore":
                    io.execute(() -> { try { String data = downloadBackup(); eval("window.loadBudgetFromGoogle&&window.loadBudgetFromGoogle(" + JSONObject.quote(data) + ");"); googleDone("restore", true, "تم تحميل النسخة من Google Drive"); } catch (Exception e) { googleDone("restore", false, cleanError(e)); } });
                    break;
            }
        }
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
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
                webView.evaluateJavascript("window.loadBudgetFromAndroid(" + JSONObject.quote(sb.toString()) + ");", null);
            } catch (Exception e) { Toast.makeText(this, "خطأ في فتح الملف: " + e.getMessage(), Toast.LENGTH_LONG).show(); }
        }
    }

    @Override protected void onDestroy() {
        io.shutdownNow();
        super.onDestroy();
    }
}
