from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
import types
import unittest
import urllib.request
from urllib.parse import quote
from pathlib import Path
from unittest.mock import MagicMock, patch


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import fetch_note as fetch
import browser_common as browser

# No browser runtime or account is needed for the bounded collection replay.
fake_playwright = types.ModuleType("playwright.sync_api")
fake_playwright.TimeoutError = type("PlaywrightTimeoutError", (Exception,), {})
fake_playwright.sync_playwright = MagicMock()
with patch.dict(sys.modules, {"playwright": types.ModuleType("playwright"), "playwright.sync_api": fake_playwright}):
    spec = importlib.util.spec_from_file_location("xhs_collect", SCRIPTS / "collect_likes.py")
    collect = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collect)


NOTE_A = "a" * 24
NOTE_B = "b" * 24
NOTE_URL = f"https://www.xiaohongshu.com/explore/{NOTE_A}"


def note(note_id, count=1):
    return {"noteId": note_id, "title": note_id, "imageList": [
        {"urlDefault": f"https://ci.xhscdn.com/image-{index}"} for index in range(count)
    ]}


class IdentityTests(unittest.TestCase):
    def test_known_id_never_falls_back_to_recommendation(self):
        with self.assertRaises(fetch.FetchError):
            fetch.select_note({"recommendations": [note(NOTE_B, 3)]}, NOTE_A)

    def test_known_id_requires_note_identity(self):
        with self.assertRaises(fetch.FetchError):
            fetch.select_note({"recommendations": [{"imageList": [{}]}]}, NOTE_A)

    def test_exact_match_wins_over_larger_carousel(self):
        selected = fetch.select_note({"rows": [note(NOTE_A), note(NOTE_B, 3)]}, NOTE_A.upper())
        self.assertEqual(NOTE_A, selected["noteId"])

    def test_unknown_id_requires_unique_primary_note(self):
        with self.assertRaises(fetch.FetchError):
            fetch.select_note({"recommendations": [note(NOTE_A), note(NOTE_B, 3)]}, None)
        with self.assertRaises(fetch.FetchError):
            fetch.select_note({"recommendations": [note(NOTE_A)]}, None)
        state = {"note": {"noteDetailMap": {NOTE_A: {"note": note(NOTE_A)}}}, "rows": [note(NOTE_B, 3)]}
        self.assertEqual(NOTE_A, fetch.select_note(state, None)["noteId"])

    def test_note_urls_have_strict_host_and_path_boundaries(self):
        for value in (f"https://evilxiaohongshu.com/explore/{NOTE_A}", f"ftp://www.xiaohongshu.com/explore/{NOTE_A}", f"https://www.xiaohongshu.com/explore/{'a' * 33}"):
            with self.subTest(value=value):
                self.assertIsNone(browser.canonical_note_url(value))
        one = browser.canonical_note_url(NOTE_URL + "?xsec_token=one")
        two = browser.canonical_note_url(NOTE_URL.replace("explore/", "discovery/item/") + "?xsec_token=two")
        self.assertEqual(one[0], two[0])
        self.assertIn("xsec_token=one", one[1])


