import Foundation

final class APIClient {

    // MARK: - Dependencies

    private let session: URLSession
    private let encoder: JSONEncoder
    private let decoder: JSONDecoder

    // MARK: - Initialization

    init(session: URLSession = .shared) {
        self.session = session
        self.encoder = JSONEncoder()
        self.decoder = JSONDecoder()
    }

    // MARK: - Public Requests

    func request<Response: Decodable>(
        endpoint: APIEndpoint
    ) async throws -> Response {
        let request = try await makeRequest(endpoint: endpoint, body: nil)
        return try await send(request)
    }

    func request<Response: Decodable, Body: Encodable>(
        endpoint: APIEndpoint,
        body: Body
    ) async throws -> Response {
        let bodyData: Data

        do {
            bodyData = try encoder.encode(body)
        } catch {
            throw APIError.encoding(error)
        }

        let request = try await makeRequest(
            endpoint: endpoint,
            body: bodyData,
            contentType: "application/json"
        )
        return try await send(request)
    }

    func upload<Response: Decodable>(
        endpoint: APIEndpoint,
        imageData: Data,
        filename: String,
        mimeType: String,
        fields: [String: String] = [:]
    ) async throws -> Response {
        var form = MultipartFormDataBuilder()

        fields.forEach { name, value in
            form.addField(name: name, value: value)
        }
        form.addFile(
            name: "file",
            filename: filename,
            mimeType: mimeType,
            data: imageData
        )

        let request = try await makeRequest(
            endpoint: endpoint,
            body: form.finalizedData(),
            contentType: form.contentType
        )
        return try await send(request)
    }
}

// MARK: - Request Builder

private extension APIClient {

    func makeRequest(
        endpoint: APIEndpoint,
        body: Data?,
        contentType: String? = nil
    ) async throws -> URLRequest {
        guard let url = Constants.apiURL(path: endpoint.path) else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = endpoint.method.rawValue
        request.timeoutInterval = endpoint.timeoutInterval
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        if let token = await MainActor.run(body: { AccountSession.shared.token }) {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body {
            request.httpBody = body
            request.setValue(contentType, forHTTPHeaderField: "Content-Type")
        }

        return request
    }
}

// MARK: - Response Handler

private extension APIClient {

    func send<Response: Decodable>(_ request: URLRequest) async throws -> Response {
        let data: Data
        let response: URLResponse

        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw APIError.transport(error)
        }

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard 200...299 ~= httpResponse.statusCode else {
            let serverError = try? decoder.decode(APIErrorResponse.self, from: data)
            throw APIError.server(
                message: serverError?.detail ?? L10n.choose("Máy chủ gặp lỗi (\(httpResponse.statusCode)).", "Server error (\(httpResponse.statusCode)).")
            )
        }

        do {
            return try decoder.decode(Response.self, from: data)
        } catch {
            throw APIError.decoding(error)
        }
    }
}
