# Quy ước dịch (Style Guide)

## Nguyên tắc chung
1. **Chính xác trước, trôi chảy sau.** Tài liệu kỹ thuật và tiêu chuẩn: không lược bỏ, không thêm ý. Câu nào khó thì dịch sát nghĩa và thêm ghi chú [ND] nếu cần.
2. **Giữ nguyên tính quy phạm.** Các động từ khiếm khuyết có ý nghĩa quy chuẩn phải dịch nhất quán:

| Tiếng Anh | Tiếng Việt |
|---|---|
| shall / must | phải |
| shall not / must not | không được |
| should | nên |
| should not | không nên |
| may | có thể |
| can | có khả năng |

3. **Xưng hô trung tính**, không dùng "bạn/chúng ta" trừ khi bản gốc dùng "you/we" một cách có chủ ý.

## Thuật ngữ
- Lần xuất hiện đầu tiên trong mỗi chương: *thuật ngữ tiếng Việt (English term, viết tắt)*. Ví dụ: *điểm thực thi chính sách (policy enforcement point, PEP)*.
- Từ lần thứ hai trở đi: dùng thuật ngữ tiếng Việt hoặc chữ viết tắt.
- Chữ viết tắt giữ nguyên dạng tiếng Anh (PEP, PDP, ZTA, MFA…).
- Thuật ngữ đã quen dùng trong ngành, khi dịch ra lại kém rõ nghĩa, thì giữ nguyên tiếng Anh (Zero Trust, firewall, VPN…). Ghi trạng thái `keep-en` trong glossary.

## Định dạng
- Tiêu đề mục giữ đúng số mục gốc: `## 2.1 Các nguyên lý Zero Trust`.
- Hình và bảng: `**Hình 1:** <chú thích đã dịch>`. Hình lấy từ bản gốc đặt trong `translation/assets/`.
- Tài liệu tham khảo: **không dịch** tên tài liệu trong danh mục tham khảo.
- Dấu câu và khoảng trắng theo chuẩn tiếng Việt, dùng dấu ngoặc kép “ ”.

## Ghi chú người dịch
```markdown
> **[ND]** Nội dung ghi chú, vd. đối chiếu với Luật An ninh mạng 2018 hoặc Nghị định 13/2023/NĐ-CP.
```
Ghi chú [ND] là tác phẩm gốc của người dịch và phải tách bạch rõ với phần dịch.
