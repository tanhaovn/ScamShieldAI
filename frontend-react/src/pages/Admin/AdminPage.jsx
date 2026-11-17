import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

function DatasetPage({ categories, form, setForm, onSubmit, items, language }) {
  const en = language === "en";
  return (
    <section className="panel">
      <h3>Training dataset</h3>
      <form onSubmit={onSubmit} className="admin-form">
        <input
          value={form.image_url}
          onChange={(event) =>
            setForm({ ...form, image_url: event.target.value })
          }
          placeholder="image_url"
        />
        <select
          value={form.scam_category_id}
          onChange={(event) =>
            setForm({ ...form, scam_category_id: event.target.value })
          }
        >
          <option value="">{en ? "Choose category" : "Chọn danh mục"}</option>
          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.display_name}
            </option>
          ))}
        </select>
        <label className="check-row">
          <input
            type="checkbox"
            checked={form.is_anonymized}
            onChange={(event) =>
              setForm({ ...form, is_anonymized: event.target.checked })
            }
          />
          Anonymized
        </label>
        <label className="check-row">
          <input
            type="checkbox"
            checked={form.is_verified}
            onChange={(event) =>
              setForm({ ...form, is_verified: event.target.checked })
            }
          />
          Verified
        </label>
        <button type="submit">{en ? "Add dataset" : "Thêm dataset"}</button>
      </form>
      <ul className="list">
        {items.length === 0 && <li>{en ? "No datasets yet" : "Chưa có dataset"}</li>}
        {items.map((item) => (
          <li key={item.id}>
            <span>{item.scam_category_id}</span>
            <strong>{item.is_verified ? "Verified" : "Pending"}</strong>
            <small>{item.uploaded_by}</small>
          </li>
        ))}
      </ul>
    </section>
  );
}

function ModelsPage({ form, setForm, onSubmit, items, language }) {
  const en = language === "en";
  return (
    <section className="panel">
      <h3>AI models</h3>
      <form onSubmit={onSubmit} className="admin-form">
        <input
          value={form.version_name}
          onChange={(event) =>
            setForm({ ...form, version_name: event.target.value })
          }
          placeholder="version_name"
        />
        <input
          value={form.description}
          onChange={(event) =>
            setForm({ ...form, description: event.target.value })
          }
          placeholder="description"
        />
        <label className="check-row">
          <input
            type="checkbox"
            checked={form.is_active}
            onChange={(event) =>
              setForm({ ...form, is_active: event.target.checked })
            }
          />
          Active
        </label>
        <button type="submit">{en ? "Add model" : "Thêm mô hình"}</button>
      </form>
      <ul className="list">
        {items.length === 0 && <li>{en ? "No models yet" : "Chưa có mô hình"}</li>}
        {items.map((item) => (
          <li key={item.id}>
            <span>{item.version_name}</span>
            <strong>{item.is_active ? "Active" : "Inactive"}</strong>
            <small>{new Date(item.created_at).toLocaleDateString()}</small>
          </li>
        ))}
      </ul>
    </section>
  );
}

