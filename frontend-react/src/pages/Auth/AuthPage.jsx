import { useState } from "react";

function ShieldLogo() {
  return (
    <svg viewBox="0 0 48 48" aria-hidden="true">
      <path d="M24 4 40 10v12c0 10.6-6.5 17.7-16 22-9.5-4.3-16-11.4-16-22V10z" />
      <path d="m17 24 4.5 4.5L31.5 18" />
    </svg>
  );
}

function DetectionVisual() {
  return (
    <div className="auth-detection" aria-hidden="true">
      <div className="auth-tech-grid" />
      <div className="auth-scan-beam" />
      <div className="auth-orbit auth-orbit-one" />
      <div className="auth-orbit auth-orbit-two" />
      <span className="auth-data-node node-one">DB</span>
      <span className="auth-data-node node-two">LOG</span>
      <span className="auth-data-node node-three">AI</span>
      <div className="auth-detect-core">
        <ShieldLogo />
        <strong>ADMIN GATE</strong>
        <small>Xác thực đặc quyền</small>
      </div>
      <span className="auth-signal signal-one" />
      <span className="auth-signal signal-two" />
      <span className="auth-signal signal-three" />
    </div>
  );
}

export default function AuthPage({
  form,
  setForm,
  loading,
  authError,
  onSubmit,
  onBack,
}) {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <main className="auth-page admin-auth-page">
      <section className="auth-card" aria-label="Đăng nhập quản trị Scam Detector">
        <aside className="auth-showcase">
          <div className="auth-brand">
            <span className="auth-brand-icon"><ShieldLogo /></span>
            <div>
              <strong>Scam Detector</strong>
              <small>Vietnamese AI Safety</small>
            </div>
          </div>

          <div className="auth-showcase-copy">
            <span className="auth-live-label"><i /> ADMIN SECURITY GATE</span>
            <h1>Khu vực quản trị hệ thống</h1>
            <p>
              Quyền truy cập dành riêng cho quản trị viên quản lý dataset,
              mô hình AI, đánh giá và nhật ký hệ thống.
            </p>
          </div>

          <DetectionVisual />

          <div className="auth-showcase-bottom admin-auth-bottom">
            <span>Không phải quản trị viên?</span>
            <button type="button" className="auth-outline-button" onClick={onBack}>
              Dùng ngay không đăng nhập
            </button>
          </div>
        </aside>

        <div className="auth-form-panel">
          <div className="auth-mobile-brand">
            <span className="auth-brand-icon"><ShieldLogo /></span>
            <strong>Scam Detector</strong>
          </div>

          <header className="auth-form-heading">
            <span className="auth-form-kicker">RESTRICTED ACCESS</span>
            <h2>Đăng nhập Admin</h2>
            <p>Người dùng thông thường không cần tài khoản để sử dụng hệ thống.</p>
          </header>

          <div className="admin-auth-notice">
            <span><ShieldLogo /></span>
            <div><strong>Chỉ dành cho quản trị viên</strong><small>Mọi lần truy cập đều được hệ thống xác thực.</small></div>
          </div>

          <form onSubmit={onSubmit} className="auth-form admin-auth-form">
            <label className="auth-field">
              <span>Email quản trị</span>
              <div>
                <i aria-hidden="true">@</i>
                <input
                  type="email"
                  autoComplete="username"
                  required
                  value={form.email}
                  onChange={(event) => setForm({ ...form, email: event.target.value })}
                  placeholder="admin@example.com"
                />
              </div>
            </label>

            <label className="auth-field">
              <span>Mật khẩu</span>
              <div>
                <i aria-hidden="true">●</i>
                <input
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  minLength={6}
                  required
                  value={form.password}
                  onChange={(event) => setForm({ ...form, password: event.target.value })}
                  placeholder="Nhập mật khẩu quản trị"
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword((value) => !value)}
                  aria-label={showPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
                >
                  {showPassword ? "Ẩn" : "Hiện"}
                </button>
              </div>
            </label>

            {authError && <p className="auth-error" role="alert">{authError}</p>}

            <button className="auth-submit" disabled={loading}>
              {loading ? "Đang xác thực..." : "Truy cập Admin Console"}
              <span aria-hidden="true">→</span>
            </button>
          </form>

          <button type="button" className="admin-back-to-guest" onClick={onBack}>
            ← Quay lại chế độ khách
          </button>

          <p className="auth-security-note">
            <span>✓</span> Phiên quản trị được bảo vệ bằng JWT và phân quyền máy chủ.
          </p>
        </div>
      </section>
    </main>
  );
}
