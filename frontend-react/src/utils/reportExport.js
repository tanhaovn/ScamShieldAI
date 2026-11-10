const esc = (value) => String(value ?? "")
  .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;").replaceAll("'", "&#039;");

const reportId = (result) => {
  const value = String(result.scan_id || result.id || Date.now()).replace(/\D/g, "");
  return `SD-RPT-${value.slice(-10).padStart(6, "0")}`;
};

const renderList = (items, empty) => {
  const values = (items || []).filter(Boolean);
  return values.length ? `<ul>${values.map((item) => `<li>${esc(item)}</li>`).join("")}</ul>` : `<p class="muted">${esc(empty)}</p>`;
};

function reportHtml(result, language) {
  const en = language === "en";
  const t = en ? {
    title: "Scam detection report", time: "Generated", code: "Report ID", verdict: "Assessment",
    score: "Risk score", source: "Input source", why: "Why this result was returned",
    action: "Recommended safe action", evidence: "Evidence", layers: "Analysis layers",
    links: "Links found", qr: "QR content", content: "Content read by the system",
    refs: "Independent sources", limits: "Technical limitations", none: "No notable evidence recorded.",
    noText: "No readable content was recorded.", footer: "Safety decision support only; not a legal conclusion.",
  } : {
    title: "Báo cáo kiểm tra lừa đảo", time: "Thời gian xuất", code: "Mã báo cáo", verdict: "Kết luận",
    score: "Điểm rủi ro", source: "Nguồn kiểm tra", why: "Vì sao có kết quả này",
    action: "Hành động an toàn đề xuất", evidence: "Bằng chứng đáng chú ý", layers: "Các lớp phân tích",
    links: "Đường link phát hiện", qr: "Nội dung QR", content: "Nội dung hệ thống đã đọc",
    refs: "Nguồn đối chiếu độc lập", limits: "Giới hạn kỹ thuật", none: "Không ghi nhận bằng chứng nổi bật.",
    noText: "Không ghi nhận được nội dung có thể đọc.", footer: "Báo cáo hỗ trợ quyết định an toàn, không phải kết luận pháp lý.",
  };
  const locale = en ? "en-US" : "vi-VN";
  const levels = en ? { an_toan: "Safe", nghi_ngo: "Suspicious", nguy_hiem: "Dangerous" } : { an_toan: "An toàn", nghi_ngo: "Nghi ngờ", nguy_hiem: "Nguy hiểm" };
  const sources = en ? { image: "Image / QR", text: "Message", url: "URL", pdf: "PDF document" } : { image: "Ảnh / QR", text: "Tin nhắn", url: "Đường link", pdf: "Tài liệu PDF" };
  const score = Math.min(100, Math.max(0, Number(result.risk_score) || 0));
  const components = result.analysis_breakdown?.components || [];
  const evidence = [...(result.highlighted_terms || []).map((x) => `${en ? "Notable phrase" : "Cụm từ đáng chú ý"}: ${x}`), ...(result.visual_flags || [])];
  const urls = (result.phishvn_urls || []).map((x) => `${x.url || x.normalized_url || ""} — ${Math.round(Number(x.risk_score ?? x.probability * 100) || 0)}/100`);
  const refs = [];
  if (result.google_safe_browsing?.matches?.length) refs.push(en ? "Google Safe Browsing confirmed a known threat-list match." : "Google Safe Browsing xác nhận URL khớp danh sách mối đe dọa đã biết.");
  else if (result.google_safe_browsing?.configured && result.google_safe_browsing?.available) refs.push(en ? "Google Safe Browsing lookup completed with no known match." : "Đã đối chiếu Google Safe Browsing và chưa có kết quả khớp đã biết.");
  if (result.phishvn_model) refs.push(`PhishVN URL model: ${result.phishvn_model}`);
  const accent = result.risk_level === "nguy_hiem" ? "#d75555" : result.risk_level === "nghi_ngo" ? "#d49a32" : "#419679";
  return `<!doctype html><html lang="${en ? "en" : "vi"}"><head><meta charset="utf-8"><title>${esc(t.title)} · ${reportId(result)}</title><style>
  @page{size:A4;margin:15mm}*{box-sizing:border-box}body{margin:0;color:#12251f;font:13px/1.55 Arial,"Segoe UI",sans-serif}header{display:flex;justify-content:space-between;gap:24px;padding:22px 24px;color:#fff;background:linear-gradient(135deg,#123f34,#3f9275);border-radius:16px}h1{margin:4px 0 6px;font-size:25px}h2{margin:0 0 10px;font-size:16px}.eyebrow,.label{font-size:10px;font-weight:700;letter-spacing:1.3px;text-transform:uppercase}.eyebrow{color:#b6f3dd}.meta{text-align:right;font-size:11px}.meta b{display:block;font-size:13px}.summary,.grid{display:grid;grid-template-columns:1.25fr .75fr;gap:12px;margin:14px 0}.grid{grid-template-columns:1fr 1fr}.card{break-inside:avoid;border:1px solid #dce9e4;border-radius:12px;padding:14px;background:#fbfdfc}.verdict{border-left:5px solid ${accent}}.score{display:flex;align-items:center;justify-content:center;text-align:center;background:#eef8f4}.score strong{display:block;font-size:40px;line-height:1;color:#256a54}.score small,.muted{color:#687d74}.label{color:#54806f}p{margin:5px 0;white-space:pre-wrap}ul{margin:7px 0 0;padding-left:19px}li{margin:3px 0}.content{overflow-wrap:anywhere}table{width:100%;border-collapse:collapse}td{padding:8px;border-bottom:1px solid #e5eeea}td:last-child{text-align:right;font-weight:700}footer{margin-top:16px;padding-top:10px;border-top:1px solid #dce9e4;color:#667a72;font-size:10px;text-align:center}@media print{body{-webkit-print-color-adjust:exact;print-color-adjust:exact}}</style></head><body>
  <header><div><span class="eyebrow">SCAM DETECTOR · SAFETY REPORT</span><h1>${esc(t.title)}</h1><p>${esc(result.original_filename || sources[result.source_type] || "Scam Detector")}</p></div><div class="meta"><span>${esc(t.code)}</span><b>${reportId(result)}</b><span>${esc(t.time)}</span><b>${esc(new Date().toLocaleString(locale))}</b></div></header>
  <div class="summary"><section class="card verdict"><span class="label">${esc(t.verdict)}</span><h2>${esc(levels[result.risk_level] || result.risk_level || "—")}</h2><p>${esc(result.explanation || t.none)}</p><p><b>${esc(t.source)}:</b> ${esc(sources[result.source_type] || result.source_type || "—")} · ${esc(result.created_at ? new Date(result.created_at).toLocaleString(locale) : "")}</p></section><section class="card score"><div><span class="label">${esc(t.score)}</span><strong>${score}</strong><small>/100</small></div></section></div>
  <div class="grid"><section class="card"><span class="label">${esc(t.why)}</span><p>${esc(result.explanation || t.none)}</p></section><section class="card"><span class="label">${esc(t.action)}</span><p>${esc(result.suggested_action || t.none)}</p></section></div>
  <div class="grid"><section class="card"><h2>${esc(t.evidence)}</h2>${renderList(evidence, t.none)}</section><section class="card"><h2>${esc(t.refs)}</h2>${renderList(refs, t.none)}</section></div>
  ${components.length ? `<section class="card"><h2>${esc(t.layers)}</h2><table>${components.map((x) => `<tr><td><b>${esc(x.title)}</b><br><span class="muted">${esc(x.summary || "")}</span></td><td>${Math.round(Number(x.score) || 0)}/100</td></tr>`).join("")}</table></section>` : ""}
  <div class="grid">${urls.length ? `<section class="card"><h2>${esc(t.links)}</h2>${renderList(urls, t.none)}</section>` : ""}${result.qr_codes?.length ? `<section class="card"><h2>${esc(t.qr)}</h2>${renderList(result.qr_codes, t.none)}</section>` : ""}</div>
  <section class="card"><h2>${esc(t.content)}</h2><p class="content">${esc(result.extracted_text || t.noText)}</p></section>
  ${result.analysis_breakdown?.limitations?.length ? `<section class="card" style="margin-top:12px"><h2>${esc(t.limits)}</h2>${renderList(result.analysis_breakdown.limitations, t.none)}</section>` : ""}<footer>${esc(t.footer)} · ${reportId(result)}</footer></body></html>`;
}

export function exportScanReport(result, language = "vi") {
  if (!result) return;
  const frame = document.createElement("iframe");
  frame.title = language === "en" ? "Printable safety report" : "Báo cáo an toàn để in";
  Object.assign(frame.style, { position: "fixed", width: "1px", height: "1px", right: "0", bottom: "0", opacity: "0", pointerEvents: "none" });
  document.body.appendChild(frame);
  frame.onload = () => {
    frame.contentWindow.focus();
    frame.contentWindow.print();
    window.setTimeout(() => frame.remove(), 1500);
  };
  frame.contentWindow.document.open();
  frame.contentWindow.document.write(reportHtml(result, language));
  frame.contentWindow.document.close();
}
