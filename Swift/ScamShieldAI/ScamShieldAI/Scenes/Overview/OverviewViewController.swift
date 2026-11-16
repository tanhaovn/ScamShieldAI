import UIKit

final class OverviewViewController: UIViewController {

    // MARK: - Constants

    private enum Layout {
        static let horizontalPadding: CGFloat = 20
        static let sectionSpacing: CGFloat = 28
        static let tabBarClearance: CGFloat = 108
    }

    // MARK: - Dependencies

    private let user: User
    private let historyService: HistoryService

    // MARK: - Properties

    var onChooseSource: ((ScanInputKind) -> Void)?
    private let greetingName = UILabel()
    private var adaptiveRows: [UIStackView] = []
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
    private let totalStat = OverviewStatView(title: "Tổng lượt phân tích", systemImageName: "viewfinder")
    private let safeStat = OverviewStatView(title: "Kết quả rủi ro thấp", systemImageName: "checkmark.shield")
    private let suspiciousStat = OverviewStatView(title: "Cần kiểm tra thêm", systemImageName: "waveform.path.ecg")
    private let dangerStat = OverviewStatView(title: "Cảnh báo nguy hiểm", systemImageName: "exclamationmark.triangle")
    private let trendCard = RiskTrendCardView()
    private let distributionCard = RiskDistributionCardView()
    private let recentStack = UIStackView()
    private let statusLabel = UILabel()
    private let averageLabel = UILabel()
    private let recordsLabel = UILabel()

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
        adaptiveRows.forEach {
            $0.axis = largeText ? .vertical : .horizontal
            $0.distribution = largeText ? .fill : .fillEqually
        }
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        let name = UserDefaults.standard.string(forKey: "scamShield.displayName") ?? "bạn"
        greetingName.text = "Xin chào, \(name)"
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

