"""Guest scans must never enter another user's history or retain uploaded files."""
import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from PIL import Image
from starlette.datastructures import Headers, UploadFile

import backend.app.main as main


class GuestScanTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.uploads = Path(self.temp.name)
        self.db = Mock()
        self.analysis = {
            "risk_score": 8, "risk_level": "an_toan", "explanation": "Nội dung bình thường",
            "suggested_action": "Xác minh người gửi", "highlighted_terms": [],
            "visual_flags": [], "phishvn_urls": [], "analysis_breakdown": {},
            "vlm_analysis": {}, "image_model_gradcam": {"available": False, "image_url": ""},
        }
        replacements = {
            "UPLOAD_DIR": self.uploads,
            "extract_text_and_boxes": Mock(return_value=("Nội dung bình thường", [])),
            "decode_qr_codes": Mock(return_value=[]),
            "_analyze_content_payload": Mock(return_value=self.analysis),
        }
        for name, replacement in replacements.items():
            patcher = patch.object(main, name, replacement)
            patcher.start()
            self.addCleanup(patcher.stop)

    async def scan(self, save_history=False, authorization=None):
        image_bytes = io.BytesIO()
        Image.new("RGB", (32, 32), "white").save(image_bytes, format="JPEG")
        image_bytes.seek(0)
        upload = UploadFile(filename="sample.jpg", file=image_bytes,
                            headers=Headers({"content-type": "image/jpeg"}))
        try:
            return await main.check_image(file=upload, scam_category_id=None, user_id=1,
                                          save_history=save_history, db=self.db, authorization=authorization)
        finally:
            await upload.close()

    async def test_guest_returns_result_without_database_or_retained_image(self):
        result = await self.scan()
        self.assertIsNone(result["scan_id"])
        self.assertIsNone(result["image_url"])
        self.assertEqual(result["risk_score"], 8)
        self.assertEqual(self.db.mock_calls, [])
        self.assertEqual(list(self.uploads.iterdir()), [])

    async def test_guest_removes_gradcam_and_does_not_return_deleted_image_url(self):
        def analyze(text, *, image_path, qr_codes):
            gradcam_path = image_path.with_name(f"{image_path.stem}.gradcam.jpg")
            gradcam_path.write_bytes(b"generated heatmap")
            return {
                **self.analysis,
                "image_model_gradcam": {
                    "available": True, "image_url": f"/uploads/{gradcam_path.name}",
                },
            }

        main._analyze_content_payload.side_effect = analyze
        result = await self.scan()
        self.assertFalse(result["image_model_gradcam"]["available"])
        self.assertEqual(result["image_model_gradcam"]["image_url"], "")
        self.assertEqual(list(self.uploads.iterdir()), [])
        self.assertEqual(self.db.mock_calls, [])

    async def test_guest_cleans_up_image_when_analysis_fails(self):
        main.extract_text_and_boxes.side_effect = RuntimeError("OCR failed")
        with self.assertRaises(RuntimeError):
            await self.scan()
        self.assertEqual(self.db.mock_calls, [])
        self.assertEqual(list(self.uploads.iterdir()), [])

    async def test_dedicated_guest_route_always_disables_server_history(self):
        with patch.object(main, "check_image", new_callable=AsyncMock) as analyze:
            upload = object()
            await main.check_image_guest(file=upload, scam_category_id=3, db=self.db)
            analyze.assert_awaited_once_with(file=upload, scam_category_id=3, user_id=0,
                                            save_history=False, db=self.db, authorization=None)

    async def test_existing_saved_scan_flow_is_preserved(self):
        self.db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(id=7, role="admin", is_active=True)
        self.db.refresh.side_effect = lambda record: setattr(record, "id", 123)
        with patch.object(main, "_decode_token", return_value="7"):
            result = await self.scan(save_history=True, authorization="Bearer test-token")
        self.assertEqual(result["scan_id"], 123)
        self.assertTrue(result["image_url"].startswith("/uploads/"))
        self.assertEqual(result["scam_category_id"], 7)
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.assertEqual(len(list(self.uploads.iterdir())), 1)


if __name__ == "__main__":
    unittest.main()
