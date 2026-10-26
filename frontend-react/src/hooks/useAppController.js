import { useEffect, useMemo, useRef, useState } from "react";

export const API_BASE =
  import.meta.env.VITE_API_BASE || "http://localhost:8000";

const GUEST_HISTORY_KEY = "scam_detector_guest_history";
const GUEST_NAME_KEY = "scam_detector_guest_name";
const GUEST_SINCE_KEY = "scam_detector_guest_since";
const MAX_GUEST_HISTORY = 50;

function loadGuestHistory() {
  try {
    const value = JSON.parse(localStorage.getItem(GUEST_HISTORY_KEY) || "[]");
    return Array.isArray(value) ? value : [];
  } catch {
    return [];
  }
}

function saveGuestHistory(items) {
  const limited = items.slice(0, MAX_GUEST_HISTORY);
  localStorage.setItem(GUEST_HISTORY_KEY, JSON.stringify(limited));
  return limited;
}

function createGuestUser() {
  let createdAt = localStorage.getItem(GUEST_SINCE_KEY);
  if (!createdAt) {
    createdAt = new Date().toISOString();
    localStorage.setItem(GUEST_SINCE_KEY, createdAt);
  }
  return {
    id: "guest-device",
    email: "Không yêu cầu email",
    full_name: localStorage.getItem(GUEST_NAME_KEY) || "Người dùng khách",
    role: "guest",
    is_active: true,
    created_at: createdAt,
    auth_provider: "local_device",
  };
}

