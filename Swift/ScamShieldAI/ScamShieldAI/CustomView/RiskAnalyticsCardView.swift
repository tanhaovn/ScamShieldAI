import UIKit

final class RiskTrendCardView: CardView {

    private let chartView = RiskLineChartView()

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
    }

    required init?(coder: NSCoder) {
        fatalError("RiskTrendCardView chỉ được sử dụng bằng code.")
    }

    func configure(items: [ScanHistoryItem]) {
        let scores = items.prefix(10).reversed().map(\.riskScore)
        chartView.configure(scores: scores)
    }

    private func setupUI() {
        translatesAutoresizingMaskIntoConstraints = false

        let eyebrow = makeLabel("LỊCH SỬ KIỂM TRA", size: 9, weight: .bold, color: AppTheme.primaryColor)
        let title = makeLabel("Xu hướng rủi ro", size: 20, weight: .bold, color: AppTheme.titleColor)
        let subtitle = makeLabel("10 lượt kiểm tra gần nhất · thang điểm 0—100", size: 12, weight: .regular, color: AppTheme.secondaryTextColor)
        subtitle.numberOfLines = 0
        let heading = UIStackView(arrangedSubviews: [eyebrow, title, subtitle])
        heading.axis = .vertical
        heading.spacing = 5

        chartView.translatesAutoresizingMaskIntoConstraints = false
        chartView.heightAnchor.constraint(equalToConstant: 205).isActive = true

        let liveDot = UIView()
        liveDot.backgroundColor = AppTheme.primaryColor
        liveDot.layer.cornerRadius = 3
        liveDot.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            liveDot.widthAnchor.constraint(equalToConstant: 6),
            liveDot.heightAnchor.constraint(equalToConstant: 6)
        ])
        let live = makeLabel("DỮ LIỆU LỊCH SỬ", size: 9, weight: .bold, color: AppTheme.primaryColor)
        let hint = makeLabel("Điểm càng cao, nguy cơ càng lớn.", size: 10, weight: .regular, color: AppTheme.secondaryTextColor)
        hint.textAlignment = .right
        hint.numberOfLines = 0
        let liveStack = UIStackView(arrangedSubviews: [liveDot, live])
        liveStack.alignment = .center
        liveStack.spacing = 7
        let footer = UIStackView(arrangedSubviews: [liveStack, UIView(), hint])
        footer.alignment = .center
        footer.spacing = 8

        let stack = UIStackView(arrangedSubviews: [heading, chartView, footer])
        stack.axis = .vertical
        stack.spacing = 15
        stack.translatesAutoresizingMaskIntoConstraints = false
        addSubview(stack)
        NSLayoutConstraint.activate([
            stack.topAnchor.constraint(equalTo: topAnchor, constant: 20),
            stack.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 18),
            stack.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -18),
            stack.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -18)
        ])
    }

    private func makeLabel(_ text: String, size: CGFloat, weight: UIFont.Weight, color: UIColor) -> UILabel {
        let label = UILabel()
        label.text = text
        label.font = .systemFont(ofSize: size, weight: weight)
        label.textColor = color
        return label
    }
}

final class RiskDistributionCardView: CardView {

