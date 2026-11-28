# Tạo repo bản dịch mới từ template này

> File này chỉ dành cho người duy trì. Xoá file này sau khi khởi tạo xong.

## 1. Kiểm tra quyền dịch (trước khi tạo repo)
- [ ] Tài liệu của chính phủ Mỹ (NIST, CISA…): đọc điều khoản riêng của cơ quan đó, dùng `--rights nist` hoặc ghi nguyên văn.
- [ ] Tài liệu của Chính phủ Úc (ACSC/ASD, cyber.gov.au) phát hành theo CC BY 4.0: dùng `--rights acsc`. Không dùng Quốc huy (Coat of Arms) và logo ASD/ACSC.
- [ ] Tài liệu thuộc bản quyền tư nhân (Anthropic, Microsoft, ISO…): **phải có văn bản cho phép** trước khi public repo hoặc đưa lên Zenodo. Chưa có thì để repo **private**.
- [ ] Rà soát hình và bảng của bên thứ ba trong bản gốc, ghi vào NOTICE.md.

## 2. Tạo repo
1. Trên trang template, bấm **Use this template → Create a new repository**.
2. Đặt tên theo quy ước `<nguon>-<ma-tai-lieu>-vi`, ví dụ `nist-sp800-207-vi`, `asd-smb-handbook-vi`.
3. Clone về máy và chạy `scripts/init.py`. Script thay mọi placeholder `{{...}}`, ghép `README.template.md` → `README.md`
   và `CHANGELOG.template.md` → `CHANGELOG.md`, rồi xoá `.is-template`.

**Bản gốc có DOI (NIST):**

```bash
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
```

**Bản gốc không có DOI (ACSC Small Business Cyber Security Handbook):** truyền `--source-doi ""` và `--source-url`.
README, NOTICE, CITATION.cff và `.zenodo.json` (`related_identifiers`, scheme `url`) sẽ dùng URL thay cho DOI.

```bash
python3 scripts/init.py \
  --repo-name asd-smb-handbook-vi \
  --title-vi "Sổ tay an ninh mạng cho doanh nghiệp nhỏ" \
  --source-title "Small Business Cyber Security Handbook" \
  --source-id "ACSC Small Business Cyber Security Handbook" \
  --source-publisher "Australian Signals Directorate (ASD)" \
  --source-authors "Australian Signals Directorate's Australian Cyber Security Centre (ASD's ACSC)" \
  --source-year 2025 \
  --source-doi "" \
  --source-url https://www.cyber.gov.au/publication/small-business-cyber-security-handbook \
  --rights acsc \
  --ch01-title "Giới thiệu"
```

Kiểm tra năm bản quyền (`--source-year`) trên trang gốc trước khi chạy. Sau đó:

```bash
python3 scripts/hash.py stamp source/en/*.md
python3 scripts/check.py && ./scripts/build.sh && python3 scripts/bundle.py
git rm TEMPLATE_SETUP.md && git add -A && git commit -m "Khởi tạo bản dịch" && git push
```

## 3. Bản gốc, tên file và trạng thái chương
- Mỗi chương có **hai file cùng tên** `NN-<slug>.md`: bản gốc trong `source/en/`, bản dịch trong `translation/`.
  `<slug>` lấy theo phần cuối URL trang gốc; chương `00` là phần giới thiệu/tóm tắt.
- Đổi tên/xoá file mẫu `01-chuong-mau.md` ở cả hai thư mục khi đưa chương thật vào.
- Trang bản quyền **không** nằm trong `translation/`: nội dung ở `templates/front-matter.md`, `build.sh` tự chèn vào đầu tài liệu.
- File EN không được sửa tay. Sau khi dán/tải nội dung mới: `python3 scripts/hash.py stamp source/en/NN-slug.md`.
  `check.py` báo lỗi nếu `source_hash` không khớp nội dung.
