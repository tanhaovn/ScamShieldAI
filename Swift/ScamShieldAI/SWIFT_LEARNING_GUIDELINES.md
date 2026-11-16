# Quy ước vừa học vừa code Swift/UIKit

## 1. Mục tiêu

Tài liệu này quy định cách hỗ trợ tôi trong quá trình vừa học vừa xây dựng ứng dụng bằng Swift và UIKit.

Mục tiêu chính:

- Tôi cần hiểu code, không chỉ nhận code hoàn chỉnh để sao chép.
- Code phải bám theo format và kiến trúc hiện có của dự án.
- Mỗi phần cần được giải thích bằng ngôn ngữ đơn giản.
- Sau mỗi phần code, hãy đặt câu hỏi để tôi tự trả lời và kiểm tra mức độ hiểu bài.
- Ưu tiên cách viết rõ ràng, phù hợp với người đang học Swift/UIKit.

## 2. Quy trình trước khi viết code

Trước khi bắt đầu một tính năng hoặc thay đổi quan trọng, hãy:

1. Đọc các file liên quan trong dự án.
2. Tóm tắt ngắn luồng code hiện tại.
3. Nói rõ phần nào sẽ được thêm hoặc sửa.
4. Đưa ra từ 2 đến 4 câu hỏi ngắn để xác nhận yêu cầu và giúp tôi suy nghĩ về cách triển khai.
5. Nếu có nhiều cách làm, hãy trình bày các lựa chọn và giải thích ưu, nhược điểm.

Ví dụ câu hỏi:

- Dữ liệu của màn hình này sẽ lấy từ API hay JSON local?
- Bạn muốn màn hình được viết hoàn toàn bằng code hay dùng XIB?
- Khi API lỗi, giao diện nên hiện alert, empty state hay nút thử lại?
- Bạn nghĩ vì sao cần dùng `[weak self]` trong closure này?

Nếu thay đổi nhỏ và yêu cầu đã rõ, có thể bắt đầu code ngay nhưng vẫn phải giải thích sau khi hoàn thành.

## 3. Format code Swift/UIKit

Code mới cần bám theo phong cách đang có trong dự án:

- Chia rõ Model, View, ViewController, Networking và Service.
- UI cập nhật trên main thread.
- Dùng `weak self` trong closure bất đồng bộ khi phù hợp.
- Ưu tiên `private` cho thuộc tính và hàm chỉ dùng nội bộ.
- Tránh force unwrap (`!`) nếu dữ liệu có thể không hợp lệ.
- Tránh magic number; đưa các giá trị layout vào `Layout` hoặc hằng số có tên rõ ràng.
- Tách các hàm như `setupHierarchy()`, `setupConstraints()`, `configureAppearance()` và `bindData()`.
- Giữ ViewController gọn; networking và xử lý dữ liệu nên được tách ra khi bắt đầu phức tạp.
- Các tiện ích dùng lại ở nhiều màn hình phải được tách thành file riêng trong thư mục `Extension`.

## 4. Quy tắc về thư mục `Extension`

Project cần có thư mục `Extension` để chứa các phần mở rộng dùng chung. Không đặt extension dài hoặc được sử dụng ở nhiều nơi bên trong một ViewController.

Cấu trúc khuyến nghị:

```text
ProductApp/
├── Extension/
│   ├── Extension+UITableView.swift
│   ├── Extension+UICollectionView.swift
│   ├── Extension+UIImageView.swift
│   ├── Extension+Double.swift
│   └── Extension+UIView.swift
├── Models/
├── Networking/
├── Scenes/
└── CustomView/
```

Các file extension thường cần:

- `Extension+UITableView.swift`: đăng ký và dequeue cell/header bằng generic.
- `Extension+UICollectionView.swift`: đăng ký và dequeue collection cell bằng generic.
- `Extension+UIImageView.swift`: tải ảnh hoặc gọi `ImageLoader` dùng chung.
- `Extension+Double.swift`: format giá tiền, số thập phân hoặc phần trăm.
- `Extension+UIView.swift`: tiện ích bo góc, shadow hoặc thêm nhiều subview nếu thật sự được dùng lại.

Quy tắc khi tạo extension:

- Mỗi extension chỉ nên có một trách nhiệm rõ ràng.
- Tên file phải cho biết type được mở rộng.
- Không đưa logic nghiệp vụ của một màn hình cụ thể vào `Extension`.
- Không tạo extension chỉ để chứa một dòng code dùng đúng một lần.
- Các hàm có thể gây crash như generic dequeue phải có thông báo lỗi rõ ràng.
- Nếu project đã có extension tương đương, phải tái sử dụng thay vì tạo bản trùng lặp.
- Extension tải ảnh phải xử lý cell reuse và nên dùng cache nếu ảnh được tải nhiều lần.

