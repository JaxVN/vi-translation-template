"""Kiểm thử scripts/ (stdlib unittest). Chạy: python3 -m unittest discover -s tests -v
Cần: pandoc, pyyaml (cho upstream_fetch)."""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"
PY = sys.executable


def run(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def copy_repo(dst: pathlib.Path) -> pathlib.Path:
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(".git", "build", "__pycache__"))
    (dst / "build").mkdir(exist_ok=True)
    return dst


class UpstreamFetchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.out = self.tmp / "en"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def config(self, url: str, selector: str = "article.content, article") -> pathlib.Path:
        cfg = self.tmp / "upstream.yaml"
        cfg.write_text(f'content_selector: "{selector}"\n'
                       f'chapters:\n  - {{chapter: "01", slug: "sample-chapter", url: "{url}"}}\n', encoding="utf-8")
        return cfg

    def fetch(self, cfg):
        return run([PY, "scripts/upstream_fetch.py", "--config", str(cfg), "--source-dir", str(self.out),
                    "--report", str(self.tmp / "report.json")], ROOT)

    def test_fixture_to_markdown(self):
        r = self.fetch(self.config((FIXTURES / "sample-chapter.html").as_uri()))
        self.assertEqual(r.returncode, 0, r.stderr)
        text = (self.out / "01-sample-chapter.md").read_text(encoding="utf-8")
        self.assertIn("# Sample chapter", text)
        self.assertIn("## Why it matters", text)
        self.assertIn("### Passphrases", text)
        self.assertIn("- Enable multi-factor authentication.", text)
        self.assertIn("**back up** important data & files", text)
        self.assertIn('upstream_last_reviewed: "1 March 2024"', text)
        for noise in ("Previous chapter", "Next chapter", "Publications", "Share", "Footer", "About", "var x"):
            self.assertNotIn(noise, text)
        # hash ghi trong file khớp với hash.py
        h = run([PY, "scripts/hash.py", "show", str(self.out / "01-sample-chapter.md")], ROOT).stdout.split()[0]
        self.assertIn(f'source_hash: "{h}"', text)
        # chạy lại → không đổi
        r2 = self.fetch(self.config((FIXTURES / "sample-chapter.html").as_uri()))
        self.assertEqual(json.loads((self.tmp / "report.json").read_text())["unchanged"][0]["chapter"], "01")
        self.assertEqual(r2.returncode, 0)

    def test_bad_url_writes_nothing(self):
        r = self.fetch(self.config((FIXTURES / "does-not-exist.html").as_uri()))
        self.assertEqual(r.returncode, 2)
        self.assertFalse((self.out / "01-sample-chapter.md").exists())
        self.assertEqual(len(json.loads((self.tmp / "report.json").read_text())["errors"]), 1)

    def test_missing_selector_writes_nothing(self):
        r = self.fetch(self.config((FIXTURES / "sample-chapter.html").as_uri(), selector="#no-such-id"))
        self.assertEqual(r.returncode, 2)
        self.assertIn("selector", r.stderr)
        self.assertFalse((self.out / "01-sample-chapter.md").exists())

    def test_empty_config_is_noop(self):
        r = run([PY, "scripts/upstream_fetch.py", "--config", "upstream.yaml", "--dry-run"], ROOT)
        self.assertEqual(r.returncode, 0, r.stderr)


