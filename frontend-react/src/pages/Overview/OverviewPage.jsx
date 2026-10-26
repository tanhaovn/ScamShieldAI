const iconPaths = {
  scan: ["M4 8V5a1 1 0 0 1 1-1h3", "M16 4h3a1 1 0 0 1 1 1v3", "M20 16v3a1 1 0 0 1-1 1h-3", "M8 20H5a1 1 0 0 1-1-1v-3", "M8 12h8"],
  shield: ["M12 3 5 6v5c0 5 3 8 7 10 4-2 7-5 7-10V6Z", "m9 12 2 2 4-5"],
  alert: ["M12 3 2.5 20h19Z", "M12 9v5", "M12 17h.01"],
  pulse: ["M3 12h4l2-6 4 12 2-6h6"],
  eye: ["M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z", "M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z"],
  link: ["M10 13a5 5 0 0 0 7 0l2-2a5 5 0 0 0-7-7l-1 1", "M14 11a5 5 0 0 0-7 0l-2 2a5 5 0 0 0 7 7l1-1"],
  image: ["M4 4h16v16H4z", "m4 16 5-5 4 4 2-2 5 5", "M15 8h.01"],
  brain: ["M9 4a3 3 0 0 0-3 3v1a3 3 0 0 0-2 3 3 3 0 0 0 2 3v1a3 3 0 0 0 3 3", "M15 4a3 3 0 0 1 3 3v1a3 3 0 0 1 2 3 3 3 0 0 1-2 3v1a3 3 0 0 1-3 3", "M9 4v16", "M15 4v16"],
  arrow: ["M5 12h14", "m14 12-5-5", "m14 12-5 5"],
};

function Icon({ name }) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      {iconPaths[name].map((path) => <path key={path} d={path} />)}
    </svg>
  );
}

function buildTrend(history) {
  const source = history.slice(0, 10).reverse();
  return source.map((item, index) => ({
    id: item.id,
    score: Number(item.risk_score) || 0,
    x: source.length === 1 ? 300 : 28 + (index * 544) / Math.max(1, source.length - 1),
    y: 175 - ((Number(item.risk_score) || 0) / 100) * 135,
  }));
}

function riskLabel(level) {
  if (level === "nguy_hiem") return "Nguy hiểm";
  if (level === "nghi_ngo") return "Nghi ngờ";
  return "An toàn";
}

