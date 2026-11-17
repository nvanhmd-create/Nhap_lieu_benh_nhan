# RULE — Quy Chuẩn Nhập Liệu Bệnh Án Nghiên Cứu Can Thiệp Đột Quỵ Bệnh Viện Hữu Nghị Việt Tiệp

Khi xử lý các file bệnh án scan / ảnh chụp từ Bệnh viện Hữu nghị Việt Tiệp và nạp vào eCRF:

## 1. Quy tắc Đối soát Định danh & Mã số Bệnh án
- **Mã hồ sơ nghiên cứu (Case Code):** Chuẩn hóa theo tiền tố `VT-` kết hợp với Mã người bệnh 10 chữ số (ví dụ: `VT-2600534972` từ mã `2600534972`).
- **Tên bệnh viện:** Luôn chọn `viet_tiep` (Bệnh viện Hữu nghị Việt Tiệp).
- **Họ và tên bệnh nhân:** Chuyển sang dạng VIẾT HOA (ví dụ: `VŨ NGỌC XUÂN`).

## 2. Bóc tách Lâm sàng & Cận lâm sàng từ Hồ sơ Việt Tiệp
- **Tờ điều trị Cấp Cứu vs Khoa Đột Quỵ:**
  - Lấy giờ vào viện và sinh hiệu đầu tiên (HA vào viện, Mạch vào viện) tại Khoa Cấp Cứu hoặc Khoa Đột Quỵ.
  - NIHSS vào viện: Trích xuất chính xác điểm NIHSS khám lúc vào khoa Đột Quỵ (thường 0 - 42 điểm).
- **Phiếu Sàng lọc Dinh dưỡng:**
  - Trích xuất Chiều cao (cm), Cân nặng (kg) và Chỉ số khối cơ thể BMI chính xác.
- **Phiếu Phẫu thuật Thủ thuật:**
  - Giờ bắt đầu thủ thuật (EVT Start / Puncture): Lấy từ mục "Phẫu thuật/thủ thuật lúc".
  - Kỹ thuật & Dụng cụ: Phân biệt rõ hút huyết khối đơn thuần (Aspiration catheter, ví dụ: REACT 71), Stent retriever (Solitaire, Trevo...), hoặc phối hợp (Solumbra).
  - Số lần kéo huyết khối (passes): Ghi nhận đúng số lần kéo/hút được mô tả trong trình tự thủ thuật.
  - Tái thông cuối cùng: Ghi nhận phân độ mTICI (TICI 2b, 2c, 3).
  - Phương pháp vô cảm: Gây mê nội khí quản (GA) vs An thần/Tiền mê (CS).

## 3. Quy chuẩn Xử lý Dữ liệu Khuyết thiếu (Missing Data)
- **Tuyệt đối không tự ý suy diễn hoặc phỏng đoán:** Trường nào trên hồ sơ gốc không có (ví dụ: SĐT người nhà, giờ kết thúc chính xác, điểm pc-ASPECTS, huyết áp 24h sau can thiệp, kết cục 90 ngày) PHẢI **để trống** trên form và thông báo rõ ràng cho người dùng.
- **Chế độ lưu hồ sơ:** Luôn lưu ở dạng **Lưu nháp (Draft)** khi hồ sơ chưa đủ 9 bước hoàn chỉnh.
