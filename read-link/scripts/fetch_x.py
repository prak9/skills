#!/usr/bin/env python3
"""Acquire one public X post through FxEmbed; retain provenance, not a completeness claim.

Standard library only. No account access, transcription, translation or Notion writes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


API_HOST = "api.fxtwitter.com"
IMAGE_HOSTS = ("pbs.twimg.com",)
MAX_JSON = 10 * 1024 * 1024
MAX_IMAGE = 40 * 1024 * 1024
MAX_IMAGES = 40
TEXT_BLOCKS = {"unstyled", "paragraph", "header-one", "header-two", "header-three",
               "blockquote", "unordered-list-item", "ordered-list-item", "code-block"}


class FetchError(RuntimeError):
    pass


def validate_url(url: str, hosts: tuple[str, ...]) -> None:
    try:
        p = urllib.parse.urlsplit(url)
        valid = (p.scheme == "https" and p.hostname in hosts and p.port in (None, 443)
                 and p.username is None and p.password is None)
    except ValueError:
        valid = False
    if not valid:
        raise FetchError("URL is outside the selected HTTPS host boundary")


def parse_url(source: str) -> tuple[str, str]:
    urls = re.findall(r"https?://[^\s<>\"'，。]+", source)
    if len(urls) != 1:
        raise FetchError("Supply exactly one X/Twitter post URL")
    url = urls[0].rstrip(").,;!?）")
    validate_url(url, ("x.com", "www.x.com", "twitter.com", "www.twitter.com", "mobile.twitter.com"))
    p = urllib.parse.urlsplit(url)
    match = re.fullmatch(r"/([A-Za-z0-9_]+)/status/(\d{2,20})(?:/(?:video|photo)/\d+)?/?", p.path)
    if not match:
        match = re.fullmatch(r"/i/(?:web/status|status|article)/(\d{2,20})/?", p.path)
        if not match:
            raise FetchError("Expected a post URL; resolve article-only/profile/short links in the browser first")
        # Article IDs are not necessarily tweet IDs; do not send them to the post endpoint.
        if "/article/" in p.path:
            raise FetchError("Resolve this article to its containing post before using the post endpoint")
        post_id = match[1]
        return f"https://x.com/i/status/{post_id}", post_id
    return f"https://x.com/{match[1]}/status/{match[2]}", match[2]


class Redirects(urllib.request.HTTPRedirectHandler):
    def __init__(self, hosts):
        super().__init__()
        self.hosts = hosts

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl, self.hosts)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def request_bytes(url: str, hosts: tuple[str, ...], limit: int) -> bytes:
    validate_url(url, hosts)
    opener = urllib.request.build_opener(Redirects(hosts))
    request = urllib.request.Request(url, headers={"User-Agent": "read-link/1.0", "Accept": "*/*"})
    try:
        with opener.open(request, timeout=25) as response:
            validate_url(response.geturl(), hosts)
            data = response.read(limit + 1)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise FetchError(f"Public retrieval failed: {exc}") from exc
    if len(data) > limit:
        raise FetchError("Response exceeded the bounded download size")
    return data


def image_suffix(data: bytes) -> str:
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return ".webp"
    raise FetchError("Image response has an unsupported signature (possibly an access page)")


def media_inventory(post: dict, article: dict) -> list[dict]:
    items = []

    def add(raw, role, order):
        if not isinstance(raw, dict):
            items.append({"type": "unknown", "url": None, "role": role,
                          "reading_order": order, "raw": raw})
            return
        info = raw.get("media_info") or {}
        url = raw.get("url") or info.get("original_img_url")
        kind = raw.get("type") or ("photo" if info.get("original_img_url") else "unknown")
        items.append({"type": kind, "url": url, "role": role, "reading_order": order,
                      "media_id": raw.get("media_id") or raw.get("id"), "raw": raw})

    media = post.get("media") or {}
    if isinstance(media.get("all"), list):
        for raw in media["all"]:
            add(raw, "post_attachment", "provider_order")
    else:
        for key in ("photos", "videos"):
            for raw in media.get(key) or []:
                add(raw, "post_attachment", "unverified")
    if article.get("cover_media"):
        add(article["cover_media"], "article_cover", "cover")
    for raw in article.get("media_entities") or []:
        add(raw, "article_inventory", "unverified")
    for index, item in enumerate(items, 1):
        item.update(index=index, path=None, status="not_attempted", inspection="pending")
    return items


def extract(data: dict, source: str) -> dict:
    canonical, post_id = parse_url(source)
    if not isinstance(data, dict) or data.get("code") != 200:
        raise FetchError("Provider returned an error or unsupported response envelope")
    post = data.get("status") or data.get("tweet")
    if not isinstance(post, dict) or str(post.get("id")) != post_id:
        raise FetchError("Response does not match the requested post ID")
    if post.get("type") == "tombstone" or (post.get("author") or {}).get("protected"):
        raise FetchError("Post unavailable or protected; do not retry through mirrors")
    article = post.get("article") or {}
    if not isinstance(article, dict):
        raise FetchError("Unsupported article schema")
    content = article.get("content") or {}
    blocks = content.get("blocks") if isinstance(content, dict) else None
    gaps = []
    text = post.get("text") if isinstance(post.get("text"), str) else ""
    basis = "post_text"
    coverage = "provider_payload" if text else "missing"
    if article:
        if isinstance(blocks, list) and blocks:
            parts = []
            for index, block in enumerate(blocks, 1):
                if not isinstance(block, dict) or not isinstance(block.get("text"), str):
                    gaps.append(f"malformed_block:{index}")
                    continue
                parts.append(block["text"])
                if block.get("type") not in TEXT_BLOCKS:
                    gaps.append(f"unresolved_block:{index}:{block.get('type')}")
            text = "\n\n".join(parts)
            basis = "article_blocks"
            coverage = "partial" if gaps else "provider_payload" if text.strip() else "missing"
        else:
            text = article.get("preview_text") or text
            basis = "article_preview"
            coverage = "preview_only" if text else "missing"
            gaps.append("article_body_missing")
    if post.get("truncated"):
        gaps.append("provider_truncated")
        coverage = "partial"
    return {
        "schema_version": 1, "source_url": canonical, "post_id": post_id,
        "provider": "FxEmbed (third-party public extraction)", "scope": "single_post",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "published_at": post.get("created_at"), "author": post.get("author"),
        "title": article.get("title"), "text": text, "text_basis": basis,
        "text_coverage": coverage, "source_completeness": "unverified",
        "block_count": len(blocks) if isinstance(blocks, list) else 0,
        "blocks": blocks, "article_entities": content.get("entityMap") if isinstance(content, dict) else None,
        "gaps": gaps, "media": media_inventory(post, article),
        "quote": post.get("quote"), "replying_to": post.get("replying_to"),
        "replying_to_status": post.get("replying_to_status"),
        "thread": "not_fetched", "ocr": "not_performed", "transcription": "not_performed",
    }


def save(data: dict, source: str, parent: Path | None, download_images: bool) -> dict:
    result = extract(data, source)
    if parent:
        parent.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="read-link-", dir=parent))
    # Fresh attempt directory: failed retries can never adopt stale artifacts.
    (directory / "response.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (directory / "source.txt").write_text(result["text"], encoding="utf-8")
    images = [item for item in result["media"] if item["type"] in ("photo", "image")]
    if download_images:
        for image in images[:MAX_IMAGES]:
            try:
                raw = request_bytes(image["url"], IMAGE_HOSTS, MAX_IMAGE)
                path = directory / f"image-{image['index']:03d}{image_suffix(raw)}"
                path.write_bytes(raw)
                image.update(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), status="downloaded")
            except (FetchError, OSError, TypeError) as exc:
                image.update(status="failed", error=str(exc))
                break
    downloaded = sum(item["status"] == "downloaded" for item in images)
    result.update(
        image_downloads=("not_applicable" if not images else "not_requested" if not download_images
                         else "complete" if downloaded == len(images) else "partial" if downloaded else "none"),
        missing_images=[item["index"] for item in images if item["status"] != "downloaded"],
        work_dir=str(directory), manifest=str(directory / "manifest.json"),
    )
    (directory / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="One public X/Twitter post URL or pasted share text")
    parser.add_argument("--json-file", type=Path, help="Replay a saved FxEmbed JSON response without metadata requests")
    parser.add_argument("--out-dir", type=Path, help="Parent for a fresh attempt directory; never overwrites earlier attempts")
    parser.add_argument("--download-images", action="store_true", help="Download reported photos, not videos; OCR remains a separate step")
    args = parser.parse_args(argv)
    try:
        canonical, post_id = parse_url(args.source)
        if args.json_file:
            with args.json_file.open("rb") as stream:
                raw = stream.read(MAX_JSON + 1)
            if len(raw) > MAX_JSON:
                raise FetchError("Saved JSON exceeds size limit")
        else:
            raw = request_bytes(f"https://{API_HOST}/2/status/{post_id}", (API_HOST,), MAX_JSON)
        data = json.loads(raw)
        result = save(data, canonical, args.out_dir, args.download_images)
        # Do not print a long third-party article into a conversational tool result.
        print(json.dumps({key: result[key] for key in (
            "work_dir", "manifest", "post_id", "text_basis", "text_coverage", "block_count",
            "source_completeness", "image_downloads", "missing_images", "gaps")}, ensure_ascii=False, indent=2))
        return 4 if result["text_coverage"] in ("preview_only", "partial", "missing") or (
            args.download_images and result["missing_images"]) else 0
    except (FetchError, ValueError, OSError, TypeError, AttributeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
