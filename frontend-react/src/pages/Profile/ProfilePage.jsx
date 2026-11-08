import { useEffect, useMemo, useState } from "react";

const iconPaths = {
  edit: ["M12 20h9", "M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z"],
  mail: ["M4 5h16v14H4z", "m4 7 8 6 8-6"],
  shield: ["M12 3 5 6v5c0 5 3 8 7 10 4-2 7-5 7-10V6Z", "m9 12 2 2 4-5"],
  calendar: ["M5 4h14a2 2 0 0 1 2 2v14H3V6a2 2 0 0 1 2-2Z", "M8 2v4", "M16 2v4", "M3 9h18"],
  key: ["M15 7a4 4 0 1 0-7 2.6L3 15v4h4v-3h3v-3h2.4A4 4 0 0 0 15 7Z"],
  activity: ["M3 12h4l2-6 4 12 2-6h6"],
  database: ["M4 6c0-1 3.6-2 8-2s8 1 8 2-3.6 2-8 2-8-1-8-2Z", "M4 6v6c0 1 3.6 2 8 2s8-1 8-2V6", "M4 12v6c0 1 3.6 2 8 2s8-1 8-2v-6"],
  cpu: ["M8 8h8v8H8z", "M9 2v3", "M15 2v3", "M9 19v3", "M15 19v3", "M2 9h3", "M2 15h3", "M19 9h3", "M19 15h3"],
  scan: ["M4 8V5a1 1 0 0 1 1-1h3", "M16 4h3a1 1 0 0 1 1 1v3", "M20 16v3a1 1 0 0 1-1 1h-3", "M8 20H5a1 1 0 0 1-1-1v-3", "M8 12h8"],
  log: ["M6 3h8l4 4v14H6z", "M14 3v5h5", "M9 13h6", "M9 17h6"],
};

function Icon({ name }) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      {iconPaths[name].map((path) => <path key={path} d={path} />)}
    </svg>
  );
}

function formatDate(value, fallback = "Chưa ghi nhận", language = "vi") {
  if (!value) return fallback;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return fallback;
  return date.toLocaleDateString(language === "en" ? "en-US" : "vi-VN", { day: "2-digit", month: "long", year: "numeric" });
}

function riskLabel(level, language) {
  if (level === "nguy_hiem") return language === "en" ? "Dangerous" : "Nguy hiểm";
  if (level === "nghi_ngo") return language === "en" ? "Suspicious" : "Nghi ngờ";
  return language === "en" ? "Safe" : "An toàn";
}

