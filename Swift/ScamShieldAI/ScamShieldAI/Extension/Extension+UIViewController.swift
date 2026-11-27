import UIKit

// MARK: - Alerts

extension UIViewController {

    @discardableResult
    func installAppBackground() -> SoftGradientBackgroundView {
        let backgroundView = SoftGradientBackgroundView()
        backgroundView.translatesAutoresizingMaskIntoConstraints = false
        view.insertSubview(backgroundView, at: 0)
        NSLayoutConstraint.activate([
            backgroundView.topAnchor.constraint(equalTo: view.topAnchor),
            backgroundView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            backgroundView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            backgroundView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
        return backgroundView
    }

    func showErrorAlert(title: String = L10n.text("Có lỗi xảy ra"), message: String) {
        let alert = UIAlertController(
            title: title,
            message: message,
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: L10n.text("Đã hiểu"), style: .default))
        present(alert, animated: true)
    }
}
