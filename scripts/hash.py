#!/usr/bin/env python3
"""Hash nội dung bản gốc tiếng Anh để phát hiện chương dịch bị lỗi thời.

hash = sha256 của thân bài sau chuẩn hoá (bỏ front matter, chuẩn hoá xuống dòng,
gộp khoảng trắng, bỏ khoảng trắng cuối dòng, gộp dòng trống) — xem frontmatter.normalize().

Lệnh:
  python3 scripts/hash.py stamp source/en/*.md          # ghi source_hash vào file EN
  python3 scripts/hash.py stamp-vi translation/NN-*.md  # chép source_hash hiện tại của file EN
                                                        # cùng tên sang file VI (khi đã dịch theo bản gốc mới)
  python3 scripts/hash.py show FILE...                   # in hash tính được, không ghi
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import frontmatter as fm  # noqa: E402

EN_DIR = fm.ROOT / "source" / "en"


def stamp(paths: list[pathlib.Path]) -> int:
    for p in paths:
        text = p.read_text(encoding="utf-8")
        h = fm.body_hash(fm.split(text)[1])
        if fm.parse(text)[0].get("source_hash") == h:
            print(f"= {p.name}: không đổi")
            continue
        p.write_text(fm.set_fields(text, {"source_hash": h}), encoding="utf-8")
        print(f"✔ {p.name}: source_hash={h[:12]}…")
    return 0


def stamp_vi(paths: list[pathlib.Path]) -> int:
    rc = 0
    for p in paths:
        en = EN_DIR / p.name
        if not en.exists():
            print(f"✘ {p.name}: không có source/en/{p.name}", file=sys.stderr)
            rc = 1
            continue
        en_meta, en_body = fm.read(en)
        h = en_meta.get("source_hash", "")
        if h != fm.body_hash(en_body):
            print(f"✘ {p.name}: source_hash của file EN chưa khớp nội dung — chạy `hash.py stamp` cho EN trước",
                  file=sys.stderr)
            rc = 1
            continue
        text = p.read_text(encoding="utf-8")
        p.write_text(fm.set_fields(text, {"source_hash": h}), encoding="utf-8")
        print(f"✔ {p.name}: source_hash={h[:12]}… (theo EN)")
    return rc


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] not in {"stamp", "stamp-vi", "show"}:
        print(__doc__, file=sys.stderr)
        return 2
    paths = [pathlib.Path(a).resolve() for a in argv[1:]]
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        print("✘ không tìm thấy: " + ", ".join(missing), file=sys.stderr)
        return 2
    if argv[0] == "stamp":
        return stamp(paths)
    if argv[0] == "stamp-vi":
        return stamp_vi(paths)
    for p in paths:
        print(f"{fm.file_hash(p)}  {p.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
