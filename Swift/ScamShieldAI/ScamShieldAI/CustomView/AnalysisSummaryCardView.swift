import UIKit

/// A readable conclusion first, followed by the content that was checked.
final class AnalysisSummaryCardView: CardView {
    private let contentStack = UIStackView()
    private let resultPanel = UIView()
    private let badgeView = RiskBadgeView()
    private let scoreRing = RiskScoreView()
    private let riskRow = UIStackView()
    private let statusMessageLabel = UILabel()
    private let verdictNoteLabel = UILabel()
    private let imageView = RemoteImageView()
    private let sourceLabel = UILabel()
    private let filenameLabel = UILabel()
    private let excerptLabel = UILabel()
    private let dateLabel = UILabel()
    private var targetScore = 0
    private var imageHeight: NSLayoutConstraint?
    private var scoreAnimationTask: Task<Void, Never>?
    private var riskLevel: RiskLevel = .safe

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
        updateRiskLayout()
        registerForTraitChanges([UITraitPreferredContentSizeCategory.self]) { (card: AnalysisSummaryCardView, _) in
            card.updateRiskLayout()
        }
        imageHeight = imageView.heightAnchor.constraint(equalToConstant: 140)
        imageHeight?.priority = .defaultHigh
        imageHeight?.isActive = true
        imageView.heightAnchor.constraint(lessThanOrEqualToConstant: 320).isActive = true
        NotificationCenter.default.addObserver(self, selector: #selector(motionPreferenceChanged), name: UIAccessibility.reduceMotionStatusDidChangeNotification, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(showFinalResult), name: UIApplication.willResignActiveNotification, object: nil)
    }

    required init?(coder: NSCoder) { fatalError("Use init(frame:)") }

    isolated deinit {
        scoreAnimationTask?.cancel()
        NotificationCenter.default.removeObserver(self)
    }

    override func didMoveToWindow() {
        super.didMoveToWindow()
        if window == nil { showFinalResult() }
    }

