# Vietnamese Scam Detection - Image Module (Scaffold)

Module kiểm tra hình ảnh (OCR + risk scoring rule-based) cho hệ thống phát hiện
lừa đảo tiếng Việt. Kết nối MySQL để lưu lịch sử kiểm tra.

## Cấu trúc project

```
scam-detector/
├── backend/
│   └── app/
│       ├── main.py          # Backend FastAPI, các endpoint
│       ├── ai/
│       │   ├── train_image_model.py # Training image classifier
│       │   └── phishing_model.py    # AI inference khi backend nhận ảnh
│       ├── ocr/             # Trích văn bản từ ảnh
│       ├── risk/            # Tính risk score từ văn bản
│       ├── visual/          # Phân tích EXIF, ELA, deepfake
│       └── db/              # Kết nối và model database
├── frontend/
│   └── index.html            # Giao diện web (HTML/CSS/JS)
├── schema.sql                # Schema MySQL (chạy 1 lần để tạo DB)
├── requirements.txt
└── .env.example
```

## Cài đặt

### Cách nhanh trên Windows

- Lần đầu: nhấp đúp `SETUP_PROJECT.bat`.
- Mỗi lần mở dự án: nhấp đúp `START_PROJECT.bat`.
- Script tự mở backend, frontend và trang web `http://127.0.0.1:5173/`.
- Để tắt: đóng hai cửa sổ **Scam Detector - Backend** và **Scam Detector - Frontend**.

Nếu dùng dòng lệnh:

```bat
cd /d D:\scam-detector
START_PROJECT.bat
```

Các bước bên dưới dành cho trường hợp cần cài hoặc chạy thủ công.

### 1. Cài MySQL và tạo database

```bash
mysql -u root -p < schema.sql
```

### 2. Cài Tesseract OCR + gói tiếng Việt (bắt buộc cho OCR)

Ubuntu/Debian:

```bash
sudo apt-get install tesseract-ocr tesseract-ocr-vie
```

macOS:

```bash
brew install tesseract tesseract-lang
```

### 3. Cài Python packages

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Cấu hình kết nối DB

```bash
cp .env.example .env
# sửa .env với thông tin MySQL thật của bạn
```

### 5. Chạy server

```bash
uvicorn backend.app.main:app --reload
```

Server chạy tại `http://localhost:8000`. Xem docs tự động (Swagger UI) tại
`http://localhost:8000/docs`.

### 6. Bật đăng nhập Google (tùy chọn)

Tạo OAuth Client ID loại **Web application** trong Google Cloud Console, sau đó
thêm hai JavaScript origin dùng khi chạy local:

- `http://localhost:5173`
- `http://127.0.0.1:5173`

Điền cùng một Client ID vào `.env`:

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
VITE_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

Khởi động lại cả backend và frontend sau khi sửa `.env`. Frontend nhận Google ID
token, backend xác minh chữ ký và audience trước khi tạo tài khoản nội bộ. Không
dùng access token hoặc thông tin email từ frontend làm bằng chứng đăng nhập.

## Test nhanh

```bash
curl -X POST "http://localhost:8000/check-image" \
  -F "file=@/duong/dan/anh_hoa_don.jpg" \
  -F "user_id=1"
```

Xem lịch sử:

```bash
curl "http://localhost:8000/history/1"
```

## Về phần "kiểm tra ảnh giả mạo" (visual forensics)

Endpoint `/check-image` giờ trả về **2 điểm rủi ro riêng biệt**, cộng lại thành
`risk_score` tổng:

- `text_risk_score`: dựa trên NỘI DUNG CHỮ trong ảnh (OCR + từ khóa lừa đảo)
- `visual_risk_score`: dựa trên BẢN THÂN TẤM ẢNH có dấu hiệu bị giả mạo không, gồm:
  - **EXIF**: ảnh có dấu vết qua phần mềm chỉnh sửa (Photoshop, Canva...) không
  - **ELA (Error Level Analysis)**: có vùng nào trong ảnh bị dán đè/chỉnh sửa cục
    bộ không (vd: sửa số tiền trong ảnh chuyển khoản). **Lưu ý: cần ảnh JPEG có
    texture thật để chính xác — ảnh nền phẳng/đơn giản sẽ không cho tín hiệu tốt.**
  - **Deepfake detection**: có 2 chế độ:
    - _Model thật_ (khuyên dùng): cần cài `transformers` + `torch` và có mạng để
      tải model lần đầu. Bỏ comment 2 dòng cuối trong `requirements.txt`.
    - _Heuristic fallback_ (mặc định khi chưa cài model thật): phân tích miền tần
      số FFT, **độ tin cậy THẤP, dễ báo sai (false positive) với ảnh có nhiều cạnh
      sắc như văn bản/đồ họa**. Chỉ nên dùng để demo/test nhanh, KHÔNG dùng làm căn
      cứ kết luận cuối trong sản phẩm thật.

## Roadmap nâng cấp

1. **Risk engine**: thay rule-based bằng model ML thật (fine-tune PhoBERT trên
   dữ liệu lừa đảo tiếng Việt đã gán nhãn) — giữ nguyên interface `analyze_text()`
   nên không cần đổi phần còn lại của hệ thống.
2. **OCR**: cân nhắc chuyển từ Tesseract sang PaddleOCR nếu độ chính xác tiếng
   Việt chưa đủ tốt.
3. **Visual forensics**: thêm module kiểm tra layout/metadata cho hóa đơn giả,
   và model phát hiện deepfake cho ảnh chân dung.
4. **Auth**: bổ sung luồng liên kết Google với tài khoản email đã tồn tại sau khi
   người dùng xác thực lại bằng mật khẩu.
5. **Từ khóa động**: chuyển `SCAM_KEYWORDS` từ hardcode sang load từ bảng
   `scam_keywords` trong MySQL để admin cập nhật được qua dashboard.

## Phân tích URL trong nội dung OCR bằng PhishVN

Backend tích hợp **PhishVN v3.1.0** theo đúng phạm vi của bộ dữ liệu:

1. Tesseract trích văn bản từ ảnh.
2. `phishvn_url_model.py` tìm URL/tên miền trong văn bản OCR.
3. Mỗi URL được chuyển thành 21 đặc trưng lexical theo schema CompPhish.
4. HistGradientBoosting dự đoán mức phishing/abuse và trả về URL, xác suất,
   điểm rủi ro cùng các dấu hiệu dễ hiểu cho giao diện.
5. Risk Engine từ khóa hiện tại tiếp tục phân tích câu tiếng Việt; PhishVN không
   được dùng như một model phân loại SMS/email vì bản phát hành này chỉ có nhãn URL.

Model tham chiếu có sẵn tại
`PhishVN A Time-Stamped Vietnamese URL Phishing Dat/p1a_results_bundle/models/HistGB_seed0.joblib`.
Để huấn luyện lại theo official gold/silver temporal split:

```bash
python -m backend.app.ai.train_phishvn_url_model
```

Model mới được lưu tại `models/phishvn_url_histgb.joblib` và sẽ được backend ưu
tiên tự động. Có thể chỉ định model khác bằng `PHISHVN_MODEL_PATH`.

Lưu ý: điểm model là tín hiệu cảnh báo, không phải bằng chứng chắc chắn. Dataset
có cả credential phishing và các dạng abuse khác; ngưỡng ứng dụng được đặt bảo
thủ để giảm cảnh báo sai.

Nguồn dữ liệu: **PhishVN v3.1.0**, DOI `10.17632/b97hxbxtpd.4`, giấy phép CC BY 4.0.
