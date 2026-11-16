import UIKit

final class AppCoordinator {

    // MARK: - Dependencies

    private let window: UIWindow

    init(window: UIWindow) {
        self.window = window
    }

    // MARK: - Navigation

    func start() {
        UserDefaults.standard.removeObject(forKey: "scamShield.authToken")
        window.tintColor = AppTheme.primaryColor
        window.overrideUserInterfaceStyle = AppearanceSettings.style
        let introduction = LoadingViewController()
        introduction.onFinish = { [weak self, weak introduction] in
            guard let self, let introduction,
                  window.rootViewController === introduction else { return }
            showMainInterface()
        }
        window.rootViewController = introduction
        window.makeKeyAndVisible()
    }

    private func showMainInterface() {
        let main = MainTabBarController(user: .guest)
        guard UIApplication.shared.applicationState == .active else {
            window.rootViewController = main
            return
        }
        UIView.transition(with: window,
                          duration: UIAccessibility.isReduceMotionEnabled ? 0.15 : 0.22,
                          options: [.transitionCrossDissolve, .allowAnimatedContent]) {
            self.window.rootViewController = main
        }
    }
}
