import Foundation

final class ScanService {
    private let apiClient: APIClient

    init(apiClient: APIClient = APIClient()) {
        self.apiClient = apiClient
    }

    func fetchCategories() async throws -> [ScamCategory] {
        try await apiClient.request(endpoint: .scamCategories)
    }

    func analyze(imageData: Data, categoryID: Int?) async throws -> ScanResult {
        try await apiClient.upload(
            endpoint: .checkImage(categoryID: categoryID),
            imageData: imageData,
            filename: "scam-check-\(UUID().uuidString).jpg",
            mimeType: "image/jpeg"
        )
    }

    func analyze(text: String, kind: ScanInputKind) async throws -> ScanResult {
        let value = text.trimmingCharacters(in: .whitespacesAndNewlines)
        return try await apiClient.request(
            endpoint: kind == .url ? .checkURL : .checkText,
            body: [kind == .url ? "url" : "text": value]
        )
    }

    func analyze(document: Data, filename: String) async throws -> ScanResult {
        try await apiClient.upload(endpoint: .checkDocument, imageData: document,
                                   filename: filename, mimeType: "application/pdf")
    }

    func ask(question: String, result: ScanResult) async throws -> String {
        let body = AssistantRequest(question: question, risk_level: result.riskLevel.rawValue,
            risk_score: result.riskScore, highlighted_terms: Array(result.highlightedTerms.prefix(30)),
            urls: Array((result.phishVNURLs ?? []).prefix(20)),
            suggested_action: String(result.suggestedAction.prefix(3000)),
            verdict: String(result.explanation.prefix(3000)))
        let response: AssistantResponse = try await apiClient.request(endpoint: .assistant, body: body)
        return response.answer
    }
}

private struct AssistantRequest: Encodable {
    let question: String
    let risk_level: String
    let risk_score: Int
    let highlighted_terms: [String]
    let urls: [PhishVNURLPrediction]
    let suggested_action: String
    let verdict: String
}
private struct AssistantResponse: Decodable { let answer: String }

/// The four input types supported by the same backend as the web app.
enum ScanInputKind: String, CaseIterable, Codable {
    case image, text, url, pdf
    var title: String {
        switch self {
        case .image: return "Ảnh"
        case .text: return "Tin nhắn"
        case .url: return "Liên kết"
        case .pdf: return "PDF"
        }
    }
    var symbol: String {
        switch self {
        case .image: return "photo.on.rectangle"
        case .text: return "text.bubble"
        case .url: return "link"
        case .pdf: return "doc.richtext"
        }
    }
}
