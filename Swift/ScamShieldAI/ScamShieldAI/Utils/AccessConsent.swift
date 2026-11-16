import UIKit
import UserNotifications

/// Pickers grant access only to the items explicitly selected by the user.
@MainActor
enum AccessConsent {
    static func confirm(on controller: UIViewController, title: String, message: String, proceed: @escaping () -> Void) {
        guard controller.presentedViewController == nil else { return }
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "Để sau", style: .cancel))
        alert.addAction(UIAlertAction(title: "Tiếp tục", style: .default) { _ in proceed() })
        controller.present(alert, animated: true)
    }

    static func notifications(on controller: UIViewController) {
        Task { @MainActor [weak controller] in
            let center = UNUserNotificationCenter.current()
            let settings = await center.notificationSettings()
            guard let controller else { return }
            switch settings.authorizationStatus {
            case .notDetermined:
                confirm(on: controller, title: "Cho phép thông báo?", message: "Bạn quyết định có nhận thông báo từ ScamShield hay không. Có thể thay đổi trong Cài đặt bất cứ lúc nào.") {
                    Task { @MainActor [weak controller] in
                        do {
                            let granted = try await center.requestAuthorization(options: [.alert, .sound, .badge])
                            controller?.showErrorAlert(title: "Quyền thông báo", message: granted ? "Đã cho phép thông báo." : "Thông báo chưa được cho phép. Bạn vẫn dùng được các chức năng kiểm tra.")
                        } catch {
                            controller?.showErrorAlert(message: "Chưa thể xin quyền thông báo. Vui lòng thử lại.")
                        }
                    }
                }
            default:
                confirm(on: controller, title: "Cài đặt thông báo", message: "Mở Cài đặt để xem hoặc thay đổi quyền thông báo của ScamShield.") {
                    if let url = URL(string: UIApplication.openSettingsURLString) { UIApplication.shared.open(url) }
                }
            }
        }
    }
}