    private let donutView = RiskDonutView()
    private let safeRow = DistributionLegendRow(title: "Rủi ro thấp", color: AppTheme.safeColor)
    private let suspiciousRow = DistributionLegendRow(title: "Nghi ngờ", color: AppTheme.suspiciousColor)
    private let dangerousRow = DistributionLegendRow(title: "Nguy hiểm", color: AppTheme.dangerousColor)

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
    }

    required init?(coder: NSCoder) {
        fatalError("RiskDistributionCardView chỉ được sử dụng bằng code.")
    }

    func configure(safe: Int, suspicious: Int, dangerous: Int) {
        let total = safe + suspicious + dangerous
        donutView.configure(values: [safe, suspicious, dangerous])
        safeRow.configure(count: safe, total: total)
        suspiciousRow.configure(count: suspicious, total: total)
        dangerousRow.configure(count: dangerous, total: total)
        accessibilityLabel = "Phân bổ kết quả. Rủi ro thấp \(safe), nghi ngờ \(suspicious), nguy hiểm \(dangerous)."
    }

    private func setupUI() {
        translatesAutoresizingMaskIntoConstraints = false
        isAccessibilityElement = true

        let eyebrow = makeLabel("MỨC ĐỘ RỦI RO", size: 9, weight: .bold, color: AppTheme.primaryColor)
        let title = makeLabel("Phân bổ kết quả", size: 20, weight: .bold, color: AppTheme.titleColor)
        let subtitle = makeLabel("Tất cả lượt đã phân tích", size: 12, weight: .regular, color: AppTheme.secondaryTextColor)
        let heading = UIStackView(arrangedSubviews: [eyebrow, title, subtitle])
        heading.axis = .vertical
        heading.spacing = 5

        donutView.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            donutView.widthAnchor.constraint(equalToConstant: 126),
            donutView.heightAnchor.constraint(equalToConstant: 126)
        ])

        let legend = UIStackView(arrangedSubviews: [safeRow, suspiciousRow, dangerousRow])
        legend.axis = .vertical
        legend.spacing = 11
        let body = UIStackView(arrangedSubviews: [donutView, legend])
        body.alignment = .center
        body.spacing = 16

        let stack = UIStackView(arrangedSubviews: [heading, body])
        stack.axis = .vertical
        stack.spacing = 18
        stack.translatesAutoresizingMaskIntoConstraints = false
        addSubview(stack)
        NSLayoutConstraint.activate([
            stack.topAnchor.constraint(equalTo: topAnchor, constant: 20),
            stack.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 18),
            stack.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -18),
            stack.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -20)
        ])
    }

    private func makeLabel(_ text: String, size: CGFloat, weight: UIFont.Weight, color: UIColor) -> UILabel {
        let label = UILabel()
        label.text = text
        label.font = .systemFont(ofSize: size, weight: weight)
        label.textColor = color
        return label
    }
}

private final class RiskLineChartView: UIView {

    private let drawingLayer = CALayer()
    private var scores: [Int] = []
    private var needsChartLayout = true
    private var lastSize = CGSize.zero

    override init(frame: CGRect) {
        super.init(frame: frame)
        isAccessibilityElement = true
        layer.addSublayer(drawingLayer)
    }

    required init?(coder: NSCoder) {
        fatalError("RiskLineChartView chỉ được sử dụng bằng code.")
    }

    func configure(scores: [Int]) {
        self.scores = scores.map { min(max($0, 0), 100) }
        accessibilityLabel = scores.isEmpty
            ? "Biểu đồ xu hướng chưa có dữ liệu"
            : "Biểu đồ xu hướng gồm \(scores.count) điểm: \(scores.map(String.init).joined(separator: ", "))"
        needsChartLayout = true
        setNeedsLayout()
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        drawingLayer.frame = bounds
        guard needsChartLayout || lastSize != bounds.size else { return }
        needsChartLayout = false
        lastSize = bounds.size
        rebuildLayers()
    }