Ví dụ extension cho `UITableView`:

```swift
import UIKit

// MARK: - Reusable

protocol Reusable {
    static var reuseIdentifier: String { get }
}

extension Reusable {
    static var reuseIdentifier: String {
        String(describing: Self.self)
    }
}

extension UITableViewCell: Reusable {}

// MARK: - Register and Dequeue

extension UITableView {

    func registerCell<T: UITableViewCell>(_ cellType: T.Type) {
        register(cellType, forCellReuseIdentifier: T.reuseIdentifier)
    }

    func registerNibCell<T: UITableViewCell>(_ cellType: T.Type) {
        let nib = UINib(nibName: T.reuseIdentifier, bundle: nil)
        register(nib, forCellReuseIdentifier: T.reuseIdentifier)
    }

    func dequeueCell<T: UITableViewCell>(for indexPath: IndexPath) -> T {
        guard let cell = dequeueReusableCell(
            withIdentifier: T.reuseIdentifier,
            for: indexPath
        ) as? T else {
            fatalError("Không thể dequeue cell: \(T.reuseIdentifier)")
        }

        return cell
    }
}
```

Ví dụ extension format tiền:

```swift
import Foundation

// MARK: - Currency Formatting

extension Double {

    var formattedCurrency: String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.currencyCode = "USD"

        return formatter.string(from: NSNumber(value: self)) ?? "$\(self)"
    }
}
```

Khi thêm một extension mới, phần giải thích sau khi code phải trả lời được:

1. Extension này giải quyết sự lặp lại nào?
2. Những file nào đang sử dụng nó?
3. Vì sao logic này phù hợp để dùng chung?
4. Có rủi ro crash, memory leak hoặc cell reuse nào không?

## 5. Quy tắc sử dụng `// MARK: -`

Mỗi phần chức năng trong một file Swift phải được chia bằng `// MARK: -`.

Format khuyến nghị:

```swift
final class ProductViewController: UIViewController {

    // MARK: - Constants

    private enum Layout {
        static let horizontalPadding: CGFloat = 16
        static let itemSpacing: CGFloat = 12
    }

    // MARK: - Properties

    private var products: [Product] = []

    // MARK: - UI Components

    private let tableView: UITableView = {
        let tableView = UITableView(frame: .zero, style: .plain)
        tableView.translatesAutoresizingMaskIntoConstraints = false
        return tableView
    }()

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        configureAppearance()
        setupHierarchy()
        setupConstraints()
    }
}

// MARK: - Setup UI

private extension ProductViewController {

    func configureAppearance() {
        view.backgroundColor = .systemBackground
    }

    func setupHierarchy() {
        view.addSubview(tableView)
    }

    func setupConstraints() {
        NSLayoutConstraint.activate([
            tableView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            tableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            tableView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
    }
}

// MARK: - UITableViewDataSource

extension ProductViewController: UITableViewDataSource {
    // Data source methods
}

// MARK: - UITableViewDelegate

extension ProductViewController: UITableViewDelegate {
    // Delegate methods
}
```

Các nhóm `MARK` thường dùng:

- `// MARK: - Constants`
- `// MARK: - Properties`
- `// MARK: - UI Components`
- `// MARK: - Initialization`
- `// MARK: - Lifecycle`
- `// MARK: - Setup UI`
- `// MARK: - Configuration`
- `// MARK: - Data Loading`
- `// MARK: - Actions`
- `// MARK: - Helpers`
- `// MARK: - UITableViewDataSource`
- `// MARK: - UITableViewDelegate`
- `// MARK: - UICollectionViewDataSource`
- `// MARK: - UICollectionViewDelegateFlowLayout`

Không cần tạo `MARK` cho một nhóm chỉ có một dòng không đáng kể. Mục tiêu là giúp file dễ đọc, không phải làm code dài hơn một cách máy móc.

## 6. Quy tắc viết chú thích

Chỉ chú thích những đoạn có khả năng được hỏi hoặc khó hiểu với người mới học. Không chú thích lại những gì code đã nói rõ.

Nên chú thích:

- Vì sao dùng `[weak self]`.
- Vì sao UI phải cập nhật trên main thread.
- Cách hoạt động của delegate và data source.
- Cách cell reuse ảnh hưởng đến việc tải ảnh bất đồng bộ.
- Ý nghĩa của generic register/dequeue.
- Cách Auto Layout xác định kích thước và vị trí.
- Vì sao dùng `guard`, optional binding hoặc early return.
- Luồng gọi API, decode JSON và xử lý lỗi.
- Những quyết định kiến trúc có nhiều cách triển khai.

Ví dụ:

```swift
ProductService.shared.fetchProducts { [weak self] result in
    // Dùng weak self để closure không giữ ViewController sau khi màn hình đã đóng.
    guard let self else { return }

    // APIClient trả completion trên main thread nên có thể cập nhật UI tại đây.
    self.activityIndicator.stopAnimating()
}
```

Không nên chú thích dư thừa:

```swift
// Đặt màu nền thành trắng
view.backgroundColor = .white
```

Ưu tiên chú thích giải thích **tại sao**, thay vì chỉ mô tả **code đang làm gì**.

## 7. Cách trình bày khi hoàn thành một phần code

Sau khi hoàn thành mỗi phần, hãy trả lời theo cấu trúc:

### Đã làm gì?

Tóm tắt ngắn các file đã thêm hoặc sửa và kết quả đạt được.

### Luồng code hoạt động thế nào?

Giải thích theo thứ tự chạy, ví dụ:

```text
ViewController xuất hiện
→ gọi ProductService
→ APIClient gửi request
→ JSON được decode thành ProductResponse
→ cập nhật mảng products
→ reload CollectionView
```

### Kiến thức Swift/UIKit cần nhớ

Giải thích các khái niệm mới xuất hiện như:

- Optional
- Closure
- Delegate
- Protocol
- Generic
- Auto Layout
- Cell reuse
- Memory management

### Câu hỏi dành cho tôi

Đặt từ 3 đến 5 câu hỏi, đi từ dễ đến khó. Chưa đưa đáp án ngay để tôi có cơ hội tự trả lời.

Ví dụ:

1. Vì sao `UITableView` cần `dataSource`?
2. `dequeueReusableCell` giúp tối ưu bộ nhớ như thế nào?
3. Điều gì có thể xảy ra nếu tải ảnh bất đồng bộ nhưng không kiểm tra cell reuse?
4. Vì sao closure gọi API thường dùng `[weak self]`?
5. Nếu API trả lỗi, bạn muốn trạng thái UI được xử lý ở lớp nào?

Sau khi tôi trả lời:

- Nhận xét từng câu.
- Giải thích lại phần chưa đúng bằng ví dụ ngắn.
- Đưa ra một bài tập nhỏ nếu cần.
- Không chỉ nói “đúng” hoặc “sai” mà phải giải thích lý do.

## 8. Khi sửa lỗi

Khi gặp bug, không sửa âm thầm. Hãy trình bày:

1. Triệu chứng của lỗi.
2. Nguyên nhân gốc.
3. Cách kiểm tra hoặc tái hiện.
4. Cách sửa.
5. Vì sao cách sửa hoạt động.
6. Một hoặc hai câu hỏi để tôi tự giải thích lại lỗi.

Ví dụ câu hỏi:

- Vì sao force unwrap URL có thể làm ứng dụng crash?
- Tại sao ảnh có thể xuất hiện nhầm khi table cell được tái sử dụng?
- `guard let` khác `if let` như thế nào trong trường hợp này?

## 9. Khi có nhiều cách triển khai

Nếu một tính năng có nhiều giải pháp, hãy:

- Đưa ra tối đa 2 hoặc 3 phương án phù hợp.
- Giải thích phương án dễ học nhất.
- Giải thích phương án phù hợp production hơn.
- Cho tôi lựa chọn trước khi thực hiện nếu sự khác biệt ảnh hưởng lớn đến kiến trúc.

Ví dụ:

- UIKit bằng code hay XIB.
- Completion handler hay `async/await`.
- MVC hiện tại hay tách ViewModel.
- `URLSession` trực tiếp hay tạo networking layer.

## 10. Mức độ hỗ trợ mong muốn

- Không viết lại toàn bộ project nếu chỉ cần sửa một phần nhỏ.
- Không sử dụng thư viện bên ngoài nếu UIKit/Foundation đã đáp ứng được yêu cầu, trừ khi đã giải thích lý do.
- Không thay đổi kiến trúc lớn mà chưa thông báo.
- Giữ tên biến và hàm rõ nghĩa.
- Code phải compile được trong phạm vi có thể kiểm tra.
- Luôn nói rõ phần nào đã kiểm tra và phần nào chưa thể kiểm tra.
- Sau mỗi tính năng, đề xuất một bài tập nhỏ để tôi tự sửa hoặc mở rộng code.

## 11. Mẫu yêu cầu ngắn có thể sử dụng

```text
Hãy hỗ trợ tôi vừa học vừa code Swift/UIKit theo file SWIFT_LEARNING_GUIDELINES.md.

Trước khi code, hãy đọc các file liên quan và hỏi tôi những câu cần thiết.
Khi code, chia file bằng // MARK: - và chú thích các đoạn dễ bị hỏi.
Sau khi hoàn thành, giải thích luồng chạy, kiến thức cần nhớ và đặt câu hỏi để tôi tự trả lời.
```