    func configure(
        image: UIImage? = nil,
        remoteURL: URL? = nil,
        filename: String,
        dateText: String,
        score: Int,
        level: RiskLevel,
        sourceKind: ScanInputKind = .image,
        excerpt: String? = nil,
        showsPreview: Bool = true
    ) {
        let normalizedScore = min(max(score, 0), 100)
        riskLevel = level
        scoreAnimationTask?.cancel()
        targetScore = normalizedScore
        let tint = AppTheme.color(for: level)
        badgeView.configure(level: level)
        resultPanel.backgroundColor = tint.withAlphaComponent(0.08)
        scoreRing.configure(level: level, finalScore: normalizedScore)
        scoreRing.display(score: normalizedScore, progress: Float(normalizedScore) / 100)
        switch level {
        case .safe:
            statusMessageLabel.text = L10n.choose("Chưa thấy dấu hiệu lừa đảo rõ ràng", "No clear signs of a scam")
            verdictNoteLabel.text = L10n.choose("Hệ thống chưa tìm thấy tín hiệu mạnh. Bạn vẫn nên kiểm tra lại nếu nội dung liên quan đến tiền, mật khẩu hoặc thông tin cá nhân.", "The system has not found strong signals. Still verify content involving money, passwords or personal information.")
        case .suspicious:
            statusMessageLabel.text = L10n.choose("Nội dung này có một số điểm đáng ngờ", "This content has some suspicious signs")
            verdictNoteLabel.text = L10n.choose("Đừng làm theo ngay. Hãy tự liên hệ đơn vị được nhắc đến bằng số điện thoại hoặc website chính thức để xác minh.", "Do not act immediately. Contact the organization using its official phone number or website to verify.")
        case .dangerous:
            statusMessageLabel.text = L10n.choose("Cảnh báo: nguy cơ lừa đảo cao", "Warning: high scam risk")
            verdictNoteLabel.text = L10n.choose("Không bấm đường link, không chuyển tiền và không cung cấp mật khẩu, mã OTP hay thông tin ngân hàng.", "Do not click links, transfer money or share passwords, OTP codes or banking information.")
        }
        sourceLabel.text = L10n.choose("ĐÃ KIỂM TRA · \(sourceKind.title.uppercased())", "CHECKED · \(sourceKind.title.uppercased())")
        filenameLabel.text = filename
        dateLabel.text = dateText
        let text = (excerpt ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        excerptLabel.text = text
        excerptLabel.isHidden = text.isEmpty || text == filename || sourceKind == .image
        imageView.cancelLoading()
        imageView.isHidden = sourceKind != .image || !showsPreview
        if sourceKind == .image {
            if let image {
                imageView.image = image
                imageView.contentMode = .scaleAspectFit
                fitImage(image)
            } else {
                imageView.contentMode = .center
                imageView.load(url: remoteURL, placeholder: UIImage(systemName: "photo")) { [weak self] loaded in
                    self?.imageView.contentMode = loaded ? .scaleAspectFit : .center
                    if loaded, let image = self?.imageView.image { self?.fitImage(image) }
                }
            }
        }
    }

    private func fitImage(_ image: UIImage) {
        imageHeight?.isActive = false
        imageHeight = imageView.heightAnchor.constraint(equalTo: imageView.widthAnchor, multiplier: image.size.height / max(image.size.width, 1))
        imageHeight?.priority = .defaultHigh
        imageHeight?.isActive = true
    }

    /// Called before presentation so the final score never flashes before the count-up.
    func prepareForReveal() {
        showFinalResult()
        guard !UIAccessibility.isReduceMotionEnabled else { return }
        display(score: 0, progress: 0)
    }

    func animateResult(delay: TimeInterval = 0.18, emitsFeedback: Bool = false) {
        prepareForReveal()
        if emitsFeedback {
            UINotificationFeedbackGenerator().notificationOccurred(riskLevel == .safe ? .success : .warning)
        }
        guard !UIAccessibility.isReduceMotionEnabled, targetScore > 0 else {
            showFinalResult()
            return
        }
        scoreAnimationTask = Task { [weak self] in
            do { try await Task.sleep(for: .seconds(max(0, delay))) } catch { return }
            let start = CACurrentMediaTime()
            while !Task.isCancelled {
                guard let self else { return }
                guard window != nil, UIApplication.shared.applicationState == .active,
                      !UIAccessibility.isReduceMotionEnabled else {
                    showFinalResult()
                    return
                }
                let elapsed = min((CACurrentMediaTime() - start) / 1.3, 1)
                let eased = 1 - pow(1 - elapsed, 2)
                display(score: Int((Double(targetScore) * eased).rounded()),
                        progress: Float(Double(targetScore) * eased / 100))
                if elapsed >= 1 {
                    showFinalResult()
                    return
                }
                do { try await Task.sleep(for: .milliseconds(16)) } catch { return }
            }
        }
    }

    @objc func showFinalResult() {
        scoreAnimationTask?.cancel()
        scoreAnimationTask = nil
        resultPanel.layer.removeAllAnimations()
        resultPanel.alpha = 1
        display(score: targetScore, progress: Float(targetScore) / 100)
    }

    @objc private func motionPreferenceChanged() {
        if UIAccessibility.isReduceMotionEnabled { showFinalResult() }
    }

    private func display(score: Int, progress: Float) {
        scoreRing.display(score: score, progress: progress)
    }

    private func updateRiskLayout() {
        let largeText = traitCollection.preferredContentSizeCategory >= .extraExtraExtraLarge
        riskRow.axis = largeText ? .vertical : .horizontal
        riskRow.alignment = largeText ? .leading : .center
    }

    private func setupUI() {
        translatesAutoresizingMaskIntoConstraints = false
        layer.cornerRadius = 22
        contentStack.axis = .vertical
        contentStack.spacing = 16
        contentStack.translatesAutoresizingMaskIntoConstraints = false
        addSubview(contentStack)

        resultPanel.layer.cornerRadius = 18
        resultPanel.layer.cornerCurve = .continuous
        let badgeRow = UIStackView(arrangedSubviews: [badgeView, UIView()])
        badgeRow.alignment = .leading

        let caption = label(L10n.text("Điểm rủi ro"), style: .caption1, color: AppTheme.secondaryTextColor)
        statusMessageLabel.font = AppTheme.font(size: 18, weight: .bold, style: .headline)
        statusMessageLabel.adjustsFontForContentSizeCategory = true
        statusMessageLabel.textColor = AppTheme.titleColor
        statusMessageLabel.numberOfLines = 0
        verdictNoteLabel.font = .preferredFont(forTextStyle: .footnote)
        verdictNoteLabel.adjustsFontForContentSizeCategory = true
        verdictNoteLabel.textColor = AppTheme.secondaryTextColor
        verdictNoteLabel.numberOfLines = 0
        let copy = UIStackView(arrangedSubviews: [caption, badgeRow, statusMessageLabel])
        copy.axis = .vertical
        copy.spacing = 7
        riskRow.addArrangedSubview(scoreRing)
        riskRow.addArrangedSubview(copy)
        riskRow.spacing = 14

        let resultStack = UIStackView(arrangedSubviews: [riskRow, verdictNoteLabel])
        resultStack.axis = .vertical
        resultStack.spacing = 12
        resultStack.translatesAutoresizingMaskIntoConstraints = false
        resultPanel.addSubview(resultStack)

        sourceLabel.font = AppTheme.font(size: 11, weight: .semibold, style: .caption1)
        sourceLabel.adjustsFontForContentSizeCategory = true
        sourceLabel.textColor = AppTheme.primaryColor
        sourceLabel.numberOfLines = 0
        filenameLabel.font = AppTheme.font(size: 16, weight: .semibold, style: .subheadline)
        filenameLabel.adjustsFontForContentSizeCategory = true
        filenameLabel.textColor = AppTheme.titleColor
        filenameLabel.numberOfLines = 0
        excerptLabel.font = .preferredFont(forTextStyle: .body)
        excerptLabel.adjustsFontForContentSizeCategory = true
        excerptLabel.textColor = AppTheme.secondaryTextColor
        excerptLabel.numberOfLines = 3
        excerptLabel.lineBreakMode = .byTruncatingTail
        dateLabel.font = .preferredFont(forTextStyle: .caption1)
        dateLabel.adjustsFontForContentSizeCategory = true
        dateLabel.textColor = AppTheme.secondaryTextColor
        dateLabel.numberOfLines = 0
        imageView.backgroundColor = .clear
        imageView.tintColor = AppTheme.secondaryTextColor
        imageView.layer.cornerRadius = 12
        imageView.clipsToBounds = true
        imageView.isAccessibilityElement = true
        imageView.accessibilityLabel = L10n.text("Ảnh đã kiểm tra")
        let sourceStack = UIStackView(arrangedSubviews: [sourceLabel, filenameLabel, imageView, excerptLabel, dateLabel])
        sourceStack.axis = .vertical
        sourceStack.spacing = 8
        contentStack.addArrangedSubview(resultPanel)
        contentStack.addArrangedSubview(sourceStack)
        NSLayoutConstraint.activate([
            contentStack.topAnchor.constraint(equalTo: topAnchor, constant: 16),
            contentStack.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
            contentStack.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),
            contentStack.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -18),
            resultStack.topAnchor.constraint(equalTo: resultPanel.topAnchor, constant: 18),
            resultStack.leadingAnchor.constraint(equalTo: resultPanel.leadingAnchor, constant: 18),
            resultStack.trailingAnchor.constraint(equalTo: resultPanel.trailingAnchor, constant: -18),
            resultStack.bottomAnchor.constraint(equalTo: resultPanel.bottomAnchor, constant: -18)
        ])
    }

    private func label(_ text: String, style: UIFont.TextStyle, color: UIColor) -> UILabel {
        let label = UILabel()
        label.text = text
        label.font = .preferredFont(forTextStyle: style)
        label.adjustsFontForContentSizeCategory = true
        label.textColor = color
        label.numberOfLines = 0
        return label
    }
}
