#!/usr/bin/env python3
"""Watcher bản gốc: tải trang HTML của từng chương trong upstream.yaml, đổi sang Markdown,
so sánh hash và ghi đè source/en/NN-slug.md nếu nội dung đã đổi.

  python3 scripts/upstream_fetch.py [--config upstream.yaml] [--only 01,03] [--dry-run]
                                    [--report build/upstream-report.json]

Cách làm:
  - Tải HTML (User-Agent rõ ràng, timeout 30 giây, retry 1 lần); tôn trọng robots.txt.
  - Cắt phần tử đầu tiên khớp `content_selector` (hỗ trợ: tag, .class, #id, tag.class, tag#id,
    và nhiều selector cách nhau bởi dấu phẩy — thử lần lượt).
  - Bỏ nav/header/footer/aside/script/style/form/button, phần tử có class/id chứa breadcrumb, menu,
    pagination, pager, share; bỏ các dòng "Previous chapter / Next chapter".
  - pandoc -f html -t gfm --wrap=none, chuẩn hoá, tính hash (giống scripts/hash.py).
  - Hash khác → ghi file (giữ front matter, cập nhật retrieved, source_hash, upstream_last_reviewed).
  - Lỗi tải (HTTP 4xx/5xx, robots.txt chặn hoặc không đọc được, timeout) hoặc không thấy selector
    → KHÔNG ghi file, ghi vào danh sách lỗi.

Phân tích HTML: dùng html.parser của stdlib (không cần beautifulsoup4). Đọc upstream.yaml: pyyaml.

Exit code: 0 = xong (có hoặc không có thay đổi) · 2 = có chương tải lỗi · 3 = lỗi cấu hình/môi trường.
Báo cáo JSON (--report): {"changed": [...], "unchanged": [...], "errors": [...]}.
URL dạng file:// được chấp nhận (dùng cho fixture kiểm thử).
"""
from __future__ import annotations

import argparse
import datetime
import html
import json
import pathlib
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import frontmatter as fm  # noqa: E402

ROOT = fm.ROOT
USER_AGENT = ("vi-translation-template-upstream-watch/2.0 "
              "(+https://github.com/JaxVN/vi-translation-template; weekly check of translated source pages)")
TIMEOUT = 30
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
DROP_TAGS = {"nav", "header", "footer", "aside", "script", "style", "noscript", "form", "button", "svg", "template"}
DROP_ATTR_RE = re.compile(r"breadcrumb|(^|[-_ ])menu($|[-_ ])|pagination|pager|share|skip-link|visually-hidden", re.I)
NAV_LINE_RE = re.compile(r"^\s*(\[?\s*)?(previous|next)\s+(chapter|page|section)\b.*$", re.I | re.M)
LAST_REVIEWED_RE = re.compile(
    r"(?:Last\s+(?:reviewed|updated|modified)|First\s+published)\s*:?\s*(?:<[^>]+>\s*)*"
    r"(\d{1,2}\s+[A-Z][a-z]+\s+\d{4}|\d{4}-\d{2}-\d{2})", re.I)


class FetchError(Exception):
    pass


# ---- Selector + trích HTML -------------------------------------------------

def parse_selector(sel: str) -> tuple[str | None, str | None, str | None]:
    m = re.fullmatch(r"\s*([a-zA-Z][a-zA-Z0-9-]*)?(?:#([\w-]+))?(?:\.([\w-]+))?\s*", sel)
    if not m or not any(m.groups()):
        raise ValueError(f"selector không hỗ trợ: {sel!r} (chỉ dùng tag, .class, #id, tag.class, tag#id)")
    tag, id_, cls = m.groups()
    return (tag.lower() if tag else None), id_, cls


