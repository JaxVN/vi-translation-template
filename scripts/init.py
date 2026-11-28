#!/usr/bin/env python3
"""Khởi tạo repo bản dịch mới từ template: thay toàn bộ placeholder {{...}}.

Ví dụ (NIST, có DOI):
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

Bản gốc không có DOI: truyền --source-doi "" và --source-url <URL trang gốc>.
Phải có ít nhất một trong hai.
"""
import argparse
import datetime
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = [
    "README.template.md", "CHANGELOG.template.md", "NOTICE.md", "CITATION.cff", ".zenodo.json",
    "metadata.yaml", "templates/front-matter.md",
]
CHAPTER_DIRS = ["source/en", "translation"]
# File *.template.md ghi đè file cùng tên (bỏ ".template") sau khi thay placeholder.
PROMOTE = {"README.template.md": "README.md", "CHANGELOG.template.md": "CHANGELOG.md"}

RIGHTS = {
    "nist": (
        "Republished courtesy of the National Institute of Standards and Technology. "
        "Works authored by NIST employees are not subject to copyright protection within the United States. "
        "Outside the United States, NIST grants the public a non-exclusive, perpetual, paid-up, royalty-free, "
        "worldwide right to reprint the work, including derivative works "
        "(https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications)."
    ),
    "acsc": (
        "© Commonwealth of Australia {year}. With the exception of the Coat of Arms and where otherwise stated, "
        "the original material is provided under a Creative Commons Attribution 4.0 International licence "
        "(https://creativecommons.org/licenses/by/4.0/). This is an unofficial translation and adaptation; "
        "it is not endorsed by the Australian Signals Directorate (ASD) or the Commonwealth."
    ),
    "permission": (
        "Translated and published with written permission of the copyright holder. "
        "All rights in the original work remain with the copyright holder."
    ),
}
# Giấy phép bản gốc mặc định theo preset (ghi vào source/en/*.md và manifest.json)
LICENSES = {"nist": "NIST (public domain in the US)", "acsc": "CC-BY-4.0", "permission": "All rights reserved (used with permission)"}


def chapter_files() -> list[str]:
    out = []
    for d in CHAPTER_DIRS:
        out += [str(p.relative_to(ROOT)) for p in sorted((ROOT / d).glob("*.md"))]
    return out


MANUAL_ACTIONS_HELP = """\
  Bật thủ công: Settings → Actions → General → Workflow permissions
    • giữ "Read repository contents and packages permissions" (quyền mặc định read-only)
    • tick "Allow GitHub Actions to create and approve pull requests"
  hoặc chạy (cần gh đã đăng nhập, quyền admin repo):
    gh api -X PUT repos/{repo}/actions/permissions/workflow \\
      -f default_workflow_permissions=read -F can_approve_pull_request_reviews=true"""


def github_repo(explicit: str) -> str:
    if explicit:
        return explicit
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?/?$", url)
    return m.group(1) if m else ""


