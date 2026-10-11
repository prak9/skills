"""Local entrypoint: explicit writes, no hidden browser startup, note export."""

from __future__ import annotations

import json
import logging
import re
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / 'runtime' / 'scripts'))
import cli

WRITE_COMMANDS = {
    'publish', 'publish-video', 'fill-publish', 'fill-publish-video',
    'click-publish', 'save-draft', 'long-article', 'select-template', 'next-step',
    'post-comment', 'reply-comment', 'like-feed', 'favorite-feed', 'delete-cookies',
}
DISABLED_COMMANDS = {
    'phone-login', 'send-code', 'verify-code', 'diagnose-404',
    'check-risk', 'get-netlog', 'risk-report',
}


def cmd_status(args):
    from xhs.bridge import BridgePage
    page = BridgePage(args.bridge_url)
    running = page.is_server_running()
    cli._output({
        'bridge_running': running,
        'extension_connected': page.is_extension_connected() if running else False,
        'login_verified': False,
        'extension_directory': str(SKILL_DIR / 'runtime' / 'extension'),
    })


def cmd_inspect_page(args):
    """Read visible evidence without navigating or clicking publish again."""
    _, page = cli._connect(args)
    result = page.evaluate('''(() => ({
      url: location.href, title: document.title,
      visible_text: (document.body?.innerText || '').slice(0, 12000),
      fields: Array.from(document.querySelectorAll('textarea,input[type="text"],[contenteditable="true"]'))
        .filter(el => el.getBoundingClientRect().height > 0)
        .map(el => ({label: el.getAttribute('placeholder') || '', text: (el.value || el.innerText || '').slice(0, 12000)})),
      note_links: Array.from(document.querySelectorAll('a[href*="/explore/"],a[href*="/discovery/item/"]'))
        .slice(0, 30).map(el => ({text: el.innerText, url: el.href}))
    }))()''')
    cli._output({'verified': False, 'page_evidence': result,
                 'limitation': '当前页面可见证据，不自动判断已发布；文本可能截断'})


def snapshot_html(snapshot, expected_id):
    """Only the requested note survives export; unrelated account state is dropped."""
    url = urlsplit(snapshot.get('url', ''))
    if (url.scheme != 'https' or url.hostname not in {'www.xiaohongshu.com', 'xiaohongshu.com'}
            or url.username or url.password or url.port not in {None, 443}):
        raise ValueError('当前页面不是获准的小红书笔记')
    match = re.fullmatch(r'/(?:explore|discovery/item)/([a-fA-F0-9]{24})/?', url.path)
    if not match or match[1].lower() != expected_id.lower():
        raise ValueError('当前标签页与目标笔记不一致；请先打开准确的笔记')
    note = snapshot.get('note')
    if not isinstance(note, dict) or note.get('noteId', note.get('id', '')).lower() != expected_id.lower():
        raise ValueError('笔记状态未加载或身份不匹配')
    state = {'note': {'noteDetailMap': {expected_id: {'note': note}}}}
    data = json.dumps(state, ensure_ascii=False).replace('<', '\\u003c')
    return '<script>window.__INITIAL_STATE__=' + data + '</script>'


def cmd_export_note(args):
    from xhs.feed_detail import _check_page_accessible
    from xhs.urls import make_feed_detail_url
    out = Path(args.out_dir).expanduser()
    if not out.is_absolute():
        raise ValueError('--out-dir 必须为绝对路径')
    if out.exists() and any(out.iterdir()):
        raise ValueError('输出目录必须为空，避免覆盖已有证据')
    reader = SKILL_DIR.parent / 'read-xiaohongshu' / 'scripts' / 'fetch_note.py'
    if not reader.is_file():
        raise FileNotFoundError('需要相邻的 read-xiaohongshu Skill')
    if not re.fullmatch(r'[a-fA-F0-9]{24}', args.feed_id):
        raise ValueError('需要实际笔记的24位 ID')
    _, page = cli._connect(args)
    if args.xsec_token:
        page.navigate(make_feed_detail_url(args.feed_id, args.xsec_token))
        page.wait_for_load()
        page.wait_dom_stable()
    _check_page_accessible(page)
    snapshot = page.evaluate('''(() => ({url: location.href,
      note: window.__INITIAL_STATE__?.note?.noteDetailMap?.['''
      + json.dumps(args.feed_id) + ''']?.note}))()''')
    html = snapshot_html(snapshot or {}, args.feed_id)
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    source = out / 'source-note.html'
    with source.open('x', encoding='utf-8') as target:
        target.write(html)
    source.chmod(0o600)
    canonical = 'https://www.xiaohongshu.com/explore/' + args.feed_id
    result = subprocess.run([
        sys.executable, str(reader), canonical, '--html-file', str(source),
        '--out-dir', str(out),
    ], check=False)
    raise SystemExit(result.returncode)