class Extractor(HTMLParser):
    """Lấy HTML bên trong phần tử đầu tiên khớp selector, bỏ các phần tử điều hướng."""

    def __init__(self, selector: tuple[str | None, str | None, str | None]):
        super().__init__(convert_charrefs=False)
        self.sel = selector
        self.depth = 0          # độ sâu trong phần tử được chọn (0 = chưa vào)
        self.done = False
        self.drop_depth = 0     # >0: đang ở trong phần tử bị bỏ
        self.out: list[str] = []

    def _match(self, tag: str, attrs: dict[str, str]) -> bool:
        t, i, c = self.sel
        return ((t is None or t == tag) and (i is None or attrs.get("id") == i)
                and (c is None or c in (attrs.get("class") or "").split()))

    @staticmethod
    def _drop(tag: str, attrs: dict[str, str]) -> bool:
        if tag in DROP_TAGS:
            return True
        if attrs.get("role") in {"navigation", "banner", "contentinfo"} or attrs.get("aria-hidden") == "true":
            return True
        return bool(DROP_ATTR_RE.search(" ".join([attrs.get("class") or "", attrs.get("id") or ""])))

    def handle_starttag(self, tag, attrs_list):
        attrs = {k: (v or "") for k, v in attrs_list}
        if self.done:
            return
        if self.depth == 0:
            if self._match(tag, attrs) and tag not in VOID:
                self.depth = 1
            return
        if tag not in VOID:
            self.depth += 1
        if self.drop_depth:
            if tag not in VOID:
                self.drop_depth += 1
            return
        if self._drop(tag, attrs):
            if tag not in VOID:
                self.drop_depth = 1
            return
        keep = {k: v for k, v in attrs.items() if k in {"href", "src", "alt", "title", "colspan", "rowspan"}}
        a = "".join(f' {k}="{html.escape(v, quote=True)}"' for k, v in keep.items())
        self.out.append(f"<{tag}{a}>")

    def handle_startendtag(self, tag, attrs_list):
        if tag not in VOID:
            self.handle_starttag(tag, attrs_list)
            self.handle_endtag(tag)
        else:
            self.handle_starttag(tag, attrs_list)

    def handle_endtag(self, tag):
        if self.done or self.depth == 0 or tag in VOID:
            return
        self.depth -= 1
        if self.depth == 0:
            self.done = True
            return
        if self.drop_depth:
            self.drop_depth -= 1
            return
        self.out.append(f"</{tag}>")

    def _text(self, s: str):
        if self.depth and not self.done and not self.drop_depth:
            self.out.append(s)

    def handle_data(self, data):
        self._text(data)

    def handle_entityref(self, name):
        self._text(f"&{name};")

    def handle_charref(self, name):
        self._text(f"&#{name};")


def extract(page_html: str, selector: str) -> str | None:
    for part in selector.split(","):
        ex = Extractor(parse_selector(part))
        ex.feed(page_html)
        ex.close()
        if ex.depth or ex.done:
            return "".join(ex.out)
    return None


def to_markdown(fragment: str, base_url: str = "") -> str:
    if not shutil.which("pandoc"):
        raise RuntimeError("cần pandoc trong PATH")
    r = subprocess.run(["pandoc", "-f", "html", "-t", "gfm", "--wrap=none"], input=fragment,
                       capture_output=True, text=True, check=True)
    md = NAV_LINE_RE.sub("", r.stdout)
    md = re.sub(r"<!-- -->\n?", "", md)
    if base_url.startswith("http"):   # link tương đối → tuyệt đối
        md = re.sub(r"\]\((/[^)\s]*)", lambda m: "](" + urllib.parse.urljoin(base_url, m.group(1)), md)
    return fm.normalize(md)


# ---- Tải trang -------------------------------------------------------------

_robots: dict[str, urllib.robotparser.RobotFileParser] = {}


