# Retrieval Contract

Read this file when invoking the fetcher, diagnosing acquisition, or handling video/partial results. Public fetching requires no login, cookies, browser runtime or MCP. Authenticated recovery additionally requires `single-note-recovery.md`.

## Inputs And Options

`fetch_note.py` accepts a URL or complete pasted share text and returns structured JSON with `work_dir`, `manifest`, `text_file`, `canonical_url`, `access_mode`, metadata and ordered media paths.

- `--out-dir DIR`: retain artifacts at a specified location.
- `--cookie-file FILE`: use an explicitly authorized Netscape or browser/MCP JSON cookie file. Resolve only that service's file; adapt in memory without copying, printing or committing credentials.
- `--html-file FILE`: parse a user-saved page.
- `--metadata-only`: diagnose parsing without downloading images; this is not OCR evidence.
- `--browser`: use an explicitly authorized dedicated session; `--headed` exposes it. Do not combine this with `--cookie-file` or `--html-file`.

The public path uses Python's standard library. JavaScript-only page state can require `yt_dlp`; first check existing isolated interpreters, then use a task-local install only when covered. Playwright is needed only for `--browser`. Do not change system packages or enter an account merely because public retrieval failed.

Use the token-free `canonical_url` for citations and keep signed retrieval URLs local. `manifest.json` owns media order, completeness, missing pages and per-item status.

## Bounded Public Mobile Recovery

An ordinary desktop `/login` redirect is not a global access verdict. For anonymous HTTP only, the fetcher makes at most one additional page request using a normal mobile browser profile and the same note's `/discovery/item/ID` share page. The target must come from the supplied exact note URL or one validated first-party `redirectPath`; preserve actual query parameters, never generate a token or guess a note ID.

Validate host, port, path and identity before the additional request and again against the returned page/state. Conflicting note IDs or ambiguous/external targets are rejected. A captcha/security block or HTTP 401/403/404/429 does not trigger this fallback. A second ordinary login response ends the attempt; no endpoint search, retries, session discovery or QR login follows automatically.

Successful manifests retain `access_mode=http` and add `retrieval_route=public_mobile`; direct public HTTP is `public_http`. Other routes are `cookie_http`, `saved_html` and `dedicated_browser`. A failed mobile attempt adds the token-free `public_mobile_attempted=true` diagnostic. None of these markers proves OCR, video transcription or a valid account session.

## Identity And Failure Classification

- **Expired/invalid share URL:** after one confirmed `404`, request a fresh share URL, original explore URL, saved HTML or screenshots.
- **`login_required`:** the selected route still lacks usable content after its bounded public attempt, or an explicitly selected session lacks a login marker. This does not prove every route needs login or another session expired. Preserve `session_source`, `session_validity=unverified` and `content_verified=false`. Do not repeat the exhausted public attempt. If no-login is required, offer saved HTML/images or a fresh share link; otherwise use `single-note-recovery.md` only within account authorization.
- **`security_block`:** captcha, risky IP or verification. Stop; do not cycle endpoints, accounts or proxies.
- **`video_handoff`:** identity/metadata were resolved, but video acquisition, transcript and frames remain unfinished.
- **No primary note/media sequence:** report a schema or identity problem; do not reinterpret it as a video or login failure.
- **Unverified identity:** a known note ID must match. Without one, require exactly one primary note in the detail map; recommendations are not substitutes.
- **Partial image download:** retain successful pages, report `ok: false`, `completeness`, `missing_pages` and exact failures; do not call the transcription complete.

Canonical IDs and type hints from redirects are diagnostic metadata, not acquired content. Do not claim page metadata proves image or spoken content.

## Video Handoff

The manifest may contain `handoff.source_url` and actual allowed-CDN `media_urls`; `downloaded=false`, `completeness=none` and `not_started` correctly describe unfinished acquisition even when metadata extraction exits successfully.

Use `watch` on a public resolved source. An authorized browser media URL may be tried directly, but never pass its browser cookies to `watch`, derive a CDN URL from a key, or repeatedly retry rejection. If media remains protected, use a user-saved video or authorized local download. Start private media with `--no-whisper` unless external audio transfer is separately covered.
