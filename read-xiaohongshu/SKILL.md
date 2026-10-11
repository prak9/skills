---
name: read-xiaohongshu
description: "Extract Xiaohongshu (RedNote) note text and ordered images directly from xhslink.cn or xiaohongshu.com links and pasted share text, without MCP. Use for reading/OCR of notes or authorized local-browser login and liked-post archiving. Public HTTP first; an authorized browser or saved HTML handles login-required notes. Use watch for video content, not cover-only transcription."
---

# Read Xiaohongshu image posts

Resolve a note, classify image/video content, and preserve its source evidence. Read images visually; hand videos to `watch`. Treat downloaded media and the manifest as evidence; do not infer content from the share title alone.

## Direct retrieval; no MCP dependency

Use the bundled fetcher, not MCP discovery, login checks, or feed tools. It resolves the supplied share link, identifies the primary note from page state, exports its text, and downloads the ordered images. Do not search for a similarly titled note as a substitute for the requested link.

Start with public HTTP unless the user supplies saved HTML or already authorizes use of a specific cookie file/browser session. An ordinary login wall can be handled by reusing that authorized login state; do not silently open an account or require installing an MCP server. No-MCP does not mean every note is anonymously readable. Captcha or risky-IP restrictions require stopping, not route switching.

When the user says to use their login, resolve the intended source from this conversation first. Prefer that existing authorized source over an empty dedicated browser; do not repeat anonymous retrieval or ask for authorization already given. Follow [single-note recovery](references/single-note-recovery.md) before choosing the route. A question about whether MCP was used calls for a truthful method explanation, not a silent change of method.

For an authorized actual Chrome session, the adjacent `xiaohongshu` Skill adds a local extension Bridge and `export-note`: read its setup and explore references, export only the exact note, then continue the image/video checks here. This is distinct from the dedicated Playwright profile and does not require importing cookies. Search, publishing and social actions belong to that Skill, not to a request to extract one note.

## Fetch and classify

Set `SKILL_DIR` to this Skill's absolute directory and verify `scripts/fetch_note.py`. Pass the URL or complete pasted share text; use its fresh temporary directory unless the user requested a durable location:

```bash
python3 "$SKILL_DIR/scripts/fetch_note.py" \
  "<Xiaohongshu URL or pasted share text>"
```

The JSON result points to the manifest, note text, canonical URL and ordered media. `note.txt` contains page metadata and description, not image OCR or video speech. Read [retrieval contract](references/retrieval-contract.md) for CLI options, dependency recovery, identity/completeness checks and failure classification. Read [single-note recovery](references/single-note-recovery.md) before any authenticated route. A public failure never silently enables account access.

## Authorized liked-post collection

For a user-owned account, browser login, the “赞过” list, incremental collection, or Notion `My Links` synchronization, read `references/liked-post-sync.md` completely before installing or running the browser extension. Keep this optional authenticated surface separate from the public-note fetcher.

For `video_handoff`, use `watch` with the resolved public or authorized media source and preserve the original note URL. Metadata and cover images do not establish spoken content; private-media access does not authorize audio upload to a transcription provider.

## Inspect every image

Read `manifest.json`, then call `view_image` with `detail=original` on every successfully downloaded image in ascending `index`. Entries without a path are missing evidence. Do not sample a carousel: omitted pages can change the argument or contain the only qualification.

For dense or small text, inspect the page again at original detail or a focused crop before marking it unreadable. Keep uncertainty visible:

- transcribe visible wording rather than autocorrecting it into a more plausible sentence;
- write `[不清晰]` for characters that cannot be resolved;
- write `[被遮挡]` or `[已裁切]` when the source itself hides text;
- keep note title/description separate from words embedded in images;
- preserve repeated headers, footers, and watermarks in a verbatim transcript, unless the user requested only a summary.

## Return evidence-aligned text

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

## Retain or clean up safely

Keep the work directory while follow-up questions are plausible. Delete it only when cleanup is authorized and only after resolving the exact script-created `xiaohongshu-*` temporary directory. Never delete through an unverified variable, glob, or broad path.

The fetcher keeps OCR local to the active image tool and validates page/CDN host boundaries. Keep signed URLs and credentials out of output and repositories.