function formatTime(value) {
  if (!value) return "Vừa hoàn tất";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Vừa hoàn tất";
  return date.toLocaleString("vi-VN", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}

export default function OverviewPage({ history, user, onStartScan }) {
  const stats = history.reduce(
    (summary, item) => {
      summary.total += 1;
      summary.score += Number(item.risk_score || 0);
      if (item.risk_level === "an_toan") summary.safe += 1;
      if (item.risk_level === "nghi_ngo") summary.suspicious += 1;
      if (item.risk_level === "nguy_hiem") summary.danger += 1;
      return summary;
    },
    { total: 0, safe: 0, suspicious: 0, danger: 0, score: 0 },
  );

  const recentScans = history.slice(0, 5);
  const trend = buildTrend(history);
  const linePoints = trend.map((point) => `${point.x},${point.y}`).join(" ");
  const areaPoints = trend.length ? `28,175 ${linePoints} 572,175` : "";
  const average = stats.total ? Math.round(stats.score / stats.total) : 0;
  const safePercent = stats.total ? Math.round((stats.safe / stats.total) * 100) : 0;
  const suspiciousPercent = stats.total ? Math.round((stats.suspicious / stats.total) * 100) : 0;
  const dangerPercent = stats.total ? Math.round((stats.danger / stats.total) * 100) : 0;
  const safeAngle = stats.total ? (stats.safe / stats.total) * 360 : 0;
  const warningAngle = stats.total ? ((stats.safe + stats.suspicious) / stats.total) * 360 : 0;
  const firstName = (user?.full_name || "Thầy").trim().split(/\s+/).pop();
  const currentHour = new Date().getHours();
  const greeting = currentHour < 12 ? "Chào buổi sáng" : currentHour < 18 ? "Chào buổi chiều" : "Chào buổi tối";
  const threatStatus = stats.danger > 0 ? `${stats.danger} cảnh báo cần chú ý` : "Không có cảnh báo nghiêm trọng";

  const kpis = [
    { label: "Tổng lượt phân tích", value: stats.total, note: "Hồ sơ đã xử lý", icon: "scan", tone: "normal" },
    { label: "Kết quả an toàn", value: stats.safe, note: `${safePercent}% tổng lượt`, icon: "shield", tone: "safe" },
    { label: "Cần kiểm tra thêm", value: stats.suspicious, note: "Tín hiệu nghi ngờ", icon: "pulse", tone: "warning" },
    { label: "Cảnh báo nguy hiểm", value: stats.danger, note: "Không nên tương tác", icon: "alert", tone: "danger" },
  ];

  const layers = [
    ["OCR ENGINE", "Đọc văn bản Việt", "eye", "ONLINE"],
    ["PHISHVN URL", "Đối chiếu liên kết", "link", "ONLINE"],
    ["VISUAL FORENSICS", "Phân tích hình ảnh", "image", "ONLINE"],
    ["RISK AI", "Tổng hợp cảnh báo", "brain", "READY"],
  ];

  return (
    <div className="overview-command-center">
      <section className="overview-hero-command">
        <div className="overview-hero-grid" aria-hidden="true" />
        <div className="overview-command-copy">
          <div className="overview-live"><i /> PROTECTION SYSTEM · LIVE</div>
          <span className="overview-greeting">{greeting}, {firstName}</span>
          <h2>An toàn số bắt đầu từ một lần kiểm tra.</h2>
          <p>OCR, nhận diện URL lừa đảo và phân tích hình ảnh đang phối hợp để bảo vệ từng quyết định của bạn.</p>
          <div className="overview-command-actions">
            <button onClick={onStartScan}><Icon name="scan" /> Kiểm tra ngay</button>
            <span><i /> {threatStatus}</span>
          </div>
        </div>

        <div className="overview-radar" aria-hidden="true">
          <span className="overview-radar-ring ring-one" />
          <span className="overview-radar-ring ring-two" />
          <span className="overview-radar-ring ring-three" />
          <span className="overview-radar-cross cross-x" />
          <span className="overview-radar-cross cross-y" />
          <span className="overview-radar-sweep" />
          <i className="overview-radar-dot dot-one" />
          <i className="overview-radar-dot dot-two" />
          <i className="overview-radar-dot dot-three" />
          <div className="overview-radar-core"><strong>{average}</strong><small>RISK AVG</small></div>
          <b className="radar-tag tag-ocr">OCR</b>
          <b className="radar-tag tag-url">URL</b>
          <b className="radar-tag tag-ai">AI</b>
        </div>

        <div className="overview-hero-readout">
          <span>SECURITY READOUT</span>
          <div><strong>{String(stats.total).padStart(2, "0")}</strong><small>OBJECTS<br />SCANNED</small></div>
          <div><strong>{safePercent}%</strong><small>SAFE<br />RATIO</small></div>
          <div className="readout-bars"><i /><i /><i /><i /><i /><i /></div>
        </div>
      </section>

      <section className="overview-kpi-grid" aria-label="Chỉ số tổng quan">
        {kpis.map((item, index) => (
          <article className={`overview-kpi-card kpi-${item.tone}`} key={item.label} style={{ "--delay": `${index * 70}ms` }}>
            <span className="overview-kpi-icon"><Icon name={item.icon} /></span>
            <div><small>{item.label}</small><strong>{item.value}</strong><span>{item.note}</span></div>
            <div className="overview-kpi-wave" aria-hidden="true"><i /><i /><i /><i /><i /><i /><i /></div>
          </article>
        ))}
      </section>

      <section className="overview-engine-strip">
        <div className="engine-strip-title"><span>SYSTEM PIPELINE</span><strong>4 lớp phân tích đang hoạt động</strong></div>
        <div className="engine-layer-list">
          {layers.map(([name, description, icon, state], index) => (
            <div className="engine-layer" key={name}>
              <span className="engine-layer-index">0{index + 1}</span>
              <span className="engine-layer-icon"><Icon name={icon} /></span>
              <p><strong>{name}</strong><small>{description}</small></p>
              <b><i />{state}</b>
              {index < layers.length - 1 && <span className="engine-flow"><i /><i /><i /></span>}
            </div>
          ))}
        </div>
      </section>

      <div className="overview-analytics-grid">
        <section className="overview-panel overview-trend-panel">
          <div className="overview-panel-heading">
            <div><span>RISK TELEMETRY</span><h3>Xu hướng rủi ro</h3><p>10 lượt kiểm tra gần nhất</p></div>
            <div className="overview-chart-legend"><i /> Điểm rủi ro <b>0—100</b></div>
          </div>
          <div className="overview-risk-chart">
            <div className="overview-chart-y"><span>100</span><span>75</span><span>50</span><span>25</span><span>0</span></div>
            {trend.length ? (
              <svg viewBox="0 0 600 205" role="img" aria-label="Biểu đồ điểm rủi ro 10 lượt gần nhất">
                <defs>
                  <linearGradient id="overviewArea" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0" stopColor="#428E72" stopOpacity=".24" />
                    <stop offset="1" stopColor="#428E72" stopOpacity="0" />
                  </linearGradient>
                </defs>
                {[40, 74, 108, 142, 175].map((y) => <line key={y} x1="28" y1={y} x2="572" y2={y} className="overview-chart-gridline" />)}
                <polygon points={areaPoints} className="overview-chart-area" />
                <polyline points={linePoints} className="overview-chart-line" />
                {trend.map((point, index) => (
                  <g key={point.id} className="overview-chart-point" style={{ "--point-delay": `${index * 90}ms` }}>
                    <circle cx={point.x} cy={point.y} r="8" className="point-halo" />
                    <circle cx={point.x} cy={point.y} r="4" className="point-core" />
                    <text x={point.x} y={Math.max(19, point.y - 13)} textAnchor="middle">{point.score}</text>
                  </g>
                ))}
              </svg>
            ) : (
              <div className="overview-chart-empty"><span><Icon name="pulse" /></span><strong>Đang chờ tín hiệu đầu tiên</strong><small>Thực hiện một lượt kiểm tra để khởi tạo biểu đồ.</small></div>
            )}
          </div>
          <div className="overview-chart-footer"><span><i /> LIVE DATA</span><p>Điểm càng cao, nguy cơ lừa đảo càng lớn.</p></div>
        </section>

        <section className="overview-panel overview-distribution-panel">
          <div className="overview-panel-heading">
            <div><span>THREAT MAP</span><h3>Phân bổ kết quả</h3><p>Tất cả lượt đã phân tích</p></div>
          </div>
          <div
            className={`overview-risk-orbit${stats.total ? "" : " is-empty"}`}
            style={{ "--safe": `${safeAngle}deg`, "--warning": `${warningAngle}deg` }}
          >
            <span className="risk-orbit-track" />
            <div><strong>{stats.total}</strong><small>TỔNG LƯỢT</small><i /></div>
          </div>
          <div className="overview-distribution-list">
            <div><i className="distribution-safe" /><span>An toàn<small>{safePercent}% kết quả</small></span><strong>{stats.safe}</strong></div>
            <div><i className="distribution-warning" /><span>Nghi ngờ<small>{suspiciousPercent}% kết quả</small></span><strong>{stats.suspicious}</strong></div>
            <div><i className="distribution-danger" /><span>Nguy hiểm<small>{dangerPercent}% kết quả</small></span><strong>{stats.danger}</strong></div>
          </div>
        </section>
      </div>

      <div className="overview-bottom-grid">
        <section className="overview-panel overview-recent-panel">
          <div className="overview-panel-heading">
            <div><span>RECENT DETECTIONS</span><h3>Phân tích gần đây</h3><p>Dòng thời gian bảo vệ của bạn</p></div>
            <span className="overview-record-badge">{recentScans.length} bản ghi</span>
          </div>
          {recentScans.length ? (
            <div className="overview-recent-list">
              {recentScans.map((item, index) => (
                <article key={item.id}>
                  <span className={`recent-scan-icon ${item.risk_level}`}><Icon name="scan" /><i /></span>
                  <div><strong>{item.original_filename || `Lượt kiểm tra #${item.id}`}</strong><small>{formatTime(item.created_at)}</small></div>
                  <span className={`recent-risk-status ${item.risk_level}`}>{riskLabel(item.risk_level)}</span>
                  <div className="recent-score"><small>RISK</small><strong>{item.risk_score}</strong></div>
                  <span className="recent-row-scan" style={{ "--row-delay": `${index * 400}ms` }} />
                </article>
              ))}
            </div>
          ) : (
            <div className="overview-recent-empty"><Icon name="scan" /><strong>Chưa có dữ liệu phân tích</strong><span>Ảnh đầu tiên của bạn sẽ xuất hiện tại đây.</span><button onClick={onStartScan}>Bắt đầu kiểm tra <Icon name="arrow" /></button></div>
          )}
        </section>

        <section className="overview-panel overview-advice-panel">
          <div className="overview-panel-heading"><div><span>AI SAFETY BRIEF</span><h3>Bản tin an toàn</h3><p>Gợi ý dựa trên dữ liệu hiện tại</p></div></div>
          <div className={`overview-advice-status ${stats.danger ? "has-danger" : "is-safe"}`}>
            <span><Icon name={stats.danger ? "alert" : "shield"} /></span>
            <div><small>TRẠNG THÁI HIỆN TẠI</small><strong>{stats.danger ? "Có nội dung nguy hiểm" : "Vùng an toàn được duy trì"}</strong></div>
          </div>
          <p>{stats.danger
            ? `Hệ thống ghi nhận ${stats.danger} kết quả nguy hiểm. Không truy cập liên kết, chuyển tiền hoặc cung cấp mã OTP trong các nội dung này.`
            : "Chưa phát hiện cảnh báo nghiêm trọng trong lịch sử. Hãy tiếp tục kiểm tra các ảnh hoặc tin nhắn đáng ngờ trước khi tương tác."}</p>
          <div className="overview-advice-rule"><i />Không chia sẻ OTP hoặc mật khẩu</div>
          <div className="overview-advice-rule"><i />Kiểm tra kỹ tên miền trước khi truy cập</div>
          <button onClick={onStartScan}>Mở AI Scanner <Icon name="arrow" /></button>
        </section>
      </div>
    </div>
  );
}
