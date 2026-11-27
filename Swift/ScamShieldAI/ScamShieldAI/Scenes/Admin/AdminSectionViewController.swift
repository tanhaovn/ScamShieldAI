import MapKit
import UIKit

enum AdminSection: String, CaseIterable {
    case history, dataset, models, evaluations, keywords, feedback, devices, logs

    var title: String {
        switch self {
        case .history: return L10n.choose("Lịch sử kiểm tra", "Check history")
        case .dataset: return L10n.choose("Dữ liệu huấn luyện", "Training dataset")
        case .models: return L10n.choose("Mô hình AI", "AI models")
        case .evaluations: return L10n.choose("Đánh giá mô hình", "Model evaluations")
        case .keywords: return L10n.choose("Từ khóa lừa đảo", "Scam keywords")
        case .feedback: return L10n.choose("Phản hồi người dùng", "User feedback")
        case .devices: return L10n.choose("Thiết bị truy cập", "Visitor devices")
        case .logs: return L10n.choose("Nhật ký hệ thống", "System logs")
        }
    }

    var subtitle: String {
        switch self {
        case .history: return L10n.choose("Lượt quét tài khoản và trên thiết bị", "Account and device scans")
        case .dataset: return L10n.choose("Quản lý mẫu huấn luyện", "Manage training samples")
        case .models: return L10n.choose("Phiên bản và trạng thái", "Versions and status")
        case .evaluations: return L10n.choose("Chất lượng bộ phát hiện", "Detector quality")
        case .keywords: return L10n.choose("Quy tắc phát hiện đang dùng", "Active detection rules")
        case .feedback: return L10n.choose("Xác nhận kết quả kiểm tra", "Check result validation")
        case .devices: return L10n.choose("Thiết bị và khu vực mạng", "Devices and network areas")
        case .logs: return L10n.choose("Hoạt động quản trị", "Administrative activity")
        }
    }

    var symbol: String {
        switch self {
        case .history: return "clock.arrow.circlepath"
        case .dataset: return "square.stack.3d.up"
        case .models: return "cube.transparent"
        case .evaluations: return "chart.bar.xaxis"
        case .keywords: return "textformat.abc"
        case .feedback: return "text.bubble"
        case .devices: return "iphone.gen3.radiowaves.left.and.right"
        case .logs: return "doc.text"
        }
    }

    var path: String {
        switch self {
        case .history: return "/scan-history"
        case .dataset: return "/training-dataset"
        case .models: return "/ai-models"
        case .evaluations: return "/model-evaluations"
        case .keywords: return "/scam-keywords"
        case .feedback: return "/scan-feedback"
        case .devices: return "/admin/devices"
        case .logs: return "/system-logs"
        }
    }

    var formFields: [AdminFormField] {
        switch self {
        case .dataset: return [
            .init(key: "image_url", title: "URL ảnh", kind: .text, required: true),
            .init(key: "scam_category_id", title: L10n.choose("ID danh mục (nếu có)", "Category ID (optional)"), kind: .integer),
            .init(key: "is_anonymized", title: L10n.choose("Đã ẩn danh", "Anonymized"), kind: .toggle),
            .init(key: "is_verified", title: L10n.choose("Đã xác minh", "Verified"), kind: .toggle)
        ]
        case .models: return [
            .init(key: "version_name", title: L10n.choose("Tên phiên bản", "Version name"), kind: .text, required: true),
            .init(key: "description", title: L10n.choose("Mô tả", "Description"), kind: .text),
            .init(key: "is_active", title: L10n.choose("Đang hoạt động", "Active"), kind: .toggle)
        ]
        case .evaluations: return [
            .init(key: "ai_model_id", title: "ID model", kind: .integer, required: true),
            .init(key: "macro_f1", title: "Macro F1 (0–1)", kind: .decimal),
            .init(key: "recall", title: "Recall (0–1)", kind: .decimal),
            .init(key: "false_alarm_rate", title: "False alarm rate (0–1)", kind: .decimal),
            .init(key: "explanation_usefulness", title: L10n.choose("Độ hữu ích giải thích (0–1)", "Explanation usefulness (0–1)"), kind: .decimal)
        ]
        case .keywords: return [
            .init(key: "keyword", title: L10n.choose("Từ khóa hoặc cụm từ", "Keyword or phrase"), kind: .text, required: true),
            .init(key: "category", title: L10n.choose("Nhóm (ví dụ phishing)", "Category (e.g. phishing)"), kind: .text, required: true, defaultValue: "phishing"),
            .init(key: "weight", title: L10n.choose("Trọng số (1–50)", "Weight (1–50)"), kind: .integer, required: true, defaultValue: "10")
        ]
        case .logs: return [
            .init(key: "action_type", title: L10n.choose("Loại hoạt động", "Action type"), kind: .text, required: true),
            .init(key: "description", title: L10n.choose("Mô tả", "Description"), kind: .text)
        ]
        default: return []
        }
    }
}

