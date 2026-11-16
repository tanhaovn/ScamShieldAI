import UIKit

// MARK: - Reusable Animations

extension UIView {

    func animateFadeAndSlideIn(
        delay: TimeInterval = 0,
        distance: CGFloat = 10
    ) {
        guard !UIAccessibility.isReduceMotionEnabled else {
            alpha = 1
            transform = .identity
            return
        }

        alpha = 0
        transform = CGAffineTransform(translationX: 0, y: distance)

        UIView.animate(
            withDuration: 0.42,
            delay: delay,
            options: [.curveEaseOut, .allowUserInteraction, .beginFromCurrentState]
        ) {
            self.alpha = 1
            self.transform = .identity
        }
    }

    func animatePop() {
        guard !UIAccessibility.isReduceMotionEnabled else {
            alpha = 1
            transform = .identity
            return
        }

        transform = CGAffineTransform(scaleX: 0.985, y: 0.985)
        alpha = 0.86

        UIView.animate(
            withDuration: 0.24,
            delay: 0,
            options: [.curveEaseOut, .allowUserInteraction, .beginFromCurrentState]
        ) {
            self.transform = .identity
            self.alpha = 1
        }
    }

    func animateShake() {
        guard !UIAccessibility.isReduceMotionEnabled else { return }

        let animation = CAKeyframeAnimation(keyPath: "transform.translation.x")
        animation.values = [0, -5, 4, -3, 2, 0]
        animation.duration = 0.26
        animation.timingFunction = CAMediaTimingFunction(name: .easeOut)
        layer.add(animation, forKey: "shake")
    }
}

// MARK: - Button Press Feedback

extension UIButton {

    /// Thêm cảm giác nhấn mềm cho các nút UIKit thông thường.
    func enableSoftPressAnimation() {
        addTarget(self, action: #selector(appPressDown), for: .touchDown)
        addTarget(
            self,
            action: #selector(appPressUp),
            for: [.touchUpInside, .touchUpOutside, .touchCancel, .touchDragExit]
        )
    }

    @objc private func appPressDown() {
        guard !UIAccessibility.isReduceMotionEnabled else { return }
        UIView.animate(withDuration: 0.1, delay: 0, options: [.allowUserInteraction]) {
            self.transform = CGAffineTransform(scaleX: 0.985, y: 0.985)
            self.alpha = 0.96
        }
    }

    @objc private func appPressUp() {
        guard !UIAccessibility.isReduceMotionEnabled else { return }
        UIView.animate(
            withDuration: 0.18,
            delay: 0,
            options: [.curveEaseOut, .allowUserInteraction, .beginFromCurrentState]
        ) {
            self.transform = .identity
            self.alpha = 1
        }
    }
}
