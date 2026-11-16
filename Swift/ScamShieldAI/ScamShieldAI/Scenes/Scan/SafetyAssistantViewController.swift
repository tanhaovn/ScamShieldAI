import UIKit

/// Follow-up answers use the completed result, just like the web assistant.
final class SafetyAssistantViewController: UIViewController, UITextFieldDelegate {
    private let result: ScanResult
    private let messages = UIStackView()
    private let scroll = UIScrollView()
    private let input = UITextField()
    private let send = UIButton(type: .system)
    private let activity = UIActivityIndicatorView(style: .medium)
    private var requestTask: Task<Void, Never>?
    private var isAsking = false
    private var suggestions: [UIButton] = []

    init(result: ScanResult) { self.result = result; super.init(nibName: nil, bundle: nil) }
    required init?(coder: NSCoder) { fatalError("Use init(result:)") }
    deinit { requestTask?.cancel() }

    override func viewDidLoad() {
        super.viewDidLoad()
        navigationItem.title = "Trợ lý an toàn"
        navigationItem.largeTitleDisplayMode = .never
        installAppBackground()
        scroll.alwaysBounceVertical = true
        scroll.showsVerticalScrollIndicator = false
        scroll.keyboardDismissMode = .interactive
        scroll.translatesAutoresizingMaskIntoConstraints = false
        messages.axis = .vertical
        messages.spacing = 14
        messages.translatesAutoresizingMaskIntoConstraints = false
        scroll.addSubview(messages)
        view.addSubview(scroll)

        let intro = InformationCardView(title: "Hiểu kết quả. Biết bước tiếp theo.", systemImageName: "sparkles")
        intro.configure(text: "Trợ lý trả lời dựa trên lần kiểm tra này: \(result.riskLevel.displayName.lowercased()), \(result.riskScore)/100 điểm. Bạn có thể chọn câu hỏi hoặc nhập nội dung bên dưới.")
        messages.addArrangedSubview(intro)
        ["Vì sao bị cảnh báo?", "Tôi đã bấm link thì làm gì?", "Tôi nên làm gì tiếp theo?", "Kết quả này có chắc chắn không?"].forEach { question in
            var config = UIButton.Configuration.tinted()
            config.title = question
            config.image = UIImage(systemName: "arrow.up.right")
            config.imagePlacement = .trailing
            config.imagePadding = 10
            config.baseForegroundColor = AppTheme.primaryColor
            config.baseBackgroundColor = AppTheme.primaryColor
            config.contentInsets = .init(top: 14, leading: 16, bottom: 14, trailing: 16)
            let button = UIButton(configuration: config, primaryAction: UIAction { [weak self] _ in self?.ask(question) })
            button.contentHorizontalAlignment = .leading
            button.titleLabel?.numberOfLines = 0
            button.enableSoftPressAnimation()
            messages.addArrangedSubview(button)
            suggestions.append(button)
        }
        let actions = suggestions.compactMap { button -> UIAction? in
            guard let question = button.configuration?.title else { return nil }
            return UIAction(title: question, image: UIImage(systemName: "text.bubble")) { [weak self] _ in self?.ask(question) }
        }
        navigationItem.rightBarButtonItem = UIBarButtonItem(title: "Gợi ý", image: UIImage(systemName: "sparkles"), menu: UIMenu(title: "Hỏi về kết quả", children: actions))
        activity.hidesWhenStopped = true
        messages.addArrangedSubview(activity)
        input.placeholder = "Hỏi về kết quả này…"
        input.font = .preferredFont(forTextStyle: .body)
        input.textColor = AppTheme.titleColor
        input.returnKeyType = .send
        input.delegate = self
        input.accessibilityIdentifier = "assistant.question"
        var config = UIButton.Configuration.filled()
        config.image = UIImage(systemName: "arrow.up")
        config.baseBackgroundColor = AppTheme.brandDark
        config.cornerStyle = .capsule
        send.configuration = config
        send.accessibilityLabel = "Gửi câu hỏi"
        send.addAction(UIAction { [weak self] _ in self?.submit() }, for: .touchUpInside)
        send.widthAnchor.constraint(equalToConstant: 44).isActive = true
        send.heightAnchor.constraint(equalToConstant: 44).isActive = true
        let composer = UIStackView(arrangedSubviews: [input, send])
        composer.spacing = 12
        composer.isLayoutMarginsRelativeArrangement = true
        composer.layoutMargins = .init(top: 12, left: 20, bottom: 12, right: 20)
        composer.backgroundColor = AppTheme.cardBackgroundColor
        composer.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(composer)
        NSLayoutConstraint.activate([
            scroll.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scroll.leadingAnchor.constraint(equalTo: view.leadingAnchor), scroll.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scroll.bottomAnchor.constraint(equalTo: composer.topAnchor),
            messages.topAnchor.constraint(equalTo: scroll.contentLayoutGuide.topAnchor, constant: 16),
            messages.leadingAnchor.constraint(equalTo: scroll.frameLayoutGuide.leadingAnchor, constant: 20),
            messages.trailingAnchor.constraint(equalTo: scroll.frameLayoutGuide.trailingAnchor, constant: -20),
            messages.bottomAnchor.constraint(equalTo: scroll.contentLayoutGuide.bottomAnchor, constant: -20),
            composer.leadingAnchor.constraint(equalTo: view.leadingAnchor), composer.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            composer.bottomAnchor.constraint(equalTo: view.keyboardLayoutGuide.topAnchor)
        ])
    }

    func textFieldShouldReturn(_ textField: UITextField) -> Bool { submit(); return false }
    private func submit() { ask(input.text ?? "") }

    private func ask(_ raw: String) {
        guard !isAsking else { return }
        let question = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard (2...500).contains(question.count) else {
            showErrorAlert(message: "Nhập câu hỏi từ 2 đến 500 ký tự."); return
        }
        input.text = ""
        suggestions.forEach { $0.isHidden = true }
        view.endEditing(true)
        append(title: "Bạn", text: question, icon: "person.crop.circle")
        isAsking = true
        send.isEnabled = false
        activity.startAnimating()
        input.placeholder = "Trợ lý đang trả lời…"
        requestTask = Task { [weak self] in
            guard let self else { return }
            defer {
                isAsking = false
                send.isEnabled = true
                activity.stopAnimating()
                input.placeholder = "Hỏi tiếp về kết quả này…"
            }
            do {
                let answer = try await ScanService().ask(question: question, result: result)
                guard !Task.isCancelled else { return }
                append(title: "Trợ lý an toàn", text: answer, icon: "sparkles")
            } catch {
                guard !Task.isCancelled else { return }
                append(title: "Chưa thể trả lời", text: "\(error.localizedDescription)\nBạn có thể gửi lại câu hỏi.", icon: "wifi.exclamationmark")
                input.text = question
            }
        }
    }

    private func append(title: String, text: String, icon: String) {
        let card = InformationCardView(title: title, systemImageName: icon)
        card.configure(text: text)
        messages.insertArrangedSubview(card, at: max(0, messages.arrangedSubviews.count - 1))
        view.layoutIfNeeded()
        let top = card.convert(card.bounds, to: scroll).minY - 16
        let maximum = max(-scroll.adjustedContentInset.top, scroll.contentSize.height - scroll.bounds.height + scroll.adjustedContentInset.bottom)
        scroll.setContentOffset(CGPoint(x: 0, y: min(maximum, max(-scroll.adjustedContentInset.top, top))), animated: !UIAccessibility.isReduceMotionEnabled)
        UIAccessibility.post(notification: .announcement, argument: "\(title): \(text)")
    }
}
