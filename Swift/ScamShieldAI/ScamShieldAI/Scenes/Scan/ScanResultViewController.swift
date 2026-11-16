import UIKit

final class ScanResultViewController: UIViewController {

    // MARK: - Properties

    private let result: ScanResult
    private let image: UIImage?

    // MARK: - UI Components

    private let scrollView = UIScrollView()
    private let contentStack = UIStackView()
    private var hasAnimatedEntrance = false
    private weak var summaryCard: AnalysisSummaryCardView?
    private weak var metricsCard: RiskMetricsCardView?

    // MARK: - Initialization

    init(result: ScanResult, image: UIImage? = nil) {
        self.result = result
        self.image = image
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("ScanResultViewController chỉ được khởi tạo bằng code.")
    }

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        summaryCard?.prepareForReveal()
        metricsCard?.prepareForReveal()
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        let firstAppearance = !hasAnimatedEntrance
        animateEntranceIfNeeded()
        animateResultValues(emitsFeedback: firstAppearance)
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        summaryCard?.showFinalResult()
        metricsCard?.showFinalValues()
    }

}

// MARK: - Setup UI

private extension ScanResultViewController {

    func animateEntranceIfNeeded() {
        guard !hasAnimatedEntrance else { return }
        hasAnimatedEntrance = true

        // Cả trang đi vào cùng một nhịp để tránh nhiều card chạy chồng lên nhau.
        contentStack.animateFadeAndSlideIn(delay: 0.04, distance: 8)
    }

    func animateResultValues(emitsFeedback: Bool) {
        summaryCard?.animateResult(delay: 0.12, emitsFeedback: emitsFeedback)
        metricsCard?.animateValues(delay: 0.28)
    }

