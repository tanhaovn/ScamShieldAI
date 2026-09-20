import Button from "./Button";

const primaryItems = [
  ["overview", "Tổng quan"],
  ["scan", "Kiểm tra ảnh"],
  ["history", "Lịch sử"],
];

const adminItems = [
  ["admin-dataset", "Dataset"],
  ["admin-models", "AI Models"],
  ["admin-evaluations", "Đánh giá Model"],
  ["admin-logs", "Nhật ký"],
];

export default function Navbar({ activePage, navigate, user, onLogout }) {
  const items =
    user.role === "admin" ? [...primaryItems, ...adminItems] : primaryItems;

  return (
    <header className="topbar">
      <button className="brand-mark" onClick={() => navigate("overview")}>
        <span className="brand-symbol" aria-hidden="true">
          S
        </span>
        <span className="brand-copy">
          <strong>Scam</strong>
          <small>Detector</small>
        </span>
      </button>

      <nav className="topbar-nav" aria-label="Điều hướng chính">
        {items.map(([page, label]) => (
          <button
            key={page}
            className={
              activePage === page ? "topbar-nav-item active" : "topbar-nav-item"
            }
            onClick={() => navigate(page)}
          >
            {label}
          </button>
        ))}
      </nav>

      <div className="topbar-actions">
        <span className="user-greeting">{user.full_name}</span>
        <Button className="header-cta" onClick={() => navigate("scan")}>
          Kiểm tra ngay
        </Button>
        <Button variant="ghost" className="logout-button" onClick={onLogout}>
          Đăng xuất
        </Button>
      </div>
    </header>
  );
}
