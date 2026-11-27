import UIKit
import AVFoundation

/// Uses the source image's coordinate system, so the overlays stay aligned after rotation.
final class AnnotatedImageView: UIView {
    private let imageView = UIImageView()
    private let regions: [ImageAnnotation]
    private let dimensions: ImageDimensions
    init(image: UIImage, dimensions: ImageDimensions, regions: [ImageAnnotation]) {
        self.regions = regions
        self.dimensions = dimensions
        super.init(frame: .zero)
        imageView.image = image
        imageView.contentMode = .scaleAspectFit
        addSubview(imageView)
        clipsToBounds = true
        layer.cornerRadius = 12
        let ratio = heightAnchor.constraint(equalTo: widthAnchor, multiplier: image.size.height / max(image.size.width, 1))
        ratio.priority = .defaultHigh
        ratio.isActive = true
        heightAnchor.constraint(lessThanOrEqualToConstant: 360).isActive = true
        isAccessibilityElement = true
        accessibilityLabel = L10n.choose("Ảnh đã phân tích, \(regions.count) vùng cần chú ý", "Analyzed image, \(regions.count) areas to review")
        accessibilityValue = regions.map { [$0.label, $0.reason].compactMap { $0 }.joined(separator: ": ") }.joined(separator: ". ")
    }
    required init?(coder: NSCoder) { fatalError("Use init(image:dimensions:regions:)") }
    override func layoutSubviews() {
        super.layoutSubviews()
        imageView.frame = bounds
        layer.sublayers?.filter { $0.name == "annotation" }.forEach { $0.removeFromSuperlayer() }
        guard dimensions.width > 0, dimensions.height > 0 else { return }
        let content = AVMakeRect(aspectRatio: imageView.image?.size ?? CGSize(width: dimensions.width, height: dimensions.height), insideRect: bounds)
        let sx = content.width / dimensions.width
        let sy = content.height / dimensions.height
        for (index, region) in regions.enumerated() {
            let rect = CGRect(x: content.minX + (region.left ?? 0) * sx, y: content.minY + (region.top ?? 0) * sy,
                              width: (region.width ?? 0) * sx, height: (region.height ?? 0) * sy).intersection(content)
            guard !rect.isNull, rect.width > 0, rect.height > 0 else { continue }
            let color = region.severity == "danger" ? AppTheme.dangerousColor : AppTheme.suspiciousColor
            let border = CAShapeLayer()
            border.name = "annotation"
            border.path = UIBezierPath(roundedRect: rect, cornerRadius: 3).cgPath
            border.strokeColor = color.cgColor
            border.fillColor = color.withAlphaComponent(0.12).cgColor
            border.lineWidth = 2
            layer.addSublayer(border)
            let number = CATextLayer()
            number.name = "annotation"
            number.string = "\(index + 1)"
            number.fontSize = 12
            number.alignmentMode = .center
            number.contentsScale = traitCollection.displayScale
            number.backgroundColor = color.cgColor
            number.foregroundColor = UIColor.white.cgColor
            number.cornerRadius = 9
            number.frame = CGRect(x: max(0, rect.minX - 9), y: max(0, rect.minY - 9), width: 18, height: 18)
            layer.addSublayer(number)
        }
    }
}
