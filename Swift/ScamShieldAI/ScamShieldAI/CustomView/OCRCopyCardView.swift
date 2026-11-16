import UIKit

final class OCRCopyCardView: CardView {

    // MARK: - UI Components

    private let iconView = UIImageView(image: UIImage(systemName: "doc.text.viewfinder"))
    private let titleLabel = UILabel()
    private let copyButton = UIButton(type: .system)
    private let bodyLabel = UILabel()

    // MARK: - Properties

    private var textToCopy = ""

    // MARK: - Initialization

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
    }

    required init?(coder: NSCoder) {
        fatalError("OCRCopyCardView chỉ được sử dụng bằng code.")
    }

    // MARK: - Configuration

    func configure(text: String?) {
        textToCopy = text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        bodyLabel.text = textToCopy.isEmpty ? "Không trích xuất được văn bản." : textToCopy
        copyButton.isEnabled = !textToCopy.isEmpty
    }
}

// MARK: - Setup UI

private extension OCRCopyCardView {

    func setupUI() {
        translatesAutoresizingMaskIntoConstraints = false

        iconView.tintColor = AppTheme.primaryColor
        iconView.contentMode = .scaleAspectFit
        iconView.translatesAutoresizingMaskIntoConstraints = false

        titleLabel.text = "Nội dung phân tích"
        titleLabel.font = .systemFont(ofSize: 17, weight: .bold)
        titleLabel.textColor = AppTheme.titleColor

        var configuration = UIButton.Configuration.tinted()
        configuration.title = "Sao chép"
        configuration.image = UIImage(systemName: "doc.on.doc")
        configuration.imagePadding = 6
        configuration.cornerStyle = .capsule
        configuration.baseForegroundColor = AppTheme.primaryColor
        copyButton.configuration = configuration
        copyButton.enableSoftPressAnimation()
        copyButton.addTarget(self, action: #selector(didTapCopy), for: .touchUpInside)
        copyButton.setContentHuggingPriority(.required, for: .horizontal)

        let headerStack = UIStackView(arrangedSubviews: [iconView, titleLabel, UIView(), copyButton])
        headerStack.axis = .horizontal
        headerStack.alignment = .center
        headerStack.spacing = 10
        headerStack.translatesAutoresizingMaskIntoConstraints = false

        bodyLabel.font = .systemFont(ofSize: 15)
        bodyLabel.textColor = AppTheme.secondaryTextColor
        bodyLabel.numberOfLines = 0
        bodyLabel.translatesAutoresizingMaskIntoConstraints = false

        addSubviews(headerStack, bodyLabel)
        NSLayoutConstraint.activate([
            headerStack.topAnchor.constraint(equalTo: topAnchor, constant: 16),
            headerStack.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 18),
            headerStack.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -14),

            iconView.widthAnchor.constraint(equalToConstant: 22),
            iconView.heightAnchor.constraint(equalToConstant: 22),

            bodyLabel.topAnchor.constraint(equalTo: headerStack.bottomAnchor, constant: 14),
            bodyLabel.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 18),
            bodyLabel.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -18),
            bodyLabel.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -18)
        ])
    }

    // MARK: - Actions

    @objc func didTapCopy() {
        guard !textToCopy.isEmpty else { return }

        UIPasteboard.general.string = textToCopy
        UINotificationFeedbackGenerator().notificationOccurred(.success)
        copyButton.animatePop()

        var copiedConfiguration = copyButton.configuration
        copiedConfiguration?.title = "Đã sao chép"
        copiedConfiguration?.image = UIImage(systemName: "checkmark")
        copyButton.configuration = copiedConfiguration

        DispatchQueue.main.asyncAfter(deadline: .now() + 1.6) { [weak self] in
            guard let self else { return }
            var resetConfiguration = copyButton.configuration
            resetConfiguration?.title = "Sao chép"
            resetConfiguration?.image = UIImage(systemName: "doc.on.doc")
            copyButton.configuration = resetConfiguration
        }
    }
}