export default function useAppController() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [me, setMe] = useState(() => createGuestUser());
  const [form, setForm] = useState({ email: "", password: "" });
  const [scanMode, setScanModeState] = useState("image");
  const [file, setFile] = useState(null);
  const [imagePreview, setImagePreview] = useState("");
  const [textInput, setTextInput] = useState("");
  const [urlInput, setUrlInput] = useState("");
  const [documentFile, setDocumentFile] = useState(null);
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);
  const [cameraError, setCameraError] = useState("");
  const videoRef = useRef(null);
  const [selectedCategoryId, setSelectedCategoryId] = useState("");
  const [categories, setCategories] = useState([]);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState(() => loadGuestHistory());
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
  const [authError, setAuthError] = useState("");
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

  function setScanMode(mode) {
    setScanModeState(mode);
    setResult(null);
  }

  useEffect(() => {
    if (!token) {
      setMe(createGuestUser());
      setHistory(loadGuestHistory());
      return;
    }
    fetch(`${API_BASE}/me`, { headers: authHeaders })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.role === "admin") {
          setMe(data);
          return;
        }
        localStorage.removeItem("token");
        setToken("");
        setMe(createGuestUser());
        setHistory(loadGuestHistory());
      })
      .catch(() => {
        localStorage.removeItem("token");
        setToken("");
        setMe(createGuestUser());
        setHistory(loadGuestHistory());
      });
  }, [token, authHeaders]);

  useEffect(() => {
    fetchCategories();
    fetchModels();
    if (token && me?.role === "admin") {
      fetchHistory();
      fetchDatasets();
      fetchEvaluations();
      fetchLogs();
    } else if (!token) {
      setHistory(loadGuestHistory());
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
    if (!token || me?.role !== "admin") {
      setHistory(loadGuestHistory());
      return;
    }
    const res = await fetch(`${API_BASE}/scan-history`, {
      headers: authHeaders,
    });
    if (res.ok) {
      const databaseHistory = await res.json();
      const combined = [...loadGuestHistory(), ...databaseHistory]
        .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
      setHistory(combined);
    }
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

  function completeAuth(data) {
    if (data.user?.role !== "admin") {
      throw new Error("Chỉ quản trị viên mới được đăng nhập");
    }
    localStorage.setItem("token", data.token);
    setToken(data.token);
    setMe(data.user);
    setForm({ email: "", password: "" });
    setAuthError("");
    navigate("overview");
  }

  async function handleAuth(event) {
    event.preventDefault();
    setLoading(true);
    setAuthError("");
    try {
      const res = await fetch(`${API_BASE}/admin/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: form.email, password: form.password }),
      });
      const data = await res.json();
      if (!res.ok) {
        setAuthError(data.detail || "Không thể xác thực quản trị viên");
        return;
      }
      completeAuth(data);
    } catch (error) {
      setAuthError(error.message || "Không kết nối được máy chủ. Hãy kiểm tra backend.");
    } finally {
      setLoading(false);
    }
  }

  async function updateProfile(fullName) {
    if (me?.role !== "admin") {
      const normalized = fullName.trim().replace(/\s+/g, " ");
      localStorage.setItem(GUEST_NAME_KEY, normalized);
      const guest = { ...createGuestUser(), full_name: normalized };
      setMe(guest);
      return guest;
    }
    const res = await fetch(`${API_BASE}/me`, {
      method: "PATCH",
      headers: authHeaders,
      body: JSON.stringify({ full_name: fullName }),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Không thể cập nhật hồ sơ");
    }
    setMe(data);
    return data;
  }

  async function handleScan(event) {
    event.preventDefault();
    if (!file) {
      alert("Vui lòng chọn ảnh trước khi phân tích");
      return;
    }
    setLoading(true);
    const body = new FormData();
    body.append("file", file);
    if (selectedCategoryId)
      body.append("scam_category_id", String(selectedCategoryId));
    const requestHeaders = token && me?.role === "admin"
      ? { Authorization: `Bearer ${token}` }
      : undefined;
    const res = await fetch(`${API_BASE}/check-image`, {
      method: "POST",
      headers: requestHeaders,
      body,
    });
    const data = await res.json();
    setLoading(false);
    if (!res.ok) {
      alert(data.detail || "Lỗi phân tích ảnh");
      return;
    }
    finalizeAnalysis(data, file.name);
  }

  function finalizeAnalysis(data, fallbackName) {
    const normalizedResult = {
      ...data,
      id: data.scan_id || Date.now(),
      original_filename: data.original_filename || fallbackName,
      created_at: data.created_at || new Date().toISOString(),
    };
    setResult(normalizedResult);

    if (data.storage === "database" && token && me?.role === "admin") {
      fetchHistory();
      return;
    }

    try {
      const localHistory = loadGuestHistory();
      const updatedLocal = saveGuestHistory([normalizedResult, ...localHistory]);
      if (me?.role === "admin") {
        setHistory((current) => [
          normalizedResult,
          ...current.filter((item) => item.id !== normalizedResult.id),
        ]);
      } else {
        setHistory(updatedLocal);
      }
    } catch {
      alert("Trình duyệt đã đầy bộ nhớ lịch sử. Hãy xóa bớt dữ liệu cũ.");
    }
  }

  async function handleContentScan(event) {
    event.preventDefault();
    let endpoint = "";
    let options = { method: "POST" };
    let fallbackName = "Nội dung phân tích";

    if (scanMode === "text") {
      if (!textInput.trim()) {
        alert("Vui lòng dán nội dung tin nhắn cần kiểm tra");
        return;
      }
      endpoint = "/check-text";
      fallbackName = "Nội dung tin nhắn";
      options.headers = { "Content-Type": "application/json" };
      options.body = JSON.stringify({ text: textInput.trim() });
    } else if (scanMode === "url") {
      if (!urlInput.trim()) {
        alert("Vui lòng nhập URL cần kiểm tra");
        return;
      }
      endpoint = "/check-url";
      fallbackName = urlInput.trim();
      options.headers = { "Content-Type": "application/json" };
      options.body = JSON.stringify({ url: urlInput.trim() });
    } else if (scanMode === "pdf") {
      if (!documentFile) {
        alert("Vui lòng chọn file PDF cần kiểm tra");
        return;
      }
      endpoint = "/check-document";
      fallbackName = documentFile.name;
      const body = new FormData();
      body.append("file", documentFile);
      options.body = body;
    } else {
      return handleScan(event);
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}${endpoint}`, options);
      const data = await res.json();
      if (!res.ok) {
        alert(data.detail || "Không thể phân tích nội dung");
        return;
      }
      finalizeAnalysis(data, fallbackName);
    } catch {
      alert("Không kết nối được máy chủ phân tích");
    } finally {
      setLoading(false);
    }
  }

  function handleImageSelect(event) {
    const selectedFile = event.target.files[0];
    setFile(selectedFile || null);
    setImagePreview(selectedFile ? URL.createObjectURL(selectedFile) : "");
    setResult(null);
  }

  function handleDocumentSelect(event) {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.size > 15 * 1024 * 1024) {
      alert("PDF tối đa 15 MB");
      event.target.value = "";
      setDocumentFile(null);
      return;
    }
    setDocumentFile(selectedFile || null);
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
    setMe(createGuestUser());
    setResult(null);
    setImagePreview("");
    setHistory(loadGuestHistory());
    setDatasets([]);
    setModels([]);
    setEvaluations([]);
    setLogs([]);
    navigate("overview");
  }

  function navigate(page) {
    window.location.hash = page;
    setActivePage(page);
  }

  return {
    token,
    me,
    form,
    setForm,
    loading,
    authError,
    handleAuth,
    updateProfile,
    activePage,
    navigate,
    logout,
    categories,
    scanMode,
    setScanMode,
    selectedCategoryId,
    setSelectedCategoryId,
    file,
    imagePreview,
    result,
    handleScan,
    handleContentScan,
    handleImageSelect,
    textInput,
    setTextInput,
    urlInput,
    setUrlInput,
    documentFile,
    handleDocumentSelect,
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
