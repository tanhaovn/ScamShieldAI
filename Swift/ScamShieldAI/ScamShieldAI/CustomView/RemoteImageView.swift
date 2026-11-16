import UIKit

final class RemoteImageView: UIImageView {

    // MARK: - Properties

    private static let imageCache = NSCache<NSURL, UIImage>()
    private var imageTask: Task<Void, Never>?
    private var representedURL: URL?

    // MARK: - Lifecycle

    deinit {
        imageTask?.cancel()
    }

    // MARK: - Image Loading

    func load(
        url: URL?,
        placeholder: UIImage? = UIImage(systemName: "photo"),
        completion: ((Bool) -> Void)? = nil
    ) {
        imageTask?.cancel()
        representedURL = url
        image = placeholder

        guard let url else {
            completion?(false)
            return
        }
        if url.isFileURL {
            let localImage = UIImage(contentsOfFile: url.path)
            image = localImage ?? placeholder
            completion?(localImage != nil)
            return
        }

        if let cachedImage = Self.imageCache.object(forKey: url as NSURL) {
            image = cachedImage
            completion?(true)
            return
        }

        imageTask = Task { [weak self] in
            guard let self else { return }

            do {
                let (data, response) = try await URLSession.shared.data(from: url)
                guard !Task.isCancelled, representedURL == url else { return }
                guard let httpResponse = response as? HTTPURLResponse,
                      200...299 ~= httpResponse.statusCode,
                      let downloadedImage = UIImage(data: data) else {
                    completion?(false)
                    return
                }

                // Cache tránh tải lại cùng một thumbnail khi table cell được tái sử dụng.
                Self.imageCache.setObject(downloadedImage, forKey: url as NSURL)
                image = downloadedImage
                completion?(true)
            } catch {
                guard !Task.isCancelled, representedURL == url else { return }
                // Báo thất bại để cell giải thích rõ vì sao ảnh không hiển thị.
                completion?(false)
            }
        }
    }

    func cancelLoading() {
        imageTask?.cancel()
        representedURL = nil
    }
}