        [makeGreetingHeader(), makeQuickSources(), makeProtectionCard(), makeRecentSection(),
         makeStatisticsSection(), makeAnalyticsSection(), makeSafetyTipCard()]
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
            contentStack.leadingAnchor.constraint(equalTo: scrollView.frameLayoutGuide.leadingAnchor, constant: Layout.horizontalPadding),
            contentStack.trailingAnchor.constraint(equalTo: scrollView.frameLayoutGuide.trailingAnchor, constant: -Layout.horizontalPadding),
            contentStack.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor, constant: -24)
        ])
    }

    func makeGreetingHeader() -> UIView {
        greetingName.text = "Xin chào, bạn"
        greetingName.font = AppTheme.font(size: 15, weight: .medium, style: .subheadline)
        greetingName.adjustsFontForContentSizeCategory = true
        greetingName.textColor = AppTheme.secondaryTextColor
        greetingName.numberOfLines = 0
        let title = makeLabel("An tâm hơn,\nmỗi ngày.", size: 32, weight: .bold, color: AppTheme.titleColor)
        title.accessibilityTraits = .header
        let text = UIStackView(arrangedSubviews: [greetingName, title])
        text.axis = .vertical
        text.spacing = 8
        let mark = UIImageView(image: UIImage(systemName: "checkmark.shield"))
        mark.tintColor = AppTheme.primaryColor
        mark.contentMode = .center
        mark.preferredSymbolConfiguration = .init(pointSize: 26, weight: .medium)
        mark.backgroundColor = AppTheme.softColor
        mark.layer.cornerRadius = 28
        mark.isAccessibilityElement = false
        NSLayoutConstraint.activate([
            mark.widthAnchor.constraint(equalToConstant: 56),
            mark.heightAnchor.constraint(equalToConstant: 56)
        ])
        let header = UIStackView(arrangedSubviews: [text, mark])
        header.alignment = .center
        header.spacing = 16
        return header
    }

    func makeProtectionCard() -> UIView {
        let card = GradientCardView(colors: [AppTheme.brandDark, AppTheme.brandDeep])
        let title = makeLabel("Một bước kiểm tra.\nThêm một lớp an tâm.", size: 23, weight: .bold, color: .white)
        title.accessibilityTraits = .header
        let subtitle = makeLabel("Kiểm tra nội dung đáng ngờ trước khi bạn hành động.", size: 14, weight: .regular, color: .white.withAlphaComponent(0.8))
        var config = UIButton.Configuration.filled()
        config.title = "Bắt đầu kiểm tra"
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
        let stack = UIStackView(arrangedSubviews: [title, subtitle, button])
        stack.axis = .vertical
        stack.spacing = 10
        stack.setCustomSpacing(18, after: subtitle)
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
        let averageTitle = makeLabel("Điểm rủi ro trung bình / 100", size: 12, weight: .medium, color: AppTheme.secondaryTextColor)
        averageTitle.numberOfLines = 0
        let averageRow = UIStackView(arrangedSubviews: [averageTitle, averageLabel])
        averageRow.spacing = 12
        let stack = UIStackView(arrangedSubviews: [makeSectionHeading("GÓC NHÌN CỦA BẠN", title: "Tổng quan rủi ro")] + rows + [averageRow])
        stack.axis = .vertical
        stack.spacing = 12
        stack.setCustomSpacing(16, after: stack.arrangedSubviews[0])
        return stack
    }

    func makeAnalyticsSection() -> UIView {
        let stack = UIStackView(arrangedSubviews: [
            makeSectionHeading("PHÂN TÍCH", title: "Dữ liệu trực quan"),
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
        let heading = UIStackView(arrangedSubviews: [makeSectionHeading("DÒNG THỜI GIAN", title: "Phân tích gần đây"), recordsLabel])
        heading.axis = .horizontal
        heading.alignment = .center
        heading.spacing = 8
        let stack = UIStackView(arrangedSubviews: [heading, statusLabel, recentStack])
        stack.axis = .vertical
        stack.spacing = 16
        return stack
    }

    func makeSafetyTipCard() -> UIView {
        let card = CardView()
        card.backgroundColor = AppTheme.softColor
        card.layer.shadowOpacity = 0
        let icon = UIImageView(image: UIImage(systemName: "lightbulb.max"))
        icon.tintColor = AppTheme.primaryColor
        icon.contentMode = .scaleAspectFit
        icon.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            icon.widthAnchor.constraint(equalToConstant: 24),
            icon.heightAnchor.constraint(equalToConstant: 28)
        ])
        let title = makeLabel("Một chút cẩn trọng, thêm an tâm", size: 14, weight: .semibold, color: AppTheme.titleColor)
        title.numberOfLines = 0
        let message = makeLabel("Kiểm tra tên miền và xác minh người gửi trước khi mở liên kết trong tin nhắn.", size: 13, weight: .regular, color: AppTheme.secondaryTextColor)
        message.numberOfLines = 0
        let text = UIStackView(arrangedSubviews: [title, message])
        text.axis = .vertical
        text.spacing = 6
        let row = UIStackView(arrangedSubviews: [icon, text])
        row.alignment = .top
        row.spacing = 12
        row.translatesAutoresizingMaskIntoConstraints = false
        card.addSubview(row)
        NSLayoutConstraint.activate([
            row.topAnchor.constraint(equalTo: card.topAnchor, constant: 18),
            row.leadingAnchor.constraint(equalTo: card.leadingAnchor, constant: 16),
            row.trailingAnchor.constraint(equalTo: card.trailingAnchor, constant: -16),
            row.bottomAnchor.constraint(equalTo: card.bottomAnchor, constant: -18)
        ])
        return card
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
        statusLabel.text = "Đang cập nhật dữ liệu…"
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
                statusLabel.text = "Chưa thể tải dữ liệu mới. Kéo xuống để thử lại."
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
        averageLabel.superview?.accessibilityValue = items.isEmpty ? "Chưa có dữ liệu" : "\(averageLabel.text ?? "") trên 100"


        recentStack.arrangedSubviews.forEach {
            recentStack.removeArrangedSubview($0)
            $0.removeFromSuperview()
        }
        let recentItems = Array(items.prefix(3))
        recordsLabel.text = "\(recentItems.count) bản ghi"
        statusLabel.isHidden = !recentItems.isEmpty
        statusLabel.text = recentItems.isEmpty
            ? "Chưa có lần kiểm tra nào. Chọn loại nội dung để bắt đầu."
            : nil
        recentItems.forEach { recentStack.addArrangedSubview(makeRecentRow(item: $0)) }
        if view.window != nil {
            recentStack.animateFadeAndSlideIn(distance: 5)
        }
    }

    func makeRecentRow(item: ScanHistoryItem) -> UIView {
        let card = CardView()
        let thumbnail = RemoteImageView()
        thumbnail.load(url: Constants.mediaURL(from: item.imageURL), placeholder: UIImage(systemName: (ScanInputKind(rawValue: item.sourceType ?? "image") ?? .image).symbol))
        thumbnail.contentMode = .scaleAspectFill
        thumbnail.clipsToBounds = true
        thumbnail.backgroundColor = AppTheme.softColor
        thumbnail.tintColor = AppTheme.primaryColor
        thumbnail.layer.cornerRadius = 12
        thumbnail.translatesAutoresizingMaskIntoConstraints = false

        let filename = makeLabel(item.originalFilename ?? "Ảnh kiểm tra #\(item.id)", size: 14, weight: .semibold, color: AppTheme.titleColor)
        filename.lineBreakMode = .byTruncatingMiddle
        let date = makeLabel(item.createdAt?.backendDateDisplayText ?? "Không rõ thời gian", size: 11, weight: .regular, color: AppTheme.secondaryTextColor)
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
        let chevron = UIImageView(image: UIImage(systemName: "chevron.right"))
        chevron.tintColor = AppTheme.secondaryTextColor.withAlphaComponent(0.5)
        chevron.contentMode = .scaleAspectFit
        chevron.translatesAutoresizingMaskIntoConstraints = false
        let row = UIStackView(arrangedSubviews: [thumbnail, labels, scoreStack, chevron])
        row.axis = .horizontal
        row.alignment = .center
        row.spacing = 11
        row.translatesAutoresizingMaskIntoConstraints = false
        card.addSubview(row)
        NSLayoutConstraint.activate([
            thumbnail.widthAnchor.constraint(equalToConstant: 54),
            thumbnail.heightAnchor.constraint(equalToConstant: 62),
            chevron.widthAnchor.constraint(equalToConstant: 8),
            row.topAnchor.constraint(equalTo: card.topAnchor, constant: 14),
            row.leadingAnchor.constraint(equalTo: card.leadingAnchor, constant: 13),
            row.trailingAnchor.constraint(equalTo: card.trailingAnchor, constant: -13),
            row.bottomAnchor.constraint(equalTo: card.bottomAnchor, constant: -14)
        ])

        // Nút trong suốt giúp cả thẻ mở được chi tiết và được VoiceOver nhận là một hành động.
        let button = UIButton(type: .system)
        button.translatesAutoresizingMaskIntoConstraints = false
        button.accessibilityLabel = "\(filename.text ?? "Ảnh kiểm tra"), \(item.riskLevel.displayName), \(item.riskScore) trên 100"
        button.accessibilityHint = "Mở chi tiết lần kiểm tra"
        button.addAction(UIAction { [weak self] _ in
            guard let self else { return }
            if let result = item.result {
                let image = item.imageURL.flatMap { Constants.mediaURL(from: $0) }.flatMap { UIImage(contentsOfFile: $0.path) }
                self.navigationController?.pushViewController(ScanResultViewController(result: result, image: image), animated: true)
            } else { self.navigationController?.pushViewController(HistoryDetailViewController(item: item), animated: true) }
        }, for: .touchUpInside)
        row.accessibilityElementsHidden = true
        card.addSubview(button)
        NSLayoutConstraint.activate([
            button.topAnchor.constraint(equalTo: card.topAnchor),
            button.leadingAnchor.constraint(equalTo: card.leadingAnchor),
            button.trailingAnchor.constraint(equalTo: card.trailingAnchor),
            button.bottomAnchor.constraint(equalTo: card.bottomAnchor)
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

private final class OverviewStatView: CardView {

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
        accessibilityValue = "Đang tải"
    }
}

private extension OverviewViewController {
    func makeQuickSources() -> UIView {
        let tiles = ScanInputKind.allCases.map { kind in
            SourceTile(kind: kind) { [weak self] in self?.onChooseSource?(kind) }
        }
        let row = UIStackView(arrangedSubviews: tiles)
        row.distribution = .fillEqually
        row.spacing = 8
        adaptiveRows.append(row)
        let stack = UIStackView(arrangedSubviews: [makeSectionHeading("", title: "Bạn muốn kiểm tra gì?"), row])
        stack.axis = .vertical
        stack.spacing = 14
        return stack
    }
}
