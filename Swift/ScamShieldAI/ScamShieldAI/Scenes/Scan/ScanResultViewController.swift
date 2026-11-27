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
    private weak var feedbackEditor: UIView?

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
        NotificationCenter.default.addObserver(self, selector: #selector(revealFeedbackEditor),
                                               name: UIResponder.keyboardDidShowNotification, object: nil)
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        summaryCard?.prepareForReveal()
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
    }

    func setupUI() {
        navigationItem.title = L10n.text("Kết quả phân tích")
        navigationItem.rightBarButtonItem = UIBarButtonItem(image: UIImage(systemName: "square.and.arrow.up"), style: .plain, target: self, action: #selector(shareResult))
        navigationItem.rightBarButtonItem?.accessibilityLabel = L10n.text("Xuất báo cáo PDF")
        view.backgroundColor = AppTheme.pageBackgroundColor
        navigationItem.largeTitleDisplayMode = .never
        navigationItem.backButtonDisplayMode = .minimal

        scrollView.alwaysBounceVertical = true
        // Chừa khoảng trống cho tab bar nổi, tránh nội dung cuối bị che.
        scrollView.contentInset.bottom = 16
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        contentStack.axis = .vertical
        contentStack.spacing = 16
        contentStack.translatesAutoresizingMaskIntoConstraints = false

        scrollView.keyboardDismissMode = .interactive
        contentStack.addArrangedSubview(makeHeroCard())
        if let detected = result.scamType, !detected.isEmpty {
            contentStack.addArrangedSubview(makeInfo(
                L10n.choose("Nhận diện", "Detected"), scamTypeLabel(detected), symbol: "viewfinder"))
        }
        if let image, let dimensions = result.imageDimensions,
           let regions = result.imageAnnotations, !regions.isEmpty {
            contentStack.addArrangedSubview(AnnotatedImageView(image: image, dimensions: dimensions, regions: regions))
            let regionText = regions.enumerated().map { index, region in
                "\(index + 1). " + [region.label, region.reason].compactMap { $0 }.joined(separator: " · ")
            }.joined(separator: "\n")
            contentStack.addArrangedSubview(makeInfo(L10n.text("Vùng ảnh cần chú ý"), regionText, symbol: "viewfinder"))
        }
        if isImageResult {
            let gradCAM = GradCAMComparisonView(result: result, originalImage: image)
            contentStack.addArrangedSubview(gradCAM)
        } else {
            contentStack.addArrangedSubview(makeEvidenceCard())
            contentStack.addArrangedSubview(makeInfo(
                L10n.choose("Vì sao có kết quả này?", "Why did I get this result?"),
                numbered(plainReasons), symbol: "sparkles"))
            contentStack.addArrangedSubview(makeInfo(L10n.text("Bạn nên làm gì?"), numbered(nextSteps), symbol: "checklist"))
        }

        let urlHighlights = (result.phishVNURLs ?? []).map(\.url)
        let textTitle = isImageResult
            ? L10n.choose("Văn bản AI đọc được từ ảnh", "Text read from the image")
            : L10n.choose("Nội dung được đưa vào phân tích", "Content submitted for analysis")
        contentStack.addArrangedSubview(DisclosureCardView(
            title: textTitle, symbol: "text.viewfinder",
            body: RecognizedTextView(text: result.extractedText, highlights: result.highlightedTerms + urlHighlights),
            expanded: true
        ))
        if let qrCodes = result.qrCodes, !qrCodes.isEmpty {
            contentStack.addArrangedSubview(DisclosureCardView(
                title: L10n.text("Mã QR được tìm thấy"), symbol: "qrcode",
                body: RecognizedTextView(text: qrCodes.joined(separator: "\n\n")), expanded: true
            ))
        }
        if let info = result.documentInfo {
            let pageCount = L10n.choose("Đã đọc \(info.processedPages)/\(info.pageCount) trang.",
                                       "Read \(info.processedPages)/\(info.pageCount) pages.")
            let scope = info.truncated ? L10n.text(" Kết quả chỉ áp dụng cho các trang đã xử lý.") : ""
            contentStack.addArrangedSubview(makeInfo(L10n.text("Phạm vi đọc tài liệu"), pageCount + scope, symbol: "doc.text"))
        }
        let feedback = ResultFeedbackView(result: result)
        feedback.onEditorFocus = { [weak self] editor in self?.feedbackEditor = editor }
        contentStack.addArrangedSubview(feedback)

        installAppBackground()
        view.addSubview(scrollView)
        scrollView.addSubview(contentStack)
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.keyboardLayoutGuide.topAnchor),
            contentStack.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor, constant: 12),
            contentStack.widthAnchor.constraint(equalTo: scrollView.frameLayoutGuide.widthAnchor, constant: -2 * 20),
            contentStack.leadingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.leadingAnchor, constant: 20),
            contentStack.trailingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.trailingAnchor, constant: -20),
            contentStack.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor, constant: -28)
        ])
    }

    func makeHeroCard() -> UIView {
        let card = AnalysisSummaryCardView()
        card.configure(
            image: image,
            remoteURL: Constants.mediaURL(from: result.imageURL),
            filename: result.originalFilename ?? L10n.text("Nội dung vừa kiểm tra"),
            dateText: result.createdAt?.backendDateDisplayText ?? L10n.text("Vừa hoàn tất"),
            score: result.riskScore,
            level: result.riskLevel,
            sourceKind: ScanInputKind(rawValue: result.sourceType ?? "image") ?? .image,
            excerpt: result.extractedText,
            showsPreview: image == nil || result.imageDimensions == nil || (result.imageAnnotations ?? []).isEmpty
        )
        summaryCard = card
        return card
    }

    var isImageResult: Bool { result.sourceType == "image" || (result.sourceType == nil && image != nil) }

    // Keep the short explanation and safety guidance consistent with the web result.
    var plainReasons: [String] {
        var reasons: [String] = []
        if !result.highlightedTerms.isEmpty {
            let terms = result.highlightedTerms.prefix(5).joined(separator: ", ")
            reasons.append(L10n.choose("Có từ ngữ thúc giục hoặc yêu cầu nhạy cảm: \(terms).",
                                       "Urgent wording or sensitive requests found: \(terms)."))
        }
        let count = result.phishVNURLs?.count ?? 0
        if count > 0 {
            let score = result.phishVNURLRiskScore ?? 0
            reasons.append(L10n.choose("Tìm thấy \(count) đường link cần kiểm tra; đường link đáng chú ý nhất có điểm \(score)/100.",
                                       "\(count) link(s) need review; the highest-risk link scored \(score)/100."))
        }
        if result.visualRiskScore >= 25 {
            reasons.append(L10n.choose("Hình ảnh có đặc điểm trình bày cần thận trọng hoặc có thể đã qua chỉnh sửa.",
                                       "The image contains visual details that require caution or may have been edited."))
        }
        return reasons.isEmpty ? [L10n.choose("Chưa tìm thấy từ ngữ, đường link hoặc dấu hiệu hình ảnh nổi bật.",
                                              "No notable wording, links or visual signals were found.")] : reasons
    }

    var nextSteps: [String] {
        switch result.riskLevel {
        case .dangerous:
            return [L10n.choose("Dừng nhắn tin và không bấm đường link.", "Stop the conversation and do not click any links."),
                    L10n.choose("Không chuyển tiền, không gửi OTP, mật khẩu hay ảnh giấy tờ.", "Do not transfer money or send OTP codes, passwords or identity documents."),
                    L10n.choose("Tự gọi tổng đài hoặc mở ứng dụng chính thức để xác minh.", "Call the official hotline or open the official app to verify.")]
        case .suspicious:
            return [L10n.choose("Chưa thực hiện yêu cầu trong nội dung.", "Do not follow the request yet."),
                    L10n.choose("Đối chiếu tên miền và số điện thoại bằng nguồn chính thức.", "Verify the domain and phone number using official sources."),
                    L10n.choose("Hỏi người thân hoặc đơn vị liên quan trước khi tiếp tục.", "Ask someone you trust or the relevant organization before continuing.")]
        case .safe:
            return [L10n.choose("Vẫn kiểm tra kỹ nếu nội dung liên quan đến tiền hoặc tài khoản.", "Still review carefully if money or accounts are involved."),
                    L10n.choose("Không chia sẻ OTP và mật khẩu trong mọi trường hợp.", "Never share OTP codes or passwords."),
                    L10n.choose("Quét lại nếu nhận được nội dung hoặc đường link mới.", "Run another check if you receive new content or a new link.")]
        }
    }

    func numbered(_ lines: [String]) -> String {
        lines.enumerated().map { "\($0.offset + 1). \($0.element)" }.joined(separator: "\n\n")
    }

    func scamTypeLabel(_ code: String) -> String {
        switch code {
        case "none": return L10n.choose("Chưa xác định loại lừa đảo", "Scam type not identified")
        case "phishing": return L10n.choose("Giả mạo để lấy thông tin", "Credential phishing")
        case "phishing_url": return L10n.choose("Đường link có dấu hiệu giả mạo", "Potential phishing link")
        case "impersonation": return L10n.choose("Mạo danh cơ quan hoặc tổ chức", "Organization impersonation")
        case "fake_invoice": return L10n.choose("Hóa đơn hoặc yêu cầu thanh toán giả", "Fake invoice or payment request")
        case "job_scam": return L10n.choose("Lừa đảo tuyển dụng, việc làm", "Employment scam")
        case "urgent_account_threat": return L10n.choose("Đe dọa khóa hoặc trừ tiền tài khoản", "Urgent account threat")
        default: return L10n.choose("Nội dung cần kiểm tra thêm", "Content needs further review")
        }
    }

    func makeInfo(_ title: String, _ text: String, symbol: String = "doc.text.magnifyingglass") -> InformationCardView {
        let card = InformationCardView(title: title, systemImageName: symbol)
        card.configure(text: text)
        return card
    }

    @objc func revealFeedbackEditor() {
        guard let editor = feedbackEditor, editor.isFirstResponder else { return }
        view.layoutIfNeeded()
        scrollView.scrollRectToVisible(editor.convert(editor.bounds, to: scrollView).insetBy(dx: 0, dy: -12), animated: true)
    }
}

