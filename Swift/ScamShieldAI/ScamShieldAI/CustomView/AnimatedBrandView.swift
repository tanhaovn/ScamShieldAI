import UIKit

/// A single brand reveal. Decorative symbols never imply background scanning.
final class AnimatedBrandView: UIView {
    private let emblem = UIImageView(image: UIImage(systemName: "checkmark.shield.fill"))
    private let wordmark = UIStackView()
    private let symbols = UIView()
    private var symbolViews: [UIImageView] = []
    private var isAnimating = false
    private var completion: (() -> Void)?

    // Keep the middle clear so the wordmark always stays readable.
    private let positions: [(String, CGFloat, CGFloat, CGFloat, CGFloat)] = [
        ("lock.fill", -0.27, -0.33, 25, -0.25),
        ("link", 0.06, -0.40, 30, 0.30),
        ("qrcode", 0.34, -0.25, 28, 0.18),
        ("text.bubble.fill", -0.40, -0.13, 25, -0.20),
        ("envelope.fill", 0.40, 0.03, 23, 0.28),
        ("doc.text.fill", -0.33, 0.25, 29, -0.32),
        ("photo.fill", 0.04, 0.34, 27, 0.20),
        ("checkmark.seal.fill", 0.32, 0.24, 27, 0.18),
        ("sparkle", -0.12, -0.22, 13, 0),
        ("sparkle", 0.23, -0.42, 11, 0),
        ("circle.fill", -0.43, 0.12, 6, 0),
        ("circle.fill", -0.14, 0.39, 6, 0)
    ]

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
    }

    required init?(coder: NSCoder) { fatalError("Use init(frame:)") }

    override func layoutSubviews() {
        super.layoutSubviews()
        symbols.bounds = bounds
        symbols.center = CGPoint(x: bounds.midX, y: bounds.midY)
        let extent = min(bounds.width, bounds.height)
        for (icon, item) in zip(symbolViews, positions) {
            icon.bounds = CGRect(x: 0, y: 0, width: item.3 + 10, height: item.3 + 10)
            icon.center = CGPoint(x: bounds.midX + item.1 * extent,
                                  y: bounds.midY + item.2 * extent)
        }
    }

    func startAnimating(completion: @escaping () -> Void) {
        guard !isAnimating else { return }
        isAnimating = true
        self.completion = completion
        guard !UIAccessibility.isReduceMotionEnabled else {
            // No scale, spin, or burst when motion is reduced.
            UIView.animate(withDuration: 0.15, animations: { self.emblem.alpha = 0.85 }) { [weak self] _ in
                self?.complete()
            }
            return
        }

        UIView.animateKeyframes(withDuration: 1.35, delay: 0,
                                options: [.calculationModeCubic, .beginFromCurrentState]) {
            UIView.addKeyframe(withRelativeStartTime: 0, relativeDuration: 0.20) {
                self.emblem.transform = CGAffineTransform(scaleX: 0.78, y: 0.78)
            }
            UIView.addKeyframe(withRelativeStartTime: 0.18, relativeDuration: 0.18) {
                self.emblem.alpha = 0
                self.emblem.transform = CGAffineTransform(scaleX: 0.55, y: 0.55)
            }
            UIView.addKeyframe(withRelativeStartTime: 0.22, relativeDuration: 0.33) {
                self.wordmark.alpha = 1
                self.wordmark.transform = .identity
                self.symbols.alpha = 1
                self.symbols.transform = CGAffineTransform(scaleX: 1.06, y: 1.06)
            }
            UIView.addKeyframe(withRelativeStartTime: 0.55, relativeDuration: 0.22) {
                self.symbols.transform = CGAffineTransform(rotationAngle: 0.045)
            }
            UIView.addKeyframe(withRelativeStartTime: 0.80, relativeDuration: 0.20) {
                self.symbols.alpha = 0
                self.symbols.transform = CGAffineTransform(scaleX: 0.5, y: 0.5)
                self.wordmark.transform = CGAffineTransform(scaleX: 0.85, y: 0.85)
            }
        } completion: { [weak self] _ in
            self?.complete()
        }
    }

    func stopAnimating() {
        completion = nil
        isAnimating = false
        [self, emblem, wordmark, symbols].forEach { $0.layer.removeAllAnimations() }
    }

    private func complete() {
        guard isAnimating else { return }
        isAnimating = false
        let callback = completion
        completion = nil
        callback?()
    }

    private func setupUI() {
        isUserInteractionEnabled = false
        accessibilityElementsHidden = true
        addSubview(symbols)
        symbols.alpha = 0
        symbols.transform = CGAffineTransform(scaleX: 0.35, y: 0.35)
        for item in positions {
            let icon = UIImageView(image: UIImage(systemName: item.0))
            icon.contentMode = .center
            icon.preferredSymbolConfiguration = .init(pointSize: item.3, weight: .medium)
            icon.tintColor = AppTheme.mintColor.withAlphaComponent(0.22)
            icon.transform = CGAffineTransform(rotationAngle: item.4)
            symbols.addSubview(icon)
            symbolViews.append(icon)
        }

        emblem.tintColor = .white
        emblem.contentMode = .scaleAspectFit
        emblem.translatesAutoresizingMaskIntoConstraints = false
        addSubview(emblem)

        let title = UILabel()
        title.text = "ScamShield AI"
        title.font = .systemFont(ofSize: 34, weight: .bold)
        title.textColor = .white
        title.textAlignment = .center
        title.adjustsFontSizeToFitWidth = true
        title.minimumScaleFactor = 0.65
        let accent = UIView()
        accent.backgroundColor = AppTheme.mintColor
        accent.layer.cornerRadius = 2
        wordmark.axis = .vertical
        wordmark.alignment = .center
        wordmark.spacing = 12
        wordmark.addArrangedSubview(title)
        wordmark.addArrangedSubview(accent)
        wordmark.translatesAutoresizingMaskIntoConstraints = false
        wordmark.alpha = 0
        wordmark.transform = CGAffineTransform(scaleX: 0.65, y: 0.65)
        addSubview(wordmark)
        NSLayoutConstraint.activate([
            emblem.widthAnchor.constraint(equalToConstant: 64),
            emblem.heightAnchor.constraint(equalToConstant: 64),
            emblem.centerXAnchor.constraint(equalTo: centerXAnchor),
            emblem.centerYAnchor.constraint(equalTo: centerYAnchor),
            wordmark.centerXAnchor.constraint(equalTo: centerXAnchor),
            wordmark.centerYAnchor.constraint(equalTo: centerYAnchor),
            wordmark.widthAnchor.constraint(equalTo: widthAnchor, constant: -24),
            title.widthAnchor.constraint(equalTo: wordmark.widthAnchor),
            accent.widthAnchor.constraint(equalToConstant: 44),
            accent.heightAnchor.constraint(equalToConstant: 4)
        ])
    }
}
