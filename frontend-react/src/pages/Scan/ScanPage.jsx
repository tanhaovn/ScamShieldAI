function ScanViewport({ imageSource, loading, result }) {
  const status = loading ? "SCANNING" : result ? "COMPLETE" : imageSource ? "TARGET READY" : "STANDBY";
  return (
    <div className={`scan-viewport ${loading ? "is-scanning" : ""} ${imageSource ? "has-image" : ""}`}>
      {imageSource ? (
        <img src={imageSource} alt="Ảnh đang chờ phân tích" />
      ) : (
        <div className="scan-idle-core" aria-hidden="true">
          <div className="scan-idle-ring ring-one" />
          <div className="scan-idle-ring ring-two" />
          <div className="scan-idle-ring ring-three" />
          <div className="scan-idle-shield">
            <svg viewBox="0 0 48 48">
              <path d="M24 4 40 10v12c0 10.6-6.5 17.7-16 22-9.5-4.3-16-11.4-16-22V10z" />
              <path d="M16 25h5l3-8 4 14 3-6h4" />
            </svg>
            <strong>AI VISION</strong>
            <small>Đang chờ dữ liệu ảnh</small>
          </div>
        </div>
      )}

      <div className="scan-hud-grid" />
      <div className="scan-beam" />
      <span className="scan-lock lock-tl" />
      <span className="scan-lock lock-tr" />
      <span className="scan-lock lock-bl" />
      <span className="scan-lock lock-br" />
      <div className="scan-axis axis-x" />
      <div className="scan-axis axis-y" />

      <div className="scan-hud-top">
        <span className="scan-status"><i /> {status}</span>
        <span className="scan-resolution">VISION · 2048 PX</span>
      </div>
      <div className="scan-hud-bottom">
        <span>OCR READY</span>
        <span>URL MODEL READY</span>
        <span>VISUAL FORENSICS READY</span>
      </div>
      {imageSource && (
        <>
          <span className="scan-target target-one"><i /> TEXT</span>
          <span className="scan-target target-two"><i /> URL</span>
          <span className="scan-target target-three"><i /> META</span>
        </>
      )}
      {loading && (
        <div className="scan-progress-overlay">
          <strong>ĐANG PHÂN TÍCH</strong>
          <span><i /></span>
          <small>Trích xuất OCR và đối chiếu tín hiệu lừa đảo...</small>
        </div>
      )}
    </div>
  );
}

