-- Database cho hệ thống phát hiện lừa đảo tiếng Việt
CREATE DATABASE IF NOT EXISTS scam_detector CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE scam_detector;

-- Bảng người dùng (users & SMEs & admin dùng chung, phân biệt qua role)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role ENUM('user', 'sme', 'admin') NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Bảng lưu từng lượt kiểm tra (text, image, url, audio)
CREATE TABLE IF NOT EXISTS scan_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    input_type ENUM('text', 'image', 'url', 'audio') NOT NULL,
    original_filename VARCHAR(512),           -- tên file gốc nếu là ảnh/audio
    extracted_text LONGTEXT,                  -- văn bản OCR trích được (nếu là ảnh)
    risk_score INT NOT NULL,                  -- 0-100, điểm tổng hợp (text + visual)
    text_risk_score INT DEFAULT 0,            -- điểm rủi ro riêng từ phân tích văn bản OCR
    visual_risk_score INT DEFAULT 0,          -- điểm rủi ro riêng từ phân tích hình ảnh (EXIF+ELA+deepfake)
    risk_level ENUM('an_toan', 'nghi_ngo', 'nguy_hiem') NOT NULL,
    scam_type VARCHAR(100),                   -- phishing, fake_invoice, impersonation, deepfake...
    explanation TEXT,                         -- giải thích lý do cảnh báo
    highlighted_terms JSON,                   -- danh sách cụm từ/URL bất thường được highlight
    visual_flags JSON,                        -- danh sách cảnh báo từ visual forensics (EXIF/ELA/deepfake)
    suggested_action TEXT,                    -- hành động an toàn được đề xuất
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Bảng sự cố dành cho SMEs quản lý (dashboard)
CREATE TABLE IF NOT EXISTS incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sme_user_id INT NOT NULL,
    scan_history_id INT NOT NULL,
    status ENUM('moi', 'dang_xu_ly', 'da_xu_ly', 'bo_qua') NOT NULL DEFAULT 'moi',
    assigned_to VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sme_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (scan_history_id) REFERENCES scan_history(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Bảng từ điển các cụm từ/pattern lừa đảo tiếng Việt (dùng cho rule-based engine + có thể dùng làm seed data huấn luyện)
CREATE TABLE IF NOT EXISTS scam_keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    keyword VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,   -- phishing, fake_invoice, impersonation...
    weight INT NOT NULL DEFAULT 10,   -- mức độ đóng góp vào risk score
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Seed data mẫu cho từ khóa lừa đảo phổ biến tiếng Việt
INSERT INTO scam_keywords (keyword, category, weight) VALUES
('chuyển khoản gấp', 'phishing', 15),
('tài khoản bị khóa', 'phishing', 15),
('nhấp vào link', 'phishing', 12),
('xác minh ngay', 'phishing', 12),
('trúng thưởng', 'phishing', 15),
('nợ xấu', 'impersonation', 15),
('cơ quan công an', 'impersonation', 20),
('shipper', 'fake_invoice', 10),
('phí vận chuyển', 'fake_invoice', 10),
('mã OTP', 'phishing', 20);
