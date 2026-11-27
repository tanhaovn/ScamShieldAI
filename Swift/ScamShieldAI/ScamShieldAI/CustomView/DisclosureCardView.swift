import UIKit

final class DisclosureCardView: CardView {
    private let toggle = UIButton(type: .system)
    private let body: UIView
    private var isExpanded: Bool

    init(title: String, symbol: String, body: UIView, expanded: Bool = false) {
        self.body = body
        self.isExpanded = expanded
        super.init(frame: .zero)
        var config = UIButton.Configuration.plain()
        config.title = title
        config.image = UIImage(systemName: symbol)
        config.imagePadding = 10
        config.baseForegroundColor = AppTheme.titleColor
        config.contentInsets = .init(top: 14, leading: 14, bottom: 14, trailing: 8)
        toggle.configuration = config
        toggle.contentHorizontalAlignment = .leading
        toggle.titleLabel?.numberOfLines = 0
        toggle.addTarget(self, action: #selector(toggleExpansion), for: .touchUpInside)
        let chevron = UIButton(type: .system)
        chevron.tintColor = AppTheme.secondaryTextColor
        chevron.widthAnchor.constraint(equalToConstant: 44).isActive = true
        chevron.isAccessibilityElement = false
        chevron.addTarget(self, action: #selector(toggleExpansion), for: .touchUpInside)
        let header = UIStackView(arrangedSubviews: [toggle, chevron])
        let stack = UIStackView(arrangedSubviews: [header, body])
        stack.axis = .vertical
        stack.spacing = 4
        stack.isLayoutMarginsRelativeArrangement = true
        stack.directionalLayoutMargins = .init(top: 4, leading: 5, bottom: 5, trailing: 5)
        stack.translatesAutoresizingMaskIntoConstraints = false
        addSubview(stack)
        NSLayoutConstraint.activate([
            stack.topAnchor.constraint(equalTo: topAnchor),
            stack.leadingAnchor.constraint(equalTo: leadingAnchor),
            stack.trailingAnchor.constraint(equalTo: trailingAnchor),
            stack.bottomAnchor.constraint(equalTo: bottomAnchor),
            toggle.heightAnchor.constraint(greaterThanOrEqualToConstant: 44)
        ])
        chevronView = chevron
        updateVisibility()
    }

    private weak var chevronView: UIButton?

    required init?(coder: NSCoder) {
        fatalError("Use init(title:symbol:body:expanded:)")
    }

    @objc private func toggleExpansion() {
        isExpanded.toggle()
        updateVisibility()
    }

    private func updateVisibility() {
        body.isHidden = !isExpanded
        let image = UIImage(systemName: isExpanded ? "chevron.up" : "chevron.down",
                            withConfiguration: UIImage.SymbolConfiguration(pointSize: 12, weight: .semibold))
        chevronView?.setImage(image, for: .normal)
        toggle.accessibilityValue = isExpanded ? L10n.choose("Đang mở", "Expanded") : L10n.choose("Đang đóng", "Collapsed")
    }
}
