#!/usr/bin/env python3
"""Parse a WebVTT subtitle file into a clean, timestamped transcript.

YouTube auto-subs emit rolling-duplicate cues (each line appears 2-3 times as it
scrolls). We dedupe consecutive identical cues and merge their time ranges.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path


TS_RE = re.compile(
    r"(?:(\d{2,}):)?(\d{2}):(\d{2})[.,](\d{3})\s+-->\s+(?:(\d{2,}):)?(\d{2}):(\d{2})[.,](\d{3})"
)
TAG_RE = re.compile(r"<[^>]+>")


def _to_seconds(h: str | None, m: str, s: str, ms: str) -> float:
    return int(h or 0) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def parse_vtt(path: str, *, diagnostics: dict | None = None) -> list[dict]:
    """Parse cues; optional diagnostics describe file parsing, not speech coverage."""
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    segments: list[dict] = []
    valid_cues = invalid_cues = empty_cues = 0
    i = 0
    while i < len(lines):
        match = TS_RE.match(lines[i])
        if not match:
            if "-->" in lines[i]:
                invalid_cues += 1
            i += 1
            continue

        start = _to_seconds(*match.groups()[:4])
        end = _to_seconds(*match.groups()[4:])
        i += 1
        if end <= start or any(int(match.groups()[index]) >= 60 for index in (1, 2, 5, 6)):
            invalid_cues += 1
            continue
        valid_cues += 1

        cue_lines: list[str] = []
        while i < len(lines) and lines[i].strip():
            cleaned = html.unescape(TAG_RE.sub("", lines[i])).strip()
            if cleaned:
                cue_lines.append(cleaned)
            i += 1

        cue_text = "\n".join(cue_lines).strip()
        if cue_text:
            segments.append({"start": round(start, 2), "end": round(end, 2), "text": cue_text})
        else:
            empty_cues += 1
        i += 1

    if diagnostics is not None:
        diagnostics.update({
            "status": "none" if not segments else "partial" if invalid_cues else "complete",
            "valid_cues": valid_cues,
            "invalid_cues": invalid_cues,
            "empty_cues": empty_cues,
        })
    return _dedupe(segments)


def _dedupe(segments: list[dict]) -> list[dict]:
    """Collapse adjacent rolling cues without merging speech across gaps."""
    out: list[dict] = []
    for index, seg in enumerate(segments):
        cue_lines = seg["text"].split("\n")
        text = " ".join(cue_lines)
        previous = segments[index - 1] if index else None
        adjacent = previous is not None and previous["start"] <= seg["start"] <= previous["end"]
        if adjacent:
            previous_lines = previous["text"].split("\n")
            if text == " ".join(previous_lines):
                out[-1]["end"] = max(out[-1]["end"], seg["end"])
                continue
            # Match complete cue lines only: a shared word or character suffix
            # can be real repetition rather than a scrolling caption window.
            for count in range(min(len(previous_lines), len(cue_lines)), 0, -1):
                if previous_lines[-count:] == cue_lines[:count]:
                    text = " ".join(cue_lines[count:])
                    break
            if not text:
                out[-1]["end"] = max(out[-1]["end"], seg["end"])
                continue
            if text.startswith(out[-1]["text"] + " "):
                out[-1]["text"] = text
                out[-1]["end"] = max(out[-1]["end"], seg["end"])
                continue
        out.append({**seg, "text": text})
    return out


def filter_range(
    segments: list[dict],
    start_seconds: float | None,
    end_seconds: float | None,
) -> list[dict]:
    """Return segments whose time range overlaps [start, end]."""
    if start_seconds is None and end_seconds is None:
        return segments
    lo = start_seconds if start_seconds is not None else float("-inf")
    hi = end_seconds if end_seconds is not None else float("inf")
    return [seg for seg in segments if seg["end"] >= lo and seg["start"] <= hi]


def format_transcript(segments: list[dict]) -> str:
    lines = []
    for seg in segments:
        start = int(seg["start"])
        stamp = f"[{start // 60:02d}:{start % 60:02d}]"
        lines.append(f"{stamp} {seg['text']}")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: transcribe.py <vtt-path>", file=sys.stderr)
        raise SystemExit(2)
    print(format_transcript(parse_vtt(sys.argv[1])))
