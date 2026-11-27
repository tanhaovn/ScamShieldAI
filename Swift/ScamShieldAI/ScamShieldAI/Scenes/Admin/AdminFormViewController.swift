import UIKit

final class AdminFormViewController: UIViewController {
    var onSaved: (() -> Void)?
    private let section: AdminSection
    private let session = AccountSession.shared
    private var inputs: [String: UITextField] = [:]
    private var switches: [String: UISwitch] = [:]
    private let errorLabel = UILabel()
    private let saveButton = UIButton(type: .system)

    init(section: AdminSection) {
        self.section = section
        super.init(nibName: nil, bundle: nil)
    }
    required init?(coder: NSCoder) { fatalError("AdminFormViewController chỉ được khởi tạo bằng code.") }

    override func viewDidLoad() {
        super.viewDidLoad()
        navigationItem.title = L10n.choose("Thêm \(section.title)", "Add \(section.title)")
        navigationItem.largeTitleDisplayMode = .never
        view.backgroundColor = AppTheme.pageBackgroundColor

        let scroll = UIScrollView()
        scroll.keyboardDismissMode = .interactive
        scroll.translatesAutoresizingMaskIntoConstraints = false
        let stack = UIStackView()
        stack.axis = .vertical
        stack.spacing = 14
        stack.translatesAutoresizingMaskIntoConstraints = false

        let heading = UILabel()
        heading.text = section.title
        heading.font = AppTheme.displayFont(size: 25, weight: .bold)
        heading.textColor = AppTheme.titleColor
        heading.numberOfLines = 0
        stack.addArrangedSubview(heading)

        for field in section.formFields {
            let card = CardView()
            let label = UILabel()
            label.text = field.title + (field.required ? " *" : "")
            label.font = AppTheme.font(size: 13, weight: .semibold)
            label.textColor = AppTheme.titleColor
            label.numberOfLines = 0
            let row = UIStackView()
            row.axis = .vertical
            row.spacing = 8
            row.translatesAutoresizingMaskIntoConstraints = false
            row.addArrangedSubview(label)
            switch field.kind {
            case .toggle:
                let toggle = UISwitch()
                toggle.onTintColor = AppTheme.primaryColor
                toggle.accessibilityLabel = field.title
                switches[field.key] = toggle
                row.addArrangedSubview(toggle)
            case .text, .integer, .decimal:
                let input = UITextField()
                input.placeholder = field.title
                input.text = field.defaultValue
                input.font = AppTheme.font(size: 15)
                input.textColor = AppTheme.titleColor
                input.backgroundColor = AppTheme.fieldBackgroundColor
                input.layer.cornerRadius = 10
                input.layer.borderWidth = 1
                input.layer.borderColor = AppTheme.borderColor.cgColor
                input.leftView = UIView(frame: CGRect(x: 0, y: 0, width: 12, height: 1))
                input.leftViewMode = .always
                input.keyboardType = field.kind == .integer ? .numberPad : field.kind == .decimal ? .decimalPad : .default
                input.autocapitalizationType = .none
                input.heightAnchor.constraint(equalToConstant: 46).isActive = true
                input.accessibilityIdentifier = "admin.form.\(field.key)"
                inputs[field.key] = input
                row.addArrangedSubview(input)
            }
            card.addSubview(row)
            NSLayoutConstraint.activate([
                row.topAnchor.constraint(equalTo: card.topAnchor, constant: 14),
                row.leadingAnchor.constraint(equalTo: card.leadingAnchor, constant: 16),
                row.trailingAnchor.constraint(equalTo: card.trailingAnchor, constant: -16),
                row.bottomAnchor.constraint(equalTo: card.bottomAnchor, constant: -14)
            ])
            stack.addArrangedSubview(card)
        }

        errorLabel.font = AppTheme.font(size: 13)
        errorLabel.textColor = AppTheme.dangerousColor
        errorLabel.numberOfLines = 0
        errorLabel.isHidden = true
        stack.addArrangedSubview(errorLabel)
        saveButton.setTitle(L10n.choose("Lưu vào hệ thống", "Save to system"), for: .normal)
        saveButton.setTitleColor(.white, for: .normal)
        saveButton.titleLabel?.font = AppTheme.font(size: 15, weight: .bold)
        saveButton.backgroundColor = AppTheme.primaryColor
        saveButton.layer.cornerRadius = 12
        saveButton.heightAnchor.constraint(equalToConstant: 52).isActive = true
        saveButton.addTarget(self, action: #selector(save), for: .touchUpInside)
        stack.addArrangedSubview(saveButton)

        view.addSubview(scroll)
        scroll.addSubview(stack)
        NSLayoutConstraint.activate([
            scroll.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scroll.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scroll.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scroll.bottomAnchor.constraint(equalTo: view.keyboardLayoutGuide.topAnchor),
            stack.topAnchor.constraint(equalTo: scroll.contentLayoutGuide.topAnchor, constant: 18),
            stack.leadingAnchor.constraint(equalTo: scroll.contentLayoutGuide.leadingAnchor, constant: 16),
            stack.trailingAnchor.constraint(equalTo: scroll.contentLayoutGuide.trailingAnchor, constant: -16),
            stack.widthAnchor.constraint(equalTo: scroll.frameLayoutGuide.widthAnchor, constant: -32),
            stack.bottomAnchor.constraint(equalTo: scroll.contentLayoutGuide.bottomAnchor, constant: -30)
        ])
    }

    @objc private func save() {
        var payload: [String: Any] = [:]
        for field in section.formFields {
            if field.kind == .toggle {
                payload[field.key] = switches[field.key]?.isOn == true
                continue
            }
            let value = inputs[field.key]?.text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
            if value.isEmpty {
                if field.required {
                    showError(L10n.choose("Vui lòng nhập \(field.title).", "Enter \(field.title)."))
                    return
                }
                continue
            }
            switch field.kind {
            case .integer:
                guard let number = Int(value) else { showError(L10n.choose("\(field.title) phải là số nguyên.", "\(field.title) must be an integer.")); return }
                if field.key == "weight" && !(1...50).contains(number) {
                    showError(L10n.choose("Trọng số phải từ 1 đến 50.", "Weight must be between 1 and 50.")); return
                }
                payload[field.key] = number
            case .decimal:
                guard let number = Double(value.replacingOccurrences(of: ",", with: ".")), (0...1).contains(number) else {
                    showError(L10n.choose("\(field.title) phải từ 0 đến 1.", "\(field.title) must be between 0 and 1.")); return
                }
                payload[field.key] = number
            case .text: payload[field.key] = value
            case .toggle: break
            }
        }
        errorLabel.isHidden = true
        saveButton.isEnabled = false
        Task { [weak self] in
            guard let self else { return }
            do {
                _ = try await session.post(path: section.path, payload: payload)
                onSaved?()
                navigationController?.popViewController(animated: true)
            } catch {
                showError(error.localizedDescription)
            }
            saveButton.isEnabled = true
        }
    }

    private func showError(_ message: String) {
        errorLabel.text = message
        errorLabel.isHidden = false
    }
}
