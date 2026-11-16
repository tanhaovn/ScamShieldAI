# ScamShield AI — iOS (UIKit / Swift)

Mã nguồn ứng dụng iOS, project Xcode, assets, launch screen và scheme dùng chung. Không cần CocoaPods hoặc thư viện Swift bên ngoài. Dữ liệu Simulator, file build và trạng thái Xcode cá nhân không được đưa lên Git.

## Clone và chạy giao diện app

Cần máy Mac có Xcode và iOS Simulator runtime. Bản này được kiểm tra bằng Xcode 26.6; deployment target iOS 17.0.

```sh
git clone --single-branch --branch duc-tuan0207 https://github.com/tanhaovn/ScamShieldAI.git
cd ScamShieldAI
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

App build và mở giao diện độc lập, nhưng phân tích ảnh/tin nhắn/liên kết/PDF và trợ lý cần backend đang chạy. Backend, model và môi trường Python không nằm trong thư mục Swift này.

Cấu hình hiện tại tại `ScamShieldAI/Utils/Constants.swift`:

- Debug trên Simulator: `http://127.0.0.1:8000` — backend phải chạy trên cùng máy Mac.
- Debug trên iPhone thật: sửa `deviceAPIBaseURL` thành địa chỉ LAN của máy chạy backend; hai thiết bị phải cùng mạng. Địa chỉ `192.168.0.3` trong source là cấu hình phát triển hiện tại, không phải địa chỉ chung cho mọi máy.
- Release: dùng Build Setting `SCAMSHIELD_API_BASE_URL`, được đưa vào Info.plist; cấu hình hiện tại là `https://scamshieldai-9go5.onrender.com`. Cần backend HTTPS tương thích, hoạt động thực tế để phân tích.

Các endpoint app cần:

| Chức năng | Endpoint |
| --- | --- |
| Danh mục | `GET /scam-categories` |
| Ảnh / QR | `POST /check-image/guest` |
| Tin nhắn | `POST /check-text` |
| Liên kết | `POST /check-url` |
| PDF | `POST /check-document` |
| Trợ lý | `POST /analysis-assistant` |

Lưu ý tương thích: backend tại commit `7e72957` của nhánh `duc-tuan0207` chưa có `/check-image/guest`. Chỉ thêm thư mục Swift không cập nhật backend đó; cần dùng backend tương thích từ môi trường phát triển hoặc bổ sung endpoint ở một thay đổi backend riêng để phân tích ảnh không trả 404. Không đổi endpoint sang luồng khác một cách tự động.

Lịch sử được lưu cục bộ trong Application Support trên thiết bị. Lịch sử đã có có thể xem không cần mạng; clone mới không mang theo dữ liệu người dùng hoặc lịch sử trong Simulator của máy cũ.

## Kiểm tra source

Từ thư mục gốc repository:

```sh
bash Swift/ScamShieldAI/Checks/run_checks.sh
```

Các check dùng URLProtocol giả lập API và thư mục tạm, kiểm tra bốn loại dữ liệu đầu vào, request trợ lý và lưu/đọc/xóa lịch sử; không cần backend trực tuyến.

## Giao diện

Bảng màu ở `AppTheme.swift`. App có chế độ sáng/tối, hỗ trợ Dynamic Type và Giảm chuyển động. Điểm rủi ro tăng dần khi mở kết quả mới hoặc xem lại từ Lịch sử. Các hiệu ứng chỉ thay đổi hiển thị, không đổi điểm phân tích.
