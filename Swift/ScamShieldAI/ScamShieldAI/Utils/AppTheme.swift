import UIKit

enum AppTheme {

    // MARK: - Colors

    // Shared palette from the web safety console, with native light/dark variants.
    static let primaryColor = adaptive(0x397C62, 0x68C39F)
    static let accentColor = primaryColor
    static let linkColor = adaptive(0x3D6E9C, 0x8EBEE9)
    static let violetColor = adaptive(0x7862A5, 0xBEABEB)

    static func displayFont(size: CGFloat, weight: UIFont.Weight) -> UIFont {
        let base = UIFont.systemFont(ofSize: size, weight: weight)
        return UIFontMetrics(forTextStyle: .headline).scaledFont(for: base)
    }

    static func font(size: CGFloat, weight: UIFont.Weight = .regular, style: UIFont.TextStyle = .body) -> UIFont {
        UIFontMetrics(forTextStyle: style).scaledFont(for: .systemFont(ofSize: size, weight: weight))
    }

    static let brandDark = color(0x164D3B)
    static let brandDeep = color(0x103C2F)
    static let mintColor = color(0xB9EFD5)
    static let softColor = adaptive(0xEAF4F0, 0x173328)
    static let titleColor = adaptive(0x142B22, 0xE6F5EF)
    static let secondaryTextColor = adaptive(0x53665D, 0xAEC3B9)
    static let pageBackgroundColor = adaptive(0xF3F6F5, 0x0B1713)
    static let fieldBackgroundColor = adaptive(0xF7FAF9, 0x11271E)
    static let cardBackgroundColor = adaptive(0xFFFFFF, 0x0E2119)
    static let borderColor = adaptive(0xDBE7E2, 0x254137)
    static let safeColor = primaryColor
    static let suspiciousColor = adaptive(0x946716, 0xE5B760)
    static let dangerousColor = adaptive(0xB94343, 0xF28B8B)

    private static func adaptive(_ light: UInt32, _ dark: UInt32) -> UIColor {
        let lightColor = color(light), darkColor = color(dark)
        return UIColor { $0.userInterfaceStyle == .dark ? darkColor : lightColor }
    }

    private static func color(_ hex: UInt32) -> UIColor {
        UIColor(
            red: CGFloat((hex >> 16) & 0xFF) / 255,
            green: CGFloat((hex >> 8) & 0xFF) / 255,
            blue: CGFloat(hex & 0xFF) / 255,
            alpha: 1
        )
    }

    // MARK: - Risk Presentation

    static func color(for riskLevel: RiskLevel) -> UIColor {
        switch riskLevel {
        case .safe:
            return safeColor
        case .suspicious:
            return suspiciousColor
        case .dangerous:
            return dangerousColor
        }
    }
}
