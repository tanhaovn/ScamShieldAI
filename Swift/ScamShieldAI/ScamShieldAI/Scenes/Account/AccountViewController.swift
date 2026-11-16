import UIKit

final class AccountViewController: UIViewController {

    // MARK: - UI Components

    private let contentStack = UIStackView()
    private let identityName = UILabel()
    private let historyLabel = UILabel()
    private let clearButton = UIButton(type: .system)
    private let historyService = HistoryService()
    private var historyTask: Task<Void, Never>?
    private var hasAnimated = false

    // MARK: - Initialization

    init(user: User) {
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("AccountViewController chỉ được khởi tạo bằng code.")
    }

    deinit { historyTask?.cancel() }

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        refreshCount()
        identityName.text = UserDefaults.standard.string(forKey: "scamShield.displayName") ?? "Người dùng khách"
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        guard !hasAnimated else { return }
        hasAnimated = true
        for (index, view) in contentStack.arrangedSubviews.enumerated() {
            view.animateFadeAndSlideIn(delay: Double(index) * 0.06, distance: 16)
        }
    }
}

// MARK: - Setup UI

private extension AccountViewController {

    func setupUI() {
        navigationItem.title = "Không gian riêng"
        navigationItem.largeTitleDisplayMode = .never
        installAppBackground()
        let scrollView = UIScrollView()
        scrollView.alwaysBounceVertical = true
        scrollView.showsVerticalScrollIndicator = false
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.contentInset.bottom = 100
        contentStack.axis = .vertical
        contentStack.spacing = 24
        contentStack.translatesAutoresizingMaskIntoConstraints = false

        let privacy = InformationCardView(title: "Bạn kiểm soát dữ liệu", systemImageName: "hand.raised.fill")
        privacy.configure(text: "Nội dung bạn chọn được gửi đến máy chủ để phân tích. Lịch sử của app lưu riêng trên thiết bị, không tự đồng bộ với web. Gỡ ứng dụng sẽ xóa dữ liệu cục bộ.")
        let safety = InformationCardView(title: "Một bước xác minh thêm", systemImageName: "checkmark.shield")
        safety.configure(text: "Điểm rủi ro là tín hiệu tham khảo. Hãy đối chiếu với nguồn chính thức trước khi chuyển tiền hoặc cung cấp thông tin cá nhân.")

        let version = label("SCAMSHIELD AI  /  \(Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0")", size: 10, color: AppTheme.secondaryTextColor)
        version.textAlignment = .center
        [makeIdentityCard(), makePreferencesCard(), makePermissionsCard(), makeStorageCard(), privacy, safety, makePrivacyButton(), version].forEach(contentStack.addArrangedSubview)
        view.addSubview(scrollView)
        scrollView.addSubview(contentStack)
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            contentStack.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor, constant: 16),
            contentStack.leadingAnchor.constraint(equalTo: scrollView.frameLayoutGuide.leadingAnchor, constant: 20),
            contentStack.trailingAnchor.constraint(equalTo: scrollView.frameLayoutGuide.trailingAnchor, constant: -20),
            contentStack.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor, constant: -28)
        ])
    }

    func makeIdentityCard() -> UIView {
        let card = GradientCardView(colors: [AppTheme.brandDark, AppTheme.brandDeep])
        let radar = UIImageView(image: UIImage(systemName: "person.crop.circle.fill"))
        radar.tintColor = AppTheme.mintColor
        radar.contentMode = .scaleAspectFit
        radar.isAccessibilityElement = false
        radar.translatesAutoresizingMaskIntoConstraints = false
        let kicker = label("KHÔNG GIAN CỦA BẠN", size: 10, color: AppTheme.mintColor)
        let title = identityName
        title.text = UserDefaults.standard.string(forKey: "scamShield.displayName") ?? "Người dùng khách"
        title.font = AppTheme.displayFont(size: 24, weight: .bold)
        title.adjustsFontForContentSizeCategory = true
        title.textColor = .white
        title.numberOfLines = 0
        let subtitle = label("Sử dụng ngay, không cần tài khoản.", size: 14, color: .white.withAlphaComponent(0.8))
        subtitle.numberOfLines = 0
        let text = UIStackView(arrangedSubviews: [kicker, title])
        text.axis = .vertical
        text.spacing = 6
        let row = UIStackView(arrangedSubviews: [radar, text])
        row.alignment = .center
        row.spacing = 16
        var editConfig = UIButton.Configuration.tinted()
        editConfig.title = "Đổi tên hiển thị"
        editConfig.image = UIImage(systemName: "pencil")
        editConfig.imagePadding = 8
        editConfig.baseForegroundColor = AppTheme.mintColor
        editConfig.baseBackgroundColor = AppTheme.mintColor
        editConfig.cornerStyle = .capsule
        editConfig.contentInsets = .init(top: 12, leading: 16, bottom: 12, trailing: 16)
        let edit = UIButton(configuration: editConfig, primaryAction: UIAction { [weak self] _ in self?.editName() })
        let stack = UIStackView(arrangedSubviews: [row, subtitle, edit])
        stack.axis = .vertical
        stack.spacing = 16
        pin(stack, inside: card, padding: 22)
        NSLayoutConstraint.activate([
            radar.widthAnchor.constraint(equalToConstant: 52),
            radar.heightAnchor.constraint(equalToConstant: 52)
        ])
        return card
    }

    func makeStorageCard() -> UIView {
        let card = CardView()
        let heading = label("Lịch sử trên thiết bị", size: 18, color: AppTheme.titleColor)
        historyLabel.font = .monospacedDigitSystemFont(ofSize: 34, weight: .bold)
        historyLabel.textColor = AppTheme.primaryColor
        historyLabel.text = "—"
        let detail = label("lượt kiểm tra đã lưu", size: 13, color: AppTheme.secondaryTextColor)
        var config = UIButton.Configuration.tinted()
        config.title = "Xóa lịch sử trên thiết bị"
        config.image = UIImage(systemName: "trash")
        config.imagePadding = 8
        config.baseForegroundColor = AppTheme.dangerousColor
        config.baseBackgroundColor = AppTheme.dangerousColor.withAlphaComponent(0.08)
        config.cornerStyle = .medium
        config.contentInsets = .init(top: 14, leading: 12, bottom: 14, trailing: 12)
        clearButton.configuration = config
        clearButton.enableSoftPressAnimation()
        clearButton.addTarget(self, action: #selector(confirmClear), for: .touchUpInside)
        var exportConfig = UIButton.Configuration.tinted()
        exportConfig.title = "Xuất kết quả (JSON)"
        exportConfig.image = UIImage(systemName: "square.and.arrow.up")
        exportConfig.imagePadding = 8
        exportConfig.baseForegroundColor = AppTheme.primaryColor
        exportConfig.baseBackgroundColor = AppTheme.primaryColor
        let export = UIButton(configuration: exportConfig, primaryAction: UIAction { [weak self] _ in self?.exportHistory() })
        let count = UIStackView(arrangedSubviews: [historyLabel, detail])
        count.alignment = .firstBaseline
        count.spacing = 10
        historyLabel.setContentHuggingPriority(.required, for: .horizontal)
        let stack = UIStackView(arrangedSubviews: [heading, count, export, clearButton])
        stack.axis = .vertical
        stack.spacing = 10
        stack.setCustomSpacing(20, after: count)
        pin(stack, inside: card, padding: 20)
        return card
    }

    func makePrivacyButton() -> UIView {
        var configuration = UIButton.Configuration.plain()
        configuration.title = "Đọc chính sách quyền riêng tư"
        configuration.image = UIImage(systemName: "hand.raised.fill")
        configuration.imagePadding = 8
        configuration.baseForegroundColor = AppTheme.primaryColor
        let button = UIButton(configuration: configuration)
        button.contentHorizontalAlignment = .center
        button.accessibilityHint = "Mở thông tin về dữ liệu được xử lý và lưu trữ"
        button.addTarget(self, action: #selector(openPrivacyPolicy), for: .touchUpInside)
        button.enableSoftPressAnimation()
        return button
    }

    func pin(_ stack: UIStackView, inside card: UIView, padding: CGFloat) {
        stack.translatesAutoresizingMaskIntoConstraints = false
        card.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.topAnchor.constraint(equalTo: card.topAnchor, constant: padding),
            stack.leadingAnchor.constraint(equalTo: card.leadingAnchor, constant: padding),
            stack.trailingAnchor.constraint(equalTo: card.trailingAnchor, constant: -padding),
            stack.bottomAnchor.constraint(equalTo: card.bottomAnchor, constant: -padding)
        ])
    }

    func label(_ text: String, size: CGFloat, color: UIColor) -> UILabel {
        let label = UILabel()
        label.text = text
        label.font = AppTheme.font(size: size, weight: size >= 18 ? .bold : .medium)
        label.adjustsFontForContentSizeCategory = true
        label.numberOfLines = 0
        label.textColor = color
        return label
    }
}

