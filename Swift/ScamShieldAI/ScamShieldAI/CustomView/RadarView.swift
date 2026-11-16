import UIKit

/// Radar trang trí dùng chung cho các màn hình, tự dừng khi rời cửa sổ.
final class RadarView: UIView {

    // MARK: - Layers

    private let gridLayer = CAShapeLayer()
    private let ringsLayer = CAShapeLayer()
    private let sweepLayer = CAGradientLayer()
    private let sweepMask = CAShapeLayer()
    private let coreLayer = CAShapeLayer()
    private let dotLayers = (0..<3).map { _ in CAShapeLayer() }
    private let shieldView = UIImageView(image: UIImage(systemName: "checkmark.shield.fill"))

    var showsCenterIcon = true { didSet { shieldView.isHidden = !showsCenterIcon } }

    // MARK: - Initialization

    override init(frame: CGRect) {
        super.init(frame: frame)
        isUserInteractionEnabled = false
        accessibilityElementsHidden = true
        configureLayers()
        NotificationCenter.default.addObserver(
            self, selector: #selector(updateMotion),
            name: UIAccessibility.reduceMotionStatusDidChangeNotification, object: nil
        )
        NotificationCenter.default.addObserver(
            self, selector: #selector(updateMotion),
            name: UIApplication.didBecomeActiveNotification, object: nil
        )
        NotificationCenter.default.addObserver(
            self, selector: #selector(stopMotion),
            name: UIApplication.willResignActiveNotification, object: nil
        )
    }

    required init?(coder: NSCoder) {
        fatalError("RadarView chỉ được khởi tạo bằng code.")
    }

    deinit {
        NotificationCenter.default.removeObserver(self)
    }

    // MARK: - Lifecycle

    override func didMoveToWindow() {
        super.didMoveToWindow()
        updateMotion()
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        // Tắt implicit animation khi Auto Layout đổi kích thước radar.
        CATransaction.begin()
        CATransaction.setDisableActions(true)
        let size = min(bounds.width, bounds.height)
        let circle = CGRect(x: bounds.midX - size / 2 + 4, y: bounds.midY - size / 2 + 4,
                            width: max(0, size - 8), height: max(0, size - 8))
        let grid = UIBezierPath()
        for index in 1...5 {
            let offset = CGFloat(index) / 6
            grid.move(to: CGPoint(x: circle.minX + circle.width * offset, y: circle.minY))
            grid.addLine(to: CGPoint(x: circle.minX + circle.width * offset, y: circle.maxY))
            grid.move(to: CGPoint(x: circle.minX, y: circle.minY + circle.height * offset))
            grid.addLine(to: CGPoint(x: circle.maxX, y: circle.minY + circle.height * offset))
        }
        gridLayer.path = grid.cgPath
        let rings = UIBezierPath()
        for inset in [CGFloat(0), 0.16, 0.32] {
            rings.append(UIBezierPath(ovalIn: circle.insetBy(dx: circle.width * inset, dy: circle.height * inset)))
        }
        ringsLayer.path = rings.cgPath
        sweepLayer.bounds = CGRect(origin: .zero, size: circle.size)
        sweepLayer.position = CGPoint(x: bounds.midX, y: bounds.midY)
        sweepMask.path = UIBezierPath(ovalIn: sweepLayer.bounds).cgPath
        coreLayer.path = UIBezierPath(ovalIn: circle.insetBy(dx: circle.width * 0.34, dy: circle.height * 0.34)).cgPath
        shieldView.frame = CGRect(x: bounds.midX - size * 0.09, y: bounds.midY - size * 0.11,
                                  width: size * 0.18, height: size * 0.22)
        let points: [(CGFloat, CGFloat)] = [(0.72, 0.25), (0.21, 0.54), (0.64, 0.81)]
        for (index, point) in points.enumerated() {
            let center = CGPoint(x: circle.minX + circle.width * point.0,
                                 y: circle.minY + circle.height * point.1)
            dotLayers[index].path = UIBezierPath(ovalIn: CGRect(x: center.x - 3, y: center.y - 3, width: 6, height: 6)).cgPath
        }
        CATransaction.commit()
    }
}

// MARK: - Appearance and Motion

private extension RadarView {

    func configureLayers() {
        gridLayer.strokeColor = AppTheme.mintColor.withAlphaComponent(0.09).cgColor
        gridLayer.lineWidth = 0.5
        ringsLayer.strokeColor = AppTheme.mintColor.withAlphaComponent(0.3).cgColor
        ringsLayer.lineWidth = 1
        ringsLayer.fillColor = UIColor.clear.cgColor
        sweepLayer.type = .conic
        sweepLayer.startPoint = CGPoint(x: 0.5, y: 0.5)
        sweepLayer.endPoint = CGPoint(x: 0.5, y: 0)
        sweepLayer.colors = [UIColor.clear.cgColor, UIColor.clear.cgColor,
                             AppTheme.mintColor.withAlphaComponent(0.28).cgColor, UIColor.clear.cgColor]
        sweepLayer.locations = [0, 0.68, 0.99, 1]
        sweepLayer.mask = sweepMask
        coreLayer.fillColor = AppTheme.brandDeep.cgColor
        coreLayer.strokeColor = AppTheme.mintColor.withAlphaComponent(0.45).cgColor
        [gridLayer, sweepLayer, ringsLayer, coreLayer].forEach(layer.addSublayer)
        for dot in dotLayers {
            dot.fillColor = AppTheme.mintColor.cgColor
            dot.shadowColor = AppTheme.mintColor.cgColor
            dot.shadowOpacity = 0.7
            dot.shadowRadius = 5
            dot.shadowOffset = .zero
            layer.addSublayer(dot)
        }
        shieldView.tintColor = AppTheme.mintColor
        shieldView.contentMode = .scaleAspectFit
        addSubview(shieldView)
    }

    @objc func updateMotion() {
        stopMotion()
        guard window != nil, !UIAccessibility.isReduceMotionEnabled,
              UIApplication.shared.applicationState != .background else { return }
        let rotation = CABasicAnimation(keyPath: "transform.rotation.z")
        rotation.fromValue = 0
        rotation.toValue = Double.pi * 2
        rotation.duration = 9
        rotation.repeatCount = .infinity
        sweepLayer.add(rotation, forKey: "radarSweep")
        for (index, dot) in dotLayers.enumerated() {
            let pulse = CABasicAnimation(keyPath: "opacity")
            pulse.fromValue = 0.35
            pulse.toValue = 1
            pulse.duration = 1.3
            pulse.autoreverses = true
            pulse.repeatCount = .infinity
            pulse.beginTime = CACurrentMediaTime() + Double(index) * 0.45
            dot.add(pulse, forKey: "signalPulse")
        }
    }

    @objc func stopMotion() {
        sweepLayer.removeAllAnimations()
        dotLayers.forEach { $0.removeAllAnimations() }
    }
}