class RedirectTests(unittest.TestCase):
    def handler(self, opener):
        return next(item for item in opener.handlers if isinstance(item, urllib.request.HTTPRedirectHandler))

    def test_redirect_targets_rejected_before_followup_request(self):
        handler = self.handler(fetch.build_opener(None))
        request = urllib.request.Request("https://xhslink.cn/share")
        for target in ("http://127.0.0.1/private", "http://10.1.2.3/private", "http://[::1]/private", "https://example.com/private", "file:///etc/passwd", "https://evilxiaohongshu.com/note", "https://www.xiaohongshu.com:8765/private", "https://user:pass@www.xiaohongshu.com/note", "https://ci.xhscdn.com/image"):
            with self.subTest(target=target), self.assertRaises(fetch.FetchError):
                handler.redirect_request(request, None, 302, "Found", {}, target)

    def test_initial_request_rejected_before_open(self):
        opener = MagicMock()
        with self.assertRaises(fetch.FetchError):
            fetch.request_url(opener, "http://127.0.0.1/private", 1)
        opener.open.assert_not_called()

    def test_allowed_redirect_rechecks_each_hop(self):
        handler = self.handler(fetch.build_opener(None))
        request = urllib.request.Request("https://xhslink.cn/share")
        redirected = handler.redirect_request(request, None, 302, "Found", {}, NOTE_URL)
        self.assertEqual(NOTE_URL, redirected.full_url)
        with self.assertRaises(fetch.FetchError):
            handler.redirect_request(redirected, None, 302, "Found", {}, "https://example.com/private")

    def test_image_redirects_keep_cdn_boundary_and_no_cookie_leak(self):
        opener = fetch.build_opener(None)
        handler = self.handler(opener)
        observed = []
        def open_request(request, **kwargs):
            redirected = handler.redirect_request(request, None, 302, "Found", {}, "https://ci2.xhscdn.com/image")
            observed.append(redirected)
            with self.assertRaises(fetch.FetchError):
                handler.redirect_request(redirected, None, 302, "Found", {}, "https://xhslink.cn/share")
            response = MagicMock()
            response.geturl.return_value = redirected.full_url
            response.headers.get.return_value = None
            response.headers.get_content_type.return_value = "image/png"
            response.read.return_value = b"image"
            response.__enter__.return_value = response
            return response
        with patch.object(opener, "open", side_effect=open_request):
            fetch.request_url(opener, "https://ci.xhscdn.com/image", 1, referer=NOTE_URL)
        self.assertEqual("https://ci2.xhscdn.com/image", observed[0].full_url)
        request = urllib.request.Request(NOTE_URL)
        request.add_unredirected_header("Cookie", "secret=value")
        redirected = handler.redirect_request(request, None, 302, "Found", {}, "https://www.xiaohongshu.com/explore")
        self.assertFalse(redirected.has_header("Cookie"))

    def test_authorized_cookie_file_only_sends_page_domain_cookies(self):
        with tempfile.TemporaryDirectory() as directory:
            cookies = Path(directory) / "cookies.txt"
            cookies.write_text(
                "# Netscape HTTP Cookie File\n"
                ".xiaohongshu.com\tTRUE\t/\tTRUE\t2147483647\tweb_session\tfixture\n"
                ".xhscdn.com\tTRUE\t/\tTRUE\t2147483647\tprivate\tunrelated\n"
                ".example.com\tTRUE\t/\tTRUE\t2147483647\tprivate\tunrelated\n"
            )
            opener = fetch.build_opener(cookies)
        processor = next(item for item in opener.handlers if isinstance(item, urllib.request.HTTPCookieProcessor))
        self.assertEqual(["web_session"], [cookie.name for cookie in processor.cookiejar])
        page = processor.http_request(urllib.request.Request(NOTE_URL))
        self.assertEqual("web_session=fixture", page.get_header("Cookie"))
        image = processor.http_request(urllib.request.Request("https://ci.xhscdn.com/image"))
        self.assertIsNone(image.get_header("Cookie"))

    def test_mcp_json_cookies_are_loaded_in_memory_and_scoped(self):
        rows = [
            {'name': 'web_session', 'value': 'fixture', 'domain': '.xiaohongshu.com', 'path': '/', 'secure': True, 'expires': -1},
            {'name': 'host_only', 'value': 'fixture', 'domain': 'www.xiaohongshu.com', 'path': '/', 'expires': 2147483647},
            {'name': 'expired', 'value': 'fixture', 'domain': '.xiaohongshu.com', 'expires': 1},
            {'name': 'unrelated', 'value': 'fixture', 'domain': '.example.com'},
        ]
        for payload in (rows, {'cookies': rows, 'origins': []}):
            with self.subTest(shape=type(payload).__name__), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'cookies.json'
                original = json.dumps(payload)
                path.write_text(original)
                opener = fetch.build_opener(path)
                self.assertEqual(original, path.read_text())
                self.assertEqual(['cookies.json'], [p.name for p in Path(directory).iterdir()])
            processor = next(h for h in opener.handlers if isinstance(h, urllib.request.HTTPCookieProcessor))
            self.assertEqual({'web_session', 'host_only'}, {c.name for c in processor.cookiejar})
            request = processor.http_request(urllib.request.Request(NOTE_URL))
            self.assertIn('web_session=fixture', request.get_header('Cookie'))
            for url in ('https://ci.xhscdn.com/image', 'http://www.xiaohongshu.com/explore'):
                self.assertIsNone(processor.http_request(urllib.request.Request(url)).get_header('Cookie'))
            subdomain = processor.http_request(urllib.request.Request('https://child.www.xiaohongshu.com/'))
            self.assertNotIn('host_only', subdomain.get_header('Cookie', ''))

    def test_bad_json_cookies_do_not_echo_secrets(self):
        payloads = [
            '{"cookies": ["secret-value"',
            {'cookies': 'secret-value'},
            [{'domain': '.xiaohongshu.com', 'name': 'a', 'value': 'secret-value\r\nInjected: yes'}],
            [{'domain': '.xiaohongshu.com', 'name': 'a', 'value': 'secret-value', 'expires': 'invalid'}],
        ]
        for payload in payloads:
            with self.subTest(payload_type=type(payload).__name__), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'cookies.json'
                path.write_text(payload if isinstance(payload, str) else json.dumps(payload))
                with self.assertRaises(fetch.FetchError) as caught:
                    fetch.build_opener(path)
                self.assertNotIn('secret-value', str(caught.exception))


class ManifestTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.html = self.root / "page.html"
        state = {"note": {"noteDetailMap": {NOTE_A: {"note": note(NOTE_A, 3)}}}}
        self.html.write_text("<script>window.__INITIAL_STATE__=" + json.dumps(state) + "</script>")
        self.args = argparse.Namespace(source=NOTE_URL, cookie_file=None, html_file=str(self.html), timeout=1, out_dir=str(self.root / "output"), metadata_only=False)

    def test_public_share_exports_body_without_browser_or_mcp(self):
        primary = dict(note(NOTE_A), title='测试标题', desc='第一段\n\n第二段', user={'nickname': '作者'})
        page = '<script>window.__INITIAL_STATE__=' + json.dumps({'note': {'noteDetailMap': {NOTE_A: {'note': primary}}}}) + '</script>'
        self.args.source = '测试标题 https://xhslink.cn/o/example 复制到小红书'
        self.args.html_file = None
        with patch.object(fetch, 'request_url', side_effect=[
            (page.encode(), NOTE_URL + '?xsec_token=private', 'text/html'),
            (b'GIF89aimage', 'https://ci.xhscdn.com/image', 'image/gif'),
        ]), patch.object(fetch, 'read_browser_page') as browser_read:
            result = fetch.run(self.args)
        browser_read.assert_not_called()
        self.assertTrue(result['ok'])
        self.assertEqual('http', result['access_mode'])
        self.assertEqual(NOTE_URL, result['canonical_url'])
        body = Path(result['text_file']).read_text()
        self.assertIn('第一段\n\n第二段', body)
        self.assertIn('作者', body)
        self.assertIn('未包含图片 OCR', body)
        self.assertNotIn('xsec_token', body)

    def test_body_survives_image_failure(self):
        with patch.object(fetch, 'request_url', side_effect=fetch.FetchError('HTTP 403', 3)):
            result = fetch.run(self.args)
        self.assertFalse(result['ok'])
        self.assertTrue(Path(result['text_file']).is_file())
        manifest = json.loads(Path(result['manifest']).read_text())
        self.assertEqual('note.txt', manifest['text_file'])

    def test_existing_text_is_never_overwritten(self):
        output = Path(self.args.out_dir)
        output.mkdir()
        (output / 'note.txt').write_text('user content')
        with patch.object(fetch, 'request_url') as request, self.assertRaises(fetch.FetchError):
            fetch.run(self.args)
        request.assert_not_called()
        self.assertEqual('user content', (output / 'note.txt').read_text())

    def test_download_failure_retains_order_hashes_and_missing_pages(self):
        png = b"\x89PNG\r\n\x1a\nimage"
        with patch.object(fetch, "request_url", side_effect=[(png, "https://ci.xhscdn.com/one", "image/png"), fetch.FetchError("HTTP 403", 3)]) as request:
            result = fetch.run(self.args)
        self.assertFalse(result["ok"])
        self.assertEqual(2, request.call_count)
        manifest = json.loads(Path(result["manifest"]).read_text())
        self.assertEqual("partial", manifest["completeness"])
        self.assertFalse(manifest["downloaded"])
        self.assertEqual([2, 3], manifest["missing_pages"])
        self.assertEqual([1, 2, 3], [image["index"] for image in manifest["images"]])
        self.assertEqual(64, len(manifest["images"][0]["sha256"]))
        self.assertEqual("failed", manifest["images"][1]["status"])
        self.assertEqual("not_attempted", manifest["images"][2]["status"])
        self.assertTrue(Path(result["images"][0]["path"]).is_file())

    def test_complete_and_metadata_only_manifests(self):
        with patch.object(fetch, "request_url", return_value=(b"GIF89aimage", "https://ci.xhscdn.com/one", "image/gif")):
            result = fetch.run(self.args)
        self.assertTrue(result["ok"])
        self.assertTrue(result["downloaded"])
        self.assertEqual("complete", json.loads(Path(result["manifest"]).read_text())["completeness"])
        self.args.metadata_only = True
        self.args.out_dir = str(self.root / "metadata")
        with patch.object(fetch, "request_url") as request:
            result = fetch.run(self.args)
        request.assert_not_called()
        self.assertFalse(result["downloaded"])
        self.assertEqual("none", json.loads(Path(result["manifest"]).read_text())["completeness"])

    def test_direct_source_identity_survives_redirect(self):
        page = "<script>window.__INITIAL_STATE__=" + json.dumps({"rows": [note(NOTE_B)]}) + "</script>"
        self.args.html_file = None
        self.args.metadata_only = True
        with patch.object(fetch, "request_url", return_value=(page.encode(), NOTE_URL.replace(NOTE_A, NOTE_B), "text/html")), self.assertRaises(fetch.FetchError):
            fetch.run(self.args)

    def test_login_is_classified_before_parsing_without_downloading(self):
        self.args.html_file = None
        target = NOTE_URL + '?type=video&xsec_token=private-token'
        login = 'https://www.xiaohongshu.com/login?redirectPath=' + quote(target, safe='')
        with patch.object(fetch, 'request_url', return_value=(b'<html>login</html>', login, 'text/html')) as request:
            with self.assertRaises(fetch.FetchError) as caught:
                fetch.run(self.args)
        self.assertEqual('login_required', caught.exception.details['status'])
        self.assertEqual(NOTE_A, caught.exception.details['note_id'])
        self.assertEqual('video', caught.exception.details['note_type_hint'])
        self.assertNotIn('private-token', json.dumps(caught.exception.details))
        self.assertEqual(1, request.call_count)
        self.assertFalse(Path(self.args.out_dir).exists())

    def test_video_without_images_returns_handoff_not_ocr_success(self):
        video = {'noteId': NOTE_A, 'type': 'video', 'title': 'video', 'desc': 'caption',
                 'video': {'media': {'stream': {'h264': [{'masterUrl': 'https://sns-video-bd.xhscdn.com/video.mp4'}]}}}}
        self.html.write_text('<script>window.__INITIAL_STATE__=' + json.dumps({'note': {'noteDetailMap': {NOTE_A: {'note': video}}}}) + '</script>')
        with patch.object(fetch, 'request_url') as request:
            result = fetch.run(self.args)
        request.assert_not_called()
        self.assertEqual('video_handoff', result['status'])
        self.assertEqual('none', result['completeness'])
        self.assertFalse(result['downloaded'])
        self.assertEqual('watch', result['handoff']['skill'])
        self.assertEqual(['https://sns-video-bd.xhscdn.com/video.mp4'], result['handoff']['media_urls'])
        self.assertEqual('caption', result['description'])
        self.assertEqual('not_started', result['handoff']['transcript_status'])
        self.assertIn('未包含视频逐字稿', Path(result['text_file']).read_text())

    def test_video_cover_does_not_count_as_video_content(self):
        video = dict(note(NOTE_A), type='video', video={'consumer': {'originVideoKey': 'not-a-url'}})
        self.html.write_text('<script>window.__INITIAL_STATE__=' + json.dumps({'rows': [video]}) + '</script>')
        with patch.object(fetch, 'request_url') as request:
            result = fetch.run(self.args)
        request.assert_not_called()
        self.assertEqual('video_handoff', result['status'])
        self.assertEqual([], result['handoff']['media_urls'])
        self.assertFalse(result['downloaded'])


