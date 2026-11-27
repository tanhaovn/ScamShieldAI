import Foundation

enum BatchInput {
    static func urls(from input: String) -> [String] {
        input.components(separatedBy: CharacterSet(charactersIn: "\r\n,;"))
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
    }
}

struct BatchResponse: Decodable { let results: [BatchURLResult] }
struct BatchURLResult: Codable {
    let url: String
    let status: String
    let risk_score: Int
    // Invalid URLs use "unknown" and must never appear as a safe result.
    let risk_level: String
    var domain_intelligence: [DomainIntelligence]?
    var google_safe_browsing: SafeBrowsingEvidence?
}

struct ScanFeedbackRequest: Encodable {
    let scan_id: Int?
    let client_scan_id: String
    let verdict: String
    let predicted_level: String
    let risk_score: Int
    let source_type: String
    let original_filename: String?
    let note: String?
    let highlighted_terms: [String]
    let urls: [String]

    init(result: ScanResult, verdict: String, note: String) {
        scan_id = result.scanID
        client_scan_id = result.scanID.map(String.init) ?? result.createdAt ?? ""
        self.verdict = verdict
        predicted_level = result.riskLevel.rawValue
        risk_score = result.riskScore
        source_type = result.sourceType ?? "unknown"
        original_filename = result.originalFilename
        let trimmed = note.trimmingCharacters(in: .whitespacesAndNewlines)
        self.note = trimmed.isEmpty ? nil : String(trimmed.prefix(1000))
        highlighted_terms = Array(result.highlightedTerms.prefix(30))
        urls = Array((result.phishVNURLs ?? []).prefix(20)).map(\.url)
    }
}
struct FeedbackResponse: Decodable { let id: Int; let status: String }

struct DomainIntelligence: Codable {
    var host: String?
    var level: String?
    var score: Int?
    var signals: [String]?
}
struct SafeBrowsingEvidence: Codable {
    var configured: Bool?
    var available: Bool?
    var matches: [ThreatMatch]?
    var note: String?
    struct ThreatMatch: Codable { var url: String?; var threat_types: [String]?; var threat_labels: [String]? }
    var summary: String {
        if !(matches ?? []).isEmpty { return L10n.text("Có khớp danh sách mối đe dọa đã biết.") }
        if configured == true && available == true { return L10n.text("Chưa có kết quả khớp đã biết. Không có khớp không có nghĩa URL chắc chắn an toàn.") }
        return L10n.text("Chưa cấu hình hoặc chưa sẵn sàng; chưa thể đối chiếu nguồn này.")
    }
}
struct ImageGradCAM: Codable {
    var available: Bool?
    var image_url: String?
    var target_class: String?
    var target_score: Double?
    var note: String?
}
struct VisionAnalysis: Codable {
    var available: Bool?
    var risk_score: Int?
    var provider: String?
    var model: String?
    var summary: String?
    var risk_indicators: [String]?
    var reasoning: String?
    var explanation_source: String?
    var explanation_items: [ExplanationItem]?
    var note: String?
    struct ExplanationItem: Codable {
        var observation: String?
        var location: String?
        var why_risky: String?
        var explanation: String?
    }
}
struct ImageDimensions: Codable { let width: Double; let height: Double }
struct ImageAnnotation: Codable {
    var left: Double?
    var top: Double?
    var width: Double?
    var height: Double?
    var label: String?
    var reason: String?
    var severity: String?
}
