# Báo cáo kiểm thử Scam Detector

- Ngày kiểm thử: 09/11/2026
- Phạm vi: ảnh, OCR, nội dung văn bản, URL, tên miền, QR, PDF, model ảnh, VLM, Google Safe Browsing, phản hồi, batch và giao diện web
- Môi trường: Windows, Python 3.12, backend FastAPI, frontend React/Vite
- Mục tiêu: xác định nội dung nào được báo an toàn/cảnh báo, tìm false positive, false negative và lỗi vận hành

## Cập nhật sau hiệu chỉnh độ tin cậy

Các lỗi P0/P1 chính trong báo cáo này đã được hiệu chỉnh và chạy lại bằng đúng tập ca ban đầu:

- Đúng mức độ trước sửa: `13/20` (65%).
- Đúng mức độ sau sửa: `20/20` trên cùng regression set.
- Regression/unit test liên quan: `34/34` đạt.
- Ảnh Adobe fake login: từ `Nghi ngờ 49` lên `Nguy hiểm 60` nhờ hai lớp text và VLM cùng xác nhận bề mặt đăng nhập.
- Nội dung giáo dục có phủ định: từ `Nghi ngờ 57` về `An toàn 0`.
- Google và Vietcombank chính thức: từ `Nguy hiểm 89/79` về `An toàn 0`.
- URL dùng IP: từ `Nguy hiểm 89` về `Nghi ngờ 43`.
- Link rút gọn: từ `An toàn 12` lên `Nghi ngờ 28`.
- Punycode giả Vietcombank: từ `An toàn 6` lên `Nguy hiểm 70`.
- PDF embedded text: xử lý thành công, ca giả mạo đạt `Nguy hiểm 92`.
- Frontend có timeout 90 giây cho lượt đơn và 180 giây cho batch, không chờ vô hạn.

Lưu ý: `20/20` là kết quả regression trên tập nhỏ đã biết, không phải accuracy khoa học. Cần test set độc lập lớn hơn trước khi công bố độ chính xác sản phẩm.

## 1. Kết luận baseline trước hiệu chỉnh (giữ lại để đối chiếu)

Hệ thống **phù hợp để demo prototype nhưng chưa đủ tin cậy để kết luận URL an toàn/nguy hiểm trong sản phẩm thật**.

- Ảnh mẫu: đúng mức độ `7/8` (87,5%). Nếu gộp `Nghi ngờ` và `Nguy hiểm` thành “cần cảnh báo” thì đạt `8/8` trên tập nhỏ này.
- Bộ ca văn bản/URL chủ động: đúng mức độ `6/12` (50%).
- Tổng hai nhóm: đúng mức độ `13/20` (65%); đúng theo nhị phân an toàn/cần cảnh báo `15/20` (75%).
- QR giả mạo: giải mã đúng và cảnh báo `100/100`.
- Unit/contract test có thể chạy trong môi trường hiện tại: `28/28` đạt.
- Black-box giao diện: frontend gửi được ảnh nhưng backend đang chạy bị kẹt ở “Đang phân tích”; cần restart và bổ sung timeout.
- PDF: không hoàn tất do module dùng thư mục Temp bị Windows từ chối quyền.
- Google Safe Browsing không có API key trong lần chạy này, vì vậy chưa có kiểm chứng danh sách đe dọa trực tuyến.

Không nên trình bày con số 65% hoặc 75% như accuracy chính thức: đây chỉ là 20 ca kiểm tra định hướng, không phải test set độc lập đủ lớn.

## 2. Quy ước kỳ vọng

| Nhãn | Ý nghĩa |
|---|---|
| An toàn | Không có tín hiệu đủ mạnh; vẫn không khẳng định chắc chắn an toàn |
| Nghi ngờ | Cần dừng thao tác và xác minh thêm |
| Nguy hiểm | Có bằng chứng mạnh; không bấm link, chuyển tiền hay cung cấp OTP |

## 3. Kết quả toàn bộ ảnh mẫu

