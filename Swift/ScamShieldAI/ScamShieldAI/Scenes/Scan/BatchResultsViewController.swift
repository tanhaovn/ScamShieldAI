import UIKit

final class BatchResultsViewController: UIViewController {
    private let results: [BatchURLResult]
    init(results: [BatchURLResult]) {
        self.results = results
        super.init(nibName: nil, bundle: nil)
    }
    required init?(coder: NSCoder) { fatalError("Use init(results:)") }

    override func viewDidLoad() {
        super.viewDidLoad()
        title = L10n.text("Kết quả nhiều URL")
        view.backgroundColor = AppTheme.pageBackgroundColor
        navigationItem.rightBarButtonItem = UIBarButtonItem(title: L10n.text("Xuất CSV"), style: .plain, target: self, action: #selector(exportCSV))
        let scroll = UIScrollView()
        let stack = UIStackView()
        stack.axis = .vertical
        stack.spacing = 16
        scroll.translatesAutoresizingMaskIntoConstraints = false
        stack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(scroll)
        scroll.addSubview(stack)
        let summary = InformationCardView(title: L10n.choose("Đã kiểm tra \(results.count) URL", "Checked \(results.count) URL"), systemImageName: "link")
        summary.configure(text: L10n.choose("\(results.filter { $0.status == "checked" }.count) hợp lệ · \(results.filter { $0.status != "checked" }.count) không hợp lệ", "\(results.filter { $0.status == "checked" }.count) valid · \(results.filter { $0.status != "checked" }.count) invalid"))
        stack.addArrangedSubview(summary)
        for result in results {
            let level = RiskLevel(rawValue: result.risk_level)
            let card = InformationCardView(title: result.url, systemImageName: result.status == "checked" ? "link" : "exclamationmark.triangle")
            card.configure(text: result.status == "checked"
                ? L10n.choose("\(level?.displayName ?? "Chưa xác định") · \(result.risk_score)/100", "\(level?.displayName ?? "Unknown") · \(result.risk_score)/100")
                : L10n.text("URL không hợp lệ · Chưa được phân tích"))
            stack.addArrangedSubview(card)
        }
        NSLayoutConstraint.activate([
            scroll.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scroll.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor),
            scroll.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scroll.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            stack.topAnchor.constraint(equalTo: scroll.contentLayoutGuide.topAnchor, constant: 20),
            stack.bottomAnchor.constraint(equalTo: scroll.contentLayoutGuide.bottomAnchor, constant: -24),
            stack.widthAnchor.constraint(equalTo: scroll.frameLayoutGuide.widthAnchor, constant: -2 * 20),
            stack.leadingAnchor.constraint(equalTo: scroll.contentLayoutGuide.leadingAnchor, constant: 20),
            stack.trailingAnchor.constraint(equalTo: scroll.contentLayoutGuide.trailingAnchor, constant: -20)
        ])
    }

    @objc private func exportCSV() {
        do {
            let url = FileManager.default.temporaryDirectory.appendingPathComponent("ScamShield-URLs-\(UUID()).csv")
            try BatchCSV.data(results).write(to: url, options: .atomic)
            let share = UIActivityViewController(activityItems: [url], applicationActivities: nil)
            share.popoverPresentationController?.barButtonItem = navigationItem.rightBarButtonItem
            share.completionWithItemsHandler = { _, _, _, _ in try? FileManager.default.removeItem(at: url) }
            present(share, animated: true)
        } catch { showErrorAlert(message: L10n.text("Không xuất được CSV. Vui lòng thử lại.")) }
    }
}
