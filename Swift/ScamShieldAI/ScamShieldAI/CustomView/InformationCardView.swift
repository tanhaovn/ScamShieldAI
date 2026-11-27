import UIKit

final class InformationCardView: CardView {

    // MARK: - UI Components

    private let iconView = UIImageView()
    private let titleLabel = UILabel()
    private let bodyLabel = UILabel()

    // MARK: - Initialization

    init(title: String, systemImageName: String) {
        super.init(frame: .zero)
        titleLabel.text = title
        iconView.image = UIImage(systemName: systemImageName)
        setupUI()
    }

    required init?(coder: NSCoder) {
        fatalError("InformationCardView chỉ được sử dụng bằng code.")
    }

    // MARK: - Configuration

    func configure(text: String, accentColor: UIColor = AppTheme.primaryColor) {
        bodyLabel.text = text.isEmpty ? L10n.text("Chưa có dữ liệu.") : text
        iconView.tintColor = accentColor
    }
}

// MARK: - Setup UI

private extension InformationCardView {

    func setupUI() {
        translatesAutoresizingMaskIntoConstraints = false

        iconView.contentMode = .scaleAspectFit
        iconView.tintColor = AppTheme.primaryColor
        iconView.preferredSymbolConfiguration = .init(pointSize: 20, weight: .semibold)
        let iconTile = UIView()
        iconTile.backgroundColor = AppTheme.softColor
        iconTile.layer.cornerRadius = 18
        iconTile.layer.cornerCurve = .continuous
        iconView.translatesAutoresizingMaskIntoConstraints = false
        iconTile.addSubview(iconView)
        titleLabel.font = .preferredFont(forTextStyle: .headline)
        titleLabel.adjustsFontForContentSizeCategory = true
        titleLabel.textColor = AppTheme.titleColor
        titleLabel.numberOfLines = 0
        bodyLabel.font = .preferredFont(forTextStyle: .subheadline)
        bodyLabel.adjustsFontForContentSizeCategory = true
        bodyLabel.textColor = AppTheme.secondaryTextColor
        bodyLabel.numberOfLines = 0
        let header = UIStackView(arrangedSubviews: [iconTile, titleLabel])
        header.spacing = 12
        header.alignment = .center
        let stack = UIStackView(arrangedSubviews: [header, bodyLabel])
        stack.axis = .vertical
        stack.spacing = 12
        stack.translatesAutoresizingMaskIntoConstraints = false
        addSubview(stack)
        NSLayoutConstraint.activate([
            iconTile.widthAnchor.constraint(equalToConstant: 36),
            iconTile.heightAnchor.constraint(equalToConstant: 36),
            iconView.centerXAnchor.constraint(equalTo: iconTile.centerXAnchor),
            iconView.centerYAnchor.constraint(equalTo: iconTile.centerYAnchor),
            iconView.widthAnchor.constraint(equalToConstant: 22),
            iconView.heightAnchor.constraint(equalToConstant: 22),
            stack.topAnchor.constraint(equalTo: topAnchor, constant: 20),
            stack.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 20),
            stack.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -20),
            stack.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -20)
        ])
    }
}
