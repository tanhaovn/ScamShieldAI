import UIKit

final class RiskMetricsCardView: CardView {

    // MARK: - UI Components

    private let contentStack = UIStackView()
    private var metricViews: [MetricBarView] = []

    // MARK: - Initialization

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
    }

    required init?(coder: NSCoder) {
        fatalError("RiskMetricsCardView chỉ được sử dụng bằng code.")
    }

    // MARK: - Configuration

    func configure(
        textScore: Int,
        visualScore: Int,
        imageModelScore: Int?,
        imageModelAvailable: Bool,
        urlScore: Int? = nil,
        components: [AnalysisComponent]? = nil
    ) {
        metricViews.forEach {
            contentStack.removeArrangedSubview($0)
            $0.removeFromSuperview()
        }
        metricViews = []

        if let components, !components.isEmpty {
            components.forEach { addMetric(title: $0.title, score: $0.score) }
        } else {
            addMetric(title: "Nội dung văn bản", score: textScore)
            if let urlScore { addMetric(title: "Đường dẫn · PhishVN", score: urlScore) }
            addMetric(title: "Dấu hiệu hình ảnh", score: visualScore)
            if imageModelAvailable, let imageModelScore {
                addMetric(title: "Nhận diện hình ảnh", score: imageModelScore)
            }
        }
        metricViews.forEach(contentStack.addArrangedSubview)
    }

    func prepareForReveal() {
        metricViews.forEach { $0.prepareForReveal() }
    }

    func showFinalValues() {
        metricViews.forEach { $0.showFinalValue() }
    }

    func animateValues(delay: TimeInterval = 0.28) {
        metricViews.enumerated().forEach { index, metricView in
            metricView.animateValue(delay: delay + Double(index) * 0.08)
        }
    }
}

// MARK: - Setup UI

private extension RiskMetricsCardView {

    func addMetric(title: String, score: Int) {
        let metric = MetricBarView(title: title)
        let color = score >= 60 ? AppTheme.dangerousColor
            : score >= 25 ? AppTheme.suspiciousColor : AppTheme.primaryColor
        metric.configure(value: score, color: color)
        metricViews.append(metric)
    }

    func setupUI() {
        translatesAutoresizingMaskIntoConstraints = false

        let iconView = UIImageView(image: UIImage(systemName: "slider.horizontal.3"))
        iconView.tintColor = AppTheme.primaryColor
        iconView.contentMode = .scaleAspectFit
        iconView.translatesAutoresizingMaskIntoConstraints = false

        let titleLabel = UILabel()
        titleLabel.text = "Chi tiết đánh giá"
        titleLabel.font = .preferredFont(forTextStyle: .headline)
        titleLabel.adjustsFontForContentSizeCategory = true
        titleLabel.numberOfLines = 0
        titleLabel.textColor = AppTheme.titleColor

        let header = UIStackView(arrangedSubviews: [iconView, titleLabel])
        header.spacing = 10
        header.alignment = .center

        let subtitleLabel = UILabel()
        subtitleLabel.text = "Điểm cảnh báo của từng lớp phân tích, trên thang 100."
        subtitleLabel.font = .preferredFont(forTextStyle: .subheadline)
        subtitleLabel.adjustsFontForContentSizeCategory = true
        subtitleLabel.textColor = AppTheme.secondaryTextColor
        subtitleLabel.numberOfLines = 0

        contentStack.axis = .vertical
        contentStack.spacing = 18
        contentStack.translatesAutoresizingMaskIntoConstraints = false
        contentStack.addArrangedSubview(header)
        contentStack.addArrangedSubview(subtitleLabel)
        contentStack.setCustomSpacing(6, after: header)

        addSubview(contentStack)
        NSLayoutConstraint.activate([
            iconView.widthAnchor.constraint(equalToConstant: 23),
            iconView.heightAnchor.constraint(equalToConstant: 23),
            contentStack.topAnchor.constraint(equalTo: topAnchor, constant: 20),
            contentStack.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 20),
            contentStack.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -20),
            contentStack.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -22)
        ])
    }
}
