# Retrieval Contract

Read this file when invoking the fetcher, diagnosing acquisition, or handling video/partial results. Public fetching remains the default; authenticated recovery additionally requires `single-note-recovery.md`.

## Inputs And Options

`fetch_note.py` accepts a URL or complete pasted share text and returns structured JSON with `work_dir`, `manifest`, `text_file`, `canonical_url`, `access_mode`, metadata and ordered media paths.

- `--out-dir DIR`: retain artifacts at a specified location.
- `--cookie-file FILE`: use an explicitly authorized Netscape or browser/MCP JSON cookie file. Resolve only that service's file; adapt in memory without copying, printing or committing credentials.
- `--html-file FILE`: parse a user-saved page.
- `--metadata-only`: diagnose parsing without downloading images; this is not OCR evidence.
- `--browser`: use an explicitly authorized dedicated session; `--headed` exposes it. Do not combine this with `--cookie-file` or `--html-file`.

The public path uses Python's standard library. JavaScript-only page state can require `yt_dlp`; first check existing isolated interpreters, then use a task-local install only when covered. Playwright is needed only for `--browser`. Do not change system packages or enter an account merely because public retrieval failed.

Use the token-free `canonical_url` for citations and keep signed retrieval URLs local. `manifest.json` owns media order, completeness, missing pages and per-item status.

## Identity And Failure Classification

- **Expired/invalid share URL:** after one confirmed `404`, request a fresh share URL, original explore URL, saved HTML or screenshots.
- **`login_required`:** the selected route saw a login page or lacks a login marker. This does not prove another session expired. Preserve `session_source`, `session_validity=unverified` and `content_verified=false`; use `single-note-recovery.md` rather than retrying anonymously or routing to MCP.
- **`security_block`:** captcha, risky IP or verification. Stop; do not cycle endpoints, accounts or proxies.
- **`video_handoff`:** identity/metadata were resolved, but video acquisition, transcript and frames remain unfinished.
- **No primary note/media sequence:** report a schema or identity problem; do not reinterpret it as a video or login failure.
- **Unverified identity:** a known note ID must match. Without one, require exactly one primary note in the detail map; recommendations are not substitutes.
- **Partial image download:** retain successful pages, report `ok: false`, `completeness`, `missing_pages` and exact failures; do not call the transcription complete.

Canonical IDs and type hints from redirects are diagnostic metadata, not acquired content. Do not claim page metadata proves image or spoken content.

## Video Handoff

The manifest may contain `handoff.source_url` and actual allowed-CDN `media_urls`; `downloaded=false`, `completeness=none` and `not_started` correctly describe unfinished acquisition even when metadata extraction exits successfully.

Use `watch` on a public resolved source. An authorized browser media URL may be tried directly, but never pass its browser cookies to `watch`, derive a CDN URL from a key, or repeatedly retry rejection. If media remains protected, use a user-saved video or authorized local download. Start private media with `--no-whisper` unless external audio transfer is separately covered.
