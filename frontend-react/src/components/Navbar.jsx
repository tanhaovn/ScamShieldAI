import { useState } from "react";

const primaryItems = [
  { page: "overview", vi: "Tổng quan", en: "Overview", icon: "dashboard" },
  { page: "scan", vi: "Kiểm tra lừa đảo", en: "Scam check", icon: "scan" },
  { page: "statistics", vi: "Thống kê", en: "Statistics", icon: "chart" },
  { page: "history", vi: "Lịch sử", en: "History", icon: "history" },
  { page: "profile", vi: "Cá nhân", en: "Profile", icon: "user" },
];

const adminItems = [
  { page: "admin-dataset", vi: "Dữ liệu", en: "Dataset", icon: "database" },
  { page: "admin-models", vi: "Mô hình AI", en: "AI Models", icon: "model" },
  { page: "admin-evaluations", vi: "Đánh giá", en: "Evaluations", icon: "chart" },
  { page: "admin-keywords", vi: "Từ khóa", en: "Keywords", icon: "keyword" },
  { page: "admin-feedback", vi: "Phản hồi", en: "Feedback", icon: "message" },
  { page: "admin-devices", vi: "Thiết bị", en: "Devices", icon: "location" },
  { page: "admin-logs", vi: "Nhật ký", en: "Logs", icon: "file" },
];

const iconPaths = {
  dashboard: ["M4 4h6v6H4z", "M14 4h6v6h-6z", "M4 14h6v6H4z", "M14 14h6v6h-6z"],
  scan: ["M4 8V5a1 1 0 0 1 1-1h3", "M16 4h3a1 1 0 0 1 1 1v3", "M20 16v3a1 1 0 0 1-1 1h-3", "M8 20H5a1 1 0 0 1-1-1v-3", "M8 12h8"],
  history: ["M3 12a9 9 0 1 0 3-6.7", "M3 4v5h5", "M12 7v5l3 2"],
  database: ["M4 6c0-1.1 3.6-2 8-2s8 .9 8 2-3.6 2-8 2-8-.9-8-2Z", "M4 6v6c0 1.1 3.6 2 8 2s8-.9 8-2V6", "M4 12v6c0 1.1 3.6 2 8 2s8-.9 8-2v-6"],
  model: ["M12 3 4 7v10l8 4 8-4V7z", "m4 7 8 4 8-4", "M12 11v10"],
  chart: ["M5 20V10", "M12 20V4", "M19 20v-7", "M3 20h18"],
  keyword: ["M4 5h16v4H4z", "M4 13h10v4H4z", "M17 13h3v4h-3z"],
  message: ["M4 5h16v12H8l-4 4z", "M8 9h8", "M8 13h5"],
  location: ["M12 21s7-6.1 7-12a7 7 0 1 0-14 0c0 5.9 7 12 7 12Z", "M12 12a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"],
  file: ["M6 3h8l4 4v14H6z", "M14 3v5h5", "M9 13h6", "M9 17h6"],
  logout: ["M10 17l5-5-5-5", "M15 12H3", "M15 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4"],
  login: ["m14 7 5 5-5 5", "M19 12H7", "M9 4H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4"],
  user: ["M20 21a8 8 0 0 0-16 0", "M12 13a5 5 0 1 0 0-10 5 5 0 0 0 0 10Z"],
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

function NavGroup({ label, items, activePage, navigate, language, mobileAction }) {
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
            <span>{item[language] || item.vi}</span>
          </button>
        ))}
        {mobileAction && (
          <button
            className={`sidebar-nav-item mobile-admin-access ${mobileAction.active ? "active" : ""}`}
            onClick={mobileAction.onClick}
          >
            <NavIcon name={mobileAction.icon} />
            <span>{mobileAction.label}</span>
          </button>
        )}
      </nav>
    </section>
  );
}

