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
};

function Icon({ name }) {
  return <svg viewBox="0 0 24 24" aria-hidden="true">{iconPaths[name].map((path) => <path key={path} d={path} />)}</svg>;
}

function formatTime(value, language) {
  if (!value) return language === "en" ? "Just now" : "Vừa xong";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return language === "en" ? "Just now" : "Vừa xong";
  return date.toLocaleString(language === "en" ? "en-US" : "vi-VN", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}

function riskLabel(level, language) {
  if (level === "nguy_hiem") return language === "en" ? "Danger" : "Nguy hiểm";
  if (level === "nghi_ngo") return language === "en" ? "Review" : "Cần kiểm tra";
  return language === "en" ? "Safe" : "An toàn";
}

function SparkBars({ tone }) {
  return <span className={`console-spark ${tone}`} aria-hidden="true">{[3, 6, 4, 8, 10, 7, 11].map((height, index) => <i key={index} style={{ height: `${height + 4}px` }} />)}</span>;
}

export default function OverviewPage({ history, user, onStartScan, language = "vi" }) {
  const en = language === "en";
  const stats = history.reduce((summary, item) => {
    summary.total += 1;
    summary.score += Number(item.risk_score) || 0;
    if (item.risk_level === "an_toan") summary.safe += 1;
    if (item.risk_level === "nghi_ngo") summary.suspicious += 1;
    if (item.risk_level === "nguy_hiem") summary.danger += 1;
    return summary;
  }, { total: 0, safe: 0, suspicious: 0, danger: 0, score: 0 });

  const safePercent = stats.total ? Math.round((stats.safe / stats.total) * 100) : 100;
  const avgRisk = stats.total ? Math.round(stats.score / stats.total) : 0;
  const safeShare = stats.total ? (stats.safe / stats.total) * 100 : 100;
  const warningShare = stats.total ? (stats.suspicious / stats.total) * 100 : 0;
  const distribution = { background: `conic-gradient(#4f9d7f 0 ${safeShare}%, #d9a441 ${safeShare}% ${safeShare + warningShare}%, #d86666 ${safeShare + warningShare}% 100%)` };
  const recent = history.slice(0, 5);
  const trend = history.slice(0, 10).reverse();
  const chartData = trend.length ? trend : [{ risk_score: 0 }, { risk_score: 0 }];
  const chartPoints = chartData.map((item, index, list) => {
    const x = 24 + (index * 552) / Math.max(1, list.length - 1);
    const y = 150 - Math.min(100, Math.max(0, Number(item.risk_score) || 0)) * 1.15;
    return `${x},${y}`;
  }).join(" ");
  const displayName = en && user?.full_name === "Người dùng khách" ? "Guest" : user?.full_name;
  const firstName = (displayName || (en ? "Guest" : "bạn")).trim().split(/\s+/).pop();

  const statCards = [
    { icon: "scan", label: en ? "Total analyses" : "Tổng lượt phân tích", value: stats.total, note: en ? "Processed records" : "Hồ sơ đã xử lý", tone: "neutral" },
    { icon: "shield", label: en ? "Safe results" : "Kết quả an toàn", value: stats.safe, note: `${stats.total ? safePercent : 0}% ${en ? "of all checks" : "tổng lượt"}`, tone: "safe" },
    { icon: "pulse", label: en ? "Needs review" : "Cần kiểm tra thêm", value: stats.suspicious, note: en ? "Suspicious signals" : "Tín hiệu nghi ngờ", tone: "warning" },
    { icon: "alert", label: en ? "Danger alerts" : "Cảnh báo nguy hiểm", value: stats.danger, note: en ? "Do not interact" : "Không nên tương tác", tone: "danger" },
  ];
  const pipeline = [
    ["eye", "OCR ENGINE", en ? "Reads Vietnamese text" : "Đọc văn bản Việt"],
    ["link", "PHISHVN + GOOGLE", en ? "Cross-checks URLs" : "Đối chiếu liên kết"],
    ["image", "VISUAL FORENSICS", en ? "Analyzes image signals" : "Phân tích hình ảnh"],
    ["brain", "RISK AI", en ? "Explains the warning" : "Tổng hợp cảnh báo"],
  ];

  return (
    <div className="console-overview">
      <section className="console-hero">
        <div className="console-hero-copy">
          <span className="console-live"><i /> {en ? "PROTECTION SYSTEM · LIVE" : "HỆ THỐNG BẢO VỆ · TRỰC TUYẾN"}</span>
          <p className="console-greeting">{en ? `Hello, ${firstName}` : `Chào ${firstName},`}</p>
          <h2>{en ? <>Digital safety starts<br />with one check.</> : <>An toàn số bắt đầu từ<br />một lần kiểm tra.</>}</h2>
          <p className="console-hero-lead">{en ? "OCR, verified URL intelligence and image analysis work together to protect every decision." : "OCR, nguồn đối chiếu URL và phân tích hình ảnh phối hợp để bảo vệ từng quyết định của bạn."}</p>
          <div className="console-hero-actions">
            <button onClick={onStartScan}><Icon name="scan" /> {en ? "Check now" : "Kiểm tra ngay"} <Icon name="arrow" /></button>
            <span><i /> {stats.danger ? (en ? `${stats.danger} danger alert${stats.danger > 1 ? "s" : ""}` : `${stats.danger} cảnh báo nguy hiểm`) : (en ? "No critical alerts" : "Không có cảnh báo nghiêm trọng")}</span>
          </div>
        </div>

        <div className="console-radar-zone" aria-label={en ? `Average risk ${avgRisk} out of 100` : `Rủi ro trung bình ${avgRisk} trên 100`}>
          <div className="console-radar">
            <span className="radar-ring ring-a" /><span className="radar-ring ring-b" /><span className="radar-ring ring-c" />
            <span className="radar-cross horizontal" /><span className="radar-cross vertical" /><span className="radar-sweep" />
            <span className="radar-lock-frame" />
            <span className="radar-blip blip-a" /><span className="radar-blip blip-b" /><span className="radar-blip blip-c" /><span className="radar-blip blip-d" />
            <span className="radar-node node-ocr"><i />OCR</span><span className="radar-node node-url"><i />URL</span><span className="radar-node node-ai"><i />AI</span>
            <div className="radar-core"><strong>{avgRisk}</strong><small>{en ? "RISK AVG" : "RỦI RO TB"}</small></div>
          </div>
          <div className="console-readout">
            <span>{en ? "SECURITY READOUT" : "CHỈ SỐ AN TOÀN"}</span>
            <div><strong>{String(stats.total).padStart(2, "0")}</strong><small>{en ? "OBJECTS SCANNED" : "LƯỢT ĐÃ QUÉT"}</small></div>
            <div><strong>{safePercent}%</strong><small>{en ? "SAFE RATIO" : "TỶ LỆ AN TOÀN"}</small></div>
            <SparkBars tone="safe" />
          </div>
        </div>
      </section>

      <section className="console-stat-grid">
        {statCards.map((card) => <article className={`console-stat-card ${card.tone}`} key={card.label}><span className="console-stat-icon"><Icon name={card.icon} /></span><div><small>{card.label}</small><strong>{card.value}</strong><span>{card.note}</span></div><SparkBars tone={card.tone} /></article>)}
      </section>

      <section className="console-pipeline">
        <div className="console-pipeline-title"><span>SYSTEM PIPELINE</span><strong>{en ? "4 analysis layers are active" : "4 lớp phân tích đang hoạt động"}</strong></div>
        <div className="console-pipeline-flow">
          {pipeline.map(([icon, title, note], index) => <article key={title}><b>{String(index + 1).padStart(2, "0")}</b><span><Icon name={icon} /></span><div><strong>{title}</strong><small>{note}</small></div><i>{index === 3 ? "READY" : "ONLINE"}</i></article>)}
        </div>
      </section>

      <section className="console-analytics-grid">
        <article className="console-panel console-trend-panel">
          <header><div><span>{en ? "RISK TELEMETRY" : "DỮ LIỆU RỦI RO"}</span><h3>{en ? "Recent risk trend" : "Xu hướng rủi ro"}</h3><p>{en ? "Last 10 checks" : "10 lượt kiểm tra gần nhất"}</p></div><b><i /> {en ? "Risk score" : "Điểm rủi ro"} <strong>0–100</strong></b></header>
          <div className="console-chart-wrap"><div className="console-chart-axis"><span>100</span><span>75</span><span>50</span><span>25</span><span>0</span></div><svg viewBox="0 0 600 170" preserveAspectRatio="none" aria-label={en ? "Risk trend chart" : "Biểu đồ xu hướng rủi ro"}><defs><linearGradient id="riskArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#579f84" stopOpacity=".3" /><stop offset="1" stopColor="#579f84" stopOpacity="0" /></linearGradient></defs><path className="console-chart-grid" d="M20 35H580M20 64H580M20 93H580M20 122H580M20 150H580" /><polygon points={`24,150 ${chartPoints} 576,150`} fill="url(#riskArea)" /><polyline points={chartPoints} fill="none" />{chartData.map((item, index, list) => { const cx = 24 + (index * 552) / Math.max(1, list.length - 1); const cy = 150 - Math.min(100, Math.max(0, Number(item.risk_score) || 0)) * 1.15; return <circle key={index} cx={cx} cy={cy} r="4" />; })}</svg></div>
        </article>

        <article className="console-panel console-distribution-panel">
          <header><div><span>{en ? "THREAT MAP" : "PHÂN BỐ KẾT QUẢ"}</span><h3>{en ? "Result distribution" : "Mức độ an toàn"}</h3><p>{en ? "All analyzed content" : "Tất cả lượt đã phân tích"}</p></div></header>
          <div className="console-donut" style={distribution}><div><strong>{stats.total}</strong><span>{en ? "checks" : "lượt quét"}</span></div></div>
          <div className="console-donut-legend"><span className="safe"><i />{en ? "Safe" : "An toàn"}<b>{stats.safe}</b></span><span className="warning"><i />{en ? "Review" : "Kiểm tra"}<b>{stats.suspicious}</b></span><span className="danger"><i />{en ? "Danger" : "Nguy hiểm"}<b>{stats.danger}</b></span></div>
        </article>
      </section>

      <section className="console-panel console-recent-panel">
        <header><div><span>{en ? "LATEST ACTIVITY" : "HOẠT ĐỘNG GẦN ĐÂY"}</span><h3>{en ? "Recent checks" : "Lượt kiểm tra gần nhất"}</h3></div><button onClick={onStartScan}>{en ? "New check" : "Kiểm tra mới"}<Icon name="arrow" /></button></header>
        <div className="console-recent-list">{recent.length ? recent.map((item) => <article key={item.id}><span className={`console-recent-icon ${item.risk_level}`}><Icon name={item.source_type === "url" ? "link" : item.source_type === "image" ? "image" : "scan"} /></span><div><strong>{item.original_filename || (en ? "Checked content" : "Nội dung đã kiểm tra")}</strong><small><Icon name="clock" /> {formatTime(item.created_at, language)}</small></div><b className={item.risk_level}>{riskLabel(item.risk_level, language)} · {item.risk_score || 0}</b></article>) : <div className="console-empty"><span><Icon name="scan" /></span><div><strong>{en ? "No checks yet" : "Chưa có lượt kiểm tra"}</strong><small>{en ? "Start with an image, message, URL or PDF." : "Bắt đầu với ảnh, tin nhắn, URL hoặc PDF đáng ngờ."}</small></div><button onClick={onStartScan}>{en ? "Start now" : "Bắt đầu ngay"}</button></div>}</div>
      </section>
    </div>
  );
}
