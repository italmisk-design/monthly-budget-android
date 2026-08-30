from pathlib import Path

p=Path('ios/Tofeeri/ViewController.swift')
s=p.read_text(encoding='utf-8')

if 'import UniformTypeIdentifiers' not in s:
    s=s.replace('import CryptoKit\n','import CryptoKit\nimport UniformTypeIdentifiers\n',1)

if 'UIDocumentPickerDelegate' not in s.split('{',1)[0]:
    s=s.replace('ASWebAuthenticationPresentationContextProviding {','ASWebAuthenticationPresentationContextProviding, UIDocumentPickerDelegate {',1)

if 'private var exportTempURL:' not in s:
    s=s.replace('    private let driveScope = "https://www.googleapis.com/auth/drive.appdata"\n','    private let driveScope = "https://www.googleapis.com/auth/drive.appdata"\n    private var exportTempURL: URL?\n',1)

old='''        case "backup": uploadBackup(payload)\n        case "restore": restoreBackup()\n        default: break\n'''
new='''        case "backup": uploadBackup(payload)\n        case "restore": restoreBackup()\n        case "savefile": exportLocalBackup(payload, filename: body["filename"] as? String ?? "Wafferli-Backup.json")\n        case "openfile": importLocalBackup()\n        default: break\n'''
if 'case "savefile"' not in s:
    if old not in s: raise SystemExit('message switch marker missing')
    s=s.replace(old,new,1)

if 'private func exportLocalBackup' not in s:
    marker='    func presentationAnchor(for session: ASWebAuthenticationSession) -> ASPresentationAnchor { view.window ?? ASPresentationAnchor() }\n'
    block='''    func presentationAnchor(for session: ASWebAuthenticationSession) -> ASPresentationAnchor { view.window ?? ASPresentationAnchor() }\n\n    private func exportLocalBackup(_ content: String, filename: String) {\n        DispatchQueue.main.async {\n            do {\n                let safeName = filename.isEmpty ? "Wafferli-Backup.json" : filename\n                let url = FileManager.default.temporaryDirectory.appendingPathComponent(safeName)\n                guard let data = content.data(using: .utf8) else { throw WError("invalid data") }\n                try data.write(to: url, options: .atomic)\n                self.exportTempURL = url\n                let picker = UIDocumentPickerViewController(forExporting: [url], asCopy: true)\n                picker.delegate = self\n                self.present(picker, animated: true)\n            } catch { self.showToast("تعذر تصدير النسخة") }\n        }\n    }\n\n    private func importLocalBackup() {\n        DispatchQueue.main.async {\n            let picker = UIDocumentPickerViewController(forOpeningContentTypes: [UTType.json, UTType.data], asCopy: true)\n            picker.delegate = self\n            self.present(picker, animated: true)\n        }\n    }\n\n    func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {\n        guard controller.documentPickerMode == .open, let url = urls.first else { return }\n        do {\n            let text = try String(contentsOf: url, encoding: .utf8)\n            eval("window.loadBudgetFromNative&&window.loadBudgetFromNative(\\(jsQuote(text)));")\n        } catch { showToast("تعذر فتح ملف النسخة الاحتياطية") }\n    }\n\n    func documentPickerWasCancelled(_ controller: UIDocumentPickerViewController) { }\n\n    private func showToast(_ text: String) {\n        DispatchQueue.main.async {\n            let alert = UIAlertController(title: nil, message: text, preferredStyle: .alert)\n            self.present(alert, animated: true)\n            DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) { alert.dismiss(animated: true) }\n        }\n    }\n'''
    if marker not in s: raise SystemExit('presentation anchor marker missing')
    s=s.replace(marker,block,1)

p.write_text(s,encoding='utf-8')
print('iOS native backup picker patch applied')