    private func rebuildLayers() {
        drawingLayer.sublayers?.forEach { $0.removeFromSuperlayer() }
        let plot = CGRect(x: 31, y: 20, width: max(1, bounds.width - 43), height: max(1, bounds.height - 46))

        [100, 75, 50, 25, 0].forEach { value in
            let ratio = CGFloat(100 - value) / 100
            let y = plot.minY + ratio * plot.height
            let gridPath = UIBezierPath()
            gridPath.move(to: CGPoint(x: plot.minX, y: y))
            gridPath.addLine(to: CGPoint(x: plot.maxX, y: y))
            let grid = CAShapeLayer()
            grid.path = gridPath.cgPath
            grid.strokeColor = AppTheme.borderColor.cgColor
            grid.lineWidth = 1
            grid.lineDashPattern = [3, 5]
            drawingLayer.addSublayer(grid)

            let label = CATextLayer()
            label.string = String(value)
            label.font = UIFont.monospacedDigitSystemFont(ofSize: 8, weight: .medium)
            label.fontSize = 8
            label.foregroundColor = AppTheme.secondaryTextColor.cgColor
            label.alignmentMode = .right
            label.contentsScale = UIScreen.main.scale
            label.frame = CGRect(x: 0, y: y - 5, width: 25, height: 11)
            drawingLayer.addSublayer(label)
        }

        guard !scores.isEmpty else {
            let empty = CATextLayer()
            empty.string = "Thực hiện một lượt kiểm tra để tạo biểu đồ"
            empty.font = UIFont.systemFont(ofSize: 11, weight: .medium)
            empty.fontSize = 11
            empty.foregroundColor = AppTheme.secondaryTextColor.cgColor
            empty.alignmentMode = .center
            empty.contentsScale = UIScreen.main.scale
            empty.frame = CGRect(x: plot.minX, y: plot.midY - 8, width: plot.width, height: 20)
            drawingLayer.addSublayer(empty)
            return
        }

        let points = scores.enumerated().map { index, score in
            let x = scores.count == 1
                ? plot.midX
                : plot.minX + CGFloat(index) * plot.width / CGFloat(scores.count - 1)
            let y = plot.maxY - CGFloat(score) / 100 * plot.height
            return CGPoint(x: x, y: y)
        }

        let linePath = UIBezierPath()
        linePath.move(to: points[0])
        points.dropFirst().forEach(linePath.addLine)

        let areaPath = UIBezierPath(cgPath: linePath.cgPath)
        areaPath.addLine(to: CGPoint(x: points.last?.x ?? plot.maxX, y: plot.maxY))
        areaPath.addLine(to: CGPoint(x: points[0].x, y: plot.maxY))
        areaPath.close()
        let areaMask = CAShapeLayer()
        areaMask.path = areaPath.cgPath
        let gradient = CAGradientLayer()
        gradient.frame = bounds
        gradient.colors = [
            AppTheme.primaryColor.withAlphaComponent(0.24).cgColor,
            AppTheme.primaryColor.withAlphaComponent(0.01).cgColor
        ]
        gradient.startPoint = CGPoint(x: 0.5, y: 0)
        gradient.endPoint = CGPoint(x: 0.5, y: 1)
        gradient.mask = areaMask
        drawingLayer.addSublayer(gradient)

        let line = CAShapeLayer()
        line.path = linePath.cgPath
        line.fillColor = UIColor.clear.cgColor
        line.strokeColor = AppTheme.primaryColor.cgColor
        line.lineWidth = 3
        line.lineCap = .round
        line.lineJoin = .round
        drawingLayer.addSublayer(line)

        var pointLayers: [CALayer] = []
        for (index, point) in points.enumerated() {
            let halo = CAShapeLayer()
            halo.path = UIBezierPath(ovalIn: CGRect(x: point.x - 8, y: point.y - 8, width: 16, height: 16)).cgPath
            halo.fillColor = AppTheme.primaryColor.withAlphaComponent(0.11).cgColor
            drawingLayer.addSublayer(halo)

            let dot = CAShapeLayer()
            dot.path = UIBezierPath(ovalIn: CGRect(x: point.x - 4, y: point.y - 4, width: 8, height: 8)).cgPath
            dot.fillColor = UIColor.white.cgColor
            dot.strokeColor = AppTheme.primaryColor.cgColor
            dot.lineWidth = 2.5
            drawingLayer.addSublayer(dot)
            pointLayers.append(contentsOf: [halo, dot])

            let score = CATextLayer()
            score.string = String(scores[index])
            score.font = UIFont.monospacedDigitSystemFont(ofSize: 9, weight: .bold)
            score.fontSize = 9
            score.foregroundColor = AppTheme.brandDark.cgColor
            score.alignmentMode = .center
            score.contentsScale = UIScreen.main.scale
            score.frame = CGRect(x: point.x - 15, y: max(0, point.y - 20), width: 30, height: 12)
            drawingLayer.addSublayer(score)
            pointLayers.append(score)
        }

        guard !UIAccessibility.isReduceMotionEnabled else { return }
        line.strokeEnd = 0
        let lineAnimation = CABasicAnimation(keyPath: "strokeEnd")
        lineAnimation.fromValue = 0
        lineAnimation.toValue = 1
        lineAnimation.duration = 0.85
        lineAnimation.timingFunction = CAMediaTimingFunction(name: .easeOut)
        line.strokeEnd = 1
        line.add(lineAnimation, forKey: "drawLine")

        gradient.opacity = 0
        let fade = CABasicAnimation(keyPath: "opacity")
        fade.fromValue = 0
        fade.toValue = 1
        fade.duration = 0.65
        fade.beginTime = CACurrentMediaTime() + 0.25
        fade.fillMode = .backwards
        gradient.opacity = 1
        gradient.add(fade, forKey: "fadeArea")

        pointLayers.enumerated().forEach { index, layer in
            let appear = CAAnimationGroup()
            let scale = CABasicAnimation(keyPath: "transform.scale")
            scale.fromValue = 0.45
            scale.toValue = 1
            let opacity = CABasicAnimation(keyPath: "opacity")
            opacity.fromValue = 0
            opacity.toValue = 1
            appear.animations = [scale, opacity]
            appear.duration = 0.25
            appear.beginTime = CACurrentMediaTime() + 0.35 + Double(index / 3) * 0.06
            appear.fillMode = .backwards
            layer.add(appear, forKey: "pointAppear")
        }
    }
}

