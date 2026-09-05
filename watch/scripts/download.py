#!/usr/bin/env python3
"""Download a video via yt-dlp, or resolve a local file path.

Also fetches subtitles (manual first, then auto-generated) in VTT format so
transcribe.py can parse them without needing Whisper.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse


VIDEO_EXTS = {".mp4", ".mkv", ".webm", ".mov", ".m4v", ".avi", ".flv", ".wmv"}


def is_url(source: str) -> bool:
    if source.startswith("-"):
        return False
    parsed = urlparse(source)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def resolve_local(path: str) -> dict:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise SystemExit(f"File not found: {p}")
    if p.suffix.lower() not in VIDEO_EXTS:
        print(
            f"[watch] warning: {p.suffix} is not a known video extension, proceeding anyway",
            file=sys.stderr,
        )
    return {
        "video_path": str(p),
        "subtitle_path": None,
        "info": {"title": p.name, "url": str(p)},
        "downloaded": False,
    }


def _select_subtitle(info: dict, preferred: str | None) -> dict | None:
    """Select one track, keeping translated auto-captions out of the default."""
    tracks = []
    for field, kind in (("subtitles", "manual"), ("automatic_captions", "automatic")):
        for language, formats in (info.get(field) or {}).items():
            if (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", language)
                    or language == "live_chat" or not formats):
                continue
            translated = any(
                "tlang" in parse_qs(urlparse(item.get("url") or "").query)
                for item in formats
            )
            tracks.append({"language": language, "kind": "translated" if translated else kind})

    def matches(language: str, wanted: str) -> bool:
        language, wanted = language.lower(), wanted.lower()
        return language.split("-", 1)[0] == wanted.split("-", 1)[0]

    if preferred:
        selected = [track for track in tracks if matches(track["language"], preferred)]
        if selected:
            return min(selected, key=lambda track: (
                track["kind"] != "manual", track["kind"] == "translated",
                track["language"].lower() != preferred.lower(), track["language"],
            ))
    tracks = [track for track in tracks if track["kind"] != "translated"]
    source_language = info.get("language") or ""
    if not tracks:
        return None
    return min(tracks, key=lambda track: (
        track["kind"] != "manual",
        not (source_language and matches(track["language"], source_language)),
        not track["language"].endswith("-orig"), track["language"],
    ))


def _pick_video(out_dir: Path) -> Path | None:
    for ext in (".mp4", ".mkv", ".webm", ".mov", ".m4a", ".mp3", ".opus"):
        for candidate in out_dir.glob(f"video*{ext}"):
            if candidate.is_file() and candidate.stat().st_size > 0:
                return candidate
    for candidate in out_dir.glob("video.*"):
        if candidate.suffix.lower() in VIDEO_EXTS and candidate.is_file() and candidate.stat().st_size > 0:
            return candidate
    return None


def _download_attempt(
    url: str, out_dir: Path, *, captions_only: bool, audio_only: bool = False,
    subtitle_lang: str | None = None,
) -> dict:
    if shutil.which("yt-dlp") is None:
        raise SystemExit("yt-dlp is not installed. Install with: brew install yt-dlp")

    out_dir.mkdir(parents=True, exist_ok=True)
    # A fresh directory binds every discovered file to this attempt. Existing
    # video/subtitle artifacts are never evidence of a new download succeeding.
    attempt = Path(tempfile.mkdtemp(prefix="source-", dir=out_dir))
    metadata = subprocess.run(
        ["yt-dlp", "--skip-download", "--dump-single-json", "--no-playlist", "--", url],
        capture_output=True, text=True,
    )
    if metadata.stderr:
        print(metadata.stderr, file=sys.stderr, end="")
    try:
        raw = json.loads(metadata.stdout or "{}")
        if not isinstance(raw, dict) or not raw:
            raise ValueError("no video metadata")
    except (ValueError, TypeError):
        if not captions_only:
            raise SystemExit(f"yt-dlp did not return video metadata (exit {metadata.returncode})")
        return {"video_path": None, "subtitle_path": None, "subtitle_info": None,
                "info": {"url": url}, "downloaded": False}
    info_path = attempt / "source.info.json"
    info_path.write_text(json.dumps(raw), encoding="utf-8")
    track = _select_subtitle(raw, subtitle_lang)
    info = _read_info(info_path, url)
    if captions_only and track is None:
        return {"video_path": None, "subtitle_path": None, "subtitle_info": None,
                "info": info, "downloaded": False}
    cmd = [
        "yt-dlp",
        "--load-info-json", str(info_path),
        "--write-info-json",
        "--no-playlist",
        "--ignore-errors",
        "-o", str(attempt / "video.%(ext)s"),
    ]
    if track:
        cmd.extend([
            "--write-subs" if track["kind"] == "manual" else "--write-auto-subs",
            "--sub-langs", re.escape(track["language"]),
            "--sub-format", "vtt/best", "--convert-subs", "vtt",
        ])
    if captions_only:
        cmd.append("--skip-download")
    else:
        fmt = "ba/bestaudio" if audio_only else "bv*[height<=720]+ba/b[height<=720]/bv+ba/b"
        cmd.extend(["-N", "8", "-f", fmt, "--merge-output-format", "mp4"])
    result = subprocess.run(cmd, stdout=sys.stderr, stderr=sys.stderr)
    video = None if captions_only else _pick_video(attempt)
    if not captions_only and video is None:
        raise SystemExit(f"yt-dlp did not produce a video file in {attempt} (exit {result.returncode})")
    subtitle = attempt / f"video.{track['language']}.vtt" if track else None
    if subtitle is not None and (not subtitle.is_file() or subtitle.stat().st_size == 0):
        subtitle = None
    return {
        "video_path": str(video) if video else None,
        "subtitle_path": str(subtitle) if subtitle else None,
        "subtitle_info": track if subtitle else None,
        "info": info,
        "downloaded": video is not None,
    }


def fetch_captions(url: str, out_dir: Path, subtitle_lang: str | None = None) -> dict:
    """Fetch metadata and one manual/native VTT track without downloading video."""
    return _download_attempt(url, out_dir, captions_only=True, subtitle_lang=subtitle_lang)


def _read_info(info_path: Path, url: str) -> dict:
    info: dict = {}
    if info_path.exists():
        try:
            raw = json.loads(info_path.read_text(encoding="utf-8"))
            info = {
                "title": raw.get("title"),
                "uploader": raw.get("uploader") or raw.get("channel"),
                "duration": raw.get("duration"),
                "url": raw.get("webpage_url") or url,
            }
        except Exception as exc:
            print(f"[watch] info.json parse failed: {exc}", file=sys.stderr)
            info = {"url": url}
    return info


def download_url(
    url: str,
    out_dir: Path,
    audio_only: bool = False,
    subtitle_lang: str | None = None,
) -> dict:
    # A subtitle failure may leave a valid media file in this fresh attempt.
    return _download_attempt(url, out_dir, captions_only=False, audio_only=audio_only,
                             subtitle_lang=subtitle_lang)


def download(
    source: str,
    out_dir: Path,
    audio_only: bool = False,
    subtitle_lang: str | None = None,
) -> dict:
    if is_url(source):
        return download_url(source, out_dir, audio_only=audio_only, subtitle_lang=subtitle_lang)
    return resolve_local(source)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: download.py <url-or-path> <out-dir>", file=sys.stderr)
        raise SystemExit(2)
    result = download(sys.argv[1], Path(sys.argv[2]))
    print(json.dumps(result, indent=2))