def enable_actions_pr_permission(repo: str) -> None:
    """Bật 'Allow GitHub Actions to create and approve pull requests' (watcher cần để mở PR),
    giữ quyền mặc định của GITHUB_TOKEN là read. Setting này không được kế thừa từ template."""
    print("\n— Cấu hình GitHub Actions —")
    if not repo:
        print("⚠ Không xác định được repo GitHub (không có remote origin); bỏ qua.")
        print(MANUAL_ACTIONS_HELP.format(repo="OWNER/REPO"))
        return
    if not shutil.which("gh"):
        print("⚠ Không có gh CLI; bỏ qua.")
        print(MANUAL_ACTIONS_HELP.format(repo=repo))
        return
    r = subprocess.run(["gh", "api", "-X", "PUT", f"repos/{repo}/actions/permissions/workflow",
                        "-f", "default_workflow_permissions=read", "-F", "can_approve_pull_request_reviews=true"],
                       capture_output=True, text=True)
    if r.returncode == 0:
        print(f"✔ {repo}: Actions được tạo/duyệt PR; quyền mặc định GITHUB_TOKEN = read")
    else:
        msg = (r.stderr or r.stdout).strip().splitlines()
        print(f"⚠ Không bật được ({msg[-1] if msg else 'lỗi không rõ'}); bỏ qua.")
        print(MANUAL_ACTIONS_HELP.format(repo=repo))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo-name", required=True)
    p.add_argument("--title-vi", required=True)
    p.add_argument("--source-title", required=True)
    p.add_argument("--source-id", required=True)
    p.add_argument("--source-publisher", required=True)
    p.add_argument("--source-authors", required=True)
    p.add_argument("--source-year", required=True)
    p.add_argument("--source-doi", default="", help="DOI bản gốc; để trống nếu không có (khi đó cần --source-url)")
    p.add_argument("--source-url", default="", help="URL trang bản gốc; bắt buộc khi --source-doi rỗng")
    p.add_argument("--rights", default="nist",
                   help="'nist', 'acsc', 'permission', hoặc nguyên văn câu ghi quyền của bên phát hành")
    p.add_argument("--source-license", default=None,
                   help="Giấy phép bản gốc (mặc định theo preset --rights, vd. acsc → CC-BY-4.0)")
    p.add_argument("--ch01-title", default="Giới thiệu")
    p.add_argument("--github-repo", default="",
                   help="OWNER/REPO để bật quyền Actions tạo PR (mặc định đọc từ git remote origin)")
    p.add_argument("--skip-github-settings", action="store_true",
                   help="không gọi GitHub API để cấu hình quyền Actions")
    a = p.parse_args()

    doi, url = a.source_doi.strip(), a.source_url.strip()
    if not doi and not url:
        p.error("cần --source-doi hoặc --source-url (bản gốc không có DOI thì truyền --source-doi \"\" --source-url <URL>)")
    if not (ROOT / ".is-template").exists():
        print("✘ Repo này đã được khởi tạo (không còn .is-template).", file=sys.stderr)
        return 1

    if doi:
        link = f"https://doi.org/{doi}"
        ref_md, ref_text = f"DOI [{doi}]({link})", f"DOI: {link}"
        ident, scheme, cff = doi, "doi", f'doi: "{doi}"'
    else:
        link = url
        ref_md, ref_text = f"<{url}>", f"URL: {url}"
        ident, scheme, cff = url, "url", f'url: "{url}"'

    today = datetime.date.today()
    rights = RIGHTS[a.rights].format(year=a.source_year) if a.rights in RIGHTS else a.rights
    license_ = a.source_license if a.source_license is not None else LICENSES.get(a.rights, "")
    values = {
        "REPO_NAME": a.repo_name,
        "TITLE_VI": a.title_vi,
        "SOURCE_TITLE": a.source_title,
        "SOURCE_ID": a.source_id,
        "SOURCE_PUBLISHER": a.source_publisher,
        "SOURCE_AUTHORS": a.source_authors,
        "SOURCE_YEAR": a.source_year,
        "SOURCE_DOI": doi,
        "SOURCE_URL": url or link,
        "SOURCE_LINK": link,
        "SOURCE_REF_MD": ref_md,
        "SOURCE_REF_TEXT": ref_text,
        "SOURCE_IDENTIFIER": ident,
        "SOURCE_IDENTIFIER_SCHEME": scheme,
        "SOURCE_CFF_IDENT": cff,
        "SOURCE_LICENSE": license_,
        "SOURCE_RIGHTS_STATEMENT": rights,
        "CH01_TITLE": a.ch01_title,
        "YEAR": str(today.year),
        "DATE": today.isoformat(),
    }

    for rel in FILES + chapter_files():
        f = ROOT / rel
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        for k, v in values.items():
            # JSON và YAML trong ngoặc kép cần escape dấu ngoặc kép
            vv = v.replace('"', '\\"') if f.suffix in {".json", ".yaml"} else v
            text = text.replace("{{" + k + "}}", vv)
        target = ROOT / PROMOTE.get(rel, rel)
        target.write_text(text, encoding="utf-8")
        if target != f:
            f.unlink()
            print(f"✔ {rel} → {target.relative_to(ROOT)}")
        else:
            print(f"✔ {rel}")

    marker = ROOT / ".is-template"
    marker.unlink()
    print("✔ đã xoá .is-template (bật kiểm tra placeholder trong CI)")

    if a.skip_github_settings:
        print("\n— Bỏ qua cấu hình GitHub Actions (--skip-github-settings) —")
        print(MANUAL_ACTIONS_HELP.format(repo=github_repo(a.github_repo) or "OWNER/REPO"))
    else:
        enable_actions_pr_permission(github_repo(a.github_repo))

    print("\nXong. Chạy: python3 scripts/hash.py stamp source/en/*.md && python3 scripts/check.py && ./scripts/build.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
