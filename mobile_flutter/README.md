# Scam Detector Mobile

Flutter app dùng chung backend FastAPI của project `scam-detector`.

## Chạy app

1. Cài Flutter SDK và Android Studio/emulator.
2. Từ thư mục này tạo các file platform còn thiếu:

```powershell
flutter create .
```

3. Cài dependency và chạy app:

```powershell
flutter pub get
flutter run
```

## Địa chỉ backend

Mặc định app dùng:

- Android emulator: `http://10.0.2.2:8000`
- iOS simulator: `http://127.0.0.1:8000`

Khi chạy trên điện thoại thật, sửa `defaultApiBase` trong `lib/main.dart` thành IP LAN của máy chạy backend, ví dụ `http://192.168.1.10:8000`. Backend cần chạy với:

```powershell
uvicorn backend.app.main:app --host 0.0.0.0 --reload
```

Nếu Android không gọi được HTTP local, kiểm tra firewall Windows và quyền mạng local.
