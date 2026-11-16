import UIKit

enum AppearanceSettings {
    static var selection: Int { UserDefaults.standard.integer(forKey: "scamShield.appearance") }
    static var style: UIUserInterfaceStyle {
        switch selection {
        case 1: return .light
        case 2: return .dark
        default: return .unspecified
        }
    }
    static func apply(_ index: Int) {
        UserDefaults.standard.set(index, forKey: "scamShield.appearance")
        UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }
            .flatMap(\.windows).forEach { $0.overrideUserInterfaceStyle = style }
    }
}
