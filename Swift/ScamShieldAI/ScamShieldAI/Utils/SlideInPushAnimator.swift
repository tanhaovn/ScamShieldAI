import UIKit

// MARK: - Slide-In Push Animator

/// Hiệu ứng push tuỳ chỉnh: màn mới trượt vào từ phải với spring damping,
/// đồng thời màn hiện tại lùi nhẹ sang trái — giống chuẩn UIKit nhưng mượt hơn.
///
/// Cách dùng:
/// ```swift
/// navigationController?.delegate = self  // trước khi push
/// navigationController?.pushViewController(detailVC, animated: true)
/// ```
/// Rồi implement UINavigationControllerDelegate để trả về animator này.
final class SlideInPushAnimator: NSObject, UIViewControllerAnimatedTransitioning {

    // MARK: - UIViewControllerAnimatedTransitioning

    func transitionDuration(
        using transitionContext: (any UIViewControllerContextTransitioning)?
    ) -> TimeInterval {
        0.40
    }

    func animateTransition(using transitionContext: any UIViewControllerContextTransitioning) {
        // Nếu người dùng bật Reduce Motion thì dùng default (không animate).
        guard !UIAccessibility.isReduceMotionEnabled else {
            transitionContext.completeTransition(true)
            return
        }

        guard
            let toView = transitionContext.view(forKey: .to),
            let fromView = transitionContext.view(forKey: .from)
        else {
            transitionContext.completeTransition(false)
            return
        }

        let container = transitionContext.containerView
        let width = container.bounds.width

        // Đặt màn mới ở bên phải ngoài màn hình trước khi animate.
        toView.transform = CGAffineTransform(translationX: width, y: 0)
        container.addSubview(toView)

        UIView.animate(
            withDuration: transitionDuration(using: transitionContext),
            delay: 0,
            usingSpringWithDamping: 0.88,
            initialSpringVelocity: 0.3,
            options: [.allowUserInteraction]
        ) {
            // Màn mới trượt vào vị trí chính giữa.
            toView.transform = .identity
            // Màn cũ lùi nhẹ 28% sang trái, tạo cảm giác chiều sâu như iOS.
            fromView.transform = CGAffineTransform(translationX: -width * 0.28, y: 0)
        } completion: { _ in
            fromView.transform = .identity
            transitionContext.completeTransition(!transitionContext.transitionWasCancelled)
        }
    }
}
