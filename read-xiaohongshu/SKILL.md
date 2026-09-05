---
name: read-xiaohongshu
description: "Extract ordered images and visible text from public Xiaohongshu (RedNote) image posts and share links, or collect a user's own liked posts through an explicitly authorized local browser session for incremental archiving. Use when Codex receives an xhslink.cn or xiaohongshu.com note URL, pasted Xiaohongshu share text, a request to read/OCR/transcribe a carousel, or a request to log in locally and sync liked Xiaohongshu posts into Notion. Preserve image order and evidence, keep credentials and browser state outside the repository, stop on platform security controls, and use watch for video notes."
---

# Read Xiaohongshu image posts

Resolve a public note, preserve its image order and metadata, then use visual inspection to transcribe the text. Treat downloaded images and the manifest as evidence; do not infer text from the share title alone.

## Resolve `SKILL_DIR`

Set `SKILL_DIR` to the absolute directory containing this file. Verify the bundled fetcher before use:

```bash
SKILL_DIR="<absolute path to read-xiaohongshu>"
test -f "$SKILL_DIR/scripts/fetch_note.py"
```

## 1. Fetch the note

Pass either the URL or the complete pasted share text. Use a fresh temporary directory unless the user requested a durable output location:

```bash
python3 "$SKILL_DIR/scripts/fetch_note.py" \
  "<Xiaohongshu URL or pasted share text>"
```

The script prints structured JSON containing `work_dir`, `manifest`, note metadata, and ordered image paths. It accepts:

- `--out-dir DIR` to retain artifacts at a specific location.
- `--cookie-file FILE` only when the user explicitly authorizes use of a Netscape-format cookie file. Never discover, copy, print, or commit browser cookies.
- `--html-file FILE` to parse a page the user saved locally when direct retrieval is unavailable.
- `--metadata-only` for parser diagnosis without downloading images; this is not successful OCR evidence.

The fetcher requires the Python `yt_dlp` module for robust parsing of Xiaohongshu's JavaScript state. If absent, first check existing isolated interpreters. Use an announced task-local install when covered by the request and environment; ask only if installation needs new permission. If unavailable, use supplied HTML/screenshots where possible rather than ending at an install instruction. Do not alter system packages or access a browser account merely because public retrieval failed.

## Authorized liked-post collection

For a user-owned account, browser login, the “赞过” list, incremental collection, or Notion `My Links` synchronization, read `references/liked-post-sync.md` completely before installing or running the browser extension. Keep this optional authenticated surface separate from the public-note fetcher.

## 2. Classify retrieval failures

- **Expired or invalid `xhslink.cn` URL:** stop after the first confirmed `404`; ask for a fresh share link, the original `xiaohongshu.com/explore/...` URL, saved HTML, or screenshots.
- **Captcha, login, or verification redirect:** state that public retrieval was blocked. Offer `--cookie-file` only with explicit authorization, or ask for saved HTML/screenshots.
- **No image sequence:** if the note is video, route to `watch`; otherwise report the schema mismatch and retain the page for diagnosis.
- **Unverified note identity:** a known note ID must match exactly. For a share link without an ID, the parser requires one primary note in the page's detail map; recommendations alone are insufficient. Request the original note URL or a fresh saved page if identity cannot be established.
- **Partial image download:** the fetcher stops on the first failure, retains successful images, and writes `manifest.json` with `completeness`, `missing_pages`, and per-image status. Its JSON result has `ok: false` and the CLI exits nonzero. Do not call the transcription complete; name the missing page numbers.

Do not defeat access controls, repeatedly retry a blocked endpoint, or claim that note metadata proves what the images say.

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
