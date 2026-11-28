# vi-translation-template

**Template cho các bản dịch tiếng Việt không chính thức của tài liệu an toàn thông tin.**
**A GitHub template for unofficial Vietnamese translations of cybersecurity documents.**

Mỗi bản dịch là một repo riêng tạo từ template này. Repo bản dịch là nguồn chuẩn duy nhất: bản DOCX/HTML/EPUB, DOI Zenodo và nội dung trên blog [jaxvn.io.vn](https://jaxvn.io.vn) đều sinh từ release của repo.
Each translation lives in its own repository created from this template. The translation repo is the single source of truth: DOCX/HTML/EPUB, the Zenodo DOI and the blog content are all generated from its releases.

## Có gì trong template / What's inside

| Đường dẫn / Path | Nội dung / Purpose |
|---|---|
| `source/en/` | Bản gốc tiếng Anh, mỗi chương một file kèm `source_hash` / Original English chapters with a content hash |
| `translation/` | Bản dịch, cùng tên file với `source/en/`; `status`: `draft` · `machine-reviewed` · `reviewed` |
| `templates/front-matter.md` | Trang bản quyền, build tự chèn đầu tài liệu / Copyright page, prepended at build time |
| `glossary.csv`, `docs/style-guide.md` | Thuật ngữ và quy ước dịch / Terminology and style guide |
| `scripts/init.py` | Thay placeholder khi tạo repo mới / Fills in placeholders for a new repo |
| `scripts/check.py` | Kiểm tra repo; cảnh báo chương **OUTDATED** / Repo checks, flags outdated chapters |
| `scripts/hash.py` | Ghi `source_hash` cho EN, đồng bộ sang VI / Stamps content hashes |
| `scripts/build.sh` | Xuất DOCX/HTML/EPUB (chỉ chương khác `draft`) / Builds outputs (non-draft chapters only) |
| `scripts/bundle.py` | Sinh `build/site-bundle.zip` + `manifest.json` cho blog / Site bundle for the blog |
| `scripts/upstream_fetch.py`, `upstream.yaml` | Theo dõi bản gốc trực tuyến, mở PR khi có thay đổi / Watches the upstream web pages |
| `.github/workflows/` | `check` (PR), `release` (đính kèm file + bundle), `upstream-watch` (hằng tuần) |
| `README.template.md`, `CHANGELOG.template.md` | Thành `README.md`, `CHANGELOG.md` của repo bản dịch sau `init.py` |

## Cách dùng / How to use

1. **Use this template → Create a new repository**, đặt tên `<nguon>-<ma-tai-lieu>-vi` (vd. `asd-smb-handbook-vi`).
2. Clone về và chạy `python3 scripts/init.py ...` (ví dụ đầy đủ trong [TEMPLATE_SETUP.md](TEMPLATE_SETUP.md)).
3. `python3 scripts/check.py && ./scripts/build.sh`, rồi commit.

Hướng dẫn chi tiết (quyền dịch, cấu hình GitHub, Zenodo, watcher): **[TEMPLATE_SETUP.md](TEMPLATE_SETUP.md)**.
Quy trình dịch và trạng thái chương: [CONTRIBUTING.md](CONTRIBUTING.md) · Lịch sử template: [CHANGELOG.md](CHANGELOG.md).

## Giấy phép / License

Mã và tài liệu của template: [CC BY 4.0](LICENSE). Bản quyền bản gốc thuộc bên phát hành; xem `NOTICE.md` trong từng repo bản dịch.

---

Duy trì bởi / Maintained by [JaxVN](https://github.com/JaxVN).
