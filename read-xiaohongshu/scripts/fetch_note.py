#!/usr/bin/env python3
"""Resolve a public Xiaohongshu note and download its ordered image carousel."""

from __future__ import annotations

import argparse
import hashlib
import html.parser
import http.cookiejar
import json
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
MAX_HTML_BYTES = 20 * 1024 * 1024
MAX_IMAGE_BYTES = 40 * 1024 * 1024
MAX_IMAGES = 30
NOTE_HOSTS = ("xiaohongshu.com", "xhslink.cn")
IMAGE_HOSTS = ("xiaohongshu.com", "xhscdn.com")
URL_RE = re.compile(r"https?://[^\s<>\"'，。！？；、]+", re.IGNORECASE)
NOTE_ID_RE = re.compile(r"/(?:explore|discovery/item)/([0-9a-f]{16,32})(?:/|$)", re.IGNORECASE)


class FetchError(RuntimeError):
    def __init__(self, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.exit_code = exit_code


class MetaParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "meta":
            return
        values = {key.lower(): value for key, value in attrs if value is not None}
        name = values.get("property") or values.get("name")
        content = values.get("content")
        if name and content:
            self.meta[name.lower()] = content


def host_matches(host: str | None, suffixes: Iterable[str]) -> bool:
    normalized = (host or "").split(":", 1)[0].lower().rstrip(".")
    return any(normalized == suffix or normalized.endswith(f".{suffix}") for suffix in suffixes)


def validate_request_url(url: str, hosts: tuple[str, ...]) -> None:
    try:
        parsed = urllib.parse.urlsplit(url)
        valid = (
            parsed.scheme in {"http", "https"}
            and host_matches(parsed.hostname, hosts)
            and parsed.username is None and parsed.password is None
            and parsed.port in {None, 80 if parsed.scheme == "http" else 443}
        )
    except ValueError:
        valid = False
    if not valid:
        raise FetchError("URL is outside the permitted Xiaohongshu page/CDN boundary", 3)


class SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        hosts = getattr(req, "xhs_allowed_hosts", NOTE_HOSTS)
        validate_request_url(newurl, hosts)
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None:
            redirected.xhs_allowed_hosts = hosts
            # CookieProcessor must recompute cookie scope for the new URL.
            redirected.remove_header("Cookie")
            redirected.remove_header("Authorization")
        return redirected


def extract_source_url(source: str) -> str:
    match = URL_RE.search(source)
    if not match:
        raise FetchError("No HTTP(S) URL found in the supplied text", 2)
    url = match.group(0).rstrip(")]}>.,;:!?，。！？；、")
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not host_matches(parsed.hostname, NOTE_HOSTS):
        raise FetchError("Only xhslink.cn and xiaohongshu.com note URLs are supported", 2)
    validate_request_url(url, NOTE_HOSTS)
    return url


def build_opener(cookie_file: Path | None) -> urllib.request.OpenerDirector:
    handlers: list[Any] = [SafeRedirectHandler()]
    if cookie_file:
        if not cookie_file.is_file():
            raise FetchError(f"Cookie file does not exist: {cookie_file}", 2)
        jar = http.cookiejar.MozillaCookieJar(str(cookie_file))
        try:
            jar.load(ignore_discard=True, ignore_expires=True)
        except Exception as exc:
            raise FetchError(f"Could not read Netscape cookie file: {exc}", 2) from exc
        for cookie in list(jar):
            if not host_matches(cookie.domain.lstrip("."), NOTE_HOSTS):
                jar.clear(cookie.domain, cookie.path, cookie.name)
        handlers.append(urllib.request.HTTPCookieProcessor(jar))
    return urllib.request.build_opener(*handlers)


def read_limited(response: Any, limit: int) -> bytes:
    declared = response.headers.get("Content-Length")
    if declared and declared.isdigit() and int(declared) > limit:
        raise FetchError(f"Response exceeds the {limit}-byte safety limit", 4)
    data = response.read(limit + 1)
    if len(data) > limit:
        raise FetchError(f"Response exceeds the {limit}-byte safety limit", 4)
    return data


def request_url(
    opener: urllib.request.OpenerDirector,
    url: str,
    timeout: float,
    *,
    referer: str | None = None,
) -> tuple[bytes, str, str]:
    hosts = NOTE_HOSTS if referer is None else IMAGE_HOSTS
    validate_request_url(url, hosts)
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
    }
    if referer:
        headers["Referer"] = referer
    request = urllib.request.Request(url, headers=headers)
    request.xhs_allowed_hosts = hosts
    try:
        with opener.open(request, timeout=timeout) as response:
            final_url = response.geturl()
            validate_request_url(final_url, hosts)
            limit = MAX_HTML_BYTES if referer is None else MAX_IMAGE_BYTES
            return read_limited(response, limit), final_url, response.headers.get_content_type()
    except urllib.error.HTTPError as exc:
        if exc.code in {404, 410}:
            raise FetchError(
                "The Xiaohongshu share/note URL is expired, removed, or invalid (HTTP 404/410)", 3
            ) from exc
        if exc.code in {401, 403, 429}:
            raise FetchError(f"Xiaohongshu blocked public retrieval (HTTP {exc.code})", 3) from exc
        raise FetchError(f"Xiaohongshu request failed with HTTP {exc.code}", 3) from exc
    except urllib.error.URLError as exc:
        raise FetchError(f"Could not retrieve Xiaohongshu URL: {exc.reason}", 3) from exc


