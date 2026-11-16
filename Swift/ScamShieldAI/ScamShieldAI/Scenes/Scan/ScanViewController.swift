import PhotosUI
import AVFoundation
import UIKit
import UniformTypeIdentifiers

final class ScanViewController: UIViewController {

    // MARK: - Dependencies

    private let scanService: ScanService

    // MARK: - Properties

    private var inputKind: ScanInputKind = .image
    private let sourceControl = UISegmentedControl(items: ScanInputKind.allCases.map(\.title))
    private let imageSection = UIStackView()
    private let textSection = UIStackView()
    private let documentSection = UIStackView()
    private let contentEditor = UITextView()
    private var editorHeightConstraint: NSLayoutConstraint?
    private let inputHint = UILabel()
    private let characterCount = UILabel()
    private let documentLabel = UILabel()
    private var textDraft = ""
    private var urlDraft = ""
    private var documentData: Data?
    private var documentName: String?
    private var categories: [ScamCategory] = []
    private var selectedCategory: ScamCategory?
    private var selectedImage: UIImage?
    private var categoryTask: Task<Void, Never>?
    private var scanTask: Task<Void, Never>?
    private var hasAnimatedEntrance = false
    private var isAnalyzing = false
    private var imageLoadID = UUID()
    private let imageStatusLabel = UILabel()
    private let actionDock = UIVisualEffectView(effect: UIBlurEffect(style: .systemMaterial))

    // MARK: - UI Components

    private let scrollView: UIScrollView = {
        let view = UIScrollView()
        view.keyboardDismissMode = .interactive
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()

    private let contentStack = UIStackView()
    private let categoryButton = UIButton(type: .system)
    private let previewCard = CardView()
    private let scanFrame = ScanFrameView()

    private let previewImageView: UIImageView = {
        let view = UIImageView()
        view.contentMode = .scaleAspectFit
        view.clipsToBounds = true
        view.backgroundColor = AppTheme.softColor
        view.tintColor = AppTheme.secondaryTextColor
        view.layer.cornerRadius = 16
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()

    private let previewPlaceholder = UIStackView()

    private let analyzeButton: PrimaryButton = {
        let button = PrimaryButton(type: .system)
        button.setPrimaryTitle("Phân tích rủi ro")
        button.isEnabled = false
        button.alpha = 0.55
        return button
    }()

    private let statusLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 13, weight: .medium)
        label.textColor = AppTheme.secondaryTextColor
        label.numberOfLines = 0
        label.textAlignment = .center
        label.isHidden = true
        return label
    }()

    // MARK: - Initialization

    init(scanService: ScanService) {
        self.scanService = scanService
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("ScanViewController chỉ được khởi tạo bằng code.")
    }

    deinit {
        categoryTask?.cancel()
        scanTask?.cancel()
        NotificationCenter.default.removeObserver(self)
    }

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        configureActions()
        loadCategories()
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        animateEntranceIfNeeded()
    }
}

// MARK: - Setup UI

private extension ScanViewController {

