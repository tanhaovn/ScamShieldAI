import UIKit

// MARK: - Upload Preparation

extension UIImage {

    func preparingForUpload(maxDimension: CGFloat = 1_800) -> UIImage {
        let longestSide = max(size.width, size.height)
        guard longestSide > 0, maxDimension > 0 else { return self }

        let scale = min(1, maxDimension / longestSide)
        let targetSize = CGSize(width: size.width * scale, height: size.height * scale)
        let format = UIGraphicsImageRendererFormat()
        format.scale = 1
        format.opaque = true
        let renderer = UIGraphicsImageRenderer(size: targetSize, format: format)

        // Thu nhỏ trước khi upload giúp iPhone dùng ít RAM và backend OCR nhanh hơn.
        return renderer.image { context in
            UIColor.white.setFill()
            context.fill(CGRect(origin: .zero, size: targetSize))
            draw(in: CGRect(origin: .zero, size: targetSize))
        }
    }
}
