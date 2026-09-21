import { useEffect, useRef, useState } from "react";

function ShieldLogo() {
  return (
    <svg viewBox="0 0 48 48" aria-hidden="true">
      <path d="M24 4 40 10v12c0 10.6-6.5 17.7-16 22-9.5-4.3-16-11.4-16-22V10z" />
      <path d="m17 24 4.5 4.5L31.5 18" />
    </svg>
  );
}

function GoogleMark() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path fill="#4285F4" d="M21.6 12.2c0-.7-.1-1.5-.2-2.2H12v4.2h5.4a4.7 4.7 0 0 1-2 3v2.7h3.3c1.9-1.8 2.9-4.4 2.9-7.7Z" />
      <path fill="#34A853" d="M12 22c2.7 0 5-.9 6.7-2.4l-3.3-2.7c-.9.6-2 1-3.4 1a5.9 5.9 0 0 1-5.5-4.1H3.1v2.8A10 10 0 0 0 12 22Z" />
      <path fill="#FBBC05" d="M6.5 13.8a6 6 0 0 1 0-3.8V7.2H3.1a10 10 0 0 0 0 9.4z" />
      <path fill="#EA4335" d="M12 5.9c1.5 0 2.8.5 3.9 1.5l2.9-2.9A9.8 9.8 0 0 0 3.1 7.2L6.5 10A5.9 5.9 0 0 1 12 5.9Z" />
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
      <span className="auth-data-node node-one">OCR</span>
      <span className="auth-data-node node-two">URL</span>
      <span className="auth-data-node node-three">AI</span>
      <div className="auth-detect-core">
        <ShieldLogo />
        <strong>LIVE DETECT</strong>
        <small>Phân tích đa tín hiệu</small>
      </div>
      <span className="auth-signal signal-one" />
      <span className="auth-signal signal-two" />
      <span className="auth-signal signal-three" />
    </div>
  );
}

