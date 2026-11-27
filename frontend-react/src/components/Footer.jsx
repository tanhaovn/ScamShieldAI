export default function Footer({ language = "vi" }) {
  const en = language === "en";
  return (
    <footer className="app-footer">
      <div className="footer-main">
        <div className="footer-brand-column">
          <div className="footer-brand"><span><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3 6 7v7c0 7.2 4.1 12.1 10 15 5.9-2.9 10-7.8 10-15V7Z" /><path d="m11.5 16 3 3 6.5-8" /></svg></span><div><strong>Scam Detector</strong><small>{en ? "Digital safety platform" : "Nền tảng an toàn số"}</small></div></div>
          <p>{en ? "AI-assisted scam detection for images, messages, links and documents." : "Hệ thống AI hỗ trợ phát hiện lừa đảo trong hình ảnh, tin nhắn, đường link và tài liệu."}</p>
          <span className="footer-official"><i />{en ? "Detection service is operating" : "Dịch vụ phát hiện đang hoạt động"}</span>
        </div>
        <div className="footer-link-column"><strong>{en ? "Detection" : "Kiểm tra"}</strong><span>{en ? "Images & QR codes" : "Hình ảnh & mã QR"}</span><span>{en ? "Messages & email" : "Tin nhắn & email"}</span><span>{en ? "Links & domains" : "Đường link & tên miền"}</span><span>{en ? "PDF documents" : "Tài liệu PDF"}</span></div>
        <div className="footer-link-column"><strong>{en ? "Protection" : "Bảo vệ"}</strong><span>OCR</span><span>Google Safe Browsing</span><span>PhishVN</span><span>{en ? "Visual AI analysis" : "Phân tích hình ảnh AI"}</span></div>
        <div className="footer-contact-column"><strong>{en ? "Principle" : "Nguyên tắc"}</strong><p>{en ? "Check before you trust. Results are decision support and should be reviewed with context." : "Kiểm tra trước khi bạn tin. Kết quả là thông tin hỗ trợ quyết định và cần được xem xét theo ngữ cảnh."}</p></div>
      </div>
      <div className="footer-legal"><span>© 2026 Scam Detector</span><span>{en ? "Built for safer digital decisions." : "Được xây dựng vì những quyết định số an toàn hơn."}</span></div>
    </footer>
  );
}
