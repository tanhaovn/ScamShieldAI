import Foundation
import Security

/// Account JWT used by scans, history and the native administrator area.
@MainActor
final class AccountSession {
    static let shared = AccountSession()
    static let didChange = Notification.Name("scamShield.accountSessionDidChange")

    private let keychainService = "ScamShieldAI.AccountSession"
    private let keychainAccount = "account-jwt"
    private let sessionServerKey = "scamShield.sessionServerURL"
    private(set) var token: String?
    private(set) var user: User?

    private init() {
        token = UserDefaults.standard.string(forKey: sessionServerKey) == Constants.apiBaseURL ? readToken() : nil
    }

    var isAuthenticated: Bool { token != nil && user != nil }
    var isSignedIn: Bool { isAuthenticated && user?.role == "admin" }

    func signIn(account: String, password: String, adminOnly: Bool = false) async throws {
        let credentials = ["email": account.trimmingCharacters(in: .whitespacesAndNewlines), "password": password]
        let data = try await send(path: adminOnly ? "/admin/login" : "/login", method: "POST", payload: credentials, authenticated: false)
        let response = try JSONDecoder().decode(LoginResponse.self, from: data)
        guard !adminOnly || response.user.role == "admin" else {
            throw APIError.server(message: L10n.text("Tài khoản này không có quyền quản trị."))
        }
        try storeToken(response.token)
        UserDefaults.standard.set(Constants.apiBaseURL, forKey: sessionServerKey)
        token = response.token
        user = response.user
        NotificationCenter.default.post(name: Self.didChange, object: nil)
    }

    func restore() async throws {
        guard token != nil else { return }
        do {
            let data = try await send(path: "/me")
            let verified = try JSONDecoder().decode(User.self, from: data)
            user = verified
            NotificationCenter.default.post(name: Self.didChange, object: nil)
        } catch {
            // Keep the keychain entry during a temporary network outage.
            throw error
        }
    }

    func signOut() {
        token = nil
        user = nil
        SecItemDelete(keychainQuery() as CFDictionary)
        UserDefaults.standard.removeObject(forKey: sessionServerKey)
        NotificationCenter.default.post(name: Self.didChange, object: nil)
    }

    func rows(path: String) async throws -> [[String: Any]] {
        let data = try await send(path: path)
        guard let rows = try JSONSerialization.jsonObject(with: data) as? [[String: Any]] else {
            throw APIError.invalidResponse
        }
        return rows
    }

    func post(path: String, payload: [String: Any] = [:]) async throws -> [String: Any] {
        let data = try await send(path: path, method: "POST", payload: payload)
        guard let object = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            throw APIError.invalidResponse
        }
        return object
    }

    private func send(path: String, method: String = "GET", payload: [String: Any]? = nil,
                      authenticated: Bool = true) async throws -> Data {
        guard let url = Constants.apiURL(path: path) else { throw APIError.invalidURL }
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.timeoutInterval = path == "/model-evaluations/run" ? 120 : 30
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        if authenticated {
            guard let token else { throw APIError.server(message: L10n.choose("Vui lòng đăng nhập tài khoản.", "Please sign in.")) }
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        if let payload {
            guard JSONSerialization.isValidJSONObject(payload) else { throw APIError.invalidResponse }
            request.httpBody = try JSONSerialization.data(withJSONObject: payload)
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        }
        let data: Data
        let response: URLResponse
        do { (data, response) = try await URLSession.shared.data(for: request) }
        catch { throw APIError.transport(error) }
        guard let http = response as? HTTPURLResponse else { throw APIError.invalidResponse }
        guard (200...299).contains(http.statusCode) else {
            if http.statusCode == 401 && authenticated { signOut() }
            let detail = (try? JSONSerialization.jsonObject(with: data) as? [String: Any])?["detail"] as? String
            throw APIError.server(message: detail ?? L10n.choose("Máy chủ trả về lỗi \(http.statusCode).", "Server error \(http.statusCode)."))
        }
        return data
    }

    private func keychainQuery() -> [String: Any] {
        [kSecClass as String: kSecClassGenericPassword,
         kSecAttrService as String: keychainService,
         kSecAttrAccount as String: keychainAccount]
    }

    private func readToken() -> String? {
        var query = keychainQuery()
        query[kSecReturnData as String] = true
        query[kSecMatchLimit as String] = kSecMatchLimitOne
        var item: CFTypeRef?
        guard SecItemCopyMatching(query as CFDictionary, &item) == errSecSuccess,
              let data = item as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }

    private func storeToken(_ value: String) throws {
        SecItemDelete(keychainQuery() as CFDictionary)
        var query = keychainQuery()
        query[kSecValueData as String] = Data(value.utf8)
        query[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else {
            throw APIError.server(message: L10n.choose("Không thể lưu phiên đăng nhập an toàn trên thiết bị (Keychain: \(status)).",
                                                       "Could not securely store the session (Keychain: \(status))."))
        }
    }
}

private struct LoginResponse: Decodable {
    let token: String
    let user: User
}
