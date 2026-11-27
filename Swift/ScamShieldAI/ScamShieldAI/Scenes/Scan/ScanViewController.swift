import PhotosUI
import AVFoundation
import UIKit
import UniformTypeIdentifiers

final class ScanViewController: UIViewController {

    // MARK: - Dependencies

    private let scanService: ScanService

    // MARK: - Properties

    private var inputKind: ScanInputKind = .image
    private let sourceControl = UISegmentedControl(items: ScanInputKind.allCases.map { $0 == .batch ? L10n.choose("Loạt URL", "Batch") : $0.title })
    private let imageSection = UIStackView()
    private let textSection = UIStackView()
    private let documentSection = UIStackView()
    private let contentEditor = UITextView()
    private let editorPlaceholder = UILabel()
    private var editorHeightConstraint: NSLayoutConstraint?
    private let inputHint = UILabel()
    private let characterCount = UILabel()
    private let documentLabel = UILabel()
    private var textDraft = ""
    private var urlDraft = ""
    private var batchDraft = ""
    private var documentData: Data?
    private var documentName: String?
    private var categories: [ScamCategory] = []
    private var selectedCategory: ScamCategory?
    private var selectedImage: UIImage?
    private var healthTask: Task<Void, Never>?
    private let backendStatus = UILabel()
    private var categoryTask: Task<Void, Never>?
    private var scanTask: Task<Void, Never>?
    private var hasAnimatedEntrance = false
    private var isAnalyzing = false
    private var imageLoadID = UUID()
    private let sourcePicker = UIStackView()
    private var sourcePickerButtons: [UIButton] = []
    private let privacyLabel = UILabel()

    // MARK: - UI Components

    private let scrollView: UIScrollView = {
        let view = UIScrollView()
        view.keyboardDismissMode = .interactive
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()

    private let contentStack = UIStackView()
    private let previewCard = CardView()
    private let scanFrame = ScanFrameView()
    private var previewRatio: NSLayoutConstraint?
    private var previewMaximumHeight: NSLayoutConstraint?
    private var placeholderConstraints: [NSLayoutConstraint] = []

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
        button.setPrimaryTitle(L10n.choose("Phân tích ngay", "Analyze now"))
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
        healthTask?.cancel()
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

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        navigationController?.setNavigationBarHidden(true, animated: animated)
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        if let navigationController, navigationController.topViewController !== self {
            navigationController.setNavigationBarHidden(false, animated: animated)
        }
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        animateEntranceIfNeeded()
        healthTask?.cancel()
        healthTask = Task { [weak self] in
            guard let self else { return }
            let ready = (try? await scanService.backendIsReady()) == true
            guard !Task.isCancelled else { return }
            backendStatus.isHidden = ready
            backendStatus.text = L10n.choose("Máy chủ chưa sẵn sàng. Lượt phân tích đầu có thể lâu hơn.", "Server not ready. The first scan may take longer.")
        }
    }
}

// MARK: - Setup UI

private extension ScanViewController {