- File VI có `status`: `draft` → `machine-reviewed` → `reviewed` (xem CONTRIBUTING.md). Khi bản gốc đổi, `check.py` cảnh báo
  **OUTDATED**; dịch lại xong thì chạy `python3 scripts/hash.py stamp-vi translation/NN-slug.md`.

## 4. Watcher bản gốc (tuỳ chọn)
Điền `upstream.yaml`:

```yaml
source_name: "ACSC Small Business Cyber Security Handbook"
index_url: "https://www.cyber.gov.au/publication/small-business-cyber-security-handbook"
content_selector: "article"
chapters:
  - {chapter: "01", slug: "<slug>", url: "https://www.cyber.gov.au/.../<slug>"}
```

- Workflow **Upstream watch** chạy thứ Hai hằng tuần (và chạy tay qua *Actions → Run workflow*). Có thay đổi → mở PR
  `upstream/<ngày>`; tải lỗi → mở/comment vào Issue có label `upstream-fetch-failed` (không tạo Issue trùng).
- Thử local: `python3 scripts/upstream_fetch.py --dry-run --only 01` (cần `pandoc` và `pip install pyyaml`).
- `content_selector` chỉ hỗ trợ selector đơn giản (`tag`, `.class`, `#id`, `tag.class`, `tag#id`, nhiều selector cách nhau bằng dấu phẩy).
- **Lưu ý cyber.gov.au:** trang này đã từng từ chối công cụ fetch tự động (không đọc được `robots.txt`) dù mở bình thường
  bằng Chrome thật. Watcher tôn trọng `robots.txt`: nếu runner bị chặn, nó **không ghi file** mà mở Issue nhắc lấy thủ công —
  mở trang bằng trình duyệt, sao chép phần nội dung, đổi sang Markdown, dán vào `source/en/NN-slug.md`, chạy `hash.py stamp`, mở PR.

## 5. Cấu hình repo trên GitHub
- [ ] **Settings → Branches → Add rule** cho `main`: Require a pull request + Require review from Code Owners + Require status checks (`check`).
- [ ] **Settings → General → Features**: bật Issues, tắt Wiki nếu không dùng.
- [ ] **Settings → Actions → General → Workflow permissions**: giữ quyền mặc định *read*, bật *Allow GitHub Actions to create and approve pull requests* (cho watcher).
  Setting này không kế thừa từ template; `init.py` tự bật qua `gh api` nếu có quyền (bỏ qua bằng `--skip-github-settings`), không được thì in hướng dẫn.
- [ ] Thêm **Description** và **Topics**: `vietnamese-translation`, `cybersecurity`…

## 6. Bật DOI trên Zenodo và đồng bộ blog
- [ ] Vào https://zenodo.org/account/settings/github/ , bật công tắc cho repo mới.
- [ ] Tạo GitHub Release `v0.1.0`. Zenodo đọc `.zenodo.json` và cấp DOI; workflow `release` đính kèm DOCX/HTML/EPUB và `site-bundle.zip`.
- [ ] Cập nhật DOI bản dịch vào dòng "DOI bản dịch" trong README.md (dùng concept DOI). `bundle.py` đọc DOI từ dòng này cho `manifest.json`.
- [ ] Blog (JaxVN/jaxvn-site) chỉ nhận `site-bundle.zip` từ release; không sửa nội dung bản dịch trực tiếp trên blog.
- [ ] DOI v1.0 chỉ phát hành khi mọi chương đều `reviewed` (chương `machine-reviewed` chưa tính là hoàn tất).

## 7. Khi có người đóng góp
- Thêm họ vào `authors` trong `CITATION.cff` và `contributors` trong `.zenodo.json`
  (`{"name": "Họ, Tên", "type": "Editor"}`; Zenodo chưa có vai trò Translator, dùng `Editor` hoặc `Other`).
- Cập nhật bảng "Những người đóng góp" trong `templates/front-matter.md`.
