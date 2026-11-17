---
name: viet-tiep-ecrf-entry
description: Tự động trích xuất thông tin bệnh án can thiệp đột quỵ từ tài liệu/ảnh chụp hồ sơ Bệnh viện Hữu nghị Việt Tiệp và đồng bộ dữ liệu vào hệ thống eCRF dotquyevt.freehosting.dev.
---

# Kỹ Năng Tự Động Hóa Nhập Liệu eCRF Bệnh Viện Hữu Nghị Việt Tiệp

Kỹ năng này hướng dẫn xử lý và nạp dữ liệu từ các chứng từ y tế của Bệnh viện Hữu nghị Việt Tiệp:
1. **Tờ điều trị Cấp cứu & Đột quỵ**: Triệu chứng khởi phát, thời gian, sinh hiệu vào viện, NIHSS, CTA.
2. **Phiếu sàng lọc dinh dưỡng**: Chiều cao, cân nặng, BMI.
3. **Phiếu khai thác tiền sử**: Yếu tố nguy cơ, tiền sử phẫu thuật, thuốc tim mạch / chống đông.
4. **Phiếu phẫu thuật thủ thuật**: Thời gian can thiệp, vị trí chọc mạch, dụng cụ can thiệp, số passes, kết quả mTICI, phương pháp vô cảm.
5. **Bảng kê vật tư / dược phẩm**: Thuốc mê (Propofol, Midazolam...), kháng đông (Heparin), loại sheath và catheter.
6. **Dữ liệu monitor huyết áp**: Chuỗi huyết áp và nhịp tim đo quanh thủ thuật.

## Quy trình đối chiếu lâm sàng & chuỗi huyết áp Monitor (Step 5)
1. **Xác định mốc khởi đầu $T_0$**: Lấy giờ chọc mạch (Puncture time) từ Phiếu phẫu thuật thủ thuật (mục "Sát khuẩn vị trí động mạch đùi lúc" hoặc "Phẫu thuật/thủ thuật lúc"). Đối chiếu với mốc thời gian NIBP gần nhất trên ảnh monitor (trong vòng 1-2 phút).
2. **Chuẩn hóa chuỗi thời gian**: Gán mốc NIBP tại $T_0$ là **0 phút**, mỗi lần đo NIBP kế tiếp tăng đều **3 phút/lần** (0, 3, 6, 9, 12... phút).
3. **Xác định mốc kết thúc thủ thuật**: Lấy giờ kết thúc từ Phiếu PTTT (mục "Kết thúc can thiệp lúc"). Tất cả các ô sau mốc kết thúc được **để trống**.
4. **Nhập liệu & Lưu nháp**:
   - Tự động nạp qua script: `python3 scripts/reconcile_and_submit.py -f <patient_json>`
   - Hoặc điền trực tiếp qua Console trình duyệt với file JavaScript sinh tự động `fill_step5_console.js`.
   - Các trường chưa có dữ liệu (kết cục 90 ngày, HA 24h nếu chưa đủ) được để trống và lưu ở trạng thái **Lưu nháp (Draft)**.
