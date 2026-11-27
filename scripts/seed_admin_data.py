"""Seed comprehensive, realistic data for admin dashboard tabs."""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.config import ADMIN_EMAIL, APP_VERSION
from backend.app.db.database import Base, SessionLocal, engine
from backend.app.db.models import (
    AiModel,
    ModelEvaluation,
    ScamCategory,
    ScamKeyword,
    ScanFeedback,
    SystemActivityLog,
    TrainingDataset,
    User,
    VisitorDevice,
)
from backend.app.evaluation.benchmark import run_detector_benchmark
from backend.app.services.analysis import analyze_content_payload
from backend.app.services.runtime import GIT_COMMIT


def seed_admin_dashboard_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Find admin user
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        admin_id = admin.id if admin else 1

        # 1. AI Models
        models_data = [
            (
                "ResNet18-PhishGuard v1.2.0",
                "Mô hình ResNet18 fine-tuned nhận diện giao diện lừa đảo, giả mạo ngân hàng & hóa đơn số tích hợp Grad-CAM.",
                True,
            ),
            (
                "PhishVN-HistGB v3.1.0",
                "Mô hình Gradient Boosting phân loại URL độc hại dựa trên 21 đặc trưng từ vựng tập dữ liệu PhishVN.",
                False,
            ),
            (
                "Gemini-VLM-Hybrid v1.0",
                "Mô hình thị giác ngôn ngữ kết hợp (Multimodal CoT) suy luận nguyên nhân lừa đảo và đối chiếu thương hiệu.",
                False,
            ),
        ]
        created_models = []
        for name, desc, active in models_data:
            m = db.query(AiModel).filter(AiModel.version_name == name).first()
            if not m:
                m = AiModel(version_name=name, description=desc, is_active=active)
                db.add(m)
                db.flush()
            created_models.append(m)
        active_model = created_models[0]

        # 2. Model Evaluations (Run actual benchmark)
        existing_evals = db.query(ModelEvaluation).count()
        if existing_evals == 0:
            print("Đang chạy bộ kiểm thử benchmark thực tế để lấy số liệu chuẩn...")
            benchmark_result = run_detector_benchmark(analyze_content_payload)
            ev = ModelEvaluation(
                ai_model_id=active_model.id,
                macro_f1=benchmark_result["macro_f1"],
                recall=benchmark_result["binary"]["recall"],
                false_alarm_rate=benchmark_result["binary"]["false_alarm_rate"],
                explanation_usefulness=0.92,
            )
            db.add(ev)
            db.flush()

            # Thêm 1 đánh giá lịch sử phiên bản trước để thấy biểu đồ tiến triển
            prev_model = created_models[1]
            prev_ev = ModelEvaluation(
                ai_model_id=prev_model.id,
                macro_f1=0.7850,
                recall=0.8120,
                false_alarm_rate=0.0840,
                explanation_usefulness=0.8500,
                evaluated_at=datetime.utcnow() - timedelta(days=14),
            )
            db.add(prev_ev)

        # 3. Training Datasets
        categories = {c.code: c.id for c in db.query(ScamCategory).all()}
        if db.query(TrainingDataset).count() == 0:
            sample_datasets = [
                ("uploads/dataset_samples/sample_bill_vcb_fake.jpg", "fake_invoice", True, True),
                ("uploads/dataset_samples/sample_login_bidv_phish.png", "phishing_screenshot", True, True),
                ("uploads/dataset_samples/sample_congan_threat_sms.png", "sms_scam", True, True),
                ("uploads/dataset_samples/sample_vietin_auth_redirect.jpg", "payment_redirect", True, False),
                ("uploads/dataset_samples/sample_shopee_job_telegram.png", "impersonation", True, True),
                ("uploads/dataset_samples/sample_mbbank_biometric_scam.png", "phishing_screenshot", False, True),
                ("uploads/dataset_samples/sample_zalopay_cashback_fake.jpg", "payment_redirect", True, True),
                ("uploads/dataset_samples/sample_vnpost_parcel_fee.jpg", "fake_invoice", True, False),
            ]
            for url, cat_code, anon, ver in sample_datasets:
                cat_id = categories.get(cat_code)
                db.add(
                    TrainingDataset(
                        image_url=url,
                        scam_category_id=cat_id,
                        is_anonymized=anon,
                        is_verified=ver,
                        uploaded_by=admin_id,
                    )
                )

        # 4. Scam Keywords
        keywords_to_seed = [
            ("xác thực sinh trắc học khẩn cấp", "phishing", 35),
            ("cập nhật thông tin ngân hàng ngay", "phishing", 30),
            ("liên kết nhận quà tri ân", "phishing", 25),
            ("lệnh phong tỏa tài sản", "urgent_account_threat", 40),
            ("tài khoản sẽ bị tạm khóa sau 24h", "urgent_account_threat", 35),
            ("viện kiểm sát nhân dân tối cao", "impersonation", 35),
            ("cục an ninh mạng quốc gia", "impersonation", 35),
            ("bộ công an thông báo vi phạm", "impersonation", 35),
            ("tuyển cộng tác viên shopee", "job_scam", 30),
            ("việc nhẹ lương cao tại nhà", "job_scam", 30),
            ("làm nhiệm vụ xem video nhận tiền", "job_scam", 25),
            ("nạp tiền hoàn gốc kèm hoa hồng", "job_scam", 35),
            ("phí hoàn tất thủ tục giải ngân", "fake_invoice", 30),
            ("hóa đơn chuyển tiền thành công", "fake_invoice", 20),
            ("phí bảo hiểm khoản vay cá nhân", "fake_invoice", 30),
        ]
        for kw, cat, weight in keywords_to_seed:
            if not db.query(ScamKeyword).filter(ScamKeyword.keyword == kw).first():
                db.add(ScamKeyword(keyword=kw, category=cat, weight=weight))

        # 5. Scan Feedback
        if db.query(ScanFeedback).count() < 10:
            feedbacks = [
                (
                    "correct",
                    "nguy_hiem",
                    92,
                    "image",
                    "Hoa_don_chuyen_khoan_VCB.jpg",
                    "Phát hiện rất chuẩn bill giả mạo số tiền và lệch phông chữ.",
                    ["xác thực sinh trắc học", "mã otp"],
                ),
                (
                    "false_alarm",
                    "nghi_ngo",
                    48,
                    "url",
                    "https://portal.hcmut.edu.vn/auth",
                    "Đây là cổng đăng nhập trường ĐH Bách Khoa chính thức, không phải lừa đảo.",
                    ["đăng nhập tài khoản"],
                ),
                (
                    "correct",
                    "nguy_hiem",
                    85,
                    "text",
                    "Tin nhắn từ đầu số lạ",
                    "Đúng chiêu trò dọa phạt nguội và yêu cầu chuyển tiền vào tài khoản cá nhân.",
                    ["bộ công an", "lệnh phong tỏa"],
                ),
                (
                    "missed_scam",
                    "an_toan",
                    15,
                    "image",
                    "qr_nap_the_game.png",
                    "Mã QR này quét ra trang lừa thẻ cào Zing nhưng hệ thống báo an toàn.",
                    [],
                ),
                (
                    "correct",
                    "nguy_hiem",
                    96,
                    "pdf",
                    "Giay_trieu_tap_CAND.pdf",
                    "Văn bản giả mạo công an rất tinh vi, may mắn hệ thống đã cảnh báo đỏ.",
                    ["viện kiểm sát", "phong tỏa tài khoản"],
                ),
            ]
            for verdict, pred_lvl, score, src, fname, note, terms in feedbacks:
                db.add(
                    ScanFeedback(
                        verdict=verdict,
                        predicted_level=pred_lvl,
                        risk_score=score,
                        source_type=src,
                        original_filename=fname,
                        note=note,
                        evidence_snapshot={"highlighted_terms": terms, "urls": []},
                        review_status="reviewed" if verdict == "correct" else "pending",
                    )
                )

        # 6. Visitor Devices with coordinates in Vietnam
        existing_devices = db.query(VisitorDevice).all()
        # Ensure devices have coordinates for Leaflet map display
        coords_vn = [
            (21.0285, 105.8542, "Hà Nội", "Windows 11", "Chrome 128"),
            (10.8231, 106.6297, "TP. Hồ Chí Minh", "macOS Sonoma", "Safari 17"),
            (16.0544, 108.2022, "Đà Nẵng", "Windows 10", "Edge 126"),
            (10.0452, 105.7469, "Cần Thơ", "Android 14", "Chrome Mobile"),
            (20.8449, 106.6881, "Hải Phòng", "iOS 17.5", "Mobile Safari"),
            (12.2388, 109.1967, "Nha Trang", "Windows 11", "Firefox 129"),
            (21.5942, 105.8482, "Thái Nguyên", "Ubuntu Linux", "Chrome 127"),
            (11.9404, 108.4583, "Đà Lạt", "macOS Sequoia", "Chrome 128"),
        ]
        for i, (lat, lng, city, platform, browser) in enumerate(coords_vn):
            device_id = f"demo-device-vn-{i+1}"
            dev = db.query(VisitorDevice).filter(VisitorDevice.device_id == device_id).first()
            if not dev:
                dev = VisitorDevice(
                    device_id=device_id,
                    device_name=f"Máy trạm {city} (#{i+1})",
                    platform=platform,
                    browser=browser,
                    user_agent=f"Mozilla/5.0 ({platform}) {browser}",
                    ip_address=f"113.161.{10+i}.{45+i*3}",
                    latitude=lat,
                    longitude=lng,
                    location_accuracy=15.0,
                    location_permission="granted",
                    visit_count=12 + i * 5,
                )
                db.add(dev)

        # 7. System Activity Logs
        if db.query(SystemActivityLog).count() == 0:
            logs = [
                ("admin_login", f"Admin [{ADMIN_EMAIL}] đăng nhập hệ thống thành công qua JWT session."),
                ("model_benchmark", f"Thực thi bộ benchmark tự động: đạt Macro F1 cao trên tập dữ liệu kiểm thử."),
                ("keyword_sync", "Cập nhật 15 quy tắc từ khóa lừa đảo mới vào cơ chế Risk Engine thời gian thực."),
                ("dataset_curation", "Xác thực và phân loại 8 mẫu dữ liệu huấn luyện mới vào thư viện Dataset."),
                ("system_config", f"Khởi động hệ thống v{APP_VERSION} ({GIT_COMMIT}) với chế độ SQLite/FastAPI sẵn sàng."),
            ]
            for action, desc in logs:
                db.add(
                    SystemActivityLog(
                        admin_id=admin_id,
                        action_type=action,
                        description=desc,
                    )
                )

        db.commit()
        print("Đã hoàn tất điền số liệu mẫu cho toàn bộ 7 mục quản trị!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_admin_dashboard_data()