// MARK: - Local History Actions

private extension AccountViewController {

    func refreshCount() {
        historyTask?.cancel()
        historyTask = Task { [weak self] in
            guard let self else { return }
            do {
                let count = try await historyService.fetchHistory().count
                guard !Task.isCancelled else { return }
                historyLabel.text = "\(count)"
                clearButton.isEnabled = count > 0
            } catch {
                historyLabel.text = "Không đọc được"
                clearButton.isEnabled = false
            }
        }
    }

    @objc func confirmClear() {
        let alert = UIAlertController(title: "Xóa toàn bộ lịch sử?", message: "Ảnh và kết quả đã lưu trên thiết bị sẽ bị xóa. Thao tác này không thể hoàn tác.", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "Giữ lại", style: .cancel))
        alert.addAction(UIAlertAction(title: "Xóa lịch sử", style: .destructive) { [weak self] _ in
            self?.clearHistory()
        })
        present(alert, animated: true)
    }

    @objc func openPrivacyPolicy() {
        navigationController?.pushViewController(PrivacyPolicyViewController(), animated: true)
    }

    func clearHistory() {
        clearButton.isEnabled = false
        historyTask = Task { [weak self] in
            guard let self else { return }
            do {
                _ = try await historyService.clearHistory()
                historyLabel.text = "0"
                NotificationCenter.default.post(name: .historyDidChange, object: nil)
                UINotificationFeedbackGenerator().notificationOccurred(.success)
            } catch {
                clearButton.isEnabled = true
                showErrorAlert(message: "Không thể xóa lịch sử lúc này. Vui lòng thử lại.")
            }
        }
    }
}

