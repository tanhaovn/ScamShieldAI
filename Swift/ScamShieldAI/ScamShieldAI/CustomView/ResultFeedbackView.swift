import UIKit

final class ResultFeedbackView: CardView, UITextViewDelegate {
    private let result: ScanResult
    private let editor = UITextView()
    private let submit = PrimaryButton(type: .system)
    private let status = UILabel()
    private let form = UIStackView()
    private let choiceStack = UIStackView()
    private var verdict: String?
    private var task: Task<Void, Never>?
    var onEditorFocus: ((UIView) -> Void)?

    init(result: ScanResult) {
        self.result = result
        super.init(frame: .zero)
        setup()
    }

    required init?(coder: NSCoder) { fatalError("Use init(result:)") }

    isolated deinit { task?.cancel() }

    private func setup() {
        let heading = UILabel()
        heading.text = L10n.text("Kết quả này có chính xác không?")
        heading.font = .preferredFont(forTextStyle: .headline)
        heading.adjustsFontForContentSizeCategory = true
        heading.textColor = AppTheme.titleColor
        heading.numberOfLines = 0
        heading.accessibilityTraits = .header

        choiceStack.axis = .vertical
        choiceStack.spacing = 8
        let options: [(String, String, String, String, UIColor)] = [
            ("correct", L10n.text("Kết quả đúng"), L10n.choose("Cảnh báo phù hợp với nội dung", "The warning matches this content"), "checkmark.circle", AppTheme.safeColor),
            ("false_alarm", L10n.text("Cảnh báo sai"), L10n.choose("Nội dung an toàn nhưng bị cảnh báo", "Safe content was flagged"), "exclamationmark.circle", AppTheme.suspiciousColor),
            ("missed_scam", L10n.text("Bỏ sót lừa đảo"), L10n.choose("Kết quả chưa cảnh báo đúng mức", "The result should be more severe"), "plus.circle", AppTheme.dangerousColor)
        ]
        for (value, title, detail, symbol, tint) in options {
            var config = UIButton.Configuration.plain()
            config.title = title
            config.subtitle = detail
            config.image = UIImage(systemName: symbol)?.withTintColor(tint, renderingMode: .alwaysOriginal)
            config.imagePadding = 12
            config.baseForegroundColor = AppTheme.titleColor
            config.background.backgroundColor = AppTheme.fieldBackgroundColor
            config.background.cornerRadius = 12
            config.contentInsets = .init(top: 10, leading: 12, bottom: 10, trailing: 12)
            let button = UIButton(configuration: config)
            button.accessibilityIdentifier = "result.feedback.\(value)"
            button.contentHorizontalAlignment = .leading
            button.titleLabel?.numberOfLines = 0
            button.addAction(UIAction { [weak self, weak button] _ in
                guard let self else { return }
                verdict = value
                for case let choice as UIButton in choiceStack.arrangedSubviews {
                    let selected = choice === button
                    choice.isSelected = selected
                    choice.configuration?.background.strokeColor = selected ? tint : .clear
                    choice.configuration?.background.strokeWidth = selected ? 1.5 : 0
                }
                form.isHidden = false
                status.isHidden = true
            }, for: .touchUpInside)
            choiceStack.addArrangedSubview(button)
        }

        let hint = UILabel()
        hint.text = L10n.text("Ghi chú không bắt buộc · Tối đa 1.000 ký tự")
        hint.font = .preferredFont(forTextStyle: .footnote)
        hint.adjustsFontForContentSizeCategory = true
        hint.numberOfLines = 0
        hint.textColor = AppTheme.secondaryTextColor
        editor.font = .preferredFont(forTextStyle: .body)
        editor.adjustsFontForContentSizeCategory = true
        editor.backgroundColor = AppTheme.fieldBackgroundColor
        editor.textColor = AppTheme.titleColor
        editor.layer.cornerRadius = 12
        editor.textContainerInset = .init(top: 10, left: 10, bottom: 10, right: 10)
        editor.heightAnchor.constraint(equalToConstant: 100).isActive = true
        editor.accessibilityLabel = L10n.text("Ghi chú phản hồi")
        editor.delegate = self
        submit.setPrimaryTitle(L10n.text("Gửi phản hồi"))
        submit.addTarget(self, action: #selector(send), for: .touchUpInside)
        form.axis = .vertical
        form.spacing = 10
        [hint, editor, submit].forEach(form.addArrangedSubview)
        form.isHidden = true

        status.numberOfLines = 0
        status.font = .preferredFont(forTextStyle: .subheadline)
        status.adjustsFontForContentSizeCategory = true
        status.isHidden = true

        let stack = UIStackView(arrangedSubviews: [heading, choiceStack, form, status])
        stack.axis = .vertical
        stack.spacing = 12
        stack.translatesAutoresizingMaskIntoConstraints = false
        addSubview(stack)
        NSLayoutConstraint.activate([
            stack.topAnchor.constraint(equalTo: topAnchor, constant: 16),
            stack.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
            stack.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),
            stack.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -16)
        ])
    }

    func textViewDidBeginEditing(_ textView: UITextView) { onEditorFocus?(textView) }

    func textView(_ textView: UITextView, shouldChangeTextIn range: NSRange, replacementText text: String) -> Bool {
        guard let range = Range(range, in: textView.text) else { return false }
        return textView.text.replacingCharacters(in: range, with: text).count <= 1000
    }

    @objc private func send() {
        guard task == nil, let verdict else { return }
        endEditing(true)
        let payload = ScanFeedbackRequest(result: result, verdict: verdict, note: editor.text)
        let service = ScanService()
        submit.isLoading = true
        choiceStack.isUserInteractionEnabled = false
        editor.isEditable = false
        status.isHidden = true
        task = Task { [weak self] in
            let success: Bool
            do {
                try await service.sendFeedback(payload)
                success = true
            } catch {
                success = false
            }
            guard !Task.isCancelled, let self else { return }
            task = nil
            submit.isLoading = false
            choiceStack.isUserInteractionEnabled = true
            editor.isEditable = true
            status.isHidden = false
            if success {
                choiceStack.isHidden = true
                form.isHidden = true
                status.textColor = AppTheme.primaryColor
                status.text = L10n.text("Cảm ơn bạn. Phản hồi đã được đưa vào hàng chờ kiểm định.")
            } else {
                status.textColor = AppTheme.dangerousColor
                status.text = L10n.text("Chưa gửi được phản hồi. Bạn có thể thử lại.")
            }
            UIAccessibility.post(notification: .announcement, argument: status.text)
        }
    }
}
