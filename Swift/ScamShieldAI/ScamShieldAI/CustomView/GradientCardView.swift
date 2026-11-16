import UIKit

final class GradientCardView: CardView {

    // MARK: - Layers

    private let gradientLayer = CAGradientLayer()
    private let contourLayer = CAShapeLayer()
    private let signalLayer = CAGradientLayer()

    // MARK: - Initialization

    init(colors: [UIColor]) {
        super.init(frame: .zero)
        configureGradient(colors: colors)
        NotificationCenter.default.addObserver(self, selector: #selector(updateMotion), name: UIAccessibility.reduceMotionStatusDidChangeNotification, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(updateMotion), name: UIApplication.didBecomeActiveNotification, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(stopMotion), name: UIApplication.willResignActiveNotification, object: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("GradientCardView chỉ được sử dụng bằng code.")
    }

    override func didMoveToWindow() {
        super.didMoveToWindow()
        updateMotion()
    }

    @objc private func updateMotion() {
        guard window != nil, UIApplication.shared.applicationState == .active,
              !UIAccessibility.isReduceMotionEnabled, bounds.width > 0 else { stopMotion(); return }
        guard signalLayer.animation(forKey: "signal") == nil else { return }
        let animation = CABasicAnimation(keyPath: "position.x")
        animation.fromValue = -70
        animation.toValue = bounds.width + 70
        animation.duration = 6
        animation.repeatCount = .infinity
        signalLayer.add(animation, forKey: "signal")
    }

    @objc private func stopMotion() { signalLayer.removeAllAnimations() }

    // MARK: - Layout

    override func layoutSubviews() {
        super.layoutSubviews()
        gradientLayer.frame = bounds
        let path = UIBezierPath()
        // Broad arcs leave the text area calm while adding depth to the surface.
        let center = CGPoint(x: bounds.width + 35, y: bounds.height * 0.32)
        for radius: CGFloat in [90, 125, 160, 195, 230] {
            path.append(UIBezierPath(arcCenter: center, radius: radius, startAngle: 0, endAngle: .pi * 2, clockwise: true))
        }
        contourLayer.frame = bounds
        contourLayer.path = path.cgPath
        signalLayer.bounds = CGRect(x: 0, y: 0, width: 90, height: 2)
        signalLayer.position = CGPoint(x: -70, y: 1)
        updateMotion()
        layer.shadowPath = UIBezierPath(roundedRect: bounds, cornerRadius: layer.cornerRadius).cgPath
    }
}

// MARK: - Setup UI

private extension GradientCardView {

    func configureGradient(colors: [UIColor]) {
        backgroundColor = .clear
        layer.borderWidth = 0
        layer.masksToBounds = false

        gradientLayer.colors = colors.map(\.cgColor)
        gradientLayer.startPoint = CGPoint(x: 0, y: 0)
        gradientLayer.endPoint = CGPoint(x: 1, y: 1)
        gradientLayer.cornerRadius = layer.cornerRadius
        gradientLayer.cornerCurve = .continuous
        layer.insertSublayer(gradientLayer, at: 0)
        contourLayer.strokeColor = UIColor.white.withAlphaComponent(0.07).cgColor
        contourLayer.fillColor = UIColor.clear.cgColor
        contourLayer.lineWidth = 1
        gradientLayer.addSublayer(contourLayer)
        gradientLayer.masksToBounds = true
        signalLayer.colors = [UIColor.clear.cgColor, AppTheme.mintColor.withAlphaComponent(0.65).cgColor, UIColor.clear.cgColor]
        signalLayer.startPoint = CGPoint(x: 0, y: 0.5)
        signalLayer.endPoint = CGPoint(x: 1, y: 0.5)
        gradientLayer.addSublayer(signalLayer)
    }
}
