---
name: read-xiaohongshu
description: "Extract Xiaohongshu (RedNote) note text and ordered images directly from xhslink.cn or xiaohongshu.com links and pasted share text, without MCP. Use for reading/OCR of notes or authorized local-browser login and liked-post archiving. Public HTTP first; an authorized browser or saved HTML handles login-required notes. Use watch for video content, not cover-only transcription."
---

# Read Xiaohongshu image posts

Resolve a note, classify image/video content, and preserve its source evidence. Read images visually; hand videos to `watch`. Treat downloaded media and the manifest as evidence; do not infer content from the share title alone.

## Direct retrieval; no MCP dependency

Use the bundled fetcher, not MCP discovery, login checks, or feed tools. It resolves the supplied share link, identifies the primary note from page state, exports its text, and downloads the ordered images. Do not search for a similarly titled note as a substitute for the requested link.

Start with public HTTP unless the user supplies saved HTML or already authorizes use of a specific cookie file/browser session. An ordinary login wall can be handled by reusing that authorized login state; do not silently open an account or require installing an MCP server. No-MCP does not mean every note is anonymously readable. Captcha or risky-IP restrictions require stopping, not route switching.

## Resolve `SKILL_DIR`

Set `SKILL_DIR` to the absolute directory containing this file. Verify the bundled fetcher before use:

```bash
SKILL_DIR="<absolute path to read-xiaohongshu>"
test -f "$SKILL_DIR/scripts/fetch_note.py"
```

## 1. Fetch the note without MCP

Pass either the URL or the complete pasted share text. Use a fresh temporary directory unless the user requested a durable output location:

```bash
python3 "$SKILL_DIR/scripts/fetch_note.py" \
  "<Xiaohongshu URL or pasted share text>"
```

The script prints structured JSON containing `work_dir`, `manifest`, `text_file`, `canonical_url`, `access_mode`, note metadata, and ordered image paths. `note.txt` preserves the title, author and note description with original paragraph breaks; it is **not** image OCR or a video transcript. `manifest.json` records media order and completeness, including partial failures. Use the token-free `canonical_url` for citations; keep signed retrieval URLs local. It accepts:

- `--out-dir DIR` to retain artifacts at a specific location.
- `--cookie-file FILE` for an explicitly authorized Netscape or browser/MCP JSON cookie file. Existing MCP login cookies can be reused without invoking its service; read [single-note recovery](references/single-note-recovery.md). Resolve only the authorized service's file, never scan unrelated profiles. Adapt it in memory, without copying, printing or committing credentials.
- `--html-file FILE` to parse a page the user saved locally when direct retrieval is unavailable.
- `--metadata-only` for parser diagnosis without downloading images; this is not successful OCR evidence.
- `--browser` for a single note through an explicitly authorized dedicated session; optional `--headed` shows that browser. Do not combine it with `--cookie-file` or `--html-file`. Read [single-note recovery](references/single-note-recovery.md) before use; a public extraction failure never silently enables account access.

Public fetching uses Python's standard library. Valid JSON page state needs no extra dependency; JavaScript-only state (for example `undefined`) additionally uses `yt_dlp`. If that parser is needed but absent, first check existing isolated interpreters. Use an announced task-local install when covered by the request and environment; ask only if installation needs new permission. Playwright is needed only for `--browser`, not public fetching. Do not alter system packages or access a browser account merely because public retrieval failed.

## Authorized liked-post collection

For a user-owned account, browser login, the “赞过” list, incremental collection, or Notion `My Links` synchronization, read `references/liked-post-sync.md` completely before installing or running the browser extension. Keep this optional authenticated surface separate from the public-note fetcher.

## 2. Classify retrieval failures

