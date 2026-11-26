# Tạo repo bản dịch mới từ template này

> File này chỉ dành cho người duy trì. Xoá file này sau khi khởi tạo xong.

## 1. Kiểm tra quyền dịch (trước khi tạo repo)
- [ ] Tài liệu của chính phủ Mỹ (NIST, CISA…): đọc điều khoản riêng của cơ quan đó, dùng `--rights nist` hoặc ghi nguyên văn.
- [ ] Tài liệu thuộc bản quyền tư nhân (Anthropic, Microsoft, ISO…): **phải có văn bản cho phép** trước khi public repo hoặc đưa lên Zenodo. Chưa có thì để repo **private**.
- [ ] Rà soát hình và bảng của bên thứ ba trong bản gốc, ghi vào NOTICE.md.

## 2. Tạo repo
1. Trên trang template, bấm **Use this template → Create a new repository**.
2. Đặt tên theo quy ước `<nguon>-<ma-tai-lieu>-vi`, ví dụ `nist-sp800-207-vi`, `nist-csf-2-0-vi`.
3. Clone về máy và chạy:

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
python3 scripts/check.py && ./scripts/build.sh
git rm TEMPLATE_SETUP.md && git commit -am "Khởi tạo bản dịch" && git push
```

## 3. Cấu hình repo trên GitHub
- [ ] **Settings → Branches → Add rule** cho `main`: Require a pull request + Require review from Code Owners + Require status checks (`check`).
- [ ] **Settings → General → Features**: bật Issues, tắt Wiki nếu không dùng.
- [ ] Thêm **Description** và **Topics**: `vietnamese-translation`, `cybersecurity`, `zero-trust`…

## 4. Bật DOI trên Zenodo
- [ ] Vào https://zenodo.org/account/settings/github/ , bật công tắc cho repo mới.
- [ ] Tạo GitHub Release `v0.1.0`. Zenodo đọc `.zenodo.json` và cấp DOI.
- [ ] Cập nhật DOI bản dịch vào README.md (dùng concept DOI, là DOI luôn trỏ về bản mới nhất).

## 5. Khi có người đóng góp
- Thêm họ vào `authors` trong `CITATION.cff` và `contributors` trong `.zenodo.json`
  (`{"name": "Họ, Tên", "type": "Editor"}`; Zenodo chưa có vai trò Translator, dùng `Editor` hoặc `Other`).
- Cập nhật bảng "Những người đóng góp" trong chương 00.
