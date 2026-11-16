import UIKit

final class ScanHistoryCell: UITableViewCell {

    // MARK: - UI Components

    private let cardView = CardView()
    private let thumbnailView = RemoteImageView()
    private let unavailableImageLabel = UILabel()
    private let filenameLabel = UILabel()
    private let dateLabel = UILabel()
    private let scoreLabel = UILabel()
    private let riskBadgeView = RiskBadgeView()
    private let riskLine = UIView()

    // MARK: - Initialization

    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupUI()
    }

    required init?(coder: NSCoder) {
        fatalError("ScanHistoryCell chỉ được sử dụng bằng code.")
    }

    // MARK: - Reuse and Interaction

    override func prepareForReuse() {
        super.prepareForReuse()
        thumbnailView.cancelLoading()
        thumbnailView.image = UIImage(systemName: "photo")
        unavailableImageLabel.isHidden = true
        cardView.transform = .identity
    }

    override func setHighlighted(_ highlighted: Bool, animated: Bool) {
        super.setHighlighted(highlighted, animated: animated)
        guard !UIAccessibility.isReduceMotionEnabled else { return }
        UIView.animate(withDuration: 0.18, delay: 0, options: [.beginFromCurrentState, .allowUserInteraction]) {
            self.cardView.transform = highlighted ? CGAffineTransform(scaleX: 0.985, y: 0.985) : .identity
        }
    }

    // MARK: - Configuration

    func configure(item: ScanHistoryItem) {
        unavailableImageLabel.isHidden = true
        thumbnailView.load(
            url: Constants.mediaURL(from: item.imageURL),
            placeholder: UIImage(systemName: (ScanInputKind(rawValue: item.sourceType ?? "image") ?? .image).symbol)
        ) { [weak self] didLoadImage in
            self?.unavailableImageLabel.isHidden = didLoadImage || (item.sourceType != nil && item.sourceType != "image")
            self?.thumbnailView.contentMode = didLoadImage ? .scaleAspectFill : .center
        }
        filenameLabel.text = item.originalFilename ?? "Ảnh kiểm tra #\(item.id)"
        dateLabel.text = item.createdAt?.backendDateDisplayText ?? "Không rõ thời gian"
        scoreLabel.text = "\(item.riskScore) / 100"
        scoreLabel.textColor = AppTheme.color(for: item.riskLevel)
        riskLine.backgroundColor = AppTheme.color(for: item.riskLevel)
        riskBadgeView.configure(level: item.riskLevel)
        accessibilityLabel = "\(filenameLabel.text ?? "Ảnh kiểm tra"), \(item.riskLevel.displayName), điểm rủi ro \(item.riskScore) trên 100, \(dateLabel.text ?? "")"
        isAccessibilityElement = true
        accessibilityTraits = .button
    }
}

// MARK: - Setup UI

private extension ScanHistoryCell {

    func setupUI() {
        backgroundColor = .clear
        selectionStyle = .none
        cardView.translatesAutoresizingMaskIntoConstraints = false

        thumbnailView.contentMode = .scaleAspectFill
        thumbnailView.clipsToBounds = true
        thumbnailView.backgroundColor = AppTheme.softColor
        thumbnailView.tintColor = AppTheme.primaryColor
        thumbnailView.layer.cornerRadius = 17
        thumbnailView.translatesAutoresizingMaskIntoConstraints = false

        unavailableImageLabel.text = "Ảnh không\ncòn tồn tại"
        unavailableImageLabel.font = .systemFont(ofSize: 7.5, weight: .semibold)
        unavailableImageLabel.textColor = AppTheme.secondaryTextColor
        unavailableImageLabel.textAlignment = .center
        unavailableImageLabel.numberOfLines = 2
        unavailableImageLabel.adjustsFontSizeToFitWidth = true
        unavailableImageLabel.minimumScaleFactor = 0.85
        unavailableImageLabel.backgroundColor = AppTheme.softColor
        unavailableImageLabel.translatesAutoresizingMaskIntoConstraints = false

        filenameLabel.font = .preferredFont(forTextStyle: .headline)
        filenameLabel.adjustsFontForContentSizeCategory = true
        filenameLabel.numberOfLines = 2
        filenameLabel.textColor = AppTheme.titleColor
        filenameLabel.lineBreakMode = .byTruncatingMiddle
        filenameLabel.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)

