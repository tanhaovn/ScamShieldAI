import UIKit

final class AccountViewController: UIViewController {

    // MARK: - UI Components

    private let contentStack = UIStackView()
    private let identityName = UILabel()
    private let avatarLabel = UILabel()
    private let identityKicker = UILabel()
    private let introSubtitle = UILabel()
    private let signInInfo = UILabel()
    private let storageInfo = UILabel()
    private let roleInfo = UILabel()
    private let privacyDetail = UILabel()
    private let privacyBullets = (0..<2).map { _ in UILabel() }
    private weak var editNameButton: UIButton?
    private let total = ProfileStatView(title: L10n.choose("Đã kiểm tra", "Checked"), symbol: "viewfinder")
    private let safe = ProfileStatView(title: L10n.choose("An toàn", "Safe"), symbol: "checkmark.shield")
    private let review = ProfileStatView(title: L10n.choose("Cần chú ý", "Needs attention"), symbol: "exclamationmark.triangle")
    private let average = ProfileStatView(title: L10n.choose("Rủi ro TB", "Average risk"), symbol: "chart.bar")
    private let historyStatus = UILabel()
    private let activityCount = UILabel()
    private let recentActivity = UIStackView()
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

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        if navigationController?.topViewController !== self {
            navigationController?.setNavigationBarHidden(false, animated: animated)
        }
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        navigationController?.setNavigationBarHidden(true, animated: animated)
        refreshAccountUI()
        refreshCount()
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

private final class ProfileStatView: CardView {
    private let iconBox = UIView()
    private let iconView = UIImageView()
    private let valueLabel = UILabel()

    init(title: String, symbol: String) {
        super.init(frame: .zero)
        iconView.image = UIImage(systemName: symbol)
        iconView.contentMode = .scaleAspectFit
        iconView.preferredSymbolConfiguration = .init(pointSize: 17, weight: .semibold)
        iconView.translatesAutoresizingMaskIntoConstraints = false
        iconBox.layer.cornerRadius = 10
        iconBox.translatesAutoresizingMaskIntoConstraints = false
        iconBox.addSubview(iconView)

        let titleLabel = UILabel()
        titleLabel.text = title
        titleLabel.font = AppTheme.font(size: 11, weight: .medium)
        titleLabel.textColor = AppTheme.secondaryTextColor
        titleLabel.numberOfLines = 2
        valueLabel.text = "—"
        valueLabel.font = .monospacedDigitSystemFont(ofSize: 24, weight: .bold)
        valueLabel.textColor = AppTheme.titleColor
        let copy = UIStackView(arrangedSubviews: [titleLabel, valueLabel])
        copy.axis = .vertical
        copy.spacing = 2
        let row = UIStackView(arrangedSubviews: [iconBox, copy])
        row.alignment = .center
        row.spacing = 10
        row.translatesAutoresizingMaskIntoConstraints = false
        addSubview(row)
        NSLayoutConstraint.activate([
            heightAnchor.constraint(greaterThanOrEqualToConstant: 78),
            row.topAnchor.constraint(equalTo: topAnchor, constant: 10),
            row.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 10),
            row.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -8),
            row.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -10),
            iconBox.widthAnchor.constraint(equalToConstant: 36),
            iconBox.heightAnchor.constraint(equalToConstant: 36),
            iconView.widthAnchor.constraint(equalToConstant: 20),
            iconView.heightAnchor.constraint(equalToConstant: 20),
            iconView.centerXAnchor.constraint(equalTo: iconBox.centerXAnchor),
            iconView.centerYAnchor.constraint(equalTo: iconBox.centerYAnchor)
        ])
        isAccessibilityElement = true
        accessibilityLabel = title
        accessibilityValue = L10n.choose("Đang tải", "Loading")
    }

    required init?(coder: NSCoder) { fatalError("ProfileStatView chỉ được khởi tạo bằng code.") }

    func setAccentColor(_ color: UIColor) {
        iconView.tintColor = color
        iconBox.backgroundColor = color.withAlphaComponent(0.1)
    }

    func setValue(_ value: Int) {
        valueLabel.text = "\(value)"
        accessibilityValue = "\(value)"
    }
}

// MARK: - Setup UI

private extension AccountViewController {

