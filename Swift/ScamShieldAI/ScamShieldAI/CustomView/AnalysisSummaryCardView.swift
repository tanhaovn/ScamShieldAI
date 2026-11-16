import UIKit

/// A readable conclusion first, followed by the content that was checked.
final class AnalysisSummaryCardView: CardView {
    private let contentStack = UIStackView()
    private let resultPanel = UIView()
    private let badgeView = RiskBadgeView()
    private let scoreLabel = UILabel()
    private let statusMessageLabel = UILabel()
    private let progressView = UIProgressView(progressViewStyle: .default)
    private let imageView = RemoteImageView()
    private let sourceLabel = UILabel()
    private let filenameLabel = UILabel()
    private let excerptLabel = UILabel()
    private let dateLabel = UILabel()
    private var targetScore = 0
    private var scoreAnimationTask: Task<Void, Never>?
    private var riskLevel: RiskLevel = .safe

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
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
        excerpt: String? = nil
    ) {
        let normalizedScore = min(max(score, 0), 100)
        riskLevel = level
        scoreAnimationTask?.cancel()
        targetScore = normalizedScore
        let tint = AppTheme.color(for: level)
        badgeView.configure(level: level)
        resultPanel.backgroundColor = tint.withAlphaComponent(0.08)
        scoreLabel.textColor = tint
        scoreLabel.text = "\(normalizedScore)/100"
        scoreLabel.accessibilityLabel = "Điểm rủi ro: \(normalizedScore) trên 100"
        progressView.progressTintColor = tint
        progressView.trackTintColor = tint.withAlphaComponent(0.14)
        progressView.setProgress(Float(normalizedScore) / 100, animated: false)
        switch level {
        case .safe: statusMessageLabel.text = "Chưa thấy dấu hiệu rủi ro cao"
        case .suspicious: statusMessageLabel.text = "Có dấu hiệu cần kiểm tra kỹ"
        case .dangerous: statusMessageLabel.text = "Nguy cơ lừa đảo cao"
        }
        sourceLabel.text = "ĐÃ KIỂM TRA · \(sourceKind.title.uppercased())"
        filenameLabel.text = filename
        dateLabel.text = dateText
        let text = (excerpt ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        excerptLabel.text = text
        excerptLabel.isHidden = text.isEmpty || sourceKind == .image
        imageView.cancelLoading()
        imageView.isHidden = sourceKind != .image
        if sourceKind == .image {
            if let image {
                imageView.image = image
                imageView.contentMode = .scaleAspectFit
            } else {
                imageView.contentMode = .center
                imageView.load(url: remoteURL, placeholder: UIImage(systemName: "photo")) { [weak self] loaded in
                    self?.imageView.contentMode = loaded ? .scaleAspectFit : .center
                }
            }
        }
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
        scoreLabel.text = "\(score)/100"
        progressView.setProgress(progress, animated: false)
        // VoiceOver always reads the actual saved result, never an intermediate number.
        scoreLabel.accessibilityLabel = "Điểm rủi ro: \(targetScore) trên 100"
    }

    private func setupUI() {
        translatesAutoresizingMaskIntoConstraints = false
        contentStack.axis = .vertical
        contentStack.spacing = 16
        contentStack.translatesAutoresizingMaskIntoConstraints = false
        addSubview(contentStack)

        resultPanel.layer.cornerRadius = 18
        resultPanel.layer.cornerCurve = .continuous
        let badgeRow = UIStackView(arrangedSubviews: [badgeView, UIView()])
        badgeRow.alignment = .leading

        scoreLabel.font = UIFontMetrics(forTextStyle: .largeTitle).scaledFont(for: .monospacedDigitSystemFont(ofSize: 40, weight: .bold))
        scoreLabel.adjustsFontForContentSizeCategory = true
        scoreLabel.numberOfLines = 1
        scoreLabel.adjustsFontSizeToFitWidth = true
        scoreLabel.minimumScaleFactor = 0.65
        let caption = label("Điểm rủi ro · thang 100", style: .subheadline, color: AppTheme.secondaryTextColor)
        statusMessageLabel.font = .preferredFont(forTextStyle: .headline)
        statusMessageLabel.adjustsFontForContentSizeCategory = true
        statusMessageLabel.textColor = AppTheme.titleColor
        statusMessageLabel.numberOfLines = 0
        let note = label("Kết quả hỗ trợ tham khảo. Hãy xác minh qua kênh chính thức.", style: .footnote, color: AppTheme.secondaryTextColor)
        let resultStack = UIStackView(arrangedSubviews: [badgeRow, scoreLabel, caption, progressView, statusMessageLabel, note])
        resultStack.axis = .vertical
        resultStack.spacing = 10
        resultStack.setCustomSpacing(2, after: scoreLabel)
        resultStack.setCustomSpacing(16, after: caption)
        resultStack.setCustomSpacing(16, after: progressView)
        resultStack.translatesAutoresizingMaskIntoConstraints = false
        resultPanel.addSubview(resultStack)

        sourceLabel.font = AppTheme.font(size: 11, weight: .semibold, style: .caption1)
        sourceLabel.adjustsFontForContentSizeCategory = true
        sourceLabel.textColor = AppTheme.primaryColor
        sourceLabel.numberOfLines = 0
        filenameLabel.font = .preferredFont(forTextStyle: .subheadline)
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
        imageView.backgroundColor = AppTheme.fieldBackgroundColor
        imageView.tintColor = AppTheme.secondaryTextColor
        imageView.layer.cornerRadius = 12
        imageView.clipsToBounds = true
        imageView.isAccessibilityElement = true
        imageView.accessibilityLabel = "Ảnh đã kiểm tra"
        let imageHeight = imageView.heightAnchor.constraint(equalToConstant: 140)
        imageHeight.priority = .defaultHigh
        imageHeight.isActive = true
        let sourceStack = UIStackView(arrangedSubviews: [sourceLabel, filenameLabel, imageView, excerptLabel, dateLabel])
        sourceStack.axis = .vertical
        sourceStack.spacing = 8
        contentStack.addArrangedSubview(resultPanel)
        contentStack.addArrangedSubview(sourceStack)
        progressView.isAccessibilityElement = false
        NSLayoutConstraint.activate([
            contentStack.topAnchor.constraint(equalTo: topAnchor, constant: 16),
            contentStack.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
            contentStack.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),
            contentStack.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -18),
            resultStack.topAnchor.constraint(equalTo: resultPanel.topAnchor, constant: 18),
            resultStack.leadingAnchor.constraint(equalTo: resultPanel.leadingAnchor, constant: 18),
            resultStack.trailingAnchor.constraint(equalTo: resultPanel.trailingAnchor, constant: -18),
            resultStack.bottomAnchor.constraint(equalTo: resultPanel.bottomAnchor, constant: -18),
            progressView.heightAnchor.constraint(equalToConstant: 6)
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