        dateLabel.font = .preferredFont(forTextStyle: .caption1)
        dateLabel.adjustsFontForContentSizeCategory = true
        dateLabel.numberOfLines = 0
        dateLabel.textColor = AppTheme.secondaryTextColor

        scoreLabel.font = .monospacedDigitSystemFont(ofSize: 22, weight: .bold)
        scoreLabel.textAlignment = .right
        scoreLabel.setContentCompressionResistancePriority(.required, for: .horizontal)

        let textStack = UIStackView(arrangedSubviews: [filenameLabel, dateLabel])
        textStack.axis = .vertical
        textStack.spacing = 7

        let chevron = UIImageView(image: UIImage(systemName: "chevron.right"))
        chevron.tintColor = AppTheme.primaryColor
        chevron.contentMode = .scaleAspectFit
        chevron.translatesAutoresizingMaskIntoConstraints = false

        let topRow = UIStackView(arrangedSubviews: [thumbnailView, textStack, chevron])
        topRow.spacing = 12
        topRow.alignment = .center

        let scoreCaption = UILabel()
        scoreCaption.text = "Điểm rủi ro"
        scoreCaption.font = .preferredFont(forTextStyle: .caption2)
        scoreCaption.adjustsFontForContentSizeCategory = true
        scoreCaption.textColor = AppTheme.secondaryTextColor
        scoreCaption.textAlignment = .right
        let scoreStack = UIStackView(arrangedSubviews: [scoreCaption, scoreLabel])
        scoreStack.axis = .vertical
        scoreStack.spacing = 3
        let bottomRow = UIStackView(arrangedSubviews: [riskBadgeView, UIView(), scoreStack])
        bottomRow.spacing = 8
        bottomRow.alignment = .center

        let stack = UIStackView(arrangedSubviews: [topRow, bottomRow])
        stack.axis = .vertical
        stack.spacing = 12
        stack.translatesAutoresizingMaskIntoConstraints = false

        riskLine.layer.cornerRadius = 2
        riskLine.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(cardView)
        cardView.addSubviews(stack, riskLine)
        NSLayoutConstraint.activate([
            cardView.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 6),
            cardView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            cardView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            cardView.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -6),
            stack.topAnchor.constraint(equalTo: cardView.topAnchor, constant: 16),
            stack.leadingAnchor.constraint(equalTo: cardView.leadingAnchor, constant: 16),
            stack.trailingAnchor.constraint(equalTo: cardView.trailingAnchor, constant: -16),
            stack.bottomAnchor.constraint(equalTo: cardView.bottomAnchor, constant: -16),
            thumbnailView.widthAnchor.constraint(equalToConstant: 54),
            thumbnailView.heightAnchor.constraint(equalToConstant: 54),
            chevron.widthAnchor.constraint(equalToConstant: 17),
            chevron.heightAnchor.constraint(equalToConstant: 17),
            riskLine.leadingAnchor.constraint(equalTo: cardView.leadingAnchor),
            riskLine.centerYAnchor.constraint(equalTo: cardView.centerYAnchor),
            riskLine.widthAnchor.constraint(equalToConstant: 3),
            riskLine.heightAnchor.constraint(equalToConstant: 38)
        ])
        thumbnailView.addSubview(unavailableImageLabel)
        NSLayoutConstraint.activate([
            unavailableImageLabel.leadingAnchor.constraint(equalTo: thumbnailView.leadingAnchor),
            unavailableImageLabel.trailingAnchor.constraint(equalTo: thumbnailView.trailingAnchor),
            unavailableImageLabel.bottomAnchor.constraint(equalTo: thumbnailView.bottomAnchor),
            unavailableImageLabel.heightAnchor.constraint(equalToConstant: 27)
        ])
    }
}
