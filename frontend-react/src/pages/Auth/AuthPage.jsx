export default function AuthPage({
  mode,
  setMode,
  form,
  setForm,
  loading,
  onSubmit,
}) {
  return (
    <div className="page auth-page">
      <div className="auth-card">
        <h1>Scam Detector</h1>
        <div className="tabs">
          <button
            className={mode === "login" ? "tab active" : "tab"}
            onClick={() => setMode("login")}
          >
            Đăng nhập
          </button>
          <button
            className={mode === "register" ? "tab active" : "tab"}
            onClick={() => setMode("register")}
          >
            Đăng ký
          </button>
        </div>
        <form onSubmit={onSubmit} className="auth-form">
          {mode === "register" && (
            <input
              value={form.full_name}
              onChange={(event) =>
                setForm({ ...form, full_name: event.target.value })
              }
              placeholder="Họ tên"
            />
          )}
          <input
            type="email"
            value={form.email}
            onChange={(event) =>
              setForm({ ...form, email: event.target.value })
            }
            placeholder="Email"
          />
          <input
            type="password"
            value={form.password}
            onChange={(event) =>
              setForm({ ...form, password: event.target.value })
            }
            placeholder="Mật khẩu"
          />
          <button disabled={loading}>
            {loading
              ? "Đang xử lý..."
              : mode === "login"
                ? "Đăng nhập"
                : "Tạo tài khoản"}
          </button>
        </form>
      </div>
    </div>
  );
}
