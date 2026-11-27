#!/usr/bin/env python3
"""Đóng gói bundle cho blog: build/site-bundle.zip

Nội dung zip:
  manifest.json   — thông tin repo, phiên bản, nguồn và danh sách chương (kèm status, outdated)
  en/<file>.md    — bản gốc tiếng Anh (source/en/)
  vi/<file>.md    — bản dịch (translation/), TẤT CẢ chương kể cả draft; blog tự lọc theo status
  assets/...      — hình ảnh (translation/assets/, source/en/assets/) nếu có

Chương có bản EN nhưng chưa có file dịch được ghi status "untranslated".

  python3 scripts/bundle.py [--version vX.Y.Z] [--out build/site-bundle.zip]
Phiên bản mặc định: tag Git của commit hiện tại (GITHUB_REF_NAME khi chạy release), không có thì "dev".
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import frontmatter as fm  # noqa: E402

ROOT = fm.ROOT
EN_DIR, VI_DIR = ROOT / "source" / "en", ROOT / "translation"


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def detect_version() -> str:
    if os.environ.get("GITHUB_REF_TYPE") == "tag" and os.environ.get("GITHUB_REF_NAME"):
        return os.environ["GITHUB_REF_NAME"]
    return git("describe", "--tags", "--exact-match") or "dev"


def detect_repo() -> str:
    if os.environ.get("GITHUB_REPOSITORY"):
        return os.environ["GITHUB_REPOSITORY"]
    cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    m = re.search(r'repository-code:\s*"?https://github\.com/([^/"\s]+/[^/"\s]+?)(?:\.git)?"?\s*$', cff, re.M)
    if m:
        return m.group(1)
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", git("remote", "get-url", "origin"))
    return m.group(1) if m else ROOT.name


def concept_doi() -> str | None:
    """Concept DOI Zenodo ghi trong README (dòng 'DOI bản dịch'); chưa có thì None."""
    path = ROOT / "README.md"
    if not path.exists():
        return None
    readme = path.read_text(encoding="utf-8")
    for line in readme.splitlines():
        if "DOI bản dịch" in line or "Translation DOI" in line:
            m = re.search(r"10\.\d{4,9}/[^\s)\]|]+", line)
            if m:
                return m.group(0)
    return None


def metadata() -> dict[str, str]:
    meta = {}
    for line in (ROOT / "metadata.yaml").read_text(encoding="utf-8").splitlines():
        m = fm.LINE_RE.match(line)
        if m and m.group(2):
            meta[m.group(1)] = fm._unquote(m.group(2))
    return meta


def build_manifest(version: str) -> dict:
    md = metadata()
    en = {p.name: fm.read(p)[0] for p in fm.chapter_files("source/en")} if EN_DIR.exists() else {}
    vi = {p.name: fm.read(p)[0] for p in fm.chapter_files("translation")}
    chapters = []
    for name in sorted(set(en) | set(vi)):
        e, v = en.get(name, {}), vi.get(name)
        m = re.match(r"^(\d{2})-(.+)\.md$", name)
        chapters.append({
            "chapter": (v or e).get("chapter") or m.group(1),
            "slug": (v or e).get("slug") or m.group(2),
            "file": name,
            "part": e.get("part") or (v or {}).get("part") or "",
            "title_en": e.get("title") or (v or {}).get("title_en") or "",
            "title_vi": (v or {}).get("title_vi") or "",
            "status": v.get("status", "draft") if v is not None else "untranslated",
            "outdated": bool(v is not None and e and v.get("source_hash", "") != e.get("source_hash", "")),
            "upstream_url": e.get("upstream_url") or "",
            "upstream_last_reviewed": e.get("upstream_last_reviewed") or "",
        })
    return {
        "repo": detect_repo(),
        "version": version,
        "concept_doi": concept_doi(),
        "generated_at": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
        "source": {
            "title": md.get("source-title", ""),
            "publisher": md.get("source-publisher", ""),
            "url": md.get("source-url", ""),
            "license": md.get("source-license", ""),
        },
        "chapters": chapters,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default=None)
    ap.add_argument("--out", default=str(ROOT / "build" / "site-bundle.zip"))
    a = ap.parse_args()

    manifest = build_manifest(a.version or detect_version())
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        for prefix, folder in (("en", EN_DIR), ("vi", VI_DIR)):
            for p in fm.chapter_files(str(folder.relative_to(ROOT))) if folder.exists() else []:
                z.write(p, f"{prefix}/{p.name}")
                n += 1
        for folder in (VI_DIR / "assets", EN_DIR / "assets"):
            if folder.is_dir():
                for p in sorted(folder.rglob("*")):
                    if p.is_file() and f"assets/{p.relative_to(folder)}" not in z.namelist():
                        z.write(p, f"assets/{p.relative_to(folder).as_posix()}")
                        n += 1
    print(f"✔ {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}: "
          f"{len(manifest['chapters'])} chương, {n} file, version {manifest['version']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
