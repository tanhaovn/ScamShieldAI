import UIKit

final class OverviewViewController: UIViewController {

    // MARK: - Constants

    private enum Layout {
        static let horizontalPadding: CGFloat = 20
        static let sectionSpacing: CGFloat = 24
        static let tabBarClearance: CGFloat = 108
    }

    // MARK: - Dependencies

    private let user: User
    private let historyService: HistoryService

    // MARK: - Properties

    private let greetingName = UILabel()
    private var adaptiveRows: [UIStackView] = []
    private weak var heroHeader: UIStackView?
    var onStartScan: (() -> Void)?
    private var loadTask: Task<Void, Never>?
    private var hasAnimatedEntrance = false

    // MARK: - UI Components

    private let scrollView: UIScrollView = {
        let view = UIScrollView()
        view.alwaysBounceVertical = true
        view.refreshControl = UIRefreshControl()
        view.showsVerticalScrollIndicator = false
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()
    private let contentStack = UIStackView()
    private let totalStat = OverviewStatView(title: L10n.text("Tổng lượt phân tích"), systemImageName: "viewfinder")
    private let safeStat = OverviewStatView(title: L10n.text("Kết quả rủi ro thấp"), systemImageName: "checkmark.shield")
    private let suspiciousStat = OverviewStatView(title: L10n.text("Cần kiểm tra thêm"), systemImageName: "waveform.path.ecg")
    private let dangerStat = OverviewStatView(title: L10n.text("Cảnh báo nguy hiểm"), systemImageName: "exclamationmark.triangle")
    private let trendCard = RiskTrendCardView()
    private let distributionCard = RiskDistributionCardView()
    private let recentStack = UIStackView()
    private let statusLabel = UILabel()
    private let averageLabel = UILabel()
    private let recordsLabel = UILabel()
    private weak var radarScore: UILabel?

    // MARK: - Initialization

    init(user: User, historyService: HistoryService) {
        self.user = user
        self.historyService = historyService
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("OverviewViewController chỉ được khởi tạo bằng code.")
    }

    deinit {
        loadTask?.cancel()
        NotificationCenter.default.removeObserver(self)
    }

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        updateAdaptiveRows()
        registerForTraitChanges([UITraitPreferredContentSizeCategory.self]) { (controller: OverviewViewController, _: UITraitCollection) in
            controller.updateAdaptiveRows()
        }
        configureActions()
        loadHistory()
    }

    private func updateAdaptiveRows() {
        let largeText = traitCollection.preferredContentSizeCategory >= .extraExtraExtraLarge
        heroHeader?.axis = largeText ? .vertical : .horizontal
        heroHeader?.alignment = largeText ? .leading : .center
        adaptiveRows.forEach {
            $0.axis = largeText ? .vertical : .horizontal
            $0.distribution = largeText ? .fill : .fillEqually
        }
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        if let name = UserDefaults.standard.string(forKey: "scamShield.displayName"), !name.isEmpty {
            greetingName.text = L10n.choose("Xin chào, \(name)", "Hello, \(name)")
        } else {
            greetingName.text = L10n.choose("Xin chào, bạn", "Hello there")
        }
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        animateEntranceIfNeeded()
    }
}
// MARK: - Setup UI

private extension OverviewViewController {

