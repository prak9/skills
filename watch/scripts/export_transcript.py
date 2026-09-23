#!/usr/bin/env python3
"""Export acquired captions offline; does not verify speech or publish content."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from download import _read_info
from transcribe import format_transcript, parse_vtt


def write_transcript(artifact: dict, out_dir: Path) -> dict[str, str]:
    """Save all segments, not a console preview; preserve range and failure evidence."""
    document = dict(artifact)
    segments = document["segments"]
    document["coverage"] = {
        "segment_count": len(segments),
        "first_start": min((s["start"] for s in segments), default=None),
        "last_end": max((s["end"] for s in segments), default=None),
        "speech_verified": False,
    }
    if not segments:
        document["completeness"] = {**document.get("completeness", {}), "status": "none"}
    info = document.get("info") or {}
    metadata = {key: document.get(key) for key in (
        "source", "transcript_source", "subtitle_info", "raw_subtitle_path",
        "completeness", "completeness_scope", "segment_range", "coverage", "parse_diagnostics",
    )}
    metadata["info"] = {key: info.get(key) for key in (
        "title", "uploader", "upload_date", "duration", "language", "license",
    )}
    markdown = (
        "# Acquired transcript\n\n"
        "Processing status applies only to the recorded scope, not verified full speech. "
        "Caption gaps can be silence or missing content; timestamps alone cannot decide. "
        "No speaker labels or missing words have been inferred.\n\n"
        "```json\n" + json.dumps(metadata, ensure_ascii=False, indent=2) + "\n```\n\n"
        "## Timestamped text\n\n" + format_transcript(segments) + "\n"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    contents = {
        "json": json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        "txt": "".join(s["text"] + "\n" for s in segments),
        "md": markdown,
    }
    paths = {}
    for extension, content in contents.items():
        path = out_dir / f"transcript.{extension}"
        path.write_text(content, encoding="utf-8")
        paths[extension] = str(path)
    return paths


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path, help="Saved watch transcript.json or WebVTT")
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--info-json", type=Path, help="Matching yt-dlp metadata (VTT replay only)")
    ap.add_argument("--source-url", default=None, help="Original video URL (VTT replay only)")
    ap.add_argument("--subtitle-lang", default=None, help="Acquired track language, not inferred from text")
    ap.add_argument("--subtitle-kind", choices=["manual", "automatic", "translated", "unknown"], default="unknown")
    args = ap.parse_args()
    if args.input.suffix.lower() == ".vtt":
        diagnostics = {}
        segments = parse_vtt(str(args.input), diagnostics=diagnostics)
        info = _read_info(args.info_json, args.source_url or "") if args.info_json else {}
        artifact = {
            "source": args.source_url or info.get("url") or str(args.input.resolve()),
            "info": info, "transcript_source": "captions",
            "subtitle_info": {"language": args.subtitle_lang, "kind": args.subtitle_kind},
            "raw_subtitle_path": str(args.input.resolve()),
            "parse_diagnostics": diagnostics,
            "completeness": {"status": diagnostics["status"], "missing_intervals": []},
            "completeness_scope": "acquired caption file",
            "segment_range": {"start": None, "end": None},
            "segments": segments,
        }
    else:
        artifact = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(artifact, dict) or not isinstance(artifact.get("segments"), list):
            ap.error("Expected a saved watch transcript with a segments list")
    if not artifact["segments"]:
        artifact["completeness"] = {**artifact.get("completeness", {}), "status": "none"}
    paths = write_transcript(artifact, args.out_dir)
    print(json.dumps({"artifacts": paths, "segments": len(artifact["segments"]),
                      "completeness": artifact.get("completeness")}, ensure_ascii=False, indent=2))
    return 0 if artifact["segments"] and artifact.get("completeness", {}).get("status") == "complete" else 4


if __name__ == "__main__":
    raise SystemExit(main())
