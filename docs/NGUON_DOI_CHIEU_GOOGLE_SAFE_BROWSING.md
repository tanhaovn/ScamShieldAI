# Nguồn đối chiếu độc lập: Google Safe Browsing v5

## Mục đích sử dụng

SFDS sử dụng Google Safe Browsing v5 như một lớp **đối chiếu danh tiếng URL độc
lập** bên cạnh mô hình PhishVN. Hệ thống chỉ gọi API với URL đã được người dùng
cung cấp hoặc được trích từ ảnh, QR và tài liệu; SFDS không tự mở URL cần kiểm
tra.

Khi Google trả về một threat match, kết quả được ghi riêng với nguồn
`Google Safe Browsing v5`, loại đe dọa và thời hạn cache. Tín hiệu này được ưu
tiên ở mức nguy hiểm vì đó là kết quả khớp danh sách đe dọa đã biết, không phải
dự đoán xác suất từ model của nhóm.

## Vì sao nguồn này có sức thuyết phục

- Dịch vụ do Google vận hành và có tài liệu API chính thức.
- Danh sách bao phủ social engineering/phishing, malware, unwanted software và
  potentially harmful applications.
- API v5 hỗ trợ tra cứu URL thời gian gần thực và trả về `threatTypes` cụ thể.
- Phản hồi có `cacheDuration`; SFDS tuân thủ thời hạn này và không cache một kết
  quả nguy hiểm quá 30 phút nếu chưa kiểm tra lại.
- Nguồn này độc lập với tập PhishVN và model ResNet18 do dự án sử dụng.

## Giới hạn cần công bố

- Google Safe Browsing API dành cho mục đích phi thương mại. Sản phẩm thương mại
  phải dùng Google Web Risk hoặc có thỏa thuận phù hợp.
- URL được gửi tới Google để đối chiếu; điều này phải được nêu trong chính sách
  quyền riêng tư của ứng dụng.
- Không có threat match **không chứng minh URL an toàn**. URL mới hoặc chiến dịch
  mới có thể chưa nằm trong danh sách.
- Chỉ cảnh báo thực sự do API trả về mới được gắn nguồn Google. Cảnh báo từ
  PhishVN, OCR, Risk Engine hoặc ResNet18 không được trình bày như kết luận của
  Google.

## Cách trình bày khi bảo vệ báo cáo

> Hệ thống không chỉ dựa vào model do nhóm tự huấn luyện. Với URL, SFDS kết hợp
> mô hình PhishVN chuyên cho dữ liệu Việt Nam và đối chiếu độc lập qua Google
> Safe Browsing v5. Khi Google xác nhận URL khớp danh sách đe dọa đã biết, hệ
> thống hiển thị riêng nguồn và loại đe dọa. Nếu Google không có kết quả, hệ
> thống không suy diễn rằng URL an toàn mà tiếp tục dùng các lớp phân tích nội
> bộ và hiển thị giới hạn của kết quả.

## Tài liệu chính thức

1. Google Safe Browsing — Overview: https://developers.google.com/safe-browsing/
2. Google Safe Browsing API v5 — `urls.search`:
   https://developers.google.com/safe-browsing/reference/rest/v5/urls/search
3. Appropriate Usage:
   https://developers.google.com/safe-browsing/reference/Appropriate.Usage
4. Terms of Service: https://developers.google.com/safe-browsing/terms

Ngày đối chiếu tài liệu: 08/11/2026.
