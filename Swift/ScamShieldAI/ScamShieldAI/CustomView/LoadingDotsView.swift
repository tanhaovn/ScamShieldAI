import UIKit

final class LoadingDotsView: UIView {

    // MARK: - UI Components

    private let dotViews: [UIView] = (0..<3).map { _ in
        let view = UIView()
        view.backgroundColor = AppTheme.primaryColor
        view.layer.cornerRadius = 4
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }

    // MARK: - Initialization

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
    }

    required init?(coder: NSCoder) {
        fatalError("LoadingDotsView chỉ được sử dụng bằng code.")
    }

    // MARK: - Animation

    func startAnimating() {
        dotViews.enumerated().forEach { index, dot in
            let animation = CABasicAnimation(keyPath: "transform.translation.y")
            animation.fromValue = 3
            animation.toValue = -4
            animation.duration = 0.42
            animation.beginTime = CACurrentMediaTime() + Double(index) * 0.14
            animation.autoreverses = true
            animation.repeatCount = .infinity
            animation.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
            dot.layer.add(animation, forKey: "bounce")
        }
    }

    func stopAnimating() {
        dotViews.forEach { $0.layer.removeAllAnimations() }
    }
}

// MARK: - Setup UI

private extension LoadingDotsView {

    func setupUI() {
        let stackView = UIStackView(arrangedSubviews: dotViews)
        stackView.axis = .horizontal
        stackView.spacing = 8
        stackView.translatesAutoresizingMaskIntoConstraints = false
        addSubview(stackView)

        dotViews.forEach { dot in
            NSLayoutConstraint.activate([
                dot.widthAnchor.constraint(equalToConstant: 8),
                dot.heightAnchor.constraint(equalToConstant: 8)
            ])
        }

        NSLayoutConstraint.activate([
            stackView.topAnchor.constraint(equalTo: topAnchor, constant: 4),
            stackView.leadingAnchor.constraint(equalTo: leadingAnchor),
            stackView.trailingAnchor.constraint(equalTo: trailingAnchor),
            stackView.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -4)
        ])
    }
}
