"""Fake, sandboxed tools. Each one must be safe no matter what arguments the model sends.
Errors are short text (no real filesystem paths) so they can be sent back to the model."""
import json
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
FILES_DIR = PROJECT / "fixtures" / "files"
PAGES_DIR = PROJECT / "fixtures" / "pages"
OUTBOX = PROJECT / "outbox" / "emails.jsonl"

# fetch_page never touches the network: known URLs map to local fixture pages.
PAGES = {"https://example.com/news": "news.html"}


def read_file(path: str, root: Path = FILES_DIR) -> str:
    if not isinstance(path, str):
        return "error: path must be a string"
    root = root.resolve()
    target = (root / path).resolve()  # resolve() collapses '..' and follows symlinks
    if not target.is_relative_to(root):
        return "error: access denied"
    if not target.is_file():
        return "error: file not found"
    return target.read_text()


def fetch_page(url: str, pages: dict = PAGES, pages_dir: Path = PAGES_DIR) -> str:
    if url not in pages:
        return "error: 404 not found"
    return (pages_dir / pages[url]).read_text()


def send_email(to: str, subject: str, body: str, outbox: Path = OUTBOX) -> str:
    if not all(isinstance(x, str) for x in (to, subject, body)):
        return "error: to, subject and body must be strings"
    outbox.parent.mkdir(parents=True, exist_ok=True)
    record = {"ts": time.time(), "to": to, "subject": subject, "body": body}
    with outbox.open("a") as f:
        f.write(json.dumps(record) + "\n")
    return f"email queued to {to}"
