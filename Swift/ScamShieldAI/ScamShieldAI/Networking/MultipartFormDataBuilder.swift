import Foundation

struct MultipartFormDataBuilder {

    // MARK: - Properties

    let boundary = "Boundary-\(UUID().uuidString)"
    private var body = Data()

    var contentType: String {
        "multipart/form-data; boundary=\(boundary)"
    }

    // MARK: - Add Parts

    mutating func addField(name: String, value: String) {
        append("--\(boundary)\r\n")
        append("Content-Disposition: form-data; name=\"\(name)\"\r\n\r\n")
        append("\(value)\r\n")
    }

    mutating func addFile(
        name: String,
        filename: String,
        mimeType: String,
        data: Data
    ) {
        append("--\(boundary)\r\n")
        append(
            "Content-Disposition: form-data; name=\"\(name)\"; "
                + "filename=\"\(filename)\"\r\n"
        )
        append("Content-Type: \(mimeType)\r\n\r\n")
        body.append(data)
        append("\r\n")
    }

    mutating func finalizedData() -> Data {
        append("--\(boundary)--\r\n")
        return body
    }
}

// MARK: - Private Helpers

private extension MultipartFormDataBuilder {

    mutating func append(_ string: String) {
        guard let data = string.data(using: .utf8) else { return }
        body.append(data)
    }
}
