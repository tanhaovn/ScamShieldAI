import UIKit

extension HistoryViewController: UISearchResultsUpdating {
    func updateSearchResults(for searchController: UISearchController) {
        guard currentState == .content || currentState == .empty else { return }
        tableView.reloadData()
        render(state: filteredItems.isEmpty ? .empty : .content)
    }
}

final class HistoryViewController: UIViewController {

    // MARK: - Dependencies

    private let historyService: HistoryService

    // MARK: - Properties

    private var items: [ScanHistoryItem] = []
    private var currentState: State = .loading
    private var animatedItemIDs = Set<Int>()
    private var loadTask: Task<Void, Never>?
    private var deleteTask: Task<Void, Never>?
    private let pushAnimator = SlideInPushAnimator()
    private let searchController = UISearchController(searchResultsController: nil)

    // MARK: - UI Components

    private let tableView: UITableView = {
        let view = UITableView(frame: .zero, style: .plain)
        view.backgroundColor = .clear
        view.separatorStyle = .none
        // Allow filenames and accessibility text sizes to expand without clipping.
        view.rowHeight = UITableView.automaticDimension
        view.estimatedRowHeight = 148
        view.contentInset = UIEdgeInsets(top: 4, left: 0, bottom: 100, right: 0)
        view.refreshControl = UIRefreshControl()
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()

    private let summaryCard = GradientCardView(colors: [AppTheme.brandDark, AppTheme.brandDeep])
    private let filterControl = UISegmentedControl(items: ["Tất cả", "Thấp", "Nghi ngờ", "Nguy hiểm"])
    private var filteredItems: [ScanHistoryItem] {
        let levels: [RiskLevel] = [.safe, .suspicious, .dangerous]
        let index = filterControl.selectedSegmentIndex
        let query = (searchController.searchBar.text ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        return items.filter { item in
            let matchesLevel = index <= 0 || item.riskLevel == levels[index - 1]
            let text = [item.originalFilename, item.extractedText, item.explanation, item.createdAt?.backendDateDisplayText]
                .compactMap { $0 }.joined(separator: " ")
            return matchesLevel && (query.isEmpty || text.range(of: query, options: [.caseInsensitive, .diacriticInsensitive]) != nil)
        }
    }
    private let countLabel = UILabel()

    private let stateStack = UIStackView()
    private let stateIcon = UIImageView()
    private let stateTitleLabel = UILabel()
    private let stateMessageLabel = UILabel()
    private let retryButton = UIButton(type: .system)
    private let activityIndicator = UIActivityIndicatorView(style: .large)

    // MARK: - Initialization

    init(historyService: HistoryService) {
        self.historyService = historyService
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("HistoryViewController chỉ được khởi tạo bằng code.")
    }

    deinit {
        loadTask?.cancel()
        deleteTask?.cancel()
        NotificationCenter.default.removeObserver(self)
    }

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        configureActions()
        loadHistory(showLoadingState: true)
    }
}

// MARK: - Setup UI

private extension HistoryViewController {