function EvaluationsPage({ form, setForm, onSubmit, items, language, runResult, running, onRun }) {
  const en = language === "en";
  const fields = [
    "ai_model_id",
    "macro_f1",
    "recall",
    "false_alarm_rate",
    "explanation_usefulness",
  ];
  const latest = items[0];
  const metrics = latest ? [
    ["Macro F1", latest.macro_f1, "f1"],
    ["Recall", latest.recall, "recall"],
    [en ? "Explanation" : "Giải thích", latest.explanation_usefulness, "explain"],
    [en ? "False alarm" : "Cảnh báo sai", latest.false_alarm_rate, "false"],
  ] : [];
  const labels = runResult?.labels || [];
  const labelName = {
    an_toan: en ? "Safe" : "An toàn",
    nghi_ngo: en ? "Review" : "Nghi ngờ",
    nguy_hiem: en ? "Danger" : "Nguy hiểm",
  };
  return (
    <section className="panel admin-evaluation-dashboard">
      <div className="admin-evaluation-heading"><div><span className="eyebrow">MODEL QUALITY</span><h3>{en ? "Automated detector evaluation" : "Đánh giá bộ phát hiện tự động"}</h3><p>{en ? "Run versioned cases through the same production analysis pipeline." : "Chạy bộ ca kiểm thử có phiên bản bằng đúng pipeline phân tích đang dùng."}</p></div><button type="button" className="evaluation-run-button" onClick={onRun} disabled={running}>{running ? (en ? "Evaluating..." : "Đang đánh giá...") : (en ? "Run evaluation" : "Chạy đánh giá tự động")}</button></div>
      {runResult && <section className="evaluation-run-results">
        <div className="evaluation-runtime-line"><span><i /> {runResult.suite}</span><code>v{runResult.runtime?.app_version} · {runResult.runtime?.git_commit}</code><small>{new Date(runResult.generated_at).toLocaleString(en ? "en-US" : "vi-VN")}</small></div>
        <div className="evaluation-kpi-grid">
          <article><span>{en ? "Cases passed" : "Ca đạt"}</span><strong>{runResult.passed}/{runResult.total}</strong><small>{Math.round(runResult.accuracy * 100)}% {en ? "exact accuracy" : "đúng chính xác 3 mức"}</small></article>
          <article><span>Macro F1</span><strong>{Math.round(runResult.macro_f1 * 100)}%</strong><small>{en ? "Across all three levels" : "Trên cả ba mức rủi ro"}</small></article>
          <article><span>Recall</span><strong>{Math.round(runResult.binary.recall * 100)}%</strong><small>{runResult.binary.false_negative} {en ? "missed alerts" : "cảnh báo bị bỏ sót"}</small></article>
          <article className={runResult.binary.false_positive ? "has-failure" : ""}><span>{en ? "False alarms" : "Cảnh báo sai"}</span><strong>{runResult.binary.false_positive}</strong><small>{Math.round(runResult.binary.false_alarm_rate * 100)}% FAR</small></article>
        </div>
        <div className="evaluation-detail-grid">
          <div className="confusion-matrix-wrap"><h4>{en ? "Confusion matrix" : "Ma trận nhầm lẫn"}</h4><p>{en ? "Rows are expected, columns are detector output." : "Hàng là kết quả mong đợi, cột là kết quả bộ quét."}</p><table className="confusion-matrix"><thead><tr><th>{en ? "Expected ↓ / Output →" : "Mong đợi ↓ / Kết quả →"}</th>{labels.map((label) => <th key={label}>{labelName[label]}</th>)}</tr></thead><tbody>{labels.map((actual) => <tr key={actual}><th>{labelName[actual]}</th>{labels.map((predicted) => <td className={actual === predicted ? "correct" : (runResult.confusion_matrix[actual][predicted] ? "incorrect" : "")} key={predicted}>{runResult.confusion_matrix[actual][predicted]}</td>)}</tr>)}</tbody></table></div>
          <div className="evaluation-failures"><h4>{en ? "Cases needing attention" : "Ca cần chú ý"}</h4>{runResult.failed === 0 ? <div className="evaluation-all-pass"><b>✓</b><span><strong>{en ? "All regression cases passed" : "Tất cả ca hồi quy đều đạt"}</strong><small>{en ? "This is a regression check, not a real-world accuracy claim." : "Đây là kiểm thử hồi quy, không phải tuyên bố độ chính xác ngoài thực tế."}</small></span></div> : runResult.rows.filter((row) => !row.passed).map((row) => <article key={row.id}><code>{row.id}</code><strong>{labelName[row.expected]} → {labelName[row.actual]}</strong><small>{row.score}/100 · {row.content}</small></article>)}</div>
        </div>
      </section>}
      {!runResult && <div className="evaluation-empty-state"><span>◎</span><div><strong>{en ? "No automated run in this session" : "Chưa chạy đánh giá trong phiên này"}</strong><small>{en ? "Press Run evaluation to measure the live backend." : "Nhấn Chạy đánh giá để đo trực tiếp backend hiện tại."}</small></div></div>}
      <div className="evaluation-history-heading"><div><h4>{en ? "Saved evaluation history" : "Lịch sử đánh giá đã lưu"}</h4><p>{en ? "Automatic runs are saved when an active model exists." : "Lượt chạy tự động được lưu khi có model đang hoạt động."}</p></div>{latest && <div className="admin-evaluation-badge"><i /> #{latest.id}</div>}</div>
      {latest && <>
        <div className="admin-metric-grid">{metrics.map(([label, value, type]) => { const percent = Math.round((Number(value) || 0) * 100); const display = type === "false" ? percent : percent; return <article className={type} key={label}><span>{label}</span><strong>{display}%</strong><div><i style={{ width: `${Math.min(100, percent)}%` }} /></div><small>{type === "false" ? (en ? "Lower is better" : "Càng thấp càng tốt") : (en ? "Higher is better" : "Càng cao càng tốt")}</small></article>; })}</div>
        <div className="admin-quality-summary"><div className="admin-quality-ring" style={{ "--quality": `${Math.round((Number(latest.macro_f1) || 0) * 360)}deg` }}><span><strong>{Math.round((Number(latest.macro_f1) || 0) * 100)}</strong><small>F1</small></span></div><div><small>{en ? "CURRENT QUALITY" : "CHẤT LƯỢNG HIỆN TẠI"}</small><h4>{Number(latest.macro_f1) >= .8 ? (en ? "Ready for controlled validation" : "Sẵn sàng kiểm định có kiểm soát") : (en ? "More validation data required" : "Cần thêm dữ liệu kiểm định")}</h4><p>{en ? "A model should only be promoted after reviewing recall, false alarms and dataset provenance together." : "Chỉ nên đưa model vào sử dụng sau khi xem đồng thời recall, cảnh báo sai và nguồn gốc tập dữ liệu."}</p></div></div>
      </>}
      <form onSubmit={onSubmit} className="admin-form">
        <span className="admin-form-caption">{en ? "Manual reference entry (optional)" : "Nhập số liệu tham chiếu thủ công (không bắt buộc)"}</span>
        {fields.map((field) => (
          <input
            key={field}
            type="number"
            step={field === "ai_model_id" ? undefined : "0.01"}
            value={form[field]}
            onChange={(event) =>
              setForm({ ...form, [field]: event.target.value })
            }
            placeholder={field}
          />
        ))}
        <button type="submit">{en ? "Save evaluation" : "Lưu đánh giá"}</button>
      </form>
      <ul className="list admin-evaluation-list">
        {items.length === 0 && <li>{en ? "No evaluations yet" : "Chưa có đánh giá"}</li>}
        {items.map((item) => (
          <li key={item.id}>
            <span>Model #{item.ai_model_id}<small>{new Date(item.evaluated_at).toLocaleDateString(en ? "en-US" : "vi-VN")}</small></span>
            <strong>F1 {Math.round((Number(item.macro_f1) || 0) * 100)}%</strong>
            <small>Recall {Math.round((Number(item.recall) || 0) * 100)}% · FAR {Math.round((Number(item.false_alarm_rate) || 0) * 100)}%</small>
          </li>
        ))}
      </ul>
    </section>
  );
}

function LogsPage({ form, setForm, onSubmit, items, language }) {
  const en = language === "en";
  return (
    <section className="panel">
      <h3>System activity logs</h3>
      <form onSubmit={onSubmit} className="admin-form">
        <input
          value={form.action_type}
          onChange={(event) =>
            setForm({ ...form, action_type: event.target.value })
          }
          placeholder="action_type"
        />
        <input
          value={form.description}
          onChange={(event) =>
            setForm({ ...form, description: event.target.value })
          }
          placeholder="description"
        />
        <button type="submit">{en ? "Add log" : "Ghi nhật ký"}</button>
      </form>
      <ul className="list">
        {items.length === 0 && <li>{en ? "No logs yet" : "Chưa có nhật ký"}</li>}
        {items.map((item) => (
          <li key={item.id}>
            <span>{item.action_type}</span>
            <strong>{item.admin_id}</strong>
            <small>{item.description}</small>
          </li>
        ))}
      </ul>
    </section>
  );
}

function KeywordsPage({ form, setForm, onSubmit, items, language }) {
  const en = language === "en";
  return <section className="panel"><div className="admin-evaluation-heading"><div><span className="eyebrow">LIVE RULE ENGINE</span><h3>{en ? "Scam keyword management" : "Quản lý từ khóa lừa đảo"}</h3><p>{en ? "Add verified phrases without redeploying the application." : "Thêm cụm từ đã kiểm chứng mà không cần triển khai lại ứng dụng."}</p></div><div className="admin-evaluation-badge"><i /> {items.length} {en ? "active rules" : "quy tắc đang dùng"}</div></div><form onSubmit={onSubmit} className="admin-form keyword-form"><input value={form.keyword} onChange={(e) => setForm({ ...form, keyword: e.target.value })} placeholder={en ? "Keyword or phrase" : "Từ khóa hoặc cụm từ"} required /><select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}><option value="phishing">Phishing</option><option value="impersonation">Impersonation</option><option value="fake_invoice">Fake invoice</option><option value="job_scam">Job scam</option><option value="urgent_account_threat">Urgent threat</option></select><input type="number" min="1" max="50" value={form.weight} onChange={(e) => setForm({ ...form, weight: e.target.value })} placeholder="Weight" /><button type="submit">{en ? "Add rule" : "Thêm quy tắc"}</button></form><div className="keyword-rule-grid">{items.length === 0 ? <p>{en ? "No custom rules yet. Built-in fallbacks remain active." : "Chưa có quy tắc tùy chỉnh. Bộ mặc định vẫn đang hoạt động."}</p> : items.map((item) => <article key={item.id}><span>{item.category}</span><strong>{item.keyword}</strong><b>+{item.weight}</b></article>)}</div></section>;
}

