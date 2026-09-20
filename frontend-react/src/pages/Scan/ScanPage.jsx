export default function ScanPage({
  categories,
  selectedCategoryId,
  setSelectedCategoryId,
  onSubmit,
  imagePreview,
  onImageSelect,
  onOpenCamera,
  loading,
  isCameraOpen,
  cameraStream,
  cameraError,
  videoRef,
  onCapturePhoto,
  onCloseCamera,
  result,
  apiBase,
}) {
  return (
    <div className="grid page-view">
      <section className="panel">
        <div className="workspace-heading">
          <div>
            <span className="eyebrow">IMAGE CHECK</span>
            <h2>Kiểm tra một hình ảnh</h2>
            <p>
              Upload ảnh hóa đơn, tin nhắn hoặc link đáng ngờ để bắt đầu phân
              tích.
            </p>
          </div>
          <span className="privacy-badge">PRIVATE ANALYSIS</span>
        </div>
        <form onSubmit={onSubmit} className="scan-form">
          <label className="label">Danh mục scam</label>
          <select
            value={selectedCategoryId}
            onChange={(event) => setSelectedCategoryId(event.target.value)}
          >
            {categories.length === 0 && <option value="">Đang tải...</option>}
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.display_name}
              </option>
            ))}
          </select>
          <label className="dropzone">
            <input type="file" accept="image/*" onChange={onImageSelect} />
            <span className="dropzone-icon">+</span>
            <strong>
              {imagePreview ? "Đổi hình ảnh" : "Kéo ảnh vào đây hoặc chọn file"}
            </strong>
            <small>JPG, PNG hoặc WEBP · tối đa theo cấu hình hệ thống</small>
          </label>
          <button
            type="button"
            className="camera-button"
            onClick={onOpenCamera}
          >
            Chụp ảnh bằng camera
          </button>
          {imagePreview && (
            <img src={imagePreview} alt="Preview" className="preview" />
          )}
          <button className="scan-submit" disabled={loading}>
            {loading ? "Đang phân tích..." : "Kiểm tra"}
          </button>
        </form>

        {isCameraOpen && (
          <div className="camera-modal-backdrop">
            <section
              className="camera-modal"
              role="dialog"
              aria-modal="true"
              aria-labelledby="camera-title"
            >
              <div className="modal-header">
                <h3 id="camera-title">Chụp ảnh</h3>
                <button
                  type="button"
                  className="close-button"
                  onClick={onCloseCamera}
                >
                  Đóng
                </button>
              </div>
              {cameraStream ? (
                <video
                  ref={videoRef}
                  className="camera-video"
                  autoPlay
                  playsInline
                  muted
                />
              ) : (
                <p className="camera-error">{cameraError}</p>
              )}
              {cameraStream && cameraError && (
                <p className="camera-error">{cameraError}</p>
              )}
              <div className="camera-actions">
                <button
                  type="button"
                  onClick={onCapturePhoto}
                  disabled={!cameraStream}
                >
                  Chụp ảnh
                </button>
                <button type="button" className="ghost" onClick={onCloseCamera}>
                  Hủy
                </button>
              </div>
            </section>
          </div>
        )}
      </section>

      <section className="panel visual-preview-panel">
        <div className="preview-heading">
          <div>
            <span className="eyebrow">VISUAL PREVIEW</span>
            <h3>Ảnh đang được kiểm tra</h3>
          </div>
          <span className="preview-status">{result ? "DONE" : "READY"}</span>
        </div>
        <div className="visual-preview">
          {imagePreview || result?.image_url ? (
            <img
              src={imagePreview || `${apiBase}${result.image_url}`}
              alt="Ảnh đang phân tích"
            />
          ) : (
            <>
              <div className="preview-grid-lines" />
              <div className="preview-orbit preview-orbit-one" />
              <div className="preview-orbit preview-orbit-two" />
              <div className="preview-focus">
                <span>SCAN</span>
                <b>+</b>
              </div>
              <span className="preview-tag preview-tag-ocr">OCR</span>
              <span className="preview-tag preview-tag-risk">RISK</span>
            </>
          )}
        </div>
        <div className="preview-caption">
          <strong>
            {result ? "Phân tích đã hoàn tất" : "Chưa có ảnh được chọn"}
          </strong>
          <span>
            {result
              ? `Risk score ${result.risk_score} · ${result.risk_level}`
              : "Upload ảnh để xem preview và bắt đầu phân tích."}
          </span>
        </div>
        {result && (
          <div className="side-analysis-result">
            <div className="side-analysis-topline">
              <span>ANALYSIS RESULT</span>
              <strong>{result.risk_score}/100</strong>
            </div>
            <div className="side-risk-meter">
              <span
                style={{
                  width: `${Math.min(100, Math.max(0, Number(result.risk_score) || 0))}%`,
                }}
              />
            </div>
            <div className="side-analysis-grid">
              <div>
                <small>Mức độ</small>
                <b>{result.risk_level}</b>
              </div>
              <div>
                <small>Loại scam</small>
                <b>{result.scam_type || result.scam_category_id}</b>
              </div>
            </div>
            <div className="side-analysis-copy">
              <strong>Giải thích</strong>
              <p>{result.explanation}</p>
              <strong>Hành động đề xuất</strong>
              <p>{result.suggested_action}</p>
            </div>
            <details className="side-ocr">
              <summary>Văn bản nhận diện từ ảnh (OCR)</summary>
              <pre>
                {result.extracted_text ||
                  "Không nhận diện được văn bản trong ảnh."}
              </pre>
            </details>
          </div>
        )}
      </section>
    </div>
  );
}
