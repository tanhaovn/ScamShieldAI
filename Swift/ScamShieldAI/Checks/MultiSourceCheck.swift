import Foundation

final class MockScanProtocol: URLProtocol {
    static var requests: [URLRequest] = []
    static var bodies: [Data] = []
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        Self.requests.append(request)
        var body = request.httpBody ?? Data()
        if let stream = request.httpBodyStream {
            stream.open()
            defer { stream.close() }
            let buffer = UnsafeMutablePointer<UInt8>.allocate(capacity: 4096)
            defer { buffer.deallocate() }
            while stream.hasBytesAvailable {
                let count = stream.read(buffer, maxLength: 4096)
                if count <= 0 { break }
                body.append(buffer, count: count)
            }
        }
        Self.bodies.append(body)
        let path = request.url!.path
        let kind = path == "/check-text" ? "text" : path == "/check-url" ? "url" : path == "/check-document" ? "pdf" : "image"
        var json = """
        {"scan_id":null,"image_url":null,"source_type":"\(kind)","original_filename":"Kiểm tra \(kind)","extracted_text":"Nội dung kiểm tra","risk_score":42,"risk_level":"nghi_ngo","text_risk_score":42,"visual_risk_score":0,"image_model_available":false,"image_model_score":0,"highlighted_terms":["OTP"],"visual_flags":[],"explanation":"Cần xác minh","suggested_action":"Không chia sẻ OTP","qr_codes":[],"phishvn_urls":[{"url":"https://example.com","risk_score":20}],"analysis_breakdown":{"components":[]}}
        """
        if path == "/check-urls-batch" { json = #"{"results":[{"url":"https://example.com","status":"checked","risk_score":10,"risk_level":"an_toan"},{"url":"invalid","status":"invalid","risk_score":0,"risk_level":"unknown"}]}"# }
        if path == "/scan-feedback" { json = #"{"id":7,"status":"pending"}"# }
        client?.urlProtocol(self, didReceive: HTTPURLResponse(url: request.url!, statusCode: 200, httpVersion: nil, headerFields: ["Content-Type":"application/json"])!, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: Data(json.utf8))
        client?.urlProtocolDidFinishLoading(self)
    }
    override func stopLoading() {}
}

@main struct MultiSourceCheck {
    static func main() async throws {
        let configuration = URLSessionConfiguration.ephemeral
        configuration.protocolClasses = [MockScanProtocol.self]
        let session = URLSession(configuration: configuration)
        let service = ScanService(apiClient: APIClient(session: session))
        let text = try await service.analyze(text: "  Nội dung tin nhắn  ", kind: .text)
        precondition(text.sourceType == "text")
        let body = try JSONSerialization.jsonObject(with: MockScanProtocol.bodies.last!) as! [String: String]
        precondition(body["text"] == "Nội dung tin nhắn")
        let url = try await service.analyze(text: "https://example.com", kind: .url)
        precondition(url.sourceType == "url")
        let pdf = try await service.analyze(document: Data("%PDF-test".utf8), filename: "sample.pdf")
        precondition(pdf.sourceType == "pdf")
        let multipart = String(decoding: MockScanProtocol.bodies.last!, as: UTF8.self)
        precondition(multipart.contains("application/pdf") && multipart.contains("sample.pdf") && multipart.contains("name=\"file\""))
        let image = try await service.analyze(imageData: Data([1,2,3]), categoryID: 4)
        precondition(MockScanProtocol.requests.last!.url!.path == "/check-image/guest")
        precondition(MockScanProtocol.requests.last!.url!.query == "scam_category_id=4")
        let batch = try await service.analyzeBatch(input: "https://example.com; invalid\n")
        precondition(batch.results.count == 2 && batch.results[1].risk_level == "unknown")
        let batchBody = try JSONSerialization.jsonObject(with: MockScanProtocol.bodies.last!) as! [String: [String]]
        precondition(batchBody["urls"] == ["https://example.com", "invalid"])
        precondition(MockScanProtocol.requests.last!.timeoutInterval == 180)
        try await service.sendFeedback(ScanFeedbackRequest(result: text, verdict: "false_alarm", note: "  Review  "))
        let feedback = try JSONSerialization.jsonObject(with: MockScanProtocol.bodies.last!) as! [String: Any]
        precondition(feedback["verdict"] as? String == "false_alarm" && feedback["note"] as? String == "Review")
        precondition(feedback["urls"] as? [String] == ["https://example.com"])
        precondition(MockScanProtocol.requests.map { $0.url!.path } ==
            ["/check-text", "/check-url", "/check-document", "/check-image/guest", "/check-urls-batch", "/scan-feedback"])
        precondition(BatchInput.urls(from: " a,b; c\r\n\n") == ["a", "b", "c"])
        let malicious = BatchURLResult(url: "=SUM(1,2)", status: "invalid", risk_score: 0, risk_level: "unknown")
        let csv = String(decoding: BatchCSV.data([malicious]), as: UTF8.self)
        precondition(csv.contains("\"'=SUM(1,2)\""))
        var payload = try JSONSerialization.jsonObject(with: JSONEncoder().encode(image)) as! [String: Any]
        payload["image_model_gradcam"] = ["available":true,"image_url":"/uploads/map.jpg","target_score":87,"target_class":"phishing"]
        payload["image_dimensions"] = ["width":400,"height":720]
        payload["image_annotations"] = [["left":10,"top":20,"width":100,"height":30,"label":"OTP","reason":"Sensitive request"]]
        payload["google_safe_browsing"] = ["configured":true,"available":true,"matches":[["url":"https://example.com","threat_types":["SOCIAL_ENGINEERING"]]]]
        payload["domain_intelligence"] = [["host":"example.com","score":30,"level":"review","signals":["test"]]]
        payload["vlm_analysis"] = ["provider":"gemini","model":"gemini-test","summary":"Test summary","risk_indicators":["Sensitive request"],"explanation_source":"vision_language_model","reasoning":"Test explanation","explanation_items":[["observation":"Login","location":"center","why_risky":"test"]]]
        let enriched = try JSONDecoder().decode(ScanResult.self, from: JSONSerialization.data(withJSONObject: payload))
        let roundTrip = try JSONDecoder().decode(ScanResult.self, from: JSONEncoder().encode(enriched))
        precondition(roundTrip.imageGradCAM?.target_score == 87 && roundTrip.imageAnnotations?.first?.left == 10)
        precondition(roundTrip.safeBrowsing?.matches?.first?.threat_types == ["SOCIAL_ENGINEERING"])
        precondition(roundTrip.visionAnalysis?.reasoning == "Test explanation" && roundTrip.domainIntelligence?.first?.score == 30)
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent("ScamShieldMultiSource-\(UUID())")
        defer { try? FileManager.default.removeItem(at: directory) }
        let store = HistoryService(directory: directory)
        try store.save(result: text)
        try store.save(result: url)
        try store.save(result: pdf)
        try store.save(result: enriched, imageData: Data([1,2,3]))
        let reopened = try await HistoryService(directory: directory).fetchHistory()
        precondition(reopened.count == 4)
        precondition(reopened.filter { $0.imageURL == nil }.count == 3)
        precondition(reopened.first { $0.sourceType == "text" }?.result?.riskScore == 42)
        let savedVision = reopened.first { $0.sourceType == "image" }?.reportResult.visionAnalysis
        precondition(savedVision?.provider == "gemini" && savedVision?.summary == "Test summary")
        precondition(savedVision?.risk_indicators == ["Sensitive request"] && savedVision?.explanation_items?.first?.why_risky == "test")
        let files = try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
        precondition(files.filter { $0.pathExtension == "jpg" }.count == 1)
        // History from the previous app version must remain readable.
        let legacy = #"{"id":1,"risk_score":12,"risk_level":"an_toan","original_filename":"Old image"}"#
        let oldItem = try JSONDecoder().decode(ScanHistoryItem.self, from: Data(legacy.utf8))
        precondition(oldItem.result == nil && oldItem.sourceType == nil)
        _ = try await store.clearHistory()
        let finalFiles = try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
        precondition(finalFiles.count == 1)
        print("PASS: five input modes, multipart PDF/image, batch invalid URL, feedback payload, CSV escaping, rich evidence round-trip and history")
    }
}
