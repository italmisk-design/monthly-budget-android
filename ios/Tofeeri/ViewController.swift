import UIKit
import WebKit
import AuthenticationServices
import CryptoKit

final class ViewController: UIViewController, WKNavigationDelegate, WKUIDelegate, WKScriptMessageHandler, ASWebAuthenticationPresentationContextProviding {
    private var webView: WKWebView!
    private var pageLoaded = false
    private var authSession: ASWebAuthenticationSession?
    private let defaults = UserDefaults.standard
    private let backupName = "Wafferli-Backup.json"
    private let driveScope = "https://www.googleapis.com/auth/drive.appdata"

    private var googleConfig: [String: Any] {
        guard let url = Bundle.main.url(forResource: "GoogleService-Info", withExtension: "plist"),
              let data = try? Data(contentsOf: url),
              let obj = try? PropertyListSerialization.propertyList(from: data, format: nil) as? [String: Any] else { return [:] }
        return obj
    }
    private var clientID: String { googleConfig["CLIENT_ID"] as? String ?? "426484865881-u9emuf2gngkqs29quh6ulurr571kcn3k.apps.googleusercontent.com" }
    private var reversedClientID: String { googleConfig["REVERSED_CLIENT_ID"] as? String ?? "com.googleusercontent.apps.426484865881-u9emuf2gngkqs29quh6ulurr571kcn3k" }

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground

        let config = WKWebViewConfiguration()
        config.websiteDataStore = .default()
        config.preferences.javaScriptCanOpenWindowsAutomatically = true
        config.defaultWebpagePreferences.allowsContentJavaScript = true
        config.userContentController.add(self, name: "Wafferli")

        webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = self
        webView.uiDelegate = self
        webView.allowsBackForwardNavigationGestures = true
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.isOpaque = false
        webView.backgroundColor = .clear
        webView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(webView)

        NSLayoutConstraint.activate([
            webView.topAnchor.constraint(equalTo: view.topAnchor), webView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            webView.trailingAnchor.constraint(equalTo: view.trailingAnchor), webView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])

