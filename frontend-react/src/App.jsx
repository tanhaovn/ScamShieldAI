import Button from "./components/Button";
import Card from "./components/Card";
import Footer from "./components/Footer";
import Navbar from "./components/Navbar";
import useAppController, { API_BASE } from "./hooks/useAppController";
import AdminPage from "./pages/Admin/AdminPage";
import AuthPage from "./pages/Auth/AuthPage";
import HistoryPage from "./pages/History/HistoryPage";
import OverviewPage from "./pages/Overview/OverviewPage";
import ProfilePage from "./pages/Profile/ProfilePage";
import ScanPage from "./pages/Scan/ScanPage";

function App() {
  const app = useAppController();
  const pageMeta = {
    overview: ["Tổng quan", "Theo dõi các lượt kiểm tra và mức độ rủi ro"],
    scan: ["Kiểm tra ảnh", "Phân tích nội dung OCR, URL và dấu hiệu chỉnh sửa"],
    history: ["Lịch sử", "Xem lại các kết quả phân tích trước đây"],
    profile: ["Trang cá nhân", "Danh tính số, hoạt động và quyền truy cập của bạn"],
    "admin-dataset": ["Training Dataset", "Quản lý dữ liệu phục vụ huấn luyện"],
    "admin-models": ["AI Models", "Quản lý các phiên bản mô hình"],
    "admin-evaluations": ["Đánh giá Model", "Theo dõi chỉ số chất lượng mô hình"],
    "admin-logs": ["Nhật ký hệ thống", "Theo dõi hoạt động quản trị"],
  };

  if (!app.token || !app.me) {
    return (
      <AuthPage
        mode={app.mode}
        setMode={app.setMode}
        form={app.form}
        setForm={app.setForm}
        loading={app.loading}
        authError={app.authError}
        googleClientId={app.googleClientId}
        onSubmit={app.handleAuth}
        onGoogleAuth={app.handleGoogleAuth}
      />
    );
  }

  function renderPage() {
    if (app.activePage === "overview") {
      return (
        <OverviewPage
          history={app.history}
          user={app.me}
          onStartScan={() => app.navigate("scan")}
        />
      );
    }
    if (app.activePage === "scan") {
      return (
        <ScanPage
          {...app}
          apiBase={API_BASE}
          onSubmit={app.handleScan}
          onImageSelect={app.handleImageSelect}
          onOpenCamera={app.openCamera}
          onCapturePhoto={app.capturePhoto}
          onCloseCamera={app.closeCamera}
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
        />
      );
    }
    if (app.me.role === "admin" && app.activePage.startsWith("admin-")) {
      return <AdminPage {...app} />;
    }
    return (
      <Card className="panel">
        <h3>Không tìm thấy trang</h3>
        <Button onClick={() => app.navigate("overview")}>Về tổng quan</Button>
      </Card>
    );
  }

  const [pageTitle, pageDescription] =
    pageMeta[app.activePage] || ["Scam Detector", "Hệ thống phân tích rủi ro"];

  return (
    <div className="app-shell">
      <Navbar
        activePage={app.activePage}
        navigate={app.navigate}
        user={app.me}
        onLogout={app.logout}
      />
      <section className="app-stage">
        <header className="workspace-topbar">
          <div>
            <span className="workspace-kicker">SCAM DETECTOR</span>
            <h1>{pageTitle}</h1>
            <p>{pageDescription}</p>
          </div>
          <div className="workspace-status">
            <span className="status-pulse" />
            <div>
              <strong>Hệ thống sẵn sàng</strong>
              <small>{new Date().toLocaleDateString("vi-VN")}</small>
            </div>
          </div>
        </header>
        <div className="app-content">{renderPage()}</div>
        <Footer />
      </section>
    </div>
  );
}

export default App;
