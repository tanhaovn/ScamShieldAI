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
    scan: ["Kiểm tra lừa đảo", "Ảnh, QR, tin nhắn, đường link và tài liệu PDF"],
    history: ["Lịch sử", "Xem lại các kết quả phân tích trước đây"],
    profile: ["Không gian cá nhân", "Dữ liệu và lịch sử trên thiết bị của bạn"],
    "admin-login": ["Đăng nhập quản trị", "Khu vực dành riêng cho quản trị viên"],
    "admin-dataset": ["Training Dataset", "Quản lý dữ liệu phục vụ huấn luyện"],
    "admin-models": ["AI Models", "Quản lý các phiên bản mô hình"],
    "admin-evaluations": ["Đánh giá Model", "Theo dõi chỉ số chất lượng mô hình"],
    "admin-logs": ["Nhật ký hệ thống", "Theo dõi hoạt động quản trị"],
  };

  if (app.activePage === "admin-login" && app.me.role !== "admin") {
    return (
      <AuthPage
        form={app.form}
        setForm={app.setForm}
        loading={app.loading}
        authError={app.authError}
        onSubmit={app.handleAuth}
        onBack={() => app.navigate("overview")}
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
    if (app.activePage.startsWith("admin-")) {
      return (
        <Card className="panel guest-admin-gate">
          <span>ADMIN ACCESS</span>
          <h3>Khu vực dành riêng cho quản trị viên</h3>
          <p>Người dùng thông thường không cần đăng nhập để kiểm tra ảnh.</p>
          <Button onClick={() => app.navigate("admin-login")}>Đăng nhập quản trị</Button>
        </Card>
      );
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
        onAdminLogin={() => app.navigate("admin-login")}
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
              <strong>{app.me.role === "admin" ? "Admin đang hoạt động" : "Chế độ khách sẵn sàng"}</strong>
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
