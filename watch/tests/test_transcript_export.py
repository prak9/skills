from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import download
import watch


class TranscriptExportTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.work = Path(directory.name)

    def test_metadata_keeps_provenance_not_signed_media_urls(self):
        raw = {
            "id": "abc", "title": "中文访谈", "channel": "Author",
            "upload_date": "20240902", "duration": 3000, "language": None,
            "license": None, "description": "Video description, not speech",
            "subtitles": {"zh": [{"url": "https://host/?secret=signed"}], "en": [{}]},
            "automatic_captions": {"fr": [{"url": "https://host/?tlang=fr"}]},
            "http_headers": {"Authorization": "secret-header"},
        }
        path = self.work / "source.info.json"
        path.write_text(json.dumps(raw))
        info = download._read_info(path, "https://example.com/abc")
        self.assertEqual("20240902", info.get("upload_date"))
        self.assertIn("language", info)
        self.assertIsNone(info["language"])
        self.assertEqual({"zh", "en", "fr"}, {t["language"] for t in info["available_subtitles"]})
        self.assertEqual("translated", next(t["kind"] for t in info["available_subtitles"] if t["language"] == "fr"))
        self.assertNotIn("secret", json.dumps(info))

    def test_quiet_watch_retains_every_segment_and_metadata(self):
        vtt = self.work / "captions.vtt"
        vtt.write_text("WEBVTT\n\n00:00.000 --> 00:01.000\nUnused\n")
        segments = [{"start": i * 2, "end": i * 2 + 1, "text": f"spoken-{i}"} for i in range(1800)]
        output = self.work / "output"
        stdout = io.StringIO()
        with patch.object(sys, "argv", ["watch", "https://example.com/video", "--detail", "transcript",
                                       "--no-whisper", "--no-print-transcript", "--out-dir", str(output)]), patch.object(
            watch, "get_config", return_value={"detail": "transcript"}
        ), patch.object(watch, "fetch_captions", return_value={
            "subtitle_path": str(vtt), "subtitle_info": {"language": "zh", "kind": "manual"},
            "info": {"title": "Example", "duration": 3600, "upload_date": "20240902", "language": None},
        }), patch.object(watch, "parse_vtt", return_value=segments), patch.object(
            watch, "download"
        ) as media, contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(0, watch.main())
        media.assert_not_called()
        self.assertNotIn("spoken-1799", stdout.getvalue())
        self.assertLess(len(stdout.getvalue()), 3000)
        text = (output / "transcript.txt").read_text()
        self.assertEqual([s["text"] for s in segments], text.splitlines())
        markdown = (output / "transcript.md").read_text()
        self.assertIn("spoken-1799", markdown)
        artifact = json.loads((output / "transcript.json").read_text())
        self.assertEqual("20240902", artifact["info"]["upload_date"])
        self.assertEqual(str(vtt), artifact["raw_subtitle_path"])
        self.assertEqual(1800, artifact["coverage"]["segment_count"])
        self.assertFalse(artifact["coverage"]["speech_verified"])

    def test_offline_vtt_export_preserves_source_without_network(self):
        vtt = self.work / "source.zh.vtt"
        original = "WEBVTT\n\n00:30.000 --> 00:31.000\n第一句\n\n46:50.000 --> 46:51.000\n末句\n"
        vtt.write_text(original, encoding="utf-8")
        info = self.work / "source.info.json"
        info.write_text(json.dumps({"title": "Offline", "duration": 2837, "webpage_url": "https://example.com/v"}))
        result = subprocess.run([sys.executable, str(SCRIPTS / "export_transcript.py"), str(vtt),
                                 "--info-json", str(info), "--subtitle-lang", "zh", "--subtitle-kind", "manual",
                                 "--out-dir", str(self.work / "out")], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        artifact = json.loads((self.work / "out/transcript.json").read_text())
        self.assertEqual({"language": "zh", "kind": "manual"}, artifact["subtitle_info"])
        self.assertEqual(30, artifact["coverage"]["first_start"])
        self.assertEqual(2811, artifact["coverage"]["last_end"])
        self.assertFalse(artifact["coverage"]["speech_verified"])
        self.assertEqual(original, vtt.read_text())

    def test_partial_json_replay_preserves_gaps_and_focus(self):
        artifact = {
            "source": "local.mp4", "info": {"title": "Example"},
            "transcript_source": "whisper (groq)", "subtitle_info": None,
            "completeness": {"status": "partial", "missing_intervals": [{"start": 10, "end": 20}]},
            "completeness_scope": "full source audio",
            "segment_range": {"start": 0, "end": 30},
            "segments": [{"start": 21, "end": 22, "text": "recovered"}],
        }
        path = self.work / "input.json"
        path.write_text(json.dumps(artifact))
        result = subprocess.run([sys.executable, str(SCRIPTS / "export_transcript.py"), str(path),
                                 "--out-dir", str(self.work / "out")], capture_output=True, text=True)
        self.assertEqual(4, result.returncode, result.stderr)
        result = json.loads((self.work / "out/transcript.json").read_text())
        for key in ("completeness", "segment_range", "completeness_scope"):
            self.assertEqual(artifact[key], result[key])
        self.assertIn("partial", (self.work / "out/transcript.md").read_text())

    def test_empty_vtt_is_not_successful_full_text(self):
        path = self.work / "empty.vtt"
        path.write_text("WEBVTT\n")
        result = subprocess.run([sys.executable, str(SCRIPTS / "export_transcript.py"), str(path),
                                 "--out-dir", str(self.work / "out")], capture_output=True, text=True)
        self.assertEqual(4, result.returncode)
        result = json.loads((self.work / "out/transcript.json").read_text())
        self.assertEqual("none", result["completeness"]["status"])
        self.assertEqual(0, result["coverage"]["segment_count"])

    def test_empty_legacy_json_reports_none_in_console_and_file(self):
        path = self.work / "empty.json"
        path.write_text(json.dumps({"segments": [], "completeness": {"status": "complete"}}))
        result = subprocess.run([sys.executable, str(SCRIPTS / "export_transcript.py"), str(path),
                                 "--out-dir", str(self.work / "out")], capture_output=True, text=True)
        self.assertEqual(4, result.returncode)
        report = json.loads(result.stdout)
        artifact = json.loads((self.work / "out/transcript.json").read_text())
        self.assertEqual("none", report["completeness"]["status"])
        self.assertEqual(report["completeness"], artifact["completeness"])

    def test_watch_reports_damaged_captions_as_partial(self):
        vtt = self.work / "damaged.vtt"
        vtt.write_text("WEBVTT\n\n00:01.000 --> 00:02.000\nHeard\n\nbad --> time\nLost\n")
        stdout = io.StringIO()
        with patch.object(sys, "argv", ["watch", "https://example.com/v", "--detail", "transcript",
                                       "--no-whisper", "--subtitle-lang", "zh", "--out-dir", str(self.work)]), patch.object(
            watch, "get_config", return_value={"detail": "transcript"}
        ), patch.object(watch, "fetch_captions", return_value={
            "subtitle_path": str(vtt), "subtitle_info": {"language": "en", "kind": "manual"},
            "info": {"duration": 30, "language": None, "available_subtitles": [
                {"language": "en", "kind": "manual"}, {"language": "fr", "kind": "manual"},
            ]},
        }), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(0, watch.main())
        artifact = json.loads((self.work / "transcript.json").read_text())
        self.assertEqual("partial", artifact["completeness"]["status"])
        self.assertEqual(1, artifact["parse_diagnostics"]["invalid_cues"])
        self.assertIn("requested zh unavailable", stdout.getvalue())
        self.assertIn("Source language:** unknown", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