    func setupUI() {
        navigationItem.title = "Kết quả phân tích"
        navigationItem.rightBarButtonItem = UIBarButtonItem(image: UIImage(systemName: "square.and.arrow.up"), style: .plain, target: self, action: #selector(shareResult))
        navigationItem.rightBarButtonItem?.accessibilityLabel = "Chia sẻ kết quả"
        view.backgroundColor = AppTheme.pageBackgroundColor
        navigationItem.largeTitleDisplayMode = .never
        navigationItem.backButtonDisplayMode = .minimal

        scrollView.alwaysBounceVertical = true
        // Chừa khoảng trống cho tab bar nổi, tránh nội dung cuối bị che.
        scrollView.contentInset.bottom = 104
        scrollView.verticalScrollIndicatorInsets.bottom = 104
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        contentStack.axis = .vertical
        contentStack.spacing = 16
        contentStack.translatesAutoresizingMaskIntoConstraints = false

        let explanationCard = InformationCardView(
            title: "Giải thích từ AI",
            systemImageName: "sparkles"
        )
        explanationCard.configure(text: result.explanation)

        let actionCard = InformationCardView(
            title: "Bạn nên làm gì?",
            systemImageName: "checklist"
        )
        actionCard.configure(text: result.suggestedAction, accentColor: AppTheme.accentColor)

        let terms = result.highlightedTerms.isEmpty
            ? "Không phát hiện cụm từ rủi ro nổi bật."
            : result.highlightedTerms.map { "• \($0)" }.joined(separator: "\n")
        let termCard = InformationCardView(
            title: "Tín hiệu văn bản",
            systemImageName: "text.magnifyingglass"
        )
        termCard.configure(text: terms)

        let visualFlags = result.visualFlags.isEmpty
            ? "Không phát hiện dấu hiệu hình ảnh bất thường nổi bật."
            : result.visualFlags.map { "• \($0)" }.joined(separator: "\n")
        let visualCard = InformationCardView(
            title: "Tín hiệu hình ảnh",
            systemImageName: "photo.badge.exclamationmark"
        )
        visualCard.configure(text: visualFlags)

        let ocrCard = OCRCopyCardView()
        ocrCard.configure(text: result.extractedText)

        [
            makeHeroCard(),
            actionCard,
            makeAssistantButton(),
            explanationCard,
            makeMetricsCard(),
            termCard,
            visualCard,
            ocrCard,
            makeDisclaimerLabel()
        ].forEach(contentStack.addArrangedSubview)

        visualCard.isHidden = result.sourceType != nil && result.sourceType != "image"
        if let qrCodes = result.qrCodes, !qrCodes.isEmpty {
            let qrCard = InformationCardView(title: "Mã QR được tìm thấy", systemImageName: "qrcode")
            qrCard.configure(text: qrCodes.joined(separator: "\n\n"))
            contentStack.insertArrangedSubview(qrCard, at: 4)
        }
        if let info = result.documentInfo {
            let pdf = InformationCardView(title: "Phạm vi đọc tài liệu", systemImageName: "doc.text")
            pdf.configure(text: "Đã đọc \(info.processedPages)/\(info.pageCount) trang." + (info.truncated ? " Kết quả chỉ áp dụng cho các trang đã xử lý." : ""))
            contentStack.insertArrangedSubview(pdf, at: 1)
        }
        if let urls = result.phishVNURLs, !urls.isEmpty {
            let urlCard = InformationCardView(title: "Liên kết được phân tích", systemImageName: "link")
            urlCard.configure(text: urls.map { "\($0.url)\nĐiểm rủi ro: \($0.riskScore)/100" }.joined(separator: "\n\n"))
            contentStack.insertArrangedSubview(urlCard, at: 4)
        }
        installAppBackground()
        view.addSubview(scrollView)
        scrollView.addSubview(contentStack)
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            contentStack.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor, constant: 12),
            contentStack.leadingAnchor.constraint(equalTo: scrollView.frameLayoutGuide.leadingAnchor, constant: 20),
            contentStack.trailingAnchor.constraint(equalTo: scrollView.frameLayoutGuide.trailingAnchor, constant: -20),
            contentStack.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor, constant: -28)
        ])
    }

    func makeHeroCard() -> UIView {
        let card = AnalysisSummaryCardView()
        card.configure(
            image: image,
            filename: result.originalFilename ?? "Nội dung vừa kiểm tra",
            dateText: result.createdAt?.backendDateDisplayText ?? "Vừa hoàn tất",
            score: result.riskScore,
            level: result.riskLevel,
            sourceKind: ScanInputKind(rawValue: result.sourceType ?? "image") ?? .image,
            excerpt: result.extractedText
        )
        summaryCard = card
        return card
    }

    func makeMetricsCard() -> UIView {
        let card = RiskMetricsCardView()
        card.configure(
            textScore: result.textRiskScore,
            visualScore: result.visualRiskScore,
            imageModelScore: result.imageModelScore,
            imageModelAvailable: result.imageModelAvailable,
            urlScore: result.phishVNURLRiskScore,
            components: result.analysisBreakdown?.components
        )
        metricsCard = card
        return card
    }

    func makeDisclaimerLabel() -> UILabel {
        let label = UILabel()
        label.text = "Kết quả AI mang tính hỗ trợ. Không chuyển tiền hoặc cung cấp thông tin nhạy cảm chỉ dựa trên kết quả này."
        label.font = .preferredFont(forTextStyle: .footnote)
        label.adjustsFontForContentSizeCategory = true
        label.textColor = AppTheme.secondaryTextColor
        label.textAlignment = .center
        label.numberOfLines = 0
        return label
    }
}

private extension ScanResultViewController {
    func makeAssistantButton() -> UIView {
        var config = UIButton.Configuration.filled()
        config.title = "Hỏi trợ lý về kết quả này"
        config.subtitle = "Giải thích dấu hiệu · Hướng dẫn bước tiếp theo"
        config.image = UIImage(systemName: "sparkles")
        config.imagePadding = 12
        config.baseBackgroundColor = AppTheme.brandDark
        config.baseForegroundColor = .white
        config.cornerStyle = .large
        config.contentInsets = .init(top: 18, leading: 16, bottom: 18, trailing: 16)
        let button = UIButton(configuration: config, primaryAction: UIAction { [weak self] _ in
            guard let self else { return }
            self.navigationController?.pushViewController(SafetyAssistantViewController(result: self.result), animated: true)
        })
        button.titleLabel?.numberOfLines = 0
        button.accessibilityIdentifier = "result.assistant"
        button.enableSoftPressAnimation()
        return button
    }

    @objc func shareResult() {
        let text = "ScamShield AI — \(result.riskLevel.displayName) (\(result.riskScore)/100)\n\n\(result.explanation)\n\nHành động đề xuất:\n\(result.suggestedAction)\n\nKết quả hỗ trợ tham khảo, không thay thế xác minh qua nguồn chính thức."
        let controller = UIActivityViewController(activityItems: [text], applicationActivities: nil)
        controller.popoverPresentationController?.barButtonItem = navigationItem.rightBarButtonItem
        present(controller, animated: true)
    }
}
