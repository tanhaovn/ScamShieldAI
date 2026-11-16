import UIKit

/// Compact category shortcuts; descriptions remain available to VoiceOver.
final class SourceTile: UIControl {
    private let surface = CardView()

    init(kind: ScanInputKind, action: @escaping () -> Void) {
        super.init(frame: .zero)
        let tint: UIColor
        let detail: String
        switch kind {
        case .image: tint = AppTheme.primaryColor; detail = "Ảnh chụp & mã QR"
        case .text: tint = AppTheme.linkColor; detail = "Tin nhắn đáng ngờ"
        case .url: tint = AppTheme.violetColor; detail = "Website & tên miền"
        case .pdf: tint = AppTheme.suspiciousColor; detail = "Nội dung tài liệu"
        }
        surface.isUserInteractionEnabled = false
        surface.translatesAutoresizingMaskIntoConstraints = false
        addSubview(surface)
        let icon = UIImageView(image: UIImage(systemName: kind.symbol))
        icon.contentMode = .center
        icon.preferredSymbolConfiguration = .init(pointSize: 23, weight: .regular)
        icon.tintColor = tint
        icon.backgroundColor = tint.withAlphaComponent(0.1)
        icon.layer.cornerRadius = 22
        let title = UILabel()
        title.text = kind.title
        title.numberOfLines = 0
        title.textAlignment = .center
        title.font = AppTheme.font(size: 13, weight: .semibold, style: .subheadline)
        title.adjustsFontForContentSizeCategory = true
        title.textColor = AppTheme.titleColor
        let stack = UIStackView(arrangedSubviews: [icon, title])
        stack.axis = .vertical
        stack.alignment = .center
        stack.spacing = 10
        stack.translatesAutoresizingMaskIntoConstraints = false
        surface.addSubview(stack)
        NSLayoutConstraint.activate([
            surface.topAnchor.constraint(equalTo: topAnchor), surface.bottomAnchor.constraint(equalTo: bottomAnchor),
            surface.leadingAnchor.constraint(equalTo: leadingAnchor), surface.trailingAnchor.constraint(equalTo: trailingAnchor),
            stack.topAnchor.constraint(equalTo: surface.topAnchor, constant: 14),
            stack.bottomAnchor.constraint(equalTo: surface.bottomAnchor, constant: -14),
            stack.leadingAnchor.constraint(equalTo: surface.leadingAnchor, constant: 4),
            stack.trailingAnchor.constraint(equalTo: surface.trailingAnchor, constant: -4),
            title.widthAnchor.constraint(equalTo: stack.widthAnchor),
            icon.widthAnchor.constraint(equalToConstant: 44), icon.heightAnchor.constraint(equalToConstant: 44),
            heightAnchor.constraint(greaterThanOrEqualToConstant: 100)
        ])
        isAccessibilityElement = true
        accessibilityLabel = "Kiểm tra \(kind.title.lowercased())"
        accessibilityHint = detail
        accessibilityIdentifier = "overview.source.\(kind.rawValue)"
        accessibilityTraits = .button
        addAction(UIAction { _ in action() }, for: .touchUpInside)
    }

    required init?(coder: NSCoder) { fatalError("Use init(kind:action:)") }

    override var isHighlighted: Bool {
        didSet {
            guard !UIAccessibility.isReduceMotionEnabled else { return }
            UIView.animate(withDuration: 0.16, delay: 0, options: [.beginFromCurrentState, .allowUserInteraction]) {
                self.surface.transform = self.isHighlighted ? CGAffineTransform(scaleX: 0.97, y: 0.97) : .identity
            }
        }
    }
}
