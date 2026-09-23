from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "fetch_x.py"
spec = importlib.util.spec_from_file_location("fetch_x", SCRIPT)
fetch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch)
URL = "https://x.com/example/status/1234567890"


def payload(**changes):
    post = {"id": "1234567890", "text": "Synthetic original, not a preview.",
            "author": {"screen_name": "example"}, "media": {}}
    post.update(changes)
    return {"code": 200, "status": post}


class ExtractionTests(unittest.TestCase):
    def test_url_normalization_and_media_suffix(self):
        for url in (URL + "?s=46", URL + "/video/1", URL.replace("x.com", "mobile.twitter.com")):
            self.assertEqual((URL, "1234567890"), fetch.parse_url(url))

    def test_rejects_untrusted_hosts_and_ambiguous_urls(self):
        for url in ("https://evilx.com/a/status/1234567890", URL + "evil", URL + " " + URL,
                    "https://x.com@evil.com/a/status/1234567890", "file:///etc/passwd",
                    "https://x.com:8080/a/status/1234567890"):
            with self.subTest(url=url), self.assertRaises(fetch.FetchError):
                fetch.parse_url(url)

    def test_exact_identity_and_api_error_required(self):
        for data in (payload(id="9999999999"), {"code": 403, "status": payload()["status"]},
                     {"code": 200, "status": {"type": "tombstone", "id": "1234567890"}}):
            with self.assertRaises(fetch.FetchError):
                fetch.extract(data, URL)

    def test_legacy_payload_keeps_single_post_scope(self):
        data = payload()
        data["tweet"] = data.pop("status")
        result = fetch.extract(data, URL)
        self.assertEqual("single_post", result["scope"])
        self.assertEqual("provider_payload", result["text_coverage"])
        self.assertEqual("unverified", result["source_completeness"])

    def test_article_blocks_override_empty_post_and_preview(self):
        result = fetch.extract(payload(text="", article={"title": "Example", "preview_text": "teaser",
            "content": {"blocks": [{"type": "header-two", "text": "Heading"},
                                   {"type": "unstyled", "text": "Do not remove the condition."}],
                        "entityMap": []}}), URL)
        self.assertEqual("article_blocks", result["text_basis"])
        self.assertIn("Do not remove the condition.", result["text"])
        self.assertNotIn("teaser", result["text"])
        self.assertEqual(2, result["block_count"])

    def test_preview_is_not_article_body(self):
        result = fetch.extract(payload(text="teaser", article={"title": "Article", "preview_text": "teaser"}), URL)
        self.assertEqual("preview_only", result["text_coverage"])
        self.assertIn("article_body_missing", result["gaps"])

    def test_unknown_blocks_fail_closed_without_dropping_text(self):
        result = fetch.extract(payload(article={"content": {"blocks": [
            {"type": "atomic", "text": " ", "entityRanges": [{"key": 0}]},
            {"type": "new-format", "text": "Keep me"}]}}), URL)
        self.assertEqual("partial", result["text_coverage"])
        self.assertIn("Keep me", result["text"])
        self.assertEqual(2, len(result["gaps"]))

    def test_mixed_media_order_and_quote_remain_separate(self):
        media = {"all": [{"type": "photo", "url": "https://pbs.twimg.com/media/a.jpg"},
                         {"type": "video", "url": "https://video.twimg.com/a.mp4"},
                         {"type": "photo", "url": "https://pbs.twimg.com/media/b.jpg"}]}
        result = fetch.extract(payload(media=media, quote={"id": "9876543210", "text": "Other author"}), URL)
        self.assertEqual(["photo", "video", "photo"], [m["type"] for m in result["media"]])
        self.assertEqual("pending", result["media"][0]["inspection"])
        self.assertNotIn("Other author", result["text"])
        self.assertEqual("9876543210", result["quote"]["id"])

    def test_article_cover_and_inventory_are_not_body_order_claim(self):
        result = fetch.extract(payload(article={"cover_media": {"media_info": {
            "original_img_url": "https://pbs.twimg.com/media/cover.jpg"}},
            "media_entities": [{"media_info": {"original_img_url": "https://pbs.twimg.com/media/page.jpg"}}]}), URL)
        self.assertEqual(["article_cover", "article_inventory"], [m["role"] for m in result["media"]])
        self.assertEqual("unverified", result["media"][1]["reading_order"])

    def test_empty_body_is_not_successful_extraction(self):
        result = fetch.extract(payload(text=""), URL)
        self.assertEqual("missing", result["text_coverage"])


class NetworkAndArtifactTests(unittest.TestCase):
    def test_redirects_cannot_leave_selected_boundary(self):
        handler = fetch.Redirects(("api.fxtwitter.com",))
        for target in ("http://127.0.0.1/x", "https://evil.com/x", "https://api.fxtwitter.com:444/x"):
            with self.assertRaises(fetch.FetchError):
                handler.redirect_request(urllib.request.Request("https://api.fxtwitter.com/2/status/123"),
                                         None, 302, "Found", {}, target)

    def test_image_signature_rejects_html(self):
        with self.assertRaises(fetch.FetchError):
            fetch.image_suffix(b"<html>blocked</html>")
        self.assertEqual(".png", fetch.image_suffix(b"\x89PNG\r\n\x1a\nsynthetic"))

    def test_partial_images_keep_manifest_and_fresh_attempt(self):
        data = payload(media={"all": [
            {"type": "photo", "url": "https://pbs.twimg.com/media/a.png"},
            {"type": "photo", "url": "https://pbs.twimg.com/media/b.png"}]})
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(fetch, "request_bytes", side_effect=[b"\x89PNG\r\n\x1a\nfixture", fetch.FetchError("HTTP 403")]):
                first = fetch.save(data, URL, Path(directory), True)
            second = fetch.save(data, URL, Path(directory), False)
            self.assertNotEqual(first["work_dir"], second["work_dir"])
            manifest = json.loads(Path(first["manifest"]).read_text())
            self.assertEqual("partial", manifest["image_downloads"])
            self.assertEqual([2], manifest["missing_images"])
            self.assertEqual("pending", manifest["media"][0]["inspection"])
            self.assertEqual(64, len(manifest["media"][0]["sha256"]))
            self.assertEqual("not_requested", second["image_downloads"])

    def test_file_replay_has_no_metadata_network_request(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_text(json.dumps(payload()))
            with patch.object(fetch, "request_bytes") as request:
                self.assertEqual(0, fetch.main([URL, "--json-file", str(path), "--out-dir", directory]))
            request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