function FeedbackPage({ items, language, onRefresh }) {
  const en = language === "en";
  const labels = {
    correct: en ? "Correct result" : "Kết quả đúng",
    false_alarm: en ? "False warning" : "Cảnh báo sai",
    missed_scam: en ? "Missed scam" : "Bỏ sót lừa đảo",
  };
  return <section className="panel admin-feedback-page"><div className="admin-evaluation-heading"><div><span className="eyebrow">USER VALIDATION</span><h3>{en ? "Feedback from users" : "Phản hồi từ người dùng"}</h3><p>{en ? "Every submitted validation is stored in the shared database." : "Mọi xác nhận đã gửi đều được lưu trong cơ sở dữ liệu dùng chung."}</p></div><div className="admin-heading-actions"><button type="button" onClick={onRefresh}>{en ? "Refresh" : "Làm mới"}</button><div className="admin-evaluation-badge"><i /> {items.length} {en ? "responses" : "phản hồi"}</div></div></div><div className="admin-feedback-list">{items.length === 0 ? <div className="admin-empty-state">{en ? "No feedback yet." : "Chưa có phản hồi nào."}</div> : items.map((item) => <article className={`verdict-${item.verdict}`} key={item.id}><header><span>{labels[item.verdict] || item.verdict}</span><time>{new Date(item.created_at).toLocaleString(en ? "en-US" : "vi-VN")}</time></header><div><strong>{item.original_filename || `${en ? "Check" : "Lượt kiểm tra"} #${item.client_scan_id || item.scan_id || "—"}`}</strong><b>{item.risk_score}/100 · {item.predicted_level}</b></div><p>{item.note || (en ? "No additional comment." : "Người dùng không để lại ghi chú.")}</p><footer><span>{item.source_type}</span><span>{item.review_status === "pending" ? (en ? "Pending review" : "Chờ xem xét") : item.review_status}</span></footer></article>)}</div></section>;
}