    func setupUI() {
        navigationItem.title = "Lịch sử kiểm tra"
        navigationItem.largeTitleDisplayMode = .never
        view.backgroundColor = AppTheme.pageBackgroundColor
        navigationItem.backButtonDisplayMode = .minimal
        searchController.searchResultsUpdater = self
        searchController.obscuresBackgroundDuringPresentation = false
        searchController.searchBar.placeholder = "Tìm tên, nội dung hoặc ngày"
        searchController.searchBar.tintColor = AppTheme.primaryColor
        navigationItem.searchController = searchController
        navigationItem.hidesSearchBarWhenScrolling = false
        definesPresentationContext = true
        tableView.keyboardDismissMode = .onDrag

        tableView.registerCell(ScanHistoryCell.self)
        tableView.dataSource = self
        tableView.delegate = self

        configureSummaryCard()

        stateIcon.contentMode = .scaleAspectFit
        stateIcon.tintColor = AppTheme.primaryColor
        stateIcon.translatesAutoresizingMaskIntoConstraints = false

        stateTitleLabel.font = AppTheme.font(size: 20, weight: .bold)
        stateTitleLabel.adjustsFontForContentSizeCategory = true
        stateTitleLabel.numberOfLines = 0
        stateTitleLabel.textColor = AppTheme.titleColor
        stateTitleLabel.textAlignment = .center

        stateMessageLabel.font = AppTheme.font(size: 14)
        stateMessageLabel.adjustsFontForContentSizeCategory = true
        stateMessageLabel.textColor = AppTheme.secondaryTextColor
        stateMessageLabel.textAlignment = .center
        stateMessageLabel.numberOfLines = 0

        var retryConfiguration = UIButton.Configuration.tinted()
        retryConfiguration.title = "Thử lại"
        retryConfiguration.image = UIImage(systemName: "arrow.clockwise")
        retryConfiguration.imagePadding = 7
        retryConfiguration.baseForegroundColor = AppTheme.primaryColor
        retryButton.configuration = retryConfiguration
        retryButton.enableSoftPressAnimation()

        stateStack.axis = .vertical
        stateStack.alignment = .center
        stateStack.spacing = 10
        [stateIcon, activityIndicator, stateTitleLabel, stateMessageLabel, retryButton]
            .forEach(stateStack.addArrangedSubview)
        stateStack.translatesAutoresizingMaskIntoConstraints = false

        installAppBackground()
        filterControl.selectedSegmentIndex = 0
        filterControl.selectedSegmentTintColor = AppTheme.cardBackgroundColor
        filterControl.backgroundColor = AppTheme.softColor
        filterControl.setTitleTextAttributes([.foregroundColor: AppTheme.titleColor, .font: UIFont.systemFont(ofSize: 11, weight: .semibold)], for: .normal)
        filterControl.translatesAutoresizingMaskIntoConstraints = false
        filterControl.addTarget(self, action: #selector(didChangeFilter), for: .valueChanged)
        view.addSubviews(summaryCard, filterControl, tableView, stateStack)
        NSLayoutConstraint.activate([
            summaryCard.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 8),
            summaryCard.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            summaryCard.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),

            filterControl.topAnchor.constraint(equalTo: summaryCard.bottomAnchor, constant: 18),
            filterControl.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            filterControl.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            filterControl.heightAnchor.constraint(equalToConstant: 44),
            tableView.topAnchor.constraint(equalTo: filterControl.bottomAnchor, constant: 12),
            tableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            tableView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            stateStack.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            stateStack.centerYAnchor.constraint(equalTo: tableView.centerYAnchor, constant: -30),
            stateStack.leadingAnchor.constraint(greaterThanOrEqualTo: view.leadingAnchor, constant: 36),
            stateStack.trailingAnchor.constraint(lessThanOrEqualTo: view.trailingAnchor, constant: -36),
            stateIcon.widthAnchor.constraint(equalToConstant: 58),
            stateIcon.heightAnchor.constraint(equalToConstant: 58)
        ])
    }

    func configureSummaryCard() {
        summaryCard.translatesAutoresizingMaskIntoConstraints = false
        let radar = UIImageView(image: UIImage(systemName: "clock.arrow.circlepath"))
        radar.preferredSymbolConfiguration = .init(pointSize: 32, weight: .light)
        radar.tintColor = AppTheme.mintColor
        radar.contentMode = .center
        radar.backgroundColor = UIColor.white.withAlphaComponent(0.08)
        radar.layer.cornerRadius = 22
        radar.translatesAutoresizingMaskIntoConstraints = false
        let eyebrow = UILabel()
        eyebrow.text = "HOẠT ĐỘNG CỦA BẠN"
        eyebrow.font = .systemFont(ofSize: 10, weight: .bold)
        eyebrow.textColor = AppTheme.mintColor
        countLabel.text = "0 lần kiểm tra"
        countLabel.font = AppTheme.displayFont(size: 24, weight: .bold)
        countLabel.adjustsFontForContentSizeCategory = true
        countLabel.textColor = .white
        countLabel.numberOfLines = 0
        let hint = UILabel()
        hint.text = "Lưu riêng trên thiết bị của bạn."
        hint.font = .systemFont(ofSize: 12)
        hint.textColor = .white.withAlphaComponent(0.75)
        hint.numberOfLines = 0
        let text = UIStackView(arrangedSubviews: [eyebrow, countLabel, hint])
        text.axis = .vertical
        text.spacing = 6
        let stack = UIStackView(arrangedSubviews: [text, radar])
        stack.alignment = .center
        stack.spacing = 8
        stack.translatesAutoresizingMaskIntoConstraints = false
        summaryCard.addSubview(stack)
        NSLayoutConstraint.activate([
            radar.widthAnchor.constraint(equalToConstant: 44),
            radar.heightAnchor.constraint(equalToConstant: 44),
            stack.topAnchor.constraint(equalTo: summaryCard.topAnchor, constant: 18),
            stack.leadingAnchor.constraint(equalTo: summaryCard.leadingAnchor, constant: 20),
            stack.trailingAnchor.constraint(equalTo: summaryCard.trailingAnchor, constant: -16),
            stack.bottomAnchor.constraint(equalTo: summaryCard.bottomAnchor, constant: -18)
        ])
    }