private final class RiskDonutView: UIView {

    private let ringLayer = CALayer()
    private let totalLabel = UILabel()
    private let captionLabel = UILabel()
    private var values = [0, 0, 0]
    private var needsRingLayout = true
    private var lastSize = CGSize.zero

    override init(frame: CGRect) {
        super.init(frame: frame)
        layer.addSublayer(ringLayer)
        totalLabel.font = .monospacedDigitSystemFont(ofSize: 27, weight: .bold)
        totalLabel.textColor = AppTheme.titleColor
        totalLabel.textAlignment = .center
        captionLabel.text = "TỔNG LƯỢT"
        captionLabel.font = .systemFont(ofSize: 8, weight: .bold)
        captionLabel.textColor = AppTheme.secondaryTextColor
        captionLabel.textAlignment = .center
        let stack = UIStackView(arrangedSubviews: [totalLabel, captionLabel])
        stack.axis = .vertical
        stack.spacing = 1
        stack.translatesAutoresizingMaskIntoConstraints = false
        addSubview(stack)
        NSLayoutConstraint.activate([
            stack.centerXAnchor.constraint(equalTo: centerXAnchor),
            stack.centerYAnchor.constraint(equalTo: centerYAnchor)
        ])
    }

    required init?(coder: NSCoder) {
        fatalError("RiskDonutView chỉ được sử dụng bằng code.")
    }

