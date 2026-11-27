# Đối chiếu Swift với web

Mốc đối chiếu: `origin/main` — `0d9d930d480070cc6e4b89b0de4ab453424ed909`, kiểm tra ngày 18/11/2026.
Phạm vi gốc: chức năng cho người dùng khách. Bản cập nhật ngày 27/11/2026 thêm giao diện quản trị native trong ứng dụng iOS.

| Phần của web | Swift sau đồng bộ |
| --- | --- |
| Tổng quan | Radar, thống kê từ lịch sử thật, các lớp phân tích, xu hướng, phân bổ và 5 lượt gần nhất |
| Đầu vào | Ảnh/QR, tin nhắn, liên kết, PDF, loạt URL |
| Ảnh | Chọn từ thư viện hoặc camera; khung xem trước theo tỷ lệ ảnh, không cắt ảnh |
| Kết quả | Điểm và mức nguy cơ từ backend; kết luận, loại lừa đảo, OCR/QR và phạm vi PDF |
| Bằng chứng ảnh | Ảnh gốc và Grad-CAM; observation/why_risky khi backend có giải thích thị giác |
| Phản hồi | Đúng, cảnh báo sai, bỏ sót; ghi chú tùy chọn và trạng thái gửi ngay trong kết quả |
| Loạt URL | Giữ trạng thái URL lỗi riêng, xuất CSV cùng các cột URL/điểm/mức nguy cơ như web |
| Lịch sử | Lọc mức nguy cơ, tìm tên hoặc mã, xem chi tiết, xóa mục và xuất PDF |
| Giải thích trong lịch sử | Ưu tiên chi tiết AI, rồi chỉ báo rủi ro, rồi bằng chứng thành phần; dùng giải thích cũ nếu thiếu dữ liệu mới |
| Cá nhân | Thẻ hồ sơ khách, thống kê, thông tin tài khoản, quyền riêng tư, lượt gần đây, Việt/English, sáng/tối |
| Admin | Tab thứ năm mở đăng nhập và tám mục quản trị native: lịch sử, dataset, AI models, đánh giá, từ khóa, phản hồi, thiết bị và nhật ký |

## Đã bỏ phần dư

- Trợ lý hỏi đáp, nút mở chatbot và API `/analysis-assistant`: backend/web mới đã gỡ.
- Bộ chọn danh mục trên màn quét: web mới không còn hiển thị. Danh mục đầu tiên vẫn được chọn tự động.
- Bảng chi tiết kỹ thuật: web mới đã gỡ khỏi kết quả; dữ liệu backend vẫn được lưu để lịch sử và xuất báo cáo sử dụng.
- Các nút dán riêng, lối tắt nguồn quét trên Tổng quan và các thẻ chỉ số lặp lại; thao tác dán vẫn dùng menu nhập liệu của iOS.

## Khác biệt do nền tảng và dữ liệu

- iOS dùng tab bar, bộ chọn ảnh/tệp và bảng chia sẻ của hệ thống. Giữ màu thương hiệu, radar và hiệu ứng điểm tăng dần; tôn trọng Giảm chuyển động và cỡ chữ hệ thống.
- Lịch sử khách trên iPhone nằm trên thiết bị. Khi đăng nhập, app tải thêm lịch sử của tài khoản từ backend và ghép với bản ghi cục bộ; localStorage của trình duyệt web không được đồng bộ.
- Hướng dẫn quyền riêng tư và xin quyền camera phục vụ luồng iOS. Chức năng quản trị thiết bị nằm trong Admin Console sau đăng nhập; app khách không yêu cầu quyền vị trí.
- Admin đăng nhập bằng JWT lưu trong Keychain và gọi backend API. Sau khi đăng nhập, lịch sử tài khoản được tải từ backend; lịch sử khách trong trình duyệt web không tự đồng bộ.
- Trạng thái thiếu OCR, model, Google Safe Browsing hoặc AI thị giác lấy từ backend. App không tự tạo điểm hoặc giả dữ liệu AI khi dịch vụ chưa sẵn sàng.

## Đã kiểm tra

- Build Xcode thành công từ thư mục `Swift` trong bản clone mới, không dùng thư mục build hay Simulator của repository cũ.
- `Checks/run_checks.sh` qua: năm chế độ đầu vào, multipart, URL lỗi, payload phản hồi, CSV, lưu/đọc dữ liệu mới và lịch sử cũ. Có kiểm tra giải thích Gemini vẫn còn sau khi lưu và mở lại.
- Backend main mới chạy với SQLite thử nghiệm riêng: health, danh mục, text, URL, batch, PDF, ảnh, phản hồi; endpoint trợ lý cũ trả 404. Grad-CAM thật trả `available: true`.
- Web main mới build production thành công.
- Mở app trên iOS Simulator 26.0 và 26.5; kiểm tra màn Tổng quan, màn quét, tỷ lệ ảnh xem trước và kết quả ảnh. Hiệu ứng điểm khi mở lại kết quả đã quan sát được.
- Bản cập nhật native được build trên iOS Simulator 26.0; đã mở các màn Kiểm tra, Cá nhân, đăng nhập Admin, danh sách và chi tiết lịch sử, biểu mẫu dataset và kiểm tra trường bắt buộc. Phiên Admin trong Keychain được khôi phục sau khi khởi động lại bản app ký cho Simulator.

Gemini trực tuyến và Google Safe Browsing chưa được kiểm tra bằng khóa dịch vụ thật. Camera trên iPhone thật, tạo bản ghi Admin và việc gửi phản hồi qua toàn bộ thao tác giao diện cần kiểm tra bổ sung; kiểm tra API phản hồi đã qua.

## Chạy

Xem [README.md](README.md) để mở Xcode, cấu hình backend và chạy kiểm tra. Phân tích cần backend đang hoạt động; build và mở giao diện không cần máy chủ. Simulator và các file build không nằm trong mã nguồn Swift.
