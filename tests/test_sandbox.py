import json
import tempfile
import unittest
from pathlib import Path

from tools.sandbox import fetch_page, read_file, send_email


class ReadFileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "files"
        self.root.mkdir()
        (self.root / "a.txt").write_text("hello")
        (self.tmp / "secret.txt").write_text("TOP SECRET")  # outside the root

    def test_reads_inside(self):
        self.assertEqual(read_file("a.txt", root=self.root), "hello")

    def test_blocks_escape(self):
        for bad in ["../secret.txt", "/etc/passwd", "sub/../../secret.txt"]:
            self.assertEqual(read_file(bad, root=self.root), "error: access denied", bad)

    def test_blocks_symlink_escape(self):
        (self.root / "link.txt").symlink_to(self.tmp / "secret.txt")
        self.assertEqual(read_file("link.txt", root=self.root), "error: access denied")

    def test_missing_and_bad_type(self):
        self.assertEqual(read_file("nope.txt", root=self.root), "error: file not found")
        self.assertIn("error", read_file(123, root=self.root))


class FetchPageTests(unittest.TestCase):
    def test_known_and_unknown(self):
        d = Path(tempfile.mkdtemp())
        (d / "p.html").write_text("<p>hi</p>")
        self.assertEqual(fetch_page("https://x.test/p", {"https://x.test/p": "p.html"}, d), "<p>hi</p>")
        self.assertEqual(fetch_page("https://evil.test/", {}, d), "error: 404 not found")


class SendEmailTests(unittest.TestCase):
    def test_writes_outbox_only(self):
        out = Path(tempfile.mkdtemp()) / "outbox" / "emails.jsonl"
        send_email("a@b.test", "Hi", "Body", outbox=out)
        send_email("c@d.test", "Yo", "Body2", outbox=out)
        rows = [json.loads(line) for line in out.read_text().splitlines()]
        self.assertEqual([r["to"] for r in rows], ["a@b.test", "c@d.test"])


if __name__ == "__main__":
    unittest.main()