export default function ProfilePage({
  user,
  history = [],
  datasets = [],
  models = [],
  logs = [],
  onUpdateProfile,
  language = "vi",
}) {
  const en = language === "en";
  const [editing, setEditing] = useState(false);
  const [fullName, setFullName] = useState(user.full_name || "");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const displayName = en && user.full_name === "Người dùng khách" ? "Guest user" : user.full_name;

  useEffect(() => setFullName(user.full_name || ""), [user.full_name]);

  const initials = (displayName || user.email || "U")
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  const isAdmin = user.role === "admin";
  const isGuest = user.role === "guest";

  const scanStats = useMemo(() => history.reduce(
    (stats, item) => {
      stats.total += 1;
      stats.score += Number(item.risk_score || 0);
      if (item.risk_level === "an_toan") stats.safe += 1;
      if (item.risk_level === "nghi_ngo") stats.suspicious += 1;
      if (item.risk_level === "nguy_hiem") stats.danger += 1;
      return stats;
    },
    { total: 0, safe: 0, suspicious: 0, danger: 0, score: 0 },
  ), [history]);

  const averageRisk = scanStats.total ? Math.round(scanStats.score / scanStats.total) : 0;
  const safeRate = scanStats.total ? Math.round((scanStats.safe / scanStats.total) * 100) : 0;
  const activeModels = models.filter((model) => model.is_active).length;
  const providerName = isGuest
    ? (en ? "Stored privately in this browser" : "Lưu riêng trên trình duyệt")
    : user.auth_provider === "google" ? "Google" : (en ? "Secure password" : "Mật khẩu bảo mật");

  const statCards = isAdmin
    ? [
        ["Dataset", datasets.length, "database", en ? "Data sources" : "Nguồn dữ liệu"],
        ["AI Models", models.length, "cpu", en ? `${activeModels} active` : `${activeModels} đang hoạt động`],
        [en ? "Logs" : "Nhật ký", logs.length, "log", en ? "Admin activity" : "Hoạt động quản trị"],
        [en ? "Checks" : "Lượt quét", scanStats.total, "scan", en ? "From this account" : "Của tài khoản này"],
      ]
    : [
        [en ? "Checked" : "Đã kiểm tra", scanStats.total, "scan", en ? "Total analyses" : "Tổng lượt phân tích"],
        [en ? "Safe results" : "Kết quả an toàn", scanStats.safe, "shield", en ? `${safeRate}% of all checks` : `${safeRate}% tổng lượt`],
        [en ? "Needs attention" : "Cần chú ý", scanStats.suspicious, "activity", en ? "Suspicious signals" : "Dấu hiệu nghi ngờ"],
        [en ? "Average risk" : "Điểm rủi ro TB", averageRisk, "cpu", en ? "Out of 100" : "Trên thang 100"],
      ];

  async function handleSave(event) {
    event.preventDefault();
    const normalized = fullName.trim().replace(/\s+/g, " ");
    if (normalized.length < 2) {
      setError(en ? "Display name must contain at least 2 characters." : "Tên hiển thị phải có ít nhất 2 ký tự.");
      return;
    }
    setSaving(true);
    setError("");
    setMessage("");
    try {
      await onUpdateProfile(normalized);
      setEditing(false);
      setMessage(en ? "Profile updated." : "Hồ sơ đã được cập nhật.");
    } catch (saveError) {
      setError(saveError.message || (en ? "Unable to update profile." : "Không thể cập nhật hồ sơ."));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className={`profile-page ${isAdmin ? "profile-admin" : "profile-user"}`}>
      <section className="profile-identity-hero">
        <div className="profile-simple-avatar" aria-hidden="true">
          <span className="profile-avatar-large">{initials}</span>
        </div>

        <div className="profile-hero-copy">
          <div className="profile-live-label"><i /> {isGuest ? (en ? "Profile stored on this device" : "Hồ sơ đang lưu trên thiết bị") : (en ? "Verified account" : "Tài khoản đã xác thực")}</div>
          <span className="profile-role-chip">{isAdmin ? (en ? "Administrator" : "Quản trị viên") : (en ? "No sign-in required" : "Không cần đăng nhập")}</span>
          <h2>{displayName || (en ? "Scam Detector user" : "Người dùng Scam Detector")}</h2>
          <p>{isAdmin
            ? (en ? "Manage account information and monitor system activity." : "Quản lý thông tin tài khoản và theo dõi hoạt động hệ thống.")
            : (en ? "No account required. Analysis history stays private in this device's browser." : "Không cần tài khoản. Lịch sử phân tích được giữ riêng trên trình duyệt của thiết bị này.")}</p>
          <div className="profile-hero-meta">
            <span><Icon name="mail" /> {isGuest ? (en ? "No email required" : "Không yêu cầu email") : user.email}</span>
            <span><Icon name="shield" /> {isGuest ? (en ? "Local data is active" : "Dữ liệu cục bộ đang hoạt động") : (en ? "Verified account" : "Tài khoản đã xác thực")}</span>
          </div>
        </div>

      </section>

      <section className="profile-stat-grid" aria-label={en ? "Account statistics" : "Thống kê tài khoản"}>
        {statCards.map(([label, value, icon, note], index) => (
          <article className="profile-stat-card" key={label} style={{ "--delay": `${index * 80}ms` }}>
            <span className="profile-stat-icon"><Icon name={icon} /></span>
            <div><small>{label}</small><strong>{value}</strong><span>{note}</span></div>
            <i className="profile-stat-signal" />
          </article>
        ))}
      </section>

      <div className="profile-content-grid">
        <section className="profile-panel profile-account-panel">
          <div className="profile-panel-heading">
            <div><span>{en ? "YOUR INFORMATION" : "THÔNG TIN CỦA BẠN"}</span><h3>{en ? "Account information" : "Thông tin tài khoản"}</h3></div>
            {!editing && (
              <button className="profile-edit-button" onClick={() => { setEditing(true); setMessage(""); }}>
                <Icon name="edit" /> {en ? "Edit" : "Chỉnh sửa"}
              </button>
            )}
          </div>

          {editing ? (
            <form className="profile-edit-form" onSubmit={handleSave}>
              <label>
                <span>{en ? "Display name" : "Tên hiển thị"}</span>
                <input value={fullName} onChange={(event) => setFullName(event.target.value)} maxLength="100" autoFocus />
              </label>
              {error && <p className="profile-form-error">{error}</p>}
              <div className="profile-form-actions">
                <button type="button" className="profile-cancel-button" onClick={() => { setEditing(false); setFullName(user.full_name || ""); setError(""); }}>{en ? "Cancel" : "Hủy"}</button>
                <button type="submit" disabled={saving}>{saving ? (en ? "Saving..." : "Đang lưu...") : (en ? "Save changes" : "Lưu thay đổi")}</button>
              </div>
            </form>
          ) : (
            <div className="profile-info-list">
              <div><span className="profile-info-icon"><Icon name="mail" /></span><p><small>{isGuest ? (en ? "Sign in" : "Đăng nhập") : (en ? "Sign-in email" : "Email đăng nhập")}</small><strong>{isGuest ? (en ? "No sign-in or registration required" : "Không yêu cầu đăng nhập hoặc đăng ký") : user.email}</strong></p><b>{isGuest ? (en ? "Not needed" : "Không cần") : (en ? "Verified" : "Đã xác minh")}</b></div>
              <div><span className="profile-info-icon"><Icon name="key" /></span><p><small>{en ? "Data protection" : "Cách bảo vệ dữ liệu"}</small><strong>{providerName}</strong></p><b>{en ? "Secure" : "An toàn"}</b></div>
              <div><span className="profile-info-icon"><Icon name="calendar" /></span><p><small>{isGuest ? (en ? "Started storing on device" : "Bắt đầu lưu trên thiết bị") : (en ? "Member since" : "Thành viên từ")}</small><strong>{formatDate(user.created_at, en ? "Not recorded" : "Chưa ghi nhận", language)}</strong></p><b>{en ? "Active" : "Đang dùng"}</b></div>
              <div><span className="profile-info-icon"><Icon name="shield" /></span><p><small>{en ? "Access level" : "Quyền sử dụng"}</small><strong>{isAdmin ? (en ? "Administrator" : "Quản trị viên") : (en ? "Standard user" : "Người dùng thông thường")}</strong></p><b>{isAdmin ? (en ? "Admin" : "Quản trị") : (en ? "Basic" : "Cơ bản")}</b></div>
            </div>
          )}
          {message && <p className="profile-form-success">{message}</p>}
        </section>

        <section className="profile-panel profile-security-panel">
          <div className="profile-panel-heading">
            <div><span>{en ? "PRIVACY" : "QUYỀN RIÊNG TƯ"}</span><h3>{en ? "Your data is protected" : "Dữ liệu của bạn được bảo vệ"}</h3></div>
            <span className="profile-secure-dot">{en ? "Protected" : "Bảo vệ"}</span>
          </div>
          <div className="profile-security-visual">
            <div className="security-ring" style={{ "--security": user.auth_provider === "google" ? "100" : isGuest ? "95" : "92" }}>
              <div><Icon name="shield" /><strong>{user.auth_provider === "google" ? "100" : isGuest ? "95" : "92"}%</strong><small>{en ? "Trust score" : "Độ tin cậy"}</small></div>
            </div>
          </div>
          <ul className="profile-security-list">
            <li><i /> {isGuest ? (en ? "No email or password is collected" : "Không thu thập email hoặc mật khẩu") : (en ? "Encrypted sign-in session" : "Phiên đăng nhập được mã hóa")}</li>
            <li><i /> {isGuest ? (en ? "History stays in this browser" : "Lịch sử lưu trên trình duyệt hiện tại") : (en ? "Unique identity email" : "Email định danh duy nhất")}</li>
            <li><i /> {isGuest ? (en ? "No user account is created on the server" : "Không tạo tài khoản người dùng trên máy chủ") : (en ? "Check data is separated by account" : "Dữ liệu kiểm tra tách biệt theo tài khoản")}</li>
          </ul>
        </section>

        <section className="profile-panel profile-activity-panel">
          <div className="profile-panel-heading">
            <div><span>{en ? "RECENT HISTORY" : "LỊCH SỬ GẦN ĐÂY"}</span><h3>{en ? "Recent activity" : "Hoạt động gần đây"}</h3></div>
            <span className="profile-record-count">{history.length} {en ? "records" : "bản ghi"}</span>
          </div>
          {history.length ? (
            <div className="profile-timeline">
              {history.slice(0, 5).map((item) => (
                <div className="profile-timeline-item" key={item.id}>
                  <span className={`timeline-node risk-${item.risk_level}`}><Icon name="scan" /></span>
                  <div>
                    <strong>{item.original_filename || `${en ? "Check" : "Lượt kiểm tra"} #${item.id}`}</strong>
                    <small>{formatDate(item.created_at, en ? "Just completed" : "Vừa hoàn tất", language)}</small>
                  </div>
                  <span className={`profile-risk-pill ${item.risk_level}`}>{riskLabel(item.risk_level, language)}</span>
                  <b>{item.risk_score}</b>
                </div>
              ))}
            </div>
          ) : (
            <div className="profile-empty-activity"><Icon name="activity" /><strong>{en ? "No activity yet" : "Chưa có hoạt động"}</strong><span>{en ? "New analyses will appear here." : "Các lượt phân tích mới sẽ xuất hiện tại đây."}</span></div>
          )}
        </section>

        {isAdmin && <section className="profile-panel profile-permission-panel">
          <div className="profile-panel-heading">
            <div><span>{en ? "ADMIN PERMISSIONS" : "QUYỀN QUẢN TRỊ"}</span><h3>{en ? "Access permissions" : "Quyền truy cập"}</h3></div>
          </div>
          <div className="profile-permission-map">
            <span className="permission-core">{en ? "Admin" : "Quản trị"}<i /></span>
            {["Dataset", "AI Models", en ? "Evaluations" : "Đánh giá", en ? "Logs" : "Nhật ký"].map((permission, index) => (
              <div className={`permission-node permission-${index + 1}`} key={permission}><i />{permission}<b>{en ? "On" : "Bật"}</b></div>
            ))}
          </div>
          <p>{en ? "This account can configure data and models and monitor administrative activity." : "Tài khoản có quyền cấu hình dữ liệu, mô hình và theo dõi hoạt động quản trị."}</p>
        </section>}
      </div>
    </div>
  );
}
