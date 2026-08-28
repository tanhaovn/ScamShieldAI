from io import BytesIO

from PIL import Image
from fastapi.testclient import TestClient

from backend.app.main import app


buffer = BytesIO()
img = Image.new("RGB", (128, 128), color=(255, 255, 255))
img.save(buffer, format="JPEG")
buffer.seek(0)

with TestClient(app) as client:
    response = client.post(
        "/check-image",
        files={"file": ("sample.jpg", buffer.read(), "image/jpeg")},
        data={"user_id": 1},
    )

print("status_code=", response.status_code)
print(response.json())
