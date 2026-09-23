# Single-note login recovery

Use this branch when a public note resolves to an ordinary login page, or the user requests retrieval through an authorized local browser. No MCP service is needed or checked. This is distinct from captcha or risky-IP restrictions, which require stopping. Do not retry anonymously through the login `redirectPath`: the ID/type in that target are diagnostic hints only.

## Authorization and runtime

Use an already applicable authorization for the user's own dedicated browser session; otherwise ask once whether to use it for this note. Permission merely to edit this skill, or merely receiving a link, does not authorize opening that profile. Never request passwords, SMS codes or cookie values in chat. A configured profile alone is not permission; once the intended session is authorized, do not ask again for each read within that scope.

## Reuse an authorized MCP cookie file without MCP

When the user authorizes reusing their existing MCP login, locate that service's cookie-file path from its local configuration. Do not call MCP tools, scan unrelated profiles, or print credential values. A service access token is not a Xiaohongshu cookie; a note's `xsec_token` is not an account session either.

```bash
python3 "<SKILL_DIR>/scripts/fetch_note.py" "<original share or note URL>" \
  --cookie-file "<authorized service cookie-file path>"
```

The reader accepts Netscape cookies, a JSON cookie array, or an object with a `cookies` array (browser/MCP exports). JSON entries use `name`, `value`, `domain`, optional `path`, `secure`, `expires` and `httpOnly`; unrelated storage fields are ignored. It reads the file without modifying it, adapts cookies in memory, filters unrelated domains and expired entries, and retains domain/path/secure scope. No converted credential file is created. Cookie presence alone does not establish a valid login: verify retrieval of the exact requested note. If still redirected to ordinary login, report that reuse did not restore access; if security verification appears, stop. Never describe metadata handoff as full video extraction.

## Optional dedicated browser runtime

Check the optional runtime without opening the account:

```bash
python3 "<SKILL_DIR>/scripts/setup_browser.py" --check
```

The result includes `venv_python`; use that interpreter. If setup/login is needed, follow the setup and session sections of [liked-post-sync.md](liked-post-sync.md), but do not run its collection steps. Login is performed by the user in the dedicated browser, with security checks unchanged. An existing authorized logged-in Chrome can instead supply saved note HTML or video through available browser tools; do not discover/import its profile or cookies.

## Read just the requested note

```bash
<venv_python> "<SKILL_DIR>/scripts/fetch_note.py" "<original share or note URL>" --browser
```

Add `--headed` when appropriate. The reader opens a fresh tab in the dedicated profile, checks session/security before and after navigation, parses only the primary note, and closes its browser context. Close other processes using this dedicated profile first; a profile lock is not a reason to kill the user's browser. It neither exports cookies nor runs the likes collector. Raw page HTML and full account state are not persisted.

- Image notes: preserve the ordered image manifest and inspect every downloaded page. Image requests retain the existing public CDN path; protected media can still fail and must remain marked missing.
- Video notes: return `video_handoff` with verified note identity and any actual media URLs. Continue with the video handoff in `SKILL.md`; do not call metadata or a cover image a transcript.
- Login expired: return `login_required`, no background login loop. Ask the user to complete normal login, then resume this note under existing authorization.
- CAPTCHA/risky IP: return `security_block` and stop, including when cookies still exist.
- Parser/runtime problem: report the actual error; do not claim all failures were login blocks.

Saved HTML remains usable with `--html-file`; prefer the original note URL for identity checking. A saved login shell is not a saved article. Keep signed source/media URLs and local artifacts out of public logs/repositories; use the canonical note URL for Notion source attribution. Existing destination and archive authorization carry forward, but create no placeholder/full-text page before content has been acquired and checked.
