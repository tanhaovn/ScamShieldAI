# -*- coding: utf-8 -*-
"""
Generate accurate UI mockups reflecting the real SFDS codebase.
No registration screen (Public scan is frictionless, only admin logs in).
Outputs 7 clean screens to ui_diagrams/
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs("ui_diagrams", exist_ok=True)

def setup_canvas(w=12, h=7):
    fig, ax = plt.subplots(figsize=(w, h), dpi=250)
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis('off')
    bg = patches.Rectangle((0, 0), w, h, facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.5)
    ax.add_patch(bg)
    return fig, ax

# 1. FIG 1: OVERVIEW
def gen_overview():
    fig, ax = setup_canvas(12, 7)
    nav = patches.Rectangle((0, 6.2), 12, 0.8, facecolor="#0F172A", edgecolor="none")
    ax.add_patch(nav)
    ax.text(0.6, 6.55, "SFDS - SCAM FRAUD DETECTOR", color="#F8FAFC", fontsize=11, fontweight='bold')
    ax.text(6.0, 6.55, "Tổng quan    Kiểm tra lừa đảo    Lịch sử    Cá nhân    Quản trị", color="#94A3B8", fontsize=9.5)
    ax.text(11.2, 6.55, "Khách trải nghiệm", color="#38BDF8", fontsize=9.5, ha='right', fontweight='bold')
    
    hero = patches.FancyBboxPatch((0.6, 4.3), 10.8, 1.7, boxstyle="round,pad=0.1", facecolor="#1E293B", edgecolor="#334155")
    ax.add_patch(hero)
    ax.text(6.0, 5.5, "LÁ CHẮN AI BẢO VỆ NGƯỜI DÂN KHỎI LỪA ĐẢO TRỰC TUYẾN", color="#38BDF8", fontsize=13, fontweight='bold', ha='center')
    ax.text(6.0, 5.0, "Nhận diện tức thì tin nhắn giả mạo, đường link độc hại & ảnh chụp màn hình chuyển khoản giả", color="#F8FAFC", fontsize=9.5, ha='center')
    
    scan_cta = patches.FancyBboxPatch((4.5, 4.5), 3.0, 0.38, boxstyle="round,pad=0.05", facecolor="#2563EB", edgecolor="none")
    ax.add_patch(scan_cta)
    ax.text(6.0, 4.67, "BẮT ĐẦU QUÉT NGAY", color="#FFFFFF", fontsize=9, fontweight='bold', ha='center')
    
    threats = [
        ("Mạo danh Công an", "Đe dọa bắt giữ, yêu cầu chuyển tiền vào tài khoản tạm giữ để điều tra.", "#DC2626"),
        ("Giả mạo Ngân hàng", "Link web mạo danh VCB, MB, Techcombank đánh cắp mã OTP & mật khẩu.", "#EA580C"),
        ("Biên lai Fake (Bill ảo)", "Chỉnh sửa hóa đơn chuyển tiền thành công bằng Photoshop để lừa ship hàng.", "#0284C7"),
        ("Bẫy Đầu tư / Việc làm", "Nhiệm vụ Shopee, hoa hồng ảo, nạp tiền mở khóa quỹ đầu tư siêu lợi nhuận.", "#7C3AED")
    ]
    for i, (t, desc, c) in enumerate(threats):
        x = 0.6 + i * 2.75
        card = patches.FancyBboxPatch((x, 1.8), 2.55, 2.2, boxstyle="round,pad=0.1", facecolor="#FFFFFF", edgecolor="#CBD5E1")
        ax.add_patch(card)
        bar = patches.Rectangle((x, 3.8), 2.55, 0.15, facecolor=c, edgecolor="none")
        ax.add_patch(bar)
        ax.text(x + 0.15, 3.5, t, fontsize=10, fontweight='bold', color="#0F172A")
        ax.text(x + 0.15, 2.5, desc, fontsize=8, color="#64748B", wrap=True)
        
    stats_box = patches.FancyBboxPatch((0.6, 0.4), 10.8, 1.1, boxstyle="round,pad=0.1", facecolor="#F1F5F9", edgecolor="#CBD5E1")
    ax.add_patch(stats_box)
    ax.text(2.0, 1.05, "12,450+", fontsize=14, fontweight='bold', color="#0F172A", ha='center')
    ax.text(2.0, 0.65, "Lượt quét toàn hệ thống", fontsize=8.5, color="#64748B", ha='center')
    
    ax.text(5.0, 1.05, "98.4%", fontsize=14, fontweight='bold', color="#059669", ha='center')
    ax.text(5.0, 0.65, "Độ chính xác nhận diện", fontsize=8.5, color="#64748B", ha='center')
    
    ax.text(8.0, 1.05, "< 2.1 giây", fontsize=14, fontweight='bold', color="#2563EB", ha='center')
    ax.text(8.0, 0.65, "Tốc độ xử lý đa phương thức", fontsize=8.5, color="#64748B", ha='center')
    
    ax.text(10.2, 1.05, "4,120+", fontsize=14, fontweight='bold', color="#DC2626", ha='center')
    ax.text(10.2, 0.65, "Vụ lừa đảo bị chặn đứng", fontsize=8.5, color="#64748B", ha='center')
    
    plt.tight_layout()
    plt.savefig("ui_diagrams/fig1_ui_overview.png", bbox_inches='tight')
    plt.close()

# 2. FIG 2: SCAN INPUT
def gen_scan_input():
    fig, ax = setup_canvas(12, 7)
    nav = patches.Rectangle((0, 6.3), 12, 0.7, facecolor="#0F172A", edgecolor="none")
    ax.add_patch(nav)
    ax.text(0.6, 6.6, "SFDS - KIỂM TRA LỪA ĐẢO ĐA PHƯƠNG THỨC", color="#F8FAFC", fontsize=11, fontweight='bold')
    
    tabs = [("Ảnh chụp màn hình", True), ("Đường link (URL)", False), ("Đoạn chat / Tin nhắn", False), ("File tài liệu PDF", False)]
    for i, (tab_name, active) in enumerate(tabs):
        tx = 0.6 + i * 2.75
        c = "#2563EB" if active else "#E2E8F0"
        tc = "#FFFFFF" if active else "#475569"
        btn = patches.FancyBboxPatch((tx, 5.6), 2.6, 0.5, boxstyle="round,pad=0.05", facecolor=c, edgecolor="none")
        ax.add_patch(btn)
        ax.text(tx + 1.3, 5.82, tab_name, color=tc, fontsize=9, fontweight='bold', ha='center')
        
    vp = patches.FancyBboxPatch((0.6, 0.6), 6.8, 4.7, boxstyle="round,pad=0.1", facecolor="#0F172A", edgecolor="#38BDF8", linewidth=1.5)
    ax.add_patch(vp)
    
    ax.text(1.0, 4.9, "● AI VISION ACTIVE", color="#22C55E", fontsize=8.5, fontweight='bold')
    ax.text(6.8, 4.9, "1920x1080 · RGB", color="#94A3B8", fontsize=8.5, ha='right')
    
    drop_zone = patches.FancyBboxPatch((1.4, 1.4), 5.2, 3.1, boxstyle="round,pad=0.1", facecolor="#1E293B", edgecolor="#38BDF8", linestyle="--")
    ax.add_patch(drop_zone)
    ax.text(4.0, 3.2, "KÉO THẢ ẢNH CHỤP MÀN HÌNH VÀO ĐÂY", color="#38BDF8", fontsize=10, fontweight='bold', ha='center')
    ax.text(4.0, 2.7, "Hỗ trợ định dạng PNG, JPG, JPEG, WEBP (Tối đa 10MB)", color="#94A3B8", fontsize=8.5, ha='center')
    
    browse_btn = patches.FancyBboxPatch((2.8, 1.8), 2.4, 0.45, boxstyle="round,pad=0.05", facecolor="#2563EB", edgecolor="none")
    ax.add_patch(browse_btn)
    ax.text(4.0, 2.0, "Chọn file từ thiết bị", color="#FFFFFF", fontsize=8.5, fontweight='bold', ha='center')
    
    side = patches.FancyBboxPatch((7.7, 0.6), 3.7, 4.7, boxstyle="round,pad=0.1", facecolor="#FFFFFF", edgecolor="#CBD5E1")
    ax.add_patch(side)
    ax.text(8.0, 4.9, "Tùy Chọn Phân Tích", fontsize=11, fontweight='bold', color="#0F172A")
    ax.text(8.0, 4.4, "URL nghi vấn kèm theo:", fontsize=8.5, fontweight='bold', color="#334155")
    inp_url = patches.FancyBboxPatch((8.0, 3.9), 3.1, 0.38, boxstyle="round,pad=0.05", facecolor="#F8FAFC", edgecolor="#CBD5E1")
    ax.add_patch(inp_url)
    ax.text(8.1, 4.08, "http://vietcombank-xacminh.com", color="#0F172A", fontsize=8)
    
    ax.text(8.0, 3.5, "Nội dung tin nhắn nhận được:", fontsize=8.5, fontweight='bold', color="#334155")
    inp_txt = patches.FancyBboxPatch((8.0, 2.1), 3.1, 1.2, boxstyle="round,pad=0.05", facecolor="#F8FAFC", edgecolor="#CBD5E1")
    ax.add_patch(inp_txt)
    ax.text(8.1, 3.0, "Tài khoản VCB của bạn bị tạm khóa.\nVui lòng nhấp vào link xác minh mã OTP\nngay trong 10 phút...", color="#64748B", fontsize=7.5)
    
    scan_btn = patches.FancyBboxPatch((8.0, 0.9), 3.1, 0.6, boxstyle="round,pad=0.05", facecolor="#DC2626", edgecolor="none")
    ax.add_patch(scan_btn)
    ax.text(9.55, 1.2, "PHÂN TÍCH RỦI RO NGAY", color="#FFFFFF", fontsize=10, fontweight='bold', ha='center')
    
    plt.tight_layout()
    plt.savefig("ui_diagrams/fig2_ui_scan_input.png", bbox_inches='tight')
    plt.close()

# 3. FIG 3: SCAN RESULT & EXPLANATION
def gen_scan_result():
    fig, ax = setup_canvas(12, 7)
    nav = patches.Rectangle((0, 6.3), 12, 0.7, facecolor="#0F172A", edgecolor="none")
    ax.add_patch(nav)
    ax.text(0.6, 6.6, "KẾT QUẢ PHÂN TÍCH LỪA ĐẢO & GIẢI THÍCH TRỰC QUAN", color="#F8FAFC", fontsize=11, fontweight='bold')
    
    left = patches.FancyBboxPatch((0.6, 0.6), 3.8, 5.4, boxstyle="round,pad=0.1", facecolor="#FFFFFF", edgecolor="#CBD5E1")
    ax.add_patch(left)
    ax.text(2.5, 5.5, "MỨC ĐỘ NGUY HIỂM", fontsize=12, fontweight='bold', color="#0F172A", ha='center')
    
    gauge_circle = patches.Circle((2.5, 4.2), 1.1, facecolor="#FEE2E2", edgecolor="#DC2626", linewidth=4)
    ax.add_patch(gauge_circle)
    ax.text(2.5, 4.3, "88%", fontsize=20, fontweight='bold', color="#DC2626", ha='center')
    ax.text(2.5, 3.7, "NGUY HIỂM CAO", fontsize=9, fontweight='bold', color="#DC2626", ha='center')
    
    sub_scores = [
        ("Tên miền (PhishVN):", "92% (Giả mạo)", "#DC2626"),
        ("Hình ảnh (ResNet-18):", "85% (Logo mạo danh)", "#EA580C"),
        ("Nội dung (NLP & OCR):", "88% (Hối thúc, mã OTP)", "#DC2626"),
        ("Pháp y ảnh (ELA):", "Phát hiện can thiệp số", "#EAB308")
    ]
    for idx, (label, val, col) in enumerate(sub_scores):
        sy = 2.8 - idx * 0.45
        ax.text(0.9, sy, label, fontsize=8, color="#334155", fontweight='bold')
        ax.text(4.1, sy, val, fontsize=8, color=col, fontweight='bold', ha='right')
        
    report_btn = patches.FancyBboxPatch((0.9, 0.9), 3.2, 0.4, boxstyle="round,pad=0.05", facecolor="#F1F5F9", edgecolor="#CBD5E1")
    ax.add_patch(report_btn)
    ax.text(2.5, 1.08, "Báo cáo sai lệch / Phản hồi", color="#475569", fontsize=8.5, ha='center', fontweight='bold')
    
    right = patches.FancyBboxPatch((4.7, 0.6), 6.7, 5.4, boxstyle="round,pad=0.1", facecolor="#FFFFFF", edgecolor="#CBD5E1")
    ax.add_patch(right)
    ax.text(5.0, 5.5, "Giải Thích Lý Do Cảnh Báo (Chain-of-Thought):", fontsize=11, fontweight='bold', color="#0F172A")
    
    cot_steps = [
        ("1. Tên miền bất thường:", "Tên miền 'vietcombank-xacminh.com' KHÔNG thuộc cổng thông tin chính thức vietcombank.com.vn. Tên miền mới đăng ký 3 ngày trước."),
        ("2. Mạo danh thương hiệu:", "Logo ngân hàng Vietcombank được sử dụng trái phép trên giao diện không có chứng chỉ số EV SSL."),
        ("3. Ngữ cảnh thúc ép lừa đảo:", "Văn bản chứa các từ khóa đe dọa 'tài khoản bị khóa' và yêu cầu 'nhập mã OTP ngay lập tức' - dấu hiệu điển hình của bẫy lừa đảo."),
        ("4. Dấu vết chỉnh sửa (ELA):", "Phân tích Error Level Analysis phát hiện vùng số tiền và con dấu có tần số nén JPEG không đồng nhất với ảnh nền.")
    ]
    for idx, (step_t, step_d) in enumerate(cot_steps):
        ey = 4.9 - idx * 0.8
        ax.text(5.0, ey, step_t, fontsize=8.5, fontweight='bold', color="#DC2626")
        ax.text(5.0, ey - 0.4, step_d, fontsize=8, color="#475569", wrap=True)
        
    rec_box = patches.FancyBboxPatch((5.0, 0.9), 6.1, 1.3, boxstyle="round,pad=0.05", facecolor="#EFF6FF", edgecolor="#BFDBFE")
    ax.add_patch(rec_box)
    ax.text(5.2, 1.9, "Khuyến Nghị Hành Động An Toàn:", fontsize=9.5, fontweight='bold', color="#1D4ED8")
    ax.text(5.2, 1.5, "• TUYỆT ĐỐI KHÔNG đăng nhập tài khoản hoặc cung cấp mã OTP vào trang web này.", fontsize=8, color="#1E40AF")
    ax.text(5.2, 1.25, "• KHÔNG chuyển tiền theo bất kỳ yêu cầu đe dọa nào từ số điện thoại lạ.", fontsize=8, color="#1E40AF")
    ax.text(5.2, 1.0, "• Liên hệ ngay hotline chính thức của ngân hàng (1900 54 54 13) để kiểm tra tình trạng.", fontsize=8, color="#1E40AF")
    
    plt.tight_layout()
    plt.savefig("ui_diagrams/fig3_ui_scan_result.png", bbox_inches='tight')
    plt.close()

# 4. FIG 4: HISTORY
def gen_history():
    fig, ax = setup_canvas(12, 7)
    nav = patches.Rectangle((0, 6.3), 12, 0.7, facecolor="#0F172A", edgecolor="none")
    ax.add_patch(nav)
    ax.text(0.6, 6.6, "SFDS - LỊCH SỬ KIỂM TRA & PHÁP Y DỮ LIỆU", color="#F8FAFC", fontsize=11, fontweight='bold')
    
    filter_bar = patches.FancyBboxPatch((0.6, 5.4), 10.8, 0.65, boxstyle="round,pad=0.05", facecolor="#FFFFFF", edgecolor="#CBD5E1")
    ax.add_patch(filter_bar)
    ax.text(0.9, 5.72, "Tìm kiếm từ khóa, URL hoặc mã quét...", color="#94A3B8", fontsize=8.5)
    ax.text(6.0, 5.72, "Lọc mức rủi ro: [ Tất cả ]   [ Nguy hiểm ]   [ Nghi ngờ ]   [ An toàn ]", color="#334155", fontsize=8.5)
    
    exp_btn = patches.FancyBboxPatch((9.7, 5.52), 1.5, 0.4, boxstyle="round,pad=0.05", facecolor="#2563EB", edgecolor="none")
    ax.add_patch(exp_btn)
    ax.text(10.45, 5.7, "Xuất CSV", color="#FFFFFF", fontsize=8.5, fontweight='bold', ha='center')
    
    tbl_hdr = patches.Rectangle((0.6, 4.8), 10.8, 0.45, facecolor="#E2E8F0", edgecolor="#CBD5E1")
    ax.add_patch(tbl_hdr)
    cols = [(0.8, "Thời gian"), (2.3, "Loại dữ liệu"), (4.0, "Nội dung kiểm tra"), (7.5, "Điểm rủi ro"), (8.8, "Mức độ"), (10.2, "Thao tác")]
    for cx, ctitle in cols:
        ax.text(cx, 4.95, ctitle, fontsize=8.5, fontweight='bold', color="#0F172A")
        
    rows = [
        ("04/11 10:15", "URL", "vietcombank-xacminh.com", "88/100", "Nguy hiểm", "#DC2626"),
        ("04/11 09:40", "Hình ảnh", "bill_chuyen_khoan_vcb_5tr.png", "74/100", "Nguy hiểm", "#DC2626"),
        ("03/11 21:05", "Tin nhắn", "Em bên tuyển dụng Shopee ngày làm 2h...", "62/100", "Nghi ngờ", "#EA580C"),
        ("03/11 16:30", "URL", "dichvucong.gov.vn", "0/100", "An toàn", "#059669"),
        ("03/11 14:10", "Hình ảnh", "can_cuoc_cong_dan_gia.jpg", "82/100", "Nguy hiểm", "#DC2626"),
        ("02/11 11:20", "PDF", "quyet_dinh_khoi_to_gia_mao.pdf", "91/100", "Nguy hiểm", "#DC2626"),
        ("01/11 08:15", "Tin nhắn", "Ma OTP cua ban la 592819...", "5/100", "An toàn", "#059669")
    ]
    for i, (t, dtype, content, score, level, color) in enumerate(rows):
        ry = 4.25 - i * 0.5
        bg_col = "#F8FAFC" if i % 2 == 0 else "#FFFFFF"
        row_rect = patches.Rectangle((0.6, ry), 10.8, 0.45, facecolor=bg_col, edgecolor="#E2E8F0", linewidth=0.5)
        ax.add_patch(row_rect)
        ax.text(0.8, ry + 0.15, t, fontsize=8, color="#334155")
        ax.text(2.3, ry + 0.15, dtype, fontsize=8, color="#0F172A", fontweight='bold')
        ax.text(4.0, ry + 0.15, content, fontsize=8, color="#334155")
        ax.text(7.5, ry + 0.15, score, fontsize=8, color=color, fontweight='bold')
        ax.text(8.8, ry + 0.15, level, fontsize=8, color=color, fontweight='bold')
        ax.text(10.2, ry + 0.15, "Xem chi tiết", fontsize=8, color="#2563EB", fontweight='bold')
        
    ax.text(6.0, 0.4, "Hiển thị 1 - 7 trong số 40 lượt quét gần nhất (Bộ nhớ cục bộ lưu trữ tối đa 50 lượt)", fontsize=8, color="#64748B", ha='center')
    
    plt.tight_layout()
    plt.savefig("ui_diagrams/fig4_ui_history.png", bbox_inches='tight')
    plt.close()

# 5. FIG 5: PROFILE PAGE
def gen_profile():
    fig, ax = setup_canvas(12, 7)
    nav = patches.Rectangle((0, 6.3), 12, 0.7, facecolor="#0F172A", edgecolor="none")
    ax.add_patch(nav)
    ax.text(0.6, 6.6, "SFDS - KHÔNG GIAN CÁ NHÂN & THIẾT BỊ", color="#F8FAFC", fontsize=11, fontweight='bold')
    
    # Left: User Identity Card
    left = patches.FancyBboxPatch((0.8, 1.2), 4.5, 4.8, boxstyle="round,pad=0.15", facecolor="#FFFFFF", edgecolor="#CBD5E1")
    ax.add_patch(left)
    
    # Avatar Circle
    avatar = patches.Circle((3.05, 4.8), 0.8, facecolor="#0284C7", edgecolor="#38BDF8", linewidth=2)
    ax.add_patch(avatar)
    ax.text(3.05, 4.75, "KH", fontsize=16, fontweight='bold', color="#FFFFFF", ha='center')
    
    ax.text(3.05, 3.7, "Khách Trải Nghiệm", fontsize=12, fontweight='bold', color="#0F172A", ha='center')
    ax.text(3.05, 3.35, "Phiên làm việc cục bộ thiết bị", fontsize=8.5, color="#64748B", ha='center')
    
    badge = patches.FancyBboxPatch((2.0, 2.8), 2.1, 0.35, boxstyle="round,pad=0.05", facecolor="#E0F2FE", edgecolor="none")
    ax.add_patch(badge)
    ax.text(3.05, 2.95, "VAI TRÒ: CITIZEN / USER", color="#0369A1", fontsize=7.5, fontweight='bold', ha='center')
    
    ax.text(1.2, 2.3, "Bộ nhớ thiết bị:", fontsize=8.5, fontweight='bold', color="#334155")
    ax.text(4.9, 2.3, "40 lượt quét", fontsize=8.5, color="#0F172A", ha='right')
    
    ax.text(1.2, 1.85, "Phiên bản AI:", fontsize=8.5, fontweight='bold', color="#334155")
    ax.text(4.9, 1.85, "PhishVN-v1.2", fontsize=8.5, color="#059669", ha='right')
    
    # Right: Personal Stats & Settings
    right = patches.FancyBboxPatch((5.8, 1.2), 5.4, 4.8, boxstyle="round,pad=0.15", facecolor="#FFFFFF", edgecolor="#CBD5E1")
    ax.add_patch(right)
    
    ax.text(6.1, 5.5, "Hoạt Động & Bảo Mật Trên Thiết Bị", fontsize=11, fontweight='bold', color="#0F172A")
    
    p_stats = [
        ("Tổng lượt đã quét:", "40 lượt", "#2563EB"),
        ("Số vụ phát hiện Nguy hiểm:", "14 vụ (35%)", "#DC2626"),
        ("Số lượt An toàn:", "22 lượt (55%)", "#059669"),
        ("Số lượt Nghi ngờ:", "4 lượt (10%)", "#EA580C")
    ]
    for idx, (lbl, val, col) in enumerate(p_stats):
        py = 4.8 - idx * 0.55
        pbox = patches.Rectangle((6.1, py - 0.15), 4.8, 0.42, facecolor="#F8FAFC", edgecolor="#E2E8F0")
        ax.add_patch(pbox)
        ax.text(6.3, py, lbl, fontsize=8.5, color="#334155")
        ax.text(10.7, py, val, fontsize=8.5, color=col, fontweight='bold', ha='right')
        
    ax.text(6.1, 2.3, "Tùy chọn dữ liệu:", fontsize=9, fontweight='bold', color="#0F172A")
    clr_btn = patches.FancyBboxPatch((6.1, 1.6), 2.3, 0.42, boxstyle="round,pad=0.05", facecolor="#FEE2E2", edgecolor="#FCA5A5")
    ax.add_patch(clr_btn)
    ax.text(7.25, 1.78, "Xóa lịch sử cục bộ", color="#DC2626", fontsize=8, fontweight='bold', ha='center')
    
    sync_btn = patches.FancyBboxPatch((8.6, 1.6), 2.3, 0.42, boxstyle="round,pad=0.05", facecolor="#F1F5F9", edgecolor="#CBD5E1")
    ax.add_patch(sync_btn)
    ax.text(9.75, 1.78, "Đồng bộ dữ liệu", color="#475569", fontsize=8, fontweight='bold', ha='center')
    
    plt.tight_layout()
    plt.savefig("ui_diagrams/fig5_ui_profile.png", bbox_inches='tight')
    plt.close()

# 6. FIG 6: ADMIN LOGIN
def gen_admin_login():
    fig, ax = setup_canvas(11, 6.5)
    
    left_card = patches.FancyBboxPatch((0.8, 0.8), 4.5, 4.9, boxstyle="round,pad=0.2", facecolor="#0F172A", edgecolor="#1E293B", linewidth=1.5)
    ax.add_patch(left_card)
    ax.text(3.05, 5.0, "SFDS ADMIN GATE", color="#38BDF8", fontsize=13, fontweight='bold', ha='center')
    ax.text(3.05, 4.5, "Hệ Thống Quản Trị Nhận Diện Lừa Đảo", color="#F8FAFC", fontsize=11, fontweight='bold', ha='center')
    ax.text(3.05, 3.8, "Quyền truy cập dành riêng cho quản trị viên\nquản lý dataset, mô hình AI và kiểm duyệt sự cố.", color="#94A3B8", fontsize=9.5, ha='center', style='italic')
    
    hud_box = patches.Rectangle((1.5, 1.8), 3.1, 1.6, facecolor="#1E293B", edgecolor="#38BDF8", linewidth=1)
    ax.add_patch(hud_box)
    ax.text(3.05, 2.7, "[ SECURE AI INFERENCE CORE ]", color="#38BDF8", fontsize=8.5, fontweight='bold', ha='center')
    ax.text(3.05, 2.2, "JWT Auth · OWASP ASVS · Role Guard", color="#64748B", fontsize=8, ha='center')
    
    right_card = patches.FancyBboxPatch((5.7, 0.8), 4.5, 4.9, boxstyle="round,pad=0.2", facecolor="#FFFFFF", edgecolor="#E2E8F0", linewidth=1.5)
    ax.add_patch(right_card)
    ax.text(7.95, 5.1, "Đăng Nhập Quản Trị", color="#0F172A", fontsize=14, fontweight='bold', ha='center')
    ax.text(7.95, 4.7, "Nhập thông tin xác thực để vào bảng điều khiển", color="#64748B", fontsize=9, ha='center')
    
    ax.text(6.2, 4.15, "Email quản trị viên:", fontsize=9, fontweight='bold', color="#334155")
    inp1 = patches.FancyBboxPatch((6.2, 3.65), 3.5, 0.42, boxstyle="round,pad=0.05", facecolor="#F8FAFC", edgecolor="#CBD5E1")
    ax.add_patch(inp1)
    ax.text(6.35, 3.82, "admin@scamdetector.local", color="#0F172A", fontsize=9)
    
    ax.text(6.2, 3.25, "Mật khẩu:", fontsize=9, fontweight='bold', color="#334155")
    inp2 = patches.FancyBboxPatch((6.2, 2.75), 3.5, 0.42, boxstyle="round,pad=0.05", facecolor="#F8FAFC", edgecolor="#CBD5E1")
    ax.add_patch(inp2)
    ax.text(6.35, 2.92, "••••••••••••", color="#0F172A", fontsize=10)
    
    btn = patches.FancyBboxPatch((6.2, 1.8), 3.5, 0.55, boxstyle="round,pad=0.05", facecolor="#2563EB", edgecolor="none")
    ax.add_patch(btn)
    ax.text(7.95, 2.05, "ĐĂNG NHẬP HỆ THỐNG", color="#FFFFFF", fontsize=10, fontweight='bold', ha='center')
    
    ax.text(7.95, 1.3, "Quay lại trang quét công cộng (Không cần đăng nhập)", color="#2563EB", fontsize=8.5, ha='center')
    
    plt.tight_layout()
    plt.savefig("ui_diagrams/fig6_ui_admin_login.png", bbox_inches='tight')
    plt.close()

# 7. FIG 7: ADMIN CONSOLE
def gen_admin_console():
    fig, ax = setup_canvas(12, 7)
    nav = patches.Rectangle((0, 6.3), 12, 0.7, facecolor="#0F172A", edgecolor="none")
    ax.add_patch(nav)
    ax.text(0.6, 6.6, "SFDS - BẢNG ĐIỀU KHIỂN QUẢN TRỊ VIÊN", color="#F8FAFC", fontsize=11, fontweight='bold')
    ax.text(11.2, 6.6, "admin@scamdetector.local (ADMIN)", color="#38BDF8", fontsize=8.5, ha='right')
    
    # 4 Admin Tabs
    atabs = [("Dataset Huấn Luyện", True), ("Mô Hình AI", False), ("Đánh Giá Model", False), ("Nhật Ký Hệ Thống", False)]
    for i, (tab_name, active) in enumerate(atabs):
        tx = 0.6 + i * 2.75
        c = "#2563EB" if active else "#E2E8F0"
        tc = "#FFFFFF" if active else "#475569"
        btn = patches.FancyBboxPatch((tx, 5.6), 2.6, 0.5, boxstyle="round,pad=0.05", facecolor=c, edgecolor="none")
        ax.add_patch(btn)
        ax.text(tx + 1.3, 5.82, tab_name, color=tc, fontsize=9, fontweight='bold', ha='center')
        
    # Dataset Form (Left)
    form_card = patches.FancyBboxPatch((0.6, 0.6), 4.5, 4.7, boxstyle="round,pad=0.1", facecolor="#FFFFFF", edgecolor="#CBD5E1")
    ax.add_patch(form_card)
    ax.text(0.9, 4.85, "Thêm Mẫu Training Dataset", fontsize=11, fontweight='bold', color="#0F172A")
    
    ax.text(0.9, 4.4, "Đường dẫn ảnh mẫu (Image URL):", fontsize=8, fontweight='bold', color="#334155")
    i1 = patches.Rectangle((0.9, 4.0), 3.9, 0.35, facecolor="#F8FAFC", edgecolor="#CBD5E1")
    ax.add_patch(i1)
    ax.text(1.0, 4.12, "uploads/samples/fake_bill_01.jpg", fontsize=7.5, color="#64748B")
    
    ax.text(0.9, 3.65, "Phân loại thủ đoạn (Category):", fontsize=8, fontweight='bold', color="#334155")
    i2 = patches.Rectangle((0.9, 3.25), 3.9, 0.35, facecolor="#F8FAFC", edgecolor="#CBD5E1")
    ax.add_patch(i2)
    ax.text(1.0, 3.37, "Biên lai chuyển khoản giả mạo (Fake Bill)", fontsize=7.5, color="#0F172A")
    
    ax.text(0.9, 2.8, "[✓] Anonymized (Đã làm mờ thông tin cá nhân PII)", fontsize=8, color="#0F172A")
    ax.text(0.9, 2.4, "[✓] Verified (Đã xác minh nhãn Ground-truth)", fontsize=8, color="#0F172A")
    
    add_btn = patches.FancyBboxPatch((0.9, 1.4), 3.9, 0.5, boxstyle="round,pad=0.05", facecolor="#059669", edgecolor="none")
    ax.add_patch(add_btn)
    ax.text(2.85, 1.62, "LƯU VÀO KHO DỮ LIỆU HUẤN LUYỆN", color="#FFFFFF", fontsize=8.5, fontweight='bold', ha='center')
    
    # Dataset List (Right)
    list_card = patches.FancyBboxPatch((5.4, 0.6), 6.0, 4.7, boxstyle="round,pad=0.1", facecolor="#FFFFFF", edgecolor="#CBD5E1")
    ax.add_patch(list_card)
    ax.text(5.7, 4.85, "Danh Sách Dataset Phục Vụ Retraining", fontsize=11, fontweight='bold', color="#0F172A")
    
    d_rows = [
        ("Mã DS-01", "Phishing URL", "Verified", "admin@scamdetector.local", "#059669"),
        ("Mã DS-02", "Fake Bill", "Verified", "admin@scamdetector.local", "#059669"),
        ("Mã DS-03", "Mạo danh công an", "Pending", "sme_user_02", "#EA580C"),
        ("Mã DS-04", "Deepfake Video", "Verified", "admin@scamdetector.local", "#059669"),
        ("Mã DS-05", "SMS Lừa đảo", "Pending", "sme_user_01", "#EA580C")
    ]
    for idx, (code, cat, status, uploader, col) in enumerate(d_rows):
        dy = 4.2 - idx * 0.7
        d_box = patches.Rectangle((5.7, dy - 0.25), 5.4, 0.55, facecolor="#F8FAFC", edgecolor="#E2E8F0")
        ax.add_patch(d_box)
        ax.text(5.9, dy + 0.05, code, fontsize=8.5, fontweight='bold', color="#0F172A")
        ax.text(7.2, dy + 0.05, cat, fontsize=8, color="#334155")
        ax.text(9.2, dy + 0.05, status, fontsize=8, color=col, fontweight='bold')
        ax.text(5.9, dy - 0.18, f"Người tải lên: {uploader}", fontsize=7.5, color="#94A3B8")
        
    plt.tight_layout()
    plt.savefig("ui_diagrams/fig7_ui_admin_console.png", bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    print("Generating accurate UI Mockups...")
    gen_overview()
    gen_scan_input()
    gen_scan_result()
    gen_history()
    gen_profile()
    gen_admin_login()
    gen_admin_console()
    print("Accurate UI mockups generated in ui_diagrams/!")
