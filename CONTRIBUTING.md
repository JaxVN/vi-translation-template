# Hướng dẫn đóng góp

Cảm ơn bạn quan tâm đến bản dịch. Vui lòng đọc kỹ mục **Giấy phép** trước khi đóng góp.

## 1. Giấy phép đóng góp — đọc trước

Khi gửi đóng góp (Pull Request, file DOCX đã sửa, comment góp ý), bạn đồng ý rằng:

- Phần đóng góp được phát hành theo **CC BY 4.0**, cùng giấy phép với bản dịch.
- Bản dịch **có thể được in thành sách giấy hoặc phát hành thương mại** (qua nhà xuất bản), cũng như được phát hành miễn phí dạng số.
- Bạn được **ghi công** trong `CITATION.cff`, metadata DOI trên Zenodo, và trang ghi công của mọi ấn bản (kể cả sách in). Đóng góp là tự nguyện, không kèm thù lao hay nhuận bút, trừ khi có thỏa thuận riêng bằng văn bản.
- Nội dung bạn gửi là do bạn viết, không sao chép từ bản dịch khác còn bản quyền.

## 2. Các cách tham gia

### A. Không dùng GitHub — góp ý qua DOCX
1. Tải file `*.docx` mới nhất trong mục **Releases**.
2. Bật **Track Changes** (Review → Track Changes) để sửa, hoặc dùng **Comment** để góp ý.
3. Gửi file lại cho người duy trì (email hoặc kênh đã trao đổi), ghi rõ tên muốn được ghi công.
4. Người duy trì đưa góp ý vào bản Markdown. **File DOCX không phải bản gốc**, nên mọi chỉnh sửa chỉ có hiệu lực sau khi được cập nhật vào repo.

### B. Sửa trực tiếp trên web GitHub
1. Mở file chương trong `translation/` (bản gốc đối chiếu ở `source/en/`, cùng tên file), bấm biểu tượng ✏️.
2. Sửa nội dung, ghi mô tả ngắn, chọn **Propose changes**. GitHub tự tạo Pull Request.

### C. Fork và Pull Request
1. Fork repo, tạo branch `chXX-ten-ngan`.
2. Sửa, chạy `python3 scripts/check.py && ./scripts/build.sh` để kiểm tra.
3. Gửi Pull Request theo mẫu có sẵn.

## 3. Nhận dịch một chương

Để tránh hai người dịch trùng: mở Issue **"Nhận dịch chương"**, chờ người duy trì xác nhận rồi mới bắt đầu. Nếu sau 30 ngày chưa có tiến triển, chương có thể được giao cho người khác.

## 4. Trạng thái chương và quy trình dịch

Mỗi file trong `translation/` có trường `status` trong front matter:

| `status` | Nghĩa | Lên blog? | Vào DOCX/HTML/EPUB? | Tính là hoàn tất (DOI v1.0)? |
|---|---|---|---|---|
| `draft` | Bản nháp, đang dịch | Không | Không | Không |
| `machine-reviewed` | AI dịch nháp, người dịch đã **soát nhanh** | Có, kèm banner “bản dịch máy đã soát nhanh” | Có | **Không** |
| `reviewed` | Đã **hậu biên tập đầy đủ** | Có | Có | Có |

Quy trình cho một chương:

1. **Dịch nháp bằng AI** từ `source/en/NN-slug.md`, đưa glossary và style guide vào prompt. Giữ nguyên cấu trúc heading và gắn
   `{#anchor}` theo heading bản EN. `status: "draft"`.
2. **Soát nhanh** (bắt buộc trước khi chuyển `machine-reviewed`), tối thiểu kiểm:
   - động từ quy phạm (must/should/may… theo bảng trong style guide);
   - con số, ngày tháng, đơn vị, số điện thoại, URL;
   - thuật ngữ đúng `glossary.csv`;
   - câu phủ định và câu điều kiện không bị đảo nghĩa.
3. **Hiệu đính đầy đủ** (người hiệu đính ghi tên vào `reviewer`): đọc đối chiếu toàn văn, sửa văn phong, kiểm [ND]. Chuyển `status: "reviewed"`.

Khi bản gốc thay đổi, `scripts/check.py` cảnh báo **OUTDATED** cho chương tương ứng. Cập nhật bản dịch theo diff của
`source/en/`, rồi chạy `python3 scripts/hash.py stamp-vi translation/NN-slug.md` để đánh dấu đã theo kịp bản gốc.
**Không sửa tay file trong `source/en/`** — CI sẽ báo lỗi vì `source_hash` không khớp.

## 5. Quy ước dịch

Xem [docs/style-guide.md](docs/style-guide.md). Tóm tắt:

- **Thuật ngữ phải theo [`glossary.csv`](glossary.csv).** Muốn đổi hay thêm thuật ngữ thì mở Issue "Đề xuất thuật ngữ", không tự đổi trong bài.
- Giữ nguyên cấu trúc mục, số mục, số hình và số bảng của bản gốc.
- Ghi chú của người dịch đặt trong khối `> **[ND]** ...`.
- Mỗi file chương bắt đầu bằng phần metadata (front matter): `chapter`, `slug`, `title_vi`, `title_en`, `translator`, `reviewer`, `status`, `source_hash`.
- Heading `##`/`###` gắn anchor trùng bản EN, vd. `## Sao lưu dữ liệu {#back-up-your-data}`, để liên kết giữa hai bản ổn định.

## 6. Quy trình duyệt

- Nhánh `main` chỉ nhận thay đổi qua Pull Request và cần người duy trì duyệt.
- Mỗi **Release** là một bản đã được rà soát, và Zenodo cấp DOI phiên bản cho mỗi Release.
