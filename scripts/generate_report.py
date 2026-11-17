#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, os

with open('audit_all_50_vt_cases_results.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

artifact_dir = '/Users/vuonganhmd/.gemini/antigravity/brain/41995fb1-ed6f-4ee4-962b-53ea4f192cf6'
os.makedirs(artifact_dir, exist_ok=True)
md_path = os.path.join(artifact_dir, 'VT_eCRF_Audit_Report.md')
ws_md_path = 'Bao_Cao_Kiem_Toan_eCRF_Viet_Tiep_50_Ca.md'

lines = []
lines.append('# BÁO CÁO KIỂM TOÁN & ĐỐI SOÁT DỮ LIỆU KHUYẾT THIẾU eCRF BỆNH VIỆN VIỆT TIỆP')
lines.append('')
lines.append('> [!NOTE]')
lines.append('> Báo cáo được tự động quét và kiểm toán trực tiếp từ cơ sở dữ liệu hệ thống eCRF Stroke Registry ([dotquyevt.freehosting.dev](https://dotquyevt.freehosting.dev)) đối với toàn bộ **50 ca bệnh án** của Bệnh viện Hữu nghị Việt Tiệp.')
lines.append('')
lines.append('## 1. Tổng Quan Tình Trạng Hồ Sơ (Executive Summary)')
lines.append('')
lines.append('- **Tổng số ca của Bệnh viện Việt Tiệp trên eCRF:** **50 ca**')
lines.append('- **Phân bố trạng thái:**')
lines.append('  - **Đã nộp lần 1:** **22 ca** (44.0%)')
lines.append('  - **Đang lưu nháp (Draft):** **28 ca** (56.0%)')
lines.append('- **Phân nhóm hành động:**')
lines.append('  - **🟢 Nhóm 1 (18 ca):** Đã hoàn tất 100% Bước 1–8 và hầu hết Bước 9, **chỉ còn thiếu duy nhất thang điểm mRS khi ra viện**.')
lines.append('  - **🟡 Nhóm 2 (16 ca):** Đã hoàn tất 100% Bước 1–8, **chờ bổ sung trọn gói thông tin xuất viện tại Bước 9** (NIHSS ra viện, ngày ra viện, LOS, mRS, TOAST, PISCES).')
lines.append('  - **🔴 Nhóm 3 (16 ca):** Các ca tồn đọng **cần bổ sung số liệu ở các bước tiền lâm sàng, trong can thiệp hoặc sau can thiệp** (Bước 2, 3, 4, 5, 7, 8).')
lines.append('')
lines.append('```mermaid')
lines.append('pie title "Phân Bổ Tình Trạng Hồ Sơ eCRF Việt Tiệp (50 Ca)"')
lines.append('    "Nhóm 1: Chỉ thiếu mRS ra viện (Đã nộp)" : 18')
lines.append('    "Nhóm 2: Xong B1-B8, thiếu gói Bước 9" : 16')
lines.append('    "Nhóm 3: Tồn đọng cần bổ sung B2-B8" : 16')
lines.append('```')
lines.append('')
lines.append('---')
lines.append('')
lines.append('## 2. Bảng Kiểm Toán Chi Tiết Toàn Bộ 50 Ca Bệnh Án')
lines.append('')
lines.append('| STT | Study ID | Mã bệnh án | Họ và tên bệnh nhân | Trạng thái eCRF | HA Monitor (B5) | HA Sau EVT (B8) | Chi tiết số liệu còn thiếu cần bổ sung |')
lines.append('|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---|')

for idx, c in enumerate(cases):
    meta = c['meta']
    status = meta.get('status', meta.get('status_db', ''))
    s5 = c.get('step5_readings_count', 0)
    s8 = c.get('step8_readings_count', 0)
    
    missing_summary = c.get('missing_summary', [])
    if not missing_summary:
        miss_str = '<span style="color:green;font-weight:bold;">Đầy đủ 100%</span>'
    else:
        items = []
        for m in missing_summary:
            items.append(f'• {m}')
        miss_str = '<br>'.join(items)
        
    s5_str = f'{s5} mốc' if s5 > 0 else '<span style="color:red;font-weight:bold;">0 mốc</span>'
    s8_str = f'{s8}/8 mốc' if s8 == 8 else f'<span style="color:orange;font-weight:bold;">{s8}/8 mốc</span>'
    
    status_badge = f'**{status}**'
    lines.append(f"| {idx+1:02d} | `{meta['study_id']}` | `{meta['case_code']}` | **{meta['name']}** | {status_badge} | {s5_str} | {s8_str} | {miss_str} |")

lines.append('')
lines.append('---')
lines.append('')
lines.append('## 3. Danh Mục Chi Tiết Theo Từng Nhóm Xử Lý')
lines.append('')
lines.append('### 🟢 Nhóm 1 — 18 Ca Đã Nộp Lần 1 (Chỉ Thiếu Duy Nhất Điểm mRS Ra Viện)')
lines.append('> [!TIP]')
lines.append('> Các ca này đã hoàn thành 100% tất cả các bước từ 1 đến 8 (đầy đủ monitor can thiệp và 8h sau can thiệp) và đã hoàn tất các chỉ số xuất viện/viêm phổi PISCES. **Chỉ cần tra cứu hồ sơ để bổ sung đúng 1 chỉ số: mRS khi ra viện (0 – 6 điểm)**.')
lines.append('')
lines.append('| STT | Study ID | Mã bệnh án | Họ và tên | Điểm mRS ra viện hiện tại | Ghi chú lâm sàng |')
lines.append('|:---:|:---:|:---:|:---|:---:|:---|')

for idx, c in enumerate(cases):
    m = c.get('step_missing', {})
    if list(m.keys()) == ['b9'] and m['b9'] == ['Thang mRS ra viện']:
        meta = c['meta']
        lines.append(f"| {idx+1:02d} | `{meta['study_id']}` | `{meta['case_code']}` | {meta['name']} | *Chưa điền (Trống)* | Đã nộp lần 1 thành công |")

lines.append('')
lines.append('### 🟡 Nhóm 2 — 16 Ca Đã Xong Bước 1–8 (Chờ Bổ Sung Trọn Gói Bước 9)')
lines.append('> [!IMPORTANT]')
lines.append('> Các ca này đã xong hoàn chỉnh tiền lâm sàng, can thiệp EVT, HA monitor và HA 8h đầu, nhưng đang dừng ở dạng Lưu nháp do thiếu thông tin giấy ra viện. Cần tra cứu phiếu ra viện / tóm tắt bệnh án để bổ sung:')
lines.append('> - Điểm NIHSS 24h & NIHSS ra viện')
lines.append('> - Ngày giờ ra viện & Thời gian nằm viện (LOS)')
lines.append('> - Thang điểm tàn tật mRS khi ra viện')
lines.append('> - Phân loại căn nguyên TOAST')
lines.append('> - Viêm phổi trong viện (thang PISCES, kháng sinh)')
lines.append('')
lines.append('| STT | Study ID | Mã bệnh án | Họ và tên | Trạng thái B1–B8 | Gói dữ liệu Bước 9 cần bổ sung |')
lines.append('|:---:|:---:|:---:|:---|:---:|:---|')

for idx, c in enumerate(cases):
    m = c.get('step_missing', {})
    if list(m.keys()) == ['b9'] and m['b9'] != ['Thang mRS ra viện']:
        meta = c['meta']
        miss_fields = ', '.join(m['b9'])
        lines.append(f"| {idx+1:02d} | `{meta['study_id']}` | `{meta['case_code']}` | {meta['name']} | Đầy đủ 100% | {miss_fields} |")

lines.append('')
lines.append('### 🔴 Nhóm 3 — 16 Ca Cần Bổ Sung Số Liệu Tồn Đọng (Bước 2 đến Bước 8)')
lines.append('> [!WARNING]')
lines.append('> Các ca này bị khuyết thiếu số liệu tại các bước can thiệp, huyết áp monitor hoặc hình ảnh học sau 24h. Cần ưu tiên thu thập để hoàn thiện trước khi đánh giá kết cục:')
lines.append('')

for idx, c in enumerate(cases):
    m = c.get('step_missing', {})
    s_keys = [k for k in m.keys() if k != 'b9']
    if s_keys:
        meta = c['meta']
        status = meta.get('status', meta.get('status_db', ''))
        lines.append(f"#### Ca {idx+1:02d}: `{meta['study_id']}` — {meta['name']} (`{meta['case_code']}`) — *{status}*")
        for k in s_keys:
            step_name = {'b2': 'Bước 2 (Lựa chọn)', 'b3': 'Bước 3 (Lâm sàng)', 'b4': 'Bước 4 (Can thiệp)', 'b5': 'Bước 5 (Monitor HA)', 'b7': 'Bước 7 (CĐHA 24h)', 'b8': 'Bước 8 (HA sau EVT)'}.get(k, k)
            lines.append(f"- **{step_name}:** {', '.join(m[k])}")
        if 'b9' in m:
            lines.append(f"- **Bước 9 (Kết cục):** {', '.join(m['b9'])}")
        lines.append('')

full_text = '\n'.join(lines)
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(full_text)
with open(ws_md_path, 'w', encoding='utf-8') as f:
    f.write(full_text)

print(f"Generated clean report at {md_path} ({len(full_text)} chars)")
print(f"Generated workspace copy at {ws_md_path}")
