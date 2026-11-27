#!/usr/bin/env python3
"""Đọc/ghi front matter YAML phẳng (key: "value") của file chương — chỉ dùng stdlib.

Front matter trong repo này chỉ gồm các cặp `key: value` một dòng (giá trị là chuỗi),
nên không cần pyyaml. Module này được check.py, hash.py, bundle.py, upstream_fetch.py dùng chung.

Dùng như lệnh:
  python3 scripts/frontmatter.py publishable translation   # in các chương status != draft
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATUSES = ("draft", "machine-reviewed", "reviewed")
FM_RE = re.compile(r"\A---\n(.*?)\n---[ \t]*(?:\n|\Z)", re.S)
LINE_RE = re.compile(r"^([A-Za-z0-9_-]+):[ \t]*(.*?)[ \t]*$")


def _unquote(v: str) -> str:
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        inner = v[1:-1]
        return inner.replace('\\"', '"').replace("\\\\", "\\") if v[0] == '"' else inner.replace("''", "'")
    # bỏ comment cuối dòng với giá trị không có ngoặc kép
    return re.sub(r"\s+#.*$", "", v)


def _quote(v: str) -> str:
    return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'


def split(text: str) -> tuple[str | None, str]:
    """Trả về (khối front matter không gồm dấu ---, thân bài). Không có front matter → (None, text)."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    m = FM_RE.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def parse(text: str) -> tuple[dict[str, str], str]:
    raw, body = split(text)
    data: dict[str, str] = {}
    if raw is not None:
        for line in raw.split("\n"):
            m = LINE_RE.match(line)
            if m:
                data[m.group(1)] = _unquote(m.group(2))
    return data, body


def read(path: pathlib.Path) -> tuple[dict[str, str], str]:
    return parse(path.read_text(encoding="utf-8"))


def set_fields(text: str, fields: dict[str, str]) -> str:
    """Cập nhật (hoặc thêm cuối) các khoá trong front matter, giữ nguyên thứ tự và dòng khác."""
    raw, body = split(text)
    lines = raw.split("\n") if raw is not None else []
    for key, value in fields.items():
        new = f"{key}: {_quote(value)}"
        for i, line in enumerate(lines):
            m = LINE_RE.match(line)
            if m and m.group(1) == key:
                lines[i] = new
                break
        else:
            lines.append(new)
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def render(fields: dict[str, str], body: str) -> str:
    head = "\n".join(f"{k}: {_quote(v)}" for k, v in fields.items())
    return f"---\n{head}\n---\n\n{body.strip()}\n"


# ---- Hash nội dung --------------------------------------------------------

def normalize(body: str) -> str:
    """Chuẩn hoá thân bài: xuống dòng \\n, gộp khoảng trắng trong dòng, bỏ khoảng trắng cuối dòng,
    gộp nhiều dòng trống liên tiếp thành một, bỏ dòng trống đầu/cuối."""
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    out: list[str] = []
    for line in body.split("\n"):
        line = re.sub(r"[ \t\f\v ]+", " ", line).rstrip()
        if line == "" and (not out or out[-1] == ""):
            continue
        out.append(line)
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out) + "\n"


def body_hash(body: str) -> str:
    return hashlib.sha256(normalize(body).encode("utf-8")).hexdigest()


def file_hash(path: pathlib.Path) -> str:
    return body_hash(read(path)[1])


# ---- Slug heading (dùng cho anchor) ----------------------------------------

HEADING_RE = re.compile(r"^(#{2,3})[ \t]+(.+?)[ \t]*$", re.M)
ANCHOR_RE = re.compile(r"\{#([A-Za-z0-9_:.-]+)[^}]*\}\s*$")


def slugify(text: str) -> str:
    text = re.sub(r"`|\*|_|\[|\]|\(.*?\)", "", text).lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.U)
    text = re.sub(r"\s+", "-", text.strip())
    return re.sub(r"-{2,}", "-", text).strip("-")


def headings(body: str) -> list[tuple[str, str | None]]:
    """Danh sách (tiêu đề, anchor tường minh hoặc None) của heading ## và ### (bỏ qua khối code)."""
    body = re.sub(r"^```.*?^```", "", body, flags=re.S | re.M)
    res = []
    for m in HEADING_RE.finditer(body):
        title = m.group(2)
        a = ANCHOR_RE.search(title)
        res.append((ANCHOR_RE.sub("", title).strip(), a.group(1) if a else None))
    return res


def heading_ids(body: str) -> set[str]:
    return {a or slugify(t) for t, a in headings(body)}


def chapter_files(folder: str) -> list[pathlib.Path]:
    return sorted((ROOT / folder).glob("[0-9][0-9]-*.md"))


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "publishable":
        for p in chapter_files(argv[1]):
            if read(p)[0].get("status", "draft") != "draft":
                print(p.relative_to(ROOT))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
