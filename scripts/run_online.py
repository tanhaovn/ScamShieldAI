import os
import sys
import time
import re
import shutil
import subprocess
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

print("1. Kiem tra Frontend...", flush=True)
dist_file = ROOT / "frontend-react" / "dist" / "index.html"
if not dist_file.exists():
    print("   Dang build Frontend lan dau...", flush=True)
    subprocess.run(
        ["cmd.exe", "/c", "npm.cmd run build"],
        cwd=ROOT / "frontend-react",
        capture_output=True,
        text=True,
    )
else:
    print("   Frontend da san sang!", flush=True)

print("2. Khoi dong Backend FastAPI tai cong 8000...", flush=True)

backend_env = os.environ.copy()
backend_env["USE_VLM_ANALYZER"] = "true"
backend_env["VLM_MODEL_ID"] = "HuggingFaceTB/SmolVLM-500M-Instruct"
backend_env["VLM_DEVICE"] = "auto"
backend_env["VLM_LOCAL_FILES_ONLY"] = "true"
backend_env["VLM_MAX_NEW_TOKENS"] = "140"
backend_env["HF_HUB_OFFLINE"] = "1"
backend_env["TRANSFORMERS_OFFLINE"] = "1"

python_exe = ROOT / ".venv" / "Scripts" / "python.exe"
if not python_exe.exists():
    python_exe = sys.executable

backend_proc = subprocess.Popen(
    [str(python_exe), "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd=ROOT,
    env=backend_env,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

time.sleep(2)

print("3. Khoi dong Cloudflare Tunnel tao link HTTPS...", flush=True)
local_cloudflared = ROOT / "cloudflared.exe"
cloudflared_exe = (
    str(local_cloudflared)
    if local_cloudflared.exists()
    else shutil.which("cloudflared")
)
if not cloudflared_exe:
    print("[LOI] Chua cai cloudflared hoac cloudflared chua co trong PATH!")
    print("Tai va cai dat tai: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/")
    backend_proc.terminate()
    sys.exit(1)

cf_proc = subprocess.Popen(
    [cloudflared_exe, "tunnel", "--url", "http://127.0.0.1:8000"],
    cwd=ROOT,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding="utf-8",
    errors="replace",
)

tunnel_url = None
start_time = time.time()
while time.time() - start_time < 30:
    line = cf_proc.stdout.readline()
    if not line:
        continue
    match = re.search(r"(https://[a-zA-Z0-9-]+\.trycloudflare\.com)", line)
    if match:
        tunnel_url = match.group(1)
        break

if tunnel_url:
    print("\n" + "=" * 65)
    print(f"Link website: {tunnel_url}")
    print("=" * 65)


    try:
        webbrowser.open(tunnel_url)
    except Exception:
        pass

    try:
        cf_proc.wait()
    except KeyboardInterrupt:
        print("\nDang tat he thong...")
else:
    print("[LOI] Khong the lay duong link tu Cloudflare Tunnel trong 30 giay.")

if backend_proc.poll() is None:
    backend_proc.terminate()
if cf_proc.poll() is None:
    cf_proc.terminate()
