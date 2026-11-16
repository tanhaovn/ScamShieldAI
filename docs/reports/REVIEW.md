# Code Review

## Pham vi

Review nhanh backend FastAPI, authentication va luong upload anh duoc mo ta
trong README va cac test hien co.

## Findings

### High - Secret va tai khoan admin mac dinh

- `backend/app/main.py` dung `dev-secret-key-change-me` lam gia tri mac dinh
  cho `JWT_SECRET`.
- `seed_default_categories()` tao tai khoan
  `admin@scamdetector.local` voi mat khau `Admin@123`.

Neu cau hinh moi truong bi thieu khi deploy, token co the bi forge va tai
khoan admin co the bi dang nhap bang thong tin da duoc commit trong source.

**De xuat:** fail-fast khi `JWT_SECRET` thieu trong production; dua thong tin
admin vao quy trinh bootstrap an toan, bat buoc doi mat khau lan dau va khong
seed mat khau co dinh.

### Medium - Upload file can gioi han o lop API

Endpoint `/check-image` nhan `UploadFile`; can xac minh dung loai file, kich
thuoc toi da va ten file truoc khi luu vao `uploads/`. Khong nen tin vao
`content_type` do client gui; nen doc magic bytes va tao ten file server-side.

**De xuat:** gioi han request body, cho phep mot tap dinh dang anh ro rang,
chan file qua lon/anh loi, va luu file ngoai thu muc static neu khong can phuc
vu truc tiep.

### Medium - Test dang phu thuoc trang thai database

`tests/test_check_image_local.py` xoa va tao lai user admin truc tiep trong
`SessionLocal`. Cac test co the anh huong lan nhau va khong tao database rieng
cho moi test, nen ket qua co the phu thuoc thu tu chay.

**De xuat:** dung fixture database ly lap, reset transaction sau moi test va
khong dung du lieu runtime/mac dinh lam tien dieu kien.

## Diem dang co

- Password duoc hash bang PBKDF2-HMAC-SHA256 voi salt ngau nhien.
- JWT co truong het han (`exp`) va endpoint protected kiem tra user ton tai.
- Test hien co bao phu dang ky/dang nhap, upload anh co ban va mot so admin
  endpoint.

## Uu tien xu ly

1. Loai bo secret va credential mac dinh khoi production path.
2. Bo sung validation va gioi han cho upload.
3. Tach database test khoi database runtime va bo sung test cho authorization,
   file khong hop le, file qua lon va token het han.