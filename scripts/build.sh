#!/usr/bin/env bash
# Ghép các chương trong translation/ theo thứ tự tên file, xuất DOCX (để góp ý), HTML và EPUB.
# Cần: pandoc >= 2.19
set -euo pipefail
cd "$(dirname "$0")/.."

NAME="$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")"
OUT="build"
mkdir -p "$OUT"
mapfile -t CHAPTERS < <(ls translation/[0-9][0-9]-*.md | sort)

COMMON=(metadata.yaml "${CHAPTERS[@]}" --from markdown+yaml_metadata_block --resource-path=translation)

pandoc "${COMMON[@]}" -o "$OUT/$NAME.docx"
pandoc "${COMMON[@]}" --standalone --embed-resources -o "$OUT/$NAME.html"
pandoc "${COMMON[@]}" -o "$OUT/$NAME.epub"

echo "✔ Đã build:"
ls -1 "$OUT"/"$NAME".*