private extension AccountViewController {
    func makePreferencesCard() -> UIView {
        let card = CardView()
        let title = label("Giao diện", size: 18, color: AppTheme.titleColor)
        let subtitle = label("Chọn cách hiển thị phù hợp với bạn", size: 13, color: AppTheme.secondaryTextColor)
        subtitle.numberOfLines = 0
        let control = UISegmentedControl(items: ["Hệ thống", "Sáng", "Tối"])
        control.selectedSegmentIndex = AppearanceSettings.selection
        control.selectedSegmentTintColor = AppTheme.softColor
        control.setTitleTextAttributes([.foregroundColor: AppTheme.titleColor], for: .normal)
        control.heightAnchor.constraint(equalToConstant: 44).isActive = true
        control.accessibilityIdentifier = "settings.appearance"
        control.addAction(UIAction { [weak control] _ in
            guard let control else { return }
            AppearanceSettings.apply(control.selectedSegmentIndex)
            UISelectionFeedbackGenerator().selectionChanged()
        }, for: .valueChanged)
        let stack = UIStackView(arrangedSubviews: [title, subtitle, control])
        stack.axis = .vertical
        stack.spacing = 12
        pin(stack, inside: card, padding: 20)
        return card
    }

    func editName() {
        let alert = UIAlertController(title: "Tên hiển thị", message: "Tên chỉ được lưu trên thiết bị của bạn.", preferredStyle: .alert)
        alert.addTextField { field in
            field.placeholder = "Bạn muốn được gọi là gì?"
            field.text = UserDefaults.standard.string(forKey: "scamShield.displayName")
            field.autocapitalizationType = .words
        }
        alert.addAction(UIAlertAction(title: "Hủy", style: .cancel))
        alert.addAction(UIAlertAction(title: "Lưu", style: .default) { [weak self, weak alert] _ in
            let value = String((alert?.textFields?.first?.text ?? "").trimmingCharacters(in: .whitespacesAndNewlines).prefix(40))
            UserDefaults.standard.set(value.isEmpty ? "bạn" : value, forKey: "scamShield.displayName")
            self?.identityName.text = value.isEmpty ? "bạn" : value
        })
        present(alert, animated: true)
    }

