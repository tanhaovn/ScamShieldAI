# ScamShield AI — iOS (UIKit / Swift)

Mã nguồn ứng dụng iOS, project Xcode, assets, launch screen và scheme dùng chung. Không cần CocoaPods hoặc thư viện Swift bên ngoài. Dữ liệu Simulator, file build và trạng thái Xcode cá nhân không được đưa lên Git.

Bảng đối chiếu chức năng, phần thêm/bỏ và phạm vi kiểm tra: [WEB_PARITY.md](WEB_PARITY.md).

## Chạy giao diện iOS

Mở dự án Xcode từ bản sao có thư mục Swift đã đồng bộ. Cần máy Mac có Xcode và iOS Simulator runtime. Bản này được kiểm tra bằng Xcode 26.6; deployment target iOS 17.0.

```sh
open Swift/ScamShieldAI/ScamShieldAI.xcodeproj
```

Trong Xcode:

1. Chọn scheme **ScamShieldAI** (đã chia sẻ trong repository).
2. Chọn một **iPhone Simulator** đã cài. Nếu chưa có runtime, tải trong Xcode Settings → Components.
3. Nhấn **Run** (`Cmd + R`). App mở vào Tổng quan, không cần đăng nhập.

Simulator được Xcode tạo trên máy người clone, không cần sao chép máy ảo của người phát triển. Build trên Simulator không cần tài khoản ký ứng dụng. Khi chạy trên iPhone thật, chọn Apple Development Team của bạn trong Signing & Capabilities; nếu cần, đổi Bundle Identifier sang tên riêng.

### Build bằng dòng lệnh

Chạy từ thư mục gốc repository, chọn đúng Xcode đã cài:

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcodebuild \
  -project Swift/ScamShieldAI/ScamShieldAI.xcodeproj \
  -scheme ScamShieldAI \
  -configuration Debug \
  -destination 'generic/platform=iOS Simulator' \
  -derivedDataPath /tmp/ScamShieldAI-build \
  CODE_SIGNING_ALLOWED=YES CODE_SIGN_IDENTITY=- build
```

## Kết nối backend để phân tích

App build và mở giao diện độc lập, nhưng phân tích ảnh/tin nhắn/liên kết/PDF cần backend đang chạy. Backend, model và môi trường Python không nằm trong thư mục Swift này.

Chạy backend theo README của repository, từ thư mục gốc để backend tìm được `models/` và `uploads/`. Cấu hình iOS ở `ScamShieldAI/Utils/Constants.swift`:

- Đặt địa chỉ backend trong Build Setting `SCAMSHIELD_API_BASE_URL` của cấu hình cần chạy. Chỉ dán phần gốc `https://domain`, không chép `?zarsrc=...` hoặc `#admin-login`. Trong Debug, nếu setting trống, app dùng tunnel tạm ở `fallbackAPIBaseURL` trong `Constants.swift`; Release không dùng tunnel dự phòng và cần một địa chỉ HTTPS ổn định.
- Debug trên Simulator dùng `SCAMSHIELD_DEBUG_API_BASE_URL` trong mục Run của scheme Xcode nếu cần trỏ tới backend khác, ví dụ `http://127.0.0.1:8000`. Địa chỉ HTTP chỉ được dùng cho localhost trong bản Debug.
- iPhone thật cần truy cập được backend HTTPS. Không phải cùng Wi-Fi khi dùng tunnel Cloudflare.

Các endpoint app cần:

| Chức năng | Endpoint |
| --- | --- |
| Danh mục | `GET /scam-categories` |
| Ảnh / QR khách | `POST /check-image/guest` (ảnh tạm được xóa trên máy chủ sau phân tích) |
| Ảnh / QR Admin | `POST /check-image` (lưu vào lịch sử tài khoản) |
| Tin nhắn | `POST /check-text` |
| Liên kết | `POST /check-url` |
| PDF | `POST /check-document` |
| Nhiều URL | `POST /check-urls-batch` |
| Phản hồi | `POST /scan-feedback` |
| Trạng thái máy chủ | `GET /health` |
| Đăng nhập Admin | `POST /admin/login`, `GET /me` |
| Lịch sử theo tài khoản | `GET /scan-history` với Bearer token |

## Admin trên iPhone

