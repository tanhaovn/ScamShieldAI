# -*- coding: utf-8 -*-
"""
Script to generate official Vietnamese C1SE.06_ProductBacklog_SFDS_v1.0_VI.xlsx
Capstone Project: SFDS (Hệ Thống Cảnh Báo và Phát Hiện Lừa Đảo Trực Tuyến Đa Phương Thức Có Giải Thích)
Team: C1SE.06 - CMU-SE 450 - Đại học Duy Tân
Output: D:\scam-detector\TAILIEU_CAPSTONE_C1SE06_SFDS\3. PRODUCT BACKLOG & USER STORY\C1SE.06_ProductBacklog_SFDS_v1.0_VI.xlsx
"""

import os
import xlsxwriter

def create_backlog_vi():
    output_dir = r"D:\scam-detector\TAILIEU_CAPSTONE_C1SE06_SFDS\3. PRODUCT BACKLOG & USER STORY"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, "C1SE.06_ProductBacklog_SFDS_v1.0_VI.xlsx")
    workbook = xlsxwriter.Workbook(filename)

    font_family = "Times New Roman"

    title_fmt = workbook.add_format({
        'font_name': font_family,
        'font_size': 16,
        'bold': True,
        'font_color': '#000000',
        'align': 'left',
        'valign': 'vcenter'
    })

    subtitle_fmt = workbook.add_format({
        'font_name': font_family,
        'font_size': 11,
        'italic': True,
        'font_color': '#444444',
        'align': 'left',
        'valign': 'vcenter'
    })

    header_fmt = workbook.add_format({
        'font_name': font_family,
        'font_size': 11,
        'bold': True,
        'font_color': '#000000',
        'bg_color': '#D9D9D9',
        'border': 1,
        'border_color': '#000000',
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True
    })

    cell_center = workbook.add_format({
        'font_name': font_family,
        'font_size': 10.5,
        'border': 1,
        'border_color': '#000000',
        'align': 'center',
        'valign': 'top'
    })

    cell_left = workbook.add_format({
        'font_name': font_family,
        'font_size': 10.5,
        'border': 1,
        'border_color': '#000000',
        'align': 'left',
        'valign': 'top',
        'text_wrap': True
    })

    cell_bold_left = workbook.add_format({
        'font_name': font_family,
        'font_size': 10.5,
        'bold': True,
        'border': 1,
        'border_color': '#000000',
        'align': 'left',
        'valign': 'top'
    })

    cell_right = workbook.add_format({
        'font_name': font_family,
        'font_size': 10.5,
        'border': 1,
        'border_color': '#000000',
        'align': 'right',
        'valign': 'top'
    })

    priority_high = workbook.add_format({
        'font_name': font_family,
        'font_size': 10.5,
        'bold': True,
        'border': 1,
        'border_color': '#000000',
        'align': 'center',
        'valign': 'top',
        'bg_color': '#FCE4D6',
        'font_color': '#C00000'
    })

    status_done = workbook.add_format({
        'font_name': font_family,
        'font_size': 10.5,
        'bold': True,
        'border': 1,
        'border_color': '#000000',
        'align': 'center',
        'valign': 'top',
        'bg_color': '#E2EFDA',
        'font_color': '#375623'
    })

    status_in_progress = workbook.add_format({
        'font_name': font_family,
        'font_size': 10.5,
        'bold': True,
        'border': 1,
        'border_color': '#000000',
        'align': 'center',
        'valign': 'top',
        'bg_color': '#FFF2CC',
        'font_color': '#7F6000'
    })

    status_todo = workbook.add_format({
        'font_name': font_family,
        'font_size': 10.5,
        'border': 1,
        'border_color': '#000000',
        'align': 'center',
        'valign': 'top',
        'bg_color': '#F2F2F2',
        'font_color': '#595959'
    })

    sec_header_fmt = workbook.add_format({
        'font_name': font_family,
        'font_size': 12,
        'bold': True,
        'font_color': '#000000',
        'bg_color': '#BFBFBF',
        'border': 1,
        'border_color': '#000000',
        'align': 'left',
        'valign': 'vcenter'
    })

    total_fmt = workbook.add_format({
        'font_name': font_family,
        'font_size': 11,
        'bold': True,
        'font_color': '#000000',
        'bg_color': '#D9D9D9',
        'border': 1,
        'border_color': '#000000',
        'align': 'right',
        'valign': 'vcenter'
    })

    # ==========================================
    # SHEET 1: TỔNG QUAN DỰ ÁN
    # ==========================================
    ws_info = workbook.add_worksheet("Tổng quan Dự án")
    ws_info.set_column('A:A', 4)
    ws_info.set_column('B:B', 24)
    ws_info.set_column('C:C', 38)
    ws_info.set_column('D:D', 20)
    ws_info.set_column('E:E', 25)
    ws_info.set_column('F:F', 20)

    ws_info.write('B2', "TỔNG QUAN QUẢN LÝ DỰ ÁN CAPSTONE", title_fmt)
    ws_info.write('B3', "Đại học Duy Tân - Viện Đào tạo & Nghiên cứu Quốc tế - CMU-SE 450", subtitle_fmt)

    ws_info.write('B5', "THÔNG TIN DỰ ÁN", sec_header_fmt)
    ws_info.write('C5', "", sec_header_fmt)
    ws_info.write('D5', "", sec_header_fmt)
    ws_info.write('E5', "", sec_header_fmt)
    ws_info.write('F5', "", sec_header_fmt)

    info_rows = [
        ("Tên dự án", "Hệ Thống Cảnh Báo và Phát Hiện Lừa Đảo Trực Tuyến Đa Phương Thức Có Giải Thích (SFDS)"),
        ("Mã học phần / Lớp", "CMU-SE 450 - Nhóm C1SE.06"),
        ("Năm học / Niên khóa", "2026 / Giai đoạn Đồ án Tốt nghiệp 1"),
        ("Trưởng nhóm dự án", "Phạm Tấn Hào (Mã SV: 29219020823) - phamtanhao1909@gmail.com"),
        ("Giảng viên hướng dẫn", "KS. Hà Mạnh Toàn (lhttuy@gmail.com)"),
        ("Công nghệ cốt lõi", "FastAPI (Python 3.12), React 18 (Vite), PyTorch, Scikit-Learn, Tesseract OCR, MySQL 8.0 / SQLite")
    ]
    for r_idx, (k, v) in enumerate(info_rows, start=6):
        ws_info.write(f'B{r_idx}', k, cell_bold_left)
        ws_info.write(f'C{r_idx}', v, cell_left)
        ws_info.write(f'D{r_idx}', "", cell_left)
        ws_info.write(f'E{r_idx}', "", cell_left)
        ws_info.write(f'F{r_idx}', "", cell_left)

    ws_info.write('B13', "THÀNH VIÊN NHÓM & PHÂN CÔNG TRÁCH NHIỆM", sec_header_fmt)
    ws_info.write('C13', "", sec_header_fmt)
    ws_info.write('D13', "", sec_header_fmt)
    ws_info.write('E13', "", sec_header_fmt)
    ws_info.write('F13', "", sec_header_fmt)

    team_headers = ["Họ và tên thành viên", "Mã sinh viên", "Vai trò dự án", "Địa chỉ Email", "Số điện thoại"]
    for c_idx, h in enumerate(team_headers, start=1):
        ws_info.write(13, c_idx, h, header_fmt)

    team_data = [
        ("Phạm Tấn Hào", "29219020823", "Trưởng nhóm / Scrum Master / Backend Core", "phamtanhao1909@gmail.com", "0961651933"),
        ("Đào Thị Mỹ Nhung", "29209200048", "QA Lead / UI-UX Lead / Quản lý tài liệu", "mynhung150905@gmail.com", "0376415338"),
        ("Trần Hoàng Nhật Nam", "29219423638", "Frontend Developer / Viết tài liệu kỹ thuật", "trannamnhathoang@gmail.com", "0795798736"),
        ("Nguyễn Phan Đức Tuấn", "29211151140", "AI Lead / Full-stack Developer", "ductuan02072005@gmail.com", "0932442770")
    ]
    for r_idx, row in enumerate(team_data, start=14):
        ws_info.write(r_idx, 1, row[0], cell_bold_left)
        ws_info.write(r_idx, 2, row[1], cell_center)
        ws_info.write(r_idx, 3, row[2], cell_left)
        ws_info.write(r_idx, 4, row[3], cell_left)
        ws_info.write(r_idx, 5, row[4], cell_center)

    ws_info.write('B20', "TỔNG KẾT TIẾN ĐỘ CÁC SPRINT", sec_header_fmt)
    ws_info.write('C20', "", sec_header_fmt)
    ws_info.write('D20', "", sec_header_fmt)
    ws_info.write('E20', "", sec_header_fmt)
    ws_info.write('F20', "", sec_header_fmt)

    sprint_headers = ["Sprint", "Thời gian", "Mục tiêu trọng tâm", "Công số dự tính (h)", "Trạng thái"]
    for c_idx, h in enumerate(sprint_headers, start=1):
        ws_info.write(20, c_idx, h, header_fmt)

    sprint_data = [
        ("Sprint 1", "Tuần 1 - Tuần 3", "Thiết lập kiến trúc, Domain Gating, mô hình URL PhishVN & ResNet-18 baseline", 160, "Hoàn thành"),
        ("Sprint 2", "Tuần 4 - Tuần 6", "Động cơ OCR tiếng Việt, quy tắc từ khóa rủi ro, Tổng hợp đồng thuận Consensus", 180, "Hoàn thành"),
        ("Sprint 3", "Tuần 7 - Tuần 9", "Giao diện React quét an toàn, Trực quan hóa suy luận CoT, Lịch sử LocalStorage", 170, "Đang thực hiện"),
        ("Sprint 4", "Tuần 10 - Tuần 12", "Cổng thông tin Quản trị viên, Quản trị Danh sách trắng/đen, Xuất báo cáo", 150, "Cần làm"),
        ("Sprint 5", "Tuần 13 - Tuần 15", "Kiểm thử chịu tải toàn diện, Tăng cường bảo mật, Chuẩn bị bảo vệ Capstone 1", 140, "Cần làm")
    ]
    for r_idx, row in enumerate(sprint_data, start=21):
        ws_info.write(r_idx, 1, row[0], cell_bold_left)
        ws_info.write(r_idx, 2, row[1], cell_center)
        ws_info.write(r_idx, 3, row[2], cell_left)
        ws_info.write(r_idx, 4, row[3], cell_right)
        st = row[4]
        if st == "Hoàn thành":
            ws_info.write(r_idx, 5, st, status_done)
        elif st == "Đang thực hiện":
            ws_info.write(r_idx, 5, st, status_in_progress)
        else:
            ws_info.write(r_idx, 5, st, status_todo)

    ws_info.write(26, 1, "Tổng số giờ công kỹ thuật dự toán", total_fmt)
    ws_info.write(26, 2, "", total_fmt)
    ws_info.write(26, 3, "", total_fmt)
    ws_info.write(26, 4, 800, total_fmt)
    ws_info.write(26, 5, "", total_fmt)

    # ==========================================
    # SHEET 2: PRODUCT BACKLOG
    # ==========================================
    ws_pb = workbook.add_worksheet("Product Backlog")
    
    ws_pb.set_column('A:A', 3)
    ws_pb.set_column('B:B', 10)  # Mã
    ws_pb.set_column('C:C', 28)  # Tiêu đề tính năng
    ws_pb.set_column('D:D', 20)  # Với vai trò là..
    ws_pb.set_column('E:E', 38)  # Tôi muốn ..
    ws_pb.set_column('F:F', 36)  # Để có thể ..
    ws_pb.set_column('G:G', 48)  # Tiêu chí Nghiệm thu (AC)
    ws_pb.set_column('H:H', 22)  # Ghi chú
    ws_pb.set_column('I:I', 10)  # Mức ưu tiên
    ws_pb.set_column('J:J', 16)  # Trạng thái
    ws_pb.set_column('K:K', 14)  # Loại
    ws_pb.set_column('L:L', 12)  # Mã Dự án
    ws_pb.set_column('M:M', 12)  # Sprint
    ws_pb.set_column('N:N', 14)  # Ước lượng\n(Giờ)
    ws_pb.set_column('O:O', 22)  # Người thực hiện

    ws_pb.write('B5', "DANH MỤC PRODUCT BACKLOG", title_fmt)

    headers = [
        "Mã", "Tiêu đề tính năng", "Với vai trò là..", "Tôi muốn ..", "Để có thể ..", 
        "Tiêu chí Nghiệm thu (Acceptance Criteria)", "Ghi chú kỹ thuật", "Mức ưu tiên", "Trạng thái", 
        "Loại", "Mã Dự án", "Sprint", "Ước lượng\n(Giờ)", "Người thực hiện"
    ]
    for c_idx, h in enumerate(headers, start=1):
        ws_pb.write(6, c_idx, h, header_fmt)

    backlog_data = [
        (
            "PB-01",
            "Kiến trúc Dự án & Khung nền tảng Cốt lõi",
            "Kỹ sư Hệ thống",
            "khởi tạo khung máy chủ FastAPI, giao diện React 18 (Vite) và lược đồ CSDL ORM",
            "đội ngũ phát triển có môi trường làm việc thống nhất, ổn định để phát triển các module giám định đa phương thức.",
            "- Ứng dụng FastAPI khởi tạo đầy đủ CORS, Uvicorn và cấu trúc routing.\n- React 18 (Vite) tích hợp sẵn Tailwind CSS.\n- CSDL SQLite cục bộ và SQLAlchemy ORM được cấu hình hoàn chỉnh.\n- Bộ kiểm thử tự động pytest và linter sẵn sàng hoạt động.",
            "Nền tảng kiến trúc cơ sở",
            5, "Hoàn thành", "Tech Spike", "C1SE.06", "Sprint 1", 36, "Phạm Tấn Hào"
        ),
        (
            "PB-02",
            "Xác thực Quản trị viên & Cổng Bảo mật",
            "Quản trị viên",
            "xác thực thông tin định danh và nhận mã phiên làm việc JWT bảo mật",
            "các khu vực quản trị nhạy cảm (dữ liệu, checkpoint mô hình) chỉ dành riêng cho nhân sự được phân quyền.",
            "- Người dùng đại chúng quét tự do không cần đăng nhập.\n- Đăng nhập quản trị viên cấp mã JWT ký số an toàn.\n- Thông tin sai trả về HTTP 401 kèm thông báo lỗi rõ ràng.\n- Cơ chế hết hạn và làm mới token (refresh token) hoạt động chuẩn.",
            "Tuân thủ OWASP ASVS",
            5, "Hoàn thành", "User Story", "C1SE.06", "Sprint 1", 28, "Phạm Tấn Hào"
        ),
        (
            "PB-03",
            "Pipeline Phân tích Từ vựng URL PhishVN",
            "Kỹ sư AI",
            "trích xuất 21 đặc trưng từ vựng từ liên kết khả nghi và phân loại nguy cơ bằng HistGradientBoosting",
            "hệ thống phát hiện ngay lập tức các liên kết độc hại, trang web lừa đảo chiếm đoạt tài khoản và thủ thuật tên miền lừa đảo.",
            "- Trích xuất 21 đặc trưng: độ dài URL, entropy, địa chỉ IP, ký tự punycode, số dấu gạch nối, từ tố nhạy cảm.\n- Mô hình HistGradientBoosting trả về điểm rủi ro chuẩn hóa [0, 1].\n- Thời gian xử lý < 250ms cho mỗi truy vấn liên kết.",
            "Huấn luyện trên 100k+ URL VN",
            5, "Hoàn thành", "User Story", "C1SE.06", "Sprint 1", 48, "Nguyễn Phan Đức Tuấn"
        ),
        (
            "PB-04",
            "Bộ Lọc Cổng Tên Miền & Danh Sách Tin Cậy",
            "Hệ thống",
            "lọc trước tên miền dựa trên danh sách trắng chính thức (.gov.vn, ngân hàng) và danh sách đen đã biết",
            "các cổng thông tin chính phủ không bao giờ bị báo nhầm, và các tên miền lừa đảo đã biết bị chặn đứng ngay lập tức trong 0ms.",
            "- Danh sách trắng nhận diện tên miền ngân hàng/cơ quan nhà nước hợp pháp và khóa an toàn.\n- Danh sách đen nhận diện tên miền lừa đảo và gán điểm nguy hiểm 100 ngay lập tức.\n- Độ trễ tra cứu dưới 10ms.",
            "Tầng lọc Domain Gating",
            5, "Hoàn thành", "User Story", "C1SE.06", "Sprint 1", 24, "Phạm Tấn Hào"
        ),
        (
            "PB-05",
            "Bộ Phân loại Giả mạo Thương hiệu ResNet-18",
            "Kỹ sư AI",
            "phân tích ảnh chụp màn hình tải lên để phát hiện logo thương hiệu làm giả và bố cục thị giác đáng ngờ",
            "hệ thống nhận diện được hành vi mạo danh các tổ chức tài chính lớn tại Việt Nam ngay cả khi văn bản bị biến dạng.",
            "- Mạng ResNet-18 trích xuất đặc trưng thị giác từ ảnh đầu vào.\n- Kỹ thuật hiệu chỉnh nhiệt độ (T=1.8) loại bỏ các xác suất cực đoan thiếu chuẩn hóa.\n- Phân loại chính xác các thương hiệu ngân hàng phổ biến (Vietcombank, MB, Techcombank...).",
            "Kiểm thử trên 5.000+ ảnh",
            4, "Hoàn thành", "User Story", "C1SE.06", "Sprint 1", 44, "Nguyễn Phan Đức Tuấn"
        ),
        (
            "PB-06",
            "Giám định Pháp chứng Thị giác JPEG ELA & EXIF",
            "Chuyên viên Pháp chứng",
            "thực hiện phân tích mức nén ảnh ELA và kiểm tra siêu dữ liệu EXIF máy ảnh",
            "hệ thống phát hiện dấu vết cắt ghép số, sửa đổi số tiền trên hóa đơn chuyển tiền và phần mềm đồ họa can thiệp.",
            "- Tính ma trận sai phân điểm ảnh JPEG ở mức chất lượng 90% để làm nổi bật vùng nén bất thường.\n- Đọc thẻ EXIF để phát hiện dấu vết phần mềm Photoshop hoặc trình chỉnh sửa ảnh số.\n- Gán nhãn cảnh báo vùng chỉnh sửa kèm điểm pháp chứng.",
            "Phát hiện biên lai giả mạo",
            4, "Hoàn thành", "User Story", "C1SE.06", "Sprint 2", 36, "Phạm Tấn Hào"
        ),
        (
            "PB-07",
            "Trích xuất OCR Tiếng Việt & Đóng khung Vùng Chữ",
            "Người dùng",
            "trích xuất nội dung văn bản tiếng Việt có dấu từ hình ảnh và nhận diện tọa độ hộp giới hạn (Bounding Box)",
            "người dùng nhìn thấy chính xác những đoạn văn bản đáng ngờ nào trong ảnh đang bị hệ thống cảnh báo.",
            "- Tesseract OCR trích xuất chuẩn xác văn bản tiếng Việt (vie+eng).\n- Tọa độ [x, y, w, h] của từng từ được tính toán chuẩn theo tỷ lệ ảnh gốc.\n- Tỷ lệ lỗi ký tự (CER) < 8% trên các mẫu ảnh chụp rõ nét.",
            "Tích hợp Tesseract 5.3",
            5, "Hoàn thành", "User Story", "C1SE.06", "Sprint 2", 40, "Nguyễn Phan Đức Tuấn"
        ),
        (
            "PB-08",
            "Bộ Quy tắc Nhận diện Từ khóa Lừa đảo Tiếng Việt",
            "Chuyên viên Bảo mật",
            "quét văn bản trích xuất đối soát với từ điển các thủ đoạn lừa đảo và mẫu Regex nhạy cảm",
            "những từ ngữ kích động tâm lý khẩn cấp, yêu cầu cung cấp OTP hay đe dọa tố tụng đều bị phát hiện kịp thời.",
            "- Từ điển chứa hơn 150 cụm từ lừa đảo tiếng Việt phân loại theo chủ đề.\n- Mẫu Regex nhận diện số tài khoản ngân hàng, mã OTP, số CMND/CCCD.\n- Tính điểm rủi ro từ vựng theo trọng số động.",
            "Từ điển lừa đảo bản địa",
            4, "Hoàn thành", "User Story", "C1SE.06", "Sprint 2", 32, "Đào Thị Mỹ Nhung"
        ),
        (
            "PB-09",
            "Động cơ Suy luận Giải thích Rủi ro CoT (Chain-of-Thought)",
            "Người dùng",
            "nhận được chuỗi giải thích lập luận từng bước thay vì chỉ một con số rủi ro đơn thuần",
            "người dùng hiểu rõ lý do tại sao nội dung này bị coi là lừa đảo và nâng cao nhận thức cảnh giác số.",
            "- Chuỗi suy luận CoT 4 bước: Nhận diện thương hiệu -> Phát hiện bất thường -> Thao túng tâm lý -> Kết luận phân loại.\n- Bầu chọn đồng thuận đa phương thức (Consensus Fusion) dung hòa các tín hiệu AI.\n- Ngôn ngữ giải thích mạch lạc, tự nhiên, dễ tiếp thu cho người phổ thông.",
            "Lõi XAI tạo sự khác biệt",
            5, "Hoàn thành", "User Story", "C1SE.06", "Sprint 2", 42, "Nguyễn Phan Đức Tuấn"
        ),
        (
            "PB-10",
            "Bộ Sinh Khuyến nghị Hành động Khẩn cấp",
            "Người dùng",
            "nhận các bước chỉ dẫn hành động cụ thể ngay khi phát hiện nguy cơ lừa đảo cao",
            "nạn nhân biết cách xử lý ngay lập tức để không bị mất tiền (khóa thẻ, báo công an, đổi mật khẩu).",
            "- Tự động sinh 3 biện pháp ứng phó tức thì phù hợp với loại hình lừa đảo.\n- Cung cấp số điện thoại đường dây nóng của Cục An toàn thông tin và các ngân hàng lớn.\n- Hỗ trợ nút sao chép nhanh cảnh báo để gửi cho người thân.",
            "Hướng dẫn giảm thiểu thiệt hại",
            4, "Hoàn thành", "User Story", "C1SE.06", "Sprint 2", 30, "Trần Hoàng Nhật Nam"
        ),
        (
            "PB-11",
            "Giao diện Quét Đa phương thức Thân thiện (Web Client)",
            "Người dùng",
            "quét nội dung qua nhiều hình thức linh hoạt (ảnh, camera, dán văn bản, URL, tài liệu PDF)",
            "người dùng có thể kiểm tra mọi dấu hiệu lừa đảo trên cùng một giao diện duy nhất một cách nhanh chóng.",
            "- Hỗ trợ kéo thả ảnh (PNG, JPG, WebP) và dán nội dung từ clipboard.\n- Chụp ảnh trực tiếp từ camera trên thiết bị di động.\n- Thanh tiến trình trực quan hiển thị trạng thái quét theo thời gian thực.",
            "Giao diện React 18 SPA",
            5, "Đang thực hiện", "User Story", "C1SE.06", "Sprint 3", 40, "Trần Hoàng Nhật Nam"
        ),
        (
            "PB-12",
            "Đồng hồ Đo Điểm Rủi ro & Bảng Phân rã Trọng số",
            "Người dùng",
            "quan sát điểm rủi ro tổng hợp trực quan (0-100%) và bảng phân bổ điểm thành phần",
            "người dùng nhanh chóng nắm bắt mức độ nguy hiểm thông qua màu sắc và các chỉ số thành phần minh bạch.",
            "- Đồng hồ rủi ro với hiệu ứng chuyển màu: Xanh lá (<40%), Vàng (40-74%), Đỏ (>=75%).\n- Phân rã 3 nhóm rủi ro: Thị giác/Logo (35%), Từ vựng/Tâm lý (40%), Kỹ thuật ngầm (25%).\n- Tương thích tốt trên cả máy tính và màn hình điện thoại.",
            "Thiết kế trực quan UI/UX",
            4, "Đang thực hiện", "User Story", "C1SE.06", "Sprint 3", 38, "Trần Hoàng Nhật Nam"
        ),
        (
            "PB-13",
            "Quản lý Lịch sử Quét An toàn Phía Trình duyệt (LocalStorage)",
            "Người dùng",
            "xem lại các phiên kiểm tra trước đây và xuất dữ liệu báo cáo mà không cần tạo tài khoản",
            "người dùng theo dõi được các mối đe dọa đã gặp trong khi quyền riêng tư cá nhân được bảo vệ tối đa.",
            "- Lưu trữ tối đa 50 bản ghi kiểm tra gần nhất trong localStorage của trình duyệt.\n- Hỗ trợ tìm kiếm theo từ khóa và lọc theo cấp độ rủi ro.\n- Nút xuất dữ liệu ra tệp CSV phục vụ bằng chứng pháp chứng.",
            "Zero-PII bảo vệ riêng tư",
            4, "Đang thực hiện", "User Story", "C1SE.06", "Sprint 3", 26, "Trần Hoàng Nhật Nam"
        ),
        (
            "PB-14",
            "Hộp thoại Đóng góp Ý kiến & Phản hồi Độ chính xác",
            "Người dùng",
            "đóng góp phản hồi về kết quả phân tích của AI (Chính xác, Báo nhầm, Cần cải thiện)",
            "hệ thống thu thập dữ liệu thực tế để đội ngũ kỹ sư AI liên tục tinh chỉnh và nâng cấp mô hình.",
            "- Hộp thoại phản hồi mở nhanh từ trang kết quả thẩm định.\n- Tùy chọn gửi kèm ghi chú chi tiết về tình huống thực tế.\n- Lưu phản hồi vào cơ sở dữ liệu phục vụ tái huấn luyện mô hình.",
            "Vòng lặp phản hồi người dùng",
            3, "Đang thực hiện", "User Story", "C1SE.06", "Sprint 3", 28, "Đào Thị Mỹ Nhung"
        ),
        (
            "PB-15",
            "Bảng Điều khiển Tiếp nhận & Xử lý Sự cố (Admin Incident Triage)",
            "Quản trị viên",
            "theo dõi danh sách các sự cố lừa đảo nghiêm trọng được báo cáo và chuyển trạng thái xử lý",
            "đội ngũ an ninh mạng có thể điều tra sâu và phối hợp ngăn chặn các chiến dịch lừa đảo diện rộng.",
            "- Bảng quản lý sự cố hỗ trợ phân trang, lọc theo trạng thái ('moi', 'dang_xu_ly', 'da_xu_ly').\n- Phân công chuyên viên phụ trách và ghi chú kết quả giám định pháp chứng.\n- Cập nhật trạng thái sự cố theo thời gian thực.",
            "Quy trình xử lý sự cố an ninh",
            4, "Cần làm", "User Story", "C1SE.06", "Sprint 4", 36, "Phạm Tấn Hào"
        ),
        (
            "PB-16",
            "Bảng Thống kê & Giám sát An ninh Mạng Trực tiếp (Threat Intel)",
            "Quản trị viên",
            "quan sát các chỉ số đo lường an ninh trực quan (tổng lượt quét, tỷ lệ lừa đảo, thủ đoạn nổi cộm)",
            "nhóm quản trị nắm bắt được xu hướng tội phạm mạng tại Việt Nam theo từng mốc thời gian.",
            "- Biểu đồ thể hiện biến động số vụ lừa đảo theo ngày/tuần.\n- Danh sách các tổ chức, ngân hàng đang bị mạo danh nhiều nhất.\n- Chỉ số hiệu năng hệ thống (độ trễ phản hồi trung bình, số yêu cầu đồng thời).",
            "Báo cáo phân tích chuyên sâu",
            4, "Cần làm", "User Story", "C1SE.06", "Sprint 4", 34, "Phạm Tấn Hào"
        ),
        (
            "PB-17",
            "Giao diện Quản trị Tập Dữ liệu Huấn luyện & Mô hình AI",
            "Kỹ sư AI",
            "quản lý kho mẫu dữ liệu huấn luyện đã ẩn danh hóa và chuyển đổi phiên bản mô hình AI đang chạy",
            "đội ngũ kỹ thuật có thể triển khai phiên bản mô hình mới (hot-swap) một cách an toàn và tiện lợi.",
            "- Quản trị danh mục mẫu huấn luyện (ảnh, văn bản, nhãn xác thực).\n- Sổ đăng ký mô hình AI (Model Registry) hiển thị các checkpoint và cờ kích hoạt Active.\n- Cập nhật động danh sách từ khóa lừa đảo và trọng số rủi ro trực tiếp trên giao diện.",
            "Quản trị chu kỳ sống AI",
            4, "Cần làm", "User Story", "C1SE.06", "Sprint 4", 30, "Nguyễn Phan Đức Tuấn"
        ),
        (
            "PB-18",
            "Xuất Báo cáo Pháp chứng Định dạng PDF & CSV",
            "Chuyên viên Phân tích",
            "xuất biên bản giám định pháp chứng số chi tiết dạng tệp PDF có dấu chứng thực hoặc tệp CSV",
            "người dùng và doanh nghiệp có tài liệu chính thống để nộp cho cơ quan công an khi tố giác tội phạm.",
            "- Tạo tệp PDF chứa ảnh chụp bằng chứng, vùng khoanh đỏ, bảng điểm và chuỗi giải thích CoT.\n- Đóng dấu thời gian (Timestamp) và mã băm SHA-256 bảo đảm tính toàn vẹn của bằng chứng.\n- Xuất dữ liệu hàng loạt dạng CSV phục vụ kiểm toán.",
            "Tài liệu bằng chứng pháp lý",
            3, "Cần làm", "User Story", "C1SE.06", "Sprint 4", 28, "Đào Thị Mỹ Nhung"
        ),
        (
            "PB-19",
            "Tăng cường Bảo mật, Chống Tấn công DoS & Quản lý Tải",
            "Kỹ sư Bảo mật",
            "áp dụng cơ chế giới hạn tần suất gửi yêu cầu (Rate Limiting) và làm sạch dữ liệu đầu vào",
            "hệ thống được bảo vệ vững chắc trước các cuộc tấn công từ chối dịch vụ và hành vi spam máy chủ.",
            "- Giới hạn tần suất 30 yêu cầu/phút trên mỗi địa chỉ IP (SlowAPI).\n- Cấu hình đầy đủ các tiêu chuẩn bảo mật HTTP Header (CSP, HSTS, X-Frame-Options).\n- Kiểm tra nghiêm ngặt mã tệp magic byte, ngăn chặn tệp mã độc mạo danh ảnh.",
            "Phòng thủ chiều sâu",
            4, "Cần làm", "User Story", "C1SE.06", "Sprint 5", 32, "Phạm Tấn Hào"
        ),
        (
            "PB-20",
            "Kiểm thử Chịu tải Toàn diện & Đo lường Benchmark Học thuật",
            "Đội ngũ Dự án",
            "thực hiện kiểm thử tải với Locust và đo lường độ chính xác theo các chỉ số khoa học (Macro-F1, Recall)",
            "đồ án chứng minh được tính hiệu quả, độ chính xác cao và sẵn sàng cho buổi bảo vệ chính thức trước hội đồng.",
            "- Kiểm thử chịu tải 50 người dùng đồng thời với độ trễ P95 < 2.5 giây.\n- Báo cáo đo lường Macro-F1 >= 0.88 trên tập kiểm thử xác thực.\n- Hoàn thiện toàn bộ tài liệu kỹ thuật, slide thuyết trình và kịch bản demo bảo vệ.",
            "Nghiệm thu Đồ án Tốt nghiệp 1",
            5, "Cần làm", "User Story", "C1SE.06", "Sprint 5", 40, "Đào Thị Mỹ Nhung"
        )
    ]

    for r_idx, item in enumerate(backlog_data, start=7):
        ws_pb.write(r_idx, 1, item[0], cell_bold_left)
        ws_pb.write(r_idx, 2, item[1], cell_bold_left)
        ws_pb.write(r_idx, 3, item[2], cell_left)
        ws_pb.write(r_idx, 4, item[3], cell_left)
        ws_pb.write(r_idx, 5, item[4], cell_left)
        ws_pb.write(r_idx, 6, item[5], cell_left)
        ws_pb.write(r_idx, 7, item[6], cell_left)
        ws_pb.write(r_idx, 8, item[7], priority_high)

        st = item[8]
        if st == "Hoàn thành":
            ws_pb.write(r_idx, 9, st, status_done)
        elif st == "Đang thực hiện":
            ws_pb.write(r_idx, 9, st, status_in_progress)
        else:
            ws_pb.write(r_idx, 9, st, status_todo)

        ws_pb.write(r_idx, 10, item[9], cell_center)
        ws_pb.write(r_idx, 11, item[10], cell_center)
        ws_pb.write(r_idx, 12, item[11], cell_center)
        ws_pb.write(r_idx, 13, item[12], cell_right)
        ws_pb.write(r_idx, 14, item[13], cell_left)

    total_row_idx = len(backlog_data) + 7
    ws_pb.write(total_row_idx, 1, "Tổng cộng", total_fmt)
    for c in range(2, 13):
        ws_pb.write(total_row_idx, c, "", total_fmt)
    ws_pb.write_formula(total_row_idx, 13, f'=SUM(N8:N{total_row_idx})', total_fmt)
    ws_pb.write(total_row_idx, 14, "", total_fmt)

    # ==========================================
    # CÁC TAB SPRINT CHI TIẾT (Sprint 1 đến Sprint 5)
    # ==========================================
    sprint_details = [
        ("Sprint 1", "Sprint 1 – Thiết lập Khung Kiến trúc & Mô hình AI Baseline", [
            ("TS-01-01", "PB-01", "Cấu hình khung máy chủ FastAPI, CORS, bộ định tuyến và ghi log", "Phạm Tấn Hào", 16, 16, "Hoàn thành"),
            ("TS-01-02", "PB-01", "Khởi tạo ứng dụng React 18 SPA với Vite và Tailwind CSS", "Trần Hoàng Nhật Nam", 12, 12, "Hoàn thành"),
            ("TS-01-03", "PB-01", "Cấu hình CSDL SQLite và định nghĩa lược đồ bảng SQLAlchemy ORM", "Phạm Tấn Hào", 8, 8, "Hoàn thành"),
            ("TS-01-04", "PB-02", "Hiện thực hóa các điểm cuối xác thực JWT và hàm băm mật khẩu", "Phạm Tấn Hào", 18, 18, "Hoàn thành"),
            ("TS-01-05", "PB-02", "Thiết kế giao diện AuthPage và lưu trữ token bảo mật trên frontend", "Trần Hoàng Nhật Nam", 10, 10, "Hoàn thành"),
            ("TS-01-06", "PB-03", "Xây dựng module trích xuất 21 đặc trưng từ vựng liên kết URL", "Nguyễn Phan Đức Tuấn", 24, 24, "Hoàn thành"),
            ("TS-01-07", "PB-03", "Huấn luyện & xuất checkpoint mô hình HistGradientBoosting PhishVN", "Nguyễn Phan Đức Tuấn", 24, 24, "Hoàn thành"),
            ("TS-01-08", "PB-04", "Hiện thực hóa động cơ lọc cổng tên miền Danh sách trắng & Danh sách đen", "Phạm Tấn Hào", 14, 14, "Hoàn thành"),
            ("TS-01-09", "PB-04", "Kiểm thử chuẩn hóa định dạng tên miền và xử lý mã punycode", "Đào Thị Mỹ Nhung", 10, 10, "Hoàn thành"),
            ("TS-01-10", "PB-05", "Tinh chỉnh mô hình ResNet-18 nhận diện logo thương hiệu Việt Nam", "Nguyễn Phan Đức Tuấn", 28, 28, "Hoàn thành"),
            ("TS-01-11", "PB-05", "Áp dụng kỹ thuật chuẩn hóa nhiệt độ (T=1.8) trên đầu ra PyTorch", "Nguyễn Phan Đức Tuấn", 16, 16, "Hoàn thành")
        ]),
        ("Sprint 2", "Sprint 2 – Pipeline OCR, Phân tích Rủi ro & Suy luận CoT", [
            ("TS-02-01", "PB-06", "Hiện thực hóa pipeline tính toán pháp chứng mức nén ảnh OpenCV ELA", "Phạm Tấn Hào", 20, 20, "Hoàn thành"),
            ("TS-02-02", "PB-06", "Trích xuất siêu dữ liệu ảnh EXIF và phát hiện dấu vết phần mềm can thiệp", "Phạm Tấn Hào", 16, 16, "Hoàn thành"),
            ("TS-02-03", "PB-07", "Tích hợp động cơ Tesseract OCR 5.x với gói dữ liệu tiếng Việt", "Nguyễn Phan Đức Tuấn", 22, 22, "Hoàn thành"),
            ("TS-02-04", "PB-07", "Bổ sung các bước tiền xử lý ảnh (ngưỡng tương thích, khử nhiễu)", "Nguyễn Phan Đức Tuấn", 18, 18, "Hoàn thành"),
            ("TS-02-05", "PB-08", "Biên soạn bộ từ điển từ khóa lừa đảo tiếng Việt toàn diện", "Đào Thị Mỹ Nhung", 18, 18, "Hoàn thành"),
            ("TS-02-06", "PB-08", "Hiện thực hóa biểu thức Regex nhận diện số tài khoản ngân hàng & OTP", "Đào Thị Mỹ Nhung", 14, 14, "Hoàn thành"),
            ("TS-02-07", "PB-09", "Xây dựng logic suy luận chuỗi giải thích CoT 4 bước", "Nguyễn Phan Đức Tuấn", 24, 24, "Hoàn thành"),
            ("TS-02-08", "PB-09", "Hiện thực hóa thuật toán bầu chọn đồng thuận Consensus Fusion", "Nguyễn Phan Đức Tuấn", 18, 18, "Hoàn thành"),
            ("TS-02-09", "PB-10", "Xây dựng module sinh nội dung giải thích bằng tiếng Việt dễ hiểu", "Trần Hoàng Nhật Nam", 18, 18, "Hoàn thành"),
            ("TS-02-10", "PB-10", "Viết unit test kiểm thử tính nhất quán của văn bản giải thích", "Đào Thị Mỹ Nhung", 12, 12, "Hoàn thành")
        ]),
        ("Sprint 3", "Sprint 3 – Giao diện Người dùng Web SPA & Trải nghiệm UI-UX", [
            ("TS-03-01", "PB-11", "Xây dựng giao diện ScanPage hỗ trợ đa dạng đầu vào (URL/Văn bản/Ảnh)", "Trần Hoàng Nhật Nam", 22, 18, "Đang thực hiện"),
            ("TS-03-02", "PB-11", "Hiện thực hóa vùng kéo thả ảnh chụp màn hình kèm xem trước trực quan", "Trần Hoàng Nhật Nam", 18, 14, "Đang thực hiện"),
            ("TS-03-03", "PB-12", "Phát triển thành phần Đồng hồ đo rủi ro chuyển màu động", "Trần Hoàng Nhật Nam", 20, 16, "Đang thực hiện"),
            ("TS-03-04", "PB-12", "Hiển thị các thẻ bằng chứng đa phương thức và khuyến nghị an toàn", "Đào Thị Mỹ Nhung", 18, 12, "Đang thực hiện"),
            ("TS-03-05", "PB-13", "Hiện thực hóa bộ nhớ đệm localStorage lưu trữ 50 lượt quét gần nhất", "Trần Hoàng Nhật Nam", 14, 10, "Đang thực hiện"),
            ("TS-03-06", "PB-13", "Xây dựng trang HistoryPage hỗ trợ tìm kiếm, lọc và xem lại chi tiết", "Trần Hoàng Nhật Nam", 12, 8, "Đang thực hiện"),
            ("TS-03-07", "PB-14", "Tạo hộp thoại tiếp nhận phản hồi đóng góp ý kiến và API tương ứng", "Đào Thị Mỹ Nhung", 16, 10, "Đang thực hiện"),
            ("TS-03-08", "PB-14", "Kiểm tra tính hợp lệ của phản hồi và thông báo xác nhận toast", "Đào Thị Mỹ Nhung", 12, 8, "Đang thực hiện")
        ]),
        ("Sprint 4", "Sprint 4 – Cổng Quản trị Viên, Báo cáo & Giám sát An ninh", [
            ("TS-04-01", "PB-15", "Xây dựng bảng xem xét sự cố an ninh dành cho quản trị viên", "Phạm Tấn Hào", 20, 0, "Cần làm"),
            ("TS-04-02", "PB-15", "Hiện thực hóa các hành động thụ lý sự cố (Xác minh, Bỏ qua, Gắn cờ)", "Phạm Tấn Hào", 16, 0, "Cần làm"),
            ("TS-04-03", "PB-16", "Phát triển bảng điều khiển phân tích tri thức đe dọa (Threat Intel)", "Phạm Tấn Hào", 20, 0, "Cần làm"),
            ("TS-04-04", "PB-16", "Hiện thực hóa các thẻ chỉ số KPI (Tổng lượt quét, Tỷ lệ lừa đảo, Độ trễ)", "Phạm Tấn Hào", 14, 0, "Cần làm"),
            ("TS-04-05", "PB-17", "Xây dựng giao diện quản trị Danh sách trắng / đen và API CRUD", "Nguyễn Phan Đức Tuấn", 18, 0, "Cần làm"),
            ("TS-04-06", "PB-17", "Bổ sung giao diện quản trị từ khóa rủi ro và trọng số động", "Nguyễn Phan Đức Tuấn", 12, 0, "Cần làm"),
            ("TS-04-07", "PB-18", "Hiện thực hóa tính năng xuất báo cáo PDF kèm dấu pháp chứng số", "Đào Thị Mỹ Nhung", 18, 0, "Cần làm"),
            ("TS-04-08", "PB-18", "Hiện thực hóa tính năng xuất dữ liệu sự cố dạng CSV kiểm toán", "Đào Thị Mỹ Nhung", 10, 0, "Cần làm")
        ]),
        ("Sprint 5", "Sprint 5 – Tăng cường Bảo mật, Tối ưu Tải & Bảo vệ Đồ án", [
            ("TS-05-01", "PB-19", "Cấu hình giới hạn tần suất gửi yêu cầu SlowAPI (30 req/phút/IP)", "Phạm Tấn Hào", 14, 0, "Cần làm"),
            ("TS-05-02", "PB-19", "Cấu hình bảo mật HTTP Header, CORS và lọc sạch dữ liệu đầu vào", "Phạm Tấn Hào", 18, 0, "Cần làm"),
            ("TS-05-03", "PB-20", "Thực thi toàn bộ bộ kiểm thử pytest trên tất cả các engine AI", "Đào Thị Mỹ Nhung", 18, 0, "Cần làm"),
            ("TS-05-04", "PB-20", "Kiểm thử chịu tải Locust dưới điều kiện 50 người dùng đồng thời", "Phạm Tấn Hào", 12, 0, "Cần làm"),
            ("TS-05-05", "PB-20", "Kiểm tra hiệu chuẩn mô hình, đảm bảo không còn lỗi điểm số nhảy vọt", "Nguyễn Phan Đức Tuấn", 14, 0, "Cần làm"),
            ("TS-05-06", "PB-20", "Chuẩn bị slide thuyết trình hoàn chỉnh và kịch bản demo bảo vệ đồ án", "Trần Hoàng Nhật Nam", 20, 0, "Cần làm")
        ])
    ]

    sp_headers = ["Mã công việc", "Tham chiếu PB", "Mô tả công việc", "Người thực hiện", "Giờ dự kiến", "Giờ thực tế", "Trạng thái"]

    for sp_name, sp_title, tasks in sprint_details:
        ws_sp = workbook.add_worksheet(sp_name)
        ws_sp.set_column('A:A', 3)
        ws_sp.set_column('B:B', 14)  # Mã công việc
        ws_sp.set_column('C:C', 14)  # Tham chiếu PB
        ws_sp.set_column('D:D', 46)  # Mô tả công việc
        ws_sp.set_column('E:E', 24)  # Người thực hiện
        ws_sp.set_column('F:F', 14)  # Giờ dự kiến
        ws_sp.set_column('G:G', 14)  # Giờ thực tế
        ws_sp.set_column('H:H', 18)  # Trạng thái

        ws_sp.write('B2', sp_title, title_fmt)
        ws_sp.write('B3', "Nhóm Đồ án Capstone C1SE.06 - Đại học Duy Tân", subtitle_fmt)

        for c_idx, h in enumerate(sp_headers, start=1):
            ws_sp.write(4, c_idx, h, header_fmt)

        for r_idx, task in enumerate(tasks, start=5):
            ws_sp.write(r_idx, 1, task[0], cell_bold_left)
            ws_sp.write(r_idx, 2, task[1], cell_center)
            ws_sp.write(r_idx, 3, task[2], cell_left)
            ws_sp.write(r_idx, 4, task[3], cell_left)
            ws_sp.write(r_idx, 5, task[4], cell_right)
            ws_sp.write(r_idx, 6, task[5], cell_right)

            st = task[6]
            if st == "Hoàn thành":
                ws_sp.write(r_idx, 7, st, status_done)
            elif st == "Đang thực hiện":
                ws_sp.write(r_idx, 7, st, status_in_progress)
            else:
                ws_sp.write(r_idx, 7, st, status_todo)

        total_r = len(tasks) + 5
        ws_sp.write(total_r, 1, "Tổng cộng", total_fmt)
        ws_sp.write(total_r, 2, "", total_fmt)
        ws_sp.write(total_r, 3, "", total_fmt)
        ws_sp.write(total_r, 4, "", total_fmt)
        ws_sp.write_formula(total_r, 5, f'=SUM(F6:F{total_r})', total_fmt)
        ws_sp.write_formula(total_r, 6, f'=SUM(G6:G{total_r})', total_fmt)
        ws_sp.write(total_r, 7, "", total_fmt)

    workbook.close()
    print("Successfully generated:", filename)

if __name__ == "__main__":
    create_backlog_vi()
