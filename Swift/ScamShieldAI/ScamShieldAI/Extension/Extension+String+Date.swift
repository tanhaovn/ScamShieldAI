import Foundation

// MARK: - Backend Date Formatting

extension String {

    var backendDateDisplayText: String {
        let isoFormatter = ISO8601DateFormatter()
        isoFormatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]

        let fallbackFormatter = DateFormatter()
        fallbackFormatter.locale = Locale(identifier: "en_US_POSIX")
        fallbackFormatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"

        let date = isoFormatter.date(from: self)
            ?? ISO8601DateFormatter().date(from: self)
            ?? fallbackFormatter.date(from: String(prefix(19)))

        guard let date else { return self }

        let displayFormatter = DateFormatter()
        displayFormatter.locale = Locale(identifier: "vi_VN")
        displayFormatter.dateFormat = "HH:mm • dd/MM/yyyy"
        return displayFormatter.string(from: date)
    }
}