export default function AuthPage({
  mode,
  setMode,
  form,
  setForm,
  loading,
  authError,
  googleClientId,
  onSubmit,
  onGoogleAuth,
}) {
  const [showPassword, setShowPassword] = useState(false);
  const googleButtonRef = useRef(null);
  const googleCallbackRef = useRef(onGoogleAuth);
  googleCallbackRef.current = onGoogleAuth;

  useEffect(() => {
    if (!googleClientId || !googleButtonRef.current) return undefined;

    let cancelled = false;
    const renderGoogleButton = () => {
      if (cancelled || !window.google?.accounts?.id || !googleButtonRef.current) {
        return;
      }
      googleButtonRef.current.replaceChildren();
      window.google.accounts.id.initialize({
        client_id: googleClientId,
        callback: ({ credential }) => googleCallbackRef.current(credential),
      });
      window.google.accounts.id.renderButton(googleButtonRef.current, {
        type: "standard",
        theme: "outline",
        size: "large",
        shape: "rectangular",
        text: mode === "register" ? "signup_with" : "signin_with",
        logo_alignment: "left",
        width: 360,
        locale: "vi",
      });
    };

    if (window.google?.accounts?.id) {
      renderGoogleButton();
    } else {
      let script = document.getElementById("google-identity-services");
      if (!script) {
        script = document.createElement("script");
        script.id = "google-identity-services";
        script.src = "https://accounts.google.com/gsi/client?hl=vi";
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
      }
      script.addEventListener("load", renderGoogleButton, { once: true });
    }

    return () => {
      cancelled = true;
    };
  }, [googleClientId, mode]);

  const isLogin = mode === "login";

  return (
    <main className="auth-page">
      <section className="auth-card" aria-label="Xác thực Scam Detector">
        <aside className="auth-showcase">
          <div className="auth-brand">
            <span className="auth-brand-icon"><ShieldLogo /></span>
            <div>
              <strong>Scam Detector</strong>
              <small>Vietnamese AI Safety</small>
            </div>
          </div>

          <div className="auth-showcase-copy">
            <span className="auth-live-label"><i /> AI ENGINE ONLINE</span>
            <h1>{isLogin ? "Chào mừng bạn trở lại!" : "Bắt đầu kiểm tra an toàn"}</h1>
            <p>
              OCR nội dung, nhận diện URL lừa đảo và giải thích dấu hiệu đáng
              ngờ trong cùng một quy trình.
            </p>
          </div>

          <DetectionVisual />

          <div className="auth-showcase-bottom">
            <span>Chưa {isLogin ? "có" : "dùng"} tài khoản?</span>
            <button
              type="button"
              className="auth-outline-button"
              onClick={() => setMode(isLogin ? "register" : "login")}
            >
              {isLogin ? "Tạo tài khoản" : "Đăng nhập ngay"}
            </button>
          </div>
        </aside>

        <div className="auth-form-panel">
          <div className="auth-mobile-brand">
            <span className="auth-brand-icon"><ShieldLogo /></span>
            <strong>Scam Detector</strong>
          </div>

          <header className="auth-form-heading">
            <span className="auth-form-kicker">SECURE ACCESS</span>
            <h2>{isLogin ? "Đăng nhập" : "Đăng ký tài khoản"}</h2>
            <p>
              {isLogin
                ? "Tiếp tục vào không gian phân tích của bạn."
                : "Lưu lịch sử kiểm tra và xem lại cảnh báo khi cần."}
            </p>
          </header>

          <div className="auth-mode-tabs" role="tablist" aria-label="Chọn hình thức xác thực">
            <button
              type="button"
              role="tab"
              aria-selected={isLogin}
              className={isLogin ? "active" : ""}
              onClick={() => setMode("login")}
            >
              Đăng nhập
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={!isLogin}
              className={!isLogin ? "active" : ""}
              onClick={() => setMode("register")}
            >
              Đăng ký
            </button>
          </div>

          {googleClientId ? (
            <div className="google-auth-wrap" ref={googleButtonRef} />
          ) : (
            <button className="google-auth-placeholder" type="button" disabled>
              <GoogleMark />
              <span>Tiếp tục với Google</span>
              <small>Cần cấu hình Client ID</small>
            </button>
          )}

          <div className="auth-divider"><span>hoặc dùng email</span></div>

          <form onSubmit={onSubmit} className="auth-form">
            {!isLogin && (
              <label className="auth-field">
                <span>Họ và tên</span>
                <div>
                  <i aria-hidden="true">Aa</i>
                  <input
                    autoComplete="name"
                    required
                    value={form.full_name}
                    onChange={(event) =>
                      setForm({ ...form, full_name: event.target.value })
                    }
                    placeholder="Nguyễn Văn A"
                  />
                </div>
              </label>
            )}

            <label className="auth-field">
              <span>Email</span>
              <div>
                <i aria-hidden="true">@</i>
                <input
                  type="email"
                  autoComplete="email"
                  required
                  value={form.email}
                  onChange={(event) => setForm({ ...form, email: event.target.value })}
                  placeholder="name@example.com"
                />
              </div>
            </label>

            <label className="auth-field">
              <span>Mật khẩu</span>
              <div>
                <i aria-hidden="true">●</i>
                <input
                  type={showPassword ? "text" : "password"}
                  autoComplete={isLogin ? "current-password" : "new-password"}
                  minLength={6}
                  required
                  value={form.password}
                  onChange={(event) => setForm({ ...form, password: event.target.value })}
                  placeholder={isLogin ? "Nhập mật khẩu" : "Tối thiểu 6 ký tự"}
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
              {loading
                ? "Đang xác thực..."
                : isLogin
                  ? "Đăng nhập an toàn"
                  : "Tạo tài khoản"}
              <span aria-hidden="true">→</span>
            </button>
          </form>

          <p className="auth-security-note">
            <span>✓</span> Dữ liệu đăng nhập được gửi trực tiếp tới máy chủ xác thực.
          </p>
        </div>
      </section>
    </main>
  );
}
