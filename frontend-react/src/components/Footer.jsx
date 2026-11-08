export default function Footer({ language = "vi" }) {
  return (
    <footer className="app-footer">
      <span>Scam Detector</span>
      <span>{language === "en" ? "Check before you trust." : "Kiểm tra trước khi bạn tin."}</span>
    </footer>
  );
}
