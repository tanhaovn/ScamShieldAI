import Button from "../../components/Button";
import Card from "../../components/Card";

export default function OverviewPage({ history, onStartScan }) {
  const stats = history.reduce(
    (summary, item) => {
      summary.total += 1;
      if (item.risk_level === "an_toan") summary.safe += 1;
      if (item.risk_level === "nghi_ngo") summary.suspicious += 1;
      if (item.risk_level === "nguy_hiem") summary.danger += 1;
      return summary;
    },
    { total: 0, safe: 0, suspicious: 0, danger: 0 },
  );
  const recentScans = history.slice(0, 5);
  const maxScore = Math.max(
    ...recentScans.map((item) => Number(item.risk_score) || 0),
    1,
  );

  return (
    <main className="overview-shell">
      <section className="hero-intro">
        <span className="eyebrow">SCAM DETECTOR · IMAGE VERIFICATION</span>
        <h1>
          Đừng đoán.
          <br />
          Hãy kiểm tra.
        </h1>
        <p>
          Phân tích ảnh, OCR và tín hiệu rủi ro trong vài giây để biết điều gì
          đáng tin trước khi bạn hành động.
        </p>
        <div className="welcome-actions">
          <Button onClick={onStartScan}>Kiểm tra hình ảnh</Button>
          <span className="trust-note">
            Không cần cài đặt · Kết quả dễ hiểu
          </span>
        </div>
      </section>

      <section
        className="hero-showcase"
        aria-label="Minh họa kết quả phân tích"
      >
        <div className="showcase-image image-one">
          <span>REAL</span>
        </div>
        <div className="showcase-image image-two">
          <span>OCR</span>
        </div>
        <Card className="showcase-result">
          <div className="result-kicker">
            <span className="status-dot" /> ANALYSIS COMPLETE
          </div>
          <strong>Ảnh có dấu hiệu đáng ngờ</strong>
          <div className="result-meter">
            <span />
          </div>
          <div className="result-score">
            <b>57</b>
            <span>/ 100 risk score</span>
          </div>
          <small>OCR · Visual signals · Scam patterns</small>
        </Card>
        <div className="showcase-image image-three">
          <span>SAFE?</span>
        </div>
      </section>

      <div className="overview-stats">
        <Card className="stat-card">
          <strong>01</strong>
          <span>Upload hoặc chụp ảnh</span>
        </Card>
        <Card className="stat-card">
          <strong>02</strong>
          <span>Đọc tín hiệu bằng OCR</span>
        </Card>
        <Card className="stat-card">
          <strong>03</strong>
          <span>Hành động với đủ thông tin</span>
        </Card>
      </div>

      <section className="dashboard-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">LIVE OVERVIEW</span>
            <h2>Nhìn nhanh tình hình kiểm tra</h2>
          </div>
          <span className="section-meta">Dữ liệu từ các lần scan gần nhất</span>
        </div>
        <div className="metric-grid">
          <Card className="metric-card metric-total">
            <span>TỔNG LƯỢT KIỂM TRA</span>
            <strong>{stats.total}</strong>
            <small>ảnh đã được phân tích</small>
          </Card>
          <Card className="metric-card metric-safe">
            <span>AN TOÀN</span>
            <strong>{stats.safe}</strong>
            <small>tín hiệu thấp</small>
          </Card>
          <Card className="metric-card metric-suspicious">
            <span>NGHI NGỜ</span>
            <strong>{stats.suspicious}</strong>
            <small>cần xem lại</small>
          </Card>
          <Card className="metric-card metric-danger">
            <span>NGUY HIỂM</span>
            <strong>{stats.danger}</strong>
            <small>nên xử lý ngay</small>
          </Card>
        </div>

        <div className="dashboard-lower">
          <Card className="activity-card">
            <div className="card-heading">
              <h3>Hoạt động gần đây</h3>
              <span>{recentScans.length} bản ghi</span>
            </div>
            {recentScans.length === 0 ? (
              <p className="empty-state">
                Chưa có lần kiểm tra nào. Hãy bắt đầu với một hình ảnh.
              </p>
            ) : (
              <ul className="activity-list">
                {recentScans.map((item) => (
                  <li key={item.id}>
                    <span className={`risk-mark risk-${item.risk_level}`} />
                    <div>
                      <strong>
                        {item.original_filename ||
                          `Category #${item.scam_category_id}`}
                      </strong>
                      <small>
                        {item.risk_level} ·{" "}
                        {item.created_at
                          ? new Date(item.created_at).toLocaleString("vi-VN")
                          : "Vừa xong"}
                      </small>
                    </div>
                    <b>{item.risk_score}</b>
                  </li>
                ))}
              </ul>
            )}
          </Card>
          <Card className="distribution-card">
            <div className="card-heading">
              <h3>Phân bổ rủi ro</h3>
              <span>Risk score</span>
            </div>
            <div className="distribution-chart">
              {recentScans.length === 0 ? (
                <p className="empty-state">Chưa có dữ liệu biểu đồ.</p>
              ) : (
                recentScans.map((item) => (
                  <div className="chart-column" key={item.id}>
                    <span
                      style={{
                        height: `${Math.max(12, ((Number(item.risk_score) || 0) / maxScore) * 100)}%`,
                      }}
                    />
                    <small>{item.risk_score}</small>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
      </section>
    </main>
  );
}
