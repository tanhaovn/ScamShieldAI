const iconPaths = {
  scan: ["M4 8V5a1 1 0 0 1 1-1h3", "M16 4h3a1 1 0 0 1 1 1v3", "M20 16v3a1 1 0 0 1-1 1h-3", "M8 20H5a1 1 0 0 1-1-1v-3", "M8 12h8"],
  shield: ["M12 3 5 6v5c0 5 3 8 7 10 4-2 7-5 7-10V6Z", "m9 12 2 2 4-5"],
  alert: ["M12 3 2.5 20h19Z", "M12 9v5", "M12 17h.01"],
  pulse: ["M3 12h4l2-6 4 12 2-6h6"],
  link: ["M10 13a5 5 0 0 0 7 0l2-2a5 5 0 0 0-7-7l-1 1", "M14 11a5 5 0 0 0-7 0l-2 2a5 5 0 0 0 7 7l1-1"],
  image: ["M4 4h16v16H4z", "m4 16 5-5 4 4 2-2 5 5", "M15 8h.01"],
  eye: ["M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z", "M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z"],
  brain: ["M9 4a3 3 0 0 0-3 3v1a3 3 0 0 0-1 5 3 3 0 0 0 3 4h1v3", "M15 4a3 3 0 0 1 3 3v1a3 3 0 0 1 1 5 3 3 0 0 1-3 4h-1v3", "M9 4v16M15 4v16"],
  arrow: ["M5 12h14", "m14 12-5-5", "m14 12-5 5"],
  clock: ["M12 3a9 9 0 1 0 9 9", "M12 7v5l3 2"],
  people: ["M16 20v-1.5a4.5 4.5 0 0 0-4.5-4.5h-3A4.5 4.5 0 0 0 4 18.5V20", "M10 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z", "M17 4.5a3.5 3.5 0 0 1 0 6.8", "M18 14a4 4 0 0 1 3 3.9V20"],
  check: ["M20 6 9 17l-5-5"],
};

function Icon({ name }) {
  return <svg viewBox="0 0 24 24" aria-hidden="true">{iconPaths[name].map((path) => <path key={path} d={path} />)}</svg>;
}