def decode_html(data: bytes, content_type: str) -> str:
    if content_type not in {"text/html", "application/xhtml+xml", "text/plain"}:
        raise FetchError(f"Expected an HTML note page, got {content_type}", 4)
    for encoding in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def classify_access_page(final_url: str, page: str) -> None:
    parsed = urllib.parse.urlsplit(final_url)
    if not host_matches(parsed.hostname, ("xiaohongshu.com",)):
        raise FetchError(f"Share link redirected outside Xiaohongshu: {parsed.hostname}", 3)
    blocked_markers = (
        "/website-login/captcha",
        "verifyType=",
        "当前笔记暂时无法浏览",
        "error_code=300031",
    )
    missing_markers = ("/404?", "笔记不存在", "笔记已删除")
    if any(marker in final_url or marker in page for marker in blocked_markers):
        raise FetchError(
            "Xiaohongshu redirected to login/captcha/verification; public retrieval is unavailable", 3
        )
    if any(marker in final_url or marker in page for marker in missing_markers):
        raise FetchError("The Xiaohongshu note is unavailable, removed, or expired", 3)


def extract_balanced_object(page: str, marker: str) -> str | None:
    start = page.find(marker)
    if start < 0:
        return None
    assignment = page.find("=", start + len(marker))
    if assignment < 0:
        return None
    cursor = assignment + 1
    while cursor < len(page) and page[cursor].isspace():
        cursor += 1
    if cursor >= len(page) or page[cursor] != "{":
        return None
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(cursor, len(page)):
        char = page[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {'"', "'", "`"}:
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return page[cursor : index + 1]
    return None


def parse_initial_state(page: str) -> dict[str, Any]:
    raw = None
    for marker in ("window.__INITIAL_STATE__", "window.__INITIAL_SSR_STATE__"):
        raw = extract_balanced_object(page, marker)
        if raw:
            break
    if not raw:
        raise FetchError("Could not find Xiaohongshu initial state in the page", 4)
    try:
        state = json.loads(raw)
    except json.JSONDecodeError:
        try:
            from yt_dlp.utils import js_to_json
        except ImportError as exc:
            raise FetchError(
                "The page contains JavaScript state; install the Python yt_dlp module to parse it", 4
            ) from exc
        try:
            state = json.loads(js_to_json(raw))
        except Exception as exc:
            raise FetchError(f"Could not parse Xiaohongshu initial state: {exc}", 4) from exc
    if not isinstance(state, dict):
        raise FetchError("Xiaohongshu initial state is not an object", 4)
    return state


def iter_nested_objects(root: Any, limit: int = 100_000) -> Iterable[dict[str, Any]]:
    stack = [root]
    seen: set[int] = set()
    visited = 0
    while stack and visited < limit:
        value = stack.pop()
        visited += 1
        if isinstance(value, dict):
            identity = id(value)
            if identity in seen:
                continue
            seen.add(identity)
            yield value
            stack.extend(value.values())
        elif isinstance(value, list):
            stack.extend(value)


def note_candidates(state: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[int] = set()

    note_root = state.get("note")
    if isinstance(note_root, dict):
        detail_map = note_root.get("noteDetailMap")
        if isinstance(detail_map, dict):
            for value in detail_map.values():
                candidate = value.get("note") if isinstance(value, dict) else None
                if isinstance(candidate, dict):
                    candidates.append(candidate)

    for value in iter_nested_objects(state):
        if isinstance(value.get("imageList"), list):
            candidates.append(value)

    unique: list[dict[str, Any]] = []
    for candidate in candidates:
        identity = id(candidate)
        if identity not in seen:
            seen.add(identity)
            unique.append(candidate)
    return unique


def text_value(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def select_note(state: dict[str, Any], expected_id: str | None) -> dict[str, Any]:
    candidates = note_candidates(state)
    if not candidates:
        raise FetchError("No note object with an image sequence was found", 5)

    def candidate_id(candidate: dict[str, Any]) -> str:
        return (text_value(candidate.get("noteId")) or text_value(candidate.get("id")) or "").lower()

    if expected_id:
        matches = [candidate for candidate in candidates if candidate_id(candidate) == expected_id.lower()]
        if not matches:
            raise FetchError(f"Requested note {expected_id} is absent from the page state", 5)
        return matches[0]

    # A recommendation carousel is not proof of the requested note's identity.
    note_root = state.get("note")
    detail_map = note_root.get("noteDetailMap") if isinstance(note_root, dict) else None
    if isinstance(detail_map, dict) and len(detail_map) == 1:
        key, detail = next(iter(detail_map.items()))
        primary = detail.get("note") if isinstance(detail, dict) else None
        if (isinstance(primary, dict) and re.fullmatch(r"[0-9a-f]{16,32}", str(key), re.I)
                and candidate_id(primary) == str(key).lower()):
            return primary
    raise FetchError("Cannot establish a unique primary note identity from this page", 5)


def normalize_http_url(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    url = f"https:{value}" if value.startswith("//") else value
    try:
        validate_request_url(url, IMAGE_HOSTS)
    except FetchError:
        return None
    return url


def image_url(image: dict[str, Any]) -> str | None:
    for key in ("urlDefault", "url", "originalUrl", "urlPre"):
        if candidate := normalize_http_url(image.get(key)):
            return candidate

    info_list = image.get("infoList")
    if not isinstance(info_list, list):
        return None
    by_scene: dict[str, str] = {}
    fallback: list[str] = []
    for info in info_list:
        if not isinstance(info, dict):
            continue
        candidate = normalize_http_url(info.get("url"))
        if not candidate:
            continue
        scene = text_value(info.get("imageScene")) or ""
        by_scene[scene] = candidate
        fallback.append(candidate)
    for scene in ("WB_DFT", "CRD_WM_WEBP", "WB_PRV"):
        if scene in by_scene:
            return by_scene[scene]
    return fallback[0] if fallback else None


def ordered_images(note: dict[str, Any]) -> list[dict[str, Any]]:
    raw_images = note.get("imageList")
    if not isinstance(raw_images, list) or not raw_images:
        raise FetchError("The note has no image carousel; it may be a video note", 5)
    if len(raw_images) > MAX_IMAGES:
        raise FetchError(f"Image count exceeds the {MAX_IMAGES}-page safety limit", 5)
    images: list[dict[str, Any]] = []
    for index, item in enumerate(raw_images, start=1):
        if not isinstance(item, dict):
            raise FetchError(f"Image {index} metadata is malformed", 4)
        url = image_url(item)
        if not url:
            raise FetchError(f"Image {index} has no supported Xiaohongshu CDN URL", 4)
        images.append(
            {
                "index": index,
                "url": url,
                "width": item.get("width") if isinstance(item.get("width"), int) else None,
                "height": item.get("height") if isinstance(item.get("height"), int) else None,
            }
        )
    return images


def sniff_image_type(data: bytes, content_type: str) -> tuple[str, str]:
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg", "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png", "image/png"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return ".gif", "image/gif"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return ".webp", "image/webp"
    if len(data) >= 12 and data[4:12] in {b"ftypavif", b"ftypavis"}:
        return ".avif", "image/avif"
    mapping = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/avif": ".avif",
    }
    if content_type in mapping:
        return mapping[content_type], content_type
    raise FetchError(f"Downloaded media is not a recognized image ({content_type})", 4)


def download_images(
    opener: urllib.request.OpenerDirector,
    images: list[dict[str, Any]],
    output_dir: Path,
    referer: str,
    timeout: float,
) -> None:
    image_dir = output_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    for image in images:
        try:
            data, final_url, content_type = request_url(
                opener, image["url"], timeout, referer=referer
            )
            validate_request_url(final_url, IMAGE_HOSTS)
            suffix, detected_type = sniff_image_type(data, content_type)
            relative_path = Path("images") / f"{image['index']:03d}{suffix}"
            destination = output_dir / relative_path
            if destination.exists():
                raise FetchError(f"Refusing to overwrite existing file: {destination}", 2)
            destination.write_bytes(data)
        except (FetchError, OSError) as exc:
            image.update({"status": "failed", "error": str(exc)})
            if isinstance(exc, FetchError):
                raise
            raise FetchError(f"Could not save image {image['index']}: {exc}", 4) from exc
        image.update(
            {
                "url": final_url,
                "path": str(relative_path),
                "content_type": detected_type,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "status": "downloaded",
            }
        )


def note_metadata(note: dict[str, Any], expected_id: str | None) -> dict[str, Any]:
    user = note.get("user") if isinstance(note.get("user"), dict) else {}
    return {
        "note_id": text_value(note.get("noteId")) or text_value(note.get("id")) or expected_id,
        "title": text_value(note.get("title")),
        "description": text_value(note.get("desc")) or text_value(note.get("description")),
        "author": text_value(user.get("nickname")) or text_value(user.get("name")),
        "author_id": text_value(user.get("userId")) or text_value(user.get("id")),
    }


def parse_meta_fallback(page: str) -> dict[str, str]:
    parser = MetaParser()
    parser.feed(page)
    return parser.meta


def write_manifest(output_dir: Path, manifest: dict[str, Any]) -> Path:
    path = output_dir / "manifest.json"
    if path.exists():
        raise FetchError(f"Refusing to overwrite existing file: {path}", 2)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def run(args: argparse.Namespace) -> dict[str, Any]:
    source_url = extract_source_url(args.source)
    cookie_file = Path(args.cookie_file).expanduser().resolve() if args.cookie_file else None
    opener = build_opener(cookie_file)

    if args.html_file:
        html_path = Path(args.html_file).expanduser().resolve()
        if not html_path.is_file():
            raise FetchError(f"HTML file does not exist: {html_path}", 2)
        page = html_path.read_text(encoding="utf-8")
        final_url = source_url
    else:
        data, final_url, content_type = request_url(opener, source_url, args.timeout)
        page = decode_html(data, content_type)
        classify_access_page(final_url, page)

    source_match = NOTE_ID_RE.search(urllib.parse.urlsplit(source_url).path)
    final_match = NOTE_ID_RE.search(urllib.parse.urlsplit(final_url).path)
    if source_match and final_match and source_match.group(1).lower() != final_match.group(1).lower():
        raise FetchError("The note redirect changed the requested note identity", 5)
    expected_match = source_match or final_match
    expected_id = expected_match.group(1).lower() if expected_match else None
    state = parse_initial_state(page)
    note = select_note(state, expected_id)
    images = ordered_images(note)
    metadata = note_metadata(note, expected_id)
    meta = parse_meta_fallback(page)
    metadata["title"] = metadata["title"] or text_value(meta.get("og:title"))
    metadata["description"] = metadata["description"] or text_value(meta.get("og:description"))

    if args.out_dir:
        output_dir = Path(args.out_dir).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path(tempfile.mkdtemp(prefix="xiaohongshu-"))

    if (output_dir / "manifest.json").exists():
        raise FetchError(f"Refusing to overwrite existing file: {output_dir / 'manifest.json'}", 2)
    for image in images:
        image.update({"path": None, "status": "not_attempted"})
    failure = None
    if not args.metadata_only:
        try:
            download_images(opener, images, output_dir, final_url, args.timeout)
        except FetchError as exc:
            failure = exc
    downloaded_count = sum(bool(image.get("path")) for image in images)
    completeness = "complete" if downloaded_count == len(images) else "partial" if downloaded_count else "none"
    missing_pages = [image["index"] for image in images if not image.get("path")]

    manifest = {
        "schema_version": 1,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source_url": source_url,
        "resolved_url": final_url,
        **metadata,
        "image_count": len(images),
        "downloaded": completeness == "complete",
        "completeness": completeness,
        "missing_pages": missing_pages,
        "images": images,
    }
    manifest_path = write_manifest(output_dir, manifest)
    return {
        "ok": failure is None,
        **({"error": str(failure), "exit_code": failure.exit_code} if failure else {}),
        "work_dir": str(output_dir),
        "manifest": str(manifest_path),
        "resolved_url": final_url,
        "note_id": metadata["note_id"],
        "title": metadata["title"],
        "description": metadata["description"],
        "image_count": len(images),
        "downloaded": completeness == "complete",
        "completeness": completeness,
        "missing_pages": missing_pages,
        "images": [
            {
                "index": image["index"],
                "path": str(output_dir / image["path"]) if image.get("path") else None,
            }
            for image in images
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve a Xiaohongshu image note and download its ordered images"
    )
    parser.add_argument("source", help="Xiaohongshu URL or pasted share text containing one")
    parser.add_argument("--out-dir", help="Artifact directory; defaults to a safe temporary directory")
    parser.add_argument("--cookie-file", help="Explicitly authorized Netscape-format cookie file")
    parser.add_argument("--html-file", help="Parse a locally saved note page instead of retrieving it")
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Parse image metadata without downloading images (diagnostic only)",
    )
    parser.add_argument("--timeout", type=float, default=20.0, help="Network timeout in seconds")
    return parser.parse_args()


def main() -> int:
    try:
        result = run(parse_args())
    except FetchError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return exc.exit_code
    except KeyboardInterrupt:
        print(json.dumps({"ok": False, "error": "Interrupted"}), file=sys.stderr)
        return 130
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result.get("exit_code", 0)


if __name__ == "__main__":
    raise SystemExit(main())
