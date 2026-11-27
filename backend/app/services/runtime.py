import os

from backend.app.core.config import APP_ENV, APP_VERSION, PROJECT_ROOT, STARTED_AT
from backend.app.db.database import engine


def read_git_commit() -> str:
    """Resolve a short revision without invoking Git in a request handler."""
    configured = (os.getenv("GIT_COMMIT") or os.getenv("RENDER_GIT_COMMIT") or "").strip()
    if configured:
        return configured[:12]
    try:
        git_dir = PROJECT_ROOT / ".git"
        if git_dir.is_file():
            target = git_dir.read_text(encoding="utf-8").strip().removeprefix("gitdir: ")
            git_dir = (PROJECT_ROOT / target).resolve()
        head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
        if not head.startswith("ref: "):
            return head[:12]
        ref_name = head.removeprefix("ref: ")
        ref_file = git_dir / ref_name
        if ref_file.exists():
            return ref_file.read_text(encoding="utf-8").strip()[:12]
        packed = git_dir / "packed-refs"
        if packed.exists():
            for line in packed.read_text(encoding="utf-8").splitlines():
                if line.endswith(f" {ref_name}"):
                    return line.split(" ", 1)[0][:12]
    except (OSError, ValueError):
        pass
    return "unknown"


GIT_COMMIT = read_git_commit()


def runtime_info() -> dict:
    return {
        "status": "ok",
        "app_version": APP_VERSION,
        "git_commit": GIT_COMMIT,
        "environment": APP_ENV,
        "started_at": STARTED_AT.isoformat(),
        "services": {
            "database": engine.url.get_backend_name(),
            "image_model": (PROJECT_ROOT / "models" / "phishing_resnet18.pt").exists(),
            "url_model": (PROJECT_ROOT / "models" / "phishvn_url_histgb.joblib").exists(),
            "safe_browsing": bool(os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "").strip()),
        },
    }
