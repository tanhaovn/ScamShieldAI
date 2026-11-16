import UIKit

final class MetricBarView: UIView {

    // MARK: - UI Components

    private let titleLabel = UILabel()
    private let valueLabel = UILabel()
    private let trackView = UIView()
    private let fillView = UIView()
    private var fillWidthConstraint: NSLayoutConstraint?
    private var targetValue = 0
    private var valueAnimationTask: Task<Void, Never>?

    // MARK: - Initialization

    init(title: String) {
        super.init(frame: .zero)
        titleLabel.text = title
        setupUI()
        NotificationCenter.default.addObserver(self, selector: #selector(motionPreferenceChanged), name: UIAccessibility.reduceMotionStatusDidChangeNotification, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(showFinalValue), name: UIApplication.willResignActiveNotification, object: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("MetricBarView chỉ được sử dụng bằng code.")
    }

    deinit {
        valueAnimationTask?.cancel()
        NotificationCenter.default.removeObserver(self)
    }

    // MARK: - Configuration

    func configure(value: Int, color: UIColor) {
        targetValue = min(max(value, 0), 100)
        fillView.backgroundColor = color
        valueLabel.accessibilityLabel = "\(targetValue) trên 100"
        showFinalValue()
    }

    override func didMoveToWindow() {
        super.didMoveToWindow()
        if window == nil { showFinalValue() }
    }

    func prepareForReveal() {
        showFinalValue()
        guard !UIAccessibility.isReduceMotionEnabled else { return }
        valueLabel.text = "0/100"
        setProgress(0)
        layoutIfNeeded()
    }

    func animateValue(delay: TimeInterval = 0) {
        prepareForReveal()
        guard !UIAccessibility.isReduceMotionEnabled, targetValue > 0 else {
            showFinalValue()
            return
        }
        valueAnimationTask = Task { [weak self] in
            do { try await Task.sleep(for: .seconds(max(0, delay))) } catch { return }
            let start = CACurrentMediaTime()
            while !Task.isCancelled {
                guard let self else { return }
                guard window != nil, UIApplication.shared.applicationState == .active,
                      !UIAccessibility.isReduceMotionEnabled else {
                    showFinalValue()
                    return
                }
                let progress = min((CACurrentMediaTime() - start) / 1.3, 1)
                let eased = 1 - pow(1 - progress, 2)
                valueLabel.text = "\(Int((Double(targetValue) * eased).rounded()))/100"
                setProgress(CGFloat(Double(targetValue) * eased / 100))
                layoutIfNeeded()
                if progress >= 1 { showFinalValue(); return }
                do { try await Task.sleep(for: .milliseconds(16)) } catch { return }
            }
        }
    }

    @objc func showFinalValue() {
        valueAnimationTask?.cancel()
        valueAnimationTask = nil
        valueLabel.text = "\(targetValue)/100"
        setProgress(CGFloat(targetValue) / 100)
        setNeedsLayout()
    }

    @objc private func motionPreferenceChanged() {
        if UIAccessibility.isReduceMotionEnabled { showFinalValue() }
    }

    private func setProgress(_ progress: CGFloat) {
        fillWidthConstraint?.isActive = false
        fillWidthConstraint = fillView.widthAnchor.constraint(equalTo: trackView.widthAnchor, multiplier: progress)
        fillWidthConstraint?.isActive = true
    }

}

// MARK: - Setup UI

private extension MetricBarView {

    func setupUI() {
        translatesAutoresizingMaskIntoConstraints = false

        titleLabel.font = .systemFont(ofSize: 14, weight: .medium)
        titleLabel.textColor = AppTheme.titleColor
        valueLabel.font = .monospacedDigitSystemFont(ofSize: 13, weight: .semibold)
        valueLabel.textColor = AppTheme.secondaryTextColor
        valueLabel.textAlignment = .right

        trackView.backgroundColor = AppTheme.borderColor
        trackView.layer.cornerRadius = 4
        trackView.translatesAutoresizingMaskIntoConstraints = false
        fillView.layer.cornerRadius = 4
        fillView.translatesAutoresizingMaskIntoConstraints = false

        let labelsStack = UIStackView(arrangedSubviews: [titleLabel, valueLabel])
        labelsStack.axis = .horizontal
        labelsStack.distribution = .fill

        let contentStack = UIStackView(arrangedSubviews: [labelsStack, trackView])
        contentStack.axis = .vertical
        contentStack.spacing = 8
        contentStack.translatesAutoresizingMaskIntoConstraints = false

        addSubview(contentStack)
        trackView.addSubview(fillView)
        NSLayoutConstraint.activate([
            contentStack.topAnchor.constraint(equalTo: topAnchor),
            contentStack.leadingAnchor.constraint(equalTo: leadingAnchor),
            contentStack.trailingAnchor.constraint(equalTo: trailingAnchor),
            contentStack.bottomAnchor.constraint(equalTo: bottomAnchor),
            trackView.heightAnchor.constraint(equalToConstant: 8),
            fillView.leadingAnchor.constraint(equalTo: trackView.leadingAnchor),
            fillView.topAnchor.constraint(equalTo: trackView.topAnchor),
            fillView.bottomAnchor.constraint(equalTo: trackView.bottomAnchor)
        ])
    }
}
