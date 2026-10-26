import { useEffect, useState } from "react";

function ScanViewport({ imageSource, loading, result, mode, textPreview, documentName }) {
  const sourceReady = Boolean(imageSource || textPreview || documentName);
  const status = loading ? "SCANNING" : result ? "COMPLETE" : sourceReady ? "TARGET READY" : "STANDBY";
  const sourceLabels = { image: "AI VISION", text: "MESSAGE NLP", url: "URL INTELLIGENCE", pdf: "DOCUMENT OCR" };
  const annotations = result?.image_annotations || [];
  const dimensions = result?.image_dimensions;
  const canAnnotate = Boolean(imageSource && dimensions?.width && dimensions?.height);
  const markerUnit = canAnnotate ? Math.max(dimensions.width, dimensions.height) / 100 : 10;
  return (
    <div className={`scan-viewport ${loading ? "is-scanning" : ""} ${sourceReady ? "has-image" : ""} source-${mode}`}>
      {imageSource ? (
        canAnnotate ? (
          <svg
            className="scan-annotated-image"
            viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
            preserveAspectRatio="xMidYMid meet"
            role="img"
            aria-label={`Ảnh đã phân tích, phát hiện ${annotations.length} vùng cần chú ý`}
          >
            <image href={imageSource} width={dimensions.width} height={dimensions.height} />
            {annotations.map((region, index) => {
              const badgeX = Math.max(region.left, markerUnit * 1.35);
              const badgeY = Math.max(region.top, markerUnit * 1.35);
              return (
                <g className={`scan-image-annotation ${region.severity || "warning"}`} key={`${region.label}-${index}`}>
                  <rect x={region.left} y={region.top} width={region.width} height={region.height} rx={markerUnit * 0.45} />
                  <circle cx={badgeX} cy={badgeY} r={markerUnit * 1.15} />
                  <text x={badgeX} y={badgeY} fontSize={markerUnit * 1.25}>{index + 1}</text>
                  <title>{`${region.label}: ${region.reason}`}</title>
                </g>
              );
            })}
          </svg>
        ) : <img src={imageSource} alt="Ảnh đang chờ phân tích" />
      ) : sourceReady ? (
        <div className="scan-source-preview">
          <span className="scan-source-symbol">{mode === "pdf" ? "PDF" : mode === "url" ? "URL" : "TXT"}</span>
          <small>{sourceLabels[mode]}</small>
          <strong>{documentName || textPreview}</strong>
          <p>{mode === "pdf" ? "Tối đa 10 trang · OCR bản scan · tự động tìm QR" : "Nội dung đã khóa và sẵn sàng phân tích"}</p>
        </div>
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
            <strong>{sourceLabels[mode]}</strong>
            <small>Đang chờ dữ liệu đầu vào</small>
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
        <span className="scan-resolution">{sourceLabels[mode]} · SECURE INPUT</span>
      </div>
      <div className="scan-hud-bottom">
        <span>{mode === "url" ? "URL PARSER READY" : "OCR/NLP READY"}</span>
        <span>URL MODEL READY</span>
        <span>{mode === "image" ? "QR + VISUAL READY" : "RISK ENGINE READY"}</span>
      </div>
      {sourceReady && (
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
          <small>Trích xuất dữ liệu và đối chiếu tín hiệu lừa đảo...</small>
        </div>
      )}
      {!loading && annotations.length > 0 && (
        <div className="scan-annotation-count"><i /> Đã khoanh {annotations.length} vùng đáng chú ý trên ảnh</div>
      )}
    </div>
  );
}

function normalizeForMatch(value) {
  return value
    .toLocaleLowerCase("vi-VN")
    .replace(/đ/g, "d")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

function HighlightedContent({ text, terms = [], urls = [] }) {
  if (!text) return <span>Không nhận diện được văn bản trong nội dung này.</span>;

  const characters = Array.from(text);
  let normalizedText = "";
  const normalizedToOriginal = [];
  characters.forEach((character, originalIndex) => {
    const normalizedCharacter = normalizeForMatch(character);
    Array.from(normalizedCharacter).forEach((part) => {
      normalizedText += part;
      normalizedToOriginal.push(originalIndex);
    });
  });

  const candidates = [...terms, ...urls]
    .map((value) => String(value || "").trim())
    .filter((value) => value.length >= 2)
    .sort((left, right) => right.length - left.length);
  const ranges = [];
  candidates.forEach((candidate) => {
    const needle = normalizeForMatch(candidate);
    let position = normalizedText.indexOf(needle);
    while (needle && position >= 0) {
      const start = normalizedToOriginal[position];
      const end = normalizedToOriginal[position + needle.length - 1] + 1;
      if (!ranges.some((range) => start < range.end && end > range.start)) {
        ranges.push({ start, end });
      }
      position = normalizedText.indexOf(needle, position + needle.length);
    }
  });

  if (!ranges.length) return <span>{text}</span>;
  ranges.sort((left, right) => left.start - right.start);
  const output = [];
  let cursor = 0;
  ranges.forEach((range, index) => {
    if (range.start > cursor) output.push(characters.slice(cursor, range.start).join(""));
    output.push(<mark key={`${range.start}-${index}`}>{characters.slice(range.start, range.end).join("")}</mark>);
    cursor = range.end;
  });
  if (cursor < characters.length) output.push(characters.slice(cursor).join(""));
  return output;
}

function SafetyAssistant({ result, apiBase }) {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const quickQuestions = [
    "Vì sao bị cảnh báo?",
    "Tôi đã bấm link thì làm gì?",
    "Tôi nên làm gì tiếp theo?",
    "Kết quả này có chắc chắn không?",
  ];

  useEffect(() => {
    const opening = result.risk_level === "nguy_hiem"
      ? "Kết quả có nguy cơ cao. Tôi có thể giải thích lý do và hướng dẫn thầy xử lý an toàn."
      : result.risk_level === "nghi_ngo"
        ? "Kết quả còn điểm cần xác minh. Thầy có thể hỏi tôi vì sao hoặc nên làm gì tiếp theo."
        : "Chưa thấy tín hiệu mạnh, nhưng tôi vẫn có thể giúp thầy kiểm tra các bước an toàn.";
    setMessages([{ role: "assistant", text: opening }]);
    setQuestion("");
  }, [result]);

  async function askAssistant(value) {
    const nextQuestion = String(value || question).trim();
    if (!nextQuestion || asking) return;
    setMessages((current) => [...current, { role: "user", text: nextQuestion }]);
    setQuestion("");
    setAsking(true);
    try {
      const response = await fetch(`${apiBase}/analysis-assistant`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: nextQuestion,
          risk_level: result.risk_level || "nghi_ngo",
          risk_score: Number(result.risk_score) || 0,
          highlighted_terms: result.highlighted_terms || [],
          urls: result.phishvn_urls || [],
          suggested_action: result.suggested_action || "",
          verdict: result.analysis_breakdown?.verdict?.headline || result.explanation || "",
        }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "Không thể nhận câu trả lời");
      setMessages((current) => [...current, { role: "assistant", text: payload.answer }]);
    } catch (error) {
      setMessages((current) => [...current, {
        role: "assistant",
        text: "Trợ lý đang tạm gián đoạn. Thầy hãy dừng tương tác với nội dung đáng ngờ và xác minh qua kênh chính thức.",
      }]);
    } finally {
      setAsking(false);
    }
  }

  return (
    <section className="scan-safety-assistant" id="scan-ai-assistant">
      <header>
        <div className="assistant-orb"><i /><i /><i /></div>
        <div>
          <small>TRỢ LÝ AN TOÀN SAU KHI QUÉT</small>
          <h3>Hỏi để hiểu kết quả và xử lý đúng</h3>
          <p>Chỉ trả lời dựa trên kết quả vừa phân tích, không tự mở đường link.</p>
        </div>
        <span className="assistant-grounded-badge"><i /> Bám sát kết quả</span>
      </header>
      <div className="assistant-messages" aria-live="polite">
        {messages.map((message, index) => (
          <div className={`assistant-message ${message.role}`} key={`${message.role}-${index}`}>
            <span>{message.role === "assistant" ? "AI" : "Bạn"}</span>
            <p>{message.text}</p>
          </div>
        ))}
        {asking && <div className="assistant-message assistant thinking"><span>AI</span><p><i /><i /><i /></p></div>}
      </div>
      <div className="assistant-quick-questions">
        {quickQuestions.map((item) => <button type="button" onClick={() => askAssistant(item)} disabled={asking} key={item}>{item}</button>)}
      </div>
      <form className="assistant-input" onSubmit={(event) => { event.preventDefault(); askAssistant(); }}>
        <input value={question} onChange={(event) => setQuestion(event.target.value)} maxLength="500" placeholder="Ví dụ: Tôi đã nhập mật khẩu thì phải làm sao?" />
        <button disabled={asking || !question.trim()} aria-label="Gửi câu hỏi">→</button>
      </form>
    </section>
  );
}

function ResultConsole({ result, apiBase }) {
  const score = Math.min(100, Math.max(0, Number(result.risk_score) || 0));
  const levelLabels = {
    an_toan: "An toàn",
    nghi_ngo: "Nghi ngờ",
    nguy_hiem: "Nguy hiểm",
  };
  const level = levelLabels[result.risk_level] || result.risk_level;
  const sourceLabel = {
    image: "Ảnh / QR",
    text: "Tin nhắn",
    url: "URL trực tiếp",
    pdf: "Tài liệu PDF",
  }[result.source_type] || "Nội dung";
  const scamTypeLabel = {
    none: "Chưa xác định loại lừa đảo",
    phishing: "Giả mạo để lấy thông tin",
    phishing_url: "Đường link có dấu hiệu giả mạo",
    impersonation: "Mạo danh cơ quan hoặc tổ chức",
    fake_invoice: "Hóa đơn hoặc yêu cầu thanh toán giả",
    job_scam: "Lừa đảo tuyển dụng, việc làm",
    urgent_account_threat: "Đe dọa khóa hoặc trừ tiền tài khoản",
  }[result.scam_type] || "Nội dung cần kiểm tra thêm";
  const levelCopy = {
    an_toan: {
      title: "Chưa thấy dấu hiệu lừa đảo rõ ràng",
      body: "Hệ thống chưa tìm thấy tín hiệu mạnh. Bạn vẫn nên kiểm tra lại nếu nội dung liên quan đến tiền, mật khẩu hoặc thông tin cá nhân.",
      icon: "✓",
    },
    nghi_ngo: {
      title: "Nội dung này có một số điểm đáng ngờ",
      body: "Đừng làm theo ngay. Hãy tự liên hệ đơn vị được nhắc đến bằng số điện thoại hoặc website chính thức để xác minh.",
      icon: "!",
    },
    nguy_hiem: {
      title: "Cảnh báo: nguy cơ lừa đảo cao",
      body: "Không bấm đường link, không chuyển tiền và không cung cấp mật khẩu, mã OTP hay thông tin ngân hàng.",
      icon: "!",
    },
  }[result.risk_level] || {};
  const suspiciousUrls = (result.phishvn_urls || []).map((item) => item.url || item.normalized_url);
  const suspiciousCount = (result.highlighted_terms?.length || 0) + suspiciousUrls.length;
  const plainReasons = [];
  if (result.highlighted_terms?.length) {
    plainReasons.push(`Có từ ngữ thúc giục hoặc yêu cầu nhạy cảm: ${result.highlighted_terms.slice(0, 5).join(", ")}.`);
  }
  if (suspiciousUrls.length) {
    plainReasons.push(`Tìm thấy ${suspiciousUrls.length} đường link cần kiểm tra; đường link đáng chú ý nhất có điểm ${result.phishvn_url_risk_score || 0}/100.`);
  }
  if ((result.visual_risk_score || 0) >= 25) {
    plainReasons.push("Hình ảnh có đặc điểm trình bày cần thận trọng hoặc có thể đã qua chỉnh sửa.");
  }
  if (!plainReasons.length) plainReasons.push("Chưa tìm thấy từ ngữ, đường link hoặc dấu hiệu hình ảnh nổi bật.");
  const nextSteps = {
    nguy_hiem: ["Dừng nhắn tin và không bấm đường link.", "Không chuyển tiền, không gửi OTP, mật khẩu hay ảnh giấy tờ.", "Tự gọi tổng đài hoặc mở ứng dụng chính thức để xác minh."],
    nghi_ngo: ["Chưa thực hiện yêu cầu trong nội dung.", "Đối chiếu tên miền và số điện thoại bằng nguồn chính thức.", "Hỏi người thân hoặc đơn vị liên quan trước khi tiếp tục."],
    an_toan: ["Vẫn kiểm tra kỹ nếu nội dung liên quan đến tiền hoặc tài khoản.", "Không chia sẻ OTP và mật khẩu trong mọi trường hợp.", "Quét lại nếu nhận được nội dung hoặc đường link mới."],
  }[result.risk_level] || [];

  return (
    <section className="scan-result-console">
      <header className="scan-result-header">
        <div>
          <span className="scan-result-live"><i /> ĐÃ PHÂN TÍCH XONG</span>
          <h2>Kết quả kiểm tra</h2>
          <p>Giải thích ngắn gọn để mọi người đều có thể hiểu và xử lý an toàn.</p>
        </div>
        <div className="scan-result-score" style={{ "--scan-score": `${score * 3.6}deg` }}>
          <div><strong>{score}</strong><small>/100</small></div>
        </div>
      </header>

      <section className={`scan-plain-verdict ${result.risk_level}`}>
        <span>{levelCopy.icon || "i"}</span>
        <div>
          <small>KẾT LUẬN DỄ HIỂU</small>
          <h3>{levelCopy.title || level}</h3>
          <p>{levelCopy.body || result.explanation}</p>
        </div>
        <b>{suspiciousCount ? `${suspiciousCount} chi tiết cần chú ý` : "Chưa có chi tiết nổi bật"}</b>
      </section>

      <div className="scan-result-summary">
        <article>
          <span>Mức nguy cơ</span>
          <strong>{level}</strong>
          <small>ĐIỂM CẢNH BÁO {score}/100</small>
        </article>
        <article>
          <span>Nội dung đã kiểm tra</span>
          <strong>{sourceLabel}</strong>
          <small>{scamTypeLabel}</small>
        </article>
        <article>
          <span>Đường link tìm thấy</span>
          <strong>{result.phishvn_urls?.length || 0} đường link</strong>
          <small>{result.phishvn_url_risk_score ?? 0}/100 ĐIỂM ĐÁNG NGỜ</small>
        </article>
      </div>

      <div className="scan-simple-result-grid">
        <section className="scan-why-card">
          <div className="scan-friendly-heading"><span>01</span><div><small>LÝ DO CẢNH BÁO</small><h3>Vì sao có kết quả này?</h3></div></div>
          <ol>{plainReasons.map((reason, index) => <li key={reason}><b>{index + 1}</b><span>{reason}</span></li>)}</ol>
        </section>
        <section className="scan-next-steps-card">
          <div className="scan-friendly-heading"><span>02</span><div><small>HÀNH ĐỘNG AN TOÀN</small><h3>Thầy nên làm gì tiếp theo?</h3></div></div>
          <ol>{nextSteps.map((step, index) => <li key={step}><b>{index + 1}</b><span>{step}</span></li>)}</ol>
        </section>
      </div>

      <div className="scan-readable-content">
          <details className="scan-ocr-console" open>
            <summary>
              <span className="scan-section-index">03</span>
              <div>
                <small>NỘI DUNG HỆ THỐNG ĐÃ ĐỌC · {result.extracted_text?.trim() ? `${result.extracted_text.trim().length} KÝ TỰ` : "KHÔNG CÓ DỮ LIỆU"}</small>
                <strong>{result.source_type === "image" ? "Văn bản AI đọc được từ ảnh" : "Nội dung được đưa vào phân tích"}</strong>
              </div>
              <b>⌄</b>
            </summary>
            <div className="scan-highlighted-text">
              <HighlightedContent text={result.extracted_text} terms={result.highlighted_terms} urls={suspiciousUrls} />
            </div>
            {(result.highlighted_terms?.length > 0 || suspiciousUrls.length > 0) && (
              <p className="scan-highlight-note"><mark>Chữ nền vàng, in đậm</mark> là từ hoặc đường link hệ thống cho rằng cần chú ý.</p>
            )}
          </details>

          {result.qr_codes?.length > 0 && (
            <details className="scan-qr-console" open>
              <summary>
                <span className="scan-section-index">QR</span>
                <div><small>QR DECODE · {result.qr_codes.length} KẾT QUẢ</small><strong>Nội dung mã QR tìm thấy</strong></div>
                <b>⌄</b>
              </summary>
              <div>{result.qr_codes.map((value) => <code key={value}>{value}</code>)}</div>
            </details>
          )}

          {result.document_info && (
            <div className="scan-document-summary">
              <span>PDF</span>
              <div><strong>{result.document_info.processed_pages}/{result.document_info.page_count} trang đã đọc</strong><small>{result.document_info.truncated ? "Giới hạn xử lý 10 trang đầu" : "Đã xử lý toàn bộ tài liệu"}</small></div>
            </div>
          )}
      </div>

      <SafetyAssistant result={result} apiBase={apiBase} />

      <details className="scan-technical-panel">
        <summary><div><small>DÀNH CHO NGƯỜI MUỐN XEM KỸ</small><strong>Chi tiết phân tích kỹ thuật</strong></div><span>+</span></summary>
        <div className="scan-signal-column">
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
            <details className="scan-phishvn-console">
              <summary>
                <div><strong>Xem chi tiết đường link đáng ngờ</strong><small>Thông tin kỹ thuật: {result.phishvn_model}</small></div>
                <b>{result.phishvn_url_risk_score}/100</b>
              </summary>
              <div className="scan-phishvn-list">
                {result.phishvn_urls.map((item) => (
                  <article key={item.normalized_url}>
                    <div><strong>{item.url}</strong><span>{item.label === "phishing" ? "Nguy hiểm" : item.label === "suspicious" ? "Nghi ngờ" : "Cần kiểm tra"} · {(item.probability * 100).toFixed(1)}%</span></div>
                    <ul>{item.suspicious_signals.map((signal) => <li key={signal}>{signal}</li>)}</ul>
                  </article>
                ))}
              </div>
            </details>
          )}

          {result.analysis_breakdown && (
            <details className="scan-method-console">
              <summary>Xem cách tính điểm và giới hạn kỹ thuật <span>+</span></summary>
              <p>{result.analysis_breakdown.score_method}</p>
              <ul>{result.analysis_breakdown.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
            </details>
          )}
        </div>
      </details>
    </section>
  );
}

export default function ScanPage({
  scanMode,
  setScanMode,
  categories,
  selectedCategoryId,
  setSelectedCategoryId,
  onSubmit,
  onContentSubmit,
  imagePreview,
  onImageSelect,
  textInput,
  setTextInput,
  urlInput,
  setUrlInput,
  documentFile,
  handleDocumentSelect,
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
  const [assistantHintVisible, setAssistantHintVisible] = useState(false);
  const imageSource = imagePreview || (result?.image_url ? `${apiBase}${result.image_url}` : "");
  const textPreview = scanMode === "text"
    ? textInput.trim().slice(0, 180)
    : scanMode === "url" ? urlInput.trim().slice(0, 180) : "";
  const sourceReady = scanMode === "image"
    ? Boolean(imagePreview)
    : scanMode === "text"
      ? Boolean(textInput.trim())
      : scanMode === "url"
        ? Boolean(urlInput.trim())
        : Boolean(documentFile);
  const modes = [
    ["image", "Ảnh & QR", "▣"],
    ["text", "Tin nhắn", "Aa"],
    ["url", "URL", "⌁"],
    ["pdf", "PDF", "▤"],
  ];

  function openAssistant() {
    if (result) {
      setAssistantHintVisible(false);
      document.getElementById("scan-ai-assistant")?.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    setAssistantHintVisible(true);
  }

  return (
    <div className={`scan-experience ${loading ? "loading" : ""}`}>
      <section className="scan-command-banner">
        <div>
          <span className="scan-banner-live"><i /> AI DETECTION LAB ONLINE</span>
          <h2>Trung tâm kiểm định đa nguồn</h2>
          <p>Phân tích ảnh, QR, tin nhắn, URL và PDF trong cùng một quy trình AI đa tầng.</p>
        </div>
        <div className="scan-banner-engines" aria-label="Các công cụ phân tích đang sẵn sàng">
          <span><i /> OCR<strong>READY</strong></span>
          <span><i /> QR<strong>READY</strong></span>
          <span><i /> URL AI<strong>READY</strong></span>
        </div>
      </section>

      <div className="scan-workbench">
        <section className="scan-control-panel panel">
          <header className="scan-panel-heading">
            <div><span className="eyebrow">INPUT CONTROL</span><h3>Thiết lập lượt quét</h3></div>
            <span className="scan-private-badge">PRIVATE</span>
          </header>

          <div className="scan-source-tabs" role="tablist" aria-label="Chọn nguồn cần kiểm tra">
            {modes.map(([value, label, icon]) => (
              <button
                type="button"
                role="tab"
                aria-selected={scanMode === value}
                className={scanMode === value ? "active" : ""}
                key={value}
                onClick={() => setScanMode(value)}
              >
                <span>{icon}</span>{label}
              </button>
            ))}
          </div>

          <form onSubmit={scanMode === "image" ? onSubmit : onContentSubmit} className="scan-control-form">
            {scanMode === "image" && (
              <>
                <label className="scan-field-label" htmlFor="scan-category">Danh mục cần đối chiếu</label>
                <div className="scan-select-wrap">
                  <span>01</span>
                  <select id="scan-category" value={selectedCategoryId} onChange={(event) => setSelectedCategoryId(event.target.value)}>
                    {categories.length === 0 && <option value="">Đang tải...</option>}
                    {categories.map((category) => <option key={category.id} value={category.id}>{category.display_name}</option>)}
                  </select>
                </div>
              </>
            )}

            {scanMode === "image" && (
              <label className={`scan-upload-zone ${imagePreview ? "has-file" : ""}`}>
                <input type="file" accept="image/*" onChange={onImageSelect} />
                <span className="scan-upload-icon">
                  <svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 22V7m0 0-6 6m6-6 6 6M6 20v5h20v-5" /></svg>
                </span>
                <strong>{imagePreview ? "Ảnh đã được nạp · Chọn ảnh khác" : "Kéo ảnh vào hoặc nhấn để chọn"}</strong>
                <small>JPG · PNG · WEBP · TỰ ĐỘNG QUÉT QR</small>
                <div className="scan-upload-corners"><i /><i /><i /><i /></div>
              </label>
            )}

            {scanMode === "text" && (
              <label className="scan-direct-input">
                <span>Dán nội dung SMS, email hoặc đoạn chat</span>
                <textarea
                  value={textInput}
                  onChange={(event) => setTextInput(event.target.value)}
                  maxLength="20000"
                  rows="9"
                  placeholder="Ví dụ: Tài khoản của quý khách sẽ bị khóa. Truy cập đường dẫn sau để xác minh..."
                />
                <small>{textInput.length.toLocaleString("vi-VN")} / 20.000 ký tự</small>
              </label>
            )}

            {scanMode === "url" && (
              <label className="scan-direct-input scan-url-input">
                <span>Nhập URL hoặc tên miền cần kiểm tra</span>
                <div><b>URL</b><input value={urlInput} onChange={(event) => setUrlInput(event.target.value)} placeholder="https://example.com/xac-minh-tai-khoan" /></div>
                <small>Hệ thống chỉ phân tích cấu trúc URL, không tự mở liên kết.</small>
              </label>
            )}

            {scanMode === "pdf" && (
              <label className={`scan-upload-zone scan-pdf-zone ${documentFile ? "has-file" : ""}`}>
                <input type="file" accept="application/pdf,.pdf" onChange={handleDocumentSelect} />
                <span className="scan-upload-icon"><b>PDF</b></span>
                <strong>{documentFile ? documentFile.name : "Chọn hóa đơn hoặc giấy báo PDF"}</strong>
                <small>TỐI ĐA 15 MB · 10 TRANG · HỖ TRỢ PDF SCAN</small>
                <div className="scan-upload-corners"><i /><i /><i /><i /></div>
              </label>
            )}

            <div className="scan-input-actions">
              {scanMode === "image" ? (
                <button type="button" className="scan-camera-button" onClick={onOpenCamera}>
                  <span>◎</span> Chụp bằng camera
                </button>
              ) : <span className="scan-local-storage-note">✓ Kết quả lưu trên trình duyệt</span>}
              <button className="scan-launch-button" disabled={loading || !sourceReady}>
                {loading ? <><i /> Đang phân tích...</> : <>Phân tích ngay <span>→</span></>}
              </button>
            </div>
          </form>

          <div className="scan-module-list">
            <div><span>01</span><div><strong>Content Extractor</strong><small>OCR ảnh/PDF hoặc nội dung trực tiếp</small></div><i /></div>
            <div><span>02</span><div><strong>QR Decoder</strong><small>Tự động đọc QR trong ảnh và PDF</small></div><i /></div>
            <div><span>03</span><div><strong>PhishVN URL</strong><small>Đối chiếu URL và tên miền</small></div><i /></div>
            <div><span>04</span><div><strong>Risk Fusion</strong><small>Tổng hợp và giải thích cảnh báo</small></div><i /></div>
          </div>
        </section>

        <section className="scan-viewer-panel panel">
          <header className="scan-panel-heading">
            <div><span className="eyebrow">AI VISION VIEWPORT</span><h3>Màn hình kiểm định</h3></div>
            <span className={`scan-viewer-status ${loading ? "active" : ""}`}><i /> {loading ? "SCANNING" : result ? "COMPLETE" : "READY"}</span>
          </header>
          <ScanViewport imageSource={scanMode === "image" ? imageSource : ""} loading={loading} result={result} mode={scanMode} textPreview={textPreview} documentName={scanMode === "pdf" ? documentFile?.name : ""} />
          <div className="scan-telemetry">
            <div><span>INPUT</span><strong>{sourceReady ? `${scanMode.toUpperCase()} LOCKED` : "WAITING"}</strong></div>
            <div><span>ENGINE</span><strong>{loading ? "PROCESSING" : "STANDBY"}</strong></div>
            <div><span>OUTPUT</span><strong>{result ? `${result.risk_score}/100` : "--"}</strong></div>
          </div>
        </section>
      </div>

      {result && <ResultConsole result={result} apiBase={apiBase} />}

      <aside className={`scan-ai-launcher ${result ? "is-ready" : ""}`} aria-label="Mở trợ lý AI">
        {assistantHintVisible && !result && (
          <div className="scan-ai-launcher-hint">
            <button type="button" onClick={() => setAssistantHintVisible(false)} aria-label="Đóng hướng dẫn">×</button>
            <strong>Trợ lý AI sẽ mở sau khi quét</strong>
            <p>Thầy hãy nhập ảnh, tin nhắn, URL hoặc PDF rồi bấm <b>Phân tích ngay</b>.</p>
          </div>
        )}
        <button type="button" className="scan-ai-launcher-button" onClick={openAssistant}>
          <span className="scan-ai-launcher-orb"><i /><b>AI</b></span>
          <span><small>TRỢ LÝ AI</small><strong>{result ? "Hỏi về kết quả" : "Sẵn sàng sau khi quét"}</strong></span>
          {result && <em>1</em>}
        </button>
      </aside>

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
