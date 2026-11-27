import UIKit

/// A compact score ring. Its caller drives the same count-up for the number and the arc.
final class RiskScoreView: UIView {
    private let trackLayer = CAShapeLayer()
    private let progressLayer = CAShapeLayer()
    private let scoreLabel = UILabel()
    private var tint = AppTheme.safeColor

    override init(frame: CGRect) {
        super.init(frame: frame)
        isAccessibilityElement = true

        for ring in [trackLayer, progressLayer] {
            ring.fillColor = UIColor.clear.cgColor
            ring.lineWidth = 6
            ring.lineCap = .round
            layer.addSublayer(ring)
        }
        scoreLabel.font = .monospacedDigitSystemFont(ofSize: 29, weight: .bold)
        scoreLabel.textAlignment = .center
        scoreLabel.isAccessibilityElement = false

        let denominator = UILabel()
        denominator.text = "/100"
        denominator.font = .monospacedDigitSystemFont(ofSize: 11, weight: .medium)
        denominator.textAlignment = .center
        denominator.textColor = AppTheme.secondaryTextColor
        denominator.isAccessibilityElement = false

        let stack = UIStackView(arrangedSubviews: [scoreLabel, denominator])
        stack.axis = .vertical
        stack.spacing = -2
        stack.translatesAutoresizingMaskIntoConstraints = false
        addSubview(stack)
        NSLayoutConstraint.activate([
            widthAnchor.constraint(equalToConstant: 96),
            heightAnchor.constraint(equalTo: widthAnchor),
            stack.centerXAnchor.constraint(equalTo: centerXAnchor),
            stack.centerYAnchor.constraint(equalTo: centerYAnchor)
        ])
        registerForTraitChanges([UITraitUserInterfaceStyle.self]) { (view: RiskScoreView, _) in
            view.updateColors()
        }
    }

    required init?(coder: NSCoder) {
        fatalError("Use init(frame:)")
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        let path = UIBezierPath(
            arcCenter: CGPoint(x: bounds.midX, y: bounds.midY),
            radius: max(0, min(bounds.width, bounds.height) / 2 - 5),
            startAngle: -.pi / 2,
            endAngle: .pi * 1.5,
            clockwise: true
        )
        trackLayer.path = path.cgPath
        progressLayer.path = path.cgPath
    }

    func configure(level: RiskLevel, finalScore: Int) {
        tint = AppTheme.color(for: level)
        updateColors()
        accessibilityLabel = L10n.choose("Điểm rủi ro: \(finalScore) trên 100", "Risk score: \(finalScore) out of 100")
    }

    func display(score: Int, progress: Float) {
        scoreLabel.text = "\(score)"
        CATransaction.begin()
        CATransaction.setDisableActions(true)
        progressLayer.strokeEnd = CGFloat(progress)
        CATransaction.commit()
    }

    private func updateColors() {
        let resolved = tint.resolvedColor(with: traitCollection)
        scoreLabel.textColor = tint
        trackLayer.strokeColor = resolved.withAlphaComponent(0.17).cgColor
        progressLayer.strokeColor = resolved.cgColor
    }
}
