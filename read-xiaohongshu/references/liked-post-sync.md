# Authorized liked-post synchronization

Use this extension only when the user explicitly authorizes access to their own Xiaohongshu session and names the destination. Do not request passwords, SMS codes, QR contents, raw cookies, or exported browser profiles in chat.

## Boundary

- Let the user complete login or QR confirmation themselves.
- Store the dedicated browser profile under `~/.config/read-xiaohongshu/browser-profile`, never in the repository.
- Do not import an existing browser profile or discover cookies without separate explicit permission.
- Stop on captcha, login verification, HTTP blocking, `300012` risky-IP pages, missing “赞过” access, or material DOM drift. Do not rotate proxies or bypass controls.
- Rate-limit collection, preserve source URLs, and write only new notes after a destination-side deduplication check.

## 1. Check or install the isolated browser runtime

Check first:

```bash
python3 "$SKILL_DIR/scripts/setup_browser.py" --check
```

Installation changes the local environment and downloads a Chromium build. Use an existing suitable runtime first. Run installation when explicitly approved, including an applicable setup authorization already in the current request; do not ask for the same approval twice:

```bash
python3 "$SKILL_DIR/scripts/setup_browser.py" --install
```

The isolated interpreter is normally:

```text
~/.config/read-xiaohongshu/venv/bin/python
```

## 2. Establish a dedicated session

Run from the user's normal local network. Prefer a headed browser when a display is available:

```bash
~/.config/read-xiaohongshu/venv/bin/python \
  "$SKILL_DIR/scripts/login.py" --headed
```

For a remote but trusted network, omit `--headed`; the script captures `login.png` for QR scanning and waits for the session. If it reports a security restriction, stop and move the same skill/configuration to the user's normal network rather than retrying.

## 3. Collect a bounded batch

Copy the user's own profile URL from the logged-in browser when automatic discovery is unavailable. Start with ten notes:

```bash
~/.config/read-xiaohongshu/venv/bin/python \
  "$SKILL_DIR/scripts/collect_likes.py" \
  --profile-url "https://www.xiaohongshu.com/user/profile/<user-id>" \
  --max-notes 10
```

The script saves an ordered JSON manifest outside the repository, deduplicating by `note_id` while retaining signed URLs for retrieval. It checks authentication and security restrictions before collecting each batch and after every scroll; a blocked run exits without publishing a successful collection. It does not extract note contents or write Notion.

## 4. Extract and write incrementally

For each manifest item:

1. Deduplicate by the stable, lowercase `note_id`, using the local ledger and a destination-side check. Normalize existing Xiaohongshu destination URLs to `/explore/<note_id>` with query and fragment removed for comparison: signed tokens and share parameters change without creating a new note. Preserve the original signed URL for retrieval. If that note already exists, mark it as skipped; do not create a duplicate.
2. Run `fetch_note.py` for image notes and inspect every image at original detail. Route video notes to `watch`.
3. Create one Notion page only after extraction succeeds or is explicitly labeled partial.
4. Map the `My Links` properties as follows:
   - `Name`: note title
   - `URL`: canonical Xiaohongshu note URL (`https://www.xiaohongshu.com/explore/<note_id>`, without share query parameters)
   - `Tags`: `小红书`, `点赞`, plus `图文` or `视频`
   - page body: source description, ordered image transcript or timestamped video summary, limitations, and sync time
5. Record the Notion page ID and source note ID in the local append-only sync ledger only after the Notion create call succeeds.

Use a bounded first batch and inspect the resulting pages before expanding within the authorized collection scope; the batch is a verification checkpoint, not a mandatory reapproval. Stop after repeated retrieval failures, schema drift, authentication loss, rate limiting, or any destination mismatch. Report collected, skipped, and failed counts separately; a successful sample does not mean a requested full synchronization is complete.