export default function Navbar({ activePage, navigate, user, onLogout, onLogin, onAdminLogin, language = "vi" }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const isAdmin = user.role === "admin";
  const isAdminLayout = activePage.startsWith("admin-");
  const isSignedIn = user.role !== "guest";
  const isEnglish = language === "en";
  const displayName = isEnglish && user.full_name === "Người dùng khách" ? "Guest user" : user.full_name;
  const initials = (displayName || user.email || "U")
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const goTo = (page) => {
    setMobileOpen(false);
    navigate(page);
  };

  if (!isAdminLayout) {
    return (
      <header className="site-header">
        <div className="site-header-inner">
          <button className="site-brand" onClick={() => goTo("overview")} aria-label={isEnglish ? "Scam Detector home" : "Trang chủ Scam Detector"}>
            <span className="site-brand-mark" aria-hidden="true">
              <svg viewBox="0 0 32 32"><path d="M16 3 6 7v7c0 7.2 4.1 12.1 10 15 5.9-2.9 10-7.8 10-15V7Z" /><path d="m11.5 16 3 3 6.5-8" /></svg>
            </span>
            <span><strong>Scam Detector</strong><small>{isEnglish ? "Digital safety platform" : "Nền tảng an toàn số"}</small></span>
          </button>

          <nav className="site-nav" aria-label={isEnglish ? "Main navigation" : "Điều hướng chính"}>
            {primaryItems.map((item) => (
              <button key={item.page} className={activePage === item.page ? "active" : ""} onClick={() => goTo(item.page)}>
                {item[language] || item.vi}
              </button>
            ))}
          </nav>

          <div className="site-header-actions">
            <button className="site-live-pill" type="button" onClick={() => goTo("scan")}><i />{isEnglish ? "Detector live" : "Bộ quét trực tuyến"}</button>
            {isAdmin && <button className="site-admin-link" onClick={() => goTo("admin-dataset")}>{isEnglish ? "Admin" : "Quản trị"}</button>}
            <button className="site-primary-action" onClick={() => goTo("scan")}>{isEnglish ? "Check now" : "Kiểm tra ngay"}</button>
            <button className="site-account-button" onClick={isSignedIn ? () => goTo("profile") : onLogin} title={displayName}>
              <span>{initials}</span><b>{isSignedIn ? displayName : (isEnglish ? "Sign in" : "Đăng nhập")}</b>
            </button>
            {isSignedIn && <button className="site-logout-button" onClick={onLogout} aria-label={isEnglish ? "Sign out" : "Đăng xuất"}><NavIcon name="logout" /></button>}
            <button className="site-menu-toggle" type="button" aria-expanded={mobileOpen} aria-label={isEnglish ? "Toggle navigation" : "Mở menu"} onClick={() => setMobileOpen((value) => !value)}>
              <span /><span /><span />
            </button>
          </div>
        </div>

        <div className={`site-mobile-menu ${mobileOpen ? "open" : ""}`}>
          {primaryItems.map((item) => <button key={item.page} className={activePage === item.page ? "active" : ""} onClick={() => goTo(item.page)}><NavIcon name={item.icon} />{item[language] || item.vi}</button>)}
          {isAdmin && <button onClick={() => goTo("admin-dataset")}><NavIcon name="database" />{isEnglish ? "Administration" : "Quản trị hệ thống"}</button>}
          {!isSignedIn && <button onClick={() => { setMobileOpen(false); onLogin(); }}><NavIcon name="login" />{isEnglish ? "Sign in / Register" : "Đăng nhập / Đăng ký"}</button>}
        </div>
      </header>
    );
  }

  return (
    <aside className="app-sidebar admin-navigation">
      <button className="sidebar-brand" onClick={() => goTo("overview")}>
        <span className="sidebar-logo" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M12 3 5 6v5c0 5 3 8 7 10 4-2 7-5 7-10V6Z" /><path d="m9 12 2 2 4-5" /></svg>
        </span>
        <span>
          <strong>Scam Detector</strong>
          <small>{isEnglish ? "Digital safety assistant" : "Trợ lý an toàn số"}</small>
        </span>
      </button>

      <div className="sidebar-navigation">
        <NavGroup
          label={isEnglish ? "Main menu" : "Menu chính"}
          items={primaryItems}
          activePage={activePage}
          navigate={goTo}
          language={language}
          mobileAction={{
            label: isAdmin ? (isEnglish ? "Admin" : "Quản trị") : "Admin",
            icon: isAdmin ? "database" : "login",
            active: activePage.startsWith("admin-"),
            onClick: isAdmin ? () => goTo("admin-dataset") : onAdminLogin,
          }}
        />
        {isAdmin && (
          <NavGroup
            label={isEnglish ? "Administration" : "Quản trị hệ thống"}
            items={adminItems}
            activePage={activePage}
            navigate={goTo}
            language={language}
          />
        )}
      </div>

      <div className="sidebar-bottom">
        <button className="sidebar-new-scan" onClick={() => goTo("scan")}>
          <span>+</span> {isEnglish ? "New check" : "Tạo lượt kiểm tra"}
        </button>
        {!isSignedIn && (
          <button className="sidebar-new-scan sidebar-login-button" onClick={onLogin}>
            <NavIcon name="login" /> {isEnglish ? "Sign in / Register" : "Đăng nhập / Đăng ký"}
          </button>
        )}
        <div className={`sidebar-user${activePage === "profile" ? " active" : ""}`}>
          <button
            className="sidebar-user-profile"
            onClick={() => goTo("profile")}
            title={isEnglish ? "Open profile" : "Mở trang cá nhân"}
            aria-label={`${isEnglish ? "Open profile for" : "Mở trang cá nhân của"} ${displayName || user.email}`}
          >
            <span className="user-avatar">{initials}</span>
            <span className="sidebar-user-copy">
              <strong>{displayName || (isEnglish ? "User" : "Người dùng")}</strong>
              <small>{isAdmin ? (isEnglish ? "Administrator" : "Quản trị viên") : isSignedIn ? (isEnglish ? "Account history synced" : "Lịch sử đã đồng bộ") : (isEnglish ? "History saved on device" : "Lịch sử lưu trên thiết bị")}</small>
            </span>
          </button>
          <button
            className="sidebar-logout"
            onClick={isSignedIn ? onLogout : onLogin}
            title={isSignedIn ? (isEnglish ? "Sign out" : "Đăng xuất") : (isEnglish ? "Sign in" : "Đăng nhập")}
            aria-label={isSignedIn ? (isEnglish ? "Sign out" : "Đăng xuất") : (isEnglish ? "Open sign in" : "Mở đăng nhập")}
          >
            <NavIcon name={isSignedIn ? "logout" : "login"} />
          </button>
        </div>
      </div>
    </aside>
  );
}
