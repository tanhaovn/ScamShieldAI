import UIKit

// MARK: - Padding

extension UITextField {

    func setLeftPadding(_ width: CGFloat) {
        let paddingView = UIView(frame: CGRect(x: 0, y: 0, width: width, height: 1))
        leftView = paddingView
        leftViewMode = .always
    }
}
