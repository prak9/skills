#!/usr/bin/env python3
"""Fetch a public research PDF or parse a local copy, retaining page evidence.

Requires curl for URLs and pdftotext (Poppler) for text extraction. No installs,
credentials, browser impersonation, automatic retries or OCR are performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from urllib.parse import quote, urlsplit, urlunsplit


USER_AGENT = "InvestResearch/1.0 (public document retrieval)"


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise ValueError("source must be an HTTP(S) URL or an existing local PDF")
    if parts.username or parts.password:
        raise ValueError("credential-bearing URLs are not supported")
    return urlunsplit((parts.scheme, parts.netloc,
                      quote(parts.path, safe="/%:@!$&'()*+,;=-._~"),
                      quote(parts.query, safe="%=&/?+:;,@!$'()*-._~"), ""))


def read_pdf(source: str, output_dir: Path, *, timeout: int = 45,
             max_bytes: int = 50 * 1024 * 1024) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="pdf-", dir=output_dir))
    raw = run / "source.pdf"
    result = dict(source=source, fetched_at=datetime.now(timezone.utc).isoformat(),
                  artifact_dir=str(run.resolve()), status="fetch_failed")

    def finish(status: str, **fields) -> dict:
        result.update(status=status, **fields)
        (run / "manifest.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return result

    try:
        if source.startswith(("http://", "https://")):
            url = normalize_url(source)
            result['request_url'] = url
            if not shutil.which("curl"):
                return finish("fetch_unavailable", reason="curl is not installed")
            fetched = subprocess.run([
                "curl", "--silent", "--show-error", "--location", "--max-redirs", "5",
                "--proto", "=http,https", "--proto-redir", "=http,https",
                "--max-time", str(timeout), "--max-filesize", str(max_bytes),
                "--user-agent", USER_AGENT, "--dump-header", str(run / "headers.txt"),
                "--output", str(raw), "--write-out",
                "%{http_code}\n%{url_effective}\n%{content_type}\n", url,
            ], capture_output=True, text=True, timeout=timeout + 5)
            meta = fetched.stdout.splitlines()
            result.update(http_status=int(meta[0]) if meta and meta[0].isdigit() else None,
                          final_url=meta[1] if len(meta) > 1 else None,
                          content_type=meta[2] if len(meta) > 2 else None,
                          headers_file=str(run / "headers.txt"))
            if fetched.returncode or result['http_status'] != 200:
                return finish("fetch_failed", reason=fetched.stderr.strip() or
                              f"HTTP {result['http_status']}; not a complete successful response")
        else:
            path = Path(source).expanduser()
            if not path.is_file():
                return finish("fetch_failed", reason="local source does not exist")
            if path.stat().st_size > max_bytes:
                return finish("fetch_failed", reason="local source exceeds size limit")
            shutil.copyfile(path, raw)
            result['local_source'] = str(path.resolve())
        data = raw.read_bytes()
        result.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        if len(data) > max_bytes:
            return finish("fetch_failed", reason="download exceeds size limit")
        if not data.lstrip().startswith(b"%PDF-"):
            # A 200 HTML login/error page must never become a cited PDF.
            raw.rename(run / "non-pdf-response.bin")
            return finish("not_pdf", reason="response lacks a PDF signature")
        result['pdf_file'] = str(raw)
        if not shutil.which("pdftotext"):
            return finish("parser_unavailable", reason="pdftotext (Poppler) is not installed")
        parsed = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(raw), "-"],
                                capture_output=True, timeout=timeout)
        if parsed.returncode:
            return finish("parse_failed", reason=parsed.stderr.decode("utf-8", "replace").strip())
        text = parsed.stdout.decode("utf-8", "replace")
        pages = text.split("\f")
        if pages and not pages[-1].strip():
            pages.pop()  # Poppler terminates each physical page with form-feed.
        counts = [len(page.strip()) for page in pages]
        blank = [i + 1 for i, count in enumerate(counts) if count == 0]
        text_file = run / "pages.txt"
        text_file.write_text("\n\n".join(
            f"## PDF page {i + 1}\n{page.rstrip()}" for i, page in enumerate(pages)), encoding="utf-8")
        status = "needs_ocr" if not any(counts) else "partial_text" if blank else "text_extracted"
        return finish(status, text_file=str(text_file), page_count=len(pages),
                      page_characters=counts, empty_pages=blank,
                      parser_warnings=parsed.stderr.decode("utf-8", "replace").strip(),
                      limitation="Text extraction is not visual, completeness or source-support verification; inspect material tables and image-only passages.")
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        return finish("parse_failed" if 'pdf_file' in result else "fetch_failed", reason=str(error))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="public HTTP(S) URL or local PDF")
    parser.add_argument("--output-dir", type=Path, required=True, help="research artifacts outside the skill repository")
    parser.add_argument("--timeout", type=int, default=45, help="seconds per download/extraction")
    args = parser.parse_args()
    if not 1 <= args.timeout <= 300:
        parser.error("timeout must be between 1 and 300 seconds")
    result = read_pdf(args.source, args.output_dir, timeout=args.timeout)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'text_extracted' else 2


if __name__ == "__main__":
    raise SystemExit(main())
