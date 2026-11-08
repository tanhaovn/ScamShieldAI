import { useEffect, useState } from "react";
import Button from "./components/Button";
import Card from "./components/Card";
import Footer from "./components/Footer";
import Navbar from "./components/Navbar";
import PreferencesControl from "./components/PreferencesControl";
import useAppController, { API_BASE } from "./hooks/useAppController";
import AdminPage from "./pages/Admin/AdminPage";
import AuthPage from "./pages/Auth/AuthPage";
import HistoryPage from "./pages/History/HistoryPage";
import OverviewPage from "./pages/Overview/OverviewPage";
import ProfilePage from "./pages/Profile/ProfilePage";
import ScanPage from "./pages/Scan/ScanPage";

function StatusRadar() {
  return (
    <span className="workspace-mini-radar" aria-hidden="true">
      <i className="mini-radar-ring ring-one" />
      <i className="mini-radar-ring ring-two" />
      <i className="mini-radar-sweep" />
      <i className="mini-radar-target target-one" />
      <i className="mini-radar-target target-two" />
      <span className="status-pulse" />
    </span>
  );
}

function App() {
  const app = useAppController();
  const [language, setLanguageState] = useState(() => localStorage.getItem("scam-language") || "vi");
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem("scam-theme");
    if (savedTheme) return savedTheme;
    return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  });
  const pageMetaVi = {
    overview: ["Xin chào 👋", "Không gian an toàn số dành cho bạn"],
    scan: ["Kiểm tra lừa đảo", "Phân tích ảnh, tin nhắn, đường link hoặc PDF"],
    history: ["Lịch sử kiểm tra", "Xem lại và quản lý các kết quả trước đây"],
    profile: ["Tài khoản của bạn", "Dữ liệu và lịch sử đang lưu trên thiết bị"],
    "admin-login": ["Đăng nhập quản trị", "Khu vực dành riêng cho quản trị viên"],
    "admin-dataset": ["Training Dataset", "Quản lý dữ liệu phục vụ huấn luyện"],
    "admin-models": ["AI Models", "Quản lý các phiên bản mô hình"],
    "admin-evaluations": ["Đánh giá Model", "Theo dõi chỉ số chất lượng mô hình"],
    "admin-logs": ["Nhật ký hệ thống", "Theo dõi hoạt động quản trị"],
  };
  const pageMetaEn = {
    overview: ["Hello 👋", "Your safer space for everyday digital life"],
    scan: ["Scam check", "Analyze images, messages, links or PDF files"],
    history: ["Check history", "Review and manage your previous results"],
    profile: ["Your account", "Data and history saved on this device"],
    "admin-login": ["Administrator sign in", "Restricted administrator area"],
    "admin-dataset": ["Training Dataset", "Manage model training data"],
    "admin-models": ["AI Models", "Manage model versions"],
    "admin-evaluations": ["Model evaluations", "Monitor model quality metrics"],
    "admin-logs": ["System logs", "Monitor administrative activity"],
  };
  const pageMeta = language === "en" ? pageMetaEn : pageMetaVi;

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
    localStorage.setItem("scam-theme", theme);
  }, [theme]);

  useEffect(() => {
    document.documentElement.lang = language;
    localStorage.setItem("scam-language", language);
  }, [language]);

  function setLanguage(nextLanguage) {
    setLanguageState(nextLanguage === "en" ? "en" : "vi");
  }

  if (app.activePage === "admin-login" && app.me.role !== "admin") {
    return (
      <AuthPage
        form={app.form}
        setForm={app.setForm}
        loading={app.loading}
        authError={app.authError}
        onSubmit={app.handleAuth}
        onBack={() => app.navigate("overview")}
        language={language}
      />
    );
  }

  function renderPage() {
    if (app.activePage === "overview" || (app.activePage === "admin-login" && app.me.role === "admin")) {
      return (
        <OverviewPage
          history={app.history}
          user={app.me}
          onStartScan={() => app.navigate("scan")}
          language={language}
        />
      );
    }
    if (app.activePage === "scan") {
      return (
        <ScanPage
          {...app}
          apiBase={API_BASE}
          onSubmit={app.handleScan}
          onContentSubmit={app.handleContentScan}
          onImageSelect={app.handleImageSelect}
          onOpenCamera={app.openCamera}
          onCapturePhoto={app.capturePhoto}
          onCloseCamera={app.closeCamera}
          language={language}
        />
      );
    }
    if (app.activePage === "history") {
      return (
        <HistoryPage
          history={app.history}
          selectedHistory={app.selectedHistory}
          setSelectedHistory={app.setSelectedHistory}
          apiBase={API_BASE}
          isGuest={app.me.role !== "admin"}
          language={language}
        />
      );
    }
    if (app.activePage === "profile") {
      return (
        <ProfilePage
          user={app.me}
          history={app.history}
          datasets={app.datasets}
          models={app.models}
          logs={app.logs}
          onUpdateProfile={app.updateProfile}
          language={language}
        />
      );
    }
    if (app.me.role === "admin" && app.activePage.startsWith("admin-")) {
      return <AdminPage {...app} language={language} />;
    }
    if (app.activePage.startsWith("admin-")) {
      return (
        <Card className="panel guest-admin-gate">
          <span>ADMIN ACCESS</span>
          <h3>{language === "en" ? "Administrator-only area" : "Khu vực dành riêng cho quản trị viên"}</h3>
          <p>{language === "en" ? "Standard users do not need to sign in to check content." : "Người dùng thông thường không cần đăng nhập để kiểm tra ảnh."}</p>
          <Button onClick={() => app.navigate("admin-login")}>{language === "en" ? "Administrator sign in" : "Đăng nhập quản trị"}</Button>
        </Card>
      );
    }
    return (
      <Card className="panel">
        <h3>{language === "en" ? "Page not found" : "Không tìm thấy trang"}</h3>
        <Button onClick={() => app.navigate("overview")}>{language === "en" ? "Back to overview" : "Về tổng quan"}</Button>
      </Card>
    );
  }

  const [pageTitle, pageDescription] =
    pageMeta[app.activePage] || ["Scam Detector", language === "en" ? "Risk analysis system" : "Hệ thống phân tích rủi ro"];

  return (
    <div className="app-shell">
      <Navbar
        activePage={app.activePage}
        navigate={app.navigate}
        user={app.me}
        onLogout={app.logout}
        onAdminLogin={() => app.navigate("admin-login")}
        language={language}
      />
      <section className="app-stage">
        <header className="workspace-topbar">
          <div>
            <span className="workspace-kicker">SCAM DETECTOR · {language === "en" ? "DIGITAL SAFETY" : "AN TOÀN SỐ"}</span>
            <h1>{pageTitle}</h1>
            <p>{pageDescription}</p>
          </div>
          <div className="workspace-actions">
            <PreferencesControl
              language={language}
              setLanguage={setLanguage}
              theme={theme}
              toggleTheme={() => setTheme((current) => current === "dark" ? "light" : "dark")}
            />
            <div className="workspace-status">
              <StatusRadar />
              <div>
                <strong>{app.me.role === "admin" ? (language === "en" ? "Administrator" : "Quản trị viên") : (language === "en" ? "Protection is on" : "Bảo vệ đang bật")}</strong>
                <small>{app.me.role === "admin" ? (language === "en" ? "Admin session" : "Phiên quản trị") : (language === "en" ? "Data saved locally" : "Dữ liệu lưu cục bộ")}</small>
              </div>
            </div>
          </div>
        </header>
        <div className={`app-content page-${app.activePage}`}>{renderPage()}</div>
        <Footer language={language} />
      </section>
    </div>
  );
}

export default App;
