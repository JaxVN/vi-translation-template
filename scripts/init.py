#!/usr/bin/env python3
"""Khởi tạo repo bản dịch mới từ template: thay toàn bộ placeholder {{...}}.

Ví dụ:
  python3 scripts/init.py \
    --repo-name nist-sp800-207-vi \
    --title-vi "Kiến trúc Zero Trust" \
    --source-title "Zero Trust Architecture" \
    --source-id "NIST SP 800-207" \
    --source-publisher "National Institute of Standards and Technology (NIST)" \
    --source-authors "Rose, S.; Borchert, O.; Mitchell, S.; Connelly, S." \
    --source-year 2020 \
    --source-doi 10.6028/NIST.SP.800-207 \
    --rights nist \
    --ch01-title "Giới thiệu"
"""
import argparse
import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = [
    "README.md", "NOTICE.md", "CITATION.cff", ".zenodo.json", "metadata.yaml",
    "translation/00-ban-quyen-va-mien-tru.md", "translation/01-chuong-mau.md",
]

RIGHTS = {
    "nist": (
        "Republished courtesy of the National Institute of Standards and Technology. "
        "Works authored by NIST employees are not subject to copyright protection within the United States. "
        "Outside the United States, NIST grants the public a non-exclusive, perpetual, paid-up, royalty-free, "
        "worldwide right to reprint the work, including derivative works "
        "(https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications)."
    ),
    "permission": (
        "Translated and published with written permission of the copyright holder. "
        "All rights in the original work remain with the copyright holder."
    ),
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo-name", required=True)
    p.add_argument("--title-vi", required=True)
    p.add_argument("--source-title", required=True)
    p.add_argument("--source-id", required=True)
    p.add_argument("--source-publisher", required=True)
    p.add_argument("--source-authors", required=True)
    p.add_argument("--source-year", required=True)
    p.add_argument("--source-doi", required=True)
    p.add_argument("--rights", default="nist",
                   help="'nist', 'permission', hoặc nguyên văn câu ghi quyền của bên phát hành")
    p.add_argument("--ch01-title", default="Giới thiệu")
    a = p.parse_args()

    today = datetime.date.today()
    values = {
        "REPO_NAME": a.repo_name,
        "TITLE_VI": a.title_vi,
        "SOURCE_TITLE": a.source_title,
        "SOURCE_ID": a.source_id,
        "SOURCE_PUBLISHER": a.source_publisher,
        "SOURCE_AUTHORS": a.source_authors,
        "SOURCE_YEAR": a.source_year,
        "SOURCE_DOI": a.source_doi,
        "SOURCE_RIGHTS_STATEMENT": RIGHTS.get(a.rights, a.rights),
        "CH01_TITLE": a.ch01_title,
        "YEAR": str(today.year),
        "DATE": today.isoformat(),
    }

    for rel in FILES:
        f = ROOT / rel
        text = f.read_text(encoding="utf-8")
        for k, v in values.items():
            # JSON cần escape dấu ngoặc kép
            vv = v.replace('"', '\\"') if f.suffix == ".json" else v
            text = text.replace("{{" + k + "}}", vv)
        f.write_text(text, encoding="utf-8")
        print(f"✔ {rel}")

    marker = ROOT / ".is-template"
    if marker.exists():
        marker.unlink()
        print("✔ đã xoá .is-template (bật kiểm tra placeholder trong CI)")

    print("\nXong. Chạy: python3 scripts/check.py && ./scripts/build.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
