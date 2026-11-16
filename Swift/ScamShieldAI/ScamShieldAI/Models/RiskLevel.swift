import Foundation

enum RiskLevel: String, Codable {
    case safe = "an_toan"
    case suspicious = "nghi_ngo"
    case dangerous = "nguy_hiem"

    // MARK: - Presentation Text

    var displayName: String {
        switch self {
        case .safe:
            return "Rủi ro thấp"
        case .suspicious:
            return "Nghi ngờ"
        case .dangerous:
            return "Nguy hiểm"
        }
    }

    var systemImageName: String {
        switch self {
        case .safe:
            return "checkmark.shield.fill"
        case .suspicious:
            return "exclamationmark.shield.fill"
        case .dangerous:
            return "xmark.shield.fill"
        }
    }
}