export default function OverviewPage({ history, user, onStartScan, onOpenStatistics, language = "vi" }) {
  const en = language === "en";
  const stats = history.reduce((summary, item) => {
    summary.total += 1;
    summary.score += Number(item.risk_score) || 0;
    if (item.risk_level === "an_toan") summary.safe += 1;
    return summary;
  }, { total: 0, safe: 0, score: 0 });

  const safePercent = stats.total ? Math.round((stats.safe / stats.total) * 100) : 100;
  const avgRisk = stats.total ? Math.round(stats.score / stats.total) : 0;
  const displayName = en && user?.full_name === "Người dùng khách" ? "Guest" : user?.full_name;
  const firstName = (displayName || (en ? "Guest" : "bạn")).trim().split(/\s+/).pop();

  return (
    <div className="console-overview">
      <section className="console-hero">
        <div className="console-hero-copy">
          <span className="console-live"><i /> {en ? "FREE DIGITAL SAFETY CHECK" : "KIỂM TRA AN TOÀN SỐ MIỄN PHÍ"}</span>
          <p className="console-greeting">{en ? `Hello, ${firstName}` : `Xin chào ${firstName},`}</p>
          <h2>
            <span className="hero-title-wide">{en ? <>Are you browsing<br /><em>safely?</em></> : <>Bạn có đang lướt mạng<br /><em>an toàn?</em></>}</span>
            <span className="hero-title-mobile">{en ? <>Are you<br /><em>safe online?</em></> : <>Bạn có đang<br /><em>an toàn?</em></>}</span>
          </h2>
          <p className="console-hero-lead">{en ? "Check a suspicious image, message, link or document before you trust, reply or make a payment." : "Kiểm tra hình ảnh, tin nhắn, đường link hoặc tài liệu đáng ngờ trước khi bạn tin tưởng, phản hồi hay chuyển tiền."}</p>
          <div className="console-hero-actions">
            <button onClick={onStartScan}><Icon name="scan" /> {en ? "Start a safety check" : "Bắt đầu kiểm tra"}</button>
            <span><i /> {en ? "Image · Message · URL · PDF" : "Ảnh · Tin nhắn · URL · PDF"}</span>
          </div>
        </div>

        <div className="public-protection-visual" aria-label={en ? `Average risk ${avgRisk} out of 100` : `Rủi ro trung bình ${avgRisk} trên 100`}>
          <span className="protection-orbit orbit-one" /><span className="protection-orbit orbit-two" /><span className="protection-orbit orbit-three" />
          <div className="protection-eye-character" aria-hidden="true">
            <div className="protection-eye-face">
              <img className="protection-eye-asset" src="/static/hero-safety-eye.png" alt="" />
              <span className="protection-eye-lid" />
            </div>
          </div>
          <span className="protection-tag protection-ai">AI</span><span className="protection-tag protection-url">URL</span><span className="protection-tag protection-ocr">OCR</span>
          <div className="protection-summary"><span><strong>{stats.total}</strong>{en ? "checks" : "lượt kiểm tra"}</span><span><strong>{safePercent}%</strong>{en ? "safe" : "an toàn"}</span></div>
        </div>
      </section>

      <section className="public-services-section">
        <header><span>{en ? "FREE TOOLS" : "CÔNG CỤ MIỄN PHÍ"}</span><h3>{en ? "Check suspicious content in one place" : "Kiểm tra nội dung đáng ngờ tại một nơi"}</h3><p>{en ? "Choose the type of information you received. The same analysis flow will explain the risks and recommend next steps." : "Chọn loại thông tin bạn nhận được. Hệ thống sẽ giải thích tín hiệu rủi ro và đề xuất cách xử lý tiếp theo."}</p></header>
        <div className="public-service-grid">
          {[
            ["image", en ? "Images & QR" : "Hình ảnh & QR", en ? "Read text, QR codes and visual warning signs." : "Đọc văn bản, mã QR và dấu hiệu bất thường trên ảnh."],
            ["link", en ? "Links & domains" : "Link & tên miền", en ? "Review URL structure and security intelligence." : "Đối chiếu cấu trúc URL và nguồn dữ liệu an toàn."],
            ["eye", en ? "Messages & email" : "Tin nhắn & email", en ? "Spot impersonation, urgency and payment traps." : "Phát hiện mạo danh, thúc ép và bẫy chuyển tiền."],
            ["brain", en ? "PDF documents" : "Tài liệu PDF", en ? "Extract and review notices, invoices and forms." : "Trích xuất và kiểm tra giấy báo, hóa đơn và biểu mẫu."],
          ].map(([icon, title, copy]) => <button type="button" onClick={onStartScan} key={title}><span><Icon name={icon} /></span><strong>{title}</strong><p>{copy}</p></button>)}
        </div>
      </section>

      <section className="public-safety-guide">
        <div className="public-guide-copy">
          <span>{en ? "SAFER IN THREE STEPS" : "AN TOÀN HƠN TRONG 3 BƯỚC"}</span>
          <h3>{en ? "Pause before you trust" : "Chậm lại một nhịp trước khi tin"}</h3>
          <p>{en ? "Scams work by creating urgency. A short check can help you recognize the signal and make a safer decision." : "Lừa đảo thường tạo cảm giác khẩn cấp. Một lần kiểm tra ngắn giúp bạn nhận diện tín hiệu và đưa ra quyết định an toàn hơn."}</p>
          <button type="button" onClick={onStartScan}>{en ? "Check suspicious content" : "Kiểm tra nội dung đáng ngờ"}<Icon name="arrow" /></button>
        </div>
        <ol className="public-guide-steps">
          <li><b>01</b><div><strong>{en ? "Recognize" : "Nhận diện"}</strong><p>{en ? "Look for impersonation, urgency and unusual payment requests." : "Chú ý dấu hiệu mạo danh, thúc ép và yêu cầu chuyển tiền bất thường."}</p></div></li>
          <li><b>02</b><div><strong>{en ? "Verify" : "Kiểm chứng"}</strong><p>{en ? "Check the image, message, link or document with multiple signals." : "Kiểm tra ảnh, tin nhắn, đường link hoặc tài liệu qua nhiều tín hiệu."}</p></div></li>
          <li><b>03</b><div><strong>{en ? "Act safely" : "Xử lý an toàn"}</strong><p>{en ? "Stop the interaction and contact the organization through an official channel." : "Dừng tương tác và liên hệ tổ chức qua kênh chính thức."}</p></div></li>
        </ol>
      </section>

      <section className="public-community-cta">
        <span className="community-cta-icon"><Icon name="people" /></span>
        <div><small>{en ? "YOUR PERSONAL SAFETY DATA" : "DỮ LIỆU AN TOÀN CỦA BẠN"}</small><h3>{en ? "See every check in one clear dashboard" : "Theo dõi mọi lượt kiểm tra trong một trang thống kê"}</h3><p>{en ? "View totals, risk trends, result distribution and your latest activity." : "Xem tổng số lượt, xu hướng rủi ro, phân bố kết quả và hoạt động gần đây."}</p></div>
        <button type="button" onClick={onOpenStatistics}>{en ? "Open statistics" : "Mở trang thống kê"}<Icon name="arrow" /></button>
      </section>
    </div>
  );
}
