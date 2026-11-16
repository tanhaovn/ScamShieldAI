import UIKit

// MARK: - View Hierarchy

extension UIView {

    func addSubviews(_ views: UIView...) {
        views.forEach(addSubview)
    }

}