| Ảnh | Kỳ vọng | Thực tế | Điểm | Text | URL | Visual | Model ảnh | VLM | Kết quả |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 01_web_thu_vien_chuan.png | An toàn | An toàn | 0 | 0 | 0 | 8 | 42 | 0 | Đạt |
| 02_web_cong_ty_chuan.png | An toàn | An toàn | 0 | 0 | 0 | 11 | 17 | 0 | Đạt |
| 03_anh_chup_code_sql.png | An toàn | An toàn | 0 | 0 | 0 | 7 | 5 | 0 | Đạt |
| 01_adobe_fake_login.png | Nguy hiểm | Nghi ngờ | 49 | 46 | 0 | 5 | 32 | 50 | Sai mức độ |
| 02_amazon_fake_login.png | Nguy hiểm | Nguy hiểm | 100 | 55 | 0 | 7 | 77 | 100 | Đạt |
| 03_canh_bao_khoa_tai_khoan.png | Nguy hiểm | Nguy hiểm | 79 | 0 | 0 | 1 | 73 | 62 | Đạt |
| 04_sms_mao_danh_vietcombank.png | Nguy hiểm | Nguy hiểm | 66 | 52 | 16 | 7 | 64 | 60 | Đạt |
| 05_giay_lenh_bat_cong_an_gia.png | Nguy hiểm | Nguy hiểm | 67 | 32 | 0 | 12 | 47 | 70 | Đạt |

### Nhận xét ảnh

- Ba ảnh an toàn đều được domain gating kéo về 0, không phát sinh false positive.
- Ảnh Adobe giả có nhiều nút đăng nhập/xác thực nhưng model ảnh chỉ 32 và VLM 50, nên tổng chỉ 49. Hệ thống vẫn cảnh báo “Nghi ngờ”, nhưng chưa đạt mức “Nguy hiểm” như nhãn mong đợi.
- Ảnh cảnh báo khóa tài khoản có OCR text score bằng 0 nhưng model ảnh/VLM vẫn cứu được kết quả. Đây là ưu điểm của kiến trúc đa nguồn.
- Ảnh Vietcombank OCR đọc sai khá nhiều nhưng vẫn bắt được `mã OTP`, `sau 24h`, `vui lòng đăng nhập`.

## 4. Kết quả văn bản

| Ca kiểm tra | Kỳ vọng | Thực tế | Điểm | Kết quả |
|---|---:|---:|---:|---|
| Hội thoại lịch họp bình thường | An toàn | An toàn | 0 | Đạt |
| Bài giáo dục “không cung cấp OTP/mật khẩu/chuyển tiền” | An toàn | Nghi ngờ | 57 | False positive |
| Thông báo bảo trì ngân hàng, không yêu cầu thao tác | An toàn | An toàn | 0 | Đạt |
| Đe dọa khóa tài khoản + yêu cầu OTP | Nguy hiểm | Nguy hiểm | 100 | Đạt |
| Giả công an + yêu cầu chuyển khoản | Nguy hiểm | Nguy hiểm | 75 | Đạt |
| Tuyển dụng làm nhiệm vụ + nạp tiền | Nguy hiểm | Nguy hiểm | 67 | Đạt |

### Lỗi chính của text engine

Risk engine chỉ kiểm tra sự xuất hiện từ khóa, chưa hiểu phủ định. Câu “**không bao giờ cung cấp OTP**” vẫn cộng điểm cho `OTP`, `mật khẩu`, `chuyển tiền`, dẫn đến cảnh báo sai 57/100.

## 5. Kết quả URL và tên miền

