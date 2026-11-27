# Checklist phát hành ScamShield AI lên App Store

Các phần trong binary iOS đã được chuẩn hóa theo hướng review của Apple: không còn đăng nhập bắt buộc, có màn hình quyền riêng tư và lựa chọn gửi dữ liệu trước phân tích, có privacy manifest, không cho phép ATS tải HTTP tùy ý, và bản Release chỉ nhận API HTTPS. Lượt quét ảnh của khách dùng `/check-image/guest` để xóa ảnh tạm trên máy chủ sau phân tích; tài khoản Admin vẫn lưu lịch sử máy chủ.

Trước khi archive/upload, cần hoàn tất các mục phụ thuộc môi trường phát hành:

1. Đặt `SCAMSHIELD_API_BASE_URL` trong cấu hình **Release** của Xcode thành host HTTPS thật, ổn định của backend đang có endpoint `/check-image/guest`. Không dùng tunnel `trycloudflare.com` tạm thời, `localhost`, IP LAN hoặc HTTP. Kiểm tra `/health`, đăng nhập Admin và mọi endpoint từ iPhone thật.
2. Đưa URL chính sách quyền riêng tư công khai và URL hỗ trợ thật vào App Store Connect. Nội dung chính sách phải nêu ảnh, tin nhắn, URL và PDF được gửi đến backend; khả năng xử lý bằng Google Gemini/Safe Browsing; thời gian lưu; việc xóa ảnh tạm; lịch sử Admin; và cách yêu cầu xóa dữ liệu trên máy chủ. Điền kênh hỗ trợ đó trong trang Quyền riêng tư của app nếu có URL chính thức.
3. Điền App Privacy labels trong App Store Connect theo luồng dữ liệu thực tế: ảnh/video, tin nhắn, nội dung người dùng, email và ID tài khoản Admin cho mục đích App Functionality. Xác minh với cấu hình backend phát hành và khai báo thêm nếu tích hợp SDK hoặc dịch vụ khác.
4. Tạo App Store screenshots, mô tả, từ khóa, age rating và support URL đúng với tính năng thật. Không mô tả app như công cụ kết luận chắc chắn hoặc chống virus.
5. Archive bằng tài khoản/team ký phát hành, kiểm tra trên iPhone thật với quyền Camera bị từ chối, thư viện ảnh bị giới hạn, mất mạng, backend trả lỗi và thao tác xóa lịch sử. Kiểm tra build với phiên bản Xcode/iOS SDK mà Apple yêu cầu tại thời điểm nộp.
6. Trong Review Notes, nêu rõ app dùng ngay không cần tài khoản, quy trình chọn ảnh, backend HTTPS, cách mở mục `Cá nhân → Đọc chính sách quyền riêng tư`; cung cấp tài khoản Admin demo và hướng dẫn truy cập nếu muốn Apple review phần Admin.

Việc Apple duyệt vẫn phụ thuộc metadata, máy chủ phát hành, chữ ký và kiểm thử thiết bị thật; build thành công không tự đảm bảo được phê duyệt.
