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
        let json = path == "/analysis-assistant" ? #"{"answer":"Hãy xác minh qua kênh chính thức."}"# : """
        {"scan_id":null,"image_url":null,"source_type":"\(kind)","original_filename":"Kiểm tra \(kind)","extracted_text":"Nội dung kiểm tra","risk_score":42,"risk_level":"nghi_ngo","text_risk_score":42,"visual_risk_score":0,"image_model_available":false,"image_model_score":0,"highlighted_terms":["OTP"],"visual_flags":[],"explanation":"Cần xác minh","suggested_action":"Không chia sẻ OTP","qr_codes":[],"phishvn_urls":[{"url":"https://example.com","risk_score":20}],"analysis_breakdown":{"components":[]}}
        """
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
        let answer = try await service.ask(question: "Vì sao bị cảnh báo?", result: text)
        precondition(!answer.isEmpty)
        let assistant = try JSONSerialization.jsonObject(with: MockScanProtocol.bodies.last!) as! [String: Any]
        precondition(assistant["risk_score"] as? Int == 42 && assistant["risk_level"] as? String == "nghi_ngo")
        precondition(MockScanProtocol.requests.map { $0.url!.path } == ["/check-text", "/check-url", "/check-document", "/check-image/guest", "/analysis-assistant"])
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent("ScamShieldMultiSource-\(UUID())")
        defer { try? FileManager.default.removeItem(at: directory) }
        let store = HistoryService(directory: directory)
        try store.save(result: text)
        try store.save(result: url)
        try store.save(result: pdf)
        try store.save(result: image, imageData: Data([1,2,3]))
        let reopened = try await HistoryService(directory: directory).fetchHistory()
        precondition(reopened.count == 4)
        precondition(reopened.filter { $0.imageURL == nil }.count == 3)
        precondition(reopened.first { $0.sourceType == "text" }?.result?.riskScore == 42)
        let files = try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
        precondition(files.filter { $0.pathExtension == "jpg" }.count == 1)
        // History from the previous app version must remain readable.
        let legacy = #"{"id":1,"risk_score":12,"risk_level":"an_toan","original_filename":"Old image"}"#
        let oldItem = try JSONDecoder().decode(ScanHistoryItem.self, from: Data(legacy.utf8))
        precondition(oldItem.result == nil && oldItem.sourceType == nil)
        _ = try await store.clearHistory()
        let finalFiles = try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
        precondition(finalFiles.count == 1)
        print("PASS: four scan requests, multipart PDF, grounded assistant, multisource persistence, legacy history and cleanup")
    }
}
