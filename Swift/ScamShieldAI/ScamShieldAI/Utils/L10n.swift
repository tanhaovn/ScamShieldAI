import Foundation

enum L10n {
    static var language: String { UserDefaults.standard.string(forKey: "scamShield.language") ?? "vi" }
    static let didChange = Notification.Name("scamShield.languageChanged")
    static func text(_ vietnamese: String) -> String {
        guard language == "en", let path = Bundle.main.path(forResource: "en", ofType: "lproj"),
              let bundle = Bundle(path: path) else { return vietnamese }
        return bundle.localizedString(forKey: vietnamese, value: vietnamese, table: nil)
    }
    static func choose(_ vietnamese: String, _ english: String) -> String {
        language == "en" ? english : vietnamese
    }
    static func setLanguage(_ value: String) {
        guard ["vi", "en"].contains(value), value != language else { return }
        UserDefaults.standard.set(value, forKey: "scamShield.language")
        NotificationCenter.default.post(name: didChange, object: nil)
    }
}