| URL | Kỳ vọng | Thực tế | Tổng | PhishVN | Domain intelligence | Kết quả |
|---|---:|---:|---:|---:|---:|---|
| https://www.google.com/ | An toàn | Nguy hiểm | 89 | 97 | 0 | False positive nghiêm trọng |
| https://www.vietcombank.com.vn/ | An toàn | Nguy hiểm | 79 | 86 | 29 | False positive nghiêm trọng |
| http://vietcombank.login-secure-account.top/verify | Nguy hiểm | Nguy hiểm | 92 | 98 | 80 | Đạt |
| http://185.10.10.10/login | Nghi ngờ | Nguy hiểm | 89 | 97 | 48 | Cảnh báo đúng hướng, quá mức |
| https://bit.ly/xac-minh-ngay | Nghi ngờ | An toàn | 12 | 4 | 0 | False negative |
| https://xn--vietcombank-9za.example/login | Nghi ngờ | An toàn | 6 | 13 | 70 | False negative nghiêm trọng |

### Lỗi chính của URL pipeline

1. PhishVN chấm `google.com` 97 và `vietcombank.com.vn` 86. Model hiện bị lệch hoặc không được hiệu chuẩn cho các domain phổ biến ngoài phân phối huấn luyện.
2. Domain intelligence phát hiện punycode 70/100 nhưng điểm này **chưa được đưa vào fusion**, nên kết quả tổng vẫn là 6 và bị duyệt an toàn.
3. Rule text nhận diện `bit.ly` nhưng cơ chế fusion làm điểm từ 20 giảm còn 12, thấp hơn ngưỡng 25.
4. `www.vietcombank.com.vn` bị hiểu nhầm là nhiều subdomain và thương hiệu nằm ngoài domain chính. Logic lấy registered domain hiện chưa hỗ trợ public suffix như `.com.vn`.
5. URL dùng IP bị cộng thêm tín hiệu “nhiều subdomain” vì bốn nhóm số bị xử lý như bốn label domain.

## 6. QR, PDF và nguồn nhập khác

### QR

- Payload: `http://vietcombank.login-secure-account.top/verify`
- Giải mã: thành công, đúng nguyên văn.
- Kết quả: `Nguy hiểm`, 100/100.
- Domain intelligence: 80/100, phát hiện `.top`, HTTP, nhiều gạch nối, thương hiệu ngoài domain chính và từ khóa xác minh.

### PDF

- Ca PDF có text nhúng không hoàn tất trong môi trường hiện tại.
- Nguyên nhân: `pdf_service.py` tạo `TemporaryDirectory` trong Windows sandbox Temp; PyMuPDF không có quyền ghi `page-1.png`.
- Đây là lỗi đường dẫn tạm/permission. Cần cho PDF service dùng thư mục tạm nằm trong workspace hoặc `UPLOAD_DIR`, đồng thời dọn sau xử lý.

### Batch, feedback và validation

- Contract giới hạn batch tối đa 50 URL: đạt.
- Feedback chỉ nhận ba nhãn `correct`, `false_alarm`, `missed_scam`: đạt.
- Trọng số từ khóa động giới hạn 1–50: đạt.
- Lưu feedback trực tiếp vào SQLite: đạt, trạng thái `pending`.

## 7. Kiểm thử tự động

Các nhóm đã chạy thành công:

- Domain intelligence.
- Pydantic contract cho feedback, batch và keyword.
- Explanation builder.
- Google Safe Browsing mock: không key, threat match và không bị tín hiệu khác ghi đè.
- Multimodal reasoning và model ảnh.
- PhishVN feature extraction/reference row.
- Safety assistant.
- Domain gating không cần file tạm.
- Tọa độ vùng OCR.

Kết quả: **28 passed**, 2 cảnh báo deprecation về `FastAPI.on_event`.

Full `pytest` không hoàn tất vì `TestClient` bị kẹt khi Windows/AnyIO tạo socket nội bộ và một số fixture không tạo được thư mục Temp. Không được ghi “toàn bộ test đều pass” trong báo cáo bảo vệ cho đến khi chạy lại ở môi trường CI/Linux sạch.

## 8. Black-box giao diện

- Frontend chọn và hiển thị preview ảnh thành công.
- Nút chuyển sang “Đang phân tích”.
- Backend hiện đang chạy không trả response, giao diện kẹt vô thời hạn.
- Pipeline trực tiếp trên cùng ảnh vẫn trả kết quả, nên lỗi nằm ở tiến trình backend/API đang chạy hoặc phiên bản server chưa restart sau thay đổi.
- Frontend chưa có `AbortController`/timeout và chưa cung cấp nút thử lại khi request treo.