def build_parser():
    parser = cli.build_parser()
    parser.description = '小红书本地适配 CLI；写操作必须先获得用户授权'
    parser.add_argument('--write-confirmed', action='store_true',
                        help='操作员确认已有针对本次对象、内容和设置的用户授权')
    # The upstream CLI centralizes argument definitions; reuse, don't duplicate.
    import argparse
    sub = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
    for name in DISABLED_COMMANDS:
        sub.choices.pop(name, None)
    sub._choices_actions[:] = [a for a in sub._choices_actions if a.dest not in DISABLED_COMMANDS]
    sub.add_parser('status', help='只检查连接，不打开浏览器或访问账号').set_defaults(func=cmd_status)
    sub.add_parser('inspect-page', help='只读当前页面证据，不重试发布').set_defaults(func=cmd_inspect_page)
    export = sub.add_parser('export-note', help='导出准确笔记并衔接现有正文/图片读取器')
    export.add_argument('--feed-id', required=True)
    export.add_argument('--xsec-token')
    export.add_argument('--out-dir', required=True)
    export.set_defaults(func=cmd_export_note)
    return parser


@contextmanager
def browser_lock():
    # Kernel releases the lock on cancellation/crash; never delete another PID's file.
    import fcntl
    lock_dir = SKILL_DIR / 'runtime' / '.local'
    lock_dir.mkdir(mode=0o700, exist_ok=True)
    with (lock_dir / 'browser.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('另一条命令正在操作浏览器；请等待完成') from None
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def validate_args(args):
    if args.bridge_url != 'ws://localhost:9333':
        raise ValueError('只支持本地 ws://localhost:9333')
    if args.command in WRITE_COMMANDS and not args.write_confirmed:
        raise ValueError('外部写操作需要用户授权；确认后使用 --write-confirmed')
    if args.command == 'reply-comment' and not (args.comment_id or args.user_id):
        raise ValueError('回复必须指定 comment-id 或 user-id')
    if len(getattr(args, 'tags', None) or []) > 10:
        raise ValueError('标签超过10个；先修改并确认，不能自动截取')
    if getattr(args, 'content', None) is not None and not args.content.strip():
        raise ValueError('评论/回复不能为空')
    for name in ('title_file', 'content_file', 'video'):
        value = getattr(args, name, None)
        if value and (not Path(value).is_absolute() or not Path(value).is_file()):
            raise ValueError(f'{name} 必须是存在的绝对文件路径')
    for value in getattr(args, 'images', None) or []:
        if not value.startswith(('https://', 'http://')) and (
            not Path(value).is_absolute() or not Path(value).is_file()
        ):
            raise ValueError('每张图片都必须存在且使用绝对路径，或使用获准的 HTTP(S) URL')


def main():
    args = build_parser().parse_args()
    logging.getLogger().setLevel(logging.WARNING)  # no routine signed-URL logs
    try:
        validate_args(args)
        if args.command == 'status':
            args.func(args)
        else:
            with browser_lock():
                args.func(args)
    except Exception as exc:
        from xhs.errors import OperationUnverifiedError
        unknown = isinstance(exc, OperationUnverifiedError)
        cli._output({'success': None if unknown else False,
                     'status': 'unknown' if unknown else 'error', 'error': str(exc)}, exit_code=2)


if __name__ == '__main__':
    main()
