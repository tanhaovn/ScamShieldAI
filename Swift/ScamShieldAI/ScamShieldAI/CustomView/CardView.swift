import UIKit

class CardView: UIView {

    // MARK: - Initialization

    override init(frame: CGRect) {
        super.init(frame: frame)
        configureAppearance()
    }

    required init?(coder: NSCoder) {
        fatalError("CardView chỉ được sử dụng bằng code.")
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        layer.borderColor = AppTheme.borderColor.resolvedColor(with: traitCollection).cgColor
        layer.shadowPath = UIBezierPath(roundedRect: bounds, cornerRadius: layer.cornerRadius).cgPath
    }
}

// MARK: - Setup UI

private extension CardView {

    func configureAppearance() {
        backgroundColor = AppTheme.cardBackgroundColor
        layer.cornerRadius = 16
        layer.cornerCurve = .continuous
        layer.borderWidth = 1
        layer.borderColor = AppTheme.borderColor.cgColor
        layer.shadowColor = AppTheme.titleColor.cgColor
        layer.shadowOpacity = 0
        layer.shadowOffset = CGSize(width: 0, height: 6)
        layer.shadowRadius = 10
    }
}
