import UIKit

final class PrivacyPolicyViewController: UIViewController {

    private let policyStack = UIStackView()

    override func viewDidLoad() {
        super.viewDidLoad()
        navigationItem.title = L10n.text("Quyền riêng tư")
        navigationItem.largeTitleDisplayMode = .never
        view.backgroundColor = AppTheme.pageBackgroundColor

        let scrollView = UIScrollView()
        scrollView.alwaysBounceVertical = true
        scrollView.translatesAutoresizingMaskIntoConstraints = false

        policyStack.axis = .vertical
        policyStack.spacing = 18
        policyStack.translatesAutoresizingMaskIntoConstraints = false

        addSection(
            L10n.choose("Dữ liệu được xử lý", "Data processed"),
            L10n.choose("Ảnh, tin nhắn, URL hoặc PDF bạn chọn chỉ được gửi đến máy chủ khi nhấn Phân tích. Tùy cấu hình máy chủ, ảnh có thể được phân tích bằng Google Gemini và URL có thể được đối chiếu qua Google Safe Browsing. Ứng dụng không dùng dữ liệu để quảng cáo.",
                        "Images, messages, URLs or PDFs you choose are sent to the server only when you tap Analyze. Depending on server settings, images may be analyzed by Google Gemini and URLs may be checked with Google Safe Browsing. The app does not use this data for advertising.")
        )
        addSection(
            L10n.choose("Lưu trữ và xóa", "Storage and deletion"),
            L10n.choose("Lượt kiểm tra của khách lưu trong ứng dụng trên iPhone; ảnh tải lên để quét ở chế độ khách được xóa khỏi máy chủ sau khi trả kết quả. Bạn có thể xóa từng lượt hoặc toàn bộ lịch sử cục bộ trong tab Lịch sử. Ảnh và lịch sử của tài khoản Admin có thể được lưu trên máy chủ; xóa ứng dụng không xóa dữ liệu này.",
                        "Guest checks are saved in the app on this iPhone; guest image uploads are deleted from the server after the result is returned. You can delete individual checks or all local history in the History tab. Admin account images and history may be stored on the server; uninstalling the app does not delete that server data.")
        )
        addSection(
            L10n.choose("Quyền truy cập", "Permissions"),
            L10n.choose("Camera chỉ được hỏi khi bạn chọn chụp ảnh. Trình chọn ảnh và tệp của iOS chỉ cấp quyền cho mục bạn chọn. Bạn có thể dùng tin nhắn hoặc URL mà không cấp quyền Camera hay thư viện ảnh.",
                        "Camera access is requested only when you choose to take a photo. The iOS photo and file pickers grant access only to items you select. You can check text or URLs without granting camera or photo access.")
        )
        addSection(
            L10n.choose("Giới hạn của kết quả", "Result limitations"),
            L10n.choose("Điểm rủi ro và giải thích là tín hiệu hỗ trợ, không phải kết luận chắc chắn. Hãy xác minh với kênh chính thức trước khi giao dịch hoặc cung cấp thông tin cá nhân.",
                        "Risk scores and explanations are advisory signals, not definitive conclusions. Verify through official channels before making a payment or sharing personal information.")
        )
        addSection(
            L10n.choose("Liên hệ và yêu cầu xóa", "Contact and deletion requests"),
            L10n.choose("Để yêu cầu hỗ trợ hoặc xóa dữ liệu tài khoản trên máy chủ, hãy dùng kênh hỗ trợ công bố trên trang App Store. Việc xóa lịch sử trên iPhone không xóa bản ghi của tài khoản Admin trên máy chủ.",
                        "To request support or deletion of account data on the server, use the support contact listed on the App Store page. Deleting iPhone history does not remove Admin account records from the server.")
        )

        var resetConfiguration = UIButton.Configuration.bordered()
        resetConfiguration.title = L10n.choose("Hỏi lại trước khi phân tích", "Ask again before analysis")
        resetConfiguration.image = UIImage(systemName: "arrow.counterclockwise")
        resetConfiguration.imagePadding = 8
        let resetButton = UIButton(configuration: resetConfiguration)
        resetButton.heightAnchor.constraint(greaterThanOrEqualToConstant: 44).isActive = true
        resetButton.addAction(UIAction { [weak self] _ in
            UserDefaults.standard.removeObject(forKey: Constants.analysisConsentServerKey)
            let alert = UIAlertController(
                title: L10n.choose("Đã đặt lại lựa chọn", "Choice reset"),
                message: L10n.choose("Ứng dụng sẽ hỏi lại trước lần phân tích tiếp theo.", "The app will ask again before the next analysis."),
                preferredStyle: .alert
            )
            alert.addAction(UIAlertAction(title: L10n.choose("Đóng", "Close"), style: .default))
            self?.present(alert, animated: true)
        }, for: .touchUpInside)
        policyStack.addArrangedSubview(resetButton)

        view.addSubview(scrollView)
        scrollView.addSubview(policyStack)
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            policyStack.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor, constant: 24),
            policyStack.widthAnchor.constraint(equalTo: scrollView.frameLayoutGuide.widthAnchor, constant: -2 * 20),
            policyStack.leadingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.leadingAnchor, constant: 20),
            policyStack.trailingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.trailingAnchor, constant: -20),
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
