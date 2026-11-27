import Foundation

/// Local scan history. Signed-in history is fetched separately and merged for display.
final class HistoryService {

    // MARK: - Local Storage

    private static var directory: URL {
        FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("ScamShieldHistory", isDirectory: true)
    }

    static func localImageURL(filename: String) -> URL {
        directory.appendingPathComponent(filename)
    }

    private let storageDirectory: URL

    init(directory: URL? = nil) {
        storageDirectory = directory ?? Self.directory
    }

    private var recordsURL: URL { storageDirectory.appendingPathComponent("history.json") }
    // MARK: - History

    func fetchHistory() async throws -> [ScanHistoryItem] {
        try readRecords()
    }

    func fetchAccountHistory() async throws -> [ScanHistoryItem] {
        let rows = try await AccountSession.shared.rows(path: "/scan-history")
        return rows.compactMap { row in
            if let data = try? JSONSerialization.data(withJSONObject: row),
               let item = try? JSONDecoder().decode(ScanHistoryItem.self, from: data) { return item }
            guard let id = (row["id"] as? NSNumber)?.intValue else { return nil }
            let score = (row["risk_score"] as? NSNumber)?.intValue ?? 0
            let level = RiskLevel(rawValue: row["risk_level"] as? String ?? "") ?? .suspicious
            return ScanHistoryItem(
                id: id, imageURL: row["image_url"] as? String,
                originalFilename: row["original_filename"] as? String,
                riskScore: score, riskLevel: level,
                scamCategoryID: (row["scam_category_id"] as? NSNumber)?.intValue,
                extractedText: row["extracted_text"] as? String,
                explanation: row["explanation"] as? String,
                suggestedAction: row["suggested_action"] as? String,
                highlightedRegions: nil, createdAt: row["created_at"] as? String,
                sourceType: row["source_type"] as? String)
        }
    }

    static func merge(local: [ScanHistoryItem], account: [ScanHistoryItem]) -> [ScanHistoryItem] {
        let remoteIDs = Set(account.map(\.id))
        let deviceOnly = local.filter { item in
            guard let scanID = item.result?.scanID else { return true }
            return !remoteIDs.contains(scanID)
        }
        return (account + deviceOnly).sorted { ($0.createdAt ?? "") > ($1.createdAt ?? "") }
    }

    func save(result: ScanResult, imageData: Data? = nil) throws {
        var records = try readRecords()
        try FileManager.default.createDirectory(at: storageDirectory, withIntermediateDirectories: true)
        let filename = "\(UUID().uuidString).jpg"
        let imageURL = storageDirectory.appendingPathComponent(filename)
        try imageData?.write(to: imageURL, options: [.atomic, .completeFileProtectionUnlessOpen])
        let record = ScanHistoryItem(
            id: max(Int(Date().timeIntervalSince1970 * 1_000_000), (records.first?.id ?? 0) + 1),
            imageURL: imageData == nil ? nil : "local-history/\(filename)",
            originalFilename: result.originalFilename ?? L10n.text("Ảnh kiểm tra"),
            riskScore: result.riskScore,
            riskLevel: result.riskLevel,
            scamCategoryID: result.scamCategoryID,
            extractedText: result.extractedText,
            explanation: result.explanation,
            suggestedAction: result.suggestedAction,
            highlightedRegions: HighlightedRegions(
                terms: result.highlightedTerms,
                visualFlags: result.visualFlags,
                textRiskScore: result.textRiskScore,
                visualRiskScore: result.visualRiskScore,
                imageModelAvailable: result.imageModelAvailable,
                imageModelScore: result.imageModelScore,
                phishVNURLs: result.phishVNURLs,
                analysisBreakdown: result.analysisBreakdown
            ),
            createdAt: ISO8601DateFormatter().string(from: Date()),
            sourceType: result.sourceType,
            result: result
        )
        records.insert(record, at: 0)
        do {
            try writeRecords(records)
        } catch {
            try? FileManager.default.removeItem(at: imageURL)
            throw error
        }
    }

    func deleteHistoryItem(id: Int) async throws {
        let records = try readRecords()
        let removed = records.first { $0.id == id }
        try writeRecords(records.filter { $0.id != id })
        removeImage(for: removed)
    }

    func clearHistory() async throws -> Int {
        let records = try readRecords()
        try writeRecords([])
        records.forEach { removeImage(for: $0) }
        return records.count
    }

    // MARK: - Persistence Helpers

    private func readRecords() throws -> [ScanHistoryItem] {
        guard FileManager.default.fileExists(atPath: recordsURL.path) else { return [] }
        return try JSONDecoder().decode([ScanHistoryItem].self, from: Data(contentsOf: recordsURL))
    }

    private func writeRecords(_ records: [ScanHistoryItem]) throws {
        try FileManager.default.createDirectory(at: storageDirectory, withIntermediateDirectories: true)
        let data = try JSONEncoder().encode(records)
        try data.write(to: recordsURL, options: [.atomic, .completeFileProtectionUnlessOpen])
    }

    private func removeImage(for item: ScanHistoryItem?) {
        guard let path = item?.imageURL, path.hasPrefix("local-history/") else { return }
        try? FileManager.default.removeItem(at: storageDirectory.appendingPathComponent(String(path.dropFirst(14))))
    }
}
