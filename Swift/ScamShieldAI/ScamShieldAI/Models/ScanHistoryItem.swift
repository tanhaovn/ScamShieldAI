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

    var listTitle: String {
        guard let originalFilename, !originalFilename.isEmpty else {
            return L10n.choose("Lượt kiểm tra", "Check")
        }
        let prefix = "scam-check-"
        let suffix = ".jpg"
        if originalFilename.hasPrefix(prefix), originalFilename.hasSuffix(suffix),
           UUID(uuidString: String(originalFilename.dropFirst(prefix.count).dropLast(suffix.count))) != nil {
            return L10n.text("Ảnh đã kiểm tra")
        }
        return originalFilename
    }

    var reportResult: ScanResult {
        result ?? ScanResult(createdAt: createdAt, sourceType: sourceType ?? "image", originalFilename: originalFilename,
            qrCodes: nil, documentInfo: nil, scanID: nil, imageURL: imageURL,
            extractedText: extractedText ?? "", riskScore: riskScore, riskLevel: riskLevel,
            textRiskScore: highlightedRegions?.textRiskScore ?? 0,
            visualRiskScore: highlightedRegions?.visualRiskScore ?? 0,
            imageModelAvailable: highlightedRegions?.imageModelAvailable ?? false, imageModelLabel: nil,
            imageModelScore: highlightedRegions?.imageModelScore ?? 0, scamType: nil,
            highlightedTerms: highlightedRegions?.terms ?? [], visualFlags: highlightedRegions?.visualFlags ?? [],
            explanation: explanation ?? "", suggestedAction: suggestedAction ?? "", scamCategoryID: scamCategoryID,
            phishVNURLRiskScore: nil, phishVNURLs: highlightedRegions?.phishVNURLs, analysisBreakdown: highlightedRegions?.analysisBreakdown,
            visionAnalysis: highlightedRegions?.visionAnalysis)
    }

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
    var visionAnalysis: VisionAnalysis? = nil

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
        case visionAnalysis = "vlm_analysis"
    }
}