        let nested = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "WebAssets")
        let root = Bundle.main.url(forResource: "index", withExtension: "html")
        guard let indexURL = nested ?? root else { showError("تعذر تحميل ملفات وفرلي"); return }
        webView.loadFileURL(indexURL, allowingReadAccessTo: indexURL.deletingLastPathComponent())
    }

    deinit { webView?.configuration.userContentController.removeScriptMessageHandler(forName: "Wafferli") }

    override func viewSafeAreaInsetsDidChange() { super.viewSafeAreaInsetsDidChange(); applySafeAreaToWeb() }
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) { pageLoaded = true; applySafeAreaToWeb() }

    private func applySafeAreaToWeb() {
        guard pageLoaded, webView != nil else { return }
        let i = view.safeAreaInsets
        let js = "(function(){var r=document.documentElement;r.style.setProperty('--native-safe-top','\(i.top)px');r.style.setProperty('--native-safe-bottom','\(i.bottom)px');r.style.setProperty('--native-safe-left','\(i.left)px');r.style.setProperty('--native-safe-right','\(i.right)px');})();"
        webView.evaluateJavaScript(js, completionHandler: nil)
    }

    private func eval(_ js: String) { DispatchQueue.main.async { [weak self] in self?.webView?.evaluateJavaScript(js, completionHandler: nil) } }
    private func jsQuote(_ text: String) -> String { (try? String(data: JSONEncoder().encode(text), encoding: .utf8)) ?? "\"\"" }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.name == "Wafferli", let body = message.body as? [String: Any], let action = body["action"] as? String else { return }
        let payload = body["payload"] as? String ?? ""
        switch action {
        case "status": sendGoogleStatus()
        case "signin": startGoogleSignIn()
        case "signout":
            ["w_google_access","w_google_refresh","w_google_expires","w_google_email","w_google_name"].forEach { defaults.removeObject(forKey: $0) }
            sendGoogleStatus(); googleDone("signout", true, "تم تسجيل الخروج من Google")
        case "backup": uploadBackup(payload)
        case "restore": restoreBackup()
        default: break
        }
    }

    func presentationAnchor(for session: ASWebAuthenticationSession) -> ASPresentationAnchor { view.window ?? ASPresentationAnchor() }

    private func randomVerifier() -> String {
        var bytes = [UInt8](repeating: 0, count: 48)
        _ = SecRandomCopyBytes(kSecRandomDefault, bytes.count, &bytes)
        return Data(bytes).base64EncodedString().replacingOccurrences(of: "+", with: "-").replacingOccurrences(of: "/", with: "_").replacingOccurrences(of: "=", with: "")
    }
    private func pkceChallenge(_ verifier: String) -> String {
        let digest = SHA256.hash(data: verifier.data(using: .utf8)!)
        return Data(digest).base64EncodedString().replacingOccurrences(of: "+", with: "-").replacingOccurrences(of: "/", with: "_").replacingOccurrences(of: "=", with: "")
    }

    private func startGoogleSignIn() {
        let verifier = randomVerifier(), state = UUID().uuidString
        let redirect = "\(reversedClientID):/oauthredirect"
        var c = URLComponents(string: "https://accounts.google.com/o/oauth2/v2/auth")!
        c.queryItems = [
            URLQueryItem(name: "response_type", value: "code"), URLQueryItem(name: "client_id", value: clientID),
            URLQueryItem(name: "redirect_uri", value: redirect), URLQueryItem(name: "scope", value: "openid email profile \(driveScope)"),
            URLQueryItem(name: "access_type", value: "offline"), URLQueryItem(name: "prompt", value: "consent"),
            URLQueryItem(name: "code_challenge", value: pkceChallenge(verifier)), URLQueryItem(name: "code_challenge_method", value: "S256"),
            URLQueryItem(name: "state", value: state)
        ]
        let session = ASWebAuthenticationSession(url: c.url!, callbackURLScheme: reversedClientID) { [weak self] callback, error in
            guard let self = self else { return }
            if let error = error { self.googleDone("signin", false, error.localizedDescription); return }
            guard let callback = callback, let comp = URLComponents(url: callback, resolvingAgainstBaseURL: false) else { self.googleDone("signin", false, "لم يصل رد Google"); return }
            let values = Dictionary(uniqueKeysWithValues: comp.queryItems?.map { ($0.name, $0.value ?? "") } ?? [])
            guard values["state"] == state, let code = values["code"], !code.isEmpty else { self.googleDone("signin", false, values["error"] ?? "رد Google غير صالح"); return }
            self.exchangeCode(code, verifier: verifier, redirect: redirect)
        }
        session.presentationContextProvider = self
        session.prefersEphemeralWebBrowserSession = false
        authSession = session
        if !session.start() { googleDone("signin", false, "تعذر فتح تسجيل الدخول") }
    }

    private func exchangeCode(_ code: String, verifier: String, redirect: String) {
        postForm("https://oauth2.googleapis.com/token", ["code":code,"client_id":clientID,"redirect_uri":redirect,"grant_type":"authorization_code","code_verifier":verifier]) { [weak self] result in
            guard let self = self else { return }
            switch result {
            case .failure(let e): self.googleDone("signin", false, self.clean(e))
            case .success(let obj):
                self.saveTokens(obj)
                self.fetchProfile { _ in self.sendGoogleStatus(); self.googleDone("signin", true, "تم ربط حساب Google بنجاح") }
            }
        }
    }

    private func postForm(_ endpoint: String, _ fields: [String:String], completion: @escaping (Result<[String:Any],Error>) -> Void) {
        var req = URLRequest(url: URL(string: endpoint)!); req.httpMethod = "POST"; req.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        req.httpBody = fields.map { "\($0.key.urlEncoded)=\($0.value.urlEncoded)" }.joined(separator: "&").data(using: .utf8)
        URLSession.shared.dataTask(with: req) { data, resp, err in
            if let err = err { completion(.failure(err)); return }
            do { let data = data ?? Data(); try self.check(resp, data); let o = try JSONSerialization.jsonObject(with: data) as? [String:Any] ?? [:]; completion(.success(o)) }
            catch { completion(.failure(error)) }
        }.resume()
    }

    private func saveTokens(_ obj: [String:Any]) {
        if let s = obj["access_token"] as? String { defaults.set(s, forKey: "w_google_access") }
        if let s = obj["refresh_token"] as? String { defaults.set(s, forKey: "w_google_refresh") }
        let exp = (obj["expires_in"] as? NSNumber)?.doubleValue ?? 3600
        defaults.set(Date().timeIntervalSince1970 + max(60, exp - 60), forKey: "w_google_expires")
    }

    private func withAccessToken(_ completion: @escaping (Result<String,Error>) -> Void) {
        let token = defaults.string(forKey: "w_google_access") ?? ""
        if !token.isEmpty && Date().timeIntervalSince1970 < defaults.double(forKey: "w_google_expires") { completion(.success(token)); return }
        guard let refresh = defaults.string(forKey: "w_google_refresh"), !refresh.isEmpty else { completion(.failure(WError("سجّل الدخول بحساب Google أولاً"))); return }
        postForm("https://oauth2.googleapis.com/token", ["client_id":clientID,"refresh_token":refresh,"grant_type":"refresh_token"]) { result in
            switch result { case .failure(let e): completion(.failure(e)); case .success(let o): self.saveTokens(o); completion(.success(self.defaults.string(forKey: "w_google_access") ?? "")) }
        }
    }

    private func request(_ url: URL, method: String = "GET", token: String, contentType: String? = nil, body: Data? = nil, completion: @escaping (Result<Data,Error>) -> Void) {
        var req = URLRequest(url: url); req.httpMethod = method; req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        if let contentType = contentType { req.setValue(contentType, forHTTPHeaderField: "Content-Type") }; req.httpBody = body
        URLSession.shared.dataTask(with: req) { data, resp, err in
            if let err = err { completion(.failure(err)); return }
            do { let d = data ?? Data(); try self.check(resp, d); completion(.success(d)) } catch { completion(.failure(error)) }
        }.resume()
    }

    private func check(_ response: URLResponse?, _ data: Data) throws {
        guard let h = response as? HTTPURLResponse else { throw WError("لا يوجد رد من Google") }
        guard (200...299).contains(h.statusCode) else { let body = String(data: data, encoding: .utf8) ?? ""; throw WError("Google HTTP \(h.statusCode) \(String(body.prefix(250)))") }
    }

    private func fetchProfile(_ completion: @escaping (Bool)->Void) {
        withAccessToken { result in
            guard case .success(let token) = result else { completion(false); return }
            self.request(URL(string:"https://www.googleapis.com/oauth2/v3/userinfo")!, token: token) { r in
                if case .success(let data) = r, let o = try? JSONSerialization.jsonObject(with:data) as? [String:Any] {
                    self.defaults.set(o["email"] as? String ?? "", forKey:"w_google_email"); self.defaults.set(o["name"] as? String ?? "", forKey:"w_google_name"); completion(true)
                } else { completion(false) }
            }
        }
    }

    private func latestBackupID(token: String, completion: @escaping (Result<String,Error>)->Void) {
        var c = URLComponents(string:"https://www.googleapis.com/drive/v3/files")!
        c.queryItems = [URLQueryItem(name:"spaces",value:"appDataFolder"),URLQueryItem(name:"q",value:"name='\(backupName)' and trashed=false"),URLQueryItem(name:"fields",value:"files(id,name,modifiedTime)"),URLQueryItem(name:"orderBy",value:"modifiedTime desc"),URLQueryItem(name:"pageSize",value:"1")]
        request(c.url!, token: token) { r in
            switch r { case .failure(let e): completion(.failure(e)); case .success(let data):
                do { let o = try JSONSerialization.jsonObject(with:data) as? [String:Any]; let files = o?["files"] as? [[String:Any]]; completion(.success(files?.first?["id"] as? String ?? "")) } catch { completion(.failure(error)) }
            }
        }
    }

    private func uploadBackup(_ content: String) {
        withAccessToken { result in
            guard case .success(let token) = result else { if case .failure(let e)=result { self.googleDone("backup",false,self.clean(e)) }; return }
            self.latestBackupID(token: token) { idResult in
                switch idResult {
                case .failure(let e): self.googleDone("backup",false,self.clean(e))
                case .success(let id):
                    if !id.isEmpty {
                        let u = URL(string:"https://www.googleapis.com/upload/drive/v3/files/\(id)?uploadType=media")!
                        self.request(u, method:"PATCH", token:token, contentType:"application/json; charset=utf-8", body:content.data(using:.utf8)) { r in
                            switch r { case .success: self.googleDone("backup",true,"تم حفظ النسخة على Google Drive"); case .failure(let e): self.googleDone("backup",false,self.clean(e)) }
                        }
                    } else { self.createBackup(content, token: token) }
                }
            }
        }
    }

    private func createBackup(_ content:String, token:String) {
        let boundary = "wafferli_\(Int(Date().timeIntervalSince1970))"
        let meta = "{\"name\":\"\(backupName)\",\"parents\":[\"appDataFolder\"]}"
        let body = "--\(boundary)\r\nContent-Type: application/json; charset=utf-8\r\n\r\n\(meta)\r\n--\(boundary)\r\nContent-Type: application/json; charset=utf-8\r\n\r\n\(content)\r\n--\(boundary)--\r\n"
        let u = URL(string:"https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart")!
        request(u, method:"POST", token:token, contentType:"multipart/related; boundary=\(boundary)", body:body.data(using:.utf8)) { r in
            switch r { case .success: self.googleDone("backup",true,"تم حفظ النسخة على Google Drive"); case .failure(let e): self.googleDone("backup",false,self.clean(e)) }
        }
    }

    private func restoreBackup() {
        withAccessToken { result in
            guard case .success(let token)=result else { if case .failure(let e)=result { self.googleDone("restore",false,self.clean(e)) }; return }
            self.latestBackupID(token:token) { ir in
                guard case .success(let id)=ir, !id.isEmpty else { self.googleDone("restore",false,"لا توجد نسخة احتياطية على Google Drive"); return }
                self.request(URL(string:"https://www.googleapis.com/drive/v3/files/\(id)?alt=media")!, token:token) { r in
                    switch r { case .failure(let e): self.googleDone("restore",false,self.clean(e)); case .success(let data):
                        let text=String(data:data,encoding:.utf8) ?? ""; self.eval("window.loadBudgetFromGoogle&&window.loadBudgetFromGoogle(\(self.jsQuote(text)));"); self.googleDone("restore",true,"تم تحميل النسخة من Google Drive") }
                }
            }
        }
    }

    private func sendGoogleStatus() {
        let signed = !(defaults.string(forKey:"w_google_refresh") ?? "").isEmpty || !(defaults.string(forKey:"w_google_access") ?? "").isEmpty
        let o:[String:Any] = ["signedIn":signed,"email":defaults.string(forKey:"w_google_email") ?? "","name":defaults.string(forKey:"w_google_name") ?? ""]
        if let d=try? JSONSerialization.data(withJSONObject:o), let s=String(data:d,encoding:.utf8) { eval("window.wafferliGoogleStatus&&window.wafferliGoogleStatus(\(s));") }
    }
    private func googleDone(_ action:String,_ ok:Bool,_ message:String) { eval("window.wafferliGoogleDone&&window.wafferliGoogleDone(\(jsQuote(action)),\(ok ? "true":"false"),\(jsQuote(message)));") }
    private func clean(_ e:Error)->String { String(e.localizedDescription.prefix(300)) }

    func webView(_ webView: WKWebView, runJavaScriptConfirmPanelWithMessage message: String, initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping (Bool) -> Void) {
        let a=UIAlertController(title:"وفرلي",message:message,preferredStyle:.alert); a.addAction(UIAlertAction(title:"إلغاء",style:.cancel){_ in completionHandler(false)}); a.addAction(UIAlertAction(title:"موافق",style:.destructive){_ in completionHandler(true)}); present(a,animated:true)
    }

    private func showError(_ text: String) {
        let label = UILabel(); label.text=text; label.textAlignment = .center; label.numberOfLines=0; label.translatesAutoresizingMaskIntoConstraints=false; view.addSubview(label)
        NSLayoutConstraint.activate([label.centerXAnchor.constraint(equalTo:view.centerXAnchor),label.centerYAnchor.constraint(equalTo:view.centerYAnchor),label.leadingAnchor.constraint(greaterThanOrEqualTo:view.leadingAnchor,constant:24),label.trailingAnchor.constraint(lessThanOrEqualTo:view.trailingAnchor,constant:-24)])
    }
}

private struct WError: LocalizedError { let text:String; init(_ t:String){text=t}; var errorDescription:String?{text} }
private extension String { var urlEncoded:String { addingPercentEncoding(withAllowedCharacters:.urlQueryAllowed.subtracting(CharacterSet(charactersIn:"&+=?"))) ?? self } }
