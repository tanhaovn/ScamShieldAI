import UIKit
import CoreText

enum ScanReport {
    @MainActor static func export(_ result: ScanResult) throws -> URL {
        let report = NSMutableAttributedString()
        func append(_ text: String, heading: Bool = false) {
            guard !text.isEmpty else { return }
            let paragraph = NSMutableParagraphStyle()
            paragraph.paragraphSpacing = heading ? 8 : 14
            paragraph.lineSpacing = 4
            report.append(NSAttributedString(string: text + "\n", attributes: [
                .font: heading ? UIFont.boldSystemFont(ofSize: 16) : UIFont.systemFont(ofSize: 11),
                .foregroundColor: heading ? UIColor(red: 0.08, green: 0.3, blue: 0.23, alpha: 1) : UIColor.black,
                .paragraphStyle: paragraph
            ]))
        }
        func section(_ heading: String, _ text: String?) {
            guard let text, !text.isEmpty else { return }
            append(heading, heading: true)
            append(text)
        }
        append("SCAMSHIELD AI", heading: true)
        append(L10n.text("Báo cáo kiểm tra lừa đảo"), heading: true)
        append(L10n.choose("Nguồn: \(result.originalFilename ?? result.sourceType ?? "—")\nThời gian kiểm tra: \(result.createdAt?.backendDateDisplayText ?? "—")\nThời gian xuất: \(Date().formatted())", "Source: \(result.originalFilename ?? result.sourceType ?? "—")\nChecked: \(result.createdAt?.backendDateDisplayText ?? "—")\nExported: \(Date().formatted())"))
        section(L10n.choose("Kết luận · \(result.riskScore)/100", "Assessment · \(result.riskScore)/100"), result.riskLevel.displayName + "\n" + result.explanation)
        section(L10n.text("Hành động an toàn đề xuất"), result.suggestedAction)
        section(L10n.text("Bằng chứng đáng chú ý"), (result.highlightedTerms + result.visualFlags).joined(separator: "\n"))
        section(L10n.text("Nguồn đối chiếu độc lập"), "Google Safe Browsing: " + (result.safeBrowsing?.summary ?? L10n.text("Chưa có dữ liệu đối chiếu.")) + "\nPhishVN: " + (result.phishVNModel ?? L10n.text("Chưa có dữ liệu mô hình.")))
        for component in result.analysisBreakdown?.components ?? [] {
            section("\(component.title) · \(component.score)/100", ([component.summary ?? ""] + (component.findings ?? [])).joined(separator: "\n"))
        }
        section(L10n.text("Đường link phát hiện"), result.phishVNURLs?.map { "\($0.url) · \($0.riskScore)/100" }.joined(separator: "\n"))
        section(L10n.text("Nội dung QR"), result.qrCodes?.joined(separator: "\n"))
        section(L10n.text("Nội dung hệ thống đã đọc"), result.extractedText.isEmpty ? L10n.text("Không ghi nhận được văn bản.") : result.extractedText)
        section(L10n.text("Cách tính điểm"), result.analysisBreakdown?.score_method)
        section(L10n.text("Giới hạn kỹ thuật"), result.analysisBreakdown?.limitations?.joined(separator: "\n"))
        append(L10n.text("Báo cáo hỗ trợ quyết định an toàn, không phải kết luận pháp lý."))

        let framesetter = CTFramesetterCreateWithAttributedString(report)
        let page = CGRect(x: 0, y: 0, width: 595, height: 842)
        let url = FileManager.default.temporaryDirectory.appendingPathComponent("ScamShield-report-\(UUID()).pdf")
        let renderer = UIGraphicsPDFRenderer(bounds: page)
        try renderer.writePDF(to: url) { context in
            var location = 0
            var pageNumber = 0
            while location < report.length {
                context.beginPage()
                pageNumber += 1
                let cg = context.cgContext
                cg.saveGState()
                cg.translateBy(x: 0, y: page.height)
                cg.scaleBy(x: 1, y: -1)
                let path = CGPath(rect: CGRect(x: 42, y: 52, width: 511, height: 748), transform: nil)
                let frame = CTFramesetterCreateFrame(framesetter, CFRange(location: location, length: 0), path, nil)
                CTFrameDraw(frame, cg)
                let visible = CTFrameGetVisibleStringRange(frame)
                cg.restoreGState()
                ("ScamShield AI · \(pageNumber)" as NSString).draw(at: CGPoint(x: 42, y: 810), withAttributes: [.font: UIFont.systemFont(ofSize: 9), .foregroundColor: UIColor.gray])
                guard visible.length > 0 else { break }
                location += visible.length
            }
        }
        return url
    }
}
