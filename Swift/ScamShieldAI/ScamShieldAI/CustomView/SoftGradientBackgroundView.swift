import UIKit

final class SoftGradientBackgroundView: UIView {

    // MARK: - Layers

    private let gradientLayer = CAGradientLayer()

    // MARK: - Initialization

    override init(frame: CGRect) {
        super.init(frame: frame)
        configureGradient()
    }

    required init?(coder: NSCoder) {
        fatalError("SoftGradientBackgroundView chỉ được sử dụng bằng code.")
    }

    // MARK: - Layout

    override func traitCollectionDidChange(_ previousTraitCollection: UITraitCollection?) {
        super.traitCollectionDidChange(previousTraitCollection)
        setNeedsLayout()
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        gradientLayer.frame = bounds
        gradientLayer.colors = [AppTheme.softColor, AppTheme.pageBackgroundColor, AppTheme.pageBackgroundColor].map { $0.resolvedColor(with: traitCollection).cgColor }
    }
}

// MARK: - Setup UI

private extension SoftGradientBackgroundView {

    func configureGradient() {
        gradientLayer.colors = [
            AppTheme.softColor.cgColor,
            AppTheme.pageBackgroundColor.cgColor,
            AppTheme.pageBackgroundColor.cgColor
        ]
        gradientLayer.locations = [0, 0.58, 1]
        gradientLayer.startPoint = CGPoint(x: 0.08, y: 0)
        gradientLayer.endPoint = CGPoint(x: 0.92, y: 1)
        layer.addSublayer(gradientLayer)
    }
}