struct AdminFormField {
    enum Kind: Equatable { case text, integer, decimal, toggle }
    let key: String
    let title: String
    let kind: Kind
    var required = false
    var defaultValue = ""
}

private struct AdminRecord {
    let values: [String: Any]
    let historyItem: ScanHistoryItem?
}

final class AdminSectionViewController: UIViewController, UITableViewDataSource, UITableViewDelegate {
    private let section: AdminSection
    private let session = AccountSession.shared
    private let tableView = UITableView(frame: .zero, style: .insetGrouped)
    private var records: [AdminRecord] = []
    private var loadTask: Task<Void, Never>?

    init(section: AdminSection) {
        self.section = section
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) { fatalError("AdminSectionViewController chỉ được khởi tạo bằng code.") }
    deinit { loadTask?.cancel() }

    override func viewDidLoad() {
        super.viewDidLoad()
        navigationItem.title = section.title
        navigationItem.largeTitleDisplayMode = .never
        view.backgroundColor = AppTheme.pageBackgroundColor
        tableView.backgroundColor = .clear
        tableView.dataSource = self
        tableView.delegate = self
        tableView.rowHeight = UITableView.automaticDimension
        tableView.estimatedRowHeight = 72
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "adminRecord")
        tableView.refreshControl = UIRefreshControl()
        tableView.refreshControl?.addTarget(self, action: #selector(refresh), for: .valueChanged)
        tableView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(tableView)
        NSLayoutConstraint.activate([
            tableView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            tableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            tableView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
        if !section.formFields.isEmpty {
            navigationItem.rightBarButtonItem = UIBarButtonItem(systemItem: .add, primaryAction: UIAction { [weak self] _ in self?.openForm() })
        }
        if section == .evaluations {
            let run = UIBarButtonItem(title: L10n.choose("Chạy", "Run"), primaryAction: UIAction { [weak self] _ in self?.runEvaluation() })
            navigationItem.rightBarButtonItems = [navigationItem.rightBarButtonItem, run].compactMap { $0 }
        }
        loadRows()
    }

    @objc private func refresh() { loadRows() }

    private func loadRows() {
        loadTask?.cancel()
        loadTask = Task { [weak self] in
            guard let self else { return }
            do {
                let remote = try await self.session.rows(path: self.section.path)
                var result: [AdminRecord] = remote.map { values in
                    let item: ScanHistoryItem? = self.section == .history
                        ? (try? JSONDecoder().decode(ScanHistoryItem.self, from: JSONSerialization.data(withJSONObject: values)))
                        : nil
                    return AdminRecord(values: values, historyItem: item)
                }
                if self.section == .history {
                    let serverIDs = Set(remote.compactMap { $0["id"] as? Int })
                    let local = (try? await HistoryService().fetchHistory()) ?? []
                    result += local.filter { item in
                        guard let serverID = item.result?.scanID else { return true }
                        return !serverIDs.contains(serverID)
                    }.map { item in
                        AdminRecord(values: ["id": item.id, "original_filename": item.listTitle,
                                             "risk_score": item.riskScore, "risk_level": item.riskLevel.rawValue,
                                             "created_at": item.createdAt ?? "", "storage": "device"], historyItem: item)
                    }
                    result.sort { String(describing: $0.values["created_at"] ?? "") > String(describing: $1.values["created_at"] ?? "") }
                }
                guard !Task.isCancelled else { return }
                self.records = result
                self.tableView.reloadData()
                self.updateDeviceMap()
                self.showMessage(result.isEmpty ? L10n.choose("Chưa có dữ liệu. Kéo xuống để làm mới.", "No records yet. Pull to refresh.") : nil)
            } catch {
                guard !Task.isCancelled else { return }
                self.showMessage(error.localizedDescription)
                if !self.session.isSignedIn { self.navigationController?.popViewController(animated: true) }
            }
            self.tableView.refreshControl?.endRefreshing()
        }
    }

    private func showMessage(_ message: String?) {
        guard let message else { tableView.backgroundView = nil; return }
        let label = UILabel()
        label.text = message
        label.font = AppTheme.font(size: 14)
        label.textColor = AppTheme.secondaryTextColor
        label.textAlignment = .center
        label.numberOfLines = 0
        tableView.backgroundView = label
    }

    private func updateDeviceMap() {
        guard section == .devices else { return }
        let located = records.compactMap { record -> (CLLocationCoordinate2D, String)? in
            guard let latitude = (record.values["latitude"] as? NSNumber)?.doubleValue,
                  let longitude = (record.values["longitude"] as? NSNumber)?.doubleValue else { return nil }
            return (CLLocationCoordinate2D(latitude: latitude, longitude: longitude),
                    record.values["device_name"] as? String ?? L10n.choose("Thiết bị", "Device"))
        }
        guard !located.isEmpty else { tableView.tableHeaderView = nil; return }
        let map = MKMapView(frame: CGRect(x: 0, y: 0, width: view.bounds.width, height: 230))
        map.isScrollEnabled = false
        map.isZoomEnabled = false
        for (coordinate, title) in located {
            let pin = MKPointAnnotation()
            pin.coordinate = coordinate
            pin.title = title
            map.addAnnotation(pin)
        }
        map.showAnnotations(map.annotations, animated: false)
        tableView.tableHeaderView = map
    }

    private func openForm() {
        let form = AdminFormViewController(section: section)
        form.onSaved = { [weak self] in self?.loadRows() }
        navigationController?.pushViewController(form, animated: true)
    }

    private func runEvaluation() {
        let alert = UIAlertController(title: L10n.choose("Chạy đánh giá tự động?", "Run automated evaluation?"),
                                      message: L10n.choose("Bộ ca kiểm thử sẽ chạy trên model hiện tại và lưu kết quả khi có model hoạt động.",
                                                           "Regression cases will run against the active model and save the result when one exists."),
                                      preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: L10n.choose("Hủy", "Cancel"), style: .cancel))
        alert.addAction(UIAlertAction(title: L10n.choose("Chạy đánh giá", "Run evaluation"), style: .default) { [weak self] _ in
            guard let self else { return }
            Task {
                do {
                    let result = try await self.session.post(path: "/model-evaluations/run")
                    self.navigationController?.pushViewController(AdminRecordDetailViewController(title: L10n.choose("Kết quả đánh giá", "Evaluation result"), values: result), animated: true)
                    self.loadRows()
                } catch { self.showError(error.localizedDescription) }
            }
        })
        present(alert, animated: true)
    }

    private func showError(_ message: String) {
        let alert = UIAlertController(title: L10n.choose("Không thể hoàn tất", "Could not complete"), message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }

    func tableView(_ tableView: UITableView, numberOfRowsInSection sectionIndex: Int) -> Int { records.count }

    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "adminRecord", for: indexPath)
        let record = records[indexPath.row]
        var content = cell.defaultContentConfiguration()
        content.text = recordTitle(record.values)
        content.secondaryText = recordSubtitle(record.values)
        content.image = UIImage(systemName: section.symbol)
        content.imageProperties.tintColor = AppTheme.primaryColor
        content.textProperties.color = AppTheme.titleColor
        content.secondaryTextProperties.color = AppTheme.secondaryTextColor
        cell.contentConfiguration = content
        cell.accessoryType = .disclosureIndicator
        cell.backgroundColor = AppTheme.cardBackgroundColor
        return cell
    }

    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        let record = records[indexPath.row]
        if let item = record.historyItem {
            navigationController?.pushViewController(HistoryDetailViewController(item: item), animated: true)
        } else {
            navigationController?.pushViewController(AdminRecordDetailViewController(title: recordTitle(record.values), values: record.values), animated: true)
        }
    }

    private func recordTitle(_ row: [String: Any]) -> String {
        switch section {
        case .history: return string(row["original_filename"], fallback: L10n.choose("Ảnh đã kiểm tra", "Checked image"))
        case .dataset: return string(row["image_url"], fallback: "Dataset #\(string(row["id"]))")
        case .models: return string(row["version_name"])
        case .evaluations: return "Model #\(string(row["ai_model_id"])) · F1 \(percent(row["macro_f1"]))"
        case .keywords: return string(row["keyword"])
        case .feedback: return string(row["original_filename"], fallback: string(row["verdict"]))
        case .devices: return string(row["device_name"], fallback: L10n.choose("Thiết bị chưa rõ", "Unknown device"))
        case .logs: return string(row["action_type"])
        }
    }

    private func recordSubtitle(_ row: [String: Any]) -> String {
        switch section {
        case .history:
            let levelCode = row["risk_level"] as? String ?? ""
            let level = RiskLevel(rawValue: levelCode)?.displayName ?? levelCode
            let location = (row["storage"] as? String) == "device"
                ? L10n.choose("Trên iPhone", "On iPhone") : L10n.choose("Máy chủ", "Server")
            return "\(string(row["risk_score"])) / 100 · \(level) · \(location)"
        case .dataset: return "#\(string(row["id"])) · \(string(row["created_at"]))"
        case .models: return "\(string(row["description"])) · \(string(row["is_active"]))"
        case .evaluations: return "Recall \(percent(row["recall"])) · FAR \(percent(row["false_alarm_rate"]))"
        case .keywords: return "\(string(row["category"])) · +\(string(row["weight"]))"
        case .feedback: return "\(string(row["verdict"])) · \(string(row["risk_score"])) / 100"
        case .devices: return "\(string(row["platform"])) · \(string(row["browser"])) · \(string(row["visit_count"])) lượt"
        case .logs: return "\(string(row["description"])) · \(string(row["created_at"]))"
        }
    }

    private func string(_ value: Any?, fallback: String = "—") -> String {
        guard let value, !(value is NSNull) else { return fallback }
        if let number = value as? NSNumber, CFGetTypeID(number) == CFBooleanGetTypeID() {
            return number.boolValue ? L10n.choose("Có", "Yes") : L10n.choose("Không", "No")
        }
        return String(describing: value)
    }

    private func percent(_ value: Any?) -> String {
        guard let number = value as? NSNumber else { return "—" }
        return "\(Int((number.doubleValue * 100).rounded()))%"
    }
}