function ResultConsole({ result }) {
  const score = Math.min(100, Math.max(0, Number(result.risk_score) || 0));
  const levelLabels = {
    an_toan: "An toàn",
    nghi_ngo: "Nghi ngờ",
    nguy_hiem: "Nguy hiểm",
  };
  const level = levelLabels[result.risk_level] || result.risk_level;

  return (
    <section className="scan-result-console">
      <header className="scan-result-header">
        <div>
          <span className="scan-result-live"><i /> ANALYSIS COMPLETE</span>
          <h2>Kết quả kiểm định AI</h2>
          <p>Hệ thống đã tổng hợp tín hiệu văn bản, URL và dấu vết hình ảnh.</p>
        </div>
        <div className="scan-result-score" style={{ "--scan-score": `${score * 3.6}deg` }}>
          <div><strong>{score}</strong><small>/100</small></div>
        </div>
      </header>

      <div className="scan-result-summary">
        <article>
          <span>Mức đánh giá</span>
          <strong>{level}</strong>
          <small>RISK CLASSIFICATION</small>
        </article>
        <article>
          <span>Loại nội dung</span>
          <strong>{result.scam_type || `Category #${result.scam_category_id}`}</strong>
          <small>CONTENT CATEGORY</small>
        </article>
        <article>
          <span>PhishVN URL</span>
          <strong>{result.phishvn_url_risk_score ?? 0}/100</strong>
          <small>{result.phishvn_urls?.length || 0} URL ĐƯỢC KIỂM TRA</small>
        </article>
      </div>

      <div className="scan-result-layout">
        <div className="scan-verdict-column">
          <section className="scan-verdict-card">
            <span className="scan-section-index">01</span>
            <div>
              <small>KẾT LUẬN DỄ HIỂU</small>
              <h3>{result.analysis_breakdown?.verdict?.headline || result.explanation}</h3>
              {result.analysis_breakdown?.verdict?.reason && (
                <p>{result.analysis_breakdown.verdict.reason}</p>
              )}
            </div>
          </section>

          <section className="scan-action-card">
            <span className="scan-section-index">02</span>
            <div>
              <small>HÀNH ĐỘNG AN TOÀN</small>
              <p>{result.suggested_action || "Hãy xác minh lại thông tin trước khi tương tác."}</p>
            </div>
          </section>

          <details className="scan-ocr-console" open>
            <summary>
              <span className="scan-section-index">03</span>
              <div>
                <small>OCR OUTPUT · {result.extracted_text?.trim() ? `${result.extracted_text.trim().length} KÝ TỰ` : "KHÔNG CÓ DỮ LIỆU"}</small>
                <strong>Văn bản AI đọc được từ ảnh</strong>
              </div>
              <b>⌄</b>
            </summary>
            <pre>{result.extracted_text || "Không nhận diện được văn bản trong ảnh."}</pre>
          </details>
        </div>

        <div className="scan-signal-column">
          <div className="scan-signal-heading">
            <div><span>04</span><strong>Các tín hiệu đã phân tích</strong></div>
            <small>MULTI-SIGNAL ENGINE</small>
          </div>

          {result.analysis_breakdown?.components?.length > 0 ? (
            <div className="scan-component-grid">
              {result.analysis_breakdown.components.map((component) => (
                <article className={`scan-component-card ${component.status}`} key={component.key}>
                  <header>
                    <div><strong>{component.title}</strong><small>{component.status_label}</small></div>
                    <b>{component.score}</b>
                  </header>
                  <div className="scan-component-meter"><span style={{ width: `${Math.min(100, Math.max(0, Number(component.score) || 0))}%` }} /></div>
                  <p>{component.summary}</p>
                  <ul>{component.findings.map((finding) => <li key={finding}>{finding}</li>)}</ul>
                </article>
              ))}
            </div>
          ) : (
            <p className="scan-no-signals">Không có dữ liệu phân rã tín hiệu.</p>
          )}

          {result.phishvn_urls?.length > 0 && (
            <details className="scan-phishvn-console" open>
              <summary>
                <div><strong>PhishVN URL Intelligence</strong><small>{result.phishvn_model}</small></div>
                <b>{result.phishvn_url_risk_score}/100</b>
              </summary>
              <div className="scan-phishvn-list">
                {result.phishvn_urls.map((item) => (
                  <article key={item.normalized_url}>
                    <div><strong>{item.url}</strong><span>{item.label} · {(item.probability * 100).toFixed(1)}%</span></div>
                    <ul>{item.suspicious_signals.map((signal) => <li key={signal}>{signal}</li>)}</ul>
                  </article>
                ))}
              </div>
            </details>
          )}

          {result.analysis_breakdown && (
            <details className="scan-method-console">
              <summary>Cách tính điểm và giới hạn <span>+</span></summary>
              <p>{result.analysis_breakdown.score_method}</p>
              <ul>{result.analysis_breakdown.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
            </details>
          )}
        </div>
      </div>

      <footer className="scan-result-pipeline">
        <span className="done"><i /> IMAGE INPUT</span><b>→</b>
        <span className="done"><i /> OCR ENGINE</span><b>→</b>
        <span className="done"><i /> PHISHVN URL</span><b>→</b>
        <span className="done"><i /> VISUAL AI</span><b>→</b>
        <span className="done"><i /> RISK FUSION</span>
      </footer>
    </section>
  );
}

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
  const imageSource = imagePreview || (result?.image_url ? `${apiBase}${result.image_url}` : "");

  return (
    <div className={`scan-experience ${loading ? "loading" : ""}`}>
      <section className="scan-command-banner">
        <div>
          <span className="scan-banner-live"><i /> AI DETECTION LAB ONLINE</span>
          <h2>Phòng kiểm định hình ảnh</h2>
          <p>Quét OCR, URL lừa đảo và dấu hiệu chỉnh sửa trong một quy trình phân tích đa tầng.</p>
        </div>
        <div className="scan-banner-engines" aria-label="Các công cụ phân tích đang sẵn sàng">
          <span><i /> OCR<strong>READY</strong></span>
          <span><i /> URL AI<strong>READY</strong></span>
          <span><i /> VISUAL<strong>READY</strong></span>
        </div>
      </section>

      <div className="scan-workbench">
        <section className="scan-control-panel panel">
          <header className="scan-panel-heading">
            <div><span className="eyebrow">INPUT CONTROL</span><h3>Thiết lập lượt quét</h3></div>
            <span className="scan-private-badge">PRIVATE</span>
          </header>

          <form onSubmit={onSubmit} className="scan-control-form">
            <label className="scan-field-label" htmlFor="scan-category">Danh mục cần đối chiếu</label>
            <div className="scan-select-wrap">
              <span>01</span>
              <select id="scan-category" value={selectedCategoryId} onChange={(event) => setSelectedCategoryId(event.target.value)}>
                {categories.length === 0 && <option value="">Đang tải...</option>}
                {categories.map((category) => <option key={category.id} value={category.id}>{category.display_name}</option>)}
              </select>
            </div>

            <label className={`scan-upload-zone ${imagePreview ? "has-file" : ""}`}>
              <input type="file" accept="image/*" onChange={onImageSelect} />
              <span className="scan-upload-icon">
                <svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 22V7m0 0-6 6m6-6 6 6M6 20v5h20v-5" /></svg>
              </span>
              <strong>{imagePreview ? "Ảnh đã được nạp · Chọn ảnh khác" : "Kéo ảnh vào hoặc nhấn để chọn"}</strong>
              <small>JPG · PNG · WEBP</small>
              <div className="scan-upload-corners"><i /><i /><i /><i /></div>
            </label>

            <div className="scan-input-actions">
              <button type="button" className="scan-camera-button" onClick={onOpenCamera}>
                <span>◎</span> Chụp bằng camera
              </button>
              <button className="scan-launch-button" disabled={loading || !imagePreview}>
                {loading ? <><i /> Đang quét...</> : <>Khởi động AI Scan <span>→</span></>}
              </button>
            </div>
          </form>

          <div className="scan-module-list">
            <div><span>01</span><div><strong>OCR tiếng Việt</strong><small>Trích xuất văn bản có dấu</small></div><i /></div>
            <div><span>02</span><div><strong>PhishVN URL</strong><small>Đối chiếu URL và tên miền</small></div><i /></div>
            <div><span>03</span><div><strong>Visual Forensics</strong><small>EXIF, ELA và dấu hiệu chỉnh sửa</small></div><i /></div>
          </div>
        </section>

        <section className="scan-viewer-panel panel">
          <header className="scan-panel-heading">
            <div><span className="eyebrow">AI VISION VIEWPORT</span><h3>Màn hình kiểm định</h3></div>
            <span className={`scan-viewer-status ${loading ? "active" : ""}`}><i /> {loading ? "SCANNING" : result ? "COMPLETE" : "READY"}</span>
          </header>
          <ScanViewport imageSource={imageSource} loading={loading} result={result} />
          <div className="scan-telemetry">
            <div><span>INPUT</span><strong>{imageSource ? "IMAGE LOCKED" : "WAITING"}</strong></div>
            <div><span>ENGINE</span><strong>{loading ? "PROCESSING" : "STANDBY"}</strong></div>
            <div><span>OUTPUT</span><strong>{result ? `${result.risk_score}/100` : "--"}</strong></div>
          </div>
        </section>
      </div>

      {result && <ResultConsole result={result} />}

      {isCameraOpen && (
        <div className="camera-modal-backdrop scan-camera-backdrop">
          <section className="camera-modal scan-camera-modal" role="dialog" aria-modal="true" aria-labelledby="camera-title">
            <header className="scan-camera-header">
              <div><span className="scan-banner-live"><i /> LIVE CAMERA INPUT</span><h3 id="camera-title">Chụp ảnh kiểm tra</h3></div>
              <button type="button" onClick={onCloseCamera} aria-label="Đóng camera">×</button>
            </header>
            <div className="scan-camera-viewport">
              {cameraStream ? <video ref={videoRef} className="camera-video" autoPlay playsInline muted /> : <p className="camera-error">{cameraError}</p>}
              {cameraStream && <><div className="scan-hud-grid" /><div className="scan-beam" /><span className="scan-lock lock-tl" /><span className="scan-lock lock-tr" /><span className="scan-lock lock-bl" /><span className="scan-lock lock-br" /></>}
            </div>
            {cameraStream && cameraError && <p className="camera-error">{cameraError}</p>}
            <div className="camera-actions">
              <button type="button" onClick={onCapturePhoto} disabled={!cameraStream}>Chụp và sử dụng ảnh</button>
              <button type="button" className="ghost" onClick={onCloseCamera}>Hủy</button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
