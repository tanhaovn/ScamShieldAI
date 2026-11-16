import UIKit

final class RiskScoreView: UIView {

    // MARK: - Layers

    private let trackLayer = CAShapeLayer()
    private let progressLayer = CAShapeLayer()

    // MARK: - UI Components

    private let scoreLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 34, weight: .bold)
        label.textColor = AppTheme.titleColor
        label.textAlignment = .center
        return label
    }()

    private let captionLabel: UILabel = {
        let label = UILabel()
        label.text = "ĐIỂM RỦI RO"
        label.font = .systemFont(ofSize: 10, weight: .semibold)
        label.textColor = AppTheme.secondaryTextColor
        label.textAlignment = .center
        return label
    }()

    // MARK: - Initialization

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
    }

    required init?(coder: NSCoder) {
        fatalError("RiskScoreView chỉ được sử dụng bằng code.")
    }

    // MARK: - Layout

    override func layoutSubviews() {
        super.layoutSubviews()

        let center = CGPoint(x: bounds.midX, y: bounds.midY)
        let radius = max(0, min(bounds.width, bounds.height) / 2 - 8)
        let path = UIBezierPath(
            arcCenter: center,
            radius: radius,
            startAngle: -.pi / 2,
            endAngle: .pi * 1.5,
            clockwise: true
        )
        trackLayer.path = path.cgPath
        progressLayer.path = path.cgPath
    }

    // MARK: - Configuration

    func configure(score: Int, level: RiskLevel) {
        let normalizedScore = min(max(score, 0), 100)
        let targetProgress = CGFloat(normalizedScore) / 100
        scoreLabel.text = "\(normalizedScore)"
        progressLayer.strokeColor = AppTheme.color(for: level).cgColor
        progressLayer.strokeEnd = targetProgress

        let animation = CABasicAnimation(keyPath: "strokeEnd")
        animation.fromValue = 0
        animation.toValue = targetProgress
        animation.duration = 0.9
        animation.timingFunction = CAMediaTimingFunction(name: .easeOut)
        progressLayer.add(animation, forKey: "scoreProgress")
        accessibilityLabel = "Điểm rủi ro \(normalizedScore) trên 100"
    }
}

// MARK: - Setup UI

private extension RiskScoreView {

    func setupUI() {
        translatesAutoresizingMaskIntoConstraints = false

        [trackLayer, progressLayer].forEach {
            $0.fillColor = UIColor.clear.cgColor
            $0.lineWidth = 10
            $0.lineCap = .round
            layer.addSublayer($0)
        }
        trackLayer.strokeColor = AppTheme.borderColor.cgColor

        let stackView = UIStackView(arrangedSubviews: [scoreLabel, captionLabel])
        stackView.axis = .vertical
        stackView.alignment = .fill
        stackView.spacing = -2
        stackView.translatesAutoresizingMaskIntoConstraints = false
        addSubview(stackView)

        NSLayoutConstraint.activate([
            widthAnchor.constraint(equalToConstant: 142),
            heightAnchor.constraint(equalToConstant: 142),
            stackView.centerXAnchor.constraint(equalTo: centerXAnchor),
            stackView.centerYAnchor.constraint(equalTo: centerYAnchor)
        ])
    }
}
