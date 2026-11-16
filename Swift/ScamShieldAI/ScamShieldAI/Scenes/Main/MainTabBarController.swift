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

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        configureAppearance()
        configureTabs()
        delegate = self
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

    func configureTabs() {
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

        let scanViewController = ScanViewController(scanService: scanService)
        overviewViewController.onChooseSource = { [weak self, weak scanViewController] kind in
            self?.selectedIndex = 1
            (self?.viewControllers?[1] as? UINavigationController)?.popToRootViewController(animated: false)
            scanViewController?.selectInput(kind)
        }
        let historyViewController = HistoryViewController(historyService: historyService)
        let accountViewController = AccountViewController(user: user)

        viewControllers = [
            makeNavigationController(
                root: overviewViewController,
                title: "Tổng quan",
                imageName: "shield.checkered"
            ),
            makeNavigationController(
                root: scanViewController,
                title: "Kiểm tra",
                imageName: "viewfinder"
            ),
            makeNavigationController(
                root: historyViewController,
                title: "Lịch sử",
                imageName: "clock.arrow.circlepath"
            ),
            makeNavigationController(
                root: accountViewController,
                title: "Cá nhân",
                imageName: "person.crop.circle"
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