    func configure(values: [Int]) {
        self.values = Array(values.prefix(3)) + Array(repeating: 0, count: max(0, 3 - values.count))
        totalLabel.text = String(self.values.reduce(0, +))
        needsRingLayout = true
        setNeedsLayout()
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        ringLayer.frame = bounds
        guard needsRingLayout || lastSize != bounds.size else { return }
        needsRingLayout = false
        lastSize = bounds.size
        ringLayer.sublayers?.forEach { $0.removeFromSuperlayer() }

        let center = CGPoint(x: bounds.midX, y: bounds.midY)
        let radius = max(1, min(bounds.width, bounds.height) / 2 - 12)
        let path = UIBezierPath(arcCenter: center, radius: radius, startAngle: -.pi / 2, endAngle: .pi * 1.5, clockwise: true)
        let track = CAShapeLayer()
        track.path = path.cgPath
        track.fillColor = UIColor.clear.cgColor
        track.strokeColor = AppTheme.borderColor.cgColor
        track.lineWidth = 11
        ringLayer.addSublayer(track)

        let total = values.reduce(0, +)
        guard total > 0 else { return }
        let colors = [AppTheme.safeColor, AppTheme.suspiciousColor, AppTheme.dangerousColor]
        var start: CGFloat = 0
        for (index, value) in values.enumerated() where value > 0 {
            let fraction = CGFloat(value) / CGFloat(total)
            let segment = CAShapeLayer()
            segment.path = path.cgPath
            segment.fillColor = UIColor.clear.cgColor
            segment.strokeColor = colors[index].cgColor
            segment.lineWidth = 11
            segment.lineCap = .round
            segment.strokeStart = start + 0.006
            segment.strokeEnd = max(segment.strokeStart, start + fraction - 0.006)
            ringLayer.addSublayer(segment)

            if !UIAccessibility.isReduceMotionEnabled {
                let animation = CABasicAnimation(keyPath: "strokeEnd")
                animation.fromValue = segment.strokeStart
                animation.toValue = segment.strokeEnd
                animation.duration = 0.65
                animation.beginTime = CACurrentMediaTime() + Double(index) * 0.08
                animation.fillMode = .backwards
                animation.timingFunction = CAMediaTimingFunction(name: .easeOut)
                segment.add(animation, forKey: "drawSegment")
            }
            start += fraction
        }
    }
}

private final class DistributionLegendRow: UIView {

    private let countLabel = UILabel()
    private let percentLabel = UILabel()

    init(title: String, color: UIColor) {
        super.init(frame: .zero)
        translatesAutoresizingMaskIntoConstraints = false

        let dot = UIView()
        dot.backgroundColor = color
        dot.layer.cornerRadius = 4
        dot.translatesAutoresizingMaskIntoConstraints = false
        let titleLabel = UILabel()
        titleLabel.text = title
        titleLabel.font = .systemFont(ofSize: 12, weight: .semibold)
        titleLabel.textColor = AppTheme.titleColor
        countLabel.font = .monospacedDigitSystemFont(ofSize: 15, weight: .bold)
        countLabel.textColor = color
        countLabel.textAlignment = .right
        countLabel.setContentHuggingPriority(.required, for: .horizontal)
        percentLabel.font = .systemFont(ofSize: 9, weight: .regular)
        percentLabel.textColor = AppTheme.secondaryTextColor
        let labels = UIStackView(arrangedSubviews: [titleLabel, percentLabel])
        labels.axis = .vertical
        labels.spacing = 2
        let row = UIStackView(arrangedSubviews: [dot, labels, countLabel])
        row.alignment = .center
        row.spacing = 8
        row.translatesAutoresizingMaskIntoConstraints = false
        addSubview(row)
        NSLayoutConstraint.activate([
            dot.widthAnchor.constraint(equalToConstant: 8),
            dot.heightAnchor.constraint(equalToConstant: 8),
            row.topAnchor.constraint(equalTo: topAnchor),
            row.leadingAnchor.constraint(equalTo: leadingAnchor),
            row.trailingAnchor.constraint(equalTo: trailingAnchor),
            row.bottomAnchor.constraint(equalTo: bottomAnchor)
        ])
    }

    required init?(coder: NSCoder) {
        fatalError("DistributionLegendRow chỉ được sử dụng bằng code.")
    }

    func configure(count: Int, total: Int) {
        countLabel.text = String(count)
        let percent = total == 0 ? 0 : Int((Double(count) / Double(total) * 100).rounded())
        percentLabel.text = "\(percent)% kết quả"
    }
}
