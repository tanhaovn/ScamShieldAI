import { useEffect, useMemo, useState } from "react";

const riskMeta = {
  an_toan: { label: "An toàn", short: "SAFE", className: "safe" },
  nghi_ngo: { label: "Nghi ngờ", short: "REVIEW", className: "warning" },
  nguy_hiem: { label: "Nguy hiểm", short: "ALERT", className: "danger" },
};

function getRiskMeta(level) {
  return riskMeta[level] || {
    label: level || "Chưa xác định",
    short: "UNKNOWN",
    className: "unknown",
  };
}

function formatDate(value, compact = false) {
  if (!value) return "Không có thời gian";
  return new Date(value).toLocaleString("vi-VN", compact
    ? { day: "2-digit", month: "2-digit", year: "numeric" }
    : undefined);
}

function ScoreRing({ score, large = false }) {
  const normalized = Math.min(100, Math.max(0, Number(score) || 0));
  return (
    <div
      className={large ? "history-score-ring large" : "history-score-ring"}
      style={{ "--history-score": `${normalized * 3.6}deg` }}
      aria-label={`Điểm rủi ro ${normalized} trên 100`}
    >
      <div><strong>{normalized}</strong><small>/100</small></div>
    </div>
  );
}

function DetectionPreview({ item, apiBase, modal = false }) {
  return (
    <div className={modal ? "history-detect-preview modal" : "history-detect-preview"}>
      {item.image_url ? (
        <img
          src={`${apiBase}${item.image_url}`}
          alt={item.original_filename || "Ảnh đã kiểm tra"}
        />
      ) : (
        <div className="history-preview-placeholder">
          <span>AI</span>
          <small>NO PREVIEW</small>
        </div>
      )}
      <div className="history-tech-mesh" />
      <div className="history-scan-line" />
      <span className="history-corner corner-tl" />
      <span className="history-corner corner-tr" />
      <span className="history-corner corner-bl" />
      <span className="history-corner corner-br" />
      <div className="history-detect-label"><i /> DETECTED</div>
      <div className="history-preview-code">SCAN #{String(item.id).padStart(4, "0")}</div>
    </div>
  );
}

