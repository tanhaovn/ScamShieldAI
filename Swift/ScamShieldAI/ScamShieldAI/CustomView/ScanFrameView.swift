import UIKit

final class ScanFrameView: UIView {

    // MARK: - Layers

    private let corners = CAShapeLayer()
    private let beam = CAGradientLayer()
    var isScanning = false { didSet { updateAnimation() } }

    // MARK: - Initialization

    override init(frame: CGRect) {
        super.init(frame: frame)
        isUserInteractionEnabled = false
        accessibilityElementsHidden = true
        clipsToBounds = true
        layer.cornerRadius = 16
        corners.strokeColor = AppTheme.mintColor.cgColor
        corners.fillColor = UIColor.clear.cgColor
        corners.lineWidth = 2
        corners.lineCap = .round
        beam.colors = [UIColor.clear.cgColor, AppTheme.mintColor.withAlphaComponent(0.05).cgColor,
                       AppTheme.mintColor.withAlphaComponent(0.65).cgColor]
        beam.locations = [0, 0.92, 1]
        layer.addSublayer(beam)
        layer.addSublayer(corners)
        NotificationCenter.default.addObserver(self, selector: #selector(updateAnimation),
            name: UIAccessibility.reduceMotionStatusDidChangeNotification, object: nil)
    }

    required init?(coder: NSCoder) { fatalError("ScanFrameView chỉ được sử dụng bằng code.") }
    deinit { NotificationCenter.default.removeObserver(self) }

    // MARK: - Layout and Motion

    override func layoutSubviews() {
        super.layoutSubviews()
        let path = UIBezierPath()
        let inset: CGFloat = 16
        let length: CGFloat = 22
        for (x, y, dx, dy) in [(inset, inset, CGFloat(1), CGFloat(1)),
                               (bounds.width - inset, inset, -1, 1),
                               (inset, bounds.height - inset, 1, -1),
                               (bounds.width - inset, bounds.height - inset, -1, -1)] {
            path.move(to: CGPoint(x: x + length * dx, y: y))
            path.addLine(to: CGPoint(x: x, y: y))
            path.addLine(to: CGPoint(x: x, y: y + length * dy))
        }
        corners.path = path.cgPath
        beam.frame = CGRect(x: 12, y: -60, width: max(0, bounds.width - 24), height: 60)
        updateAnimation()
    }

    override func didMoveToWindow() {
        super.didMoveToWindow()
        updateAnimation()
    }

    @objc private func updateAnimation() {
        beam.removeAllAnimations()
        beam.isHidden = !isScanning || UIAccessibility.isReduceMotionEnabled
        guard isScanning, window != nil, !UIAccessibility.isReduceMotionEnabled else { return }
        let animation = CABasicAnimation(keyPath: "transform.translation.y")
        animation.fromValue = 0
        animation.toValue = bounds.height + 60
        animation.duration = 2.4
        animation.repeatCount = .infinity
        animation.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
        beam.add(animation, forKey: "scanBeam")
    }
}