    func setupUI() {
        navigationItem.title = "ScamShield AI"
        navigationItem.largeTitleDisplayMode = .never
        navigationItem.backButtonDisplayMode = .minimal
        view.backgroundColor = AppTheme.pageBackgroundColor

        contentStack.axis = .vertical
        contentStack.spacing = Layout.sectionSpacing
        contentStack.translatesAutoresizingMaskIntoConstraints = false
        recentStack.axis = .vertical
        recentStack.spacing = 10
        statusLabel.font = .systemFont(ofSize: 14)
        statusLabel.textColor = AppTheme.secondaryTextColor
        statusLabel.textAlignment = .center
        statusLabel.numberOfLines = 0
        scrollView.contentInset.bottom = Layout.tabBarClearance
        scrollView.verticalScrollIndicatorInsets.bottom = Layout.tabBarClearance
        scrollView.refreshControl?.tintColor = AppTheme.primaryColor

        [makeProtectionCard(), makeStatisticsSection(), makePipelineCard(), makeAnalyticsSection(), makeRecentSection()]
            .forEach(contentStack.addArrangedSubview)

        installAppBackground()
        view.addSubview(scrollView)
        scrollView.addSubview(contentStack)
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            contentStack.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor, constant: 12),
            contentStack.widthAnchor.constraint(equalTo: scrollView.frameLayoutGuide.widthAnchor, constant: -2 * Layout.horizontalPadding),
            contentStack.leadingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.leadingAnchor, constant: Layout.horizontalPadding),
            contentStack.trailingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.trailingAnchor, constant: -Layout.horizontalPadding),
            contentStack.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor, constant: -24)
        ])
    }

    func makeProtectionCard() -> UIView {
        let card = GradientCardView(colors: [AppTheme.brandDark, AppTheme.brandDeep])
        greetingName.font = .preferredFont(forTextStyle: .subheadline)
        greetingName.adjustsFontForContentSizeCategory = true
        greetingName.textColor = AppTheme.mintColor
        greetingName.numberOfLines = 0

        let title = makeLabel(L10n.choose("An toàn số bắt đầu từ một lần kiểm tra", "Digital safety starts with one check"),
                              size: 30, weight: .bold, color: .white)
        title.accessibilityTraits = .header
        let subtitle = makeLabel(
            L10n.choose("Kiểm tra chữ, liên kết và hình ảnh trước khi hành động.",
                        "Review text, links and images before taking action."),
            size: 14, weight: .regular, color: UIColor.white.withAlphaComponent(0.84)
        )
        let copy = UIStackView(arrangedSubviews: [greetingName, title, subtitle])
        copy.axis = .vertical
        copy.spacing = 6
        copy.setCustomSpacing(10, after: title)

        let radar = RadarView()
        radar.showsCenterIcon = false
        let radarScore = UILabel()
        radarScore.font = .monospacedDigitSystemFont(ofSize: 24, weight: .bold)
        radarScore.textColor = AppTheme.mintColor
        radarScore.text = "—"
        radarScore.textAlignment = .center
        radarScore.translatesAutoresizingMaskIntoConstraints = false
        radar.addSubview(radarScore)
        self.radarScore = radarScore
        NSLayoutConstraint.activate([
            radar.widthAnchor.constraint(equalToConstant: 108),
            radar.heightAnchor.constraint(equalTo: radar.widthAnchor),
            radarScore.centerXAnchor.constraint(equalTo: radar.centerXAnchor),
            radarScore.centerYAnchor.constraint(equalTo: radar.centerYAnchor)
        ])
        let header = UIStackView(arrangedSubviews: [copy, radar])
        header.alignment = .center
        header.spacing = 10
        heroHeader = header

        var config = UIButton.Configuration.filled()
        config.title = L10n.text("Bắt đầu kiểm tra")
        config.image = UIImage(systemName: "arrow.right")
        config.imagePlacement = .trailing
        config.imagePadding = 12
        config.baseBackgroundColor = AppTheme.mintColor
        config.baseForegroundColor = AppTheme.brandDeep
        config.cornerStyle = .capsule
        config.contentInsets = .init(top: 14, leading: 20, bottom: 14, trailing: 20)
        config.titleTextAttributesTransformer = UIConfigurationTextAttributesTransformer { attributes in
            var result = attributes
            result.font = AppTheme.font(size: 16, weight: .semibold, style: .headline)
            return result
        }
        let button = UIButton(configuration: config)
        button.titleLabel?.numberOfLines = 0
        button.enableSoftPressAnimation()
        button.addTarget(self, action: #selector(didTapStartScan), for: .touchUpInside)
        button.accessibilityIdentifier = "overview.startScan"
        let stack = UIStackView(arrangedSubviews: [header, button])
        stack.axis = .vertical
        stack.spacing = 18
        stack.translatesAutoresizingMaskIntoConstraints = false
        card.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.topAnchor.constraint(equalTo: card.topAnchor, constant: 22),
            stack.leadingAnchor.constraint(equalTo: card.leadingAnchor, constant: 22),
            stack.trailingAnchor.constraint(equalTo: card.trailingAnchor, constant: -22),
            stack.bottomAnchor.constraint(equalTo: card.bottomAnchor, constant: -22)
        ])
        return card
    }

    func makeStatisticsSection() -> UIView {
        totalStat.setAccentColor(AppTheme.primaryColor)
        safeStat.setAccentColor(AppTheme.safeColor)
        suspiciousStat.setAccentColor(AppTheme.suspiciousColor)
        dangerStat.setAccentColor(AppTheme.dangerousColor)
        let rows = [[totalStat, safeStat], [suspiciousStat, dangerStat]].map { views in
            let row = UIStackView(arrangedSubviews: views)
            row.axis = .horizontal
            row.distribution = .fillEqually
            row.spacing = 12
            adaptiveRows.append(row)
            return row
        }
        averageLabel.font = .monospacedDigitSystemFont(ofSize: 17, weight: .bold)
        averageLabel.textColor = AppTheme.primaryColor
        averageLabel.accessibilityIdentifier = "overview.averageRisk"
        averageLabel.setContentHuggingPriority(.required, for: .horizontal)
        let averageTitle = makeLabel(L10n.text("Điểm rủi ro trung bình / 100"), size: 12, weight: .medium, color: AppTheme.secondaryTextColor)
        averageTitle.numberOfLines = 0
        let averageRow = UIStackView(arrangedSubviews: [averageTitle, averageLabel])
        averageRow.spacing = 12
        let stack = UIStackView(arrangedSubviews: [makeSectionHeading(L10n.text("GÓC NHÌN CỦA BẠN"), title: L10n.text("Tổng quan rủi ro"))] + rows + [averageRow])
        stack.axis = .vertical
        stack.spacing = 12
        stack.setCustomSpacing(16, after: stack.arrangedSubviews[0])
        return stack
    }

    func makeAnalyticsSection() -> UIView {
        let stack = UIStackView(arrangedSubviews: [
            makeSectionHeading(L10n.text("PHÂN TÍCH"), title: L10n.text("Dữ liệu trực quan")),
            trendCard,
            distributionCard
        ])
        stack.axis = .vertical
        stack.spacing = 14
        stack.setCustomSpacing(16, after: stack.arrangedSubviews[0])
        return stack
    }

    func makeRecentSection() -> UIView {
        recordsLabel.text = "—"
        recordsLabel.font = .monospacedDigitSystemFont(ofSize: 12, weight: .semibold)
        recordsLabel.textColor = AppTheme.primaryColor
        recordsLabel.setContentHuggingPriority(.required, for: .horizontal)
        var config = UIButton.Configuration.tinted()
        config.title = L10n.choose("Kiểm tra mới", "New check")
        config.baseForegroundColor = AppTheme.primaryColor
        config.cornerStyle = .capsule
        let button = UIButton(configuration: config)
        button.addTarget(self, action: #selector(didTapStartScan), for: .touchUpInside)
        button.setContentHuggingPriority(.required, for: .horizontal)
        button.heightAnchor.constraint(greaterThanOrEqualToConstant: 44).isActive = true
        let heading = UIStackView(arrangedSubviews: [
            makeSectionHeading("", title: L10n.choose("Lượt kiểm tra gần nhất", "Recent checks")), button
        ])
        heading.axis = .horizontal
        heading.alignment = .center
        heading.spacing = 8
        let stack = UIStackView(arrangedSubviews: [heading, recordsLabel, statusLabel, recentStack])
        stack.axis = .vertical
        stack.spacing = 16
        return stack
    }

    func makePipelineCard() -> UIView {
        let pipeline = InformationCardView(title: L10n.choose("Các lớp phân tích", "Analysis layers"),
                                           systemImageName: "square.stack.3d.up")
        pipeline.configure(text: L10n.choose(
            "OCR · Đọc văn bản từ ảnh\nPhishVN và Google · Đối chiếu liên kết\nPhân tích hình ảnh · Tìm dấu hiệu thị giác\nRisk AI · Tổng hợp cảnh báo",
            "OCR · Reads text from images\nPhishVN and Google · Review links\nVisual analysis · Checks image signals\nRisk AI · Summarizes the warning"
        ))
        return pipeline
    }

    func makeSectionHeading(_ eyebrow: String, title: String) -> UIView {
        let label = makeLabel(title, size: 21, weight: .bold, color: AppTheme.titleColor)
        label.accessibilityTraits = .header
        return label
    }

    func makeLabel(_ text: String, size: CGFloat, weight: UIFont.Weight, color: UIColor) -> UILabel {
        let label = UILabel()
        label.text = text
        label.font = AppTheme.font(size: size, weight: weight)
        label.adjustsFontForContentSizeCategory = true
        label.numberOfLines = 0
        label.textColor = color
        return label
    }
}

