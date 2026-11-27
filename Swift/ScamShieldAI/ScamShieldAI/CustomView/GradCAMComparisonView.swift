import UIKit

final class GradCAMComparisonView: CardView {
    init(result: ScanResult, originalImage: UIImage?) {
        super.init(frame: .zero)

        let title = label(L10n.choose("Vì sao mô hình ảnh đưa ra dự đoán này?",
                                     "Why did the image model make this prediction?"),
                          style: .headline, color: AppTheme.titleColor)
        title.accessibilityTraits = .header
        let stack = UIStackView(arrangedSubviews: [title])
        stack.axis = .vertical
        stack.spacing = 12
        stack.translatesAutoresizingMaskIntoConstraints = false
        addSubview(stack)
        NSLayoutConstraint.activate([
            stack.topAnchor.constraint(equalTo: topAnchor, constant: 16),
            stack.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
            stack.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),
            stack.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -16)
        ])

        guard let gradCAM = result.imageGradCAM, gradCAM.available == true,
              let path = gradCAM.image_url, let heatmapURL = Constants.mediaURL(from: path) else {
            let unavailable = L10n.text("Chưa có bản đồ Grad-CAM cho lần kiểm tra này.")
            stack.addArrangedSubview(label(gradCAMNote(result) ?? unavailable, style: .subheadline))
            return
        }

        let target = gradCAM.target_class ?? result.imageModelLabel
        let classification: String
        switch target {
        case "phishing": classification = L10n.choose("Giả mạo", "Phishing")
        case "legitimate": classification = L10n.choose("Hợp lệ", "Legitimate")
        default: classification = L10n.choose("Chưa xác định", "Unknown")
        }
        let score = (gradCAM.target_score ?? 0).clampedRiskPercent
        stack.addArrangedSubview(label("ResNet18 · \(classification) · \(score)%", style: .subheadline,
                                     color: AppTheme.primaryColor))

        var figures: [UIView] = []
        let originalURL = Constants.mediaURL(from: result.imageURL)
        if originalImage != nil || originalURL != nil {
            figures.append(figure(caption: L10n.choose("Ảnh gốc", "Original image"), image: originalImage, url: originalURL))
        }
        figures.append(figure(caption: L10n.text("Bản đồ Grad-CAM"), image: nil, url: heatmapURL))
        let images = UIStackView(arrangedSubviews: figures)
        images.distribution = .fillEqually
        images.alignment = .top
        images.spacing = 10
        stack.addArrangedSubview(images)
        let adapt: (UIStackView) -> Void = { row in
            let largeText = row.traitCollection.preferredContentSizeCategory.isAccessibilityCategory
            row.axis = largeText ? .vertical : .horizontal
            row.alignment = largeText ? .fill : .top
            row.distribution = largeText ? .fill : .fillEqually
        }
        adapt(images)
        images.registerForTraitChanges([UITraitPreferredContentSizeCategory.self]) { (row: UIStackView, _) in adapt(row) }

        stack.addArrangedSubview(label(L10n.choose("Màu lạnh: ít tác động · Màu nóng: tác động mạnh",
                                                  "Cool colors: lower contribution · Warm colors: higher contribution"),
                                      style: .caption1))

        let vision = result.visionAnalysis
        let points = vision?.explanation_items ?? []
        if vision?.explanation_source == "vision_language_model", !points.isEmpty {
            stack.addArrangedSubview(label(L10n.choose("Giải thích", "Explanation"), style: .headline, color: AppTheme.titleColor))
            for point in points {
                if let observation = point.observation, !observation.isEmpty {
                    stack.addArrangedSubview(label(observation, style: .subheadline, color: AppTheme.titleColor))
                }
                if let reason = point.why_risky, !reason.isEmpty {
                    stack.addArrangedSubview(label(reason, style: .subheadline))
                }
            }
        } else {
            let fallback = L10n.choose(
                "Chưa có giải thích từ AI thị giác. Grad-CAM cho biết vùng ảnh ảnh hưởng đến dự đoán.",
                "A visual AI explanation is unavailable. Grad-CAM shows which regions influenced the prediction."
            )
            stack.addArrangedSubview(label(vision?.note.flatMap { $0.isEmpty ? nil : $0 } ?? fallback, style: .subheadline))
        }
    }

    required init?(coder: NSCoder) { fatalError("Use init(result:originalImage:)") }

    private func gradCAMNote(_ result: ScanResult) -> String? {
        guard let note = result.imageGradCAM?.note, !note.isEmpty else { return nil }
        // Backend diagnostics may include a stack trace and local filesystem paths.
        let summary = note.components(separatedBy: "Chi tiết:").first ?? ""
        guard !summary.contains("\n"), !summary.contains("/") else { return nil }
        return summary.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private func figure(caption: String, image: UIImage?, url: URL?) -> UIView {
        let preview = RemoteImageView()
        preview.backgroundColor = AppTheme.fieldBackgroundColor
        preview.tintColor = AppTheme.secondaryTextColor
        preview.contentMode = .scaleAspectFit
        preview.layer.cornerRadius = 10
        preview.clipsToBounds = true
        preview.setContentHuggingPriority(.defaultLow, for: .horizontal)
        preview.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)
        let ratio = preview.heightAnchor.constraint(equalTo: preview.widthAnchor)
        ratio.priority = .defaultHigh
        ratio.isActive = true
        preview.heightAnchor.constraint(lessThanOrEqualToConstant: 230).isActive = true

        let text = label(caption, style: .caption1, color: AppTheme.titleColor)
        let stack = UIStackView(arrangedSubviews: [preview, text])
        stack.axis = .vertical
        stack.spacing = 6
        if let image {
            preview.image = image
        } else {
            preview.load(url: url, placeholder: nil) { [weak preview, weak text] success in
                guard !success else { return }
                preview?.isHidden = true
                text?.text = caption + " · " + L10n.choose("Không tải được ảnh", "Image unavailable")
            }
        }
        return stack
    }

    private func label(_ text: String, style: UIFont.TextStyle, color: UIColor = AppTheme.secondaryTextColor) -> UILabel {
        let label = UILabel()
        label.text = text
        label.font = .preferredFont(forTextStyle: style)
        label.adjustsFontForContentSizeCategory = true
        label.textColor = color
        label.numberOfLines = 0
        return label
    }
}

private extension Double {
    var clampedRiskPercent: Int { isFinite ? Int(min(max(self, 0), 100).rounded()) : 0 }
}