class AccessClassificationTests(unittest.TestCase):
    def test_login_hint_never_trusts_external_redirect(self):
        for target in ('https://evil.example/explore/' + NOTE_A,
                       'https://www.xiaohongshu.com:8765/explore/' + NOTE_A):
            with self.subTest(target=target), self.assertRaises(fetch.FetchError) as caught:
                fetch.classify_access_page('https://www.xiaohongshu.com/login?redirectPath=' + quote(target, safe=''), '')
            self.assertEqual('login_required', caught.exception.details['status'])
            self.assertIsNone(caught.exception.details.get('note_id'))

    def test_captcha_and_risky_ip_are_security_blocks(self):
        for url in ('https://www.xiaohongshu.com/website-login/captcha',
                    'https://www.xiaohongshu.com/website-login/error?error_code=300012'):
            with self.subTest(url=url), self.assertRaises(fetch.FetchError) as caught:
                fetch.classify_access_page(url, '')
            self.assertEqual('security_block', caught.exception.details['status'])

    def test_login_navigation_link_is_not_a_login_wall(self):
        fetch.classify_access_page(NOTE_URL, '<a href="/login">登录</a>')

    def test_saved_login_html_is_not_parsed_as_a_note(self):
        with tempfile.TemporaryDirectory() as directory:
            html = Path(directory) / 'login.html'
            html.write_text('<script>window.__INITIAL_STATE__={"login":{},"user":{}}</script>')
            args = argparse.Namespace(source=NOTE_URL, cookie_file=None, html_file=str(html), timeout=1, out_dir=None, metadata_only=True)
            with self.assertRaises(fetch.FetchError) as caught:
                fetch.run(args)
            self.assertEqual('login_required', caught.exception.details['status'])

    def test_video_urls_reject_external_hosts_and_do_not_synthesize_keys(self):
        video = {'consumer': {'originVideoKey': 'fake-key'}, 'media': {'stream': {'h264': [
            {'masterUrl': 'http://127.0.0.1/internal'},
            {'masterUrl': 'https://evilxhscdn.com/video.mp4'},
            {'masterUrl': 'https://sns-video-bd.xhscdn.com/video.mp4'},
            {'masterUrl': 'https://sns-video-bd.xhscdn.com/video.mp4'}]}}}
        self.assertEqual(['https://sns-video-bd.xhscdn.com/video.mp4'], fetch.video_urls(video))


class BrowserReadingTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.context, self.page = MagicMock(), MagicMock()
        self.context.new_page.return_value = self.page
        self.page.url = NOTE_URL
        self.page.goto.return_value.status = 200
        self.page.content.return_value = '<script>window.__INITIAL_STATE__={}</script>'
        for patcher in (
            patch.dict(sys.modules, {'playwright': types.ModuleType('playwright'), 'playwright.sync_api': fake_playwright}),
            patch.object(browser, 'PROFILE_DIR', Path(self.directory.name)),
            patch.object(browser, 'launch_context', return_value=self.context),
            patch.object(browser, 'has_login_session', return_value=True),
            patch.object(browser, 'risk_reason', return_value=None),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_authorized_read_returns_html_without_cookie_export(self):
        page, url = fetch.read_browser_page(NOTE_URL, 1)
        self.assertIn('__INITIAL_STATE__', page)
        self.assertEqual(NOTE_URL, url)
        self.context.storage_state.assert_not_called()
        self.context.close.assert_called_once()
        self.context.new_page.assert_called_once()

    def test_missing_session_does_not_navigate(self):
        with patch.object(browser, 'has_login_session', return_value=False):
            with self.assertRaises(fetch.FetchError) as caught:
                fetch.read_browser_page(NOTE_URL, 1)
        self.assertEqual('login_required', caught.exception.details['status'])
        self.page.goto.assert_not_called()
        self.context.close.assert_called_once()

    def test_risk_stops_before_waiting_for_content(self):
        with patch.object(browser, 'risk_reason', return_value='captcha'):
            with self.assertRaises(fetch.FetchError) as caught:
                fetch.read_browser_page(NOTE_URL, 1)
        self.assertEqual('security_block', caught.exception.details['status'])
        self.page.wait_for_function.assert_not_called()
        self.context.close.assert_called_once()

    def test_session_loss_discards_page_and_closes_context(self):
        with patch.object(browser, 'has_login_session', side_effect=[True, False]):
            with self.assertRaises(fetch.FetchError) as caught:
                fetch.read_browser_page(NOTE_URL, 1)
        self.assertEqual('login_required', caught.exception.details['status'])
        self.context.close.assert_called_once()

    def test_browser_exception_does_not_leak_signed_url(self):
        self.page.goto.side_effect = RuntimeError('url?xsec_token=secret')
        with self.assertRaises(fetch.FetchError) as caught:
            fetch.read_browser_page(NOTE_URL, 1)
        self.assertNotIn('secret', str(caught.exception))
        self.context.close.assert_called_once()

    def test_external_main_frame_navigation_is_aborted(self):
        route = MagicMock()
        route.request.url = 'http://127.0.0.1/private'
        route.request.frame = self.page.main_frame
        route.request.is_navigation_request.return_value = True
        self.page.route.side_effect = lambda pattern, callback: callback(route)
        with self.assertRaises(fetch.FetchError) as caught:
            fetch.read_browser_page(NOTE_URL, 1)
        self.assertEqual('navigation_blocked', caught.exception.details['status'])
        route.abort.assert_called_once()
        route.continue_.assert_not_called()

    def test_public_mode_never_launches_browser(self):
        args = argparse.Namespace(source=NOTE_URL, cookie_file=None, html_file=None, timeout=1, out_dir=None, metadata_only=True)
        with patch.object(fetch, 'read_browser_page') as capture, patch.object(fetch, 'request_url',
                return_value=(b'<html>login</html>', 'https://www.xiaohongshu.com/login', 'text/html')):
            with self.assertRaises(fetch.FetchError):
                fetch.run(args)
        capture.assert_not_called()


class CollectionTests(unittest.TestCase):
    def test_mid_scroll_risk_or_session_loss_stops_without_success_manifest(self):
        for failure in ("risk", "login"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "likes.json"
                page, context = MagicMock(), MagicMock()
                context.pages = [page]
                page.get_by_text.return_value.count.return_value = 1
                state = {"scrolled": False}
                page.evaluate.side_effect = lambda _: state.update(scrolled=True)
                messages = []
                with patch.object(sys, "argv", ["collect_likes", "--profile-url", "https://www.xiaohongshu.com/user/profile/me", "--max-scrolls", "1", "--out", str(output)]), patch.object(
                    collect, "launch_context", return_value=context
                ), patch.object(collect, "risk_reason", side_effect=lambda _: "captcha" if state["scrolled"] and failure == "risk" else None), patch.object(
                    collect, "has_login_session", side_effect=lambda _: not (state["scrolled"] and failure == "login")
                ), patch.object(collect, "collect_visible", return_value=[{"note_id": NOTE_A, "url": NOTE_URL}]), patch.object(
                    collect, "emit", side_effect=messages.append
                ):
                    self.assertEqual(3, collect.main())
                self.assertFalse(output.exists())
                self.assertFalse(messages[-1]["ok"])
                context.close.assert_called_once()

    def test_collection_deduplicates_note_ids_across_tokens(self):
        page = MagicMock()
        page.locator.return_value.evaluate_all.return_value = [
            {"href": NOTE_URL + "?xsec_token=one", "text": "one"},
            {"href": NOTE_URL + "?xsec_token=two", "text": "same note"},
        ]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "likes.json"
            context = MagicMock()
            context.pages = [page]
            page.get_by_text.return_value.count.return_value = 1
            with patch.object(sys, "argv", ["collect_likes", "--profile-url", "https://www.xiaohongshu.com/user/profile/me", "--max-scrolls", "1", "--out", str(output)]), patch.object(
                collect, "launch_context", return_value=context
            ), patch.object(collect, "risk_reason", return_value=None), patch.object(collect, "has_login_session", return_value=True), patch.object(collect, "emit"):
                self.assertEqual(0, collect.main())
            payload = json.loads(output.read_text())
            self.assertEqual(1, payload["count"])
            self.assertEqual(NOTE_A, payload["notes"][0]["note_id"])


if __name__ == "__main__":
    unittest.main()
