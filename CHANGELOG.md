# Nhật ký thay đổi của template

Lịch sử của **template** `JaxVN/vi-translation-template`. Repo bản dịch tạo từ template dùng
`CHANGELOG.template.md` (init.py đổi thành `CHANGELOG.md` của repo đó).
Định dạng theo [Keep a Changelog](https://keepachangelog.com/).

## [2.0.0] - 2026-11-27
### Added
- `source/en/`: bản gốc tiếng Anh theo chương, front matter `chapter, slug, title, part, upstream_url,
  upstream_last_reviewed, retrieved, source_hash, license`.
- `scripts/hash.py` (`stamp`, `stamp-vi`, `show`): sha256 của thân bài đã chuẩn hoá; `scripts/frontmatter.py` (thư viện dùng chung, stdlib).
- Front matter bản dịch thêm `slug`, `status` (`draft | machine-reviewed | reviewed`), `source_hash`.
- `check.py`: kiểm `source_hash` EN (fail nếu file EN bị sửa tay), `status` hợp lệ, tên file/chapter/slug khớp nhau;
  cảnh báo **OUTDATED** và heading thiếu `{#anchor}` theo bản EN; báo cáo số chương theo status.
- `scripts/bundle.py` → `build/site-bundle.zip` (`manifest.json`, `en/`, `vi/`, `assets/`) cho blog; chạy trong `check` và đính kèm trong `release`.
- Watcher bản gốc: `upstream.yaml`, `scripts/upstream_fetch.py` (stdlib `html.parser` + pandoc; `pyyaml` để đọc cấu hình),
  workflow `upstream-watch` hằng tuần mở PR khi bản gốc đổi, mở/comment Issue `upstream-fetch-failed` khi tải lỗi.
- `init.py`: preset `--rights acsc`; `--source-url`; `--source-doi` được để trống (dùng URL thay DOI trong README, NOTICE,
  CITATION.cff, `.zenodo.json`); `--source-license`; ghép `README.template.md`/`CHANGELOG.template.md` vào file chính.
- `tests/` (unittest + fixture HTML): watcher, hash/OUTDATED, luồng init → check → build → bundle.
- Glossary: `passkey`, `password manager`, `patch`, `incident response plan`.
- Tài liệu: quy trình 3 trạng thái trong CONTRIBUTING.md, bảng phương pháp dịch trong style guide, ví dụ ACSC và watcher trong TEMPLATE_SETUP.md.

### Changed
- `README.md` giới thiệu template (song ngữ); README của repo bản dịch chuyển sang `README.template.md`.
- Trang bản quyền chuyển từ `translation/00-ban-quyen-va-mien-tru.md` sang `templates/front-matter.md`, build tự chèn.
  Chương `00` dành cho phần giới thiệu/tóm tắt của bản gốc.
- `build.sh` chỉ ghép chương có `status` khác `draft`.
- Tên file chương: `NN-<slug theo URL gốc>.md`, trùng tên giữa `source/en/` và `translation/`.

## [1.0.0] - 2026-11-26
### Added
- Template ban đầu (commit c0b3042): README, NOTICE, CITATION.cff, `.zenodo.json`, glossary, style guide,
  `init.py`, `check.py`, `build.sh`, workflow `check` và `release`.
