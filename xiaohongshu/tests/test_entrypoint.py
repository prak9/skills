import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('local_xhs', ROOT / 'scripts' / 'xhs.py')
xhs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xhs)
NOTE_ID = '6ac09b760000000001008b8a'


class EntryTests(unittest.TestCase):
    def test_all_mutations_are_guarded_before_connect(self):
        import argparse
        for command in xhs.WRITE_COMMANDS:
            with self.subTest(command=command), self.assertRaises(ValueError):
                xhs.validate_args(argparse.Namespace(command=command, write_confirmed=False,
                                                    bridge_url='ws://localhost:9333'))

    def test_remote_bridge_is_rejected(self):
        args = xhs.build_parser().parse_args(['--bridge-url', 'ws://example.com', 'status'])
        with self.assertRaises(ValueError):
            xhs.validate_args(args)

    def test_sms_and_raw_log_commands_unavailable(self):
        for command in xhs.DISABLED_COMMANDS:
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                xhs.build_parser().parse_args([command])

    def test_snapshot_rejects_wrong_page_and_note(self):
        good = {'url': 'https://www.xiaohongshu.com/explore/' + NOTE_ID,
                'note': {'noteId': NOTE_ID, 'title': '原文'}}
        for changed in [dict(good, url='https://example.com/explore/' + NOTE_ID),
                        dict(good, url=good['url'].replace(NOTE_ID, 'a' * 24)),
                        dict(good, note={'noteId': 'a' * 24})]:
            with self.assertRaises(ValueError):
                xhs.snapshot_html(changed, NOTE_ID)

    def test_snapshot_only_contains_requested_note_and_escapes_script(self):
        snapshot = {'url': 'https://www.xiaohongshu.com/explore/' + NOTE_ID,
                    'note': {'noteId': NOTE_ID, 'desc': '</script>原文'},
                    'cookies': 'secret-not-exportable'}
        html = xhs.snapshot_html(snapshot, NOTE_ID)
        self.assertNotIn('secret-not-exportable', html)
        data = html.removeprefix('<script>window.__INITIAL_STATE__=').removesuffix('</script>')
        self.assertEqual(json.loads(data)['note']['noteDetailMap'][NOTE_ID]['note']['desc'], '</script>原文')
        self.assertEqual(html.count('</script>'), 1)

    def test_no_automatic_browser_or_server_start(self):
        with patch('xhs.bridge.BridgePage') as page, patch('subprocess.Popen') as start:
            page.return_value.is_server_running.return_value = False
            with self.assertRaises(RuntimeError):
                xhs.cli._ensure_bridge_ready('ws://localhost:9333')
            start.assert_not_called()

    def test_read_commands_need_no_write_flag(self):
        for command in ['status', 'inspect-page', 'list-feeds']:
            xhs.validate_args(xhs.build_parser().parse_args([command]))

    def test_lock_blocks_concurrent_command_and_releases(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp, patch.object(xhs, 'SKILL_DIR', Path(tmp)):
            (Path(tmp) / 'runtime').mkdir()
            with xhs.browser_lock():
                with self.assertRaises(RuntimeError):
                    with xhs.browser_lock():
                        pass
            with xhs.browser_lock():
                pass


if __name__ == '__main__':
    unittest.main()