private extension ScanResultViewController {
    @objc func shareResult() {
        do {
            let url = try ScanReport.export(result)
            let controller = UIActivityViewController(activityItems: [url], applicationActivities: nil)
            controller.popoverPresentationController?.barButtonItem = navigationItem.rightBarButtonItem
            controller.completionWithItemsHandler = { _, _, _, _ in try? FileManager.default.removeItem(at: url) }
            present(controller, animated: true)
        } catch { showErrorAlert(message: L10n.text("Không xuất được báo cáo PDF. Vui lòng thử lại.")) }
    }
}

private extension ScanResultViewController {
    func makeEvidenceCard() -> UIView {
        let card = CardView()
        let heading = UILabel()
        heading.text = L10n.text("Nguồn bằng chứng")
        heading.font = .preferredFont(forTextStyle: .headline)
        heading.textColor = AppTheme.titleColor
        heading.adjustsFontForContentSizeCategory = true
        heading.numberOfLines = 0
        heading.accessibilityTraits = .header

        let textScore = result.extractedText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            ? L10n.choose("Không có văn bản đọc được", "No readable text")
            : "\(result.textRiskScore)/100"
        let phishScore = result.phishVNAvailable == true
            ? "\(result.phishVNURLRiskScore ?? 0)/100"
            : L10n.text("Chưa sẵn sàng")
        let safeBrowsing = result.safeBrowsing?.summary ?? L10n.text("Chưa có dữ liệu đối chiếu.")
        var sources = [
            (L10n.choose("Nội dung & OCR", "Content & OCR"), textScore, "text.viewfinder"),
            ("PhishVN", phishScore, "link"),
            ("Google Safe Browsing", safeBrowsing, "checkmark.shield")
        ]
        if result.imageModelAvailable {
            sources.append((L10n.choose("Mô hình ảnh", "Image model"), "\(result.imageModelScore)/100", "photo"))
        }
        if let vision = result.visionAnalysis, vision.available == true, let score = vision.risk_score {
            sources.append((L10n.choose("AI hiểu ngữ cảnh ảnh", "Image context AI"), "\(score)/100", "sparkles"))
        }

        let stack = UIStackView(arrangedSubviews: [heading])
        stack.axis = .vertical
        stack.spacing = 8
        stack.setCustomSpacing(12, after: heading)
        for (title, value, symbol) in sources {
            stack.addArrangedSubview(makeEvidenceRow(title: title, value: value, symbol: symbol))
        }
        stack.translatesAutoresizingMaskIntoConstraints = false
        card.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.topAnchor.constraint(equalTo: card.topAnchor, constant: 18),
            stack.leadingAnchor.constraint(equalTo: card.leadingAnchor, constant: 18),
            stack.trailingAnchor.constraint(equalTo: card.trailingAnchor, constant: -18),
            stack.bottomAnchor.constraint(equalTo: card.bottomAnchor, constant: -18)
        ])
        return card
    }

    func makeEvidenceRow(title: String, value: String, symbol: String) -> UIView {
        let icon = UIImageView(image: UIImage(systemName: symbol))
        icon.tintColor = AppTheme.primaryColor
        icon.contentMode = .scaleAspectFit
        icon.widthAnchor.constraint(equalToConstant: 20).isActive = true
        icon.heightAnchor.constraint(equalTo: icon.widthAnchor).isActive = true
        icon.isAccessibilityElement = false

        let name = UILabel()
        name.text = title
        name.font = .preferredFont(forTextStyle: .subheadline)
        name.textColor = AppTheme.titleColor
        name.adjustsFontForContentSizeCategory = true
        name.numberOfLines = 0

        let detail = UILabel()
        detail.text = value
        detail.font = .preferredFont(forTextStyle: .footnote)
        detail.textColor = AppTheme.secondaryTextColor
        detail.adjustsFontForContentSizeCategory = true
        detail.numberOfLines = 0

        let text = UIStackView(arrangedSubviews: [name, detail])
        text.axis = .vertical
        text.spacing = 3
        let row = UIStackView(arrangedSubviews: [icon, text])
        row.alignment = .center
        row.spacing = 12
        row.isLayoutMarginsRelativeArrangement = true
        row.directionalLayoutMargins = .init(top: 9, leading: 12, bottom: 9, trailing: 12)
        row.backgroundColor = AppTheme.fieldBackgroundColor
        row.layer.cornerRadius = 11
        row.layer.cornerCurve = .continuous
        return row
    }

}
