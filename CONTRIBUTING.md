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
1. Mở file chương trong `translation/`, bấm biểu tượng ✏️.
2. Sửa nội dung, ghi mô tả ngắn, chọn **Propose changes**. GitHub tự tạo Pull Request.

### C. Fork và Pull Request
1. Fork repo, tạo branch `chXX-ten-ngan`.
2. Sửa, chạy `./scripts/build.sh` để kiểm tra build.
3. Gửi Pull Request theo mẫu có sẵn.

## 3. Nhận dịch một chương

Để tránh hai người dịch trùng: mở Issue **"Nhận dịch chương"**, chờ người duy trì xác nhận rồi mới bắt đầu. Nếu sau 30 ngày chưa có tiến triển, chương có thể được giao cho người khác.

## 4. Quy ước dịch

Xem [docs/style-guide.md](docs/style-guide.md). Tóm tắt:

- **Thuật ngữ phải theo [`glossary.csv`](glossary.csv).** Muốn đổi hay thêm thuật ngữ thì mở Issue "Đề xuất thuật ngữ", không tự đổi trong bài.
- Giữ nguyên cấu trúc mục, số mục, số hình và số bảng của bản gốc.
- Ghi chú của người dịch đặt trong khối `> **[ND]** ...`.
- Mỗi file chương bắt đầu bằng phần metadata (front matter): số chương, tiêu đề gốc, người dịch, người hiệu đính.

## 5. Quy trình duyệt

- Nhánh `main` chỉ nhận thay đổi qua Pull Request và cần người duy trì duyệt.
- Mỗi **Release** là một bản đã được rà soát, và Zenodo cấp DOI phiên bản cho mỗi Release.