def robots_allows(url: str) -> bool:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in {"http", "https"}:
        return True
    base = f"{parts.scheme}://{parts.netloc}"
    if base not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            req = urllib.request.Request(base + "/robots.txt", headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                rp.parse(resp.read().decode("utf-8", "replace").splitlines())
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                rp.disallow_all = True        # theo quy ước robotparser: bị chặn → coi như cấm
            else:
                rp.allow_all = True           # 404/5xx: không có robots.txt
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise FetchError(f"không đọc được robots.txt: {e}") from e
        _robots[base] = rp
    return _robots[base].can_fetch(USER_AGENT, url)


def fetch(url: str) -> str:
    if not robots_allows(url):
        raise FetchError("robots.txt không cho phép (hoặc chặn truy cập robots.txt)")
    last: Exception | None = None
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                return resp.read().decode(charset, "replace")
        except urllib.error.HTTPError as e:
            last = FetchError(f"HTTP {e.code}")
            if e.code < 500:
                break
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last = FetchError(f"lỗi kết nối: {getattr(e, 'reason', e)}")
        if attempt == 0:
            time.sleep(3)
    raise last or FetchError("không rõ lỗi")


# ---- Chạy ------------------------------------------------------------------

def load_config(path: pathlib.Path) -> dict:
    try:
        import yaml
    except ImportError:
        print("✘ cần pyyaml: pip install pyyaml", file=sys.stderr)
        sys.exit(3)
    cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    chapters = cfg.get("chapters") or []
    for c in chapters:
        if not all(str(c.get(k) or "") for k in ("chapter", "slug", "url")):
            print(f"✘ {path.name}: mỗi chương cần chapter, slug, url — {c}", file=sys.stderr)
            sys.exit(3)
        c["chapter"] = f"{int(c['chapter']):02d}" if str(c["chapter"]).isdigit() else str(c["chapter"])
    cfg["chapters"] = chapters
    return cfg


def process(c: dict, cfg: dict, source_dir: pathlib.Path, dry_run: bool) -> tuple[str, dict]:
    url, name = c["url"], f"{c['chapter']}-{c['slug']}.md"
    info = {"chapter": c["chapter"], "slug": c["slug"], "url": url, "file": name}
    page = fetch(url)
    fragment = extract(page, cfg.get("content_selector") or "article")
    if fragment is None:
        raise FetchError(f"không tìm thấy selector {cfg.get('content_selector')!r}")
    md = to_markdown(fragment, url)
    if not md.strip():
        raise FetchError("nội dung rỗng sau khi trích xuất")
    new_hash = fm.body_hash(md)
    m = LAST_REVIEWED_RE.search(re.sub(r"\s+", " ", page))
    last_reviewed = m.group(1) if m else ""

    path = source_dir / name
    today = datetime.date.today().isoformat()
    if path.exists():
        text = path.read_text(encoding="utf-8")
        meta = fm.parse(text)[0]
        if meta.get("source_hash") == new_hash and fm.file_hash(path) == new_hash:
            return "unchanged", info
        fields = {"retrieved": today, "source_hash": new_hash, "upstream_url": url}
        if last_reviewed:
            fields["upstream_last_reviewed"] = last_reviewed
        raw = fm.set_fields(text, fields)
        out = fm.split(raw)[0]
        content = f"---\n{out}\n---\n\n{md}"
        info["previous_hash"] = meta.get("source_hash", "")
    else:
        h1 = re.search(r"^# (.+)$", md, re.M)
        license_ = ""
        meta_yaml = ROOT / "metadata.yaml"
        if meta_yaml.exists():
            lm = re.search(r'^source-license:\s*"?(.*?)"?\s*$', meta_yaml.read_text(encoding="utf-8"), re.M)
            license_ = lm.group(1) if lm and "{{" not in lm.group(1) else ""
        content = fm.render({
            "chapter": c["chapter"], "slug": c["slug"],
            "title": c.get("title") or (h1.group(1).strip() if h1 else ""),
            "part": str(c.get("part") or ""), "upstream_url": url, "upstream_last_reviewed": last_reviewed,
            "retrieved": today, "source_hash": new_hash, "license": license_,
        }, md)
        info["new_file"] = True
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    info["source_hash"] = new_hash
    return "changed", info


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=str(ROOT / "upstream.yaml"))
    ap.add_argument("--source-dir", default=str(ROOT / "source" / "en"))
    ap.add_argument("--only", default="", help="danh sách số chương, vd. 01,03")
    ap.add_argument("--dry-run", action="store_true", help="không ghi file")
    ap.add_argument("--report", default="", help="ghi báo cáo JSON vào đường dẫn này")
    a = ap.parse_args()

    cfg = load_config(pathlib.Path(a.config))
    chapters = cfg["chapters"]
    if a.only:
        wanted = {f"{int(x):02d}" if x.strip().isdigit() else x.strip() for x in a.only.split(",")}
        chapters = [c for c in chapters if c["chapter"] in wanted]
    report: dict[str, list] = {"changed": [], "unchanged": [], "errors": []}
    if not chapters:
        print("upstream.yaml không có chương nào — bỏ qua.")
    for c in chapters:
        try:
            state, info = process(c, cfg, pathlib.Path(a.source_dir), a.dry_run)
            report[state].append(info)
            print(f"{'✎' if state == 'changed' else '='} {c['chapter']}-{c['slug']}: {state}")
        except (FetchError, ValueError, subprocess.CalledProcessError, RuntimeError) as e:
            report["errors"].append({"chapter": c["chapter"], "slug": c["slug"], "url": c["url"], "error": str(e)})
            print(f"✘ {c['chapter']}-{c['slug']}: {e} — {c['url']}", file=sys.stderr)
    if a.report:
        pathlib.Path(a.report).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(a.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Tổng: {len(report['changed'])} đổi · {len(report['unchanged'])} không đổi · {len(report['errors'])} lỗi")
    return 2 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