    func configureActions() {
        NotificationCenter.default.addObserver(self, selector: #selector(didCompleteScan), name: .historyDidChange, object: nil)
        tableView.refreshControl?.addTarget(self, action: #selector(didPullToRefresh), for: .valueChanged)
        retryButton.addTarget(self, action: #selector(didTapRetry), for: .touchUpInside)
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(didCompleteScan),
            name: .scanDidComplete,
            object: nil
        )
    }
}

// MARK: - Data

private extension HistoryViewController {

    enum State {
        case loading
        case content
        case empty
        case error
    }

    func loadHistory(showLoadingState: Bool) {
        loadTask?.cancel()
        if showLoadingState { render(state: .loading) }

        loadTask = Task { [weak self] in
            guard let self else { return }

            do {
                let loadedItems = try await historyService.fetchHistory()
                guard !Task.isCancelled else { return }
                items = loadedItems
                tableView.refreshControl?.endRefreshing()
                tableView.reloadData()
                updateHistoryControls()
                render(state: filteredItems.isEmpty ? .empty : .content)
            } catch {
                guard !Task.isCancelled else { return }
                tableView.refreshControl?.endRefreshing()
                render(state: .error)
            }
        }
    }

    func render(state: State) {
        currentState = state
        tableView.isHidden = state != .content
        summaryCard.isHidden = false
        stateStack.isHidden = state == .content
        activityIndicator.stopAnimating()
        stateIcon.isHidden = false
        stateTitleLabel.isHidden = false
        retryButton.isHidden = true

        switch state {
        case .loading:
            stateIcon.isHidden = true
            stateTitleLabel.isHidden = true
            stateMessageLabel.text = "Đang tải lịch sử..."
            activityIndicator.startAnimating()
        case .content:
            break
        case .empty:
            stateIcon.image = UIImage(systemName: "clock.badge.questionmark")
            stateTitleLabel.text = items.isEmpty ? "Chưa có lịch sử" : "Chưa có kết quả phù hợp"
            stateMessageLabel.text = items.isEmpty ? "Ảnh bạn kiểm tra sẽ xuất hiện tại đây." : "Thử đổi từ khóa hoặc chọn một mức rủi ro khác."
        case .error:
            stateIcon.image = UIImage(systemName: "wifi.exclamationmark")
            stateTitleLabel.text = "Không thể tải dữ liệu"
            stateMessageLabel.text = "Chưa đọc được lịch sử trên thiết bị. Vui lòng thử lại."
            retryButton.isHidden = false
        }
    }

    func updateHistoryControls() {
        countLabel.text = "\(items.count) lần kiểm tra"
        tableView.isUserInteractionEnabled = deleteTask == nil
    }
}

// MARK: - Actions

private extension HistoryViewController {

    @objc func didChangeFilter() {
        guard currentState == .content || currentState == .empty else { return }
        tableView.reloadData()
        render(state: filteredItems.isEmpty ? .empty : .content)
        UISelectionFeedbackGenerator().selectionChanged()
    }

    @objc func didPullToRefresh() {
        loadHistory(showLoadingState: false)
    }

    @objc func didTapRetry() {
        loadHistory(showLoadingState: true)
    }

    @objc func didCompleteScan() {
        loadHistory(showLoadingState: items.isEmpty)
    }

    func confirmDelete(item: ScanHistoryItem) {
        let alert = UIAlertController(
            title: "Xóa kết quả này?",
            message: item.originalFilename ?? "Ảnh kiểm tra #\(item.id)",
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "Hủy", style: .cancel))
        alert.addAction(UIAlertAction(title: "Xóa", style: .destructive) { [weak self] _ in
            self?.deleteHistoryItem(id: item.id)
        })
        present(alert, animated: true)
    }

    func deleteHistoryItem(id: Int) {
        guard deleteTask == nil else { return }
        tableView.isUserInteractionEnabled = false

        deleteTask = Task { [weak self] in
            guard let self else { return }
            defer {
                deleteTask = nil
                updateHistoryControls()
            }

            do {
                try await historyService.deleteHistoryItem(id: id)
                guard let index = items.firstIndex(where: { $0.id == id }) else { return }
                items.remove(at: index)
                tableView.reloadData()
                updateHistoryControls()
                render(state: filteredItems.isEmpty ? .empty : .content)
                NotificationCenter.default.post(name: .historyDidChange, object: nil)
                UINotificationFeedbackGenerator().notificationOccurred(.success)
            } catch {
                showErrorAlert(message: error.localizedDescription)
            }
        }
    }
}

// MARK: - Table Data Source

extension HistoryViewController: UITableViewDataSource {

    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        filteredItems.count
    }

    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell: ScanHistoryCell = tableView.dequeueCell(for: indexPath)
        cell.configure(item: filteredItems[indexPath.row])
        return cell
    }
}

