import Foundation

struct ScanResult: Codable {
    let createdAt: String?
    let sourceType: String?
    let originalFilename: String?
    let qrCodes: [String]?
    let documentInfo: DocumentInfo?
    let scanID: Int?
    let imageURL: String?
    let extractedText: String
    let riskScore: Int
    let riskLevel: RiskLevel
    let textRiskScore: Int
    let visualRiskScore: Int
    let imageModelAvailable: Bool
    let imageModelLabel: String?
    let imageModelScore: Int
    let scamType: String?
    let highlightedTerms: [String]
    let visualFlags: [String]
    let explanation: String
    let suggestedAction: String
    let scamCategoryID: Int?
    let phishVNURLRiskScore: Int?
    let phishVNURLs: [PhishVNURLPrediction]?
    let analysisBreakdown: AnalysisBreakdown?

    var imageGradCAM: ImageGradCAM? = nil
    var visionAnalysis: VisionAnalysis? = nil
    var imageDimensions: ImageDimensions? = nil
    var imageAnnotations: [ImageAnnotation]? = nil
    var domainIntelligence: [DomainIntelligence]? = nil
    var safeBrowsing: SafeBrowsingEvidence? = nil
    var phishVNAvailable: Bool? = nil
    var phishVNModel: String? = nil

    // MARK: - Coding Keys

    enum CodingKeys: String, CodingKey {
        case imageGradCAM = "image_model_gradcam"
        case visionAnalysis = "vlm_analysis"
        case imageDimensions = "image_dimensions"
        case imageAnnotations = "image_annotations"
        case domainIntelligence = "domain_intelligence"
        case safeBrowsing = "google_safe_browsing"
        case phishVNAvailable = "phishvn_available"
        case phishVNModel = "phishvn_model"
        case createdAt = "created_at"
        case sourceType = "source_type"
        case originalFilename = "original_filename"
        case qrCodes = "qr_codes"
        case documentInfo = "document_info"
        case scanID = "scan_id"
        case imageURL = "image_url"
        case extractedText = "extracted_text"
        case riskScore = "risk_score"
        case riskLevel = "risk_level"
        case textRiskScore = "text_risk_score"
        case visualRiskScore = "visual_risk_score"
        case imageModelAvailable = "image_model_available"
        case imageModelLabel = "image_model_label"
        case imageModelScore = "image_model_score"
        case scamType = "scam_type"
        case highlightedTerms = "highlighted_terms"
        case visualFlags = "visual_flags"
        case explanation
        case suggestedAction = "suggested_action"
        case scamCategoryID = "scam_category_id"
        case phishVNURLRiskScore = "phishvn_url_risk_score"
        case phishVNURLs = "phishvn_urls"
        case analysisBreakdown = "analysis_breakdown"
    }
}

// MARK: - Structured Analysis

// Các trường mới là optional ở model cha để vẫn đọc được lịch sử từ API cũ.
struct AnalysisBreakdown: Codable {
    let components: [AnalysisComponent]?
    var verdict: AnalysisVerdict? = nil
    var score_method: String? = nil
    var limitations: [String]? = nil
}

struct AnalysisVerdict: Codable {
    var headline: String?
    var reason: String?
}

struct AnalysisComponent: Codable {
    let key: String
    let title: String
    let score: Int
    let summary: String?
    var status_label: String? = nil
    var findings: [String]? = nil
}

struct PhishVNURLPrediction: Codable {
    let url: String
    let domain: String?
    let riskScore: Int
    var label: String? = nil
    var probability: Double? = nil
    var suspiciousSignals: [String]? = nil

    enum CodingKeys: String, CodingKey {
        case url, domain, label, probability
        case suspiciousSignals = "suspicious_signals"
        case riskScore = "risk_score"
    }
}

struct DocumentInfo: Codable {
    let pageCount: Int
    let processedPages: Int
    let truncated: Bool
    enum CodingKeys: String, CodingKey {
        case pageCount = "page_count", processedPages = "processed_pages", truncated
    }
}
