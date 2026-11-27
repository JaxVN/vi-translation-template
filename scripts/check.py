#!/usr/bin/env python3
"""Kiểm tra chất lượng repo.

Lỗi (exit 1): placeholder còn sót, glossary.csv sai, front matter chương thiếu/sai, status không hợp lệ,
source_hash của file EN không khớp nội dung (ai đó sửa tay bản gốc mà không stamp), .zenodo.json lỗi.
Cảnh báo (không fail): chương OUTDATED (bản gốc đổi sau lần dịch), heading thiếu {#anchor} khớp bản EN.
"""
from __future__ import annotations

import csv
import json
import pathlib
import re
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import frontmatter as fm  # noqa: E402

ROOT = fm.ROOT
errors: list[str] = []
warnings: list[str] = []
is_template = (ROOT / ".is-template").exists()

EN_DIR, VI_DIR = ROOT / "source" / "en", ROOT / "translation"
NAME_RE = re.compile(r"^(\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
EN_KEYS = ["chapter", "slug", "title", "part", "upstream_url", "upstream_last_reviewed", "retrieved",
           "source_hash", "license"]
VI_KEYS = ["chapter", "slug", "title_vi", "title_en", "translator", "reviewer", "status", "source_hash"]
PLACEHOLDER_FILES = ["README.md", "NOTICE.md", "CITATION.cff", ".zenodo.json", "metadata.yaml",
                     "CHANGELOG.md", "templates/front-matter.md"]

en_files = sorted(EN_DIR.glob("*.md")) if EN_DIR.exists() else []
vi_files = sorted(VI_DIR.glob("*.md"))

# 1. Placeholder còn sót (bỏ qua khi đang là repo template)
if not is_template:
    for f in PLACEHOLDER_FILES + [str(p.relative_to(ROOT)) for p in en_files + vi_files]:
        path = ROOT / f
        if not path.exists():
            continue
        for m in sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", path.read_text(encoding="utf-8")))):
            errors.append(f"{f}: còn placeholder {m} (chạy scripts/init.py)")
    for leftover in ["README.template.md", "CHANGELOG.template.md"]:
        if (ROOT / leftover).exists():
            errors.append(f"{leftover}: còn sót sau khi khởi tạo (init.py lẽ ra đã ghép vào file chính)")

# 2. glossary.csv
with open(ROOT / "glossary.csv", encoding="utf-8", newline="") as fh:
    rows = list(csv.reader(fh))
header = ["term_en", "abbr", "term_vi", "status", "note"]
if rows[0] != header:
    errors.append(f"glossary.csv: header phải là {header}")
seen = set()
for i, r in enumerate(rows[1:], start=2):
    if len(r) != len(header):
        errors.append(f"glossary.csv dòng {i}: có {len(r)} cột, cần {len(header)} (dùng ngoặc kép nếu có dấu phẩy)")
        continue
    key = r[0].strip().lower()
    if key in seen:
        errors.append(f"glossary.csv dòng {i}: trùng thuật ngữ '{r[0]}'")
    seen.add(key)
    if r[3] not in {"proposed", "accepted", "keep-en", "deprecated"}:
        errors.append(f"glossary.csv dòng {i}: status '{r[3]}' không hợp lệ")


def check_common(p: pathlib.Path, meta: dict, keys: list[str], where: str) -> None:
    m = NAME_RE.match(p.name)
    if not m:
        errors.append(f"{where}/{p.name}: tên file phải dạng NN-<slug-theo-url-goc>.md")
        return
    missing = [k for k in keys if k not in meta]
    if missing:
        errors.append(f"{where}/{p.name}: front matter thiếu {', '.join(missing)}")
    if meta.get("chapter") is not None and meta.get("chapter") != m.group(1):
        errors.append(f"{where}/{p.name}: chapter '{meta.get('chapter')}' không khớp tên file ({m.group(1)})")
    if meta.get("slug") is not None and meta.get("slug") != m.group(2):
        errors.append(f"{where}/{p.name}: slug '{meta.get('slug')}' không khớp tên file ({m.group(2)})")


# 3. Bản gốc tiếng Anh: front matter + source_hash phải khớp nội dung
en_meta: dict[str, tuple[dict, str]] = {}
for p in en_files:
    meta, body = fm.read(p)
    en_meta[p.name] = (meta, body)
    check_common(p, meta, EN_KEYS, "source/en")
    h = meta.get("source_hash", "")
    if not h:
        errors.append(f"source/en/{p.name}: chưa có source_hash (chạy `python3 scripts/hash.py stamp {p.relative_to(ROOT)}`)")
    elif h != fm.body_hash(body):
        errors.append(f"source/en/{p.name}: source_hash không khớp nội dung — file EN bị sửa tay? "
                      f"Nếu là cập nhật bản gốc hợp lệ, chạy `python3 scripts/hash.py stamp`")

# 4. Bản dịch: front matter, status, outdated, anchor
status_count: Counter = Counter()
outdated: list[str] = []
for p in vi_files:
    meta, body = fm.read(p)
    if not p.read_text(encoding="utf-8").startswith("---\n"):
        errors.append(f"translation/{p.name}: thiếu front matter ({', '.join(VI_KEYS)})")
        continue
    check_common(p, meta, VI_KEYS, "translation")
    status = meta.get("status", "")
    if status not in fm.STATUSES:
        errors.append(f"translation/{p.name}: status '{status}' không hợp lệ (chọn {' | '.join(fm.STATUSES)})")
    else:
        status_count[status] += 1
    if p.name in en_meta:
        e_meta, e_body = en_meta[p.name]
        if meta.get("source_hash", "") != e_meta.get("source_hash", ""):
            outdated.append(p.name)
            warnings.append(f"OUTDATED translation/{p.name}: bản gốc đã đổi (source_hash VI ≠ EN). "
                            f"Cập nhật bản dịch rồi chạy `python3 scripts/hash.py stamp-vi translation/{p.name}`")
        en_ids = fm.heading_ids(e_body)
        for title, anchor in fm.headings(body):
            if anchor is None:
                warnings.append(f"translation/{p.name}: heading “{title}” chưa có {{#anchor}} theo bản EN")
            elif anchor not in en_ids:
                warnings.append(f"translation/{p.name}: anchor #{anchor} không khớp heading nào trong source/en/{p.name}")

# 5. .zenodo.json hợp lệ
try:
    json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
except json.JSONDecodeError as e:
    errors.append(f".zenodo.json: JSON lỗi — {e}")

# ---- Báo cáo ----
for w in warnings:
    print(f"⚠ {w}")
summary = ", ".join(f"{s}: {status_count.get(s, 0)}" for s in fm.STATUSES)
print(f"Chương dịch: {len(vi_files)} ({summary}) · outdated: {len(outdated)} · bản gốc EN: {len(en_files)}")

if errors:
    print("✘ Kiểm tra thất bại:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print(f"✔ Kiểm tra đạt ({'template mode' if is_template else 'translation mode'}, {len(rows) - 1} thuật ngữ)")