function DeviceWorldMap({ items, selectedId, onSelect, language }) {
  const en = language === "en";
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const markersRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return undefined;
    const map = L.map(containerRef.current, { minZoom: 2, worldCopyJump: true }).setView([18, 0], 2);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);
    markersRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
      markersRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    const layer = markersRef.current;
    if (!map || !layer) return;
    layer.clearLayers();
    const located = items.filter((item) => Number.isFinite(item.latitude) && Number.isFinite(item.longitude));
    const points = [];
    located.forEach((item) => {
      const active = selectedId !== "all" && item.id === selectedId;
      if (item.location_permission === "ip") {
        L.circle([item.latitude, item.longitude], {
          radius: Math.max(Number(item.location_accuracy) || 25000, 10000),
          stroke: false,
          fillColor: active ? "#36b889" : "#55a98a",
          fillOpacity: active ? .2 : .12,
          interactive: false,
        }).addTo(layer);
      }
      const marker = L.circleMarker([item.latitude, item.longitude], {
        radius: active ? 10 : 7,
        weight: active ? 4 : 2,
        color: active ? "#103f30" : "#ffffff",
        fillColor: active ? "#36b889" : "#55a98a",
        fillOpacity: .92,
      }).addTo(layer);
      const tooltip = document.createElement("div");
      const title = document.createElement("strong");
      const detail = document.createElement("small");
      title.textContent = item.device_name || (en ? "Unknown device" : "Thiết bị chưa rõ");
      detail.textContent = `${item.platform || "—"} · ${item.browser || "—"} · ${item.location_permission === "ip" ? (en ? "approximate IP area" : "khu vực gần đúng theo IP") : (en ? "precise coordinates" : "tọa độ chính xác")}`;
      tooltip.className = "device-map-tooltip";
      tooltip.append(title, detail);
      marker.bindTooltip(tooltip, { direction: "top", offset: [0, -8] });
      marker.on("click", () => onSelect(item.id));
      points.push([item.latitude, item.longitude]);
    });
    if (selectedId === "all") {
      if (points.length > 1) map.fitBounds(points, { padding: [42, 42], maxZoom: 9 });
      else if (points.length === 1) map.setView(points[0], 7);
      else map.setView([18, 0], 2);
    } else {
      const selected = located.find((item) => item.id === selectedId);
      if (selected) map.setView([selected.latitude, selected.longitude], selected.location_permission === "ip" ? 9 : 14);
    }
  }, [en, items, onSelect, selectedId]);

  return <div className="admin-leaflet-map" ref={containerRef} aria-label={en ? "World map of visitor devices" : "Bản đồ thế giới của các thiết bị truy cập"} />;
}