Trang **Cá nhân** giữ bố cục hồ sơ khách của bản web tham chiếu: thẻ hồ sơ, thống kê, thông tin tài khoản, quyền riêng tư và hoạt động gần đây. Đăng nhập quản trị nằm riêng trong tab **Admin**.

Tab **Admin** là giao diện UIKit chạy trực tiếp trên iPhone. Đăng nhập bằng tài khoản admin của backend để xem lịch sử kiểm tra, dữ liệu huấn luyện, mô hình AI, đánh giá, từ khóa, phản hồi, thiết bị và nhật ký. Những mục có dữ liệu có thể mở chi tiết; dataset, model, đánh giá, từ khóa và nhật ký có biểu mẫu tạo bản ghi. Mục đánh giá có lệnh chạy đánh giá tự động. Thiết bị có bản đồ khi backend cung cấp tọa độ.

Ứng dụng chỉ hiện các chức năng Admin sau khi backend xác thực thành công. JWT được lưu trong iOS Keychain, không lưu mật khẩu, và được gắn với địa chỉ máy chủ. Sau khi đăng nhập, tab **Lịch sử** tải `/scan-history` của tài khoản đó và hiển thị cùng các lượt lưu trên iPhone, loại những lượt trùng mã. Lượt khách chỉ lưu trong trình duyệt web không nằm trong lịch sử tài khoản máy chủ.

Admin dùng cùng địa chỉ backend API với màn kiểm tra; không cần chạy frontend React.

Đối chiếu chức năng người dùng với web nhánh `main`, commit `0d9d930`. App dùng endpoint ảnh dành riêng cho khách để tránh lưu ảnh trên máy chủ; Admin dùng endpoint ảnh gắn với tài khoản. Các trường Grad-CAM, vùng ảnh, AI thị giác và nguồn đối chiếu là optional để vẫn mở được kết quả cũ. Dữ liệu phụ thuộc model/cấu hình của backend; app hiển thị trạng thái chưa có dữ liệu khi máy chủ không trả kết quả.

Lịch sử được lưu cục bộ trong Application Support trên thiết bị. Lịch sử đã có có thể xem không cần mạng; có thể xóa từng lượt hoặc toàn bộ lịch sử trên iPhone trong tab Lịch sử. Xóa cục bộ không xóa lịch sử Admin trên máy chủ. Clone mới không mang theo dữ liệu người dùng hoặc lịch sử trong Simulator của máy cũ. Trước lần phân tích đầu tiên với mỗi máy chủ, app hỏi đồng ý gửi nội dung và nêu khả năng dùng Google Gemini/Safe Browsing; có thể đặt lại lựa chọn trong trang Quyền riêng tư.

## Kiểm tra source

Từ thư mục gốc repository:

```sh
bash Swift/ScamShieldAI/Checks/run_checks.sh
```

Các check dùng URLProtocol giả lập API và thư mục tạm, kiểm tra năm loại dữ liệu đầu vào, phản hồi, URL không hợp lệ, CSV, lưu/đọc dữ liệu bằng chứng và lịch sử; không cần backend trực tuyến.

## Giao diện

Tổng quan theo thứ tự trên web: radar, thống kê, các lớp phân tích, biểu đồ và lượt gần đây. Kết quả ảnh đặt ảnh gốc cạnh Grad-CAM và hiện các dấu hiệu cụ thể khi backend có dữ liệu. Phản hồi nằm ngay trong kết quả. Nội dung đọc được và QR có thể mở hoặc thu gọn. Lịch sử ưu tiên giải thích AI và các bằng chứng đã lưu. Bộ chọn danh mục và bảng chi tiết kỹ thuật đã gỡ theo web mới. Lịch sử dùng màn xem lại và nút xuất PDF riêng. Trợ lý hỏi đáp đã được gỡ theo bản web mới.

Bảng màu ở `AppTheme.swift`. Bản iOS dùng điều hướng, bộ chọn ảnh/tệp và bảng chia sẻ của hệ thống, có Tiếng Việt/English, giao diện sáng/tối, Dynamic Type và Giảm chuyển động. Điểm vẫn tăng dần khi mở kết quả mới hoặc xem lại từ Lịch sử. Lịch sử đã lưu được giữ qua bản cập nhật.
