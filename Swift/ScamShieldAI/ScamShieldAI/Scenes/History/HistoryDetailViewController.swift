import UIKit

final class HistoryDetailViewController: UIViewController {

    // MARK: - Properties

    private let item: ScanHistoryItem
    private let scrollView = UIScrollView()
    private let contentStack = UIStackView()
    private weak var summaryCard: AnalysisSummaryCardView?

    // MARK: - Initialization

    init(item: ScanHistoryItem) {
        self.item = item
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("HistoryDetailViewController chỉ được khởi tạo bằng code.")
    }

    @objc private func exportPDF() {
        do {
            let url = try ScanReport.export(item.reportResult)
            let controller = UIActivityViewController(activityItems: [url], applicationActivities: nil)
            controller.popoverPresentationController?.barButtonItem = navigationItem.rightBarButtonItem
            controller.completionWithItemsHandler = { _, _, _, _ in try? FileManager.default.removeItem(at: url) }
            present(controller, animated: true)
        } catch { showErrorAlert(message: L10n.text("Không xuất được báo cáo PDF. Vui lòng thử lại.")) }
    }

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        navigationItem.rightBarButtonItem = UIBarButtonItem(image: UIImage(systemName: "square.and.arrow.up"), style: .plain, target: self, action: #selector(exportPDF))
        navigationItem.rightBarButtonItem?.accessibilityLabel = L10n.text("Xuất báo cáo PDF")
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        summaryCard?.prepareForReveal()
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        summaryCard?.animateResult(delay: 0.08, emitsFeedback: false)
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        summaryCard?.showFinalResult()
    }

}

// MARK: - Setup UI

private extension HistoryDetailViewController {

    func setupUI() {
        navigationItem.title = L10n.text("Chi tiết lần kiểm tra")
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

        let explanationCard = makeExplanationCard()

        let actionCard = InformationCardView(
            title: L10n.text("Bạn nên làm gì?"),
            systemImageName: "checklist"
        )
        actionCard.configure(
            text: item.suggestedAction ?? L10n.text("Hãy thận trọng và xác minh bằng kênh chính thức."),
            accentColor: AppTheme.accentColor
        )

        let recognizedText = DisclosureCardView(
            title: L10n.choose("Nội dung hệ thống đã đọc", "Content read by the system"),
            symbol: "text.viewfinder",
            body: RecognizedTextView(text: item.extractedText ?? item.result?.extractedText),
            expanded: true
        )
        [makeSummaryCard(), explanationCard, actionCard, recognizedText].forEach(contentStack.addArrangedSubview)

        installAppBackground()
        view.addSubview(scrollView)
        scrollView.addSubview(contentStack)
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            contentStack.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor, constant: 12),
            contentStack.widthAnchor.constraint(equalTo: scrollView.frameLayoutGuide.widthAnchor, constant: -2 * 20),
            contentStack.leadingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.leadingAnchor, constant: 20),
            contentStack.trailingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.trailingAnchor, constant: -20),
            contentStack.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor, constant: -28)
        ])
    }

    func makeSummaryCard() -> UIView {
        let card = AnalysisSummaryCardView()
        card.configure(
            remoteURL: Constants.mediaURL(from: item.imageURL),
            filename: item.originalFilename ?? L10n.choose("Ảnh kiểm tra #\(item.id)", "Checked image #\(item.id)"),
            dateText: item.createdAt?.backendDateDisplayText ?? L10n.text("Không rõ thời gian"),
            score: item.riskScore,
            level: item.riskLevel,
            sourceKind: ScanInputKind(rawValue: item.sourceType ?? item.result?.sourceType ?? "image") ?? .image
        )
        summaryCard = card
        return card
    }

    func makeExplanationCard() -> UIView {
        func firstText(_ values: String?...) -> String {
            values.compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
                .first { !$0.isEmpty } ?? ""
        }
        let result = item.reportResult
        let vision = result.visionAnalysis
        let isGemini = vision?.provider == "gemini" || vision?.model?.localizedCaseInsensitiveContains("gemini") == true
        let title = L10n.choose("Giải thích từ AI", "AI explanation") + (isGemini ? " · Gemini AI" : "")
        let card = InformationCardView(title: title, systemImageName: "sparkles")
        var sections: [String] = []
        let summary = firstText(vision?.summary, vision?.reasoning)
        if !summary.isEmpty {
            sections.append(L10n.choose("KẾT LUẬN CỦA AI", "AI CONCLUSION") + "\n" + summary)
        }
        let entries = vision?.explanation_items ?? []
        let evidence: [String]
        if !entries.isEmpty {
            evidence = entries.map { entry in
                let title = firstText(entry.observation, L10n.choose("Chi tiết AI nhận diện", "Detail identified by AI"))
                let detail = firstText(entry.why_risky, entry.explanation)
                return detail.isEmpty ? title : title + "\n" + detail
            }
        } else if let indicators = vision?.risk_indicators, !indicators.isEmpty {
            evidence = Array(indicators.prefix(6))
        } else {
            evidence = Array((result.analysisBreakdown?.components ?? []).flatMap { component in
                (component.findings ?? []).map { component.title + "\n" + $0 }
            }.prefix(6))
        }
        if !evidence.isEmpty {
            sections.append(evidence.enumerated().map { "\($0.offset + 1). \($0.element)" }.joined(separator: "\n\n"))
        } else {
            let fallback = (item.explanation ?? result.explanation).components(separatedBy: .newlines)
                .map { $0.replacingOccurrences(of: "^[-•]\\s*", with: "", options: .regularExpression).trimmingCharacters(in: .whitespaces) }
                .filter { !$0.isEmpty }.prefix(8)
            sections.append(fallback.isEmpty ? L10n.choose("Không có giải thích được lưu cho lượt kiểm tra này.", "No explanation was saved for this check.") : fallback.joined(separator: "\n\n"))
        }
        card.configure(text: sections.joined(separator: "\n\n"))
        return card
    }

}
