import { useEffect, useMemo, useState } from "react";

const riskMeta = {
  an_toan: { label: "An toàn", short: "An toàn", className: "safe" },
  nghi_ngo: { label: "Nghi ngờ", short: "Cần kiểm tra", className: "warning" },
  nguy_hiem: { label: "Nguy hiểm", short: "Cảnh báo", className: "danger" },
};

function getRiskMeta(level, language = "vi") {
  const meta = riskMeta[level] || {
    label: level || "Chưa xác định",
    short: "Chưa xác định",
    className: "unknown",
  };
  if (language !== "en") return meta;
  const english = {
    an_toan: { label: "Safe", short: "Safe" },
    nghi_ngo: { label: "Suspicious", short: "Review" },
    nguy_hiem: { label: "Dangerous", short: "Warning" },
  }[level] || { label: level || "Unknown", short: "Unknown" };
  return { ...meta, ...english };
}

function formatDate(value, compact = false, language = "vi") {
  if (!value) return language === "en" ? "No timestamp" : "Không có thời gian";
  return new Date(value).toLocaleString(language === "en" ? "en-US" : "vi-VN", compact
    ? { day: "2-digit", month: "2-digit", year: "numeric" }
    : undefined);
}

function ScoreRing({ score, large = false, language = "vi" }) {
  const normalized = Math.min(100, Math.max(0, Number(score) || 0));
  return (
    <div
      className={large ? "history-score-ring large" : "history-score-ring"}
      style={{ "--history-score": `${normalized * 3.6}deg` }}
      aria-label={language === "en" ? `Risk score ${normalized} out of 100` : `Điểm rủi ro ${normalized} trên 100`}
    >
      <div><strong>{normalized}</strong><small>/100</small></div>
    </div>
  );
}

function DetectionPreview({ item, apiBase, modal = false, language = "vi" }) {
  return (
    <div className={modal ? "history-detect-preview modal" : "history-detect-preview"}>
      {item.image_url ? (
        <img
          src={`${apiBase}${item.image_url}`}
          alt={item.original_filename || (language === "en" ? "Checked image" : "Ảnh đã kiểm tra")}
        />
      ) : (
        <div className="history-preview-placeholder"><span>AI</span><small>{language === "en" ? "No image preview" : "Không có ảnh xem trước"}</small></div>
      )}
    </div>
  );
}

