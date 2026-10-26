# Vietnamese SMS scam dataset

Đặt các file dữ liệu tin nhắn tiếng Việt vào thư mục này, ưu tiên:

- `full_dataset.csv`: toàn bộ dữ liệu để kiểm tra và làm sạch.
- `train.csv`: tập huấn luyện.
- `test.csv`: tập kiểm tra độc lập.

Tối thiểu CSV phải có hai cột:

```text
message,label
```

Trong đó `label = 0` là tin hợp lệ và `label = 1` là spam/lừa đảo. Không đưa
vào dữ liệu còn tên thật, số điện thoại, CCCD, tài khoản ngân hàng hoặc thông
tin cá nhân chưa được ẩn danh.

Thư mục này mới là nơi nhận dữ liệu. Pipeline huấn luyện model NLP tiếng Việt
sẽ được bổ sung riêng; việc chép CSV vào đây chưa tự động làm thay đổi Risk
Engine đang chạy.