    func exportHistory() {
        Task { [weak self] in
            guard let self else { return }
            do {
                let items = try await historyService.fetchHistory()
                let encoder = JSONEncoder()
                encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
                let url = FileManager.default.temporaryDirectory.appendingPathComponent("ScamShield-history-\(UUID().uuidString).json")
                try encoder.encode(items).write(to: url, options: .atomic)
                let share = UIActivityViewController(activityItems: [url], applicationActivities: nil)
                share.popoverPresentationController?.sourceView = view
                share.popoverPresentationController?.sourceRect = CGRect(x: view.bounds.midX, y: view.bounds.midY, width: 1, height: 1)
                share.completionWithItemsHandler = { _, _, _, _ in try? FileManager.default.removeItem(at: url) }
                present(share, animated: true)
            } catch { showErrorAlert(message: "Không xuất được lịch sử. Vui lòng thử lại.") }
        }
    }
}

private extension AccountViewController {
    func makePermissionsCard() -> UIView {
        let card = CardView()
        let title = label("Quyền truy cập", size: 18, color: AppTheme.titleColor)
        let detail = label("Bạn luôn là người quyết định", size: 13, color: AppTheme.secondaryTextColor)
        let stack = UIStackView(arrangedSubviews: [title, detail])
        stack.axis = .vertical
        stack.spacing = 16
        for (icon, text) in [("photo", "Ảnh và tệp · Chỉ nội dung bạn chọn"), ("camera", "Camera · Xin quyền khi chụp ảnh"), ("mic.slash", "Micro · App không thu âm")] {
            let symbol = UIImageView(image: UIImage(systemName: icon))
            symbol.tintColor = AppTheme.primaryColor
            symbol.contentMode = .scaleAspectFit
            symbol.widthAnchor.constraint(equalToConstant: 24).isActive = true
            let caption = label(text, size: 14, color: AppTheme.titleColor)
            caption.numberOfLines = 0
            let row = UIStackView(arrangedSubviews: [symbol, caption])
            row.spacing = 12
            stack.addArrangedSubview(row)
        }
        var config = UIButton.Configuration.tinted()
        config.title = "Quản lý thông báo"
        config.image = UIImage(systemName: "bell.badge")
        config.imagePadding = 10
        config.baseForegroundColor = AppTheme.primaryColor
        config.baseBackgroundColor = AppTheme.softColor
        config.contentInsets = .init(top: 14, leading: 16, bottom: 14, trailing: 16)
        let button = UIButton(configuration: config, primaryAction: UIAction { [weak self] _ in
            guard let self else { return }
            AccessConsent.notifications(on: self)
        })
        stack.addArrangedSubview(button)
        pin(stack, inside: card, padding: 22)
        return card
    }
}
