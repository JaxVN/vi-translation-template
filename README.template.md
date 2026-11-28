# {{TITLE_VI}}

**Bản dịch tiếng Việt không chính thức của:** *{{SOURCE_TITLE}}*
**Unofficial Vietnamese translation of:** *{{SOURCE_TITLE}}*

| | |
|---|---|
| Bản gốc / Original | {{SOURCE_PUBLISHER}}, {{SOURCE_ID}} ({{SOURCE_YEAR}}) |
| Tác giả bản gốc / Original authors | {{SOURCE_AUTHORS}} |
| Nguồn bản gốc / Original source | {{SOURCE_REF_MD}} |
| Người dịch / Translator | Hồng Bảo Ngân (JaxVN) · ORCID [0009-0000-9340-8520](https://orcid.org/0009-0000-9340-8520) |
| DOI bản dịch / Translation DOI | _cấp sau release đầu tiên trên Zenodo_ |
| Giấy phép bản dịch / License | [CC BY 4.0](LICENSE) — xem [NOTICE.md](NOTICE.md) |
| Trạng thái / Status | 🚧 Đang dịch (draft) |

> ⚠️ **Miễn trừ:** Đây là bản dịch không chính thức, không được {{SOURCE_PUBLISHER}} xem xét hay chứng thực. Khi có khác biệt về nghĩa, **bản tiếng Anh gốc là bản có giá trị**.
>
> ⚠️ **Disclaimer:** This is an unofficial translation, not reviewed or endorsed by {{SOURCE_PUBLISHER}}. In case of any discrepancy, **the original English version prevails**.

## Đọc bản dịch

- Đọc trực tuyến: các chương trong thư mục [`translation/`](translation/) (bản gốc tiếng Anh đối chiếu: [`source/en/`](source/en/))
- Tải về (DOCX / HTML / EPUB): mục **Releases** của repo này

## Tiến độ

| Chương | Tiêu đề | Người dịch | Trạng thái |
|---|---|---|---|
| 01 | {{CH01_TITLE}} | — | `draft` |

Trạng thái (ghi trong front matter từng chương, trường `status`):
`draft` bản nháp, chưa phát hành · `machine-reviewed` AI dịch nháp, người dịch đã soát nhanh (được đăng kèm banner, chưa tính là hoàn tất) · `reviewed` đã hiệu đính đầy đủ.
Chương bị đánh dấu **OUTDATED** khi bản gốc đã đổi sau lần dịch gần nhất (`scripts/check.py` báo).

## Cấu hình GitHub Actions (người duy trì)

Workflow **Upstream watch** cần quyền mở Pull Request. Setting này **không** được kế thừa khi tạo repo từ template;
`scripts/init.py` tự bật bằng `gh` nếu có quyền admin, nếu không thì bật thủ công:

- **Settings → Actions → General → Workflow permissions:** giữ *Read repository contents and packages permissions*
  (quyền mặc định của `GITHUB_TOKEN` là read-only) và tick *Allow GitHub Actions to create and approve pull requests*.
- Hoặc chạy:

```bash
gh api -X PUT repos/JaxVN/{{REPO_NAME}}/actions/permissions/workflow -f default_workflow_permissions=read -F can_approve_pull_request_reviews=true
```

Các workflow tự khai báo quyền ghi cần thiết trong khối `permissions:` của chúng.

## Tham gia dịch và góp ý

Mọi góp ý đều được ghi nhận. Có ba cách tham gia, xem chi tiết trong [CONTRIBUTING.md](CONTRIBUTING.md):

1. **Không dùng GitHub:** tải file DOCX trong Releases, bật Track Changes hoặc comment, rồi gửi lại.
2. **Biết GitHub cơ bản:** mở file `.md` trong `translation/`, bấm ✏️ để sửa, GitHub tự tạo Pull Request.
3. **Rành Git:** fork, rồi gửi Pull Request.

Báo lỗi dịch hoặc đề xuất thuật ngữ: mở **Issue** theo mẫu có sẵn.

## Trích dẫn

Xem [CITATION.cff](CITATION.cff) hoặc nút **Cite this repository** ở thanh bên phải. Khi trích dẫn nội dung chuyên môn, vui lòng trích dẫn **bản gốc**.

---

Thuộc bộ bản dịch tài liệu an toàn thông tin của [JaxVN](https://github.com/JaxVN).
