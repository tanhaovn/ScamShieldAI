export default function HistoryPage({
  history,
  selectedHistory,
  setSelectedHistory,
  apiBase,
}) {
  return (
    <>
      <section className="panel page-view history-page">
        <h3>Lịch sử kiểm tra</h3>
        <ul className="list">
          {history.length === 0 && <li>Chưa có lịch sử</li>}
          {history.map((item) => (
            <li key={item.id} className="history-item">
              <span>{item.risk_level}</span>
              <strong>{item.risk_score}</strong>
              <small>
                {item.original_filename || `Category #${item.scam_category_id}`}
              </small>
              <button
                type="button"
                className="history-detail-button"
                onClick={() => setSelectedHistory(item)}
              >
                Xem chi tiết
              </button>
            </li>
          ))}
        </ul>
      </section>

      {selectedHistory && (
        <div
          className="modal-backdrop"
          role="presentation"
          onClick={() => setSelectedHistory(null)}
        >
          <section
            className="history-modal panel"
            role="dialog"
            aria-modal="true"
            aria-labelledby="history-detail-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <h3 id="history-detail-title">Chi tiết lần kiểm tra</h3>
              <button
                type="button"
                className="close-button"
                aria-label="Đóng chi tiết"
                onClick={() => setSelectedHistory(null)}
              >
                Đóng
              </button>
            </div>
            <div className="history-detail-grid">
              <div>
                <span className="detail-label">Tên file</span>
                <strong>
                  {selectedHistory.original_filename || "Không có"}
                </strong>
              </div>
              <div>
                <span className="detail-label">Mức độ</span>
                <strong>{selectedHistory.risk_level}</strong>
              </div>
              <div>
                <span className="detail-label">Điểm rủi ro</span>
                <strong>{selectedHistory.risk_score}</strong>
              </div>
              <div>
                <span className="detail-label">Thời gian</span>
                <strong>
                  {selectedHistory.created_at
                    ? new Date(selectedHistory.created_at).toLocaleString(
                        "vi-VN",
                      )
                    : "Không có"}
                </strong>
              </div>
            </div>
            {selectedHistory.image_url && (
              <img
                src={`${apiBase}${selectedHistory.image_url}`}
                alt={selectedHistory.original_filename || "Ảnh đã kiểm tra"}
                className="detail-image"
              />
            )}
            <div className="detail-copy">
              <p>
                <strong>OCR:</strong>{" "}
                {selectedHistory.extracted_text ||
                  "Không nhận diện được văn bản"}
              </p>
              <p>
                <strong>Giải thích:</strong>{" "}
                {selectedHistory.explanation || "Không có"}
              </p>
              <p>
                <strong>Hành động đề xuất:</strong>{" "}
                {selectedHistory.suggested_action || "Không có"}
              </p>
            </div>
          </section>
        </div>
      )}
    </>
  );
}