    func setupUI() {
        navigationItem.title = "Kiểm tra lừa đảo"
        navigationItem.largeTitleDisplayMode = .never
        scrollView.contentInset.bottom = 16
        scrollView.showsVerticalScrollIndicator = false
        view.backgroundColor = AppTheme.pageBackgroundColor
        navigationItem.backButtonDisplayMode = .minimal

        contentStack.axis = .vertical
        contentStack.spacing = 24
        contentStack.translatesAutoresizingMaskIntoConstraints = false

        configureCategoryButton()
        updateCategoryMenu()

        configurePreviewCard()
        let sourceButtons = makeSourceButtons()

        let privacyLabel = UILabel()
        privacyLabel.text = "🔒 Lịch sử lưu riêng trên thiết bị. Nội dung được gửi đến máy chủ để phân tích."
        privacyLabel.font = .preferredFont(forTextStyle: .footnote)
        privacyLabel.adjustsFontForContentSizeCategory = true
        privacyLabel.textColor = AppTheme.secondaryTextColor
        privacyLabel.numberOfLines = 0
        privacyLabel.textAlignment = .center

        imageSection.axis = .vertical
        imageSection.spacing = 14
        [previewCard, sourceButtons, makeFieldTitle("Danh mục · không bắt buộc"), categoryButton].forEach(imageSection.addArrangedSubview)
        configureContentInputs()
        sourceControl.selectedSegmentIndex = 0
        sourceControl.selectedSegmentTintColor = AppTheme.cardBackgroundColor
        sourceControl.backgroundColor = AppTheme.softColor
        sourceControl.setTitleTextAttributes([.foregroundColor: AppTheme.titleColor,
            .font: UIFont.systemFont(ofSize: 13, weight: .semibold)], for: .normal)
        sourceControl.heightAnchor.constraint(equalToConstant: 48).isActive = true
        sourceControl.addTarget(self, action: #selector(changeInputKind), for: .valueChanged)
        sourceControl.accessibilityIdentifier = "scan.source"
        [
            makeScanHero(),
            sourceControl,
            imageSection,
            textSection,
            documentSection,
            statusLabel,
            privacyLabel
        ].forEach(contentStack.addArrangedSubview)

        updateInputMode()
        installAppBackground()
        view.addSubview(scrollView)
        configureActionDock()
        scrollView.addSubview(contentStack)
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: actionDock.topAnchor),
            contentStack.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor, constant: 8),
            contentStack.leadingAnchor.constraint(equalTo: scrollView.frameLayoutGuide.leadingAnchor, constant: 20),
            contentStack.trailingAnchor.constraint(equalTo: scrollView.frameLayoutGuide.trailingAnchor, constant: -20),
            contentStack.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor, constant: -28),
            categoryButton.heightAnchor.constraint(greaterThanOrEqualToConstant: 52)
        ])
    }

    func configureActionDock() {
        actionDock.layer.cornerRadius = 20
        actionDock.layer.cornerCurve = .continuous
        actionDock.layer.maskedCorners = [.layerMinXMinYCorner, .layerMaxXMinYCorner]
        actionDock.clipsToBounds = true
        actionDock.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(actionDock)
        imageStatusLabel.text = "Chọn một ảnh để bắt đầu"
        imageStatusLabel.font = .preferredFont(forTextStyle: .caption1)
        imageStatusLabel.adjustsFontForContentSizeCategory = true
        imageStatusLabel.textColor = AppTheme.secondaryTextColor
        imageStatusLabel.numberOfLines = 0
        imageStatusLabel.textAlignment = .center
        let stack = UIStackView(arrangedSubviews: [imageStatusLabel, analyzeButton])
        stack.axis = .vertical
        stack.spacing = 9
        stack.translatesAutoresizingMaskIntoConstraints = false
        actionDock.contentView.addSubview(stack)
        NSLayoutConstraint.activate([
            actionDock.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            actionDock.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            actionDock.bottomAnchor.constraint(equalTo: view.keyboardLayoutGuide.topAnchor),
            stack.topAnchor.constraint(equalTo: actionDock.contentView.topAnchor, constant: 12),
            stack.leadingAnchor.constraint(equalTo: actionDock.contentView.leadingAnchor, constant: 20),
            stack.trailingAnchor.constraint(equalTo: actionDock.contentView.trailingAnchor, constant: -20),
            stack.bottomAnchor.constraint(equalTo: actionDock.contentView.bottomAnchor, constant: -12)
        ])
    }

    func makeScanHero() -> UIView {
        let title = UILabel()
        title.text = "Kiểm tra trước khi tin."
        title.font = AppTheme.displayFont(size: 30, weight: .bold)
        title.accessibilityTraits = .header
        title.adjustsFontForContentSizeCategory = true
        title.textColor = AppTheme.titleColor
        title.numberOfLines = 0
        let subtitle = UILabel()
        subtitle.text = "Chọn nội dung. Nhận biết rủi ro. Biết bước tiếp theo."
        subtitle.font = .preferredFont(forTextStyle: .subheadline)
        subtitle.adjustsFontForContentSizeCategory = true
        subtitle.textColor = AppTheme.secondaryTextColor
        subtitle.numberOfLines = 0
        let stack = UIStackView(arrangedSubviews: [title, subtitle])
        stack.axis = .vertical
        stack.spacing = 10
        return stack
    }

    func configureCategoryButton() {
        var configuration = UIButton.Configuration.plain()
        configuration.title = "Mọi loại nội dung"
        configuration.image = UIImage(systemName: "chevron.up.chevron.down")
        configuration.imagePlacement = .trailing
        configuration.imagePadding = 8
        configuration.baseForegroundColor = AppTheme.titleColor
        configuration.background.backgroundColor = AppTheme.cardBackgroundColor
        configuration.background.cornerRadius = 14
        configuration.background.strokeColor = AppTheme.borderColor
        configuration.background.strokeWidth = 1
        categoryButton.configuration = configuration
        categoryButton.contentHorizontalAlignment = .fill
        categoryButton.showsMenuAsPrimaryAction = true
        categoryButton.enableSoftPressAnimation()
        categoryButton.translatesAutoresizingMaskIntoConstraints = false
    }

    func configurePreviewCard() {
        previewCard.translatesAutoresizingMaskIntoConstraints = false
        previewCard.isUserInteractionEnabled = true
        previewCard.addInteraction(UIDropInteraction(delegate: self))
        previewCard.addGestureRecognizer(
            UITapGestureRecognizer(target: self, action: #selector(didTapPhotoLibrary))
        )

        let iconView = UIImageView(image: UIImage(systemName: "photo.badge.plus"))
        iconView.tintColor = AppTheme.primaryColor
        iconView.contentMode = .center
        iconView.preferredSymbolConfiguration = .init(pointSize: 25, weight: .regular)
        iconView.backgroundColor = AppTheme.cardBackgroundColor
        iconView.layer.cornerRadius = 28
        iconView.translatesAutoresizingMaskIntoConstraints = false

        let titleLabel = UILabel()
        titleLabel.text = "Chọn ảnh cần kiểm tra"
        titleLabel.font = .preferredFont(forTextStyle: .headline)
        titleLabel.adjustsFontForContentSizeCategory = true
        titleLabel.textColor = AppTheme.titleColor
        titleLabel.numberOfLines = 0
        titleLabel.textAlignment = .center

        let subtitleLabel = UILabel()
        subtitleLabel.text = "Chạm vào đây hoặc kéo thả ảnh\nJPG · PNG · HEIC"
        subtitleLabel.numberOfLines = 0
        subtitleLabel.textAlignment = .center
        subtitleLabel.font = .preferredFont(forTextStyle: .subheadline)
        subtitleLabel.adjustsFontForContentSizeCategory = true
        subtitleLabel.textColor = AppTheme.secondaryTextColor

        previewPlaceholder.axis = .vertical
        previewPlaceholder.alignment = .center
        previewPlaceholder.spacing = 9
        [iconView, titleLabel, subtitleLabel].forEach(previewPlaceholder.addArrangedSubview)
        previewPlaceholder.translatesAutoresizingMaskIntoConstraints = false

        scanFrame.translatesAutoresizingMaskIntoConstraints = false
        previewCard.addSubviews(previewImageView, scanFrame, previewPlaceholder)
        NSLayoutConstraint.activate([
            previewImageView.topAnchor.constraint(equalTo: previewCard.topAnchor, constant: 10),
            previewImageView.leadingAnchor.constraint(equalTo: previewCard.leadingAnchor, constant: 10),
            previewImageView.trailingAnchor.constraint(equalTo: previewCard.trailingAnchor, constant: -10),
            previewImageView.bottomAnchor.constraint(equalTo: previewCard.bottomAnchor, constant: -10),
            previewImageView.heightAnchor.constraint(greaterThanOrEqualToConstant: 216),
            previewPlaceholder.topAnchor.constraint(greaterThanOrEqualTo: previewImageView.topAnchor, constant: 20),
            previewPlaceholder.bottomAnchor.constraint(lessThanOrEqualTo: previewImageView.bottomAnchor, constant: -20),
            scanFrame.topAnchor.constraint(equalTo: previewImageView.topAnchor),
            scanFrame.leadingAnchor.constraint(equalTo: previewImageView.leadingAnchor),
            scanFrame.trailingAnchor.constraint(equalTo: previewImageView.trailingAnchor),
            scanFrame.bottomAnchor.constraint(equalTo: previewImageView.bottomAnchor),
            previewPlaceholder.leadingAnchor.constraint(greaterThanOrEqualTo: previewImageView.leadingAnchor, constant: 28),
            previewPlaceholder.trailingAnchor.constraint(lessThanOrEqualTo: previewImageView.trailingAnchor, constant: -28),
            previewPlaceholder.centerXAnchor.constraint(equalTo: previewImageView.centerXAnchor),
            previewPlaceholder.centerYAnchor.constraint(equalTo: previewImageView.centerYAnchor),
            iconView.widthAnchor.constraint(equalToConstant: 56),
            iconView.heightAnchor.constraint(equalToConstant: 56)
        ])
    }

    func makeSourceButtons() -> UIView {
        let libraryButton = makeSourceButton(title: "Thư viện", imageName: "photo.on.rectangle")
        libraryButton.addTarget(self, action: #selector(didTapPhotoLibrary), for: .touchUpInside)

        let pasteButton = makeSourceButton(title: "Dán ảnh", imageName: "doc.on.clipboard")
        pasteButton.addTarget(self, action: #selector(didTapPasteImage), for: .touchUpInside)

        let cameraButton = makeSourceButton(title: "Camera", imageName: "camera.fill")
        cameraButton.addTarget(self, action: #selector(didTapCamera), for: .touchUpInside)

        let stack = UIStackView(arrangedSubviews: [libraryButton, pasteButton, cameraButton])
        stack.axis = .horizontal
        stack.distribution = .fillEqually
        stack.spacing = 12
        return stack
    }

    func makeSourceButton(title: String, imageName: String) -> UIButton {
        let button = UIButton(type: .system)
        var configuration = UIButton.Configuration.tinted()
        configuration.title = title
        configuration.image = UIImage(systemName: imageName)
        configuration.imagePadding = 8
        configuration.imagePlacement = .top
        configuration.baseForegroundColor = AppTheme.primaryColor
        configuration.baseBackgroundColor = AppTheme.primaryColor.withAlphaComponent(0.15)
        configuration.cornerStyle = .fixed
        configuration.background.cornerRadius = 14
        configuration.contentInsets = .init(top: 12, leading: 8, bottom: 12, trailing: 8)
        configuration.titleTextAttributesTransformer = UIConfigurationTextAttributesTransformer { attributes in
            var updated = attributes
            updated.font = AppTheme.font(size: 13, weight: .semibold, style: .subheadline)
            return updated
        }
        button.configuration = configuration
        button.enableSoftPressAnimation()
        button.heightAnchor.constraint(greaterThanOrEqualToConstant: 60).isActive = true
        return button
    }

    func makeFieldTitle(_ text: String) -> UILabel {
        let label = UILabel()
        label.text = text
        label.font = .preferredFont(forTextStyle: .subheadline)
        label.adjustsFontForContentSizeCategory = true
        label.numberOfLines = 0
        label.textColor = AppTheme.titleColor
        return label
    }
}

// MARK: - Categories

private extension ScanViewController {

    func loadCategories() {
        categoryTask?.cancel()
        categoryTask = Task { [weak self] in
            guard let self else { return }

            do {
                categories = try await scanService.fetchCategories()
                guard !Task.isCancelled else { return }
                updateCategoryMenu()
            } catch {
                guard !Task.isCancelled else { return }
                statusLabel.text = "Không tải được danh mục; AI vẫn có thể tự động nhận diện."
                statusLabel.isHidden = false
            }
        }
    }

    func updateCategoryMenu() {
        let automaticAction = UIAction(
            title: "Mọi loại nội dung",
            image: UIImage(systemName: "wand.and.stars"),
            state: selectedCategory == nil ? .on : .off
        ) { [weak self] _ in
            self?.selectCategory(nil)
        }

        let categoryActions = categories.map { category in
            UIAction(
                title: category.displayName,
                state: selectedCategory?.id == category.id ? .on : .off
            ) { [weak self] _ in
                self?.selectCategory(category)
            }
        }
        categoryButton.menu = UIMenu(children: [automaticAction] + categoryActions)
    }

    func selectCategory(_ category: ScamCategory?) {
        selectedCategory = category
        categoryButton.configuration?.title = category?.displayName ?? "Mọi loại nội dung"
        updateCategoryMenu()
    }
}

// MARK: - Actions

private extension ScanViewController {

    func configureActions() {
        analyzeButton.addTarget(self, action: #selector(didTapAnalyze), for: .touchUpInside)
        NotificationCenter.default.addObserver(self, selector: #selector(revealEditor), name: UIResponder.keyboardDidShowNotification, object: nil)
    }

    @objc func didTapPhotoLibrary() {
        guard !isAnalyzing, presentedViewController == nil else { return }
        AccessConsent.confirm(on: self, title: "Chọn ảnh để kiểm tra?", message: "App chỉ đọc ảnh bạn chọn, không xem toàn bộ thư viện. Ảnh chỉ được gửi đến máy chủ khi bạn nhấn Phân tích rủi ro.") { [weak self] in
            self?.presentPhotoPicker()
        }
    }

    func presentPhotoPicker() {
        var configuration = PHPickerConfiguration(photoLibrary: .shared())
        configuration.filter = .images
        configuration.selectionLimit = 1

        let picker = PHPickerViewController(configuration: configuration)
        picker.delegate = self
        present(picker, animated: true)
    }

    @objc func didTapCamera() {
        guard !isAnalyzing, presentedViewController == nil else { return }
        guard UIImagePickerController.isSourceTypeAvailable(.camera) else {
            showErrorAlert(message: "Camera không khả dụng trên thiết bị này. Simulator nên dùng Thư viện ảnh.")
            return
        }

        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized:
            presentCamera()
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .video) { [weak self] granted in
                DispatchQueue.main.async {
                    if granted { self?.presentCamera() } else { self?.showCameraPermissionAlert() }
                }
            }
        default:
            showCameraPermissionAlert()
        }
    }

    func showCameraPermissionAlert() {
        guard presentedViewController == nil, view.window != nil else { return }
        let alert = UIAlertController(title: "Cho phép sử dụng camera", message: "Bạn có thể bật quyền Camera trong Cài đặt hoặc chọn ảnh từ thư viện.", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "Để sau", style: .cancel))
        alert.addAction(UIAlertAction(title: "Mở Cài đặt", style: .default) { _ in
            guard let url = URL(string: UIApplication.openSettingsURLString) else { return }
            UIApplication.shared.open(url)
        })
        present(alert, animated: true)
    }

    func presentCamera() {
        guard !isAnalyzing, presentedViewController == nil, view.window != nil else { return }
        let picker = UIImagePickerController()
        picker.sourceType = .camera
        picker.cameraCaptureMode = .photo
        picker.delegate = self
        present(picker, animated: true)
    }

    @objc func didTapPasteImage() {
        guard !isAnalyzing else { return }
        guard let image = UIPasteboard.general.image else {
            showErrorAlert(message: "Clipboard chưa có ảnh. Hãy copy một ảnh rồi bấm Dán ảnh.")
            return
        }
        setSelectedImage(image)
    }

    @objc func didTapAnalyze() {
        guard !isAnalyzing else { return }
        imageLoadID = UUID()
        view.endEditing(true)
        guard isInputReady else { return }
        let kind = inputKind
        let image = selectedImage
        let imageData = kind == .image ? image?.preparingForUpload().jpegData(compressionQuality: 0.84) : nil
        if kind == .image && imageData == nil {
            showErrorAlert(message: "Không thể đọc ảnh đã chọn. Vui lòng chọn lại.")
            return
        }
        let input = contentEditor.text.trimmingCharacters(in: .whitespacesAndNewlines)
        if kind == .url {
            let candidate = input.contains("://") ? input : "https://" + input
            guard let url = URLComponents(string: candidate),
                  ["https", "http"].contains(url.scheme ?? ""),
                  let host = url.host, host.contains("."), !input.contains(where: { $0.isWhitespace }) else {
                showErrorAlert(message: "Nhập một liên kết hợp lệ, ví dụ https://example.com. Liên kết chỉ được phân tích, không tự mở.")
                return
            }
        }
        setLoading(true)
        scanTask?.cancel()
        scanTask = Task { [weak self] in
            guard let self else { return }

            do {
                let result: ScanResult
                switch kind {
                case .image:
                    result = try await scanService.analyze(imageData: imageData!, categoryID: selectedCategory?.id)
                case .text, .url:
                    result = try await scanService.analyze(text: input, kind: kind)
                case .pdf:
                    guard let documentData, let documentName else { setLoading(false); return }
                    result = try await scanService.analyze(document: documentData, filename: documentName)
                }
                guard !Task.isCancelled else { return }

                setLoading(false)
                var saveError: Error?
                do {
                    try HistoryService().save(result: result, imageData: imageData)
                    NotificationCenter.default.post(name: .scanDidComplete, object: nil)
                } catch {
                    saveError = error
                }
                let resultViewController = ScanResultViewController(
                    result: result,
                    image: kind == .image ? image : nil
                )
                navigationController?.pushViewController(resultViewController, animated: true)
                if saveError != nil {
                    // Kết quả phân tích vẫn hiển thị kể cả khi bộ nhớ thiết bị không ghi được.
                    resultViewController.navigationItem.prompt = "Không lưu được lịch sử trên thiết bị"
                }
            } catch {
                guard !Task.isCancelled else { return }
                setLoading(false)
                showErrorAlert(message: error.localizedDescription)
            }
        }
    }

    func setSelectedImage(_ image: UIImage) {
        guard !isAnalyzing else { return }
        imageLoadID = UUID()
        selectedImage = image
        previewImageView.image = image
        previewPlaceholder.isHidden = true
        previewImageView.animatePop()
        analyzeButton.isEnabled = true
        analyzeButton.alpha = 1
        statusLabel.isHidden = true
        imageStatusLabel.text = "Ảnh đã sẵn sàng · Chạm ảnh để thay đổi"
        navigationItem.rightBarButtonItem = UIBarButtonItem(image: UIImage(systemName: "trash"), style: .plain, target: self, action: #selector(clearSelectedImage))
        navigationItem.rightBarButtonItem?.accessibilityLabel = "Bỏ ảnh đã chọn"
        previewCard.layer.borderColor = AppTheme.primaryColor.withAlphaComponent(0.5).cgColor
        previewCard.layer.borderWidth = 1.5
        UIImpactFeedbackGenerator(style: .soft).impactOccurred()
    }

    func loadImage(from provider: NSItemProvider) {
        guard !isAnalyzing else { return }
        let requestID = UUID()
        imageLoadID = requestID
        guard provider.canLoadObject(ofClass: UIImage.self) else {
            showErrorAlert(message: "Nội dung được thả không phải là ảnh hỗ trợ.")
            return
        }
        imageStatusLabel.text = "Đang mở ảnh…"

        provider.loadObject(ofClass: UIImage.self) { [weak self] object, error in
            DispatchQueue.main.async {
                guard let self, self.imageLoadID == requestID, !self.isAnalyzing else { return }
                if let image = object as? UIImage {
                    self.setSelectedImage(image)
                } else {
                    self.imageStatusLabel.text = self.selectedImage == nil ? "Chọn một ảnh để bắt đầu" : "Ảnh trước vẫn được giữ lại"
                    self.showErrorAlert(message: error?.localizedDescription ?? "Không đọc được ảnh. Vui lòng chọn lại.")
                }
            }
        }
    }

    func setLoading(_ isLoading: Bool) {
        isAnalyzing = isLoading
        analyzeButton.setPrimaryTitle("Phân tích rủi ro")
        analyzeButton.isLoading = isLoading
        analyzeButton.isEnabled = !isLoading && isInputReady
        analyzeButton.alpha = isLoading || isInputReady ? 1 : 0.55
        imageStatusLabel.text = isLoading ? "Đang phân tích · Bạn có thể hủy bất cứ lúc nào" : "Sẵn sàng kiểm tra · Kết quả lưu trên thiết bị"
        navigationItem.rightBarButtonItem = isLoading
            ? UIBarButtonItem(title: "Hủy", style: .plain, target: self, action: #selector(cancelAnalysis))
            : UIBarButtonItem(image: UIImage(systemName: "trash"), style: .plain, target: self, action: #selector(clearSelectedImage))
        navigationItem.rightBarButtonItem?.accessibilityLabel = isLoading ? "Hủy phân tích" : "Bỏ ảnh đã chọn"
        contentStack.isUserInteractionEnabled = !isLoading
        categoryButton.isEnabled = !isLoading
        statusLabel.text = isLoading
            ? "Đang đối chiếu dấu hiệu và tổng hợp kết quả. Vui lòng chờ…"
            : nil
        statusLabel.isHidden = !isLoading
        updateScanLoadingAnimation(isLoading: isLoading)

        if isLoading {
            statusLabel.animateFadeAndSlideIn(distance: 8)
            UIImpactFeedbackGenerator(style: .soft).impactOccurred()
        }
    }

    @objc func cancelAnalysis() {
        scanTask?.cancel()
        scanTask = nil
        setLoading(false)
        imageStatusLabel.text = "Đã hủy · Nội dung được giữ lại để thử lại"
    }

    @objc func clearSelectedImage() {
        guard !isAnalyzing else { return }
        imageLoadID = UUID()
        switch inputKind {
        case .image:
            selectedImage = nil
            previewImageView.image = nil
            previewPlaceholder.isHidden = false
        case .text:
            contentEditor.text = ""
            textDraft = ""
        case .url:
            contentEditor.text = ""
            urlDraft = ""
        case .pdf:
            documentData = nil
            documentName = nil
            documentLabel.text = "Chọn tài liệu PDF"
        }
        analyzeButton.isEnabled = false
        analyzeButton.alpha = 0.55
        imageStatusLabel.text = "Thêm nội dung để bắt đầu"
        characterCount.text = "0 ký tự"
        statusLabel.isHidden = true
        navigationItem.rightBarButtonItem = nil
        previewCard.layer.borderColor = AppTheme.borderColor.cgColor
    }

    func updateScanLoadingAnimation(isLoading: Bool) {
        scanFrame.isScanning = isLoading
        previewCard.layer.borderColor = isLoading
            ? AppTheme.primaryColor.cgColor : AppTheme.borderColor.cgColor
    }

    func animateEntranceIfNeeded() {
        guard !hasAnimatedEntrance else { return }
        hasAnimatedEntrance = true

        for (index, element) in contentStack.arrangedSubviews.enumerated() {
            element.animateFadeAndSlideIn(delay: min(Double(index) * 0.04, 0.25), distance: 14)
        }
    }
}

// MARK: - Photo Picker

extension ScanViewController: PHPickerViewControllerDelegate {

    func picker(_ picker: PHPickerViewController, didFinishPicking results: [PHPickerResult]) {
        picker.dismiss(animated: true)
        guard let provider = results.first?.itemProvider,
              provider.canLoadObject(ofClass: UIImage.self) else { return }

        loadImage(from: provider)
    }
}

// MARK: - Drag and Drop

extension ScanViewController: UIDropInteractionDelegate {

    func dropInteraction(
        _ interaction: UIDropInteraction,
        canHandle session: UIDropSession
    ) -> Bool {
        !isAnalyzing && session.hasItemsConforming(toTypeIdentifiers: [UTType.image.identifier])
    }

    func dropInteraction(
        _ interaction: UIDropInteraction,
        sessionDidUpdate session: UIDropSession
    ) -> UIDropProposal {
        UIDropProposal(operation: .copy)
    }

    func dropInteraction(_ interaction: UIDropInteraction, sessionDidEnter session: UIDropSession) {
        UIView.animate(withDuration: 0.18, delay: 0, options: [.curveEaseOut, .allowUserInteraction]) {
            self.previewCard.transform = CGAffineTransform(scaleX: 1.008, y: 1.008)
            self.previewCard.layer.borderColor = AppTheme.primaryColor.cgColor
            self.previewCard.layer.borderWidth = 2
        }
    }

    func dropInteraction(_ interaction: UIDropInteraction, sessionDidExit session: UIDropSession) {
        restorePreviewCardAfterDrop()
    }

    func dropInteraction(_ interaction: UIDropInteraction, performDrop session: UIDropSession) {
        restorePreviewCardAfterDrop()
        guard let provider = session.items.first?.itemProvider else { return }
        loadImage(from: provider)
    }

    private func restorePreviewCardAfterDrop() {
        UIView.animate(withDuration: 0.18, delay: 0, options: [.curveEaseOut, .allowUserInteraction]) {
            self.previewCard.transform = .identity
            self.previewCard.layer.borderColor = AppTheme.borderColor.cgColor
            self.previewCard.layer.borderWidth = 1
        }
    }
}

// MARK: - Camera Picker

extension ScanViewController: UIImagePickerControllerDelegate, UINavigationControllerDelegate {

    func imagePickerController(
        _ picker: UIImagePickerController,
        didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]
    ) {
        picker.dismiss(animated: true)
        guard let image = info[.originalImage] as? UIImage else { return }
        setSelectedImage(image)
    }

    func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
        picker.dismiss(animated: true)
    }
}


// MARK: - Multisource input
extension ScanViewController: UITextViewDelegate, UIDocumentPickerDelegate {
    func selectInput(_ kind: ScanInputKind) {
        loadViewIfNeeded()
        guard !isAnalyzing else { return }
        sourceControl.selectedSegmentIndex = ScanInputKind.allCases.firstIndex(of: kind) ?? 0
        changeInputKind()
    }

    private var isInputReady: Bool {
        switch inputKind {
        case .image: return selectedImage != nil
        case .pdf: return documentData != nil
        case .text, .url:
            let count = contentEditor.text.trimmingCharacters(in: .whitespacesAndNewlines).count
            return count > (inputKind == .url ? 2 : 0) && count <= (inputKind == .url ? 4096 : 20000)
        }
    }

    private func configureContentInputs() {
        textSection.axis = .vertical
        textSection.spacing = 12
        contentEditor.font = .preferredFont(forTextStyle: .body)
        contentEditor.adjustsFontForContentSizeCategory = true
        contentEditor.textColor = AppTheme.titleColor
        contentEditor.backgroundColor = AppTheme.cardBackgroundColor
        contentEditor.layer.cornerRadius = 16
        contentEditor.layer.cornerCurve = .continuous
        contentEditor.textContainerInset = UIEdgeInsets(top: 16, left: 12, bottom: 16, right: 12)
        editorHeightConstraint = contentEditor.heightAnchor.constraint(equalToConstant: 180)
        editorHeightConstraint?.isActive = true
        contentEditor.delegate = self
        contentEditor.accessibilityIdentifier = "scan.content"
        inputHint.adjustsFontForContentSizeCategory = true
        inputHint.font = .preferredFont(forTextStyle: .subheadline)
        inputHint.textColor = AppTheme.secondaryTextColor
        inputHint.numberOfLines = 0
        characterCount.font = .preferredFont(forTextStyle: .caption1)
        characterCount.textColor = AppTheme.secondaryTextColor
        characterCount.textAlignment = .right
        let paste = makeSourceButton(title: "Dán nội dung", imageName: "doc.on.clipboard")
        paste.addAction(UIAction { [weak self] _ in
            guard let self, !self.isAnalyzing else { return }
            if let text = UIPasteboard.general.string {
                self.contentEditor.text = text
                self.textViewDidChange(self.contentEditor)
            } else { self.showErrorAlert(message: "Clipboard chưa có văn bản để dán.") }
        }, for: .touchUpInside)
        [inputHint, contentEditor, characterCount, paste].forEach(textSection.addArrangedSubview)
        let toolbar = UIToolbar()
        toolbar.sizeToFit()
        toolbar.items = [UIBarButtonItem(systemItem: .flexibleSpace),
            UIBarButtonItem(title: "Xong", primaryAction: UIAction { [weak self] _ in self?.view.endEditing(true) })]
        contentEditor.inputAccessoryView = toolbar

        documentSection.axis = .vertical
        documentSection.spacing = 14
        let card = InformationCardView(title: "Kiểm tra tài liệu", systemImageName: "doc.text.viewfinder")
        card.configure(text: "Chọn PDF từ ứng dụng Tệp. Hệ thống đọc chữ và mã QR trong tối đa 10 trang đầu, dung lượng tối đa 15 MB.")
        documentLabel.text = "Chưa chọn tài liệu"
        documentLabel.font = .preferredFont(forTextStyle: .headline)
        documentLabel.textColor = AppTheme.titleColor
        documentLabel.numberOfLines = 0
        let choose = makeSourceButton(title: "Chọn PDF từ Tệp", imageName: "folder")
        choose.addAction(UIAction { [weak self] _ in
            guard let self, !self.isAnalyzing else { return }
            AccessConsent.confirm(on: self, title: "Chọn tài liệu để kiểm tra?", message: "App chỉ đọc tệp PDF bạn chọn. Tài liệu chỉ được gửi đến máy chủ khi bạn nhấn Phân tích rủi ro.") { [weak self] in
                guard let self else { return }
                let picker = UIDocumentPickerViewController(forOpeningContentTypes: [.pdf], asCopy: true)
                picker.delegate = self
                self.present(picker, animated: true)
            }
        }, for: .touchUpInside)
        [card, documentLabel, choose].forEach(documentSection.addArrangedSubview)
    }

    @objc private func changeInputKind() {
        if inputKind == .text { textDraft = contentEditor.text }
        if inputKind == .url { urlDraft = contentEditor.text }
        imageLoadID = UUID()
        inputKind = ScanInputKind.allCases[sourceControl.selectedSegmentIndex]
        view.endEditing(true)
        updateInputMode()
        UISelectionFeedbackGenerator().selectionChanged()
    }

    private func updateInputMode() {
        imageSection.isHidden = inputKind != .image
        textSection.isHidden = inputKind != .text && inputKind != .url
        documentSection.isHidden = inputKind != .pdf
        contentEditor.text = inputKind == .url ? urlDraft : textDraft
        contentEditor.keyboardType = inputKind == .url ? .URL : .default
        contentEditor.autocapitalizationType = inputKind == .url ? .none : .sentences
        contentEditor.autocorrectionType = inputKind == .url ? .no : .default
        contentEditor.accessibilityLabel = inputKind == .url ? "Liên kết cần kiểm tra" : "Tin nhắn cần kiểm tra"
        inputHint.text = inputKind == .url
            ? "Dán liên kết đáng ngờ để kiểm tra. App không tự mở liên kết này."
            : "Dán tin nhắn, email hoặc nội dung bạn muốn xác minh."
        statusLabel.isHidden = true
        updateReadyState()
    }

    func textViewDidChange(_ textView: UITextView) {
        updateReadyState()
        revealEditor()
    }
    func textViewDidBeginEditing(_ textView: UITextView) {
        contentStack.arrangedSubviews.first?.isHidden = true
        sourceControl.isHidden = true
        inputHint.isHidden = true
        view.layoutIfNeeded()
    }

    @objc private func revealEditor() {
        guard contentEditor.isFirstResponder else { return }
        view.layoutIfNeeded()
        let available = scrollView.bounds.height - scrollView.adjustedContentInset.top - scrollView.adjustedContentInset.bottom
        editorHeightConstraint?.constant = min(180, max(80, available - 24))
        view.layoutIfNeeded()
        let rect = contentEditor.convert(contentEditor.bounds, to: scrollView).insetBy(dx: 0, dy: -8)
        scrollView.scrollRectToVisible(rect, animated: false)
    }

    func textViewDidEndEditing(_ textView: UITextView) {
        editorHeightConstraint?.constant = 180
        sourceControl.isHidden = false
        inputHint.isHidden = false
        contentStack.arrangedSubviews.first?.isHidden = false
    }

    private func updateReadyState() {
        analyzeButton.isEnabled = isInputReady && !isAnalyzing
        analyzeButton.alpha = isInputReady ? 1 : 0.55
        let limit = inputKind == .url ? 4096 : 20000
        characterCount.text = "\(contentEditor.text.count) / \(limit) ký tự"
        characterCount.textColor = contentEditor.text.count > limit ? AppTheme.dangerousColor : AppTheme.secondaryTextColor
        imageStatusLabel.text = isInputReady ? "Sẵn sàng phân tích · \(inputKind.title)" : "Thêm \(inputKind.title.lowercased()) để bắt đầu"
        navigationItem.rightBarButtonItem = isInputReady ? UIBarButtonItem(image: UIImage(systemName: "trash"), style: .plain, target: self, action: #selector(clearSelectedImage)) : nil
        navigationItem.rightBarButtonItem?.accessibilityLabel = "Xóa nội dung đang nhập"
    }

    func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
        guard !isAnalyzing, let url = urls.first else { return }
        let accessed = url.startAccessingSecurityScopedResource()
        defer { if accessed { url.stopAccessingSecurityScopedResource() } }
        do {
            let size = try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0
            guard size > 0, size <= 15 * 1024 * 1024 else {
                showErrorAlert(message: "Hãy chọn PDF có nội dung, tối đa 15 MB."); return
            }
            let data = try Data(contentsOf: url)
            guard data.count <= 15 * 1024 * 1024 else {
                showErrorAlert(message: "PDF vượt quá 15 MB."); return
            }
            documentData = data
            documentName = url.lastPathComponent
            documentLabel.text = "\(url.lastPathComponent)\n\(ByteCountFormatter.string(fromByteCount: Int64(data.count), countStyle: .file))"
            updateReadyState()
        } catch { showErrorAlert(message: "Không mở được PDF. Hãy tải tài liệu về thiết bị rồi thử lại.") }
    }
}