@unittest.skipUnless((ROOT / ".is-template").exists(), "chỉ chạy trong repo template")
class RepoFlowTest(unittest.TestCase):
    """Luồng template → init.py --rights acsc → check/build/bundle, và kiểm tra OUTDATED."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = pathlib.Path(tempfile.mkdtemp())
        cls.repo = copy_repo(cls.tmp / "asd-smb-handbook-vi")
        r = run([PY, "scripts/init.py", "--repo-name", "asd-smb-handbook-vi",
                 "--title-vi", "Sổ tay an ninh mạng cho doanh nghiệp nhỏ",
                 "--source-title", "Small Business Cyber Security Handbook", "--source-id", "ACSC SMB Handbook",
                 "--source-publisher", "Australian Signals Directorate (ASD)",
                 "--source-authors", "Australian Cyber Security Centre", "--source-year", "2025",
                 "--rights", "acsc", "--source-doi", "",
                 "--source-url", "https://www.cyber.gov.au/publication/small-business-cyber-security-handbook"],
                cls.repo)
        assert r.returncode == 0, r.stdout + r.stderr

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def check(self):
        return run([PY, "scripts/check.py"], self.repo)

    def test_1_initialized(self):
        self.assertFalse((self.repo / "README.template.md").exists())
        self.assertFalse((self.repo / ".is-template").exists())
        readme = (self.repo / "README.md").read_text(encoding="utf-8")
        self.assertIn("Sổ tay an ninh mạng", readme)
        self.assertIn("<https://www.cyber.gov.au/publication/small-business-cyber-security-handbook>", readme)
        self.assertIn("Commonwealth of Australia 2025", (self.repo / "NOTICE.md").read_text(encoding="utf-8"))
        z = json.loads((self.repo / ".zenodo.json").read_text(encoding="utf-8"))
        self.assertEqual(z["related_identifiers"][0]["scheme"], "url")
        self.assertIn('url: "https://www.cyber.gov.au/', (self.repo / "CITATION.cff").read_text(encoding="utf-8"))
        r = self.check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("translation mode", r.stdout)

    def test_2_build_and_bundle(self):
        if not shutil.which("pandoc"):
            self.skipTest("không có pandoc")
        r = run(["bash", "scripts/build.sh"], self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run([PY, "scripts/bundle.py"], self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        with zipfile.ZipFile(self.repo / "build" / "site-bundle.zip") as zf:
            names = zf.namelist()
            m = json.loads(zf.read("manifest.json"))
        self.assertIn("en/01-chuong-mau.md", names)
        self.assertIn("vi/01-chuong-mau.md", names)
        self.assertEqual(m["source"]["license"], "CC-BY-4.0")
        self.assertEqual(m["source"]["url"], "https://www.cyber.gov.au/publication/small-business-cyber-security-handbook")
        self.assertIsNone(m["concept_doi"])
        self.assertEqual(m["chapters"][0]["status"], "draft")
        self.assertFalse(m["chapters"][0]["outdated"])

    def test_3_outdated_and_tamper(self):
        en = self.repo / "source" / "en" / "01-chuong-mau.md"
        original = en.read_text(encoding="utf-8")
        try:
            en.write_text(original.replace("This is the original English text", "This is the UPDATED English text"),
                          encoding="utf-8")
            r = self.check()                    # sửa tay, chưa stamp → fail
            self.assertEqual(r.returncode, 1)
            self.assertIn("source_hash không khớp", r.stdout)
            run([PY, "scripts/hash.py", "stamp", str(en)], self.repo)
            r = self.check()                    # đã stamp → OUTDATED nhưng đạt
            self.assertEqual(r.returncode, 0, r.stdout)
            self.assertIn("OUTDATED translation/01-chuong-mau.md", r.stdout)
            self.assertIn("outdated: 1", r.stdout)
            run([PY, "scripts/hash.py", "stamp-vi", "translation/01-chuong-mau.md"], self.repo)
            self.assertIn("outdated: 0", self.check().stdout)
        finally:
            en.write_text(original, encoding="utf-8")
            run([PY, "scripts/hash.py", "stamp-vi", "translation/01-chuong-mau.md"], self.repo)

    def test_4_invalid_status_fails(self):
        vi = self.repo / "translation" / "01-chuong-mau.md"
        original = vi.read_text(encoding="utf-8")
        try:
            vi.write_text(original.replace('status: "draft"', 'status: "done"'), encoding="utf-8")
            r = self.check()
            self.assertEqual(r.returncode, 1)
            self.assertIn("status 'done' không hợp lệ", r.stdout)
        finally:
            vi.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
