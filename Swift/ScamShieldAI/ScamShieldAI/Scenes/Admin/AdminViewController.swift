import UIKit

final class AdminViewController: UIViewController {
    private let session = AccountSession.shared
    private let scrollView = UIScrollView()
    private let contentStack = UIStackView()
    private let accountField = UITextField()
    private let passwordField = UITextField()
    private let errorLabel = UILabel()
    private var submitButton: UIButton?

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        if session.token != nil {
            renderLoading()
            Task { [weak self] in
                guard let self else { return }
                do { try await session.restore() }
                catch { self.renderLogin(error: error.localizedDescription); return }
                if session.isSignedIn { self.renderDashboard() }
                else { self.renderLogin(error: L10n.choose("Tài khoản hiện tại không có quyền Admin.", "Current account has no Admin access.")) }
            }
        } else {
            renderLogin()
        }
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        navigationController?.setNavigationBarHidden(true, animated: animated)
        if isViewLoaded {
            if session.isSignedIn { renderDashboard() }
            else if session.user != nil || session.token == nil { renderLogin() }
        }
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        if navigationController?.topViewController !== self {
            navigationController?.setNavigationBarHidden(false, animated: animated)
        }
    }

    private func setupUI() {
        view.backgroundColor = AppTheme.pageBackgroundColor
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.keyboardDismissMode = .interactive
        scrollView.showsVerticalScrollIndicator = false
        scrollView.contentInset.bottom = 96
        contentStack.axis = .vertical
        contentStack.spacing = 12
        contentStack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(scrollView)
        scrollView.addSubview(contentStack)
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            contentStack.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor, constant: 16),
            contentStack.leadingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.leadingAnchor, constant: 16),
            contentStack.trailingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.trailingAnchor, constant: -16),
            contentStack.widthAnchor.constraint(equalTo: scrollView.frameLayoutGuide.widthAnchor, constant: -32),
            contentStack.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor, constant: -24)
        ])
    }

    private func clearContent() {
        contentStack.arrangedSubviews.forEach {
            contentStack.removeArrangedSubview($0)
            $0.removeFromSuperview()
        }
    }

    private func renderLoading() {
        clearContent()
        let indicator = UIActivityIndicatorView(style: .large)
        indicator.color = AppTheme.primaryColor
        indicator.startAnimating()
        contentStack.addArrangedSubview(indicator)
        contentStack.addArrangedSubview(makeLabel(L10n.choose("Đang xác thực phiên Admin…", "Checking administrator session…"), size: 15, color: AppTheme.secondaryTextColor))
    }

    private func renderLogin(error: String? = nil) {
        clearContent()
        scrollView.setContentOffset(.zero, animated: false)
        contentStack.addArrangedSubview(makeHero(
            eyebrow: "ADMIN SECURITY GATE",
            title: L10n.choose("Khu vực quản trị hệ thống", "System administration"),
            subtitle: L10n.choose("Quyền truy cập dành riêng cho quản trị viên hệ thống.",
                                  "Access is reserved for system administrators.")))

        let card = CardView()
        let kicker = makeLabel("RESTRICTED ACCESS", size: 10, color: AppTheme.primaryColor, weight: .bold)
        kicker.textAlignment = .center
        let heading = makeLabel(L10n.choose("Đăng nhập Admin", "Administrator sign in"), size: 25, color: AppTheme.titleColor, weight: .bold)
        heading.textAlignment = .center
        let message = makeLabel(L10n.choose("Sử dụng tài khoản có quyền quản trị.",
                                             "Use an account with administrator access."), size: 13, color: AppTheme.secondaryTextColor)
        message.textAlignment = .center
        let accountTitle = makeLabel("Email", size: 13, color: AppTheme.titleColor, weight: .semibold)
        configureField(accountField, placeholder: "you@example.com", secure: false)
        accountField.keyboardType = .emailAddress
        accountField.textContentType = .username
        accountField.autocapitalizationType = .none
        accountField.autocorrectionType = .no
        accountField.accessibilityIdentifier = "admin.account"
        let passwordTitle = makeLabel(L10n.choose("Mật khẩu", "Password"), size: 13, color: AppTheme.titleColor, weight: .semibold)
        configureField(passwordField, placeholder: L10n.choose("Nhập mật khẩu quản trị", "Enter administrator password"), secure: true)
        passwordField.textContentType = .password
        passwordField.accessibilityIdentifier = "admin.password"
        let reveal = UIButton(type: .system)
        reveal.setTitle(L10n.choose("Hiện mật khẩu", "Show password"), for: .normal)
        reveal.tintColor = AppTheme.primaryColor
        reveal.contentHorizontalAlignment = .trailing
        reveal.addAction(UIAction { [weak self, weak reveal] _ in
            guard let self else { return }
            passwordField.isSecureTextEntry.toggle()
            reveal?.setTitle(passwordField.isSecureTextEntry ? L10n.choose("Hiện mật khẩu", "Show password") : L10n.choose("Ẩn mật khẩu", "Hide password"), for: .normal)
        }, for: .touchUpInside)
        errorLabel.font = AppTheme.font(size: 13)
        errorLabel.textColor = AppTheme.dangerousColor
        errorLabel.numberOfLines = 0
        errorLabel.text = error
        errorLabel.isHidden = error == nil
        let submit = actionButton(L10n.choose("Truy cập Admin  →", "Open Admin  →"), filled: true)
        submit.accessibilityIdentifier = "admin.signIn"
        submit.addTarget(self, action: #selector(signIn), for: .touchUpInside)
        submitButton = submit
        let guestButton = actionButton(L10n.choose("← Quay lại chế độ khách", "← Continue as guest"), filled: false)
        guestButton.addAction(UIAction { [weak self] _ in self?.tabBarController?.selectedIndex = 0 }, for: .touchUpInside)
        let stack = UIStackView(arrangedSubviews: [kicker, heading, message, accountTitle, accountField,
                                                   passwordTitle, passwordField, reveal, errorLabel, submit, guestButton])
        stack.axis = .vertical
        stack.spacing = 12
        pin(stack, in: card, padding: 20)
        contentStack.addArrangedSubview(card)
    }

    private func renderDashboard() {
        clearContent()
        scrollView.setContentOffset(.zero, animated: false)
        let name = session.user?.fullName ?? L10n.choose("Quản trị viên", "Administrator")
        contentStack.addArrangedSubview(makeHero(
            eyebrow: "ADMIN CONSOLE · ONLINE",
            title: L10n.choose("Xin chào, \(name)", "Hello, \(name)"),
            subtitle: L10n.choose("Lịch sử tài khoản, dữ liệu huấn luyện và vận hành AI ở ngay trong ứng dụng.",
                                  "Account history, training data and AI operations in the app.")))
        let sectionTitle = makeLabel(L10n.choose("KHU VỰC QUẢN TRỊ", "ADMINISTRATION"), size: 11,
                                     color: AppTheme.primaryColor, weight: .bold)
        contentStack.addArrangedSubview(sectionTitle)
        for section in AdminSection.allCases {
            let button = UIButton(type: .system)
            button.backgroundColor = AppTheme.cardBackgroundColor
            button.layer.cornerRadius = 15
            button.layer.borderWidth = 1
            button.layer.borderColor = AppTheme.borderColor.cgColor
            button.accessibilityIdentifier = "admin.section.\(section.rawValue)"
            button.accessibilityLabel = "\(section.title), \(section.subtitle)"
            let icon = UIImageView(image: UIImage(systemName: section.symbol))
            icon.tintColor = AppTheme.primaryColor
            icon.contentMode = .scaleAspectFit
            icon.translatesAutoresizingMaskIntoConstraints = false
            let title = makeLabel(section.title, size: 16, color: AppTheme.titleColor, weight: .semibold)
            let subtitle = makeLabel(section.subtitle, size: 11, color: AppTheme.secondaryTextColor)
            let copy = UIStackView(arrangedSubviews: [title, subtitle])
            copy.axis = .vertical
            copy.spacing = 3
            let arrow = UIImageView(image: UIImage(systemName: "chevron.right"))
            arrow.tintColor = AppTheme.secondaryTextColor
            arrow.contentMode = .scaleAspectFit
            arrow.translatesAutoresizingMaskIntoConstraints = false
            let row = UIStackView(arrangedSubviews: [icon, copy, arrow])
            row.alignment = .center
            row.spacing = 13
            row.isUserInteractionEnabled = false
            row.translatesAutoresizingMaskIntoConstraints = false
            button.addSubview(row)
            NSLayoutConstraint.activate([
                icon.widthAnchor.constraint(equalToConstant: 24), icon.heightAnchor.constraint(equalToConstant: 24),
                arrow.widthAnchor.constraint(equalToConstant: 12), arrow.heightAnchor.constraint(equalToConstant: 16),
                row.topAnchor.constraint(equalTo: button.topAnchor, constant: 15),
                row.leadingAnchor.constraint(equalTo: button.leadingAnchor, constant: 16),
                row.trailingAnchor.constraint(equalTo: button.trailingAnchor, constant: -16),
                row.bottomAnchor.constraint(equalTo: button.bottomAnchor, constant: -15)
            ])
            button.addAction(UIAction { [weak self] _ in
                self?.navigationController?.pushViewController(AdminSectionViewController(section: section), animated: true)
            }, for: .touchUpInside)
            contentStack.addArrangedSubview(button)
        }
        let signOutButton = actionButton(L10n.choose("Đăng xuất quản trị", "Sign out administrator"), filled: false)
        signOutButton.addTarget(self, action: #selector(signOut), for: .touchUpInside)
        contentStack.addArrangedSubview(signOutButton)
    }

    private func makeHero(eyebrow: String, title: String, subtitle: String) -> UIView {
        let card = GradientCardView(colors: [AppTheme.brandDark, AppTheme.brandDeep])
        let shield = UIImageView(image: UIImage(systemName: "checkmark.shield"))
        shield.tintColor = AppTheme.mintColor
        shield.contentMode = .scaleAspectFit
        shield.translatesAutoresizingMaskIntoConstraints = false
        let brand = makeLabel("Scam Detector  ·  NỀN TẢNG AI AN TOÀN", size: 11, color: AppTheme.mintColor, weight: .bold)
        let eyebrowLabel = makeLabel(eyebrow, size: 10, color: AppTheme.mintColor, weight: .bold)
        let titleLabel = makeLabel(title, size: 25, color: .white, weight: .bold)
        let detail = makeLabel(subtitle, size: 13, color: UIColor.white.withAlphaComponent(0.82))
        let stack = UIStackView(arrangedSubviews: [shield, brand, eyebrowLabel, titleLabel, detail])
        stack.axis = .vertical
        stack.alignment = .leading
        stack.spacing = 10
        pin(stack, in: card, padding: 22)
        NSLayoutConstraint.activate([shield.widthAnchor.constraint(equalToConstant: 36), shield.heightAnchor.constraint(equalToConstant: 36)])
        return card
    }

    private func configureField(_ field: UITextField, placeholder: String, secure: Bool) {
        field.placeholder = placeholder
        field.isSecureTextEntry = secure
        field.backgroundColor = AppTheme.fieldBackgroundColor
        field.textColor = AppTheme.titleColor
        field.layer.cornerRadius = 11
        field.layer.borderWidth = 1
        field.layer.borderColor = AppTheme.borderColor.cgColor
        field.leftView = UIView(frame: CGRect(x: 0, y: 0, width: 14, height: 1))
        field.leftViewMode = .always
        if !field.constraints.contains(where: { $0.firstAttribute == .height }) {
            field.heightAnchor.constraint(equalToConstant: 50).isActive = true
        }
    }

    private func makeLabel(_ text: String, size: CGFloat, color: UIColor, weight: UIFont.Weight = .regular) -> UILabel {
        let label = UILabel()
        label.text = text
        label.font = AppTheme.font(size: size, weight: weight)
        label.adjustsFontForContentSizeCategory = true
        label.textColor = color
        label.numberOfLines = 0
        return label
    }

    private func actionButton(_ title: String, filled: Bool) -> UIButton {
        let button = UIButton(type: .system)
        button.setTitle(title, for: .normal)
        button.titleLabel?.font = AppTheme.font(size: 14, weight: .bold)
        button.tintColor = filled ? .white : AppTheme.primaryColor
        button.setTitleColor(filled ? .white : AppTheme.primaryColor, for: .normal)
        button.backgroundColor = filled ? AppTheme.primaryColor : AppTheme.cardBackgroundColor
        button.layer.cornerRadius = 12
        button.layer.borderWidth = filled ? 0 : 1
        button.layer.borderColor = AppTheme.borderColor.cgColor
        button.heightAnchor.constraint(greaterThanOrEqualToConstant: 48).isActive = true
        return button
    }

    private func pin(_ content: UIView, in card: UIView, padding: CGFloat) {
        content.translatesAutoresizingMaskIntoConstraints = false
        card.addSubview(content)
        NSLayoutConstraint.activate([
            content.topAnchor.constraint(equalTo: card.topAnchor, constant: padding),
            content.leadingAnchor.constraint(equalTo: card.leadingAnchor, constant: padding),
            content.trailingAnchor.constraint(equalTo: card.trailingAnchor, constant: -padding),
            content.bottomAnchor.constraint(equalTo: card.bottomAnchor, constant: -padding)
        ])
    }

    @objc private func signIn() {
        let account = accountField.text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let password = passwordField.text ?? ""
        guard !account.isEmpty, !password.isEmpty else {
            errorLabel.text = L10n.choose("Nhập tài khoản và mật khẩu.", "Enter your account and password.")
            errorLabel.isHidden = false
            return
        }
        submitButton?.isEnabled = false
        errorLabel.isHidden = true
        Task { [weak self] in
            guard let self else { return }
            do {
                try await session.signIn(account: account, password: password, adminOnly: true)
                passwordField.text = nil
                renderDashboard()
            } catch {
                errorLabel.text = error.localizedDescription
                errorLabel.isHidden = false
            }
            submitButton?.isEnabled = true
        }
    }

    @objc private func signOut() {
        session.signOut()
        passwordField.text = nil
        renderLogin()
    }
}
