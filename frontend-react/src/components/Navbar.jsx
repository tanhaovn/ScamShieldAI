const primaryItems = [
  { page: "overview", label: "Tổng quan", icon: "dashboard" },
  { page: "scan", label: "Kiểm tra lừa đảo", icon: "scan" },
  { page: "history", label: "Lịch sử", icon: "history" },
];

const adminItems = [
  { page: "admin-dataset", label: "Dataset", icon: "database" },
  { page: "admin-models", label: "AI Models", icon: "model" },
  { page: "admin-evaluations", label: "Đánh giá", icon: "chart" },
  { page: "admin-logs", label: "Nhật ký", icon: "file" },
];

const iconPaths = {
  dashboard: ["M4 4h6v6H4z", "M14 4h6v6h-6z", "M4 14h6v6H4z", "M14 14h6v6h-6z"],
  scan: ["M4 8V5a1 1 0 0 1 1-1h3", "M16 4h3a1 1 0 0 1 1 1v3", "M20 16v3a1 1 0 0 1-1 1h-3", "M8 20H5a1 1 0 0 1-1-1v-3", "M8 12h8"],
  history: ["M3 12a9 9 0 1 0 3-6.7", "M3 4v5h5", "M12 7v5l3 2"],
  database: ["M4 6c0-1.1 3.6-2 8-2s8 .9 8 2-3.6 2-8 2-8-.9-8-2Z", "M4 6v6c0 1.1 3.6 2 8 2s8-.9 8-2V6", "M4 12v6c0 1.1 3.6 2 8 2s8-.9 8-2v-6"],
  model: ["M12 3 4 7v10l8 4 8-4V7z", "m4 7 8 4 8-4", "M12 11v10"],
  chart: ["M5 20V10", "M12 20V4", "M19 20v-7", "M3 20h18"],
  file: ["M6 3h8l4 4v14H6z", "M14 3v5h5", "M9 13h6", "M9 17h6"],
  logout: ["M10 17l5-5-5-5", "M15 12H3", "M15 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4"],
  login: ["m14 7 5 5-5 5", "M19 12H7", "M9 4H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4"],
};

function NavIcon({ name }) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      {iconPaths[name].map((path) => (
        <path key={path} d={path} />
      ))}
    </svg>
  );
}

function NavGroup({ label, items, activePage, navigate }) {
  return (
    <section className="sidebar-group">
      <span className="sidebar-group-label">{label}</span>
      <nav aria-label={label}>
        {items.map((item) => (
          <button
            key={item.page}
            className={
              activePage === item.page
                ? "sidebar-nav-item active"
                : "sidebar-nav-item"
            }
            onClick={() => navigate(item.page)}
          >
            <NavIcon name={item.icon} />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </section>
  );
}

export default function Navbar({ activePage, navigate, user, onLogout, onAdminLogin }) {
  const isAdmin = user.role === "admin";
  const initials = (user.full_name || user.email || "U")
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <aside className="app-sidebar">
      <button className="sidebar-brand" onClick={() => navigate("overview")}>
        <span className="sidebar-logo" aria-hidden="true">S</span>
        <span>
          <strong>Scam Detector</strong>
          <small>AI Safety Console</small>
        </span>
      </button>

      <div className="sidebar-navigation">
        <NavGroup
          label="Không gian làm việc"
          items={primaryItems}
          activePage={activePage}
          navigate={navigate}
        />
        {isAdmin && (
          <NavGroup
            label="Quản trị hệ thống"
            items={adminItems}
            activePage={activePage}
            navigate={navigate}
          />
        )}
      </div>

      <div className="sidebar-bottom">
        <button className="sidebar-new-scan" onClick={() => navigate("scan")}>
          <span>+</span> Tạo lượt kiểm tra
        </button>
        <div className={`sidebar-user${activePage === "profile" ? " active" : ""}`}>
          <button
            className="sidebar-user-profile"
            onClick={() => navigate("profile")}
            title="Mở trang cá nhân"
            aria-label={`Mở trang cá nhân của ${user.full_name || user.email}`}
          >
            <span className="user-avatar">{initials}</span>
            <span className="sidebar-user-copy">
              <strong>{user.full_name || "Người dùng"}</strong>
              <small>{isAdmin ? "Quản trị viên" : "Lịch sử lưu trên thiết bị"}</small>
            </span>
          </button>
          <button
            className="sidebar-logout"
            onClick={isAdmin ? onLogout : onAdminLogin}
            title={isAdmin ? "Đăng xuất" : "Đăng nhập quản trị"}
            aria-label={isAdmin ? "Đăng xuất quản trị" : "Mở đăng nhập quản trị"}
          >
            <NavIcon name={isAdmin ? "logout" : "login"} />
          </button>
        </div>
      </div>
    </aside>
  );
}