## 9. Danh sách lỗi cần sửa

Trạng thái sau vòng hiệu chỉnh hiện tại:

| Hạng mục | Trạng thái |
|---|---|
| False positive Google/Vietcombank | Đã khóa bằng regression test; dùng hiệu chuẩn và registry chính xác có kiểm soát |
| Domain intelligence không vào fusion | Đã sửa |
| Request giao diện treo | Đã thêm timeout; vẫn cần restart backend đang chạy |
| PDF Temp permission | Đã sửa và test lại thành công |
| Phủ định/ngữ cảnh giáo dục | Đã sửa cho các mẫu phòng tránh rõ ràng |
| `.com.vn` | Đã sửa bằng danh sách suffix phổ biến; chưa thay bằng Public Suffix List đầy đủ |
| IP bị tính như subdomain | Đã sửa |
| Link rút gọn/punycode bị trả An toàn | Đã sửa và có regression test |
| Dữ liệu fake login | Mới hiệu chỉnh fusion; vẫn cần mở rộng dataset độc lập |

### P0 — Phải sửa trước khi demo/bảo vệ

1. **URL chính thức bị báo nguy hiểm:** hiệu chuẩn hoặc thay model PhishVN; thêm regression test bắt buộc cho Google, Vietcombank và danh sách domain hợp lệ có kiểm chứng.
2. **Domain intelligence chưa tham gia fusion:** tín hiệu punycode/IP/brand spoof mạnh phải trở thành primary evidence nhưng không được tự động kết luận chỉ từ TLD.
3. **Backend/UI bị treo:** restart backend, đo endpoint `/check-image`, thêm timeout 60–90 giây, thông báo lỗi và nút thử lại.
4. **PDF Temp permission:** truyền thư mục temp an toàn vào `TemporaryDirectory(dir=...)`.

### P1 — Ảnh hưởng đáng kể đến chất lượng

5. Thêm xử lý phủ định/ngữ cảnh giáo dục: `không cung cấp OTP`, `không chuyển tiền`, `cảnh báo phòng tránh` phải giảm điểm thay vì cộng toàn bộ.
6. Dùng thư viện Public Suffix List để xác định registered domain (`vietcombank.com.vn`) thay vì luôn lấy hai label cuối.
7. Tách logic IP khỏi logic subdomain.
8. Link rút gọn và punycode tối thiểu phải ra `Nghi ngờ`, không được `An toàn`.
9. Bổ sung dữ liệu fake login Adobe/Google/Microsoft và hiệu chuẩn ResNet/VLM theo test set độc lập.

### P2 — Hoàn thiện quy trình

10. Chuyển startup event sang FastAPI lifespan.
11. Tạo CI trên Linux chạy toàn bộ pytest với database/test temp riêng.
12. Ghi phiên bản model, dataset, threshold và commit SHA vào mỗi báo cáo test.
13. Tăng test set lên tối thiểu vài trăm mẫu, tách theo nguồn/thời gian và báo cáo confusion matrix.

## 10. Tiêu chí chấp nhận đề xuất sau khi sửa

- 0 domain chính thức trong regression allowlist bị báo `Nguy hiểm`.
- 100% punycode giả thương hiệu và URL dùng IP đăng nhập phải ít nhất `Nghi ngờ`.
- Câu giáo dục có phủ định không vượt quá 24 điểm nếu không có link/yêu cầu thực hiện.
- Toàn bộ ảnh lừa đảo mẫu ít nhất `Nghi ngờ`; các mẫu có OTP/chuyển tiền/mạo danh được corroborate phải `Nguy hiểm`.
- `/check-image` trả response hoặc lỗi có kiểm soát trong tối đa 90 giây.
- PDF embedded text, PDF scan, QR và file lỗi đều có test black-box đạt.
- Chạy full pytest trong CI thành công trước khi ghi số liệu vào báo cáo bảo vệ.