// MARK: - Table Delegate

extension HistoryViewController: UITableViewDelegate {

    func tableView(
        _ tableView: UITableView,
        willDisplay cell: UITableViewCell,
        forRowAt indexPath: IndexPath
    ) {
        guard filteredItems.indices.contains(indexPath.row) else { return }
        let itemID = filteredItems[indexPath.row].id

        // Mỗi kết quả chỉ trượt vào một lần để cuộn danh sách vẫn nhẹ và tự nhiên.
        guard animatedItemIDs.insert(itemID).inserted,
              !UIAccessibility.isReduceMotionEnabled else {
            cell.alpha = 1
            cell.transform = .identity
            return
        }

        cell.alpha = 0.78
        cell.transform = CGAffineTransform(translationX: 0, y: 6)
        UIView.animate(
            withDuration: 0.28,
            delay: min(Double(indexPath.row) * 0.025, 0.10),
            options: [.curveEaseOut, .allowUserInteraction, .beginFromCurrentState]
        ) {
            cell.alpha = 1
            cell.transform = .identity
        }
    }

    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        // Gán delegate trước khi push để dùng hiệu ứng spring tuỳ chỉnh.
        navigationController?.delegate = self
        let item = filteredItems[indexPath.row]
        let detail: UIViewController
        if let result = item.result {
            let image = item.imageURL.flatMap { Constants.mediaURL(from: $0) }.flatMap { UIImage(contentsOfFile: $0.path) }
            detail = ScanResultViewController(result: result, image: image)
        } else { detail = HistoryDetailViewController(item: item) }
        navigationController?.pushViewController(detail, animated: true)
    }

    func tableView(
        _ tableView: UITableView,
        trailingSwipeActionsConfigurationForRowAt indexPath: IndexPath
    ) -> UISwipeActionsConfiguration? {
        let item = filteredItems[indexPath.row]
        let deleteAction = UIContextualAction(
            style: .destructive,
            title: "Xóa"
        ) { [weak self] _, _, completion in
            // Chưa sửa data source cho tới khi người dùng xác nhận và API xóa thành công.
            completion(false)
            self?.confirmDelete(item: item)
        }
        deleteAction.image = UIImage(systemName: "trash.fill")

        let configuration = UISwipeActionsConfiguration(actions: [deleteAction])
        configuration.performsFirstActionWithFullSwipe = false
        return configuration
    }
}

// MARK: - Navigation Transition Delegate

extension HistoryViewController: UINavigationControllerDelegate {

    func navigationController(
        _ navigationController: UINavigationController,
        animationControllerFor operation: UINavigationController.Operation,
        from fromVC: UIViewController,
        to toVC: UIViewController
    ) -> (any UIViewControllerAnimatedTransitioning)? {
        // Chỉ dùng animator tuỳ chỉnh khi push vào màn chi tiết.
        // Pop (vuốt back) dùng animation mặc định của UIKit (trả về nil).
        if operation == .push, toVC is HistoryDetailViewController {
            return pushAnimator
        }
        return nil
    }

    func navigationController(
        _ navigationController: UINavigationController,
        didShow viewController: UIViewController,
        animated: Bool
    ) {
        // Sau khi transition hoàn tất, trả delegate về nil để không ảnh hưởng
        // đến gesture vuốt back hoặc các màn hình khác trong navigation stack.
        if viewController is HistoryDetailViewController {
            navigationController.delegate = nil
        }
    }
}