- **Expired or invalid `xhslink.cn` URL:** stop after the first confirmed `404`; ask for a fresh share link, the original `xiaohongshu.com/explore/...` URL, saved HTML, or screenshots.
- **`login_required`:** ordinary login page, including `/login?redirectPath=...`. Read [single-note recovery](references/single-note-recovery.md); reuse applicable browser authorization or request it once. Saved HTML/media are alternatives. The error may include a canonical note ID and `note_type_hint`; these come from the redirect only and are not acquired content. Do not retry the login return target anonymously or route to MCP.
- **`security_block`:** captcha, risky IP or verification. Stop, report the specific restriction; do not cycle endpoints or proxies. A logged-in session does not authorize defeating these controls.
- **`video_handoff`:** primary note identified as video, with or without a cover image. Read `watch`, use the handoff as described below; this is successful metadata extraction, not completed video acquisition/transcription.
- **No note/image sequence after these checks:** report a schema/identity issue; do not assume every missing carousel is a video or claim that every parser failure requires login.
- **Unverified note identity:** a known note ID must match exactly. For a share link without an ID, the parser requires one primary note in the page's detail map; recommendations alone are insufficient. Request the original note URL or a fresh saved page if identity cannot be established.
- **Partial image download:** the fetcher stops on the first failure, retains successful images, and writes `manifest.json` with `completeness`, `missing_pages`, and per-image status. Its JSON result has `ok: false` and the CLI exits nonzero. Do not call the transcription complete; name the missing page numbers.

Do not defeat access controls, repeatedly retry a blocked endpoint, or claim that note metadata proves what the images say.

### Video handoff

The video manifest preserves the title, description and `handoff.source_url`, plus actual allowed-CDN `media_urls` when present. It intentionally reports `downloaded=false`, `completeness=none` and transcript/frames `not_started`; an exit code of zero only confirms metadata handoff. Cover images never prove spoken content.

For publicly accessible videos, use `watch` with the resolved source. When authorized browser retrieval supplies a media URL, it can be tried as the video source; do not pass browser cookies to `watch`, invent a CDN URL from a key, or keep retrying a rejected URL. If authentication is still required for media, use a user-saved video/local authorized download. Browser access is not authorization to upload private audio to a transcription provider; start with `--no-whisper` unless that transfer is covered. Preserve the original note URL when processing a CDN URL or local file.

## 3. Inspect every image

Read `manifest.json`, then call `view_image` with `detail=original` on every successfully downloaded image in ascending `index`. Entries without a path are missing evidence. Do not sample a carousel: omitted pages can change the argument or contain the only qualification.

For dense or small text, inspect the page again at original detail or a focused crop before marking it unreadable. Keep uncertainty visible:

- transcribe visible wording rather than autocorrecting it into a more plausible sentence;
- write `[不清晰]` for characters that cannot be resolved;
- write `[被遮挡]` or `[已裁切]` when the source itself hides text;
- keep note title/description separate from words embedded in images;
- preserve repeated headers, footers, and watermarks in a verbatim transcript, unless the user requested only a summary.

## 4. Return evidence-aligned text

Default format:

```markdown
来源：<resolved note URL>
标题：<note title, if present>
正文：<note description, if present>

## 图片 1
<visible text in reading order>

## 图片 2
<visible text in reading order>

## 提炼
<optional synthesis requested by the user>

## 局限
<missing pages, access restrictions, or uncertain characters>
```

When the user asks only for a summary, still inspect all pages first, then synthesize. Distinguish verbatim transcription from interpretation.

## 5. Retain or clean up safely

Keep the work directory while follow-up questions are plausible. Delete it only when cleanup is authorized and only after resolving the exact script-created `xiaohongshu-*` temporary directory. Never delete through an unverified variable, glob, or broad path.

## Security boundary

The fetcher validates HTTP(S), standard ports, and the relevant page/CDN host boundary before the initial request and every redirect. It sends no image to an OCR service; visual reading happens through the active Codex image tool. A user-authorized cookie file is read locally; only Xiaohongshu/share-domain cookies are retained, and cookie scope is recalculated on redirects.
