import Foundation

enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case server(message: String)
    case encoding(Error)
    case decoding(Error)
    case transport(Error)

    // MARK: - User-facing Message

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return L10n.text("Địa chỉ máy chủ không hợp lệ.")
        case .invalidResponse:
            return L10n.text("Máy chủ trả về phản hồi không hợp lệ.")
        case .server(let message):
            return message
        case .encoding:
            return L10n.text("Không thể chuẩn bị dữ liệu để gửi lên máy chủ.")
        case .decoding:
            return L10n.text("Không thể đọc dữ liệu trả về từ máy chủ.")
        case .transport(let error):
            return L10n.choose("Không thể kết nối máy chủ: \(error.localizedDescription)", "Could not connect to server: \(error.localizedDescription)")
        }
    }
}

struct APIErrorResponse: Decodable {
    let detail: String
}
