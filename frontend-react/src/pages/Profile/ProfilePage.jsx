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

function formatDate(value, fallback = "Chưa ghi nhận") {
  if (!value) return fallback;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return fallback;
  return date.toLocaleDateString("vi-VN", { day: "2-digit", month: "long", year: "numeric" });
}

function riskLabel(level) {
  if (level === "nguy_hiem") return "Nguy hiểm";
  if (level === "nghi_ngo") return "Nghi ngờ";
  return "An toàn";
}

export default function ProfilePage({
  user,
  history = [],
  datasets = [],
  models = [],
  logs = [],
  onUpdateProfile,
}) {
  const [editing, setEditing] = useState(false);
  const [fullName, setFullName] = useState(user.full_name || "");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => setFullName(user.full_name || ""), [user.full_name]);

  const initials = (user.full_name || user.email || "U")
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  const isAdmin = user.role === "admin";

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
  const safeRate = scanStats.total ? Math.round((scanStats.safe / scanStats.total) * 100) : 100;
  const activeModels = models.filter((model) => model.is_active).length;
  const providerName = user.auth_provider === "google" ? "Google" : "Mật khẩu bảo mật";

  const statCards = isAdmin
    ? [
        ["Dataset", datasets.length, "database", "Nguồn dữ liệu"],
        ["AI Models", models.length, "cpu", `${activeModels} đang hoạt động`],
        ["Nhật ký", logs.length, "log", "Hoạt động quản trị"],
        ["Lượt quét", scanStats.total, "scan", "Của tài khoản này"],
      ]
    : [
        ["Đã kiểm tra", scanStats.total, "scan", "Tổng lượt phân tích"],
        ["Kết quả an toàn", scanStats.safe, "shield", `${safeRate}% tổng lượt`],
        ["Cần chú ý", scanStats.suspicious, "activity", "Dấu hiệu nghi ngờ"],
        ["Điểm rủi ro TB", averageRisk, "cpu", "Trên thang 100"],
      ];

  async function handleSave(event) {
    event.preventDefault();
    const normalized = fullName.trim().replace(/\s+/g, " ");
    if (normalized.length < 2) {
      setError("Tên hiển thị phải có ít nhất 2 ký tự.");
      return;
    }
    setSaving(true);
    setError("");
    setMessage("");
    try {
      await onUpdateProfile(normalized);
      setEditing(false);
      setMessage("Hồ sơ đã được cập nhật.");
    } catch (saveError) {
      setError(saveError.message || "Không thể cập nhật hồ sơ.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className={`profile-page ${isAdmin ? "profile-admin" : "profile-user"}`}>
      <section className="profile-identity-hero">
        <div className="profile-tech-grid" aria-hidden="true" />
        <div className="profile-orbit-stage" aria-hidden="true">
          <span className="profile-orbit orbit-a" />
          <span className="profile-orbit orbit-b" />
          <span className="profile-orbit orbit-c" />
          <span className="profile-scan-line" />
          <span className="profile-avatar-large">{initials}</span>
          <i className="profile-orbit-node node-a" />
          <i className="profile-orbit-node node-b" />
          <i className="profile-orbit-node node-c" />
        </div>

        <div className="profile-hero-copy">
          <div className="profile-live-label"><i /> IDENTITY VERIFIED · ONLINE</div>
          <span className="profile-role-chip">{isAdmin ? "ADMIN CLEARANCE" : "MEMBER ACCESS"}</span>
          <h2>{user.full_name || "Người dùng Scam Detector"}</h2>
          <p>{isAdmin
            ? "Trung tâm danh tính quản trị, giám sát AI và điều phối dữ liệu an toàn."
            : "Không gian bảo vệ cá nhân, lưu trữ lịch sử và nhận diện rủi ro bằng AI."}</p>
          <div className="profile-hero-meta">
            <span><Icon name="mail" /> {user.email}</span>
            <span><Icon name="shield" /> Tài khoản đã xác thực</span>
          </div>
        </div>

        <div className="profile-clearance-card">
          <span>ACCESS LEVEL</span>
          <strong>{isAdmin ? "A-01" : "U-01"}</strong>
          <small>{isAdmin ? "TOÀN QUYỀN HỆ THỐNG" : "KHÔNG GIAN CÁ NHÂN"}</small>
          <div className="clearance-bars"><i /><i /><i /><i /><i /></div>
        </div>
      </section>

      <section className="profile-stat-grid" aria-label="Thống kê tài khoản">
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
            <div><span>IDENTITY CORE</span><h3>Thông tin tài khoản</h3></div>
            {!editing && (
              <button className="profile-edit-button" onClick={() => { setEditing(true); setMessage(""); }}>
                <Icon name="edit" /> Chỉnh sửa
              </button>
            )}
          </div>

          {editing ? (
            <form className="profile-edit-form" onSubmit={handleSave}>
              <label>
                <span>Tên hiển thị</span>
                <input value={fullName} onChange={(event) => setFullName(event.target.value)} maxLength="100" autoFocus />
              </label>
              {error && <p className="profile-form-error">{error}</p>}
              <div className="profile-form-actions">
                <button type="button" className="profile-cancel-button" onClick={() => { setEditing(false); setFullName(user.full_name || ""); setError(""); }}>Hủy</button>
                <button type="submit" disabled={saving}>{saving ? "Đang lưu..." : "Lưu thay đổi"}</button>
              </div>
            </form>
          ) : (
            <div className="profile-info-list">
              <div><span className="profile-info-icon"><Icon name="mail" /></span><p><small>Email đăng nhập</small><strong>{user.email}</strong></p><b>VERIFIED</b></div>
              <div><span className="profile-info-icon"><Icon name="key" /></span><p><small>Phương thức xác thực</small><strong>{providerName}</strong></p><b>SECURE</b></div>
              <div><span className="profile-info-icon"><Icon name="calendar" /></span><p><small>Thành viên từ</small><strong>{formatDate(user.created_at)}</strong></p><b>ACTIVE</b></div>
              <div><span className="profile-info-icon"><Icon name="shield" /></span><p><small>Vai trò hệ thống</small><strong>{isAdmin ? "Quản trị viên" : "Người dùng"}</strong></p><b>{isAdmin ? "ADMIN" : "USER"}</b></div>
            </div>
          )}
          {message && <p className="profile-form-success">{message}</p>}
        </section>

        <section className="profile-panel profile-security-panel">
          <div className="profile-panel-heading">
            <div><span>SECURITY STATUS</span><h3>Lá chắn tài khoản</h3></div>
            <span className="profile-secure-dot">Bảo vệ</span>
          </div>
          <div className="profile-security-visual">
            <div className="security-ring" style={{ "--security": user.auth_provider === "google" ? "100" : "92" }}>
              <div><Icon name="shield" /><strong>{user.auth_provider === "google" ? "100" : "92"}%</strong><small>Độ tin cậy</small></div>
            </div>
          </div>
          <ul className="profile-security-list">
            <li><i /> Phiên đăng nhập được mã hóa</li>
            <li><i /> Email định danh duy nhất</li>
            <li><i /> Dữ liệu kiểm tra tách biệt theo tài khoản</li>
          </ul>
        </section>

        <section className="profile-panel profile-activity-panel">
          <div className="profile-panel-heading">
            <div><span>LIVE TRACE</span><h3>Hoạt động gần đây</h3></div>
            <span className="profile-record-count">{history.length} bản ghi</span>
          </div>
          {history.length ? (
            <div className="profile-timeline">
              {history.slice(0, 5).map((item) => (
                <div className="profile-timeline-item" key={item.id}>
                  <span className={`timeline-node risk-${item.risk_level}`}><Icon name="scan" /></span>
                  <div>
                    <strong>{item.original_filename || `Lượt kiểm tra #${item.id}`}</strong>
                    <small>{formatDate(item.created_at, "Vừa hoàn tất")}</small>
                  </div>
                  <span className={`profile-risk-pill ${item.risk_level}`}>{riskLabel(item.risk_level)}</span>
                  <b>{item.risk_score}</b>
                </div>
              ))}
            </div>
          ) : (
            <div className="profile-empty-activity"><Icon name="activity" /><strong>Chưa có hoạt động</strong><span>Các lượt phân tích mới sẽ xuất hiện tại đây.</span></div>
          )}
        </section>

        <section className="profile-panel profile-permission-panel">
          <div className="profile-panel-heading">
            <div><span>{isAdmin ? "ADMIN MATRIX" : "ACCESS MATRIX"}</span><h3>Quyền truy cập</h3></div>
          </div>
          <div className="profile-permission-map">
            <span className="permission-core">{isAdmin ? "ADMIN" : "USER"}<i /></span>
            {(isAdmin
              ? ["Dataset", "AI Models", "Đánh giá", "Nhật ký"]
              : ["Kiểm tra OCR", "Phân tích URL", "Lịch sử riêng", "Cảnh báo AI"]
            ).map((permission, index) => (
              <div className={`permission-node permission-${index + 1}`} key={permission}><i />{permission}<b>ON</b></div>
            ))}
          </div>
          <p>{isAdmin
            ? "Tài khoản có quyền cấu hình dữ liệu, mô hình và theo dõi hoạt động quản trị."
            : "Tài khoản chỉ truy cập dữ liệu phân tích của chính bạn; lịch sử được bảo vệ độc lập."}</p>
        </section>
      </div>
    </div>
  );
}