export default function HistoryPage({
  history,
  selectedHistory,
  setSelectedHistory,
  apiBase,
}) {
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!selectedHistory) return undefined;
    const closeOnEscape = (event) => {
      if (event.key === "Escape") setSelectedHistory(null);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [selectedHistory, setSelectedHistory]);

  const stats = useMemo(() => {
    const summary = { total: history.length, safe: 0, warning: 0, danger: 0, average: 0 };
    let scoreTotal = 0;
    history.forEach((item) => {
      scoreTotal += Number(item.risk_score) || 0;
      const meta = getRiskMeta(item.risk_level);
      if (meta.className === "safe") summary.safe += 1;
      if (meta.className === "warning") summary.warning += 1;
      if (meta.className === "danger") summary.danger += 1;
    });
    summary.average = summary.total ? Math.round(scoreTotal / summary.total) : 0;
    return summary;
  }, [history]);

  const filteredHistory = useMemo(() => {
    const keyword = search.trim().toLowerCase();
    return history.filter((item) => {
      const riskClass = getRiskMeta(item.risk_level).className;
      const matchesFilter = filter === "all" || riskClass === filter;
      const filename = (item.original_filename || "").toLowerCase();
      const matchesSearch = !keyword || filename.includes(keyword) || String(item.id).includes(keyword);
      return matchesFilter && matchesSearch;
    });
  }, [filter, history, search]);

  const filters = [
    ["all", "Tất cả", stats.total],
    ["safe", "An toàn", stats.safe],
    ["warning", "Nghi ngờ", stats.warning],
    ["danger", "Nguy hiểm", stats.danger],
  ];

  return (
    <>
      <div className="history-experience">
        <section className="history-command-center">
          <div className="history-command-copy">
            <span className="history-live"><i /> DETECTION ARCHIVE ONLINE</span>
            <h2>Trung tâm lịch sử phân tích</h2>
            <p>
              Theo dõi lại từng lần OCR, nhận diện URL và đánh giá hình ảnh trong
              một không gian trực quan.
            </p>
            <div className="history-command-metrics">
              <div><strong>{stats.total}</strong><span>Tổng lượt quét</span></div>
              <div><strong>{stats.average}</strong><span>Điểm trung bình</span></div>
              <div><strong>{stats.danger}</strong><span>Cảnh báo cao</span></div>
            </div>
          </div>
          <div className="history-radar" aria-hidden="true">
            <div className="radar-grid" />
            <div className="radar-circle circle-one" />
            <div className="radar-circle circle-two" />
            <div className="radar-circle circle-three" />
            <div className="radar-sweep" />
            <span className="radar-dot dot-one" />
            <span className="radar-dot dot-two" />
            <span className="radar-dot dot-three" />
            <div className="radar-core"><strong>{stats.total}</strong><small>SCANS</small></div>
          </div>
        </section>

        <section className="history-browser panel">
          <header className="history-browser-header">
            <div>
              <span className="eyebrow">ANALYSIS RECORDS</span>
              <h3>Dữ liệu đã kiểm tra</h3>
              <p>{filteredHistory.length} kết quả đang hiển thị</p>
            </div>
            <label className="history-search">
              <span aria-hidden="true">⌕</span>
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Tìm tên file hoặc mã lượt quét"
              />
            </label>
          </header>

          <div className="history-filter-row" role="tablist" aria-label="Lọc lịch sử theo mức độ">
            {filters.map(([value, label, count]) => (
              <button
                type="button"
                role="tab"
                aria-selected={filter === value}
                className={filter === value ? "active" : ""}
                key={value}
                onClick={() => setFilter(value)}
              >
                {label}<b>{count}</b>
              </button>
            ))}
          </div>

          {filteredHistory.length === 0 ? (
            <div className="history-empty-state">
              <div className="empty-radar"><span /></div>
              <strong>Không tìm thấy lượt kiểm tra</strong>
              <p>Thử chọn bộ lọc khác hoặc thay đổi từ khóa tìm kiếm.</p>
            </div>
          ) : (
            <div className="history-card-grid">
              {filteredHistory.map((item) => {
                const meta = getRiskMeta(item.risk_level);
                return (
                  <article className={`history-record-card ${meta.className}`} key={item.id}>
                    <DetectionPreview item={item} apiBase={apiBase} />
                    <div className="history-record-body">
                      <div className="history-record-topline">
                        <span className={`history-risk-status ${meta.className}`}><i /> {meta.label}</span>
                        <span>{formatDate(item.created_at, true)}</span>
                      </div>
                      <h4>{item.original_filename || `Lượt kiểm tra #${item.id}`}</h4>
                      <p>Mã phân tích · SD-{String(item.id).padStart(5, "0")}</p>
                      <div className="history-engine-tags">
                        <span>OCR</span><span>URL</span><span>VISUAL</span>
                      </div>
                      <div className="history-record-footer">
                        <ScoreRing score={item.risk_score} />
                        <button type="button" onClick={() => setSelectedHistory(item)}>
                          Mở phân tích <span>→</span>
                        </button>
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>
      </div>

      {selectedHistory && (
        <div className="modal-backdrop history-modal-backdrop" role="presentation" onClick={() => setSelectedHistory(null)}>
          <section
            className="history-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="history-detail-title"
            onClick={(event) => event.stopPropagation()}
          >
            <header className="history-modal-header">
              <div>
                <span className="history-live"><i /> ANALYSIS REPLAY</span>
                <h3 id="history-detail-title">Chi tiết lần kiểm tra #{selectedHistory.id}</h3>
              </div>
              <button type="button" className="history-modal-close" onClick={() => setSelectedHistory(null)} aria-label="Đóng chi tiết">×</button>
            </header>

            <div className="history-modal-layout">
              <div className="history-modal-visual">
                <DetectionPreview item={selectedHistory} apiBase={apiBase} modal />
                <div className="history-modal-score">
                  <ScoreRing score={selectedHistory.risk_score} large />
                  <div>
                    <span>Mức đánh giá</span>
                    <strong>{getRiskMeta(selectedHistory.risk_level).label}</strong>
                    <small>{getRiskMeta(selectedHistory.risk_level).short} SIGNAL</small>
                  </div>
                </div>
                <div className="history-detail-grid tech">
                  <div><span className="detail-label">File nguồn</span><strong>{selectedHistory.original_filename || "Không có"}</strong></div>
                  <div><span className="detail-label">Thời gian</span><strong>{formatDate(selectedHistory.created_at)}</strong></div>
                </div>
              </div>

              <div className="history-modal-analysis">
                <section className="history-analysis-section">
                  <header><span>01</span><div><strong>Kết luận AI</strong><small>RISK EXPLANATION</small></div></header>
                  <p>{selectedHistory.explanation || "Không có giải thích được lưu cho lượt kiểm tra này."}</p>
                </section>
                <section className="history-analysis-section">
                  <header><span>02</span><div><strong>Hành động đề xuất</strong><small>SAFETY ACTION</small></div></header>
                  <p>{selectedHistory.suggested_action || "Chưa có hành động đề xuất."}</p>
                </section>
                <details className="history-ocr-section" open>
                  <summary><span>03</span><div><strong>Văn bản OCR</strong><small>EXTRACTED CONTENT</small></div><b>⌄</b></summary>
                  <pre>{selectedHistory.extracted_text || "Không nhận diện được văn bản trong ảnh."}</pre>
                </details>
                <div className="history-pipeline">
                  <span className="done"><i /> OCR</span><b>→</b>
                  <span className="done"><i /> URL MODEL</span><b>→</b>
                  <span className="done"><i /> RISK AI</span>
                </div>
              </div>
            </div>
          </section>
        </div>
      )}
    </>
  );
}
