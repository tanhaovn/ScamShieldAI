import UIKit

final class RiskBadgeView: UIView {

    // MARK: - UI Components

    private let iconView = UIImageView()
    private let titleLabel = UILabel()

    // MARK: - Initialization

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
    }

    required init?(coder: NSCoder) {
        fatalError("RiskBadgeView chỉ được sử dụng bằng code.")
    }

    // MARK: - Configuration

    func configure(level: RiskLevel) {
        let color = AppTheme.color(for: level)
        iconView.image = UIImage(systemName: level.systemImageName)
        iconView.tintColor = color
        titleLabel.text = level.displayName
        titleLabel.textColor = color
        backgroundColor = color.withAlphaComponent(0.12)
        accessibilityLabel = L10n.choose("Mức rủi ro: \(level.displayName)", "Risk level: \(level.displayName)")
    }
}

// MARK: - Setup UI

private extension RiskBadgeView {

    func setupUI() {
        layer.cornerRadius = 12
        translatesAutoresizingMaskIntoConstraints = false

        iconView.contentMode = .scaleAspectFit
        iconView.translatesAutoresizingMaskIntoConstraints = false

        titleLabel.font = AppTheme.font(size: 13, weight: .semibold, style: .subheadline)
        titleLabel.adjustsFontForContentSizeCategory = true
        titleLabel.numberOfLines = 0
        titleLabel.setContentHuggingPriority(.required, for: .horizontal)
        titleLabel.setContentCompressionResistancePriority(.defaultHigh, for: .horizontal)
        titleLabel.translatesAutoresizingMaskIntoConstraints = false

        addSubviews(iconView, titleLabel)
        NSLayoutConstraint.activate([
            iconView.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 10),
            iconView.centerYAnchor.constraint(equalTo: centerYAnchor),
            iconView.widthAnchor.constraint(equalToConstant: 16),
            iconView.heightAnchor.constraint(equalToConstant: 16),

            titleLabel.leadingAnchor.constraint(equalTo: iconView.trailingAnchor, constant: 6),
            titleLabel.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -10),
            titleLabel.topAnchor.constraint(equalTo: topAnchor, constant: 7),
            titleLabel.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -7),
            heightAnchor.constraint(greaterThanOrEqualToConstant: 30)
        ])
    }
}