function DevicesPage({ items, language, onRefresh }) {
  const en = language === "en";
  const located = items.filter((item) => Number.isFinite(item.latitude) && Number.isFinite(item.longitude));
  const [selectedId, setSelectedId] = useState("all");
  const selected = items.find((item) => item.id === selectedId) || null;
  return <section className="panel admin-devices-page"><div className="admin-evaluation-heading"><div><span className="eyebrow">DEVICE PRESENCE</span><h3>{en ? "Devices and approximate locations" : "Thiết bị và vị trí gần đúng"}</h3><p>{en ? "Device type, operating system, browser and approximate network area are detected automatically." : "Tự động nhận diện loại thiết bị, hệ điều hành, trình duyệt và khu vực mạng gần đúng."}</p></div><div className="admin-heading-actions"><button type="button" onClick={onRefresh}>{en ? "Refresh" : "Làm mới"}</button><div className="admin-device-kpis"><span><strong>{items.length}</strong>{en ? "Devices" : "Thiết bị"}</span><span><strong>{located.length}</strong>{en ? "Located" : "Có vị trí"}</span></div></div></div><div className="admin-device-layout"><div className="admin-device-list">{items.length === 0 ? <div className="admin-empty-state">{en ? "No devices recorded yet." : "Chưa ghi nhận thiết bị nào."}</div> : <><button type="button" className={`admin-device-all ${selectedId === "all" ? "active" : ""}`} onClick={() => setSelectedId("all")}><i className="located">●</i><span><strong>{en ? "All devices" : "Tất cả thiết bị"}</strong><small>{located.length} {en ? "locations shown on the world map" : "vị trí trên bản đồ thế giới"}</small></span><b>{en ? "World view" : "Toàn thế giới"}</b></button>{items.map((item) => <button type="button" className={selected?.id === item.id ? "active" : ""} onClick={() => setSelectedId(item.id)} key={item.id}><i className={item.latitude != null ? "located" : ""}>●</i><span><strong title={item.device_name || ""}>{item.device_name || (en ? "Unknown device" : "Thiết bị chưa rõ")}</strong><small>{item.platform || "—"} · {item.browser || "—"}</small><small className="admin-device-network" title={item.ip_address || ""}>{item.ip_address || "—"} · {item.visit_count} {en ? "visits" : "lượt"} · {en ? "Last seen" : "Lần cuối"} {new Date(item.last_seen_at).toLocaleString(en ? "en-US" : "vi-VN")}</small></span><b>{item.latitude != null ? (item.location_permission === "ip" ? (en ? "Approx. by IP" : "Gần đúng theo IP") : (en ? "Located" : "Có vị trí")) : (en ? "Unavailable" : "Chưa xác định")}</b></button>)}</>}</div><div className="admin-device-map"><DeviceWorldMap items={items} selectedId={selectedId} onSelect={setSelectedId} language={language} /><div className="admin-map-caption"><strong>{selected ? selected.device_name : (en ? "All visitor devices" : "Tất cả thiết bị truy cập")}</strong><span>{selected ? (selected.latitude == null || selected.longitude == null ? (en ? "Location is not available for this device" : "Thiết bị này chưa xác định được vị trí") : selected.location_permission === "ip" ? (en ? "Approximate network area · not a street address" : "Khu vực mạng gần đúng · không phải địa chỉ cụ thể") : `${Number(selected.latitude).toFixed(5)}, ${Number(selected.longitude).toFixed(5)}`) : (en ? `${located.length} located devices worldwide` : `${located.length} thiết bị có vị trí trên toàn thế giới`)}</span>{selected?.latitude != null && <a href={`https://www.openstreetmap.org/?mlat=${selected.latitude}&mlon=${selected.longitude}#map=${selected.location_permission === "ip" ? 10 : 15}/${selected.latitude}/${selected.longitude}`} target="_blank" rel="noreferrer">{en ? "Open full map ↗" : "Mở bản đồ đầy đủ ↗"}</a>}</div></div></div></section>;
}

