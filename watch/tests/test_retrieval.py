from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import download
import transcribe
import whisper
import watch

spec = importlib.util.spec_from_file_location("watch_setup", SCRIPTS / "setup.py")
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.work = Path(directory.name)

    def fake_ytdlp(self, info, *, media=False, exit_code=0):
        def run(cmd, **kwargs):
            if "--dump-single-json" in cmd:
                return subprocess.CompletedProcess(cmd, 0, json.dumps(info), "")
            directory = Path(cmd[cmd.index("-o") + 1]).parent
            (directory / "video.info.json").write_text(json.dumps(info), encoding="utf-8")
            languages = cmd[cmd.index("--sub-langs") + 1] if "--sub-langs" in cmd else ""
            for language in info.get("subtitles", {}) | info.get("automatic_captions", {}):
                if re.fullmatch(languages, language):
                    (directory / f"video.{language}.vtt").write_text(
                        "WEBVTT\n\n00:01.000 --> 00:02.000\n原生字幕\n", encoding="utf-8"
                    )
            if media:
                (directory / "video.mp4").write_bytes(b"new-video")
            return subprocess.CompletedProcess(cmd, exit_code, "", "")
        return run

    def test_failed_download_does_not_reuse_old_video(self):
        old = self.work / "video.mp4"
        old.write_bytes(b"old-video")
        (self.work / "video.info.json").write_text('{"title":"old source"}')
        with patch.object(download.shutil, "which", return_value="yt-dlp"), patch.object(
            download.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "failed")
        ), self.assertRaises(SystemExit):
            download.download_url("https://example.com/new", self.work)
        self.assertEqual(b"old-video", old.read_bytes())

    def test_failed_captions_do_not_reuse_old_subtitles_or_info(self):
        (self.work / "video.en.vtt").write_text("stale")
        (self.work / "video.info.json").write_text('{"title":"old source"}')
        with patch.object(download.shutil, "which", return_value="yt-dlp"), patch.object(
            download.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "failed")
        ):
            result = download.fetch_captions("https://example.com/new", self.work)
        self.assertIsNone(result["subtitle_path"])
        self.assertNotEqual("old source", result["info"].get("title"))

    def test_native_chinese_subtitles_and_provenance(self):
        info = {"title": "中文", "language": "zh", "subtitles": {"zh-Hans": [{}]}}
        with patch.object(download.shutil, "which", return_value="yt-dlp"), patch.object(
            download.subprocess, "run", side_effect=self.fake_ytdlp(info)
        ):
            result = download.fetch_captions("https://example.com/zh", self.work)
        self.assertIsNotNone(result["subtitle_path"])
        self.assertEqual("zh-Hans", result["subtitle_info"]["language"])
        self.assertEqual("manual", result["subtitle_info"]["kind"])
        self.assertEqual("原生字幕", transcribe.parse_vtt(result["subtitle_path"])[0]["text"])

    def test_source_language_region_falls_back_to_same_language(self):
        info = {"language": "zh-CN", "subtitles": {"en": [{}], "zh-Hans": [{}]}}
        with patch.object(download.shutil, "which", return_value="yt-dlp"), patch.object(
            download.subprocess, "run", side_effect=self.fake_ytdlp(info)
        ):
            result = download.fetch_captions("https://example.com/zh", self.work)
        self.assertEqual("zh-Hans", result["subtitle_info"]["language"])

    def test_new_media_survives_subtitle_command_failure(self):
        info = {"title": "new source", "subtitles": {}}
        with patch.object(download.shutil, "which", return_value="yt-dlp"), patch.object(
            download.subprocess, "run", side_effect=self.fake_ytdlp(info, media=True, exit_code=1)
        ):
            result = download.download_url("https://example.com/new", self.work)
        self.assertTrue(result["downloaded"])
        self.assertEqual(b"new-video", Path(result["video_path"]).read_bytes())
        self.assertEqual("new source", result["info"]["title"])

    def test_empty_fresh_video_is_not_success(self):
        def empty_media(cmd, **kwargs):
            result = self.fake_ytdlp({"title": "new source"})(cmd, **kwargs)
            if "-o" in cmd:
                (Path(cmd[cmd.index("-o") + 1]).parent / "video.mp4").touch()
            return result
        with patch.object(download.shutil, "which", return_value="yt-dlp"), patch.object(
            download.subprocess, "run", side_effect=empty_media
        ), self.assertRaises(SystemExit):
            download.download_url("https://example.com/new", self.work)

    def test_untrusted_subtitle_language_cannot_escape_output_directory(self):
        info = {"language": "../../escape", "subtitles": {"../../escape": [{}]}}
        with patch.object(download.shutil, "which", return_value="yt-dlp"), patch.object(
            download.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(info), "")
        ) as run:
            result = download.fetch_captions("https://example.com/new", self.work)
        self.assertIsNone(result["subtitle_path"])
        self.assertEqual(1, run.call_count)

    def test_auto_subtitles_avoid_translation_by_default(self):
        info = {"language": "zh", "automatic_captions": {
            "en": [{"url": "https://example.com/sub?tlang=en"}],
            "zh-orig": [{"url": "https://example.com/sub?lang=zh"}],
        }}
        with patch.object(download.shutil, "which", return_value="yt-dlp"), patch.object(
            download.subprocess, "run", side_effect=self.fake_ytdlp(info)
        ):
            result = download.fetch_captions("https://example.com/zh", self.work)
        self.assertEqual("zh-orig", result["subtitle_info"]["language"])
        self.assertEqual("automatic", result["subtitle_info"]["kind"])

    def test_explicit_translation_is_labeled(self):
        info = {"language": "zh", "automatic_captions": {
            "en": [{"url": "https://example.com/sub?tlang=en"}],
            "zh-orig": [{"url": "https://example.com/sub?lang=zh"}],
        }}
        with patch.object(download.shutil, "which", return_value="yt-dlp"), patch.object(
            download.subprocess, "run", side_effect=self.fake_ytdlp(info)
        ):
            result = download.fetch_captions("https://example.com/zh", self.work, subtitle_lang="en")
        self.assertEqual("en", result["subtitle_info"]["language"])
        self.assertEqual("translated", result["subtitle_info"]["kind"])

    def test_vtt_both_timestamp_forms_and_rolling_duplicates(self):
        path = self.work / "captions.vtt"
        path.write_text(
            "WEBVTT\n\n00:01.250 --> 00:02.500 align:start\nHello\n\n"
            "00:00:02.500 --> 00:00:04.000\nHello world\n\n"
            "01:02:03.125 --> 01:02:04.000\nLater\n", encoding="utf-8"
        )
        self.assertEqual([
            {"start": 1.25, "end": 4.0, "text": "Hello world"},
            {"start": 3723.12, "end": 3724.0, "text": "Later"},
        ], transcribe.parse_vtt(str(path)))


