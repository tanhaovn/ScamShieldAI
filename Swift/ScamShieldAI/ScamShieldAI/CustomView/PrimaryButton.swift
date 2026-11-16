import UIKit

final class PrimaryButton: UIButton {

    // MARK: - UI Components

    private let activityIndicator = UIActivityIndicatorView(style: .medium)

    // MARK: - Properties

    private var normalTitle: String?
    private var enabledBeforeLoading = true

    var isLoading = false {
        didSet {
            guard oldValue != isLoading else { return }
            if isLoading { enabledBeforeLoading = isEnabled }
            updateLoadingState()
        }
    }

    // MARK: - Initialization

    override init(frame: CGRect) {
        super.init(frame: frame)
        configureAppearance()
    }

    required init?(coder: NSCoder) {
        fatalError("PrimaryButton chỉ được sử dụng bằng code.")
    }

    // MARK: - Configuration

    func setPrimaryTitle(_ title: String) {
        normalTitle = title
        setTitle(isLoading ? nil : title, for: .normal)
        accessibilityLabel = title
    }
}

// MARK: - Setup UI

private extension PrimaryButton {

    func configureAppearance() {
        translatesAutoresizingMaskIntoConstraints = false
        backgroundColor = AppTheme.brandDark
        setTitleColor(.white, for: .normal)
        titleLabel?.font = UIFontMetrics(forTextStyle: .headline).scaledFont(for: .systemFont(ofSize: 16, weight: .bold))
        titleLabel?.adjustsFontForContentSizeCategory = true
        titleLabel?.numberOfLines = 0
        titleLabel?.textAlignment = .center
        titleLabel?.minimumScaleFactor = 0.85
        layer.cornerRadius = 28
        layer.cornerCurve = .continuous
        layer.shadowColor = AppTheme.brandDeep.cgColor
        layer.shadowOpacity = 0
        layer.shadowRadius = 12
        layer.shadowOffset = CGSize(width: 0, height: 5)

        addTarget(self, action: #selector(animatePressDown), for: .touchDown)
        addTarget(
            self,
            action: #selector(animatePressUp),
            for: [.touchUpInside, .touchUpOutside, .touchCancel, .touchDragExit]
        )

        activityIndicator.color = .white
        activityIndicator.hidesWhenStopped = true
        activityIndicator.translatesAutoresizingMaskIntoConstraints = false
        addSubview(activityIndicator)

        NSLayoutConstraint.activate([
            heightAnchor.constraint(greaterThanOrEqualToConstant: 56),
            activityIndicator.centerXAnchor.constraint(equalTo: centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: centerYAnchor)
        ])
    }

    func updateLoadingState() {
        isEnabled = isLoading ? false : enabledBeforeLoading
        transform = .identity
        accessibilityValue = isLoading ? "Đang xử lý" : nil
        setTitle(isLoading ? nil : normalTitle, for: .normal)

        if isLoading {
            activityIndicator.startAnimating()
        } else {
            activityIndicator.stopAnimating()
        }
    }

    @objc func animatePressDown() {
        guard !UIAccessibility.isReduceMotionEnabled else { return }
        UIView.animate(withDuration: 0.1, delay: 0, options: [.allowUserInteraction]) {
            self.transform = CGAffineTransform(scaleX: 0.985, y: 0.985)
        }
    }

    @objc func animatePressUp() {
        guard !UIAccessibility.isReduceMotionEnabled else { return }
        UIView.animate(
            withDuration: 0.18,
            delay: 0,
            options: [.curveEaseOut, .allowUserInteraction, .beginFromCurrentState]
        ) {
            self.transform = .identity
        }
    }
}
