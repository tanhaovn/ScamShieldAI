import UIKit

final class RecognizedTextView: UITextView {
    init(text: String?, highlights: [String] = []) {
        super.init(frame: .zero, textContainer: nil)
        isEditable = false
        isScrollEnabled = false
        backgroundColor = AppTheme.fieldBackgroundColor
        layer.cornerRadius = 11
        layer.cornerCurve = .continuous
        textContainerInset = .init(top: 12, left: 10, bottom: 12, right: 10)
        adjustsFontForContentSizeCategory = true

        let content = text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let font = UIFont.preferredFont(forTextStyle: .body)
        let emphasized = UIFont(descriptor: font.fontDescriptor.withSymbolicTraits(.traitBold) ?? font.fontDescriptor, size: 0)
        let output = NSMutableAttributedString(
            string: content.isEmpty ? L10n.text("Không trích xuất được văn bản.") : content,
            attributes: [.font: font, .foregroundColor: AppTheme.titleColor]
        )
        let source = content as NSString
        for term in highlights where !term.isEmpty {
            var start = 0
            while start < source.length {
                let range = source.range(of: term, options: [.caseInsensitive, .diacriticInsensitive],
                                         range: NSRange(location: start, length: source.length - start))
                guard range.location != NSNotFound, range.length > 0 else { break }
                output.addAttributes([.backgroundColor: AppTheme.suspiciousColor.withAlphaComponent(0.25),
                                      .font: emphasized], range: range)
                start = NSMaxRange(range)
            }
        }
        attributedText = output
    }

    required init?(coder: NSCoder) { fatalError("Use init(text:highlights:)") }
}