    func storageStartDate() -> String {
        let key = "scamShield.guestSince"
        let defaults = UserDefaults.standard
        let date: Date
        if let existing = defaults.object(forKey: key) as? Date {
            date = existing
        } else {
            date = Date()
            defaults.set(date, forKey: key)
        }
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: L10n.choose("vi_VN", "en_US"))
        formatter.dateStyle = .long
        return formatter.string(from: date)
    }

    func setupUI() {
        navigationItem.title = L10n.choose("Tài khoản của bạn", "Your profile")
        navigationItem.largeTitleDisplayMode = .never
        installAppBackground()
        let scrollView = UIScrollView()
        scrollView.alwaysBounceVertical = true
        scrollView.showsVerticalScrollIndicator = false
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.contentInset.bottom = 24
        contentStack.axis = .vertical
        contentStack.spacing = 12
        contentStack.translatesAutoresizingMaskIntoConstraints = false

        introSubtitle.font = AppTheme.font(size: 12, weight: .medium)
        introSubtitle.textColor = UIColor.white.withAlphaComponent(0.76)
        introSubtitle.numberOfLines = 0
        let intro = UIStackView(arrangedSubviews: [
            label("SCAMSHIELD · \(L10n.choose("HỒ SƠ", "PROFILE"))", size: 10, color: AppTheme.primaryColor),
            label(L10n.choose("Cá nhân", "Profile"), size: 27, color: AppTheme.titleColor)
        ])
        intro.axis = .vertical
        intro.spacing = 4
        [intro, makeIdentityCard(), makeStatistics(), makeProfileInformation(), makePrivacyCard(), makeRecentActivity(),
         makePreferencesCard()].forEach(contentStack.addArrangedSubview)
        contentStack.setCustomSpacing(18, after: intro)
        view.addSubview(scrollView)
        scrollView.addSubview(contentStack)
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            contentStack.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor, constant: 12),
            contentStack.widthAnchor.constraint(equalTo: scrollView.frameLayoutGuide.widthAnchor, constant: -2 * 16),
            contentStack.leadingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.leadingAnchor, constant: 16),
            contentStack.trailingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.trailingAnchor, constant: -16),
            contentStack.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor, constant: -24)
        ])
    }

    func makeIdentityCard() -> UIView {
        let card = GradientCardView(colors: [AppTheme.brandDark, AppTheme.brandDeep])
        avatarLabel.text = "ND"
        avatarLabel.textAlignment = .center
        avatarLabel.font = AppTheme.font(size: 20, weight: .bold)
        avatarLabel.textColor = AppTheme.brandDeep
        avatarLabel.backgroundColor = UIColor.white.withAlphaComponent(0.94)
        avatarLabel.layer.cornerRadius = 16
        avatarLabel.clipsToBounds = true
        avatarLabel.translatesAutoresizingMaskIntoConstraints = false
        identityKicker.text = L10n.choose("HỒ SƠ TRÊN THIẾT BỊ", "ON-DEVICE PROFILE")
        identityKicker.font = AppTheme.font(size: 10, weight: .bold)
        identityKicker.textColor = AppTheme.mintColor
        let title = identityName
        title.text = UserDefaults.standard.string(forKey: "scamShield.displayName") ?? L10n.text("Người dùng khách")
        title.font = AppTheme.displayFont(size: 20, weight: .bold)
        title.adjustsFontForContentSizeCategory = true
        title.textColor = .white
        title.numberOfLines = 0
        let text = UIStackView(arrangedSubviews: [identityKicker, title, introSubtitle])
        text.axis = .vertical
        text.spacing = 4
        text.setCustomSpacing(7, after: title)
        let row = UIStackView(arrangedSubviews: [avatarLabel, text])
        row.alignment = .center
        row.spacing = 14
        let stack = UIStackView(arrangedSubviews: [row])
        stack.axis = .vertical
        pin(stack, inside: card, padding: 17)
        NSLayoutConstraint.activate([
            avatarLabel.widthAnchor.constraint(equalToConstant: 58),
            avatarLabel.heightAnchor.constraint(equalToConstant: 58)
        ])
        return card
    }

    func makeStatistics() -> UIView {
        total.setAccentColor(AppTheme.primaryColor)
        safe.setAccentColor(AppTheme.safeColor)
        review.setAccentColor(AppTheme.suspiciousColor)
        average.setAccentColor(AppTheme.primaryColor)
        let adapt: (UIStackView) -> Void = { row in
            let largeText = row.traitCollection.preferredContentSizeCategory.isAccessibilityCategory
            row.axis = largeText ? .vertical : .horizontal
            row.distribution = largeText ? .fill : .fillEqually
        }
        let rows = [[total, safe], [review, average]].map { cells in
            let row = UIStackView(arrangedSubviews: cells)
            row.spacing = 8
            adapt(row)
            row.registerForTraitChanges([UITraitPreferredContentSizeCategory.self]) { (row: UIStackView, _) in adapt(row) }
            return row
        }
        historyStatus.textColor = AppTheme.secondaryTextColor
        historyStatus.font = .preferredFont(forTextStyle: .footnote)
        historyStatus.numberOfLines = 0
        historyStatus.isHidden = true
        let stats = UIStackView(arrangedSubviews: rows + [historyStatus])
        stats.axis = .vertical
        stats.spacing = 8
        return stats
    }

    func makeProfileInformation() -> UIView {
        let card = CardView()
        let title = label(L10n.choose("Thông tin tài khoản", "Account information"), size: 17, color: AppTheme.titleColor)
        var editConfig = UIButton.Configuration.tinted()
        editConfig.title = L10n.choose("Chỉnh sửa", "Edit")
        editConfig.image = UIImage(systemName: "pencil")
        editConfig.imagePadding = 5
        editConfig.baseForegroundColor = AppTheme.primaryColor
        editConfig.baseBackgroundColor = AppTheme.softColor
        editConfig.cornerStyle = .capsule
        let edit = UIButton(configuration: editConfig, primaryAction: UIAction { [weak self] _ in self?.editName() })
        editNameButton = edit
        let heading = UIStackView(arrangedSubviews: [title, edit])
        heading.alignment = .center
        heading.distribution = .equalSpacing
        let rows = [
            infoRow("envelope", L10n.choose("Đăng nhập", "Sign in"), L10n.choose("Không yêu cầu đăng nhập hoặc đăng ký", "No sign in or registration required"), valueLabel: signInInfo),
            infoRow("key", L10n.choose("Cách bảo vệ dữ liệu", "Data protection"), L10n.choose("Lưu riêng trên thiết bị", "Stored only on this device"), valueLabel: storageInfo),
            infoRow("calendar", L10n.choose("Bắt đầu lưu trên thiết bị", "Storage started"), storageStartDate()),
            infoRow("checkmark.shield", L10n.choose("Quyền sử dụng", "Access"), L10n.choose("Người dùng thông thường", "Standard user"), valueLabel: roleInfo)
        ]
        let stack = UIStackView(arrangedSubviews: [heading] + rows)
        stack.axis = .vertical
        stack.spacing = 6
        stack.setCustomSpacing(12, after: heading)
        pin(stack, inside: card, padding: 16)
        return card
    }

    func infoRow(_ symbol: String, _ caption: String, _ value: String, valueLabel: UILabel? = nil) -> UIView {
        let icon = UIImageView(image: UIImage(systemName: symbol))
        icon.tintColor = AppTheme.primaryColor
        icon.contentMode = .scaleAspectFit
        icon.preferredSymbolConfiguration = .init(pointSize: 16, weight: .medium)
        let iconBox = UIView()
        iconBox.backgroundColor = AppTheme.softColor
        iconBox.layer.cornerRadius = 10
        iconBox.translatesAutoresizingMaskIntoConstraints = false
        icon.translatesAutoresizingMaskIntoConstraints = false
        iconBox.addSubview(icon)
        let small = label(caption, size: 11, color: AppTheme.secondaryTextColor)
        let strong = valueLabel ?? UILabel()
        strong.text = value
        strong.font = AppTheme.font(size: 13, weight: .semibold)
        strong.textColor = AppTheme.titleColor
        strong.numberOfLines = 0
        let copy = UIStackView(arrangedSubviews: [small, strong])
        copy.axis = .vertical
        copy.spacing = 2
        let row = UIStackView(arrangedSubviews: [iconBox, copy])
        row.alignment = .center
        row.spacing = 10
        row.isLayoutMarginsRelativeArrangement = true
        row.layoutMargins = UIEdgeInsets(top: 8, left: 9, bottom: 8, right: 9)
        row.backgroundColor = AppTheme.fieldBackgroundColor
        row.layer.cornerRadius = 11
        NSLayoutConstraint.activate([
            row.heightAnchor.constraint(greaterThanOrEqualToConstant: 58),
            iconBox.widthAnchor.constraint(equalToConstant: 34),
            iconBox.heightAnchor.constraint(equalToConstant: 34),
            icon.centerXAnchor.constraint(equalTo: iconBox.centerXAnchor),
            icon.centerYAnchor.constraint(equalTo: iconBox.centerYAnchor),
            icon.widthAnchor.constraint(equalToConstant: 20),
            icon.heightAnchor.constraint(equalToConstant: 20)
        ])
        return row
    }

    func makePrivacyCard() -> UIView {
        let card = CardView()
        let shield = UIImageView(image: UIImage(systemName: "checkmark.shield.fill"))
        shield.tintColor = AppTheme.primaryColor
        shield.contentMode = .scaleAspectFit
        shield.translatesAutoresizingMaskIntoConstraints = false
        let heading = label(L10n.choose("Dữ liệu của bạn", "Your data"), size: 17, color: AppTheme.titleColor)
        let headingRow = UIStackView(arrangedSubviews: [shield, heading])
        headingRow.alignment = .center
        headingRow.spacing = 9
        privacyDetail.text = L10n.choose("Chỉ gửi nội dung khi bạn nhấn Phân tích. Lịch sử khách lưu trên iPhone này.",
                                         "Content is sent only when you tap Analyze. Guest history stays on this iPhone.")
        privacyDetail.font = AppTheme.font(size: 12)
        privacyDetail.textColor = AppTheme.secondaryTextColor
        privacyDetail.numberOfLines = 0
        let bulletTexts = [
            L10n.choose("✓ Không yêu cầu email hoặc mật khẩu", "✓ No email or password required"),
            L10n.choose("✓ Không tạo tài khoản khách trên máy chủ", "✓ No guest account on the server")
        ]
        for (index, bullet) in privacyBullets.enumerated() {
            bullet.text = bulletTexts[index]
            bullet.font = AppTheme.font(size: 11, weight: .medium)
            bullet.textColor = AppTheme.titleColor
            bullet.numberOfLines = 0
        }
        let stack = UIStackView(arrangedSubviews: [headingRow, privacyDetail] + privacyBullets + [makePrivacyButton()])
        stack.axis = .vertical
        stack.spacing = 7
        stack.setCustomSpacing(10, after: headingRow)
        stack.setCustomSpacing(12, after: privacyBullets.last!)
        pin(stack, inside: card, padding: 16)
        NSLayoutConstraint.activate([
            shield.widthAnchor.constraint(equalToConstant: 21),
            shield.heightAnchor.constraint(equalToConstant: 21)
        ])
        return card
    }

    func makePrivacyButton() -> UIView {
        var configuration = UIButton.Configuration.plain()
        configuration.title = L10n.choose("Xem chính sách quyền riêng tư", "View privacy policy")
        configuration.image = UIImage(systemName: "arrow.up.right")
        configuration.imagePadding = 8
        configuration.baseForegroundColor = AppTheme.primaryColor
        configuration.background.backgroundColor = AppTheme.softColor
        configuration.background.cornerRadius = 10
        configuration.contentInsets = .init(top: 8, leading: 12, bottom: 8, trailing: 12)
        let button = UIButton(configuration: configuration)
        button.contentHorizontalAlignment = .leading
        button.accessibilityHint = L10n.text("Mở thông tin về dữ liệu được xử lý và lưu trữ")
        button.addTarget(self, action: #selector(openPrivacyPolicy), for: .touchUpInside)
        button.enableSoftPressAnimation()
        button.heightAnchor.constraint(greaterThanOrEqualToConstant: 42).isActive = true
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

    func refreshAccountUI() {
        let user = AccountSession.shared.user
        let signedIn = user != nil
        identityKicker.text = user?.role == "admin"
            ? L10n.choose("QUẢN TRỊ VIÊN", "ADMINISTRATOR")
            : signedIn ? L10n.choose("TÀI KHOẢN ĐÃ XÁC THỰC", "VERIFIED ACCOUNT")
                       : L10n.choose("HỒ SƠ TRÊN THIẾT BỊ", "ON-DEVICE PROFILE")
        identityName.text = user?.fullName ?? user?.email ?? UserDefaults.standard.string(forKey: "scamShield.displayName") ?? L10n.text("Người dùng khách")
        let nameParts = (identityName.text ?? "").split(whereSeparator: \.isWhitespace)
        let firstInitial = nameParts.first?.first.map(String.init) ?? ""
        let lastInitial = nameParts.count > 1 ? (nameParts.last?.first.map(String.init) ?? "") : ""
        avatarLabel.text = (firstInitial + lastInitial).uppercased()
        introSubtitle.text = signedIn
            ? (user?.email ?? L10n.choose("Tài khoản đã xác thực", "Verified account"))
            : L10n.choose("Lịch sử lưu riêng trên iPhone này", "History stays on this iPhone")
        signInInfo.text = user?.email ?? L10n.choose("Không yêu cầu đăng nhập hoặc đăng ký", "No sign in or registration required")
        storageInfo.text = signedIn ? L10n.choose("Máy chủ và bản sao trên iPhone", "Server and iPhone copy")
                                    : L10n.choose("Lưu riêng trên thiết bị", "Stored only on this device")
        roleInfo.text = user?.role == "admin" ? "Admin" : L10n.choose("Người dùng thông thường", "Standard user")
        editNameButton?.isHidden = signedIn
        privacyDetail.text = signedIn
            ? L10n.choose("Lịch sử tài khoản tải từ máy chủ; lượt kiểm tra trên iPhone cũng được lưu cục bộ.",
                          "Account history loads from the server; iPhone scans also keep a local copy.")
            : L10n.choose("Chỉ gửi nội dung khi bạn nhấn Phân tích. Lịch sử khách lưu trên iPhone này.",
                          "Content is sent only when you tap Analyze. Guest history stays on this iPhone.")
        let values = signedIn ? [
                L10n.choose("✓ Phiên đăng nhập lưu an toàn trong Keychain", "✓ Session stored securely in Keychain"),
                L10n.choose("✓ Chỉ tài khoản này xem được lịch sử của mình", "✓ Only this account can view its history")
            ] : [
                L10n.choose("✓ Không yêu cầu email hoặc mật khẩu", "✓ No email or password required"),
                L10n.choose("✓ Không tạo tài khoản khách trên máy chủ", "✓ No guest account on the server")
            ]
        for (label, value) in zip(privacyBullets, values) { label.text = value }
    }

    func refreshCount() {
        historyTask?.cancel()
        historyTask = Task { [weak self] in
            guard let self else { return }
            do {
                let local = try await historyService.fetchHistory()
                var history = local
                var syncError = false
                if AccountSession.shared.token != nil {
                    do {
                        if !AccountSession.shared.isAuthenticated { try await AccountSession.shared.restore() }
                        let account = try await historyService.fetchAccountHistory()
                        history = HistoryService.merge(local: local, account: account)
                    } catch {
                        syncError = true
                    }
                }
                let count = history.count
                guard !Task.isCancelled else { return }
                refreshAccountUI()
                historyStatus.text = L10n.choose("Chưa tải được lịch sử máy chủ. Mở lại trang để thử tiếp.",
                                                 "Server history is unavailable. Reopen this page to retry.")
                historyStatus.isHidden = !syncError
                total.setValue(count)
                safe.setValue(history.filter { $0.riskLevel == .safe }.count)
                review.setValue(history.filter { $0.riskLevel == .suspicious }.count)
                let riskSum = history.reduce(0) { $0 + $1.riskScore }
                average.setValue(count == 0 ? 0 : Int((Double(riskSum) / Double(count)).rounded()))
                activityCount.text = L10n.choose("\(count) bản ghi", "\(count) records")
                recentActivity.arrangedSubviews.forEach { $0.removeFromSuperview() }
                for item in history.prefix(5) {
                    recentActivity.addArrangedSubview(makeActivityRow(item))
                }
                if history.isEmpty {
                    recentActivity.addArrangedSubview(label(L10n.choose("Chưa có lượt kiểm tra nào.", "No checks yet."),
                                                           size: 13, color: AppTheme.secondaryTextColor))
                }
            } catch {
                historyStatus.text = L10n.text("Không đọc được")
                historyStatus.isHidden = false
            }
        }
    }

    @objc func openPrivacyPolicy() {
        navigationController?.pushViewController(PrivacyPolicyViewController(), animated: true)
    }


}

private extension AccountViewController {
    func makePreferencesCard() -> UIView {
        let card = CardView()
        let title = label(L10n.choose("Tùy chỉnh", "Preferences"), size: 17, color: AppTheme.titleColor)
        let control = UISegmentedControl(items: [L10n.text("Sáng"), L10n.text("Tối")])
        control.selectedSegmentIndex = traitCollection.userInterfaceStyle == .dark ? 1 : 0
        control.selectedSegmentTintColor = AppTheme.softColor
        control.setTitleTextAttributes([.foregroundColor: AppTheme.titleColor], for: .normal)
        control.heightAnchor.constraint(equalToConstant: 44).isActive = true
        control.accessibilityIdentifier = "settings.appearance"
        control.addAction(UIAction { [weak control] _ in
            guard let control else { return }
            AppearanceSettings.apply(control.selectedSegmentIndex + 1)
            UISelectionFeedbackGenerator().selectionChanged()
        }, for: .valueChanged)
        let languages = UISegmentedControl(items: ["Tiếng Việt", "English"])
        languages.selectedSegmentIndex = L10n.language == "en" ? 1 : 0
        languages.heightAnchor.constraint(equalToConstant: 44).isActive = true
        languages.accessibilityLabel = L10n.choose("Ngôn ngữ", "Language")
        languages.addAction(UIAction { [weak languages] _ in
            L10n.setLanguage(languages?.selectedSegmentIndex == 1 ? "en" : "vi")
        }, for: .valueChanged)
        let appearanceRow = settingRow(title: L10n.choose("Giao diện", "Appearance"), control: control)
        let languageRow = settingRow(title: L10n.choose("Ngôn ngữ", "Language"), control: languages)
        let stack = UIStackView(arrangedSubviews: [title, appearanceRow, languageRow])
        stack.axis = .vertical
        stack.spacing = 10
        stack.setCustomSpacing(14, after: title)
        pin(stack, inside: card, padding: 16)
        return card
    }

    func settingRow(title: String, control: UISegmentedControl) -> UIStackView {
        let caption = label(title, size: 12, color: AppTheme.secondaryTextColor)
        let row = UIStackView(arrangedSubviews: [caption, control])
        row.alignment = .center
        row.spacing = 8
        let adapt: (UIStackView) -> Void = { row in
            let largeText = row.traitCollection.preferredContentSizeCategory.isAccessibilityCategory
            row.axis = largeText ? .vertical : .horizontal
            row.distribution = largeText ? .fill : .equalSpacing
        }
        adapt(row)
        row.registerForTraitChanges([UITraitPreferredContentSizeCategory.self]) { (row: UIStackView, _) in adapt(row) }
        return row
    }

    func editName() {
        let alert = UIAlertController(title: L10n.text("Tên hiển thị"), message: L10n.text("Tên chỉ được lưu trên thiết bị của bạn."), preferredStyle: .alert)
        alert.addTextField { field in
            field.placeholder = L10n.text("Bạn muốn được gọi là gì?")
            field.text = UserDefaults.standard.string(forKey: "scamShield.displayName")
            field.autocapitalizationType = .words
        }
        alert.addAction(UIAlertAction(title: L10n.text("Hủy"), style: .cancel))
        let normalizedName: (String?) -> String = { value in
            let normalized = (value ?? "").split(whereSeparator: \.isWhitespace).joined(separator: " ")
            return String(normalized.prefix(100))
        }
        let save = UIAlertAction(title: L10n.text("Lưu"), style: .default) { [weak self, weak alert] _ in
            let value = normalizedName(alert?.textFields?.first?.text)
            guard value.count >= 2 else { return }
            UserDefaults.standard.set(value, forKey: "scamShield.displayName")
            self?.identityName.text = value
            let parts = value.split(whereSeparator: \.isWhitespace)
            let first = parts.first?.first.map(String.init) ?? ""
            let last = parts.count > 1 ? (parts.last?.first.map(String.init) ?? "") : ""
            self?.avatarLabel.text = (first + last).uppercased()
        }
        if let field = alert.textFields?.first {
            field.accessibilityHint = L10n.choose("Tên hiển thị phải có ít nhất 2 ký tự.", "Use at least 2 characters.")
            save.isEnabled = normalizedName(field.text).count >= 2
            field.addAction(UIAction { [weak field, weak save] _ in
                save?.isEnabled = normalizedName(field?.text).count >= 2
            }, for: .editingChanged)
        }
        alert.addAction(save)
        present(alert, animated: true)
    }

    func makeRecentActivity() -> UIView {
        let card = CardView()
        recentActivity.axis = .vertical
        recentActivity.spacing = 6
        activityCount.font = AppTheme.font(size: 11, weight: .semibold)
        activityCount.textColor = AppTheme.primaryColor
        activityCount.text = L10n.choose("0 bản ghi", "0 records")
        activityCount.setContentHuggingPriority(.required, for: .horizontal)
        let heading = UIStackView(arrangedSubviews: [label(L10n.choose("Hoạt động gần đây", "Recent activity"),
                                                           size: 17, color: AppTheme.titleColor), activityCount])
        heading.alignment = .center
        heading.spacing = 8
        let stack = UIStackView(arrangedSubviews: [heading, recentActivity])
        stack.axis = .vertical
        stack.spacing = 12
        pin(stack, inside: card, padding: 16)
        return card
    }

    func makeActivityRow(_ item: ScanHistoryItem) -> UIView {
        let color = AppTheme.color(for: item.riskLevel)
        let icon = UIImageView(image: UIImage(systemName: "viewfinder"))
        icon.tintColor = color
        icon.contentMode = .scaleAspectFit
        icon.preferredSymbolConfiguration = .init(pointSize: 16, weight: .semibold)
        let iconBox = UIView()
        iconBox.backgroundColor = color.withAlphaComponent(0.1)
        iconBox.layer.cornerRadius = 10
        icon.translatesAutoresizingMaskIntoConstraints = false
        iconBox.addSubview(icon)
        let title = label(item.listTitle, size: 12, color: AppTheme.titleColor)
        title.font = AppTheme.font(size: 12, weight: .semibold)
        title.numberOfLines = 1
        title.lineBreakMode = .byTruncatingMiddle
        let detail = label("\(item.riskLevel.displayName) · \(item.createdAt?.backendDateDisplayText ?? "")",
                           size: 10, color: AppTheme.secondaryTextColor)
        detail.numberOfLines = 1
        let copy = UIStackView(arrangedSubviews: [title, detail])
        copy.axis = .vertical
        copy.spacing = 3
        let score = label("\(item.riskScore)", size: 15, color: color)
        score.font = .monospacedDigitSystemFont(ofSize: 15, weight: .bold)
        score.setContentHuggingPriority(.required, for: .horizontal)
        let row = UIStackView(arrangedSubviews: [iconBox, copy, score])
        row.alignment = .center
        row.spacing = 9
        row.isLayoutMarginsRelativeArrangement = true
        row.layoutMargins = UIEdgeInsets(top: 7, left: 8, bottom: 7, right: 10)
        row.backgroundColor = AppTheme.fieldBackgroundColor
        row.layer.cornerRadius = 11
        NSLayoutConstraint.activate([
            row.heightAnchor.constraint(greaterThanOrEqualToConstant: 56),
            iconBox.widthAnchor.constraint(equalToConstant: 34),
            iconBox.heightAnchor.constraint(equalToConstant: 34),
            icon.widthAnchor.constraint(equalToConstant: 20),
            icon.heightAnchor.constraint(equalToConstant: 20),
            icon.centerXAnchor.constraint(equalTo: iconBox.centerXAnchor),
            icon.centerYAnchor.constraint(equalTo: iconBox.centerYAnchor)
        ])
        row.isAccessibilityElement = true
        row.accessibilityLabel = "\(item.listTitle), \(item.riskLevel.displayName), \(item.riskScore)/100, \(item.createdAt?.backendDateDisplayText ?? "")"
        return row
    }
}
