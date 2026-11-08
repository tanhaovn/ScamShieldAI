const languageLabels = {
  vi: { short: "VI", name: "Tiếng Việt" },
  en: { short: "EN", name: "English" },
};

function GlobeIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18M12 3c3 3.2 3 14.8 0 18M12 3c-3 3.2-3 14.8 0 18" />
    </svg>
  );
}

function ThemeIcon({ theme }) {
  return theme === "dark" ? (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M20 15.2A8.6 8.6 0 0 1 8.8 4 8.7 8.7 0 1 0 20 15.2Z" />
    </svg>
  ) : (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </svg>
  );
}

export default function PreferencesControl({ language, setLanguage, theme, toggleTheme }) {
  const isEnglish = language === "en";
  const themeLabel = theme === "dark"
    ? (isEnglish ? "Switch to light mode" : "Chuyển sang chế độ sáng")
    : (isEnglish ? "Switch to dark mode" : "Chuyển sang chế độ tối");

  return (
    <div className="preference-controls" aria-label={isEnglish ? "Display preferences" : "Tùy chọn hiển thị"}>
      <label className="language-control">
        <GlobeIcon />
        <span className="sr-only">{isEnglish ? "Language" : "Ngôn ngữ"}</span>
        <select value={language} onChange={(event) => setLanguage(event.target.value)} aria-label={isEnglish ? "Choose language" : "Chọn ngôn ngữ"}>
          {Object.entries(languageLabels).map(([value, item]) => (
            <option key={value} value={value} aria-label={item.name}>{item.short}</option>
          ))}
        </select>
        <svg className="language-chevron" viewBox="0 0 24 24" aria-hidden="true"><path d="m8 10 4 4 4-4" /></svg>
      </label>

      <button className="theme-control" type="button" onClick={toggleTheme} aria-label={themeLabel} title={themeLabel}>
        <span className="theme-control-track"><span className="theme-control-thumb"><ThemeIcon theme={theme} /></span></span>
        <span>{theme === "dark" ? (isEnglish ? "Dark" : "Tối") : (isEnglish ? "Light" : "Sáng")}</span>
      </button>
    </div>
  );
}