class SetupCliTests(unittest.TestCase):
    def test_keyless_first_run_is_ready_without_install_or_config_write(self):
        with patch.object(setup, "_check_binaries", return_value=[]), patch.object(
            setup, "_have_api_key", return_value=(False, None)
        ), patch.object(setup, "is_first_run", return_value=True), patch.object(
            setup, "get_config", return_value={"detail": "balanced"}
        ), patch.object(setup, "_scaffold_env") as scaffold, contextlib.redirect_stderr(io.StringIO()) as stderr:
            self.assertTrue(setup._status()["can_proceed"])
            self.assertEqual(0, setup.cmd_check())
            self.assertEqual("", stderr.getvalue())
            scaffold.assert_not_called()

    def test_missing_binaries_remain_a_blocker_without_an_api_key(self):
        with patch.object(setup, "_check_binaries", return_value=["ffmpeg"]), patch.object(
            setup, "_have_api_key", return_value=(False, None)
        ), patch.object(setup, "is_first_run", return_value=True), patch.object(
            setup, "get_config", return_value={"detail": "balanced"}
        ), contextlib.redirect_stderr(io.StringIO()):
            self.assertFalse(setup._status()["can_proceed"])
            self.assertEqual(2, setup.cmd_check())

    def test_keyless_install_completes_without_requesting_a_secret(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(
            setup, "CONFIG_DIR", Path(directory)
        ), patch.object(setup, "CONFIG_FILE", Path(directory) / ".env"), patch.object(
            setup, "_check_binaries", return_value=[]
        ), patch.object(setup, "_have_api_key", return_value=(False, None)), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, setup.cmd_install())
            self.assertIn("SETUP_COMPLETE=true", setup.CONFIG_FILE.read_text())

    def test_help_and_bad_arguments_never_install(self):
        for argv, code in ((["--help"], 0), (["--chekc"], 2), (["--check", "oops"], 2)):
            with self.subTest(argv=argv), patch.object(sys, "argv", ["setup.py", *argv]), patch.object(
                setup, "cmd_install", return_value=0
            ) as install, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    setup.main()
                self.assertEqual(code, raised.exception.code)
                install.assert_not_called()

    def test_existing_setup_modes(self):
        for argv, name in (([], "cmd_install"), (["--check"], "cmd_check"), (["--json"], "cmd_json")):
            with self.subTest(argv=argv), patch.object(sys, "argv", ["setup.py", *argv]), patch.object(
                setup, name, return_value=0
            ) as command:
                self.assertEqual(0, setup.main())
                command.assert_called_once_with()


