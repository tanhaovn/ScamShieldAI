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
import StatisticsPage from "./pages/Statistics/StatisticsPage";

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
    statistics: ["Thống kê an toàn", "Theo dõi kết quả và xu hướng rủi ro của bạn"],
    history: ["Lịch sử kiểm tra", "Xem lại và quản lý các kết quả trước đây"],
    profile: ["Tài khoản của bạn", "Dữ liệu và lịch sử đang lưu trên thiết bị"],
    login: ["Tài khoản người dùng", "Đăng nhập để đồng bộ lịch sử kiểm tra"],
    "admin-login": ["Đăng nhập quản trị", "Khu vực dành riêng cho quản trị viên"],
    "admin-dataset": ["Training Dataset", "Quản lý dữ liệu phục vụ huấn luyện"],
    "admin-models": ["AI Models", "Quản lý các phiên bản mô hình"],
    "admin-evaluations": ["Đánh giá Model", "Theo dõi chỉ số chất lượng mô hình"],
    "admin-keywords": ["Từ khóa lừa đảo", "Quản lý quy tắc phát hiện đang hoạt động"],
    "admin-feedback": ["Phản hồi người dùng", "Xem xác nhận và góp ý từ các lượt kiểm tra"],
    "admin-devices": ["Quản lý thiết bị", "Theo dõi thiết bị truy cập và khu vực gần đúng theo IP"],
    "admin-logs": ["Nhật ký hệ thống", "Theo dõi hoạt động quản trị"],
  };
  const pageMetaEn = {
    overview: ["Hello 👋", "Your safer space for everyday digital life"],
    scan: ["Scam check", "Analyze images, messages, links or PDF files"],
    statistics: ["Safety statistics", "Track your results and risk trends"],
    history: ["Check history", "Review and manage your previous results"],
    profile: ["Your account", "Data and history saved on this device"],
    login: ["User account", "Sign in to sync your check history"],
    "admin-login": ["Administrator sign in", "Restricted administrator area"],
    "admin-dataset": ["Training Dataset", "Manage model training data"],
    "admin-models": ["AI Models", "Manage model versions"],
    "admin-evaluations": ["Model evaluations", "Monitor model quality metrics"],
    "admin-keywords": ["Scam keywords", "Manage live detection rules"],
    "admin-feedback": ["User feedback", "Review validations and comments from checks"],
    "admin-devices": ["Device management", "Monitor visits and approximate IP-based locations"],
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

  const isAuthPage = app.activePage === "login" || app.activePage === "admin-login";
  const needsAuthPage = isAuthPage && (app.me.role === "guest" || app.activePage === "admin-login" && app.me.role !== "admin");
  if (needsAuthPage) {
    return (
      <AuthPage
        form={app.form}
        setForm={app.setForm}
        loading={app.loading}
        authError={app.authError}
        authMode={app.authMode}
        setAuthMode={app.setAuthMode}
        adminMode={app.activePage === "admin-login"}
        onSubmit={app.handleAuth}
        onBack={() => app.navigate("overview")}
        onAdminLogin={() => app.navigate("admin-login")}
        language={language}
      />
    );
  }

  function renderPage() {
    if (app.activePage === "overview" || (isAuthPage && app.me.role !== "guest")) {
      return (
        <OverviewPage
          history={app.history}
          user={app.me}
          onStartScan={() => app.navigate("scan")}
          onOpenStatistics={() => app.navigate("statistics")}
          language={language}
          backendStatus={app.backendStatus}
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
    if (app.activePage === "statistics") {
      return (
        <StatisticsPage
          history={app.history}
          onStartScan={() => app.navigate("scan")}
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
          isGuest={app.me.role === "guest"}
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
          <p>{language === "en" ? "Sign in with an administrator account to continue." : "Hãy đăng nhập bằng tài khoản quản trị để tiếp tục."}</p>
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
    <div className={`app-shell ${app.activePage.startsWith("admin-") ? "admin-shell" : "public-shell"} route-${app.activePage}`}>
      <Navbar
        activePage={app.activePage}
        navigate={app.navigate}
        user={app.me}
        onLogout={app.logout}
        onLogin={() => app.navigate("login")}
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
            <div className={`workspace-status backend-${app.backendStatus.state}`}>
              <StatusRadar />
              <div>
                <strong>{app.backendStatus.state === "online" ? (language === "en" ? "Detector online" : "Bộ quét đang hoạt động") : app.backendStatus.state === "checking" ? (language === "en" ? "Checking detector" : "Đang kiểm tra bộ quét") : app.backendStatus.state === "waking" ? (language === "en" ? "Scanner waking up" : "Máy chủ đang khởi động") : (language === "en" ? "Connection unavailable" : "Chưa kết nối được máy chủ")}</strong>
                <small>{app.backendStatus.state === "online" ? `v${app.backendStatus.app_version || "?"} · ${app.backendStatus.git_commit || "unknown"}` : app.backendStatus.state === "waking" ? (language === "en" ? "You can still start a check" : "Bạn vẫn có thể bắt đầu kiểm tra") : (language === "en" ? "We will retry automatically" : "Hệ thống sẽ tự kết nối lại")}</small>
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
