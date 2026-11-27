import Foundation

final class ScanService {
    private let apiClient: APIClient

    init(apiClient: APIClient = APIClient()) {
        self.apiClient = apiClient
    }

    func backendIsReady() async throws -> Bool {
        let response: BackendHealth = try await apiClient.request(endpoint: .health)
        return response.status == "ok"
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

    func analyzeBatch(input: String) async throws -> BatchResponse {
        try await apiClient.request(endpoint: .batch, body: ["urls": Array(BatchInput.urls(from: input).prefix(50))])
    }

    func sendFeedback(_ feedback: ScanFeedbackRequest) async throws {
        let _: FeedbackResponse = try await apiClient.request(endpoint: .feedback, body: feedback)
    }

}

/// The input types supported by the same backend as the web app.
enum ScanInputKind: String, CaseIterable, Codable {
    case image, text, url, pdf, batch
    var title: String {
        switch self {
        case .image: return L10n.text("Ảnh")
        case .text: return L10n.text("Tin nhắn")
        case .url: return L10n.text("Liên kết")
        case .pdf: return "PDF"
        case .batch: return L10n.text("Nhiều URL")
        }
    }
    var symbol: String {
        switch self {
        case .image: return "photo.on.rectangle"
        case .text: return "text.bubble"
        case .url: return "link"
        case .pdf: return "doc.richtext"
        case .batch: return "link.badge.plus"
        }
    }
}

private struct BackendHealth: Decodable { let status: String }
