# Cấu trúc dự án

Dự án tách mã nguồn, model, dữ liệu, test và tài liệu để tránh trộn file runtime
với tài nguyên phát triển.

| Thư mục | Vai trò |
| --- | --- |
| `backend/app/` | API FastAPI và các module AI, OCR, visual, risk, database |
| `frontend-react/` | Ứng dụng React/Vite; `node_modules` và `dist` không thuộc source |
| `models/` | Checkpoint model và báo cáo metric được ứng dụng nạp lúc chạy |
| `datasets/` | Dataset nghiên cứu; không được copy vào Docker runtime mặc định |
| `database/` | Schema SQL và backup phục vụ phát triển |
| `tests/` | Test tự động; dữ liệu mẫu đặt trong `tests/fixtures/` |
| `scripts/` | Công cụ đánh giá, chuẩn bị dữ liệu và sinh tài liệu |
| `docs/` | Báo cáo, thiết kế, asset sơ đồ và bộ hồ sơ capstone |
| `tessdata/` | Model ngôn ngữ Tesseract cần cho OCR |
| `uploads/` | Dữ liệu runtime tạm thời, bị Git bỏ qua |

Các file cấu hình triển khai (`Dockerfile`, `render.yaml`), dependency
(`requirements.txt`) và hướng dẫn chính (`README.md`) được giữ ở root theo thông
lệ để công cụ CI/CD nhận diện trực tiếp.

## Quy ước

- Không commit `.env`, database runtime, upload, cache, virtual environment,
  `node_modules` hoặc frontend build output.
- Model ứng dụng sử dụng được đặt trong `models/`; model/dataset nghiên cứu đặt
  trong `datasets/`.
- Tài liệu sinh tự động phải ghi vào `docs/`, không tạo thêm thư mục asset ở root.
- Thay đổi đường dẫn phải dùng đường dẫn tính từ project root, không hardcode ổ đĩa.