// MARK: - Data Loading

private extension OverviewViewController {

    func configureActions() {
        scrollView.refreshControl?.addTarget(self, action: #selector(didPullToRefresh), for: .valueChanged)
        NotificationCenter.default.addObserver(self, selector: #selector(didCompleteScan), name: .scanDidComplete, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(didChangeHistory), name: .historyDidChange, object: nil)
    }

    func loadHistory() {
        loadTask?.cancel()
        statusLabel.isHidden = false
        statusLabel.text = L10n.text("Đang cập nhật dữ liệu…")
        let service = historyService
        loadTask = Task { [weak self] in
            do {
                let items = try await service.fetchHistory()
                // Chỉ giữ màn hình sau khi request xong, để chuyển màn hình không giữ UI cũ.
                guard !Task.isCancelled, let self else { return }
                scrollView.refreshControl?.endRefreshing()
                render(items: items)
            } catch {
                guard !Task.isCancelled, let self else { return }
                scrollView.refreshControl?.endRefreshing()
                statusLabel.isHidden = false
                statusLabel.text = L10n.text("Chưa thể tải dữ liệu mới. Kéo xuống để thử lại.")
            }
        }
    }

    func render(items: [ScanHistoryItem]) {
        let safeCount = items.filter { $0.riskLevel == .safe }.count
        let suspiciousCount = items.filter { $0.riskLevel == .suspicious }.count
        let dangerCount = items.filter { $0.riskLevel == .dangerous }.count
        totalStat.setValue(items.count)
        safeStat.setValue(safeCount)
        suspiciousStat.setValue(suspiciousCount)
        dangerStat.setValue(dangerCount)
        trendCard.configure(items: items)
        distributionCard.configure(
            safe: safeCount,
            suspicious: suspiciousCount,
            dangerous: dangerCount
        )
        averageLabel.text = items.isEmpty ? "—" : "\(Int((Double(items.reduce(0) { $0 + $1.riskScore }) / Double(items.count)).rounded()))"
        averageLabel.superview?.accessibilityValue = items.isEmpty ? L10n.text("Chưa có dữ liệu") : L10n.choose("\(averageLabel.text ?? "") trên 100", "\(averageLabel.text ?? "") out of 100")


        recentStack.arrangedSubviews.forEach {
            recentStack.removeArrangedSubview($0)
            $0.removeFromSuperview()
        }
        radarScore?.text = items.isEmpty ? "0" : averageLabel.text
        let recentItems = Array(items.prefix(5))
        recordsLabel.text = L10n.choose("\(recentItems.count) bản ghi", "\(recentItems.count) records")
        statusLabel.isHidden = !recentItems.isEmpty
        statusLabel.text = recentItems.isEmpty
            ? L10n.text("Chưa có lần kiểm tra nào. Chọn loại nội dung để bắt đầu.")
            : nil
        recentItems.forEach { recentStack.addArrangedSubview(makeRecentRow(item: $0)) }
        if view.window != nil {
            recentStack.animateFadeAndSlideIn(distance: 5)
        }
    }

    func makeRecentRow(item: ScanHistoryItem) -> UIView {
        let card = CardView()
        let kind = ScanInputKind(rawValue: item.sourceType ?? "") ?? .image
        let thumbnail = UIImageView(image: UIImage(systemName: kind.symbol))
        thumbnail.contentMode = .center
        thumbnail.backgroundColor = AppTheme.color(for: item.riskLevel).withAlphaComponent(0.08)
        thumbnail.tintColor = AppTheme.color(for: item.riskLevel)
        thumbnail.layer.cornerRadius = 12
        thumbnail.isAccessibilityElement = false

        let filename = makeLabel(item.listTitle, size: 14, weight: .semibold, color: AppTheme.titleColor)
        filename.numberOfLines = 2
        filename.lineBreakMode = .byTruncatingMiddle
        let date = makeLabel(item.createdAt?.backendDateDisplayText ?? L10n.text("Không rõ thời gian"), size: 11, weight: .regular, color: AppTheme.secondaryTextColor)
        let risk = makeLabel(item.riskLevel.displayName, size: 11, weight: .semibold, color: AppTheme.color(for: item.riskLevel))
        let labels = UIStackView(arrangedSubviews: [filename, date, risk])
        labels.axis = .vertical
        labels.spacing = 5
        let score = makeLabel("\(item.riskScore)", size: 24, weight: .bold, color: AppTheme.color(for: item.riskLevel))
        score.font = .monospacedDigitSystemFont(ofSize: 24, weight: .bold)
        score.textAlignment = .center
        let scoreCaption = makeLabel("/ 100", size: 9, weight: .medium, color: AppTheme.secondaryTextColor)
        scoreCaption.textAlignment = .center
        let scoreStack = UIStackView(arrangedSubviews: [score, scoreCaption])
        scoreStack.axis = .vertical
        scoreStack.spacing = 2
        scoreStack.setContentHuggingPriority(.required, for: .horizontal)
        scoreStack.setContentCompressionResistancePriority(.required, for: .horizontal)
        let row = UIStackView(arrangedSubviews: [thumbnail, labels, scoreStack])
        row.axis = .horizontal
        row.alignment = .center
        row.spacing = 11
        row.translatesAutoresizingMaskIntoConstraints = false
        card.addSubview(row)
        NSLayoutConstraint.activate([
            thumbnail.widthAnchor.constraint(equalToConstant: 44),
            thumbnail.heightAnchor.constraint(equalToConstant: 44),
            row.topAnchor.constraint(equalTo: card.topAnchor, constant: 14),
            row.leadingAnchor.constraint(equalTo: card.leadingAnchor, constant: 13),
            row.trailingAnchor.constraint(equalTo: card.trailingAnchor, constant: -13),
            row.bottomAnchor.constraint(equalTo: card.bottomAnchor, constant: -14)
        ])

        return card
    }
}

// MARK: - Actions

private extension OverviewViewController {

    func animateEntranceIfNeeded() {
        guard !hasAnimatedEntrance else { return }
        hasAnimatedEntrance = true
        for (index, section) in contentStack.arrangedSubviews.enumerated() {
            section.animateFadeAndSlideIn(delay: Double(index) * 0.065, distance: 14)
        }
    }

    @objc func didTapStartScan() { onStartScan?() }
    @objc func didPullToRefresh() { loadHistory() }
    @objc func didCompleteScan() { loadHistory() }
    @objc func didChangeHistory() { loadHistory() }
}

final class OverviewStatView: CardView {

    // MARK: - Properties

    private let iconView = UIImageView()
    private let valueLabel = UILabel()
    private let titleLabel = UILabel()
    private var countTask: Task<Void, Never>?
    private var displayedValue = 0
    private var targetValue: Int?

    // MARK: - Initialization

    init(title: String, systemImageName: String) {
        super.init(frame: .zero)
        titleLabel.text = title
        iconView.image = UIImage(systemName: systemImageName)
        setupUI()
    }

    required init?(coder: NSCoder) {
        fatalError("OverviewStatView chỉ được sử dụng bằng code.")
    }

    isolated deinit {
        countTask?.cancel()
    }

    override func didMoveToWindow() {
        super.didMoveToWindow()
        if window == nil {
            countTask?.cancel()
            if let targetValue { updateValue(targetValue) }
        }
    }

    // MARK: - Configuration

    func setValue(_ value: Int) {
        countTask?.cancel()
        targetValue = value
        accessibilityValue = String(value)
        guard !UIAccessibility.isReduceMotionEnabled, window != nil, displayedValue != value else {
            updateValue(value)
            return
        }
        let startValue = displayedValue
        countTask = Task { [weak self] in
            // Animation hữu hạn; Task bị hủy khi thẻ rời màn hình hoặc dữ liệu mới tới.
            for step in 1...18 {
                do { try await Task.sleep(for: .milliseconds(28)) } catch { return }
                guard !Task.isCancelled, let self else { return }
                if UIAccessibility.isReduceMotionEnabled {
                    updateValue(value)
                    return
                }
                let progress = 1 - pow(1 - Double(step) / 18, 3)
                updateValue(startValue + Int((Double(value - startValue) * progress).rounded()))
            }
        }
    }

    func setAccentColor(_ color: UIColor) {
        iconView.tintColor = color
        iconView.backgroundColor = color.withAlphaComponent(0.085)
        valueLabel.textColor = AppTheme.titleColor
    }

    private func updateValue(_ value: Int) {
        displayedValue = value
        valueLabel.text = "\(value)"
    }

    // MARK: - Setup UI

    private func setupUI() {
        iconView.contentMode = .center
        iconView.preferredSymbolConfiguration = .init(pointSize: 18, weight: .medium)
        iconView.layer.cornerRadius = 13
        iconView.translatesAutoresizingMaskIntoConstraints = false
        valueLabel.text = "—"
        valueLabel.font = .monospacedDigitSystemFont(ofSize: 29, weight: .bold)
        titleLabel.font = .systemFont(ofSize: 11, weight: .medium)
        titleLabel.textColor = AppTheme.secondaryTextColor
        titleLabel.numberOfLines = 0
        let top = UIStackView(arrangedSubviews: [iconView, UIView(), valueLabel])
        top.axis = .horizontal
        top.alignment = .center
        top.spacing = 8
        let stack = UIStackView(arrangedSubviews: [top, titleLabel])
        stack.axis = .vertical
        stack.spacing = 13
        stack.translatesAutoresizingMaskIntoConstraints = false
        addSubview(stack)
        NSLayoutConstraint.activate([
            stack.topAnchor.constraint(equalTo: topAnchor, constant: 16),
            stack.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 15),
            stack.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -15),
            stack.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -16),
            iconView.widthAnchor.constraint(equalToConstant: 38),
            iconView.heightAnchor.constraint(equalToConstant: 38)
        ])
        isAccessibilityElement = true
        accessibilityLabel = titleLabel.text
        accessibilityValue = L10n.text("Đang tải")
    }
}
