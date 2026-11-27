import Foundation

enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
}

enum APIEndpoint {
    case checkText, checkURL, checkDocument, batch, feedback, health
    case scamCategories
    case checkImage(categoryID: Int?)

    // MARK: - Request Configuration

    var path: String {
        switch self {
        case .batch: return "/check-urls-batch"
        case .feedback: return "/scan-feedback"
        case .health: return "/health"
        case .checkText: return "/check-text"
        case .checkURL: return "/check-url"
        case .checkDocument: return "/check-document"
        case .scamCategories:
            return "/scam-categories"
        case .checkImage(let categoryID):
            var path = "/check-image"
            if let categoryID { path += "?scam_category_id=\(categoryID)" }
            return path
        }
    }

    var method: HTTPMethod {
        switch self {
        case .scamCategories, .health: return .get
        case .checkImage, .checkText, .checkURL, .checkDocument, .batch, .feedback: return .post
        }
    }

    var timeoutInterval: TimeInterval {
        switch self {
        case .health: return 15
        case .batch: return 180
        case .checkImage, .checkDocument, .checkText, .checkURL: return 90
        default: return 30
        }
    }
}
