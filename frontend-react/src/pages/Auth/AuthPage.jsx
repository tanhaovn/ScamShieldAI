import { useState } from "react";

function ShieldLogo() {
  return (
    <svg viewBox="0 0 48 48" aria-hidden="true">
      <path d="M24 4 40 10v12c0 10.6-6.5 17.7-16 22-9.5-4.3-16-11.4-16-22V10z" />
      <path d="m17 24 4.5 4.5L31.5 18" />
    </svg>
  );
}

function DetectionVisual({ adminMode, language }) {
  const en = language === "en";
  return (
    <div className="auth-detection" aria-hidden="true">
      <div className="auth-tech-grid" /><div className="auth-scan-beam" />
      <div className="auth-orbit auth-orbit-one" /><div className="auth-orbit auth-orbit-two" />
      <span className="auth-data-node node-one">DB</span><span className="auth-data-node node-two">LOG</span><span className="auth-data-node node-three">AI</span>
      <div className="auth-detect-core">
        <ShieldLogo />
        <strong>{adminMode ? "ADMIN GATE" : "USER ACCOUNT"}</strong>
        <small>{adminMode ? (en ? "Privileged authentication" : "Xác thực quản trị") : (en ? "Synced check history" : "Đồng bộ lịch sử kiểm tra")}</small>
      </div>
    </div>
  );
}

export default function AuthPage({ form, setForm, loading, authError, authMode, setAuthMode, adminMode = false, onSubmit, onBack, onAdminLogin, language = "vi" }) {
  const en = language === "en";
  const registering = !adminMode && authMode === "register";
  const [showPassword, setShowPassword] = useState(false);

  return (
    <main className="auth-page admin-auth-page">
      <section className="auth-card" aria-label={adminMode ? (en ? "Administrator sign in" : "Đăng nhập quản trị") : (en ? "User account" : "Tài khoản người dùng")}>
        <aside className="auth-showcase">
          <div className="auth-brand"><span className="auth-brand-icon"><ShieldLogo /></span><div><strong>Scam Detector</strong><small>{en ? "AI Safety Platform" : "Nền tảng AI an toàn"}</small></div></div>
          <div className="auth-showcase-copy">
            <span className="auth-live-label"><i /> {adminMode ? "ADMIN SECURITY GATE" : "PERSONAL SAFETY ACCOUNT"}</span>
            <h1>{adminMode ? (en ? "System administration" : "Khu vực quản trị hệ thống") : (en ? "Keep your checks with you" : "Lưu lịch sử kiểm tra theo tài khoản")}</h1>
            <p>{adminMode ? (en ? "Restricted access for system administrators." : "Quyền truy cập dành riêng cho quản trị viên hệ thống.") : (en ? "Sign in to access your check history. You can still continue as a guest." : "Đăng nhập để lưu và xem lại lịch sử kiểm tra. Bạn vẫn có thể tiếp tục với tài khoản khách.")}</p>
          </div>
          <DetectionVisual adminMode={adminMode} language={language} />
          <div className="auth-showcase-bottom admin-auth-bottom"><span>{en ? "Want to continue without an account?" : "Muốn tiếp tục mà không cần tài khoản?"}</span><button type="button" className="auth-outline-button" onClick={onBack}>{en ? "Continue as guest" : "Tiếp tục với tài khoản khách"}</button></div>
        </aside>

        <div className="auth-form-panel">
          <header className="auth-form-heading">
            <span className="auth-form-kicker">{adminMode ? "RESTRICTED ACCESS" : "PERSONAL ACCOUNT"}</span>
            <h2>{adminMode ? (en ? "Administrator sign in" : "Đăng nhập Admin") : registering ? (en ? "Create an account" : "Tạo tài khoản") : (en ? "Sign in" : "Đăng nhập")}</h2>
            <p>{adminMode ? (en ? "Use an administrator account." : "Sử dụng tài khoản có quyền quản trị.") : (en ? "Saved checks are private to your account." : "Lịch sử kiểm tra được lưu riêng theo tài khoản của bạn.")}</p>
          </header>

          {!adminMode && <div className="auth-mode-tabs" role="tablist"><button type="button" className={!registering ? "active" : ""} onClick={() => setAuthMode("login")}>{en ? "Sign in" : "Đăng nhập"}</button><button type="button" className={registering ? "active" : ""} onClick={() => setAuthMode("register")}>{en ? "Register" : "Đăng ký"}</button></div>}

          <form onSubmit={onSubmit} className="auth-form admin-auth-form">
            {registering && <label className="auth-field"><span>{en ? "Full name" : "Họ và tên"}</span><div><i aria-hidden="true">ID</i><input type="text" autoComplete="name" minLength={2} required value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} placeholder={en ? "Your full name" : "Nhập họ và tên"} /></div></label>}
            <label className="auth-field"><span>Email</span><div><i aria-hidden="true">@</i><input type="email" autoComplete="email" required value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} placeholder="you@example.com" /></div></label>
            <label className="auth-field"><span>{en ? "Password" : "Mật khẩu"}</span><div><i aria-hidden="true">●</i><input type={showPassword ? "text" : "password"} autoComplete={registering ? "new-password" : "current-password"} minLength={registering ? 8 : 6} required value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} placeholder={registering ? (en ? "At least 8 characters" : "Ít nhất 8 ký tự") : (en ? "Enter your password" : "Nhập mật khẩu")} /><button type="button" className="password-toggle" onClick={() => setShowPassword((value) => !value)}>{showPassword ? (en ? "Hide" : "Ẩn") : (en ? "Show" : "Hiện")}</button></div></label>
            {authError && <p className="auth-error" role="alert">{authError}</p>}
            <button className="auth-submit" disabled={loading}>{loading ? (en ? "Please wait..." : "Đang xử lý...") : adminMode ? (en ? "Open Admin Console" : "Truy cập Admin") : registering ? (en ? "Create account" : "Tạo tài khoản") : (en ? "Sign in" : "Đăng nhập")}<span aria-hidden="true">→</span></button>
          </form>
          {!adminMode && <button type="button" className="admin-back-to-guest" onClick={onAdminLogin}>{en ? "Administrator sign in" : "Đăng nhập quản trị"}</button>}
          <button type="button" className="admin-back-to-guest" onClick={onBack}>← {en ? "Back to guest mode" : "Quay lại chế độ khách"}</button>
        </div>
      </section>
    </main>
  );
}
