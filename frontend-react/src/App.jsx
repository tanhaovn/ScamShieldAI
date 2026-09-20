import Button from "./components/Button";
import Card from "./components/Card";
import Footer from "./components/Footer";
import Navbar from "./components/Navbar";
import useAppController, { API_BASE } from "./hooks/useAppController";
import AdminPage from "./pages/Admin/AdminPage";
import AuthPage from "./pages/Auth/AuthPage";
import HistoryPage from "./pages/History/HistoryPage";
import OverviewPage from "./pages/Overview/OverviewPage";
import ScanPage from "./pages/Scan/ScanPage";

function App() {
  const app = useAppController();

  if (!app.token || !app.me) {
    return (
      <AuthPage
        mode={app.mode}
        setMode={app.setMode}
        form={app.form}
        setForm={app.setForm}
        loading={app.loading}
        onSubmit={app.handleAuth}
      />
    );
  }

  function renderPage() {
    if (app.activePage === "overview") {
      return (
        <OverviewPage
          history={app.history}
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

  return (
    <div className="page dashboard">
      <Navbar
        activePage={app.activePage}
        navigate={app.navigate}
        user={app.me}
        onLogout={app.logout}
      />
      {renderPage()}
      <Footer />
    </div>
  );
}

export default App;
