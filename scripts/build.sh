#!/usr/bin/env bash
# Ghép trang bản quyền (templates/front-matter.md) + các chương trong translation/ có status khác draft,
# theo thứ tự tên file; xuất DOCX (để góp ý), HTML và EPUB.
# Cần: pandoc >= 2.19, python3
set -euo pipefail
cd "$(dirname "$0")/.."

NAME="$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")"
OUT="build"
mkdir -p "$OUT"
mapfile -t CHAPTERS < <(python3 scripts/frontmatter.py publishable translation)
SKIPPED=$(( $(ls translation/[0-9][0-9]-*.md 2>/dev/null | wc -l) - ${#CHAPTERS[@]} ))
echo "Ghép ${#CHAPTERS[@]} chương (bỏ qua ${SKIPPED} chương draft)"

COMMON=(metadata.yaml templates/front-matter.md "${CHAPTERS[@]}"
        --from markdown+yaml_metadata_block --resource-path=translation)

pandoc "${COMMON[@]}" -o "$OUT/$NAME.docx"
pandoc "${COMMON[@]}" --standalone --embed-resources -o "$OUT/$NAME.html"
pandoc "${COMMON[@]}" -o "$OUT/$NAME.epub"

echo "✔ Đã build:"
ls -1 "$OUT"/"$NAME".*
