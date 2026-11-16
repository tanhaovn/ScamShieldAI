# Báo cáo kiểm thử black-box Scam Detector

- Ngày chạy: 12/11/2026, múi giờ Asia/Saigon
- Phiên bản mã nguồn: `7e72957` cùng các thay đổi chưa commit trong workspace
- Môi trường: Windows, Python 3.12.5, FastAPI 0.115.0, SQLite cục bộ
- Cách chạy: khởi động Uvicorn thật trên `127.0.0.1:8765`, sau đó gọi các API chỉ qua HTTP
- Bộ chạy: `scripts/run_black_box_suite.py`
- Kết quả thô: `.pytest-work/black-box-results.json` (artifact cục bộ, không commit)

## Kết luận

**Đạt 86/86 ca, không có ca thất bại.** Backend, frontend đã build, xác thực,
phân quyền, kiểm tra text/URL/PDF/ảnh, validation và các thao tác quản trị được
quan sát là ổn định trong cấu hình cục bộ đã kiểm tra.

Kết quả này cho phép kết luận dự án **ổn định ở mức regression/demo trên môi
trường local**. Không nên diễn giải thành “ổn định tuyệt đối” hoặc accuracy sản
phẩm 100%: bộ test xác nhận hành vi HTTP và các mẫu đại diện, không thể bao phủ
mọi dữ liệu lừa đảo ngoài thực tế, tải lớn, lỗi mạng hay tích hợp bên thứ ba.

## Tổng quan kết quả

| Nhóm | Đạt/Tổng | Nội dung chính |
|---|---:|---|
| System | 11/11 | Health, version, frontend, asset, OpenAPI, Swagger, 404, 405, CORS, danh mục, model registry |
| Validation | 8/8 | Thiếu trường, dữ liệu rỗng/sai, text quá dài, batch quá giới hạn, multipart/JSON lỗi |
| Text | 6/6 | 3 nội dung an toàn và 3 nội dung nguy hiểm |
| URL | 7/7 | Domain tin cậy, link rút gọn, IP, giả thương hiệu, punycode, batch trộn |
| Assistant | 1/1 | Câu trả lời có nội dung dựa trên kết quả phân tích |
| Auth | 7/7 | Đăng ký bị khóa, login sai/đúng, Google auth chưa cấu hình, hồ sơ admin |
| Authorization | 7/7 | Các endpoint quản trị từ chối request không có token |
| Admin | 10/10 | Keyword, model, evaluation, dataset, system log, benchmark, history |
| Feedback | 2/2 | Gửi feedback ẩn danh và admin đọc danh sách |
| Document | 7/7 | Sai loại, PDF hỏng/rỗng/an toàn/nguy hiểm, giới hạn 10 trang và 15 MB |
| Image validation | 6/6 | MIME sai, bytes giả, GIF, ảnh quá nhỏ, quá 25 MP, quá 10 MB |
| Image format | 3/3 | PNG, JPEG và WEBP hợp lệ |
| Image fixtures | 8/8 | Toàn bộ 3 mẫu an toàn và 5 mẫu lừa đảo trong repository |
| Image persistence | 2/2 | Tải lại ảnh đã upload và lưu scan có đăng nhập |
| Concurrency | 1/1 | 5 request health đồng thời đều trả 200 |
| **Tổng** | **86/86** | **100% trong phạm vi suite** |

Benchmark nội bộ được gọi qua API trong suite cũng đạt **13/13** mẫu.

## Hiệu năng quan sát

- P95 của 86 ca: **1.931,91 ms**.
- Ca chậm nhất: upload PDF vượt 15 MB, **10.775,28 ms**, trả đúng `413`.
- Upload ảnh vượt 10 MB: **6.088,48 ms**, trả đúng `413`.
- Các ảnh fixture có ca chậm nhất khoảng **2.761,93 ms**.

Hai ca file quá dung lượng hiện đọc/nhận request trước khi từ chối nên chậm hơn
các ca còn lại. Đây chưa phải lỗi chức năng, nhưng có thể tối ưu ở reverse proxy
hoặc giới hạn body sớm nếu triển khai chịu lưu lượng công khai.

## Phạm vi và giới hạn

Đã kiểm tra cả luồng thành công, lỗi đầu vào, giá trị biên, quyền truy cập, lưu
dữ liệu và một mức đồng thời cơ bản. Suite sử dụng toàn bộ tám ảnh đã gán nhãn
trong `tests/fixtures/images` và tự sinh tài liệu/ảnh tạm cho từng định dạng.

Chưa được xác nhận trong lần chạy này:

- Google Safe Browsing thật vì không cung cấp API key.
- Google OAuth thật vì không cung cấp client ID; chỉ kiểm tra lỗi `503` có kiểm soát.
- Deepfake transformer và Qwen VLM vì đều bị tắt trong cấu hình test.
- MySQL, Render, cold start, stress/load kéo dài và lỗi mạng bên ngoài.
- Accuracy khoa học trên test set độc lập lớn; tám ảnh fixture chỉ là regression set nhỏ.
- Tương thích trình duyệt bằng thao tác UI; frontend được xác nhận qua HTML và asset build phục vụ từ backend.

## Rủi ro còn lại

Khi server nạp model URL, runtime phát cảnh báo model scikit-learn được serialize
bằng `1.4.2` nhưng môi trường hiện tại đang chạy `1.5.2`. `requirements.txt` đã
khóa đúng `scikit-learn==1.4.2`, vì vậy cần cài lại môi trường từ file này trước
khi đo benchmark chính thức. Không có ca nào thất bại vì cảnh báo trên, nhưng
không nên bỏ qua vì khác phiên bản có thể làm kết quả model thay đổi.

## Tính cô lập của lần chạy

- Database được sao lưu trước khi test và khôi phục lại đúng SHA-256 sau test.
- 24 file upload do hai lượt chạy tạo ra đã được xóa; thư mục `uploads` trở về 153 file ban đầu.
- Server test đã được dừng.
- Không thay đổi logic phân tích của ứng dụng.

## Chạy lại

Tạo một database test riêng hoặc sao lưu database trước khi chạy vì suite có
tạo bản ghi admin tạm thời. Khởi động backend với tài khoản admin test, rồi chạy:

```powershell
python scripts/run_black_box_suite.py `
  --base-url http://127.0.0.1:8765 `
  --admin-email <admin-email> `
  --admin-password <admin-password> `
  --json-out .pytest-work/black-box-results.json
```

Exit code `0` nghĩa là toàn bộ ca đạt; exit code `1` nghĩa là có ít nhất một ca
thất bại. Báo cáo JSON chứa trạng thái, thời gian và mô tả kỳ vọng/thực tế của
từng ca để dùng trong CI hoặc truy vết regression.

