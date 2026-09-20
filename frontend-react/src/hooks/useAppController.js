import { useEffect, useMemo, useRef, useState } from "react";

export const API_BASE =
  import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function useAppController() {
  const [mode, setMode] = useState("login");
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [me, setMe] = useState(null);
  const [form, setForm] = useState({ email: "", password: "", full_name: "" });
  const [file, setFile] = useState(null);
  const [imagePreview, setImagePreview] = useState("");
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);
  const [cameraError, setCameraError] = useState("");
  const videoRef = useRef(null);
  const [selectedCategoryId, setSelectedCategoryId] = useState("");
  const [categories, setCategories] = useState([]);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [selectedHistory, setSelectedHistory] = useState(null);
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

  useEffect(() => {
    if (videoRef.current && cameraStream)
      videoRef.current.srcObject = cameraStream;
  }, [cameraStream]);

  useEffect(() => {
    return () => cameraStream?.getTracks().forEach((track) => track.stop());
  }, [cameraStream]);

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

  async function handleAuth(event) {
    event.preventDefault();
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

  async function handleScan(event) {
    event.preventDefault();
    if (!file || !token) {
      alert("Chọn ảnh và đăng nhập trước");
      return;
    }
    setLoading(true);
    const body = new FormData();
    body.append("file", file);
    if (selectedCategoryId)
      body.append("scam_category_id", String(selectedCategoryId));
    const res = await fetch(`${API_BASE}/check-image`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body,
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

  function handleImageSelect(event) {
    const selectedFile = event.target.files[0];
    setFile(selectedFile || null);
    setImagePreview(selectedFile ? URL.createObjectURL(selectedFile) : "");
    setResult(null);
  }

  async function openCamera() {
    setCameraError("");
    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraError("Trình duyệt này không hỗ trợ mở camera trực tiếp.");
      setIsCameraOpen(true);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: "environment" } },
        audio: false,
      });
      setCameraStream(stream);
      setIsCameraOpen(true);
    } catch {
      setCameraError(
        "Không thể mở camera. Hãy cấp quyền camera cho trình duyệt rồi thử lại.",
      );
      setIsCameraOpen(true);
    }
  }

  function closeCamera() {
    cameraStream?.getTracks().forEach((track) => track.stop());
    setCameraStream(null);
    setIsCameraOpen(false);
    setCameraError("");
  }

  function capturePhoto() {
    const video = videoRef.current;
    if (!video || !video.videoWidth || !video.videoHeight) {
      setCameraError(
        "Camera chưa sẵn sàng. Vui lòng đợi một chút rồi chụp lại.",
      );
      return;
    }
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          setCameraError("Không thể tạo ảnh từ camera.");
          return;
        }
        const capturedFile = new File([blob], `camera-${Date.now()}.jpg`, {
          type: "image/jpeg",
        });
        setFile(capturedFile);
        setImagePreview(URL.createObjectURL(capturedFile));
        setResult(null);
        closeCamera();
      },
      "image/jpeg",
      0.92,
    );
  }

  async function handleCreateDataset(event) {
    event.preventDefault();
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

  async function handleCreateModel(event) {
    event.preventDefault();
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

  async function handleCreateEvaluation(event) {
    event.preventDefault();
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

  async function handleCreateLog(event) {
    event.preventDefault();
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

  function logout() {
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
  }

  function navigate(page) {
    window.location.hash = page;
    setActivePage(page);
  }

  return {
    mode,
    setMode,
    token,
    me,
    form,
    setForm,
    loading,
    handleAuth,
    activePage,
    navigate,
    logout,
    categories,
    selectedCategoryId,
    setSelectedCategoryId,
    file,
    imagePreview,
    result,
    handleScan,
    handleImageSelect,
    isCameraOpen,
    cameraStream,
    cameraError,
    videoRef,
    openCamera,
    closeCamera,
    capturePhoto,
    history,
    selectedHistory,
    setSelectedHistory,
    datasets,
    models,
    evaluations,
    logs,
    datasetForm,
    setDatasetForm,
    modelForm,
    setModelForm,
    evaluationForm,
    setEvaluationForm,
    logForm,
    setLogForm,
    handleCreateDataset,
    handleCreateModel,
    handleCreateEvaluation,
    handleCreateLog,
  };
}
