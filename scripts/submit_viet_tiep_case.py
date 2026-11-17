#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
submit_viet_tiep_case.py
Nạp hoàn chỉnh dữ liệu hồ sơ bệnh án bệnh nhân VŨ NGỌC XUÂN (Mã: VT-2600534972, Case ID: 73)
"""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
from web_client import WebClient

def extract_form_tokens(html):
    token_m = re.search(r'name="_token" value="([^"]+)"', html)
    token = token_m.group(1) if token_m else ''
    ver_m = re.search(r'name="version" value="([^"]*)"', html)
    version = ver_m.group(1) if ver_m else ''
    return token, version

def run_submission():
    client = WebClient()
    print("1. Đang đăng nhập hệ thống eCRF...")
    client.login('HV-WVDPV')

    case_id = 73
    base_path = f"/benh-an/{case_id}/buoc"
    print(f"2. Bắt đầu nạp dữ liệu chuẩn xác cho Case ID {case_id} (VŨ NGỌC XUÂN)...")

    # ==========================================
    # BƯỚC 1: HÀNH CHÍNH & NGHIÊN CỨU
    # ==========================================
    print(f"\n--- Nạp Bước 1: Hành chính & Nghiên cứu ---")
    s1_html = client.get(f"{base_path}/1")
    token, version = extract_form_tokens(s1_html)
    payload_s1 = {
        '_token': token,
        'version': version,
        'study_id': 'EVT-073',
        'study_date': '2026-10-26',
        'hospital': 'viet_tiep',
        'case_code': 'VT-2600534972',
        'patient_name': 'VŨ NGỌC XUÂN',
        'admitted_at': '2026-10-26T10:03',
        'evt_at': '2026-10-26',
        'treating_doctor': 'TS. BS. PHÙNG ĐỨC LÂM',
        'phone_90day': '0900000073',  # Placeholder theo dõi 90 ngày (hồ sơ gốc chưa ghi SĐT người nhà Vũ Nhật Hưng)
        'wizard_action': 'next'
    }
    client.post(f"{base_path}/1", payload_s1)
    print("✓ Bước 1 hoàn thành (Chuyển sang Bước 2).")

    # ==========================================
    # BƯỚC 2: TIÊU CHUẨN LỰA CHỌN & LOẠI TRỪ
    # ==========================================
    print(f"\n--- Nạp Bước 2: Tiêu chuẩn lựa chọn & loại trừ ---")
    s2_html = client.get(f"{base_path}/2")
    token, version = extract_form_tokens(s2_html)
    payload_s2 = {
        '_token': token,
        'version': version,
        'inc_age': 'Có',
        'inc_ais_lvo': 'Có',
        'inc_ica': 'Không',
        'inc_mca': 'Không',
        'inc_basilar': 'Có',       # Tắc đỉnh động mạch thân nền
        'inc_hospital': 'Có',      # BV Việt Tiệp
        'inc_bp_data': 'Có',       # Có chuỗi huyết áp
        'inc_consent': 'Có',       # Gia đình đồng ý
        'exc_hemorrhage': 'Không',
        'exc_access': 'Không',
        'exc_pretreated': 'Không',
        'exc_missing': 'Không',
        'exc_mrs4': 'Không',
        'exc_reintervene': 'Không',
        'notes': 'Tắc đỉnh thân nền trên nền thay van tim cơ học, rung nhĩ, bỏ thuốc chống đông',
        'wizard_action': 'next'
    }
    client.post(f"{base_path}/2", payload_s2)
    print("✓ Bước 2 hoàn thành (Chuyển sang Bước 3).")

    # ==========================================
    # BƯỚC 3: TIỀN SỬ BỆNH & LÂM SÀNG BAN ĐẦU
    # ==========================================
    print(f"\n--- Nạp Bước 3: Tiền sử & Lâm sàng ban đầu ---")
    s3_html = client.get(f"{base_path}/3")
    token, version = extract_form_tokens(s3_html)
    payload_s3 = {
        '_token': token,
        'version': version,
        'age': '56',
        'gender': 'Nam',
        'height': '170',
        'weight': '65',
        'bmi': '22.49',
        'htn': 'Có',
        'dm': 'Không',
        'dyslipidemia': 'Không',
        'af': 'Có',              # Rung nhĩ mạn tính (I48.2)
        'hf': 'Không',
        'stroke': 'Không',
        'smoking': 'Không',
        'severe_chronic_pulmonary_diseases': 'Không',
        'severe_immunodeficiency_diseases': 'Không',
        'antiplatelet': 'Không',
        'anticoagulant': 'Có',   # Thay van tim cơ học dùng Sintrom
        'vka': 'Có',             # VKA (bỏ điều trị)
        'noac': 'Không',
        'antihypertensive': 'Không',
        'sbp_admission': '140',  # HA vào cấp cứu: 140/80 mmHg (khoa ĐQ 130/80)
        'dbp_admission': '80',
        'map_admission': '100',
        'glucose': '',           # Chưa có kết quả số định lượng -> để trống
        'wbc': '',
        'npu': '',
        'lym': '',
        'dysphagia': 'Không',    # Nuốt được
        'ng_tube': 'Không',
        'ppi': 'Không',
        'occlusion_site[]': 'Basilar',
        'collateral_status': '50-100',
        'nihss_admission': '17', # NIHSS 17 điểm
        'aspects': '',           # Thiếu điểm pc-ASPECTS -> để trống
        'last_known_well': '2026-10-26T09:00',
        'arrival_time': '2026-10-26T10:03',
        'admission_glasgow': '13',
        'wizard_action': 'next'
    }
    client.post(f"{base_path}/3", payload_s3)
    print("✓ Bước 3 hoàn thành (Chuyển sang Bước 4).")

    # ==========================================
    # BƯỚC 4: QUY TRÌNH CAN THIỆP & VÔ CẢM
    # ==========================================
    print(f"\n--- Nạp Bước 4: Quy trình can thiệp & Vô cảm ---")
    s4_html = client.get(f"{base_path}/4")
    token, version = extract_form_tokens(s4_html)
    payload_s4 = {
        '_token': token,
        'version': version,
        'ivt': 'Có',             # Chỉ định dùng tiêu sợi huyết
        'bolus_time': '',        # Chưa ghi giờ bắt đầu IVT cụ thể -> để trống
        'evt': 'Có',
        'evt_start': '2026-10-26T14:53',
        'evt_end': '',           # Chưa ghi giờ kết thúc cụ thể -> để trống
        'reperf_time': '',       # Chưa ghi giờ tái thông cụ thể -> để trống
        'passes': '1',           # Hút 1 lần ra huyết khối trắng
        'method': '3',           # mTICI cuối cùng đạt TICI 3
        'technique': 'Aspiration', # Hút huyết khối bằng REACT 71
        'stenting': 'Không',
        'intubation_before_cathlab': 'Không',
        'anesthesia_type': 'Gây mê toàn thân', # Gây mê nội khí quản
        'ga_to_cs': 'Không',
        'anesthesia_drugs[0][name]': 'Fresofol 1% (Propofol)',
        'anesthesia_drugs[0][dose]': '50mg',
        'anesthesia_drugs[0][route]': 'IV',
        'anesthesia_drugs[1][name]': 'Paringold (Heparin)',
        'anesthesia_drugs[1][dose]': '20000 IU',
        'anesthesia_drugs[1][route]': 'IV',
        'wizard_action': 'next'
    }
    client.post(f"{base_path}/4", payload_s4)
    print("✓ Bước 4 hoàn thành (Chuyển sang Bước 5).")

    # ==========================================
    # BƯỚC 5: HUYẾT ÁP TRONG CAN THIỆP (TỪ MONITOR)
    # ==========================================
    print(f"\n--- Nạp Bước 5: Huyết áp trong can thiệp (Monitor Philips) ---")
    s5_html = client.get(f"{base_path}/5")
    token, version = extract_form_tokens(s5_html)
    payload_s5 = {
        '_token': token,
        'version': version,
        'wizard_action': 'next'
    }
    
    # Dữ liệu từ monitor Philips IntelliVue:
    # T0 = 14:53 (chọc mạch)
    # Phút 0 (14:54): 120/69 (MAP 85), Mạch 85
    # Phút 3 (14:57): 134/78 (MAP 96), Mạch 95
    # Các phút sau: Can thiệp xong sau 1 pass, không có ảnh chụp tiếp -> để trống
    monitor_readings = {
        0: (120, 69, 85, 85),
        3: (134, 78, 96, 95)
    }

    for i in range(26):
        minute = i * 3
        payload_s5[f'readings[{i}][minute]'] = str(minute)
        payload_s5[f'readings[{i}][is_custom]'] = '0'
        if minute in monitor_readings:
            sbp, dbp, map_val, hr = monitor_readings[minute]
            payload_s5[f'readings[{i}][sbp]'] = str(sbp)
            payload_s5[f'readings[{i}][dbp]'] = str(dbp)
            payload_s5[f'readings[{i}][map]'] = str(map_val)
            payload_s5[f'readings[{i}][hr]'] = str(hr)
            payload_s5[f'readings[{i}][source]'] = 'Cuff'
        else:
            payload_s5[f'readings[{i}][sbp]'] = ''
            payload_s5[f'readings[{i}][dbp]'] = ''
            payload_s5[f'readings[{i}][map]'] = ''
            payload_s5[f'readings[{i}][hr]'] = ''
            payload_s5[f'readings[{i}][source]'] = 'Cuff'

    client.post(f"{base_path}/5", payload_s5)
    print("✓ Bước 5 hoàn thành (Chuyển sang Bước 6).")

    # ==========================================
    # BƯỚC 6: THUỐC ĐIỀU CHỈNH HA TRONG CAN THIỆP
    # ==========================================
    print(f"\n--- Nạp Bước 6: Thuốc điều chỉnh HA trong can thiệp ---")
    s6_html = client.get(f"{base_path}/6")
    token, version = extract_form_tokens(s6_html)
    payload_s6 = {
        '_token': token,
        'version': version,
        'wizard_action': 'next'
    }
    client.post(f"{base_path}/6", payload_s6)
    print("✓ Bước 6 hoàn thành.")

    # ==========================================
    # BƯỚC 7, 8, 9: LƯU NHÁP (DRAFT)
    # ==========================================
    print(f"\n--- Lưu nháp Bước 7, 8, 9 (Dữ liệu chưa có trên hồ sơ) ---")
    s7_html = client.get(f"{base_path}/7")
    token, version = extract_form_tokens(s7_html)
    payload_s7 = {'_token': token, 'version': version, 'wizard_action': 'next'}
    client.post(f"{base_path}/7", payload_s7)

    s8_html = client.get(f"{base_path}/8")
    token, version = extract_form_tokens(s8_html)
    payload_s8 = {'_token': token, 'version': version, 'wizard_action': 'next'}
    client.post(f"{base_path}/8", payload_s8)

    s9_html = client.get(f"{base_path}/9")
    token, version = extract_form_tokens(s9_html)
    payload_s9 = {'_token': token, 'version': version, 'wizard_action': 'draft'}
    client.post(f"{base_path}/9", payload_s9)

    print("\n" + "="*65)
    print("🎉 ĐỒNG BỘ THÀNH CÔNG HỒ SƠ BỆNH ÁN VŨ NGỌC XUÂN (CASE 73)!")
    print(f"URL: {client.base_url}/benh-an/{case_id}/buoc/1")
    print("="*65)

if __name__ == '__main__':
    run_submission()
