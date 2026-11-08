import { useState } from "react";

function ShieldLogo() {
  return (
    <svg viewBox="0 0 48 48" aria-hidden="true">
      <path d="M24 4 40 10v12c0 10.6-6.5 17.7-16 22-9.5-4.3-16-11.4-16-22V10z" />
      <path d="m17 24 4.5 4.5L31.5 18" />
    </svg>
  );
}

function DetectionVisual({ language }) {
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
        <small>{language === "en" ? "Privileged authentication" : "Xác thực đặc quyền"}</small>
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
  language = "vi",
}) {
  const en = language === "en";
  const [showPassword, setShowPassword] = useState(false);

  return (
    <main className="auth-page admin-auth-page">
      <section className="auth-card" aria-label={en ? "Scam Detector administrator sign in" : "Đăng nhập quản trị Scam Detector"}>
        <aside className="auth-showcase">
          <div className="auth-brand">
            <span className="auth-brand-icon"><ShieldLogo /></span>
            <div>
              <strong>Scam Detector</strong>
              <small>{en ? "AI Safety Platform" : "Nền tảng AI an toàn"}</small>
            </div>
          </div>

          <div className="auth-showcase-copy">
            <span className="auth-live-label"><i /> ADMIN SECURITY GATE</span>
            <h1>{en ? "System administration" : "Khu vực quản trị hệ thống"}</h1>
            <p>
              {en ? "Restricted access for administrators who manage datasets, AI models, evaluations and system logs." : "Quyền truy cập dành riêng cho quản trị viên quản lý dataset, mô hình AI, đánh giá và nhật ký hệ thống."}
            </p>
          </div>

          <DetectionVisual language={language} />

          <div className="auth-showcase-bottom admin-auth-bottom">
            <span>{en ? "Not an administrator?" : "Không phải quản trị viên?"}</span>
            <button type="button" className="auth-outline-button" onClick={onBack}>
              {en ? "Continue without signing in" : "Dùng ngay không đăng nhập"}
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
            <h2>{en ? "Administrator sign in" : "Đăng nhập Admin"}</h2>
            <p>{en ? "Standard users do not need an account to use the system." : "Người dùng thông thường không cần tài khoản để sử dụng hệ thống."}</p>
          </header>

          <div className="admin-auth-notice">
            <span><ShieldLogo /></span>
            <div><strong>{en ? "Administrators only" : "Chỉ dành cho quản trị viên"}</strong><small>{en ? "Every access attempt is authenticated." : "Mọi lần truy cập đều được hệ thống xác thực."}</small></div>
          </div>

          <form onSubmit={onSubmit} className="auth-form admin-auth-form">
            <label className="auth-field">
              <span>{en ? "Administrator email" : "Email quản trị"}</span>
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
              <span>{en ? "Password" : "Mật khẩu"}</span>
              <div>
                <i aria-hidden="true">●</i>
                <input
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  minLength={6}
                  required
                  value={form.password}
                  onChange={(event) => setForm({ ...form, password: event.target.value })}
                  placeholder={en ? "Enter administrator password" : "Nhập mật khẩu quản trị"}
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword((value) => !value)}
                  aria-label={showPassword ? (en ? "Hide password" : "Ẩn mật khẩu") : (en ? "Show password" : "Hiện mật khẩu")}
                >
                  {showPassword ? (en ? "Hide" : "Ẩn") : (en ? "Show" : "Hiện")}
                </button>
              </div>
            </label>

            {authError && <p className="auth-error" role="alert">{authError}</p>}

            <button className="auth-submit" disabled={loading}>
              {loading ? (en ? "Authenticating..." : "Đang xác thực...") : (en ? "Open Admin Console" : "Truy cập Admin Console")}
              <span aria-hidden="true">→</span>
            </button>
          </form>

          <button type="button" className="admin-back-to-guest" onClick={onBack}>
            ← {en ? "Back to guest mode" : "Quay lại chế độ khách"}
          </button>

          <p className="auth-security-note">
            <span>✓</span> {en ? "Administrator sessions are protected by JWT and server-side authorization." : "Phiên quản trị được bảo vệ bằng JWT và phân quyền máy chủ."}
          </p>
        </div>
      </section>
    </main>
  );
}
