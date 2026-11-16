import UIKit

final class PrivacyPolicyViewController: UIViewController {

    private let policyStack = UIStackView()

    override func viewDidLoad() {
        super.viewDidLoad()
        navigationItem.title = "Quyền riêng tư"
        navigationItem.largeTitleDisplayMode = .never
        view.backgroundColor = AppTheme.pageBackgroundColor

        let scrollView = UIScrollView()
        scrollView.alwaysBounceVertical = true
        scrollView.translatesAutoresizingMaskIntoConstraints = false

        policyStack.axis = .vertical
        policyStack.spacing = 18
        policyStack.translatesAutoresizingMaskIntoConstraints = false

        addSection("Dữ liệu được xử lý", "ScamShield AI chỉ xử lý ảnh bạn chủ động chọn để kiểm tra. Ảnh được gửi đến máy chủ ScamShield AI để phân tích. Xóa lịch sử trong app chỉ xóa bản lưu trên thiết bị, không xóa bản ảnh đã gửi lên máy chủ. App không yêu cầu tài khoản và không dùng ảnh cho quảng cáo.")
        addSection("Dữ liệu lưu trên thiết bị", "Kết quả phân tích và một bản ảnh JPEG được lưu trong vùng dữ liệu riêng của ứng dụng để hiển thị Lịch sử. Bạn có thể xóa từng kết quả hoặc xóa toàn bộ trong mục Cá nhân. Gỡ ứng dụng sẽ xóa dữ liệu cục bộ.")
        addSection("Quyền truy cập", "Quyền Camera chỉ được hỏi khi bạn chọn chụp ảnh. Ảnh từ thư viện được chọn qua trình chọn ảnh của iOS; bạn có thể từ chối quyền và vẫn dùng các chức năng khác.")
        addSection("Giới hạn của kết quả", "Điểm rủi ro, giải thích và hành động đề xuất là tín hiệu hỗ trợ, không phải kết luận chắc chắn. Hãy xác minh với kênh chính thức trước khi giao dịch hoặc cung cấp thông tin cá nhân.")
        addSection("Liên hệ", "Nếu cần yêu cầu hỗ trợ hoặc yêu cầu xóa dữ liệu, hãy liên hệ nhà phát triển qua kênh hỗ trợ được công bố trên trang App Store của ứng dụng.")

        view.addSubview(scrollView)
        scrollView.addSubview(policyStack)
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            policyStack.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor, constant: 24),
            policyStack.leadingAnchor.constraint(equalTo: scrollView.frameLayoutGuide.leadingAnchor, constant: 20),
            policyStack.trailingAnchor.constraint(equalTo: scrollView.frameLayoutGuide.trailingAnchor, constant: -20),
            policyStack.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor, constant: -28)
        ])
    }

    private func addSection(_ title: String, _ body: String) {
        let card = CardView()
        let heading = UILabel()
        heading.text = title
        heading.font = UIFontMetrics(forTextStyle: .headline).scaledFont(for: .systemFont(ofSize: 18, weight: .bold))
        heading.adjustsFontForContentSizeCategory = true
        heading.textColor = AppTheme.titleColor

        let text = UILabel()
        text.text = body
        text.font = UIFontMetrics(forTextStyle: .body).scaledFont(for: .systemFont(ofSize: 15))
        text.adjustsFontForContentSizeCategory = true
        text.textColor = AppTheme.secondaryTextColor
        text.numberOfLines = 0

        let content = UIStackView(arrangedSubviews: [heading, text])
        content.axis = .vertical
        content.spacing = 8
        content.translatesAutoresizingMaskIntoConstraints = false
        card.addSubview(content)
        NSLayoutConstraint.activate([
            content.topAnchor.constraint(equalTo: card.topAnchor, constant: 18),
            content.leadingAnchor.constraint(equalTo: card.leadingAnchor, constant: 18),
            content.trailingAnchor.constraint(equalTo: card.trailingAnchor, constant: -18),
            content.bottomAnchor.constraint(equalTo: card.bottomAnchor, constant: -18)
        ])
        policyStack.addArrangedSubview(card)
    }
}
