import Foundation

enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
}

enum APIEndpoint {
    case checkText, checkURL, checkDocument, assistant
    case scamCategories
    case checkImage(categoryID: Int?)
    case legacyHistory(userID: Int)

    // MARK: - Request Configuration

    var path: String {
        switch self {
        case .checkText: return "/check-text"
        case .checkURL: return "/check-url"
        case .checkDocument: return "/check-document"
        case .assistant: return "/analysis-assistant"
        case .scamCategories:
            return "/scam-categories"
        case .checkImage(let categoryID):
            var path = "/check-image/guest"
            if let categoryID { path += "?scam_category_id=\(categoryID)" }
            return path
        case .legacyHistory(let userID):
            return "/history/\(userID)"
        }
    }

    var method: HTTPMethod {
        switch self {
        case .scamCategories, .legacyHistory: return .get
        case .checkImage, .checkText, .checkURL, .checkDocument, .assistant: return .post
        }
    }

    var timeoutInterval: TimeInterval {
        switch self {
        case .checkImage, .checkDocument: return 120
        default: return 30
        }
    }
}