final class AdminRecordDetailViewController: UIViewController {
    private let recordTitle: String
    private let values: [String: Any]

    init(title: String, values: [String: Any]) {
        recordTitle = title
        self.values = values
        super.init(nibName: nil, bundle: nil)
    }
    required init?(coder: NSCoder) { fatalError("AdminRecordDetailViewController chỉ được khởi tạo bằng code.") }

    override func viewDidLoad() {
        super.viewDidLoad()
        navigationItem.title = recordTitle
        view.backgroundColor = AppTheme.pageBackgroundColor
        let scroll = UIScrollView()
        scroll.translatesAutoresizingMaskIntoConstraints = false
        let stack = UIStackView()
        stack.axis = .vertical
        stack.spacing = 10
        stack.translatesAutoresizingMaskIntoConstraints = false
        for (key, value) in values.sorted(by: { $0.key < $1.key }) {
            let card = CardView()
            let keyLabel = UILabel()
            keyLabel.text = key.replacingOccurrences(of: "_", with: " ").uppercased()
            keyLabel.font = AppTheme.font(size: 10, weight: .bold)
            keyLabel.textColor = AppTheme.primaryColor
            let valueLabel = UILabel()
            valueLabel.text = display(value)
            valueLabel.font = AppTheme.font(size: 14)
            valueLabel.textColor = AppTheme.titleColor
            valueLabel.numberOfLines = 0
            let pair = UIStackView(arrangedSubviews: [keyLabel, valueLabel])
            pair.axis = .vertical
            pair.spacing = 7
            pair.translatesAutoresizingMaskIntoConstraints = false
            card.addSubview(pair)
            NSLayoutConstraint.activate([
                pair.topAnchor.constraint(equalTo: card.topAnchor, constant: 16),
                pair.leadingAnchor.constraint(equalTo: card.leadingAnchor, constant: 16),
                pair.trailingAnchor.constraint(equalTo: card.trailingAnchor, constant: -16),
                pair.bottomAnchor.constraint(equalTo: card.bottomAnchor, constant: -16)
            ])
            stack.addArrangedSubview(card)
        }
        view.addSubview(scroll)
        scroll.addSubview(stack)
        NSLayoutConstraint.activate([
            scroll.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scroll.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scroll.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scroll.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            stack.topAnchor.constraint(equalTo: scroll.contentLayoutGuide.topAnchor, constant: 16),
            stack.leadingAnchor.constraint(equalTo: scroll.contentLayoutGuide.leadingAnchor, constant: 16),
            stack.trailingAnchor.constraint(equalTo: scroll.contentLayoutGuide.trailingAnchor, constant: -16),
            stack.widthAnchor.constraint(equalTo: scroll.frameLayoutGuide.widthAnchor, constant: -32),
            stack.bottomAnchor.constraint(equalTo: scroll.contentLayoutGuide.bottomAnchor, constant: -24)
        ])
    }

    private func display(_ value: Any) -> String {
        if value is NSNull { return "—" }
        if let array = value as? [Any],
           let data = try? JSONSerialization.data(withJSONObject: array, options: [.prettyPrinted, .sortedKeys]),
           let text = String(data: data, encoding: .utf8) { return text }
        if let object = value as? [String: Any],
           let data = try? JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .sortedKeys]),
           let text = String(data: data, encoding: .utf8) { return text }
        return String(describing: value)
    }
}
