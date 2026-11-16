import UIKit

/// A brief, local-only introduction shown once when a scene is created.
final class LoadingViewController: UIViewController {
    var onFinish: (() -> Void)?
    private let brandView = AnimatedBrandView()
    private var hasStarted = false
    private var hasFinished = false

    override var preferredStatusBarStyle: UIStatusBarStyle { .lightContent }

    override func viewDidLoad() {
        super.viewDidLoad()
        // Matches LaunchScreen exactly to avoid a light flash on cold launch.
        view.backgroundColor = AppTheme.brandDark
        view.accessibilityLabel = "ScamShield AI"
        view.accessibilityIdentifier = "launch.introduction"
        brandView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(brandView)
        let preferredWidth = brandView.widthAnchor.constraint(equalTo: view.widthAnchor, multiplier: 0.9)
        preferredWidth.priority = .defaultHigh
        NSLayoutConstraint.activate([
            preferredWidth,
            brandView.widthAnchor.constraint(lessThanOrEqualToConstant: 390),
            brandView.heightAnchor.constraint(equalTo: brandView.widthAnchor),
            brandView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            brandView.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
        NotificationCenter.default.addObserver(self, selector: #selector(finish),
            name: UIApplication.willResignActiveNotification, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(reduceMotionChanged),
            name: UIAccessibility.reduceMotionStatusDidChangeNotification, object: nil)
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        guard !hasStarted, !hasFinished else { return }
        hasStarted = true
        brandView.startAnimating { [weak self] in self?.finish() }
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        brandView.stopAnimating()
    }

    deinit { NotificationCenter.default.removeObserver(self) }

    @objc private func reduceMotionChanged() {
        if UIAccessibility.isReduceMotionEnabled { finish() }
    }

    @objc private func finish() {
        guard !hasFinished else { return }
        hasFinished = true
        brandView.stopAnimating()
        let callback = onFinish
        onFinish = nil
        callback?()
    }
}