    func setupUI() {
        navigationItem.largeTitleDisplayMode = .never
        scrollView.contentInset.bottom = 16
        scrollView.showsVerticalScrollIndicator = false
        view.backgroundColor = AppTheme.pageBackgroundColor
        navigationItem.backButtonDisplayMode = .minimal

        contentStack.axis = .vertical
        contentStack.spacing = 12
        contentStack.translatesAutoresizingMaskIntoConstraints = false

        configurePreviewCard()
        let sourceButtons = makeSourceButtons()

        privacyLabel.font = AppTheme.font(size: 11)
        privacyLabel.adjustsFontForContentSizeCategory = true
        privacyLabel.textColor = AppTheme.secondaryTextColor
        privacyLabel.numberOfLines = 0
        privacyLabel.textAlignment = .center
        imageSection.axis = .vertical
        imageSection.spacing = 10
        [previewCard, sourceButtons].forEach(imageSection.addArrangedSubview)
        configureContentInputs()
        sourceControl.selectedSegmentIndex = 0
        sourceControl.accessibilityLabel = L10n.choose("Loại nội dung", "Content type")
        sourceControl.accessibilityIdentifier = "scan.source"
        backendStatus.font = .preferredFont(forTextStyle: .footnote)
        backendStatus.textColor = AppTheme.secondaryTextColor
        backendStatus.numberOfLines = 0
        backendStatus.isHidden = true
        let intro = UIStackView(arrangedSubviews: [
            makeText("SCAMSHIELD · \(L10n.choose("AN TOÀN SỐ", "DIGITAL SAFETY"))", size: 10, color: AppTheme.primaryColor, weight: .bold),
            makeText(L10n.choose("Kiểm tra lừa đảo", "Scam check"), size: 27, color: AppTheme.titleColor, weight: .bold),
            makeText(L10n.choose("Chọn nội dung, chúng tôi sẽ giúp bạn nhận diện rủi ro.", "Choose content and we will help you spot risks."), size: 13, color: AppTheme.secondaryTextColor)
        ])
        intro.axis = .vertical
        intro.spacing = 5

        let stepOne = CardView()
        let stepOneHeading = UIStackView(arrangedSubviews: [
            makeText(L10n.choose("BẮT ĐẦU KIỂM TRA", "START CHECKING"), size: 10, color: AppTheme.primaryColor, weight: .bold),
            makeText(L10n.choose("Bạn muốn kiểm tra gì?", "What would you like to check?"), size: 17, color: AppTheme.titleColor, weight: .bold)
        ])
        stepOneHeading.axis = .vertical
        stepOneHeading.spacing = 5
        makeSourcePicker()
        let formStack = UIStackView(arrangedSubviews: [stepOneHeading, sourcePicker, imageSection, textSection,
                                                       documentSection, statusLabel, backendStatus])
        formStack.axis = .vertical
        formStack.spacing = 16
        pin(formStack, in: stepOne, padding: 18)
        analyzeButton.layer.cornerRadius = 16
        analyzeButton.accessibilityIdentifier = "scan.analyze"
        [intro, stepOne, analyzeButton, privacyLabel].forEach(contentStack.addArrangedSubview)
        contentStack.setCustomSpacing(20, after: intro)
        contentStack.setCustomSpacing(16, after: stepOne)
        contentStack.setCustomSpacing(4, after: analyzeButton)

        updateInputMode()
        view.addSubview(scrollView)
        scrollView.addSubview(contentStack)
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.keyboardLayoutGuide.topAnchor),
            contentStack.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor, constant: 12),
            contentStack.widthAnchor.constraint(equalTo: scrollView.frameLayoutGuide.widthAnchor, constant: -2 * 20),
            contentStack.leadingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.leadingAnchor, constant: 20),
            contentStack.trailingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.trailingAnchor, constant: -20),
            contentStack.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor, constant: -24)
        ])
    }

    func makeText(_ value: String, size: CGFloat, color: UIColor, weight: UIFont.Weight = .regular) -> UILabel {
        let label = UILabel()
        label.text = value
        label.font = AppTheme.font(size: size, weight: weight)
        label.adjustsFontForContentSizeCategory = true
        label.numberOfLines = 0
        label.textColor = color
        return label
    }

    func pin(_ content: UIView, in card: UIView, padding: CGFloat) {
        content.translatesAutoresizingMaskIntoConstraints = false
        card.addSubview(content)
        NSLayoutConstraint.activate([
            content.topAnchor.constraint(equalTo: card.topAnchor, constant: padding),
            content.leadingAnchor.constraint(equalTo: card.leadingAnchor, constant: padding),
            content.trailingAnchor.constraint(equalTo: card.trailingAnchor, constant: -padding),
            content.bottomAnchor.constraint(equalTo: card.bottomAnchor, constant: -padding)
        ])
    }

    func makeSourcePicker() {
        sourcePicker.axis = .vertical
        sourcePicker.spacing = 6
        sourcePicker.backgroundColor = AppTheme.fieldBackgroundColor
        sourcePicker.layer.cornerRadius = 16
        sourcePicker.layer.borderWidth = 1
        sourcePicker.layer.borderColor = AppTheme.borderColor.cgColor
        sourcePicker.isLayoutMarginsRelativeArrangement = true
        sourcePicker.layoutMargins = UIEdgeInsets(top: 5, left: 5, bottom: 5, right: 5)
        let sources: [(String, String)] = [
            (L10n.choose("Ảnh & QR", "Image & QR"), "viewfinder"),
            (L10n.choose("Tin nhắn", "Message"), "textformat"),
            (L10n.choose("Đường link", "Link"), "link"),
            (L10n.choose("Tài liệu", "Document"), "doc.text"),
            (L10n.choose("Hàng loạt", "Batch"), "list.bullet")
        ]
        for (index, source) in sources.enumerated() {
            let button = UIButton(type: .system)
            var configuration = UIButton.Configuration.plain()
            configuration.title = source.0
            configuration.image = UIImage(systemName: source.1)
            configuration.imagePlacement = .top
            configuration.imagePadding = 3
            configuration.contentInsets = .init(top: 7, leading: 2, bottom: 7, trailing: 2)
            configuration.baseForegroundColor = AppTheme.primaryColor
            configuration.titleTextAttributesTransformer = UIConfigurationTextAttributesTransformer { attributes in
                var updated = attributes
                updated.font = AppTheme.font(size: 11, weight: .semibold)
                return updated
            }
            button.configuration = configuration
            button.layer.cornerRadius = 12
            button.layer.borderWidth = 1
            button.accessibilityIdentifier = "scan.source.\(ScanInputKind.allCases[index].rawValue)"
            button.addAction(UIAction { [weak self] _ in
                guard let self else { return }
                sourceControl.selectedSegmentIndex = index
                changeInputKind()
            }, for: .touchUpInside)
            button.heightAnchor.constraint(greaterThanOrEqualToConstant: 52).isActive = true
            sourcePickerButtons.append(button)
        }
        for range in [0..<3, 3..<5] {
            let cells: [UIView] = range.map { sourcePickerButtons[$0] }
            let row = UIStackView(arrangedSubviews: cells)
            row.axis = .horizontal
            row.spacing = 6
            row.distribution = .fillEqually
            sourcePicker.addArrangedSubview(row)
        }
        updateSourceSelection()
    }

    func updateSourceSelection() {
        for (index, button) in sourcePickerButtons.enumerated() {
            let selected = index == sourceControl.selectedSegmentIndex
            button.backgroundColor = selected ? AppTheme.softColor : .clear
            button.layer.borderColor = (selected ? AppTheme.primaryColor : UIColor.clear).cgColor
            button.accessibilityTraits = selected ? [.button, .selected] : [.button]
        }
    }

    func configurePreviewCard() {
        previewCard.translatesAutoresizingMaskIntoConstraints = false
        previewCard.backgroundColor = .clear
        previewCard.layer.borderWidth = 0
        previewCard.layer.shadowOpacity = 0
        previewCard.isUserInteractionEnabled = true
        previewCard.addInteraction(UIDropInteraction(delegate: self))
        previewCard.addGestureRecognizer(
            UITapGestureRecognizer(target: self, action: #selector(didTapPhotoLibrary))
        )

        let iconView = UIImageView(image: UIImage(systemName: "photo.badge.plus"))
        iconView.translatesAutoresizingMaskIntoConstraints = false
        iconView.contentMode = .scaleAspectFit
        iconView.tintColor = AppTheme.primaryColor
        iconView.backgroundColor = AppTheme.cardBackgroundColor
        iconView.layer.cornerRadius = 24
        iconView.clipsToBounds = true
        previewImageView.backgroundColor = AppTheme.softColor.withAlphaComponent(0.65)
        previewImageView.layer.borderColor = AppTheme.primaryColor.withAlphaComponent(0.2).cgColor
        previewImageView.layer.borderWidth = 1

        let titleLabel = UILabel()
        titleLabel.text = L10n.choose("Chọn ảnh để kiểm tra", "Choose an image to check")
        titleLabel.font = AppTheme.font(size: 15, weight: .bold)
        titleLabel.adjustsFontForContentSizeCategory = true
        titleLabel.textColor = AppTheme.titleColor
        titleLabel.numberOfLines = 0
        titleLabel.textAlignment = .center

        let formatLabel = makeText(L10n.choose("Có thể dán ảnh hoặc kéo thả · Tự đọc mã QR", "Paste or drop an image · QR codes detected automatically"),
                                   size: 11, color: AppTheme.secondaryTextColor)
        formatLabel.textAlignment = .center
        previewPlaceholder.axis = .vertical
        previewPlaceholder.alignment = .center
        previewPlaceholder.spacing = 8
        [iconView, titleLabel, formatLabel].forEach(previewPlaceholder.addArrangedSubview)
        previewPlaceholder.translatesAutoresizingMaskIntoConstraints = false

        scanFrame.translatesAutoresizingMaskIntoConstraints = false
        scanFrame.isHidden = true
        previewCard.addSubviews(previewImageView, scanFrame, previewPlaceholder)
        placeholderConstraints = [
            previewPlaceholder.leadingAnchor.constraint(greaterThanOrEqualTo: previewImageView.leadingAnchor, constant: 28),
            previewPlaceholder.trailingAnchor.constraint(lessThanOrEqualTo: previewImageView.trailingAnchor, constant: -28),
            previewImageView.heightAnchor.constraint(greaterThanOrEqualToConstant: 138),
            previewPlaceholder.topAnchor.constraint(greaterThanOrEqualTo: previewImageView.topAnchor, constant: 20),
            previewPlaceholder.bottomAnchor.constraint(lessThanOrEqualTo: previewImageView.bottomAnchor, constant: -20)
        ]
        let preferredWidth = previewImageView.widthAnchor.constraint(equalTo: previewCard.widthAnchor)
        preferredWidth.priority = .defaultHigh
        preferredWidth.isActive = true
        previewMaximumHeight = previewImageView.heightAnchor.constraint(lessThanOrEqualToConstant: 360)
        NSLayoutConstraint.activate(placeholderConstraints)
        NSLayoutConstraint.activate([
            previewImageView.topAnchor.constraint(equalTo: previewCard.topAnchor, constant: 0),
            previewImageView.leadingAnchor.constraint(greaterThanOrEqualTo: previewCard.leadingAnchor),
            previewImageView.trailingAnchor.constraint(lessThanOrEqualTo: previewCard.trailingAnchor),
            previewImageView.bottomAnchor.constraint(equalTo: previewCard.bottomAnchor, constant: 0),
            previewImageView.centerXAnchor.constraint(equalTo: previewCard.centerXAnchor),
            scanFrame.topAnchor.constraint(equalTo: previewImageView.topAnchor),
            scanFrame.leadingAnchor.constraint(equalTo: previewImageView.leadingAnchor),
            scanFrame.trailingAnchor.constraint(equalTo: previewImageView.trailingAnchor),
            scanFrame.bottomAnchor.constraint(equalTo: previewImageView.bottomAnchor),
            previewPlaceholder.centerXAnchor.constraint(equalTo: previewImageView.centerXAnchor),
            previewPlaceholder.centerYAnchor.constraint(equalTo: previewImageView.centerYAnchor),
            iconView.widthAnchor.constraint(equalToConstant: 48),
            iconView.heightAnchor.constraint(equalTo: iconView.widthAnchor)
        ])
    }

    func makeSourceButtons() -> UIView {
        let libraryButton = makeImageActionButton(title: L10n.choose("Thư viện", "Library"), imageName: "photo.on.rectangle")
        libraryButton.accessibilityIdentifier = "scan.image.library"
        libraryButton.addTarget(self, action: #selector(didTapPhotoLibrary), for: .touchUpInside)
        let pasteButton = makeImageActionButton(title: L10n.choose("Dán ảnh", "Paste image"), imageName: "doc.on.clipboard")
        pasteButton.accessibilityIdentifier = "scan.image.paste"
        pasteButton.addTarget(self, action: #selector(didTapPasteImage), for: .touchUpInside)
        let cameraButton = makeImageActionButton(title: L10n.choose("Camera", "Camera"), imageName: "camera")
        cameraButton.accessibilityIdentifier = "scan.image.camera"
        cameraButton.addTarget(self, action: #selector(didTapCamera), for: .touchUpInside)
        let row = UIStackView(arrangedSubviews: [libraryButton, pasteButton, cameraButton])
        row.axis = .horizontal
        row.spacing = 8
        row.distribution = .fillEqually
        return row
    }

    func makeImageActionButton(title: String, imageName: String) -> UIButton {
        let button = makeSourceButton(title: title, imageName: imageName)
        guard var configuration = button.configuration else { return button }
        configuration.imagePlacement = .top
        configuration.imagePadding = 5
        configuration.contentInsets = .init(top: 10, leading: 2, bottom: 10, trailing: 2)
        configuration.background.backgroundColor = AppTheme.softColor.withAlphaComponent(0.7)
        configuration.background.cornerRadius = 12
        configuration.titleTextAttributesTransformer = UIConfigurationTextAttributesTransformer { attributes in
            var updated = attributes
            updated.font = AppTheme.font(size: 11, weight: .semibold)
            return updated
        }
        button.configuration = configuration
        button.heightAnchor.constraint(greaterThanOrEqualToConstant: 58).isActive = true
        return button
    }

    func makeSourceButton(title: String, imageName: String) -> UIButton {
        let button = UIButton(type: .system)
        var configuration = UIButton.Configuration.plain()
        configuration.title = title
        configuration.image = UIImage(systemName: imageName)
        configuration.imagePadding = 8
        configuration.imagePlacement = .leading
        configuration.baseForegroundColor = AppTheme.primaryColor
        configuration.background.backgroundColor = AppTheme.cardBackgroundColor
        configuration.cornerStyle = .fixed
        configuration.background.cornerRadius = 12
        configuration.contentInsets = .init(top: 12, leading: 8, bottom: 12, trailing: 8)
        configuration.titleTextAttributesTransformer = UIConfigurationTextAttributesTransformer { attributes in
            var updated = attributes
            updated.font = AppTheme.font(size: 13, weight: .semibold, style: .subheadline)
            return updated
        }
        button.configuration = configuration
        button.enableSoftPressAnimation()
        button.heightAnchor.constraint(greaterThanOrEqualToConstant: 48).isActive = true
        return button
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
                let current = categories.first { $0.id == self.selectedCategory?.id }
                selectCategory(current ?? categories.first)
            } catch {
                guard !Task.isCancelled, !isAnalyzing else { return }
                statusLabel.text = L10n.text("Không tải được danh mục; AI vẫn có thể tự động nhận diện.")
                statusLabel.isHidden = false
            }
        }
    }

    func selectCategory(_ category: ScamCategory?) {
        selectedCategory = category
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
        AccessConsent.confirm(on: self, title: L10n.text("Chọn ảnh để kiểm tra?"), message: L10n.text("App chỉ đọc ảnh bạn chọn, không xem toàn bộ thư viện. Ảnh chỉ được gửi đến máy chủ khi bạn nhấn Phân tích ngay.")) { [weak self] in
            self?.presentPhotoPicker()
        }
    }

    @objc func didTapPasteImage() {
        guard !isAnalyzing, presentedViewController == nil else { return }
        let pasteboard = UIPasteboard.general
        if let provider = pasteboard.itemProviders.first(where: { $0.canLoadObject(ofClass: UIImage.self) }) {
            loadImage(from: provider)
        } else if let image = pasteboard.image {
            setSelectedImage(image)
        } else {
            showErrorAlert(message: L10n.choose(
                "Clipboard chưa có ảnh. Hãy sao chép một ảnh rồi nhấn Dán ảnh.",
                "There is no image on the clipboard. Copy an image, then tap Paste image."
            ))
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
            showErrorAlert(message: L10n.text("Camera không khả dụng trên thiết bị này. Simulator nên dùng Thư viện ảnh."))
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
        let alert = UIAlertController(title: L10n.text("Cho phép sử dụng camera"), message: L10n.text("Bạn có thể bật quyền Camera trong Cài đặt hoặc chọn ảnh từ thư viện."), preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: L10n.text("Để sau"), style: .cancel))
        alert.addAction(UIAlertAction(title: L10n.text("Mở Cài đặt"), style: .default) { _ in
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

    @objc func didTapAnalyze() {
        guard !isAnalyzing else { return }
        imageLoadID = UUID()
        view.endEditing(true)
        guard isInputReady else { return }
        let kind = inputKind
        let image = selectedImage
        let imageData = kind == .image ? image?.preparingForUpload().jpegData(compressionQuality: 0.84) : nil
        if kind == .image && imageData == nil {
            showErrorAlert(message: L10n.text("Không thể đọc ảnh đã chọn. Vui lòng chọn lại."))
            return
        }
        let input = contentEditor.text.trimmingCharacters(in: .whitespacesAndNewlines)
        if kind == .url {
            let candidate = input.contains("://") ? input : "https://" + input
            guard let url = URLComponents(string: candidate),
                  ["https", "http"].contains(url.scheme ?? ""),
                  let host = url.host, host.contains("."), !input.contains(where: { $0.isWhitespace }) else {
                showErrorAlert(message: L10n.text("Nhập một liên kết hợp lệ, ví dụ https://example.com. Liên kết chỉ được phân tích, không tự mở."))
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
                case .batch:
                    let batch = try await scanService.analyzeBatch(input: input)
                    guard !Task.isCancelled else { return }
                    setLoading(false)
                    navigationController?.pushViewController(BatchResultsViewController(results: batch.results), animated: true)
                    return
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
                    resultViewController.navigationItem.prompt = L10n.text("Không lưu được lịch sử trên thiết bị")
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
        NSLayoutConstraint.deactivate(placeholderConstraints)
        previewRatio?.isActive = false
        previewRatio = previewImageView.heightAnchor.constraint(equalTo: previewImageView.widthAnchor,
                                                                multiplier: image.size.height / max(image.size.width, 1))
        previewRatio?.isActive = true
        previewMaximumHeight?.isActive = true
        previewImageView.backgroundColor = .clear
        previewPlaceholder.isHidden = true
        scanFrame.isHidden = false
        previewImageView.animatePop()
        analyzeButton.isEnabled = true
        analyzeButton.alpha = 1
        statusLabel.isHidden = true
        previewImageView.layer.borderColor = AppTheme.primaryColor.withAlphaComponent(0.5).cgColor
        previewImageView.layer.borderWidth = 1.5
        updateReadyState()
        UIImpactFeedbackGenerator(style: .soft).impactOccurred()
    }

    func loadImage(from provider: NSItemProvider) {
        guard !isAnalyzing else { return }
        let requestID = UUID()
        imageLoadID = requestID
        guard provider.canLoadObject(ofClass: UIImage.self) else {
            showErrorAlert(message: L10n.text("Nội dung được thả không phải là ảnh hỗ trợ."))
            return
        }
        statusLabel.text = L10n.text("Đang mở ảnh…")
        statusLabel.isHidden = false

        provider.loadObject(ofClass: UIImage.self) { [weak self] object, error in
            DispatchQueue.main.async {
                guard let self, self.imageLoadID == requestID, !self.isAnalyzing else { return }
                if let image = object as? UIImage {
                    self.setSelectedImage(image)
                } else {
                    self.statusLabel.isHidden = true
                    self.showErrorAlert(message: error?.localizedDescription ?? L10n.text("Không đọc được ảnh. Vui lòng chọn lại."))
                }
            }
        }
    }

    func setLoading(_ isLoading: Bool) {
        isAnalyzing = isLoading
        analyzeButton.setPrimaryTitle(L10n.choose("Phân tích ngay", "Analyze now"))
        analyzeButton.isLoading = isLoading
        analyzeButton.isEnabled = !isLoading && isInputReady
        analyzeButton.alpha = isLoading || isInputReady ? 1 : 0.55
        contentStack.isUserInteractionEnabled = !isLoading
        statusLabel.text = isLoading
            ? L10n.choose("Đang phân tích…", "Analyzing…")
            : nil
        statusLabel.isHidden = !isLoading
        updateScanLoadingAnimation(isLoading: isLoading)

        if isLoading {
            statusLabel.animateFadeAndSlideIn(distance: 8)
            UIImpactFeedbackGenerator(style: .soft).impactOccurred()
        }
    }

    func updateScanLoadingAnimation(isLoading: Bool) {
        scanFrame.isScanning = isLoading
        previewImageView.layer.borderColor = isLoading
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
            self.previewImageView.layer.borderColor = AppTheme.primaryColor.cgColor
            self.previewImageView.layer.borderWidth = 2
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
            self.previewImageView.layer.borderColor = AppTheme.borderColor.cgColor
            self.previewImageView.layer.borderWidth = self.selectedImage == nil ? 0 : 1
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
    var isBusy: Bool { isAnalyzing }

    func transferDraft(to target: ScanViewController) {
        guard isViewLoaded else { return }
        target.loadViewIfNeeded()
        target.textDraft = inputKind == .text ? contentEditor.text : textDraft
        target.urlDraft = inputKind == .url ? contentEditor.text : urlDraft
        target.batchDraft = inputKind == .batch ? contentEditor.text : batchDraft
        target.documentData = documentData
        target.documentName = documentName
        target.documentLabel.text = documentName ?? L10n.text("Chưa chọn tài liệu")
        target.categories = categories
        target.selectCategory(selectedCategory)
        if let selectedImage { target.setSelectedImage(selectedImage) }
        target.sourceControl.selectedSegmentIndex = ScanInputKind.allCases.firstIndex(of: inputKind) ?? 0
        target.inputKind = inputKind
        target.updateInputMode()
    }



    private var isInputReady: Bool {
        switch inputKind {
        case .image: return selectedImage != nil
        case .pdf: return documentData != nil
        case .batch: return !BatchInput.urls(from: contentEditor.text).isEmpty
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
        contentEditor.layer.borderWidth = 1
        contentEditor.layer.borderColor = AppTheme.borderColor.cgColor
        contentEditor.textContainerInset = UIEdgeInsets(top: 16, left: 12, bottom: 16, right: 12)
        editorHeightConstraint = contentEditor.heightAnchor.constraint(equalToConstant: 140)
        editorHeightConstraint?.isActive = true
        contentEditor.delegate = self
        contentEditor.accessibilityIdentifier = "scan.content"
        editorPlaceholder.font = AppTheme.font(size: 14)
        editorPlaceholder.textColor = AppTheme.secondaryTextColor.withAlphaComponent(0.7)
        editorPlaceholder.numberOfLines = 0
        editorPlaceholder.isUserInteractionEnabled = false
        editorPlaceholder.translatesAutoresizingMaskIntoConstraints = false
        contentEditor.addSubview(editorPlaceholder)
        NSLayoutConstraint.activate([
            editorPlaceholder.topAnchor.constraint(equalTo: contentEditor.topAnchor, constant: 16),
            editorPlaceholder.leadingAnchor.constraint(equalTo: contentEditor.leadingAnchor, constant: 17),
            editorPlaceholder.trailingAnchor.constraint(equalTo: contentEditor.trailingAnchor, constant: -17)
        ])
        inputHint.adjustsFontForContentSizeCategory = true
        inputHint.font = AppTheme.font(size: 13, weight: .semibold)
        inputHint.textColor = AppTheme.titleColor
        inputHint.numberOfLines = 0
        characterCount.font = .preferredFont(forTextStyle: .caption1)
        characterCount.textColor = AppTheme.secondaryTextColor
        characterCount.textAlignment = .right
        [inputHint, contentEditor, characterCount].forEach(textSection.addArrangedSubview)
        let toolbar = UIToolbar()
        toolbar.sizeToFit()
        toolbar.items = [UIBarButtonItem(systemItem: .flexibleSpace),
            UIBarButtonItem(title: "Xong", primaryAction: UIAction { [weak self] _ in self?.view.endEditing(true) })]
        contentEditor.inputAccessoryView = toolbar

        documentSection.axis = .vertical
        documentSection.spacing = 14
        let limits = UILabel()
        limits.text = L10n.choose("Tối đa 15 MB. Phân tích 10 trang đầu.", "Up to 15 MB. Checks the first 10 pages.")
        limits.font = .preferredFont(forTextStyle: .footnote)
        limits.adjustsFontForContentSizeCategory = true
        limits.textColor = AppTheme.secondaryTextColor
        limits.numberOfLines = 0
        documentLabel.text = L10n.text("Chưa chọn tài liệu")
        documentLabel.font = .preferredFont(forTextStyle: .headline)
        documentLabel.textColor = AppTheme.titleColor
        documentLabel.numberOfLines = 0
        let choose = makeSourceButton(title: L10n.text("Chọn PDF từ Tệp"), imageName: "folder")
        choose.addAction(UIAction { [weak self] _ in
            guard let self, !self.isAnalyzing else { return }
            AccessConsent.confirm(on: self, title: L10n.text("Chọn tài liệu để kiểm tra?"), message: L10n.text("App chỉ đọc tệp PDF bạn chọn. Tài liệu chỉ được gửi đến máy chủ khi bạn nhấn Phân tích ngay.")) { [weak self] in
                guard let self else { return }
                let picker = UIDocumentPickerViewController(forOpeningContentTypes: [.pdf], asCopy: true)
                picker.delegate = self
                self.present(picker, animated: true)
            }
        }, for: .touchUpInside)
        [choose, documentLabel, limits].forEach(documentSection.addArrangedSubview)
    }

    @objc private func changeInputKind() {
        if inputKind == .text { textDraft = contentEditor.text }
        if inputKind == .url { urlDraft = contentEditor.text }
        if inputKind == .batch { batchDraft = contentEditor.text }
        imageLoadID = UUID()
        inputKind = ScanInputKind.allCases[sourceControl.selectedSegmentIndex]
        view.endEditing(true)
        updateInputMode()
        updateSourceSelection()
        UISelectionFeedbackGenerator().selectionChanged()
    }

    private func updateInputMode() {
        imageSection.isHidden = inputKind != .image
        textSection.isHidden = ![.text, .url, .batch].contains(inputKind)
        documentSection.isHidden = inputKind != .pdf
        privacyLabel.text = inputKind == .url || inputKind == .batch
            ? L10n.choose("Chỉ gửi nội dung khi bạn nhấn Phân tích. URL có thể được đối chiếu qua Google Safe Browsing.",
                          "Content is sent only when you tap Analyze. URLs may be checked with Google Safe Browsing.")
            : L10n.choose("Nội dung chỉ được gửi khi bạn nhấn Phân tích.",
                          "Content is sent only when you tap Analyze.")
        contentEditor.text = inputKind == .batch ? batchDraft : inputKind == .url ? urlDraft : textDraft
        editorHeightConstraint?.constant = inputKind == .url ? 62 : 140
        contentEditor.keyboardType = inputKind == .url ? .URL : .default
        contentEditor.autocapitalizationType = inputKind == .url ? .none : .sentences
        contentEditor.autocorrectionType = inputKind == .url ? .no : .default
        contentEditor.accessibilityLabel = inputKind == .url ? L10n.text("Liên kết cần kiểm tra") : L10n.text("Tin nhắn cần kiểm tra")
        inputHint.text = inputKind == .url
            ? L10n.choose("Nhập URL hoặc tên miền cần kiểm tra", "Enter a URL or domain")
            : L10n.choose("Dán nội dung SMS, email hoặc đoạn chat", "Paste an SMS, email or chat")
        editorPlaceholder.text = inputKind == .url
            ? "https://example.com/login"
            : L10n.choose("Ví dụ: Tài khoản của quý khách sẽ bị khóa. Truy cập đường dẫn sau để xác minh...",
                          "Example: Your account will be locked. Open this link to verify...")
        if inputKind == .batch {
            inputHint.text = L10n.choose("Dán tối đa 50 URL, mỗi dòng một URL", "Paste up to 50 URLs, one per line")
            editorPlaceholder.text = "https://example.com\nhttps://example.org"
            contentEditor.accessibilityLabel = L10n.text("Danh sách URL cần kiểm tra")
            contentEditor.autocorrectionType = .no
            contentEditor.autocapitalizationType = .none
        }
        statusLabel.isHidden = true
        editorPlaceholder.isHidden = !contentEditor.text.isEmpty
        updateSourceSelection()
        updateReadyState()
    }

    func textViewDidChange(_ textView: UITextView) {
        editorPlaceholder.isHidden = !textView.text.isEmpty
        updateReadyState()
        revealEditor()
    }
    func textViewDidBeginEditing(_ textView: UITextView) {
        sourcePicker.isHidden = true
        inputHint.isHidden = true
        view.layoutIfNeeded()
    }

    @objc private func revealEditor() {
        guard contentEditor.isFirstResponder else { return }
        view.layoutIfNeeded()
        let available = scrollView.bounds.height - scrollView.adjustedContentInset.top - scrollView.adjustedContentInset.bottom
        editorHeightConstraint?.constant = inputKind == .url ? 62 : min(140, max(80, available - 24))
        view.layoutIfNeeded()
        let rect = contentEditor.convert(contentEditor.bounds, to: scrollView).insetBy(dx: 0, dy: -8)
        scrollView.scrollRectToVisible(rect, animated: false)
    }

    func textViewDidEndEditing(_ textView: UITextView) {
        editorHeightConstraint?.constant = inputKind == .url ? 62 : 140
        sourcePicker.isHidden = false
        inputHint.isHidden = false
    }

    private func updateReadyState() {
        analyzeButton.isEnabled = isInputReady && !isAnalyzing
        analyzeButton.alpha = isInputReady ? 1 : 0.55
        let limit = inputKind == .url ? 4096 : 20000
        characterCount.text = L10n.choose("\(contentEditor.text.count) / \(limit) ký tự", "\(contentEditor.text.count) / \(limit) characters")
        characterCount.textColor = contentEditor.text.count > limit ? AppTheme.dangerousColor : AppTheme.secondaryTextColor
        if inputKind == .batch {
            let count = BatchInput.urls(from: contentEditor.text).count
            characterCount.text = count > 50 ? L10n.choose("Chỉ 50 URL đầu tiên được kiểm tra", "Only the first 50 URLs will be checked") : "\(count) / 50 URL"
            characterCount.textColor = count > 50 ? AppTheme.dangerousColor : AppTheme.secondaryTextColor
        }
    }

    func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
        guard !isAnalyzing, let url = urls.first else { return }
        let accessed = url.startAccessingSecurityScopedResource()
        defer { if accessed { url.stopAccessingSecurityScopedResource() } }
        do {
            let size = try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0
            guard size > 0, size <= 15 * 1024 * 1024 else {
                showErrorAlert(message: L10n.text("Hãy chọn PDF có nội dung, tối đa 15 MB.")); return
            }
            let data = try Data(contentsOf: url)
            guard data.count <= 15 * 1024 * 1024 else {
                showErrorAlert(message: L10n.text("PDF vượt quá 15 MB.")); return
            }
            documentData = data
            documentName = url.lastPathComponent
            documentLabel.text = "\(url.lastPathComponent)\n\(ByteCountFormatter.string(fromByteCount: Int64(data.count), countStyle: .file))"
            updateReadyState()
        } catch { showErrorAlert(message: L10n.text("Không mở được PDF. Hãy tải tài liệu về thiết bị rồi thử lại.")) }
    }
}
