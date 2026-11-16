import Foundation

@main
struct HistoryCheck {
    @MainActor static func main() async throws {
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent("scamshield-history-\(UUID())")
        defer { try? FileManager.default.removeItem(at: directory) }
        let json = #"{"scan_id":null,"image_url":null,"extracted_text":"Kiểm tra","risk_score":72,"risk_level":"nguy_hiem","text_risk_score":20,"visual_risk_score":8,"image_model_available":false,"image_model_score":0,"highlighted_terms":["OTP"],"visual_flags":[],"explanation":"Nội dung cần xác minh","suggested_action":"Không mở liên kết","phishvn_url_risk_score":72,"phishvn_urls":[{"url":"example.test","risk_score":72}],"analysis_breakdown":{"components":[{"key":"url","title":"URL","score":72}]}}"#
        let result = try JSONDecoder().decode(ScanResult.self, from: Data(json.utf8))
        let store = HistoryService(directory: directory)
        let empty = try await store.fetchHistory()
        precondition(empty.isEmpty)
        try store.save(result: result, imageData: Data([1,2,3]))
        try store.save(result: result, imageData: Data([4,5,6]))
        let restored = try await HistoryService(directory: directory).fetchHistory()
        precondition(restored.count == 2 && restored[0].id != restored[1].id)
        precondition(restored[0].highlightedRegions?.analysisBreakdown?.components?.first?.score == 72)
        precondition(restored[0].highlightedRegions?.textRiskScore == 20)
        try await store.deleteHistoryItem(id: restored[0].id)
        let remaining = try await store.fetchHistory()
        precondition(remaining.count == 1)
        let files = try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
        precondition(files.filter { $0.pathExtension == "jpg" }.count == 1)
        let cleared = try await store.clearHistory()
        precondition(cleared == 1)
        let finalFiles = try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
        precondition(finalFiles.count == 1 && finalFiles[0].lastPathComponent == "history.json")
        print("PASS: guest decode, persist/reopen, unique IDs, metrics round-trip, delete photo, clear history")
    }
}
