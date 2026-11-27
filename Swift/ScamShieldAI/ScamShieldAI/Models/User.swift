import Foundation

struct User: Codable {
    let id: Int
    let email: String
    let fullName: String?
    let role: String

    static let guest = User(id: 0, email: "", fullName: L10n.text("bạn"), role: "guest")

    // MARK: - Coding Keys

    enum CodingKeys: String, CodingKey {
        case id
        case email
        case fullName = "full_name"
        case role
    }
}
