import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'runtime' / 'scripts'
sys.path.insert(0, str(SCRIPTS))


class AdaptationTests(unittest.TestCase):
    def test_access_restriction_never_navigates_again(self):
        from xhs.feed_detail import _check_page_accessible
        from xhs.errors import PageNotAccessibleError
        page = Mock()
        page.get_element_text.return_value = '请使用小红书App扫码'
        with patch('xhs.feed_detail.time.sleep'), self.assertRaises(PageNotAccessibleError):
            _check_page_accessible(page, 'https://www.xiaohongshu.com/explore/abc')
        page.navigate.assert_not_called()

    def test_qr_never_uses_external_decoder(self):
        from xhs.login import make_qrcode_url
        with patch('http.client.HTTPSConnection') as external:
            image, link = make_qrcode_url(b'local-image')
        external.assert_not_called()
        self.assertTrue(image.startswith('data:image/png;base64,'))
        self.assertIsNone(link)

    def test_long_description_rejected_before_browser_mutation(self):
        from xhs.publish_long_article import click_next_and_fill_description
        page = Mock()
        with self.assertRaises(ValueError):
            click_next_and_fill_description(page, '字' * 1001)
        self.assertEqual(page.mock_calls, [])

    def test_missing_image_not_silently_omitted(self):
        from image_downloader import process_images
        with self.assertRaises(FileNotFoundError):
            process_images(['/nonexistent-xhs-test-image.png'])

    def test_publish_timeout_is_not_success(self):
        from xhs.publish import click_publish_button
        from xhs.errors import OperationUnverifiedError
        page = Mock()
        page.evaluate.side_effect = [None, 'fired']
        with patch('xhs.publish.time.monotonic', side_effect=[0, 20]), \
                patch('xhs.publish.time.sleep'), self.assertRaises(OperationUnverifiedError):
            click_publish_button(page)

    def test_missing_draft_button_is_not_success(self):
        from xhs.publish import save_as_draft
        from xhs.errors import PublishError
        page = Mock()
        page.evaluate.return_value = False
        with self.assertRaises(PublishError):
            save_as_draft(page)


if __name__ == '__main__':
    unittest.main()
