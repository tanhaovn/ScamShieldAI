---
title: Scam Shield AI
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Vietnamese Scam Detection - Multi-source Scanner

Hệ thống hỗ trợ phát hiện dấu hiệu lừa đảo tiếng Việt từ ảnh, mã QR, tin nhắn,
URL và tài liệu PDF. Khách có thể dùng ngay và lưu lịch sử trong `localStorage`;
người dùng đăng nhập được lưu lịch sử riêng theo tài khoản trong database.

## Cấu trúc project

```
scam-detector/
├── backend/app/             # FastAPI, AI/OCR, risk engine và database
├── frontend-react/          # React + Vite frontend
├── models/                  # Model đã huấn luyện và metrics
├── datasets/                # Dữ liệu nghiên cứu/tham chiếu
├── database/                # Schema và tài nguyên database
├── tests/                   # Test tự động và fixture
├── scripts/                 # Script đánh giá, kiểm thử và chuẩn bị dữ liệu
├── tessdata/                # Dữ liệu ngôn ngữ Tesseract
├── Dockerfile
├── render.yaml
├── requirements.txt
└── .env.example
```

### Cấu trúc backend

```text
backend/app/
├── main.py                 # Khởi tạo FastAPI, middleware và static files
├── api/
│   ├── router.py           # Đăng ký toàn bộ feature router
│   ├── dependencies.py     # Dependency xác thực dùng chung
│   └── routers/            # auth, scans, history, feedback, devices, admin, system
├── core/                   # Cấu hình môi trường và bảo mật JWT/mật khẩu
├── schemas/                # Pydantic request schemas theo từng chức năng
├── services/               # Pipeline phân tích, runtime info và khởi tạo dữ liệu
├── db/                     # SQLAlchemy engine, session và ORM models
├── ai/                     # Model ảnh, URL, VLM và domain intelligence
├── ocr/                    # OCR và đánh dấu vùng đáng ngờ
├── risk/                   # Chấm điểm và tạo giải thích
├── visual/                 # EXIF, ELA, deepfake và QR
├── document/               # Xử lý PDF
└── evaluation/             # Benchmark/regression detector
```

Các URL API cũ được giữ nguyên sau khi tách router. Swagger nhóm API theo chức
năng tại `http://127.0.0.1:8000/docs`.

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
mysql -u root -p < database/schema.sql
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

### 6. Tài khoản khách, người dùng và Admin

- Khách có thể kiểm tra ngay, không cần đăng nhập; kết quả lưu bằng `localStorage`
  trên trình duyệt hiện tại.
- Người dùng có thể đăng ký/đăng nhập. Kết quả ảnh, tin nhắn, URL và PDF sau khi
  đăng nhập được lưu theo `user_id` và xem lại tại trang Lịch sử.
- Lịch sử khách không đồng bộ sang trình duyệt hoặc thiết bị khác.
- Chỉ Admin được truy cập Dataset, AI Models, đánh giá và system logs.
- Tài khoản mặc định cho môi trường demo được tạo lúc backend khởi động; hãy đổi
  mật khẩu và `JWT_SECRET` trước khi triển khai thật.

## Test nhanh

```bash
curl -X POST "http://localhost:8000/check-image" \
  -F "file=@/duong/dan/anh_hoa_don.jpg"
```

Các nguồn đầu vào khác:

```bash
curl -X POST "http://localhost:8000/check-text" \
  -H "Content-Type: application/json" \
  -d '{"text":"Tài khoản sẽ bị khóa, hãy xác minh OTP ngay..."}'

curl -X POST "http://localhost:8000/check-url" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/login"}'

curl -X POST "http://localhost:8000/check-document" \
  -F "file=@/duong/dan/giay_bao_thanh_toan.pdf"
```

- Ảnh được OCR và tự động giải mã QR; nội dung QR không bị mở tự động.
- PDF tối đa 15 MB và xử lý 10 trang đầu. PDF có lớp chữ được trích trực tiếp;
  PDF scan được chuyển thành ảnh để OCR và quét QR.

Kết quả khách do frontend lưu trong `localStorage`. Người dùng hoặc Admin đã đăng
nhập lấy lịch sử tài khoản bằng JWT:

```bash
curl -H "Authorization: Bearer <ADMIN_JWT>" \
  "http://localhost:8000/history/1"
```

## Black-box regression

