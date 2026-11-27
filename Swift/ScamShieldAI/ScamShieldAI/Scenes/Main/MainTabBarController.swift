import UIKit

final class MainTabBarController: UITabBarController, UITabBarControllerDelegate {

    // MARK: - Dependencies

    private let user: User
    private let historyService: HistoryService
    private let scanService: ScanService

    // MARK: - Properties


    // MARK: - Initialization

    init(
        user: User,
        historyService: HistoryService = HistoryService(),
        scanService: ScanService = ScanService()
    ) {
        self.user = user
        self.historyService = historyService
        self.scanService = scanService
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("MainTabBarController chỉ được khởi tạo bằng code.")
    }

    deinit { NotificationCenter.default.removeObserver(self) }

    @objc private func languageChanged() {
        let selected = selectedIndex
        let currentScan = (viewControllers?[1] as? UINavigationController)?.viewControllers.first as? ScanViewController
        configureTabs(previousScan: currentScan)
        selectedIndex = selected
    }

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        configureAppearance()
        configureTabs()
        delegate = self
        NotificationCenter.default.addObserver(self, selector: #selector(languageChanged), name: L10n.didChange, object: nil)
    }
}

// MARK: - Setup UI

private extension MainTabBarController {

    func configureAppearance() {
        view.backgroundColor = AppTheme.pageBackgroundColor
        tabBar.tintColor = AppTheme.primaryColor
        tabBar.unselectedItemTintColor = AppTheme.secondaryTextColor

        let appearance = UITabBarAppearance()
        appearance.configureWithTransparentBackground()
        appearance.backgroundEffect = UIBlurEffect(style: .systemUltraThinMaterial)
        appearance.backgroundColor = AppTheme.cardBackgroundColor.withAlphaComponent(0.94)
        appearance.shadowColor = AppTheme.borderColor
        appearance.stackedLayoutAppearance.selected.titleTextAttributes = [
            .font: UIFont.systemFont(ofSize: 10, weight: .semibold)
        ]
        tabBar.standardAppearance = appearance
        if #available(iOS 15.0, *) {
            tabBar.scrollEdgeAppearance = appearance
        }
    }

    func configureTabs(previousScan: ScanViewController? = nil) {
        let overviewViewController = OverviewViewController(
            user: user,
            historyService: historyService
        )
        overviewViewController.onStartScan = { [weak self] in
            guard let self else { return }
            selectedIndex = 1
            (viewControllers?[1] as? UINavigationController)?.popToRootViewController(animated: false)
            animateSelectedTab(viewControllers?[1])
        }

        let scanViewController = previousScan?.isBusy == true ? previousScan! : ScanViewController(scanService: scanService)
        if scanViewController !== previousScan { previousScan?.transferDraft(to: scanViewController) }
        let historyViewController = HistoryViewController(historyService: historyService)
        let accountViewController = AccountViewController(user: user)
        let adminViewController = AdminViewController()

        viewControllers = [
            makeNavigationController(
                root: overviewViewController,
                title: L10n.text("Tổng quan"),
                imageName: "shield.checkered"
            ),
            (previousScan?.isBusy == true ? previousScan!.navigationController! : makeNavigationController(
                root: scanViewController,
                title: L10n.text("Kiểm tra"),
                imageName: "viewfinder"
            )),
            makeNavigationController(
                root: historyViewController,
                title: L10n.text("Lịch sử"),
                imageName: "clock.arrow.circlepath"
            ),
            makeNavigationController(
                root: accountViewController,
                title: L10n.text("Cá nhân"),
                imageName: "person.crop.circle"
            ),
            makeNavigationController(
                root: adminViewController,
                title: "Admin",
                imageName: "rectangle.portrait.and.arrow.right"
            )
        ]
    }

    func makeNavigationController(
        root: UIViewController,
        title: String,
        imageName: String
    ) -> UINavigationController {
        let navigationController = UINavigationController(rootViewController: root)
        navigationController.tabBarItem = UITabBarItem(
            title: title,
            image: UIImage(systemName: imageName),
            selectedImage: UIImage(systemName: imageName + ".fill") ?? UIImage(systemName: imageName)
        )

        let appearance = UINavigationBarAppearance()
        appearance.configureWithTransparentBackground()
        appearance.backgroundEffect = UIBlurEffect(style: .systemThinMaterial)
        appearance.backgroundColor = AppTheme.pageBackgroundColor.withAlphaComponent(0.82)
        appearance.shadowColor = .clear
        appearance.titleTextAttributes = [.foregroundColor: AppTheme.titleColor, .font: UIFont.systemFont(ofSize: 17, weight: .semibold)]
        appearance.largeTitleTextAttributes = [.foregroundColor: AppTheme.titleColor, .font: UIFont.systemFont(ofSize: 30, weight: .bold)]
        navigationController.navigationBar.standardAppearance = appearance
        navigationController.navigationBar.scrollEdgeAppearance = appearance
        navigationController.navigationBar.tintColor = AppTheme.primaryColor
        navigationController.navigationBar.prefersLargeTitles = true
        return navigationController
    }
}

// MARK: - Tab Bar Animation

extension MainTabBarController {

    func tabBarController(
        _ tabBarController: UITabBarController,
        didSelect viewController: UIViewController
    ) {
        animateSelectedTab(viewController)
        UISelectionFeedbackGenerator().selectionChanged()
    }

    func animateSelectedTab(_ viewController: UIViewController?) {
        guard let selectedView = viewController?.view,
              !UIAccessibility.isReduceMotionEnabled else { return }

        selectedView.alpha = 0.94

        UIView.animate(
            withDuration: 0.22,
            delay: 0,
            options: [.curveEaseOut, .allowUserInteraction, .beginFromCurrentState]
        ) {
            selectedView.alpha = 1
        }
    }
}