class WhisperCompletenessTests(unittest.TestCase):
    def test_video_chunk_pipeline_preserves_completeness(self):
        with tempfile.TemporaryDirectory() as directory:
            audio = Path(directory) / "audio.mp3"
            audio.write_bytes(b"abc")
            status = {}
            chunks = [(Path("one"), 0), (Path("bad"), 10), (Path("last"), 20)]
            def transcribe_file(backend, key, path):
                if path.name == "bad":
                    raise SystemExit("unavailable")
                return [{"start": 1, "end": 2, "text": path.name}]
            with patch.object(whisper, "extract_audio", return_value=audio), patch.object(
                whisper, "audio_duration", return_value=30
            ), patch.object(whisper, "MAX_UPLOAD_BYTES", 1), patch.object(whisper, "split_audio", return_value=chunks), patch.object(
                whisper, "_transcribe_file", side_effect=transcribe_file
            ), contextlib.redirect_stderr(io.StringIO()):
                segments, backend = whisper.transcribe_video("video.mp4", audio, "groq", "test", completeness=status)
            self.assertEqual("groq", backend)
            self.assertEqual([1, 21], [segment["start"] for segment in segments])
            self.assertEqual({"status": "partial", "missing_intervals": [{"start": 10, "end": 20}]}, status)

    def test_partial_chunks_record_missing_intervals_and_shift_successes(self):
        status = {}
        def one(path):
            if path.name == "bad":
                raise SystemExit("HTTP 503")
            return [{"start": 1.0, "end": 2.0, "text": path.name}]
        segments = whisper.transcribe_chunks(
            [(Path("first"), 0), (Path("bad"), 10), (Path("last"), 20)], one,
            completeness=status, total_seconds=30,
        )
        self.assertEqual([1.0, 21.0], [segment["start"] for segment in segments])
        self.assertEqual("partial", status["status"])
        self.assertEqual([{"start": 10, "end": 20}], status["missing_intervals"])

    def test_complete_and_all_failed_chunks(self):
        status = {}
        whisper.transcribe_chunks([(Path("one"), 0)], lambda _: [], completeness=status, total_seconds=10)
        self.assertEqual("complete", status["status"])
        self.assertEqual([], status["missing_intervals"])
        def fail(_):
            raise SystemExit("unavailable")
        with self.assertRaises(SystemExit):
            whisper.transcribe_chunks([(Path("one"), 0)], fail, completeness=status, total_seconds=10)
        self.assertEqual("none", status["status"])
        self.assertEqual([{"start": 0, "end": 10}], status["missing_intervals"])

    def test_watch_report_surfaces_partial_transcript(self):
        with tempfile.TemporaryDirectory() as directory:
            def partial(*args, **kwargs):
                kwargs["completeness"].update({"status": "partial", "missing_intervals": [{"start": 10, "end": 20}]})
                return [{"start": 1, "end": 2, "text": "heard"}], "groq"
            stdout = io.StringIO()
            with patch.object(sys, "argv", ["watch", "local.mp4", "--detail", "transcript", "--out-dir", directory]), patch.object(
                watch, "get_config", return_value={"detail": "transcript"}
            ), patch.object(watch, "download", return_value={"video_path": "local.mp4", "info": {}}), patch.object(
                watch, "get_metadata", return_value={"duration_seconds": 30, "has_audio": True}
            ), patch.object(watch, "load_api_key", return_value=("groq", "test-key")), patch.object(
                watch, "transcribe_video", side_effect=partial
            ), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(0, watch.main())
            self.assertIn("partial", stdout.getvalue())
            self.assertIn("00:10", stdout.getvalue())
            self.assertIn("00:20", stdout.getvalue())
            artifact = json.loads((Path(directory) / "transcript.json").read_text())
            self.assertEqual("partial", artifact["completeness"]["status"])
            self.assertEqual("full source audio", artifact["completeness_scope"])
            self.assertEqual({"start": None, "end": None}, artifact["segment_range"])


if __name__ == "__main__":
    unittest.main()
