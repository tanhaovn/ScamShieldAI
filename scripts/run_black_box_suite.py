"""Black-box HTTP regression suite for a running Scam Detector service.

The suite talks only to public HTTP endpoints. It does not import application
modules, so failures reflect the same boundary used by browsers and API clients.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sys
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "images"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


@dataclass
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes
    elapsed_ms: float

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


@dataclass
class CaseResult:
    name: str
    group: str
    passed: bool
    expected: str
    actual: str
    status: int | None
    elapsed_ms: float
    error: str = ""


def request(
    base_url: str,
    method: str,
    path: str,
    *,
    json_body: Any | None = None,
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 180.0,
) -> HttpResponse:
    request_headers = dict(headers or {})
    if json_body is not None:
        body = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    started = time.perf_counter()
    req = Request(base_url.rstrip("/") + path, data=body, headers=request_headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as response:
            payload = response.read()
            return HttpResponse(
                status=response.status,
                headers={key.lower(): value for key, value in response.headers.items()},
                body=payload,
                elapsed_ms=round((time.perf_counter() - started) * 1000, 2),
            )
    except HTTPError as error:
        payload = error.read()
        return HttpResponse(
            status=error.code,
            headers={key.lower(): value for key, value in error.headers.items()},
            body=payload,
            elapsed_ms=round((time.perf_counter() - started) * 1000, 2),
        )


def multipart_file(field: str, filename: str, content_type: str, payload: bytes) -> tuple[bytes, str]:
    boundary = "----sfds-black-box-" + uuid.uuid4().hex
    prefix = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field}"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode("utf-8")
    suffix = f"\r\n--{boundary}--\r\n".encode("utf-8")
    return prefix + payload + suffix, f"multipart/form-data; boundary={boundary}"


def upload(
    base_url: str,
    path: str,
    filename: str,
    content_type: str,
    payload: bytes,
    *,
    headers: dict[str, str] | None = None,
    timeout: float = 180.0,
) -> HttpResponse:
    body, multipart_type = multipart_file("file", filename, content_type, payload)
    request_headers = dict(headers or {})
    request_headers["Content-Type"] = multipart_type
    return request(base_url, "POST", path, body=body, headers=request_headers, timeout=timeout)


def summarize(response: HttpResponse) -> str:
    try:
        value = response.json()
    except (UnicodeDecodeError, json.JSONDecodeError):
        return f"HTTP {response.status}, {len(response.body)} bytes"
    if isinstance(value, dict):
        keys = ["risk_level", "risk_score", "detail", "status", "total", "passed", "failed"]
        summary = {key: value[key] for key in keys if key in value}
        return f"HTTP {response.status} {summary or list(value)[:8]}"
    return f"HTTP {response.status} {str(value)[:180]}"


def create_generated_files(temp_dir: Path) -> dict[str, Path]:
    temp_dir.mkdir(parents=True, exist_ok=True)
    files: dict[str, Path] = {}

    for image_format, suffix in (("PNG", ".png"), ("JPEG", ".jpg"), ("WEBP", ".webp")):
        path = temp_dir / f"valid-{image_format.lower()}{suffix}"
        image = Image.new("RGB", (640, 360), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((30, 30, 610, 330), outline="#16815f", width=5)
        draw.text((60, 160), "LICH HOP NOI BO 08:00", fill="black")
        image.save(path, format=image_format)
        files[image_format.lower()] = path

    tiny = temp_dir / "tiny.png"
    Image.new("RGB", (8, 8), "white").save(tiny)
    files["tiny"] = tiny

    huge_dimensions = temp_dir / "too-many-pixels.png"
    Image.new("1", (5001, 5000), 1).save(huge_dimensions, optimize=True)
    files["huge_dimensions"] = huge_dimensions

    gif = temp_dir / "unsupported.gif"
    Image.new("RGB", (64, 64), "white").save(gif, format="GIF")
    files["gif"] = gif

    import fitz

    def make_pdf(name: str, pages: list[str]) -> Path:
        path = temp_dir / name
        document = fitz.open()
        for text in pages:
            page = document.new_page()
            page.insert_text((72, 100), text, fontsize=12)
        document.save(path)
        document.close()
        return path

    files["pdf_safe"] = make_pdf("safe.pdf", ["Lich hop noi bo vao 8 gio sang thu Hai."])
    files["pdf_scam"] = make_pdf(
        "scam.pdf",
        ["Bo Cong an yeu cau chuyen khoan gap 20 trieu de phuc vu dieu tra."],
    )
    files["pdf_truncated"] = make_pdf(
        "eleven-pages.pdf",
        [f"Trang {index}: tai lieu kiem thu noi bo." for index in range(1, 12)],
    )
    files["pdf_blank"] = make_pdf("blank.pdf", [""])
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    parser.add_argument("--admin-email", required=True)
    parser.add_argument("--admin-password", required=True)
    parser.add_argument("--work-dir", type=Path, default=ROOT / ".pytest-work" / "black-box")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    generated = create_generated_files(args.work_dir)
    results: list[CaseResult] = []
    state: dict[str, Any] = {}

    def run_case(
        name: str,
        group: str,
        expected: str,
        action: Callable[[], HttpResponse],
        validate: Callable[[HttpResponse], bool],
    ) -> HttpResponse | None:
        try:
            response = action()
            passed = bool(validate(response))
            results.append(
                CaseResult(
                    name=name,
                    group=group,
                    passed=passed,
                    expected=expected,
                    actual=summarize(response),
                    status=response.status,
                    elapsed_ms=response.elapsed_ms,
                )
            )
            print(f"[{'PASS' if passed else 'FAIL'}] {group} :: {name} ({response.elapsed_ms:.0f} ms)", flush=True)
            return response
        except Exception as error:
            results.append(CaseResult(name, group, False, expected, "exception", None, 0.0, repr(error)))
            print(f"[FAIL] {group} :: {name} - {error!r}", flush=True)
            return None

    def json_post(path: str, payload: Any, headers: dict[str, str] | None = None) -> HttpResponse:
        return request(args.base_url, "POST", path, json_body=payload, headers=headers)

    def json_patch(path: str, payload: Any, headers: dict[str, str] | None = None) -> HttpResponse:
        return request(args.base_url, "PATCH", path, json_body=payload, headers=headers)

    # System boundary and frontend.
    health = run_case(
        "health schema and bundled models",
        "system",
        "200; status=ok; image_model=true; url_model=true",
        lambda: request(args.base_url, "GET", "/health"),
        lambda r: r.status == 200
        and r.json().get("status") == "ok"
        and r.json().get("services", {}).get("image_model") is True
        and r.json().get("services", {}).get("url_model") is True,
    )
    run_case("version endpoint", "system", "200", lambda: request(args.base_url, "GET", "/version"), lambda r: r.status == 200 and bool(r.json().get("app_version")))
    frontend = run_case("frontend index", "system", "200 HTML", lambda: request(args.base_url, "GET", "/"), lambda r: r.status == 200 and b"<html" in r.body.lower())
    if frontend:
        match = re.search(rb'(/assets/[^"\']+)', frontend.body)
        if match:
            asset_path = match.group(1).decode("utf-8")
            run_case("frontend hashed asset", "system", "200 non-empty", lambda p=asset_path: request(args.base_url, "GET", p), lambda r: r.status == 200 and len(r.body) > 100)
    run_case("OpenAPI schema", "system", "200 with paths", lambda: request(args.base_url, "GET", "/openapi.json"), lambda r: r.status == 200 and "/check-image" in r.json().get("paths", {}))
    run_case("Swagger UI", "system", "200 HTML", lambda: request(args.base_url, "GET", "/docs"), lambda r: r.status == 200 and b"swagger" in r.body.lower())
    run_case("unknown route", "system", "404", lambda: request(args.base_url, "GET", "/black-box-not-found"), lambda r: r.status == 404)
    run_case("wrong HTTP method", "system", "405", lambda: request(args.base_url, "GET", "/check-text"), lambda r: r.status == 405)
    run_case(
        "CORS preflight allowed origin",
        "system",
        "200 with allow-origin",
        lambda: request(
            args.base_url,
            "OPTIONS",
            "/check-text",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "POST",
            },
        ),
        lambda r: r.status == 200 and r.headers.get("access-control-allow-origin") == "http://127.0.0.1:5173",
    )
    run_case("categories available", "system", "200 and >=5", lambda: request(args.base_url, "GET", "/scam-categories"), lambda r: r.status == 200 and len(r.json()) >= 5)
    run_case("AI model registry public read", "system", "200 list", lambda: request(args.base_url, "GET", "/ai-models"), lambda r: r.status == 200 and isinstance(r.json(), list))

    # Validation and negative boundary cases.
    run_case("missing JSON field", "validation", "422", lambda: json_post("/check-text", {}), lambda r: r.status == 422)
    run_case("empty text", "validation", "422", lambda: json_post("/check-text", {"text": ""}), lambda r: r.status == 422)
    run_case("text over 20k", "validation", "422", lambda: json_post("/check-text", {"text": "a" * 20001}), lambda r: r.status == 422)
    run_case("invalid URL", "validation", "422", lambda: json_post("/check-url", {"url": "not a valid URL"}), lambda r: r.status == 422)
    run_case("empty URL batch", "validation", "422", lambda: json_post("/check-urls-batch", {"urls": []}), lambda r: r.status == 422)
    run_case("URL batch over 50", "validation", "422", lambda: json_post("/check-urls-batch", {"urls": [f"https://example{i}.com" for i in range(51)]}), lambda r: r.status == 422)
    run_case("missing image multipart", "validation", "422", lambda: request(args.base_url, "POST", "/check-image", body=b"", headers={"Content-Type": "multipart/form-data; boundary=x"}), lambda r: r.status == 422)
    run_case("malformed JSON", "validation", "422", lambda: request(args.base_url, "POST", "/check-text", body=b"{", headers={"Content-Type": "application/json"}), lambda r: r.status == 422)

    # Text classification.
    text_cases = (
        ("safe chat", "Hen ban 8 gio toi nay di uong ca phe nhe.", "an_toan"),
        ("safe prevention warning", "Canh bao an toan: khong bao gio cung cap ma OTP va khong chuyen tien cho nguoi la.", "an_toan"),
        ("safe maintenance", "He thong bao tri luc 01:00. Ban khong can dang nhap hay cung cap mat khau.", "an_toan"),
        ("danger OTP", "Tai khoan bi khoa. Dang nhap ngay va gui ma OTP de xac minh tai khoan trong 2 gio.", "nguy_hiem"),
        ("danger police transfer", "Bo Cong an yeu cau chuyen khoan gap 20 trieu de phuc vu dieu tra.", "nguy_hiem"),
        ("danger job deposit", "Tuyen cong tac vien luong cao. Nap 500.000 dong de lam nhiem vu va nhan hoa hong ngay.", "nguy_hiem"),
    )
    for name, text, expected_level in text_cases:
        run_case(
            name,
            "text",
            f"200 risk_level={expected_level}",
            lambda text=text: json_post("/check-text", {"text": text}),
            lambda r, expected_level=expected_level: r.status == 200 and r.json().get("risk_level") == expected_level and r.json().get("source_type") == "text",
        )

    # URL and batch classification.
    url_cases = (
        ("trusted Google", "https://www.google.com/", "an_toan"),
        ("trusted Microsoft", "https://www.microsoft.com/", "an_toan"),
        ("shortened URL", "https://bit.ly/kiem-tra-tai-khoan", "nghi_ngo"),
        ("IP login URL", "http://192.0.2.10/login", "nghi_ngo"),
        ("brand impersonation URL", "https://google.verify-account-security.top/login", "nguy_hiem"),
        ("punycode URL", "https://xn--googl-fsa.com/login", "nghi_ngo"),
    )
    for name, url, expected_level in url_cases:
        run_case(
            name,
            "url",
            f"200 risk_level={expected_level}",
            lambda url=url: json_post("/check-url", {"url": url}),
            lambda r, expected_level=expected_level: r.status == 200 and r.json().get("risk_level") == expected_level and r.json().get("source_type") == "url",
        )
    run_case(
        "mixed URL batch with duplicate and invalid",
        "url",
        "200 total=3; invalid preserved; duplicate removed",
        lambda: json_post("/check-urls-batch", {"urls": ["https://google.com", "not-a-url", "https://bit.ly/test", "https://google.com"]}),
        lambda r: r.status == 200 and r.json().get("total") == 3 and any(item.get("status") == "invalid" for item in r.json().get("results", [])),
    )
    run_case(
        "analysis assistant grounded response",
        "assistant",
        "200 non-empty answer",
        lambda: json_post(
            "/analysis-assistant",
            {
                "question": "Toi co nen chuyen tien khong?",
                "risk_level": "nguy_hiem",
                "risk_score": 90,
                "highlighted_terms": ["chuyen khoan", "ma OTP"],
                "urls": [],
                "suggested_action": "Khong chuyen tien.",
                "verdict": "Co dau hieu lua dao.",
            },
        ),
        lambda r: r.status == 200 and len(r.json().get("answer", "")) > 20,
    )

    # Authentication and authorization.
    run_case("public registration disabled", "auth", "403", lambda: json_post("/register", {"email": "user@example.test", "password": "Secret123"}), lambda r: r.status == 403)
    run_case("invalid admin login", "auth", "401", lambda: json_post("/login", {"email": args.admin_email, "password": "wrong-password"}), lambda r: r.status == 401)
    run_case("Google auth unavailable without client id", "auth", "503", lambda: json_post("/auth/google", {"credential": "x" * 30}), lambda r: r.status == 503)
    for endpoint in ("/me", "/scan-history", "/training-dataset", "/model-evaluations", "/system-logs", "/scam-keywords", "/scan-feedback"):
        run_case(f"unauthorized {endpoint}", "authorization", "401", lambda endpoint=endpoint: request(args.base_url, "GET", endpoint), lambda r: r.status == 401)

    login = run_case(
        "valid admin login",
        "auth",
        "200 admin token",
        lambda: json_post("/admin/login", {"email": args.admin_email, "password": args.admin_password}),
        lambda r: r.status == 200 and r.json().get("user", {}).get("role") == "admin" and bool(r.json().get("token")),
    )
    auth_headers: dict[str, str] = {}
    if login and login.status == 200:
        state["admin"] = login.json()["user"]
        auth_headers = {"Authorization": f"Bearer {login.json()['token']}"}
    run_case("admin /me", "auth", "200 role=admin", lambda: request(args.base_url, "GET", "/me", headers=auth_headers), lambda r: r.status == 200 and r.json().get("role") == "admin")
    run_case("profile validation", "auth", "422", lambda: json_patch("/me", {"full_name": "x"}, auth_headers), lambda r: r.status == 422)
    run_case("profile update", "auth", "200", lambda: json_patch("/me", {"full_name": "Black Box Admin"}, auth_headers), lambda r: r.status == 200 and r.json().get("full_name") == "Black Box Admin")

    # Admin and feedback persistence (database is restored by the orchestrating run).
    unique = uuid.uuid4().hex[:10]
    keyword_payload = {"keyword": f"blackbox-{unique}", "category": "phishing", "weight": 7}
    run_case("create scam keyword", "admin", "201", lambda: json_post("/scam-keywords", keyword_payload, auth_headers), lambda r: r.status == 201 and bool(r.json().get("id")))
    run_case("duplicate scam keyword", "admin", "409", lambda: json_post("/scam-keywords", keyword_payload, auth_headers), lambda r: r.status == 409)
    run_case("list scam keywords", "admin", "200 list", lambda: request(args.base_url, "GET", "/scam-keywords", headers=auth_headers), lambda r: r.status == 200 and isinstance(r.json(), list))
    model = run_case(
        "create AI model record",
        "admin",
        "200 id",
        lambda: json_post("/ai-models", {"version_name": f"black-box-{unique}", "description": "black-box temporary record", "is_active": True}, auth_headers),
        lambda r: r.status == 200 and bool(r.json().get("id")),
    )
    if model and model.status == 200:
        state["model_id"] = model.json()["id"]
        run_case(
            "create model evaluation",
            "admin",
            "200 id",
            lambda: json_post("/model-evaluations", {"ai_model_id": state["model_id"], "macro_f1": 0.75, "recall": 0.8, "false_alarm_rate": 0.1, "explanation_usefulness": 4.0}, auth_headers),
            lambda r: r.status == 200 and bool(r.json().get("id")),
        )
    run_case("create training dataset record", "admin", "200 id", lambda: json_post("/training-dataset", {"image_url": "/uploads/black-box-placeholder.png", "is_anonymized": True, "is_verified": False}, auth_headers), lambda r: r.status == 200 and bool(r.json().get("id")))
    run_case("create system log", "admin", "200 id", lambda: json_post("/system-logs", {"action_type": "black_box_test", "description": "temporary black-box record"}, auth_headers), lambda r: r.status == 200 and bool(r.json().get("id")))
    run_case("submit anonymous feedback", "feedback", "201 pending", lambda: json_post("/scan-feedback", {"client_scan_id": f"bb-{unique}", "verdict": "correct", "predicted_level": "an_toan", "risk_score": 5, "source_type": "text", "note": "black-box temporary feedback"}), lambda r: r.status == 201 and r.json().get("status") == "pending")
    run_case("admin lists feedback", "feedback", "200 list", lambda: request(args.base_url, "GET", "/scan-feedback", headers=auth_headers), lambda r: r.status == 200 and isinstance(r.json(), list))
    run_case("automated model benchmark", "admin", "200 all 13 pass", lambda: json_post("/model-evaluations/run", {}, auth_headers), lambda r: r.status == 200 and r.json().get("total") == 13 and r.json().get("failed") == 0)

    # PDF documents.
    run_case("document wrong type", "document", "400", lambda: upload(args.base_url, "/check-document", "note.txt", "text/plain", b"hello"), lambda r: r.status == 400)
    run_case("corrupt PDF", "document", "400", lambda: upload(args.base_url, "/check-document", "broken.pdf", "application/pdf", b"not-a-pdf"), lambda r: r.status == 400)
    run_case("blank PDF", "document", "422", lambda: upload(args.base_url, "/check-document", "blank.pdf", "application/pdf", generated["pdf_blank"].read_bytes()), lambda r: r.status == 422)
    run_case("safe text PDF", "document", "200 safe", lambda: upload(args.base_url, "/check-document", "safe.pdf", "application/pdf", generated["pdf_safe"].read_bytes()), lambda r: r.status == 200 and r.json().get("risk_level") == "an_toan" and r.json().get("source_type") == "pdf")
    run_case("scam text PDF", "document", "200 danger", lambda: upload(args.base_url, "/check-document", "scam.pdf", "application/pdf", generated["pdf_scam"].read_bytes()), lambda r: r.status == 200 and r.json().get("risk_level") == "nguy_hiem")
    run_case("PDF limited to ten pages", "document", "200 truncated=true", lambda: upload(args.base_url, "/check-document", "eleven-pages.pdf", "application/pdf", generated["pdf_truncated"].read_bytes()), lambda r: r.status == 200 and r.json().get("document_info", {}).get("processed_pages") == 10 and r.json().get("document_info", {}).get("truncated") is True)
    run_case("PDF over 15 MB", "document", "413", lambda: upload(args.base_url, "/check-document", "large.pdf", "application/pdf", b"x" * (15 * 1024 * 1024 + 1)), lambda r: r.status == 413)

    # Image validation.
    run_case("image wrong MIME", "image-validation", "400", lambda: upload(args.base_url, "/check-image", "note.txt", "text/plain", b"hello"), lambda r: r.status == 400)
    run_case("fake PNG bytes", "image-validation", "400", lambda: upload(args.base_url, "/check-image", "fake.png", "image/png", b"not-an-image"), lambda r: r.status == 400)
    run_case("unsupported GIF", "image-validation", "400", lambda: upload(args.base_url, "/check-image", "unsupported.gif", "image/gif", generated["gif"].read_bytes()), lambda r: r.status == 400)
    run_case("image too small", "image-validation", "400", lambda: upload(args.base_url, "/check-image", "tiny.png", "image/png", generated["tiny"].read_bytes()), lambda r: r.status == 400)
    run_case("image over 25 megapixels", "image-validation", "400", lambda: upload(args.base_url, "/check-image", "huge.png", "image/png", generated["huge_dimensions"].read_bytes()), lambda r: r.status == 400)
    run_case("image over 10 MB", "image-validation", "413", lambda: upload(args.base_url, "/check-image", "large.png", "image/png", b"x" * (10 * 1024 * 1024 + 1)), lambda r: r.status == 413)

    # Supported formats and all checked-in labeled fixtures.
    for key, extension, mime in (("png", "png", "image/png"), ("jpeg", "jpg", "image/jpeg"), ("webp", "webp", "image/webp")):
        run_case(
            f"valid {key.upper()} image",
            "image-format",
            "200 with image metadata",
            lambda key=key, extension=extension, mime=mime: upload(args.base_url, "/check-image", f"valid.{extension}", mime, generated[key].read_bytes()),
            lambda r: r.status == 200 and r.json().get("source_type") == "image" and r.json().get("image_dimensions", {}).get("width") == 640,
        )

    first_guest_image_url = ""
    for expected, folder in (("an_toan", "an_toan_safe"), ("alert", "lua_dao_scam")):
        for path in sorted((FIXTURES / folder).glob("*")):
            response = run_case(
                f"fixture {folder}/{path.name}",
                "image-fixture",
                "200 safe" if expected == "an_toan" else "200 suspicious-or-dangerous",
                lambda path=path: upload(args.base_url, "/check-image", path.name, "image/png", path.read_bytes()),
                lambda r, expected=expected: r.status == 200
                and (
                    r.json().get("risk_level") == "an_toan"
                    if expected == "an_toan"
                    else r.json().get("risk_level") in {"nghi_ngo", "nguy_hiem"}
                ),
            )
            if response and response.status == 200 and not first_guest_image_url:
                first_guest_image_url = response.json().get("image_url", "")
    if first_guest_image_url:
        run_case("uploaded image is retrievable", "image", "200 image bytes", lambda: request(args.base_url, "GET", first_guest_image_url), lambda r: r.status == 200 and len(r.body) > 100)

    admin_image = FIXTURES / "lua_dao_scam" / "04_sms_mao_danh_vietcombank.png"
    admin_scan = run_case(
        "authenticated image scan persists",
        "image",
        "200 storage=database and scan_id",
        lambda: upload(args.base_url, "/check-image", admin_image.name, "image/png", admin_image.read_bytes(), headers=auth_headers),
        lambda r: r.status == 200 and r.json().get("storage") == "database" and bool(r.json().get("scan_id")),
    )
    run_case("admin scan history", "admin", "200 list", lambda: request(args.base_url, "GET", "/scan-history", headers=auth_headers), lambda r: r.status == 200 and isinstance(r.json(), list) and len(r.json()) >= 1)
    if state.get("admin"):
        run_case("admin history by user id", "admin", "200 list", lambda: request(args.base_url, "GET", f"/history/{state['admin']['id']}", headers=auth_headers), lambda r: r.status == 200 and isinstance(r.json(), list))

    # Basic concurrency at the public HTTP boundary.
    def parallel_health() -> list[HttpResponse]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            return list(executor.map(lambda _: request(args.base_url, "GET", "/health"), range(5)))

    def run_parallel_case() -> HttpResponse:
        started = time.perf_counter()
        responses = parallel_health()
        combined = json.dumps([response.status for response in responses]).encode("utf-8")
        return HttpResponse(200 if all(response.status == 200 for response in responses) else 500, {}, combined, round((time.perf_counter() - started) * 1000, 2))

    run_case("five concurrent health requests", "concurrency", "all 200", run_parallel_case, lambda r: r.status == 200 and json.loads(r.body) == [200] * 5)

    passed = sum(result.passed for result in results)
    failed = len(results) - passed
    elapsed_values = sorted(result.elapsed_ms for result in results if result.elapsed_ms > 0)
    p95 = elapsed_values[min(len(elapsed_values) - 1, int(len(elapsed_values) * 0.95))] if elapsed_values else 0.0
    report = {
        "suite": "sfds-live-http-black-box-v1",
        "base_url": args.base_url,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / len(results), 4) if results else 0.0,
        "max_elapsed_ms": max(elapsed_values, default=0.0),
        "p95_elapsed_ms": p95,
        "groups": {
            group: {
                "total": sum(result.group == group for result in results),
                "passed": sum(result.group == group and result.passed for result in results),
            }
            for group in sorted({result.group for result in results})
        },
        "results": [asdict(result) for result in results],
    }
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output, encoding="utf-8")
    print(output, flush=True)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except URLError as error:
        print(f"Cannot reach target service: {error}", file=sys.stderr)
        raise SystemExit(2)
