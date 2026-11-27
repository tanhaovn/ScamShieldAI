import Foundation

struct Constants {

    // MARK: - API Environment

    static let fallbackAPIBaseURL = "https://florida-naturals-junction-balance.trycloudflare.com"

    static var defaultAPIBaseURL: String {
        if let primary = normalizedServerURL(fallbackAPIBaseURL) {
            return primary
        }
        let configured = Bundle.main.object(forInfoDictionaryKey: "SCAMSHIELD_API_BASE_URL") as? String ?? ""
        return normalizedServerURL(configured) ?? fallbackAPIBaseURL
    }

    static var apiBaseURL: String {
        #if DEBUG
        if let override = ProcessInfo.processInfo.environment["SCAMSHIELD_DEBUG_API_BASE_URL"], !override.isEmpty { return override }
        #endif
        return defaultAPIBaseURL
    }

    static func normalizedServerURL(_ value: String) -> String? {
        let normalized = value.trimmingCharacters(in: .whitespacesAndNewlines).trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        guard let components = URLComponents(string: normalized),
              let host = components.host, !host.isEmpty,
              components.scheme == "https", components.user == nil, components.password == nil,
              components.query == nil, components.fragment == nil,
              components.path.isEmpty else { return nil }
        return normalized
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
        allowed = allowed || (base.scheme == "http" &&
            ["127.0.0.1", "localhost", "::1"].contains(host))
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
