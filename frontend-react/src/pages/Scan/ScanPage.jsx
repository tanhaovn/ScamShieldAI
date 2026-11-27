import { useEffect, useState } from "react";
import { exportScanReport } from "../../utils/reportExport";

function ScanViewport({ imageSource, loading, result, mode, textPreview, documentName, language }) {
  const en = language === "en";
  const sourceReady = Boolean(imageSource || textPreview || documentName);
  const status = loading ? (en ? "Analyzing" : "Đang phân tích") : result ? (en ? "Completed" : "Đã hoàn tất") : sourceReady ? (en ? "Ready to check" : "Sẵn sàng kiểm tra") : (en ? "Waiting for content" : "Chờ nội dung");
  const sourceLabels = en ? { image: "Image & QR", text: "Message", url: "Link", pdf: "PDF document" } : { image: "Ảnh & QR", text: "Tin nhắn", url: "Đường link", pdf: "Tài liệu PDF" };
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
            aria-label={en ? `Analyzed image with ${annotations.length} areas to review` : `Ảnh đã phân tích, phát hiện ${annotations.length} vùng cần chú ý`}
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
        ) : <img src={imageSource} alt={en ? "Image awaiting analysis" : "Ảnh đang chờ phân tích"} />
      ) : sourceReady ? (
        <div className="scan-source-preview">
          <span className="scan-source-symbol">{mode === "pdf" ? "PDF" : mode === "url" ? "URL" : "TXT"}</span>
          <small>{sourceLabels[mode]}</small>
          <strong>{documentName || textPreview}</strong>
          <p>{mode === "pdf" ? (en ? "Up to 10 pages · scanned OCR · automatic QR detection" : "Tối đa 10 trang · OCR bản scan · tự động tìm QR") : (en ? "Content secured and ready for analysis" : "Nội dung đã khóa và sẵn sàng phân tích")}</p>
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
            <small>{en ? "Waiting for input" : "Đang chờ dữ liệu đầu vào"}</small>
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
        <span className="scan-resolution">{sourceLabels[mode]}</span>
      </div>
      {loading && (
        <div className="scan-progress-overlay">
          <strong>{en ? "ANALYZING" : "ĐANG PHÂN TÍCH"}</strong>
          <span><i /></span>
          <small>{en ? "Extracting data and checking scam signals..." : "Trích xuất dữ liệu và đối chiếu tín hiệu lừa đảo..."}</small>
        </div>
      )}
      {!loading && annotations.length > 0 && (
        <div className="scan-annotation-count"><i /> {en ? `${annotations.length} notable areas marked on the image` : `Đã khoanh ${annotations.length} vùng đáng chú ý trên ảnh`}</div>
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

function HighlightedContent({ text, terms = [], urls = [], language }) {
  if (!text) return <span>{language === "en" ? "No text could be recognized in this content." : "Không nhận diện được văn bản trong nội dung này."}</span>;

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

function AiExplanationAssistant({ result, apiBase, language, evidence }) {
  const en = language === "en";
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  async function askGemini(value) {
    const nextQuestion = String(value || question).trim();
    if (!nextQuestion || loading) return;
    setMessages((current) => [...current, { role: "user", text: nextQuestion }]);
    setQuestion("");
    setLoading(true);
    try {
      const response = await fetch(`${apiBase}/explain-result`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: nextQuestion,
          language,
          risk_score: Math.min(100, Math.max(0, Number(result.risk_score) || 0)),
          risk_level: result.risk_level || "unknown",
          source_type: result.source_type || "unknown",
          explanation: String(result.explanation || "").slice(0, 8000),
          extracted_text: String(result.extracted_text || "").slice(0, 6000),
          evidence: (evidence || []).slice(0, 8).map((item) => ({
            observation: String(item.observation || "").slice(0, 1000),
            why_risky: String(item.why_risky || "").slice(0, 2000),
          })),
        }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || (en ? "Gemini is unavailable right now." : "Gemini hiện chưa sẵn sàng."));
      setMessages((current) => [...current, { role: "assistant", text: payload.answer, model: payload.model }]);
    } catch (error) {
      setMessages((current) => [...current, { role: "error", text: error.message }]);
    } finally {
      setLoading(false);
    }
  }

  const quickQuestion = en ? "Why was this content flagged?" : "Tại sao nội dung này bị đánh dấu?";
  return <>
    <button type="button" className="scan-ai-ask-trigger" onClick={() => setOpen(true)}><span className="scan-ai-trigger-icon">AI</span>{en ? "Ask" : "Hỏi"}</button>
    {open && <div className="scan-ai-dialog-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setOpen(false); }}>
      <section className="scan-ai-assistant" role="dialog" aria-modal="true" aria-label={en ? "AI explanation assistant" : "Trợ lý AI giải thích kết quả"}>
        <header>
          <span className="scan-ai-avatar" aria-hidden="true"><i /><b>AI</b></span>
          <div><small>{en ? "AI EXPLANATION ASSISTANT" : "TRỢ LÝ AI GIẢI THÍCH"}</small><strong>{en ? "Ask why this result was produced" : "Hỏi thêm vì sao có kết quả này"}</strong></div>
          <span className="scan-ai-online"><i />{en ? "Ready" : "Sẵn sàng"}</span>
          <button type="button" className="scan-ai-dialog-close" onClick={() => setOpen(false)} aria-label={en ? "Close" : "Đóng"}>×</button>
        </header>
        <div className="scan-ai-chat">
          <div className="scan-ai-message assistant"><span className="scan-ai-avatar mini" aria-hidden="true"><b>AI</b></span><p>{en ? "I can explain the evidence above in simpler terms. What would you like to understand?" : "Mình có thể giải thích các bằng chứng phía trên theo cách dễ hiểu hơn. Bạn muốn hỏi điều gì?"}</p></div>
          {!messages.length && <button type="button" className="scan-ai-quick-question" onClick={() => askGemini(quickQuestion)}>{quickQuestion}</button>}
          {messages.map((message, index) => <div className={`scan-ai-message ${message.role}`} key={`${message.role}-${index}`}><span>{message.role === "user" ? (en ? "You" : "Bạn") : message.role === "error" ? "!" : "AI"}</span><p>{message.text}</p>{message.model && <small>{message.model}</small>}</div>)}
          {loading && <div className="scan-ai-message assistant loading"><span className="scan-ai-avatar mini"><b>AI</b></span><p>{en ? "AI is reviewing the evidence" : "AI đang xem lại các bằng chứng"}<i /><i /><i /></p></div>}
        </div>
        <form onSubmit={(event) => { event.preventDefault(); askGemini(); }}>
          <input value={question} onChange={(event) => setQuestion(event.target.value)} maxLength={600} autoFocus placeholder={en ? "Ask a follow-up question..." : "Hỏi thêm về kết quả này..."} />
          <button type="submit" disabled={!question.trim() || loading}>{en ? "Ask" : "Hỏi"}<span>→</span></button>
        </form>
        <p className="scan-ai-disclaimer">{en ? "The current result and extracted text are sent to the AI only when you ask. AI answers may be inaccurate." : "Kết quả hiện tại và văn bản trích xuất chỉ được gửi tới AI khi bạn đặt câu hỏi. Câu trả lời AI có thể chưa hoàn toàn chính xác."}</p>
      </section>
    </div>}
  </>;
}

function ResultFeedback({ result, apiBase, language }) {
  const en = language === "en";
  const [choice, setChoice] = useState("");
  const [note, setNote] = useState("");
  const [status, setStatus] = useState("idle");
  const options = [
    ["correct", en ? "Result is correct" : "Kết quả đúng", en ? "The warning matches this content" : "Cảnh báo phù hợp với nội dung", "✓"],
    ["false_alarm", en ? "False warning" : "Cảnh báo sai", en ? "Safe content was flagged" : "Nội dung an toàn nhưng bị cảnh báo", "!"],
    ["missed_scam", en ? "Missed a scam" : "Bỏ sót lừa đảo", en ? "The result should be more severe" : "Kết quả chưa cảnh báo đúng mức", "+"],
  ];

  async function submitFeedback() {
    if (!choice || status === "sending") return;
    setStatus("sending");
    try {
      const response = await fetch(`${apiBase}/scan-feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scan_id: result.scan_id || null,
          client_scan_id: String(result.id || ""),
          verdict: choice,
          predicted_level: result.risk_level,
          risk_score: Number(result.risk_score) || 0,
          source_type: result.source_type || "unknown",
          original_filename: result.original_filename || null,
          note: note.trim() || null,
          highlighted_terms: result.highlighted_terms || [],
          urls: (result.phishvn_urls || []).map((item) => item.url || item.normalized_url).filter(Boolean),
        }),
      });
      if (!response.ok) throw new Error("feedback_failed");
      setStatus("sent");
    } catch {
      setStatus("error");
    }
  }

  if (status === "sent") return <section className="scan-feedback-card is-sent"><span>✓</span><div><strong>{en ? "Thank you for validating this result" : "Cảm ơn bạn đã xác nhận kết quả"}</strong><p>{en ? "The feedback is queued for expert review and model evaluation." : "Phản hồi đã được đưa vào hàng chờ để kiểm định và đánh giá mô hình."}</p></div></section>;
  return (
    <section className="scan-feedback-card">
      <header><div><small>{en ? "HUMAN VALIDATION" : "XÁC NHẬN TỪ NGƯỜI DÙNG"}</small><h3>{en ? "Was this result accurate?" : "Kết quả này có chính xác không?"}</h3></div><span><i />{en ? "Helps improve detection" : "Giúp cải thiện hệ thống"}</span></header>
      <div className="scan-feedback-options">{options.map(([value, label, description, icon]) => <button type="button" aria-pressed={choice === value} className={`feedback-${value} ${choice === value ? "active" : ""}`} onClick={() => { setChoice(value); setStatus("idle"); }} key={value}><b>{icon}</b><span><strong>{label}</strong><small>{description}</small></span></button>)}</div>
      {choice && <div className="scan-feedback-detail"><textarea value={note} onChange={(event) => setNote(event.target.value)} maxLength={1000} placeholder={en ? "Optional: tell us what was right or wrong" : "Không bắt buộc: cho biết điểm nào đúng hoặc chưa đúng"} /><button type="button" onClick={submitFeedback} disabled={status === "sending"}>{status === "sending" ? (en ? "Sending..." : "Đang gửi...") : (en ? "Submit feedback" : "Gửi phản hồi")}</button></div>}
      {status === "error" && <p className="scan-feedback-error">{en ? "Could not save feedback. Please try again." : "Chưa lưu được phản hồi. Vui lòng thử lại."}</p>}
    </section>
  );
}

function ResultConsole({ result, apiBase, language }) {
  const en = language === "en";
  const score = Math.min(100, Math.max(0, Number(result.risk_score) || 0));
  const levelLabels = en ? { an_toan: "Safe", nghi_ngo: "Suspicious", nguy_hiem: "Dangerous" } : { an_toan: "An toàn", nghi_ngo: "Nghi ngờ", nguy_hiem: "Nguy hiểm" };
  const level = levelLabels[result.risk_level] || result.risk_level;
  const levelCopy = (en ? {
    an_toan: {
      title: "Low scam risk",
      icon: "✓",
    },
    nghi_ngo: {
      title: "Suspicious content",
      icon: "!",
    },
    nguy_hiem: {
      title: "High scam risk",
      icon: "!",
    },
  } : {
    an_toan: {
      title: "Nguy cơ lừa đảo thấp",
      icon: "✓",
    },
    nghi_ngo: {
      title: "Nội dung đáng nghi",
      icon: "!",
    },
    nguy_hiem: {
      title: "Nguy cơ lừa đảo cao",
      icon: "!",
    },
  })[result.risk_level] || {};
  const suspiciousUrls = (result.phishvn_urls || []).map((item) => item.url || item.normalized_url);
  const hasGradcamPayload = Object.prototype.hasOwnProperty.call(result, "image_model_gradcam");
  const gradcam = result.image_model_gradcam || {};
  const gradcamTarget = gradcam.target_class || result.image_model_label || "unavailable";
  const gradcamTargetScore = Math.min(100, Math.max(0, Number(gradcam.target_score) || 0));
  const gradcamTargetLabel = gradcamTarget === "phishing"
    ? (en ? "Phishing" : "Phishing / giả mạo")
    : gradcamTarget === "legitimate"
      ? (en ? "Legitimate" : "Hợp lệ")
      : (en ? "Unavailable" : "Chưa có kết quả");
  const vlm = result.vlm_analysis || {};
  const aiExplanationItems = Array.isArray(vlm.explanation_items) ? vlm.explanation_items : [];
  const hasAiExplanation = vlm.explanation_source === "vision_language_model"
    && aiExplanationItems.length > 0;
  return (
    <section className="scan-result-console">
      <header className="scan-result-header">
        <div className="scan-result-heading">
          <span className="scan-result-live"><i /> {en ? "ANALYSIS COMPLETE" : "ĐÃ PHÂN TÍCH XONG"}</span>
          <h2>{en ? "Check result" : "Kết quả kiểm tra"}</h2>
          <p>{en ? "A clear explanation to help you understand and respond safely." : "Giải thích ngắn gọn để mọi người đều có thể hiểu và xử lý an toàn."}</p>
          <span className={`scan-level-badge ${result.risk_level}`}>{en ? "Risk level" : "Mức độ"}: <strong>{level}</strong></span>
        </div>
        <div className="scan-result-header-actions">
          <button type="button" className="scan-report-button" onClick={() => exportScanReport(result, language)}>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v11m0 0 4-4m-4 4-4-4M5 17v3h14v-3" /></svg>
            <span>{en ? "Export PDF" : "Xuất báo cáo PDF"}</span>
          </button>
          <div className="scan-result-score" style={{ "--scan-score": `${score * 3.6}deg` }} aria-label={en ? `Risk score ${score} out of 100` : `Điểm rủi ro ${score} trên 100`}>
            <div><small>{en ? "RISK" : "RỦI RO"}</small><span><strong>{score}</strong><small>/100</small></span></div>
          </div>
        </div>
      </header>

      <section className={`scan-plain-verdict ${result.risk_level}`}>
        <span>{levelCopy.icon || "i"}</span>
        <h3>{levelCopy.title || level}</h3>
      </section>

      {result.source_type === "image" && (
        <section className={`scan-gradcam-card ${gradcam.available ? "available" : "unavailable"}`}>
          <header>
            <div>
              <small>PYTORCH GRAD-CAM · RESNET18</small>
              <h3>{en ? "Why did the image model make this prediction?" : "Vì sao mô hình ảnh đưa ra dự đoán này?"}</h3>
            </div>
            <span>{gradcamTargetLabel} · {gradcamTargetScore}%</span>
          </header>

          {gradcam.available && gradcam.image_url ? (
            <>
              <div className="scan-gradcam-comparison">
                {result.image_url && (
                  <figure>
                    <img src={`${apiBase}${result.image_url}`} alt={en ? "The image submitted for this check" : "Ảnh được gửi trong lần kiểm tra này"} />
                    <figcaption>{en ? "Image submitted for this check" : "Ảnh gốc của lần kiểm tra này"}</figcaption>
                  </figure>
                )}
                <figure>
                  <img src={`${apiBase}${gradcam.image_url}`} alt={en ? `Grad-CAM map for the ${gradcamTarget} prediction` : `Bản đồ Grad-CAM cho dự đoán ${gradcamTargetLabel}`} />
                  <figcaption>{en ? `Grad-CAM for class: ${gradcamTargetLabel}` : `Grad-CAM giải thích lớp: ${gradcamTargetLabel}`}</figcaption>
                </figure>
              </div>
              <div className="scan-gradcam-legend" aria-label={en ? "Grad-CAM color scale" : "Thang màu Grad-CAM"}>
                <span>{en ? "Lower contribution" : "Ít tác động"}</span><i /><span>{en ? "Higher contribution" : "Tác động mạnh"}</span>
              </div>
              <div className="scan-gradcam-explanation">
                <div className="scan-explanation-title-row">
                  <h4>{en ? "Explanation" : "Giải thích"}</h4>
                  <AiExplanationAssistant key={result.id || result.created_at || result.scan_id || "result"} result={result} apiBase={apiBase} language={language} evidence={aiExplanationItems} />
                </div>
                {hasAiExplanation ? (
                  <ol className="scan-ai-evidence-list">
                    {aiExplanationItems.map((item, index) => (
                      <li key={`${item.observation}-${index}`}>
                        <strong>{item.observation}</strong>
                        <p>{item.why_risky}</p>
                      </li>
                    ))}
                  </ol>
                ) : (
                  <div className="scan-ai-explanation-unavailable">
                    <strong>{en ? "A visual-language explanation is not available" : "Chưa có lời giải thích từ AI thị giác"}</strong>
                    <p>{vlm.note || (en
                      ? "Grad-CAM can localize influential pixels, but it cannot explain their semantic meaning by itself."
                      : "Grad-CAM chỉ định vị vùng tác động, tự nó không hiểu ý nghĩa và không thể nói vì sao nội dung đó là lừa đảo.")}</p>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="scan-gradcam-unavailable">
              <strong>{en ? "No Grad-CAM map is available for this check" : "Chưa tạo được bản đồ Grad-CAM cho lần kiểm tra này"}</strong>
              <p>{gradcam.note || (!hasGradcamPayload
                ? (en
                  ? "This result came from an older backend response. Restart the backend, then scan the image again."
                  : "Kết quả này được trả từ backend phiên bản cũ. Hãy khởi động lại backend rồi quét lại ảnh.")
                : (en
                  ? "The ResNet18 image model or Grad-CAM dependency was unavailable."
                  : "Model ResNet18 hoặc thư viện Grad-CAM chưa sẵn sàng."))}</p>
            </div>
          )}
        </section>
      )}

      <div className="scan-readable-content">
          <details className="scan-ocr-console" open>
            <summary>
              <span className="scan-section-index">03</span>
              <div>
                <small>{en ? "CONTENT READ BY THE SYSTEM" : "NỘI DUNG HỆ THỐNG ĐÃ ĐỌC"} · {result.extracted_text?.trim() ? `${result.extracted_text.trim().length} ${en ? "CHARACTERS" : "KÝ TỰ"}` : (en ? "NO DATA" : "KHÔNG CÓ DỮ LIỆU")}</small>
                <strong>{result.source_type === "image" ? (en ? "Text read from the image" : "Văn bản AI đọc được từ ảnh") : (en ? "Content submitted for analysis" : "Nội dung được đưa vào phân tích")}</strong>
              </div>
              <b>⌄</b>
            </summary>
            <div className="scan-highlighted-text">
              <HighlightedContent text={result.extracted_text} terms={result.highlighted_terms} urls={suspiciousUrls} language={language} />
            </div>
            {(result.highlighted_terms?.length > 0 || suspiciousUrls.length > 0) && (
              <p className="scan-highlight-note"><mark>{en ? "Bold yellow highlights" : "Chữ nền vàng, in đậm"}</mark> {en ? "mark words or links that need attention." : "là từ hoặc đường link hệ thống cho rằng cần chú ý."}</p>
            )}
          </details>

          {result.qr_codes?.length > 0 && (
            <details className="scan-qr-console" open>
              <summary>
                <span className="scan-section-index">QR</span>
                <div><small>QR DECODE · {result.qr_codes.length} {en ? "RESULTS" : "KẾT QUẢ"}</small><strong>{en ? "QR code content found" : "Nội dung mã QR tìm thấy"}</strong></div>
                <b>⌄</b>
              </summary>
              <div>{result.qr_codes.map((value) => <code key={value}>{value}</code>)}</div>
            </details>
          )}

          {result.document_info && (
            <div className="scan-document-summary">
              <span>PDF</span>
              <div><strong>{result.document_info.processed_pages}/{result.document_info.page_count} {en ? "pages read" : "trang đã đọc"}</strong><small>{result.document_info.truncated ? (en ? "Limited to the first 10 pages" : "Giới hạn xử lý 10 trang đầu") : (en ? "Entire document processed" : "Đã xử lý toàn bộ tài liệu")}</small></div>
            </div>
          )}
      </div>

      <ResultFeedback result={result} apiBase={apiBase} language={language} />

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
  batchInput,
  setBatchInput,
  batchResults,
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
  backendStatus,
  language = "vi",
}) {
  const en = language === "en";
  const imageSource = imagePreview || (result?.image_url ? `${apiBase}${result.image_url}` : "");
  const textPreview = scanMode === "text"
    ? textInput.trim().slice(0, 180)
    : scanMode === "url" ? urlInput.trim().slice(0, 180) : scanMode === "batch" ? batchInput.trim().slice(0, 180) : "";
  const sourceReady = scanMode === "image"
    ? Boolean(imagePreview)
    : scanMode === "text"
      ? Boolean(textInput.trim())
      : scanMode === "url"
        ? Boolean(urlInput.trim())
        : scanMode === "batch" ? Boolean(batchInput.trim()) : Boolean(documentFile);
  const modes = [
    ["image", en ? "Image & QR" : "Ảnh & QR", "▣"],
    ["text", en ? "Message" : "Tin nhắn", "Aa"],
    ["url", en ? "Link" : "Đường link", "⌁"],
    ["pdf", en ? "Document" : "Tài liệu", "▤"],
    ["batch", en ? "Batch" : "Hàng loạt", "≣"],
  ];

  return (
    <div className={`scan-experience ${loading ? "loading" : ""} ${result ? "has-result" : ""} ${sourceReady ? "has-source" : ""}`}>
      <section className="scan-command-banner">
        <div>
          <span className="scan-banner-live"><i /> {en ? "SAFETY CHECK" : "KIỂM TRA AN TOÀN"}</span>
          <h2>{en ? "Submit suspicious content for review" : "Gửi nội dung đáng ngờ để kiểm tra"}</h2>
          <p>{en ? "Choose a content type below. You will receive a clear result and safe next-step guidance." : "Chọn loại nội dung bên dưới. Bạn sẽ nhận được kết quả dễ hiểu và hướng dẫn xử lý an toàn."}</p>
        </div>
      </section>

      {["offline", "waking"].includes(backendStatus?.state) && (
        <div className="backend-offline-banner" role="alert">
          <span>!</span>
          <div><strong>{en ? "The scanner is waking up" : "Máy chủ phân tích đang khởi động"}</strong><small>{en ? "You can still press Analyze now. The first check may take up to a minute." : "Bạn vẫn có thể bấm Phân tích ngay. Lượt đầu tiên có thể cần chờ khoảng một phút."}</small></div>
        </div>
      )}

      <div className="scan-workbench">
        <section className="scan-control-panel panel">
          <header className="scan-panel-heading">
            <div><span className="eyebrow">{en ? "CONTENT TO CHECK" : "NỘI DUNG CẦN KIỂM TRA"}</span><h3>{en ? "Choose what you received" : "Chọn loại nội dung bạn nhận được"}</h3></div>
            <span className="scan-private-badge">🔒 {en ? "PROTECTED" : "ĐƯỢC BẢO VỆ"}</span>
          </header>

          <div className="scan-source-tabs" role="tablist" aria-label={en ? "Choose content source" : "Chọn nguồn cần kiểm tra"}>
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
              <label className={`scan-upload-zone ${imagePreview ? "has-file" : ""}`}>
                <input type="file" accept="image/*" onChange={onImageSelect} />
                <span className="scan-upload-icon">
                  <svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 22V7m0 0-6 6m6-6 6 6M6 20v5h20v-5" /></svg>
                </span>
                <strong>{imagePreview ? (en ? "Image loaded · Choose another" : "Ảnh đã được nạp · Chọn ảnh khác") : (en ? "Drop an image or tap to choose" : "Kéo ảnh vào hoặc nhấn để chọn")}</strong>
                <small>JPG · PNG · WEBP · {en ? "AUTOMATIC QR SCAN" : "TỰ ĐỘNG QUÉT QR"}</small>
                <div className="scan-upload-corners"><i /><i /><i /><i /></div>
              </label>
            )}

            {scanMode === "text" && (
              <label className="scan-direct-input">
                <span>{en ? "Paste an SMS, email or chat message" : "Dán nội dung SMS, email hoặc đoạn chat"}</span>
                <textarea
                  value={textInput}
                  onChange={(event) => setTextInput(event.target.value)}
                  maxLength="20000"
                  rows="9"
                  placeholder={en ? "Example: Your account will be locked. Visit this link to verify..." : "Ví dụ: Tài khoản của quý khách sẽ bị khóa. Truy cập đường dẫn sau để xác minh..."}
                />
                <small>{textInput.length.toLocaleString(en ? "en-US" : "vi-VN")} / 20,000 {en ? "characters" : "ký tự"}</small>
              </label>
            )}

            {scanMode === "url" && (
              <label className="scan-direct-input scan-url-input">
                <span>{en ? "Enter a URL or domain to check" : "Nhập URL hoặc tên miền cần kiểm tra"}</span>
                <div><b>URL</b><input value={urlInput} onChange={(event) => setUrlInput(event.target.value)} placeholder="https://example.com/xac-minh-tai-khoan" /></div>
                <small>{en ? "Only the URL structure is analyzed; the link is never opened." : "Hệ thống chỉ phân tích cấu trúc URL, không tự mở liên kết."}</small>
              </label>
            )}

            {scanMode === "pdf" && (
              <label className={`scan-upload-zone scan-pdf-zone ${documentFile ? "has-file" : ""}`}>
                <input type="file" accept="application/pdf,.pdf" onChange={handleDocumentSelect} />
                <span className="scan-upload-icon"><b>PDF</b></span>
                <strong>{documentFile ? documentFile.name : (en ? "Choose an invoice or PDF notice" : "Chọn hóa đơn hoặc giấy báo PDF")}</strong>
                <small>{en ? "UP TO 15 MB · 10 PAGES · SCANNED PDF SUPPORTED" : "TỐI ĐA 15 MB · 10 TRANG · HỖ TRỢ PDF SCAN"}</small>
                <div className="scan-upload-corners"><i /><i /><i /><i /></div>
              </label>
            )}

            {scanMode === "batch" && <label className="scan-direct-input"><span>{en ? "Paste up to 50 URLs, one per line" : "Dán tối đa 50 URL, mỗi dòng một URL"}</span><textarea rows="10" value={batchInput} onChange={(event) => setBatchInput(event.target.value)} placeholder={"https://example.com\nhttps://suspicious-domain.top/login"} /><small>{batchInput.split(/[\r\n,;]+/).filter((value) => value.trim()).length}/50 URL</small></label>}

            <div className="scan-input-actions">
              {scanMode === "image" ? (
                <button type="button" className="scan-camera-button" onClick={onOpenCamera}>
                  <span>◎</span> {en ? "Use camera" : "Chụp bằng camera"}
                </button>
              ) : <span className="scan-local-storage-note">✓ {en ? "Results saved in this browser" : "Kết quả lưu trên trình duyệt"}</span>}
              <button className="scan-launch-button" disabled={loading || !sourceReady}>
                {loading ? <><i /> {en ? "Analyzing..." : "Đang phân tích..."}</> : <>{en ? "Analyze now" : "Phân tích ngay"} <span>→</span></>}
              </button>
            </div>
            <p className="scan-safe-browsing-notice">
              {en
                ? "URLs found in submitted content may be sent to Google Safe Browsing for threat-list checking. A missing match does not guarantee safety."
                : "URL tìm thấy trong nội dung có thể được gửi tới Google Safe Browsing để đối chiếu danh sách đe dọa. Không có kết quả khớp không bảo đảm URL an toàn."}
            </p>
          </form>

        </section>

        <section className="scan-viewer-panel panel">
          <header className="scan-panel-heading">
            <div><span className="eyebrow">{en ? "SAFE PREVIEW" : "XEM TRƯỚC AN TOÀN"}</span><h3>{en ? "Preview before analysis" : "Xem trước trước khi phân tích"}</h3></div>
            <span className={`scan-viewer-status ${loading ? "active" : ""}`}><i /> {loading ? (en ? "SCANNING" : "ĐANG QUÉT") : result ? (en ? "COMPLETE" : "HOÀN TẤT") : (en ? "READY" : "SẴN SÀNG")}</span>
          </header>
          <ScanViewport imageSource={scanMode === "image" ? imageSource : ""} loading={loading} result={result} mode={scanMode} textPreview={textPreview} documentName={scanMode === "pdf" ? documentFile?.name : ""} language={language} />
        </section>
      </div>

      {batchResults?.length > 0 && <section className="batch-result-panel panel"><header><div><span className="eyebrow">BATCH SCAN</span><h3>{en ? "Batch results" : "Kết quả quét hàng loạt"}</h3></div><button type="button" onClick={() => { const rows = ["url,risk_score,risk_level", ...batchResults.map((item) => `"${String(item.url).replaceAll('"','""')}",${item.risk_score},${item.risk_level}`)]; const blob = new Blob([rows.join("\n")], { type: "text/csv;charset=utf-8" }); const anchor = document.createElement("a"); anchor.href = URL.createObjectURL(blob); anchor.download = "scam-detector-batch.csv"; anchor.click(); URL.revokeObjectURL(anchor.href); }}>{en ? "Download CSV" : "Tải CSV"}</button></header><div>{batchResults.map((item) => <article className={item.risk_level} key={item.url}><code>{item.url}</code><strong>{item.status === "invalid" ? (en ? "Invalid" : "Không hợp lệ") : `${item.risk_score}/100`}</strong><span>{item.risk_level}</span></article>)}</div></section>}

      {result && <ResultConsole result={result} apiBase={apiBase} language={language} />}

      {isCameraOpen && (
        <div className="camera-modal-backdrop scan-camera-backdrop">
          <section className="camera-modal scan-camera-modal" role="dialog" aria-modal="true" aria-labelledby="camera-title">
            <header className="scan-camera-header">
              <div><span className="scan-banner-live"><i /> {en ? "CAMERA ACTIVE" : "CAMERA ĐANG HOẠT ĐỘNG"}</span><h3 id="camera-title">{en ? "Take a photo to check" : "Chụp ảnh kiểm tra"}</h3></div>
              <button type="button" onClick={onCloseCamera} aria-label={en ? "Close camera" : "Đóng camera"}>×</button>
            </header>
            <div className="scan-camera-viewport">
              {cameraStream ? <video ref={videoRef} className="camera-video" autoPlay playsInline muted /> : <p className="camera-error">{cameraError}</p>}
              {cameraStream && <><div className="scan-hud-grid" /><div className="scan-beam" /><span className="scan-lock lock-tl" /><span className="scan-lock lock-tr" /><span className="scan-lock lock-bl" /><span className="scan-lock lock-br" /></>}
            </div>
            {cameraStream && cameraError && <p className="camera-error">{cameraError}</p>}
            <div className="camera-actions">
              <button type="button" onClick={onCapturePhoto} disabled={!cameraStream}>{en ? "Capture and use photo" : "Chụp và sử dụng ảnh"}</button>
              <button type="button" className="ghost" onClick={onCloseCamera}>{en ? "Cancel" : "Hủy"}</button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