export default function HistoryPage({
  history,
  selectedHistory,
  setSelectedHistory,
  apiBase,
  isGuest = false,
  language = "vi",
}) {
  const en = language === "en";
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
      const meta = getRiskMeta(item.risk_level, language);
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
      const riskClass = getRiskMeta(item.risk_level, language).className;
      const matchesFilter = filter === "all" || riskClass === filter;
      const filename = (item.original_filename || "").toLowerCase();
      const matchesSearch = !keyword || filename.includes(keyword) || String(item.id).includes(keyword);
      return matchesFilter && matchesSearch;
    });
  }, [filter, history, search]);

  const filters = [
    ["all", en ? "All" : "Tất cả", stats.total],
    ["safe", en ? "Safe" : "An toàn", stats.safe],
    ["warning", en ? "Suspicious" : "Nghi ngờ", stats.warning],
    ["danger", en ? "Dangerous" : "Nguy hiểm", stats.danger],
  ];

  return (
    <>
      <div className="history-experience">
        <section className="history-command-center">
          <div className="history-command-copy">
            <span className="history-live"><i /> {isGuest ? (en ? "History saved on this device" : "Lịch sử lưu trên thiết bị") : (en ? "Account history" : "Lịch sử tài khoản")}</span>
            <h2>{en ? "Content you have checked" : "Các nội dung bạn đã kiểm tra"}</h2>
            <p>
              {en ? "Review results, warning levels and safety guidance from every check." : "Xem lại kết quả, mức cảnh báo và hướng dẫn an toàn của từng lần kiểm tra."}
            </p>
            <div className="history-command-metrics">
              <div><strong>{stats.total}</strong><span>{en ? "Total checks" : "Tổng lượt quét"}</span></div>
              <div><strong>{stats.average}</strong><span>{en ? "Average score" : "Điểm trung bình"}</span></div>
              <div><strong>{stats.danger}</strong><span>{en ? "High warnings" : "Cảnh báo cao"}</span></div>
            </div>
            {isGuest && (
              <div className="history-local-notice">
                <i>✓</i>
                <span><strong>{en ? "Saved in this browser" : "Đang lưu trên trình duyệt này"}</strong>{en ? "Your data remains here when you return with the same browser." : "Dữ liệu vẫn còn khi bạn quay lại bằng cùng trình duyệt."}</span>
              </div>
            )}
          </div>
        </section>

        <section className="history-browser panel">
          <header className="history-browser-header">
            <div>
              <span className="eyebrow">{en ? "CHECK HISTORY" : "LỊCH SỬ KIỂM TRA"}</span>
              <h3>{en ? "Saved results" : "Kết quả đã lưu"}</h3>
              <p>{filteredHistory.length} {en ? "results shown" : "kết quả đang hiển thị"}</p>
            </div>
            <label className="history-search">
              <span aria-hidden="true">⌕</span>
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder={en ? "Search filename or check ID" : "Tìm tên file hoặc mã lượt quét"}
              />
            </label>
          </header>

          <div className="history-filter-row" role="tablist" aria-label={en ? "Filter history by risk" : "Lọc lịch sử theo mức độ"}>
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
              <strong>{en ? "No checks found" : "Không tìm thấy lượt kiểm tra"}</strong>
              <p>{en ? "Try a different filter or search term." : "Thử chọn bộ lọc khác hoặc thay đổi từ khóa tìm kiếm."}</p>
            </div>
          ) : (
            <div className="history-card-grid">
              {filteredHistory.map((item) => {
                const meta = getRiskMeta(item.risk_level, language);
                return (
                  <article className={`history-record-card ${meta.className}`} key={item.id}>
                    <DetectionPreview item={item} apiBase={apiBase} language={language} />
                    <div className="history-record-body">
                      <div className="history-record-topline">
                        <span className={`history-risk-status ${meta.className}`}><i /> {meta.label}</span>
                        <span>{formatDate(item.created_at, true, language)}</span>
                      </div>
                      <h4>{item.original_filename || `${en ? "Check" : "Lượt kiểm tra"} #${item.id}`}</h4>
                      <p>{en ? "Result ID" : "Mã kết quả"} · SD-{String(item.id).padStart(5, "0")}</p>
                      <div className="history-record-footer">
                        <ScoreRing score={item.risk_score} language={language} />
                        <button type="button" onClick={() => setSelectedHistory(item)}>
                          {en ? "Open analysis" : "Mở phân tích"} <span>→</span>
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
                <span className="history-live"><i /> {en ? "REVIEW RESULT" : "XEM LẠI KẾT QUẢ"}</span>
                <h3 id="history-detail-title">{en ? "Check details" : "Chi tiết lần kiểm tra"} #{selectedHistory.id}</h3>
              </div>
              <button type="button" className="history-modal-close" onClick={() => setSelectedHistory(null)} aria-label={en ? "Close details" : "Đóng chi tiết"}>×</button>
            </header>

            <div className="history-modal-layout">
              <div className="history-modal-visual">
                <DetectionPreview item={selectedHistory} apiBase={apiBase} modal language={language} />
                <div className="history-modal-score">
                  <ScoreRing score={selectedHistory.risk_score} large language={language} />
                  <div>
                    <span>{en ? "Risk level" : "Mức đánh giá"}</span>
                    <strong>{getRiskMeta(selectedHistory.risk_level, language).label}</strong>
                    <small>{getRiskMeta(selectedHistory.risk_level, language).short}</small>
                  </div>
                </div>
                <div className="history-detail-grid tech">
                  <div><span className="detail-label">{en ? "Source file" : "File nguồn"}</span><strong>{selectedHistory.original_filename || (en ? "None" : "Không có")}</strong></div>
                  <div><span className="detail-label">{en ? "Time" : "Thời gian"}</span><strong>{formatDate(selectedHistory.created_at, false, language)}</strong></div>
                </div>
              </div>

              <div className="history-modal-analysis">
                <section className="history-analysis-section">
                  <header><span>01</span><div><strong>{en ? "Conclusion" : "Kết luận"}</strong><small>{en ? "Why did I get this result?" : "Vì sao có kết quả này?"}</small></div></header>
                  <p>{selectedHistory.explanation || (en ? "No explanation was saved for this check." : "Không có giải thích được lưu cho lượt kiểm tra này.")}</p>
                </section>
                <section className="history-analysis-section">
                  <header><span>02</span><div><strong>{en ? "What should you do?" : "Bạn nên làm gì?"}</strong><small>{en ? "Safety guidance" : "Hướng dẫn an toàn"}</small></div></header>
                  <p>{selectedHistory.suggested_action || (en ? "No suggested action is available." : "Chưa có hành động đề xuất.")}</p>
                </section>
                <details className="history-ocr-section" open>
                  <summary><span>03</span><div><strong>{en ? "Content read by the system" : "Nội dung hệ thống đã đọc"}</strong><small>{en ? "Recognized text" : "Văn bản nhận diện được"}</small></div><b>⌄</b></summary>
                  <pre>{selectedHistory.extracted_text || (en ? "No text was recognized in the image." : "Không nhận diện được văn bản trong ảnh.")}</pre>
                </details>
              </div>
            </div>
          </section>
        </div>
      )}
    </>
  );
}