Bộ black-box gọi ứng dụng đang chạy hoàn toàn qua HTTP, bao phủ system API,
validation, text, URL, xác thực/phân quyền, admin, feedback, PDF, ảnh và truy cập
đồng thời cơ bản:

```powershell
python scripts/run_black_box_suite.py `
  --base-url http://127.0.0.1:8765 `
  --admin-email <admin-email> `
  --admin-password <admin-password> `
  --json-out .pytest-work/black-box-results.json
```

Script xuất kết quả chi tiết ra file JSON được truyền qua `--json-out`.

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

### Giải thích dự đoán ResNet18 bằng Grad-CAM

Khi model ảnh khả dụng, `/check-image` dùng `pytorch-grad-cam` trên lớp tích chập
cuối `model.layer4[-1]` và đầu ra của lớp được ResNet18 dự đoán (`phishing` hoặc
`legitimate`). API trả thêm
`image_model_gradcam.image_url`; giao diện hiển thị ảnh gốc cạnh bản đồ nhiệt để
cho biết vùng nào đóng góp mạnh vào điểm phishing. Vùng đỏ/vàng chỉ thể hiện nơi
model tập trung, không phải bounding box vật thể và không tự chứng minh ảnh là
lừa đảo. OCR/highlight vẫn là lớp giải thích riêng cho nội dung chữ.

Thư viện tham khảo: https://github.com/jacobgil/pytorch-grad-cam (MIT). Nếu dùng
trong báo cáo nghiên cứu, trích dẫn theo hướng dẫn của dự án thư viện.

### Giải thích ngữ nghĩa bằng Vision-Language Model

Grad-CAM chỉ định vị pixel tác động đến lớp ResNet18; nó không tự hiểu một vùng
chứa con chó, biểu mẫu đăng nhập hay yêu cầu chuyển tiền. Để có lời giải thích
"tại sao", backend có thể gửi **ảnh gốc + ảnh Grad-CAM** cho một VLM và yêu cầu
trả về bằng chứng có cấu trúc: chi tiết quan sát được, vị trí và cơ chế rủi ro.

```env
USE_VLM_ANALYZER=true
VLM_MODEL_ID=HuggingFaceTB/SmolVLM-500M-Instruct
GEMINI_API_KEY=your_google_ai_studio_key
GEMINI_VISION_MODEL=gemini-3.5-flash-lite
VLM_DEVICE=auto
```

Lần chạy đầu sẽ tải model từ Hugging Face. Có thể thay bằng một model VLM mạnh
hơn nếu máy có đủ RAM/GPU. Khi VLM chưa bật hoặc nạp thất bại, API vẫn dùng luật
để tính điểm dự phòng nhưng giao diện **không trình bày câu luật đó như lời giải
thích của AI**; nó báo rõ rằng chỉ có bản đồ Grad-CAM, chưa có giải thích ngữ nghĩa.

## Roadmap nâng cấp

1. **Risk engine**: thay rule-based bằng model ML thật (fine-tune PhoBERT trên
   dữ liệu lừa đảo tiếng Việt đã gán nhãn) — giữ nguyên interface `analyze_text()`
   nên không cần đổi phần còn lại của hệ thống.
2. **OCR**: cân nhắc chuyển từ Tesseract sang PaddleOCR nếu độ chính xác tiếng
   Việt chưa đủ tốt.
3. **Visual forensics**: thêm module kiểm tra layout/metadata cho hóa đơn giả,
   và model phát hiện deepfake cho ảnh chân dung.
4. **Guest storage**: bổ sung nút xuất/nhập lịch sử cục bộ nếu cần chuyển dữ liệu
   giữa hai thiết bị.
5. **Từ khóa động**: chuyển `SCAM_KEYWORDS` từ hardcode sang load từ bảng
   `scam_keywords` trong MySQL để admin cập nhật được qua dashboard.

## Dataset cần bổ sung

Các luồng QR và PDF hiện tại là bài toán **giải mã/trích xuất**, không cần
dataset mới để chạy. PhishVN đã đảm nhiệm lớp phân tích cấu trúc URL. Dataset
quan trọng nhất cần bổ sung tiếp theo là tập tin nhắn lừa đảo tiếng Việt đã gán
nhãn để thay dần Risk Engine rule-based bằng model NLP.

Schema CSV khuyến nghị:

```text
message_id,message,label,scam_type,source,collected_at,anonymized,verified,split
```

- `label`: `legitimate` hoặc `scam`.
- `scam_type`: giả ngân hàng, giả công an, tuyển dụng, đầu tư, giao hàng, OTP...
- Bắt buộc ẩn danh số điện thoại, tài khoản ngân hàng, CCCD, email và tên thật.
- Chia train/validation/test theo nguồn hoặc thời gian; không để tin gần trùng
  lặp xuất hiện ở cả train và test.
- Dataset hóa đơn/biên lai chỉ cần khi muốn huấn luyện hoặc đo chính xác OCR;
  nó không tự giúp phân loại hóa đơn có phải lừa đảo hay không.

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
`datasets/phishvn/p1a_results_bundle/models/HistGB_seed0.joblib`.
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

## Đối chiếu nguồn độc lập bằng Google Safe Browsing

Backend có thể đối chiếu URL trích từ ảnh, QR, PDF hoặc nội dung nhập trực tiếp
với **Google Safe Browsing v5**. Đây là lớp xác nhận độc lập bổ sung cho model
PhishVN: nếu Google trả về một threat match, hệ thống nâng URL lên mức nguy hiểm
và hiển thị riêng nguồn `Google Safe Browsing`; cảnh báo do các model nội bộ tạo
ra không được gắn nhãn Google.

1. Bật Safe Browsing API trong Google Cloud Console và tạo API key.
2. Điền `GOOGLE_SAFE_BROWSING_API_KEY` trong `.env`.
3. Khởi động lại backend. Nếu không có key hoặc API tạm lỗi, hệ thống vẫn dùng
   PhishVN và các lớp phân tích cục bộ như trước.

Safe Browsing API chỉ dành cho mục đích **phi thương mại**; sản phẩm thương mại
phải dùng Google Web Risk hoặc thỏa thuận phù hợp. URL được kiểm tra sẽ được gửi
tới Google. Không có kết quả khớp không đồng nghĩa URL chắc chắn an toàn. Kết quả
được cache theo thời hạn API trả về và cảnh báo URL nguy hiểm không được giữ quá
30 phút nếu chưa đối chiếu lại, theo điều khoản của Google.

Tài liệu chính thức:

- Tổng quan: https://developers.google.com/safe-browsing/
- API v5 `urls.search`: https://developers.google.com/safe-browsing/reference/rest/v5/urls/search
- Điều khoản sử dụng: https://developers.google.com/safe-browsing/terms

### Huấn luyện model ảnh không bị leakage

Model ResNet18 ảnh không được chia ngẫu nhiên từng file. Các ảnh cùng nguồn hoặc
cùng template phải nằm trong đúng một split; nếu không, ảnh biến thể của cùng một
mẫu có thể lọt vào test và làm metric tăng giả tạo.

Tạo manifest mẫu từ thư mục ảnh:

```bash
python -m backend.app.ai.prepare_image_manifest --dataset phishing_dataset
```

Sau đó điền `phishing_dataset/manifest.csv` với các cột:

```text
path,label,source,template_id,split
```

- `source`: tên nguồn/collection cụ thể (ví dụ `public_phishpedia_01`,
  `synthetic_bank_template_01`, `anonymized_user_02`), không chỉ ghi chung
  `public` hoặc `synthetic`. Một source chỉ được xuất hiện trong đúng một split.
- `template_id`: mã chung cho các ảnh cùng thiết kế/template; ảnh tự tạo từ cùng
  một template phải dùng cùng mã.
- `split`: chỉ dùng `train`, `validation`, hoặc `test`.

Huấn luyện:

```bash
python -m backend.app.ai.train_image_model \
  --dataset phishing_dataset \
  --manifest phishing_dataset/manifest.csv
```

Script sẽ dừng nếu có hash ảnh trùng giữa các split hoặc một cặp
`source/template_id` xuất hiện ở nhiều split. Augmentation chỉ chạy trên train;
validation/test giữ nguyên phân phối ảnh. Model được chọn theo `validation_macro_f1`
và lưu thêm `models/phishing_resnet18.metrics.json` gồm macro-F1, balanced accuracy
và confusion matrix trên test độc lập.

Thiết kế này giúp đo khả năng tổng quát hóa sang nguồn/template chưa thấy, nhưng
không đảm bảo model tự “suy nghĩ” như con người. Model chỉ có thể học các tín hiệu
đã xuất hiện trong dữ liệu; muốn kết luận ảnh mới tổng quát tốt cần test độc lập,
không dùng lại template và kiểm tra thêm false positive/false negative.
