import Foundation

struct Constants {

    // MARK: - API Environment

    // Debug: dòng trên dành cho Simulator, dòng dưới dành cho iPhone thật.
    static let simulatorAPIBaseURL = "http://127.0.0.1:8000"
    static let deviceAPIBaseURL = "http://192.168.0.3:8000"

    static var apiBaseURL: String {
        #if DEBUG
        #if targetEnvironment(simulator)
        return simulatorAPIBaseURL
        #else
        // iPhone và Mac phải cùng Wi-Fi. Cập nhật IP này nếu Mac đổi mạng.
        return deviceAPIBaseURL
        #endif
        #else
        let configured = (Bundle.main.object(forInfoDictionaryKey: "SCAMSHIELD_API_BASE_URL") as? String ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return configured
        #endif
    }

    // MARK: - URL Builder

    static func apiURL(path: String) -> URL? {
        let normalizedPath = path.hasPrefix("/") ? path : "/\(path)"
        guard let base = URLComponents(string: apiBaseURL),
              let host = base.host, !host.isEmpty,
              base.user == nil, base.password == nil,
              base.query == nil, base.fragment == nil,
              !apiBaseURL.contains("REPLACE_WITH"), !apiBaseURL.contains("$(") else { return nil }
        var allowed = base.scheme == "https"
        #if DEBUG
        let deviceHost = URLComponents(string: deviceAPIBaseURL)?.host
        allowed = allowed || (base.scheme == "http" &&
            (["127.0.0.1", "localhost", "::1"].contains(host) || host == deviceHost))
        #endif
        guard allowed else { return nil }
        return URL(string: apiBaseURL.trimmingCharacters(in: CharacterSet(charactersIn: "/")) + normalizedPath)
    }

    static func mediaURL(from rawValue: String?) -> URL? {
        guard let rawValue, !rawValue.isEmpty else { return nil }

        if rawValue.hasPrefix("local-history/") {
            return HistoryService.localImageURL(filename: String(rawValue.dropFirst(14)))
        }

        if let absoluteURL = URL(string: rawValue), absoluteURL.scheme != nil {
            return absoluteURL
        }

        return apiURL(path: rawValue)
    }
}
