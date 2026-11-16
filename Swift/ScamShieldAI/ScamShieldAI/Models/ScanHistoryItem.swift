import Foundation

struct ScanHistoryItem: Codable {
    let id: Int
    let imageURL: String?
    let originalFilename: String?
    let riskScore: Int
    let riskLevel: RiskLevel
    let scamCategoryID: Int?
    let extractedText: String?
    let explanation: String?
    let suggestedAction: String?
    let highlightedRegions: HighlightedRegions?
    let createdAt: String?

    var sourceType: String? = nil
    var result: ScanResult? = nil

    // MARK: - Coding Keys

    enum CodingKeys: String, CodingKey {
        case id
        case sourceType = "source_type"
        case result
        case imageURL = "image_url"
        case originalFilename = "original_filename"
        case riskScore = "risk_score"
        case riskLevel = "risk_level"
        case scamCategoryID = "scam_category_id"
        case extractedText = "extracted_text"
        case explanation
        case suggestedAction = "suggested_action"
        case highlightedRegions = "highlighted_regions"
        case createdAt = "created_at"
    }
}

struct HighlightedRegions: Codable {
    let terms: [String]?
    let visualFlags: [String]?
    let textRiskScore: Int?
    let visualRiskScore: Int?
    let imageModelAvailable: Bool?
    let imageModelScore: Int?
    let phishVNURLs: [PhishVNURLPrediction]?
    let analysisBreakdown: AnalysisBreakdown?

    // MARK: - Coding Keys

    enum CodingKeys: String, CodingKey {
        case terms
        case visualFlags = "visual_flags"
        case textRiskScore = "text_risk_score"
        case visualRiskScore = "visual_risk_score"
        case imageModelAvailable = "image_model_available"
        case imageModelScore = "image_model_score"
        case phishVNURLs = "phishvn_urls"
        case analysisBreakdown = "analysis_breakdown"
    }
}