export default function AdminPage({
  activePage,
  categories,
  datasetForm,
  setDatasetForm,
  handleCreateDataset,
  datasets,
  modelForm,
  setModelForm,
  handleCreateModel,
  models,
  evaluationForm,
  setEvaluationForm,
  handleCreateEvaluation,
  evaluations,
  evaluationRun,
  evaluationRunning,
  handleRunEvaluation,
  logForm,
  setLogForm,
  handleCreateLog,
  logs,
  keywords,
  keywordForm,
  setKeywordForm,
  handleCreateKeyword,
  feedback,
  devices,
  fetchFeedback,
  fetchDevices,
  language = "vi",
}) {
  const pages = {
    "admin-dataset": (
      <DatasetPage
        categories={categories}
        form={datasetForm}
        setForm={setDatasetForm}
        onSubmit={handleCreateDataset}
        items={datasets}
        language={language}
      />
    ),
    "admin-models": (
      <ModelsPage
        form={modelForm}
        setForm={setModelForm}
        onSubmit={handleCreateModel}
        items={models}
        language={language}
      />
    ),
    "admin-evaluations": (
      <EvaluationsPage
        form={evaluationForm}
        setForm={setEvaluationForm}
        onSubmit={handleCreateEvaluation}
        items={evaluations}
        language={language}
        runResult={evaluationRun}
        running={evaluationRunning}
        onRun={handleRunEvaluation}
      />
    ),
    "admin-logs": (
      <LogsPage
        form={logForm}
        setForm={setLogForm}
        onSubmit={handleCreateLog}
        items={logs}
        language={language}
      />
    ),
    "admin-keywords": <KeywordsPage form={keywordForm} setForm={setKeywordForm} onSubmit={handleCreateKeyword} items={keywords} language={language} />,
    "admin-feedback": <FeedbackPage items={feedback} language={language} onRefresh={fetchFeedback} />,
    "admin-devices": <DevicesPage items={devices} language={language} onRefresh={fetchDevices} />,
  };
  return <div className="admin-grid">{pages[activePage]}</div>;
}
