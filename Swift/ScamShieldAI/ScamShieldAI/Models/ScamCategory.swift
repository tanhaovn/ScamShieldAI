import Foundation

struct ScamCategory: Decodable, Hashable {
    let id: Int
    let code: String
    let displayName: String
    let description: String?

    // MARK: - Coding Keys

    enum CodingKeys: String, CodingKey {
        case id
        case code
        case displayName = "display_name"
        case description
    }
}
