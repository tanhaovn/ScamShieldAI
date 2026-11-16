import UIKit

final class HistoryDetailViewController: UIViewController {

    // MARK: - Properties

    private let item: ScanHistoryItem
    private let scrollView = UIScrollView()
    private let contentStack = UIStackView()
    private weak var summaryCard: AnalysisSummaryCardView?
    private weak var metricsCard: RiskMetricsCardView?

    // MARK: - Initialization

    init(item: ScanHistoryItem) {
        self.item = item
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("HistoryDetailViewController chỉ được khởi tạo bằng code.")
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
        summaryCard?.animateResult(delay: 0.08, emitsFeedback: false)
        metricsCard?.animateValues(delay: 0.24)
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        summaryCard?.showFinalResult()
        metricsCard?.showFinalValues()
    }

}

// MARK: - Setup UI

private extension HistoryDetailViewController {

    func setupUI() {
        navigationItem.title = "Chi tiết lần kiểm tra"
        view.backgroundColor = AppTheme.pageBackgroundColor
        navigationItem.largeTitleDisplayMode = .never
        navigationItem.backButtonDisplayMode = .minimal

        scrollView.alwaysBounceVertical = true
        // Tab bar dạng nổi cần khoảng trống để không che nội dung cuối trang.
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
        explanationCard.configure(text: item.explanation ?? "Chưa có giải thích.")

        let actionCard = InformationCardView(
            title: "Hành động đề xuất",
            systemImageName: "checklist"
        )
        actionCard.configure(
            text: item.suggestedAction ?? "Hãy thận trọng và xác minh bằng kênh chính thức.",
            accentColor: AppTheme.accentColor
        )

        let termCard = InformationCardView(
            title: "Tín hiệu văn bản",
            systemImageName: "text.magnifyingglass"
        )
        termCard.configure(text: makeTermText())

        let visualCard = InformationCardView(
            title: "Tín hiệu hình ảnh",
            systemImageName: "photo.badge.exclamationmark"
        )
        visualCard.configure(text: makeVisualFlagText())

        var cards: [UIView] = [makeSummaryCard()]
        if let metricsCard = makeMetricsCard() {
            cards.append(metricsCard)
        }
        cards.append(contentsOf: [
            explanationCard,
            actionCard,
            termCard,
            visualCard,
            makeOCRCard(),
            makeDisclaimerLabel()
        ])

        cards.forEach(contentStack.addArrangedSubview)

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

    func makeSummaryCard() -> UIView {
        let card = AnalysisSummaryCardView()
        card.configure(
            remoteURL: Constants.mediaURL(from: item.imageURL),
            filename: item.originalFilename ?? "Ảnh kiểm tra #\(item.id)",
            dateText: item.createdAt?.backendDateDisplayText ?? "Không rõ thời gian",
            score: item.riskScore,
            level: item.riskLevel
        )
        summaryCard = card
        return card
    }

    func makeOCRCard() -> UIView {
        let card = OCRCopyCardView()
        card.configure(text: item.extractedText)
        return card
    }

    func makeMetricsCard() -> RiskMetricsCardView? {
        let textScore = item.highlightedRegions?.textRiskScore ?? 0
        let visualScore = item.highlightedRegions?.visualRiskScore ?? 0
        let storedComponents = item.highlightedRegions?.analysisBreakdown?.components
        let components: [AnalysisComponent]?
        if let storedComponents, !storedComponents.isEmpty {
            components = storedComponents
        } else if item.highlightedRegions?.textRiskScore == nil,
                  item.highlightedRegions?.visualRiskScore == nil {
            components = [AnalysisComponent(
                key: "legacy_total",
                title: "Điểm rủi ro tổng hợp",
                score: item.riskScore,
                summary: "Điểm đã lưu từ lần phân tích trước."
            )]
        } else {
            components = nil
        }

        let card = RiskMetricsCardView()
        card.configure(
            textScore: textScore,
            visualScore: visualScore,
            imageModelScore: item.highlightedRegions?.imageModelScore,
            imageModelAvailable: item.highlightedRegions?.imageModelAvailable ?? false,
            urlScore: item.highlightedRegions?.phishVNURLs?.map(\.riskScore).max(),
            components: components
        )
        metricsCard = card
        return card
    }

    func makeTermText() -> String {
        let terms = item.highlightedRegions?.terms ?? []
        return terms.isEmpty
            ? "Không phát hiện cụm từ rủi ro nổi bật."
            : terms.map { "• \($0)" }.joined(separator: "\n")
    }

    func makeVisualFlagText() -> String {
        let visualFlags = item.highlightedRegions?.visualFlags ?? []
        return visualFlags.isEmpty
            ? "Không phát hiện dấu hiệu hình ảnh bất thường nổi bật."
            : visualFlags.map { "• \($0)" }.joined(separator: "\n")
    }

    func makeDisclaimerLabel() -> UILabel {
        let label = UILabel()
        label.text = "Kết quả AI mang tính hỗ trợ. Không chuyển tiền hoặc cung cấp thông tin nhạy cảm chỉ dựa trên kết quả này."
        label.font = .systemFont(ofSize: 12)
        label.textColor = AppTheme.secondaryTextColor
        label.textAlignment = .center
        label.numberOfLines = 0
        return label
    }
}
