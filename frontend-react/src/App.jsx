import { useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function App() {
  const [mode, setMode] = useState("login");
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [me, setMe] = useState(null);
  const [form, setForm] = useState({ email: "", password: "", full_name: "" });
  const [file, setFile] = useState(null);
  const [imagePreview, setImagePreview] = useState("");
  const [selectedCategoryId, setSelectedCategoryId] = useState("");
  const [categories, setCategories] = useState([]);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [models, setModels] = useState([]);
  const [evaluations, setEvaluations] = useState([]);
  const [logs, setLogs] = useState([]);
  const [datasetForm, setDatasetForm] = useState({
    image_url: "",
    scam_category_id: "",
    is_anonymized: false,
    is_verified: false,
  });
  const [modelForm, setModelForm] = useState({
    version_name: "",
    description: "",
    is_active: false,
  });
  const [evaluationForm, setEvaluationForm] = useState({
    ai_model_id: "",
    macro_f1: "",
    recall: "",
    false_alarm_rate: "",
    explanation_usefulness: "",
  });
  const [logForm, setLogForm] = useState({ action_type: "", description: "" });
  const [loading, setLoading] = useState(false);
  const [activePage, setActivePage] = useState(
    window.location.hash.replace("#", "") || "overview",
  );

  const authHeaders = useMemo(
    () => ({
      Authorization: token ? `Bearer ${token}` : "",
      "Content-Type": "application/json",
    }),
    [token],
  );

  useEffect(() => {
    if (!token) return;
    fetch(`${API_BASE}/me`, { headers: authHeaders })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setMe(data))
      .catch(() => setMe(null));
  }, [token, authHeaders]);

  useEffect(() => {
    if (!token) return;
    fetchCategories();
    fetchHistory();
    fetchModels();
    if (me?.role === "admin") {
      fetchDatasets();
      fetchEvaluations();
      fetchLogs();
    }
  }, [token, me?.role]);

  async function fetchCategories() {
    const res = await fetch(`${API_BASE}/scam-categories`, {
      headers: authHeaders,
    });
    if (res.ok) {
      const data = await res.json();
      setCategories(data);
      if (data.length && !selectedCategoryId)
        setSelectedCategoryId(String(data[0].id));
    }
  }

  async function fetchHistory() {
    if (!token) return;
    const res = await fetch(`${API_BASE}/scan-history`, {
      headers: authHeaders,
    });
    if (res.ok) setHistory(await res.json());
  }

  async function fetchDatasets() {
    const res = await fetch(`${API_BASE}/training-dataset`, {
      headers: authHeaders,
    });
    if (res.ok) setDatasets(await res.json());
  }

  async function fetchModels() {
    const res = await fetch(`${API_BASE}/ai-models`, { headers: authHeaders });
    if (res.ok) setModels(await res.json());
  }

  async function fetchEvaluations() {
    const res = await fetch(`${API_BASE}/model-evaluations`, {
      headers: authHeaders,
    });
    if (res.ok) setEvaluations(await res.json());
  }

  async function fetchLogs() {
    const res = await fetch(`${API_BASE}/system-logs`, {
      headers: authHeaders,
    });
    if (res.ok) setLogs(await res.json());
  }

  async function handleAuth(e) {
    e.preventDefault();
    setLoading(true);
    const endpoint = mode === "login" ? "/login" : "/register";
    const payload =
      mode === "login"
        ? { email: form.email, password: form.password }
        : {
            email: form.email,
            password: form.password,
            full_name: form.full_name,
          };

    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    setLoading(false);

    if (!res.ok) {
      alert(data.detail || "Lỗi xác thực");
      return;
    }

    localStorage.setItem("token", data.token);
    setToken(data.token);
    setMe(data.user);
    setMode("login");
    setForm({ email: "", password: "", full_name: "" });
  }

  async function handleScan(e) {
    e.preventDefault();
    if (!file || !token) {
      alert("Chọn ảnh và đăng nhập trước");
      return;
    }

    setLoading(true);
    const fd = new FormData();
    fd.append("file", file);
    if (selectedCategoryId)
      fd.append("scam_category_id", String(selectedCategoryId));

    const res = await fetch(`${API_BASE}/check-image`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: fd,
    });

    const data = await res.json();
    setLoading(false);

    if (!res.ok) {
      alert(data.detail || "Lỗi phân tích ảnh");
      return;
    }

    setResult(data);
    fetchHistory();
  }

  async function handleCreateDataset(e) {
    e.preventDefault();
    if (!datasetForm.image_url) {
      alert("Vui lòng nhập image_url");
      return;
    }

    const res = await fetch(`${API_BASE}/training-dataset`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify({
        ...datasetForm,
        scam_category_id: Number(datasetForm.scam_category_id || 0) || null,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      alert(data.detail || "Không thể tạo dataset");
      return;
    }

    setDatasetForm({
      image_url: "",
      scam_category_id: "",
      is_anonymized: false,
      is_verified: false,
    });
    fetchDatasets();
  }

  async function handleCreateModel(e) {
    e.preventDefault();
    if (!modelForm.version_name) {
      alert("Vui lòng nhập tên phiên bản model");
      return;
    }

    const res = await fetch(`${API_BASE}/ai-models`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify(modelForm),
    });
    const data = await res.json();
    if (!res.ok) {
      alert(data.detail || "Không thể tạo model");
      return;
    }

    setModelForm({ version_name: "", description: "", is_active: false });
    fetchModels();
  }

  async function handleCreateEvaluation(e) {
    e.preventDefault();
    const res = await fetch(`${API_BASE}/model-evaluations`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify({
        ai_model_id: Number(evaluationForm.ai_model_id),
        macro_f1: Number(evaluationForm.macro_f1 || 0),
        recall: Number(evaluationForm.recall || 0),
        false_alarm_rate: Number(evaluationForm.false_alarm_rate || 0),
        explanation_usefulness: Number(
          evaluationForm.explanation_usefulness || 0,
        ),
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      alert(data.detail || "Không thể lưu đánh giá");
      return;
    }

    setEvaluationForm({
      ai_model_id: "",
      macro_f1: "",
      recall: "",
      false_alarm_rate: "",
      explanation_usefulness: "",
    });
    fetchEvaluations();
  }

  async function handleCreateLog(e) {
    e.preventDefault();
    if (!logForm.action_type) {
      alert("Vui lòng nhập action type");
      return;
    }

    const res = await fetch(`${API_BASE}/system-logs`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify(logForm),
    });
    const data = await res.json();
    if (!res.ok) {
      alert(data.detail || "Không thể ghi log");
      return;
    }

    setLogForm({ action_type: "", description: "" });
    fetchLogs();
  }

  const logout = () => {
    localStorage.removeItem("token");
    setToken("");
    setMe(null);
    setCategories([]);
    setResult(null);
    setImagePreview("");
    setHistory([]);
    setDatasets([]);
    setModels([]);
    setEvaluations([]);
    setLogs([]);
  };

  function navigate(page) {
    window.location.hash = page;
    setActivePage(page);
  }

  if (!token || !me) {
    return (
      <div className="page auth-page">
        <div className="auth-card">
          <h1>Scam Detector</h1>
          <div className="tabs">
            <button
              className={mode === "login" ? "tab active" : "tab"}
              onClick={() => setMode("login")}
            >
              Đăng nhập
            </button>
            <button
              className={mode === "register" ? "tab active" : "tab"}
              onClick={() => setMode("register")}
            >
              Đăng ký
            </button>
          </div>

          <form onSubmit={handleAuth} className="auth-form">
            {mode === "register" && (
              <input
                value={form.full_name}
                onChange={(e) =>
                  setForm({ ...form, full_name: e.target.value })
                }
                placeholder="Họ tên"
              />
            )}
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="Email"
            />
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="Mật khẩu"
            />
            <button disabled={loading}>
              {loading
                ? "Đang xử lý..."
                : mode === "login"
                  ? "Đăng nhập"
                  : "Tạo tài khoản"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="page dashboard">
      <header className="topbar">
        <div>
          <h2>Scam Detector</h2>
          <small>
            Xin chào, {me.full_name} ({me.role})
          </small>
        </div>
        <div className="topbar-actions">
          <button className="ghost" onClick={() => navigate("overview")}>
            Trang chủ
          </button>
          <button className="ghost" onClick={logout}>
            Đăng xuất
          </button>
        </div>
      </header>

      <nav className="main-nav" aria-label="Điều hướng chính">
        <button
          className={activePage === "overview" ? "nav-item active" : "nav-item"}
          onClick={() => navigate("overview")}
        >
          Tổng quan
        </button>
        <button
          className={activePage === "scan" ? "nav-item active" : "nav-item"}
          onClick={() => navigate("scan")}
        >
          Kiểm tra ảnh
        </button>
        <button
          className={activePage === "history" ? "nav-item active" : "nav-item"}
          onClick={() => navigate("history")}
        >
          Lịch sử
        </button>
        {me.role === "admin" && (
          <>
            <button
              className={
                activePage === "admin-dataset" ? "nav-item active" : "nav-item"
              }
              onClick={() => navigate("admin-dataset")}
            >
              Dataset
            </button>
            <button
              className={
                activePage === "admin-models" ? "nav-item active" : "nav-item"
              }
              onClick={() => navigate("admin-models")}
            >
              AI Models
            </button>
            <button
              className={
                activePage === "admin-evaluations"
                  ? "nav-item active"
                  : "nav-item"
              }
              onClick={() => navigate("admin-evaluations")}
            >
              Đánh giá Model
            </button>
            <button
              className={
                activePage === "admin-logs" ? "nav-item active" : "nav-item"
              }
              onClick={() => navigate("admin-logs")}
            >
              Nhật ký
            </button>
          </>
        )}
      </nav>

      {activePage === "overview" && (
        <section className="welcome panel">
          <div>
            <span className="eyebrow">TRUNG TÂM BẢO VỆ</span>
            <h1>Kiểm tra trước khi bạn tin.</h1>
            <p>
              Phân tích ảnh đáng ngờ bằng OCR, dấu hiệu hình ảnh và điểm rủi ro.
            </p>
          </div>
          <button onClick={() => navigate("scan")}>Bắt đầu kiểm tra</button>
        </section>
      )}

      {activePage === "scan" && (
        <div className="grid page-view">
          <section className="panel">
            <h3>Kiểm tra ảnh</h3>
            <form onSubmit={handleScan} className="scan-form">
              <label className="label">Danh mục scam</label>
              <select
                value={selectedCategoryId}
                onChange={(e) => setSelectedCategoryId(e.target.value)}
              >
                {categories.length === 0 && (
                  <option value="">Đang tải...</option>
                )}
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.display_name}
                  </option>
                ))}
              </select>

              <input
                type="file"
                accept="image/*"
                onChange={(e) => {
                  const selectedFile = e.target.files[0];
                  setFile(selectedFile || null);
                  setImagePreview(
                    selectedFile ? URL.createObjectURL(selectedFile) : "",
                  );
                  setResult(null);
                }}
              />
              {imagePreview && (
                <img src={imagePreview} alt="Preview" className="preview" />
              )}
              <button disabled={loading}>
                {loading ? "Đang phân tích..." : "Kiểm tra"}
              </button>
            </form>

            {result && (
              <div className="result-box">
                <p>
                  <strong>Risk score:</strong> {result.risk_score}
                </p>
                <p>
                  <strong>Risk level:</strong> {result.risk_level}
                </p>
                <p>
                  <strong>Scam type:</strong>{" "}
                  {result.scam_type || result.scam_category_id}
                </p>
                <p>
                  <strong>Explanation:</strong> {result.explanation}
                </p>
                <p>
                  <strong>Suggested action:</strong> {result.suggested_action}
                </p>
                {result.image_url && (
                  <img
                    src={`${API_BASE}${result.image_url}`}
                    alt="Uploaded"
                    className="preview"
                  />
                )}
              </div>
            )}
          </section>

          <section className="panel history-preview">
            <h3>Lịch sử kiểm tra</h3>
            <ul className="list">
              {history.length === 0 && <li>Chưa có lịch sử</li>}
              {history.map((item) => (
                <li key={item.id}>
                  <span>{item.risk_level}</span>
                  <strong>{item.risk_score}</strong>
                  <small>{item.scam_category_id}</small>
                </li>
              ))}
            </ul>
          </section>
        </div>
      )}

      {activePage === "history" && (
        <section className="panel page-view history-page">
          <h3>Lịch sử kiểm tra</h3>
          <ul className="list">
            {history.length === 0 && <li>Chưa có lịch sử</li>}
            {history.map((item) => (
              <li key={item.id}>
                <span>{item.risk_level}</span>
                <strong>{item.risk_score}</strong>
                <small>
                  {item.original_filename ||
                    `Category #${item.scam_category_id}`}
                </small>
              </li>
            ))}
          </ul>
        </section>
      )}

      {me.role === "admin" && activePage.startsWith("admin-") && (
        <div className="admin-grid">
          {activePage === "admin-dataset" && (
            <section className="panel">
              <h3>Training dataset</h3>
              <form onSubmit={handleCreateDataset} className="admin-form">
                <input
                  value={datasetForm.image_url}
                  onChange={(e) =>
                    setDatasetForm({
                      ...datasetForm,
                      image_url: e.target.value,
                    })
                  }
                  placeholder="image_url"
                />
                <select
                  value={datasetForm.scam_category_id}
                  onChange={(e) =>
                    setDatasetForm({
                      ...datasetForm,
                      scam_category_id: e.target.value,
                    })
                  }
                >
                  <option value="">Chọn category</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.display_name}
                    </option>
                  ))}
                </select>
                <label className="check-row">
                  <input
                    type="checkbox"
                    checked={datasetForm.is_anonymized}
                    onChange={(e) =>
                      setDatasetForm({
                        ...datasetForm,
                        is_anonymized: e.target.checked,
                      })
                    }
                  />
                  Anonymized
                </label>
                <label className="check-row">
                  <input
                    type="checkbox"
                    checked={datasetForm.is_verified}
                    onChange={(e) =>
                      setDatasetForm({
                        ...datasetForm,
                        is_verified: e.target.checked,
                      })
                    }
                  />
                  Verified
                </label>
                <button type="submit">Thêm dataset</button>
              </form>
              <ul className="list">
                {datasets.length === 0 && <li>Chưa có dataset</li>}
                {datasets.map((item) => (
                  <li key={item.id}>
                    <span>{item.scam_category_id}</span>
                    <strong>{item.is_verified ? "Verified" : "Pending"}</strong>
                    <small>{item.uploaded_by}</small>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {activePage === "admin-models" && (
            <section className="panel">
              <h3>AI models</h3>
              <form onSubmit={handleCreateModel} className="admin-form">
                <input
                  value={modelForm.version_name}
                  onChange={(e) =>
                    setModelForm({ ...modelForm, version_name: e.target.value })
                  }
                  placeholder="version_name"
                />
                <input
                  value={modelForm.description}
                  onChange={(e) =>
                    setModelForm({ ...modelForm, description: e.target.value })
                  }
                  placeholder="description"
                />
                <label className="check-row">
                  <input
                    type="checkbox"
                    checked={modelForm.is_active}
                    onChange={(e) =>
                      setModelForm({
                        ...modelForm,
                        is_active: e.target.checked,
                      })
                    }
                  />
                  Active
                </label>
                <button type="submit">Thêm model</button>
              </form>
              <ul className="list">
                {models.length === 0 && <li>Chưa có model</li>}
                {models.map((item) => (
                  <li key={item.id}>
                    <span>{item.version_name}</span>
                    <strong>{item.is_active ? "Active" : "Inactive"}</strong>
                    <small>
                      {new Date(item.created_at).toLocaleDateString()}
                    </small>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {activePage === "admin-evaluations" && (
            <section className="panel">
              <h3>Model evaluations</h3>
              <form onSubmit={handleCreateEvaluation} className="admin-form">
                <input
                  type="number"
                  value={evaluationForm.ai_model_id}
                  onChange={(e) =>
                    setEvaluationForm({
                      ...evaluationForm,
                      ai_model_id: e.target.value,
                    })
                  }
                  placeholder="ai_model_id"
                />
                <input
                  type="number"
                  step="0.01"
                  value={evaluationForm.macro_f1}
                  onChange={(e) =>
                    setEvaluationForm({
                      ...evaluationForm,
                      macro_f1: e.target.value,
                    })
                  }
                  placeholder="macro_f1"
                />
                <input
                  type="number"
                  step="0.01"
                  value={evaluationForm.recall}
                  onChange={(e) =>
                    setEvaluationForm({
                      ...evaluationForm,
                      recall: e.target.value,
                    })
                  }
                  placeholder="recall"
                />
                <input
                  type="number"
                  step="0.01"
                  value={evaluationForm.false_alarm_rate}
                  onChange={(e) =>
                    setEvaluationForm({
                      ...evaluationForm,
                      false_alarm_rate: e.target.value,
                    })
                  }
                  placeholder="false_alarm_rate"
                />
                <input
                  type="number"
                  step="0.01"
                  value={evaluationForm.explanation_usefulness}
                  onChange={(e) =>
                    setEvaluationForm({
                      ...evaluationForm,
                      explanation_usefulness: e.target.value,
                    })
                  }
                  placeholder="explanation_usefulness"
                />
                <button type="submit">Lưu đánh giá</button>
              </form>
              <ul className="list">
                {evaluations.length === 0 && <li>Chưa có đánh giá</li>}
                {evaluations.map((item) => (
                  <li key={item.id}>
                    <span>Model #{item.ai_model_id}</span>
                    <strong>F1 {item.macro_f1}</strong>
                    <small>Recall {item.recall}</small>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {activePage === "admin-logs" && (
            <section className="panel">
              <h3>System activity logs</h3>
              <form onSubmit={handleCreateLog} className="admin-form">
                <input
                  value={logForm.action_type}
                  onChange={(e) =>
                    setLogForm({ ...logForm, action_type: e.target.value })
                  }
                  placeholder="action_type"
                />
                <input
                  value={logForm.description}
                  onChange={(e) =>
                    setLogForm({ ...logForm, description: e.target.value })
                  }
                  placeholder="description"
                />
                <button type="submit">Ghi log</button>
              </form>
              <ul className="list">
                {logs.length === 0 && <li>Chưa có log</li>}
                {logs.map((item) => (
                  <li key={item.id}>
                    <span>{item.action_type}</span>
                    <strong>{item.admin_id}</strong>
                    <small>{item.description}</small>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
