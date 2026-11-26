#!/usr/bin/env python3
"""Kiểm tra chất lượng repo: placeholder còn sót, glossary.csv, front matter chương, .zenodo.json."""
import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors: list[str] = []
is_template = (ROOT / ".is-template").exists()

# 1. Placeholder còn sót (bỏ qua khi đang là repo template)
if not is_template:
    for f in ["README.md", "NOTICE.md", "CITATION.cff", ".zenodo.json", "metadata.yaml",
              *[str(p.relative_to(ROOT)) for p in (ROOT / "translation").glob("*.md")]]:
        text = (ROOT / f).read_text(encoding="utf-8")
        for m in sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", text))):
            errors.append(f"{f}: còn placeholder {m} (chạy scripts/init.py)")

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

# 3. Front matter của chương
for p in sorted((ROOT / "translation").glob("*.md")):
    text = p.read_text(encoding="utf-8")
    if not re.match(r"^\d{2}-[a-z0-9-]+\.md$", p.name):
        errors.append(f"{p.name}: tên file phải dạng NN-ten-khong-dau.md")
    if not text.startswith("---\n") or "\nchapter:" not in text.split("---", 2)[1]:
        errors.append(f"{p.name}: thiếu front matter (chapter, title_vi, title_en, translator, reviewer)")

# 4. .zenodo.json hợp lệ
try:
    json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
except json.JSONDecodeError as e:
    errors.append(f".zenodo.json: JSON lỗi — {e}")

if errors:
    print("✘ Kiểm tra thất bại:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print(f"✔ Kiểm tra đạt ({'template mode' if is_template else 'translation mode'}, {len(rows) - 1} thuật ngữ)")
