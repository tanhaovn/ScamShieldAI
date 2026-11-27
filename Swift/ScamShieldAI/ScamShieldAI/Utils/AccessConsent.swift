import UIKit

/// Pickers grant access only to the items explicitly selected by the user.
@MainActor
enum AccessConsent {
    static func confirm(on controller: UIViewController, title: String, message: String, proceed: @escaping () -> Void) {
        guard controller.presentedViewController == nil else { return }
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: L10n.text("Để sau"), style: .cancel))
        alert.addAction(UIAlertAction(title: L10n.text("Tiếp tục"), style: .default) { _ in proceed() })
        controller.present(alert, animated: true)
    }
}
