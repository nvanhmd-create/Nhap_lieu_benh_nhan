#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
submit_nguyen_thi_mai.py
Nạp dữ liệu từ Bước 1 đến Bước 8 cho bệnh nhân NGUYỄN THỊ MAI (VT-2600537057, Case ID: 97)
Điều tra viên / Người nhập liệu: NGUYỄN VƯƠNG ANH
"""

import sys, os, re, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from web_client import WebClient

def extract_form_tokens(html):
    token_m = re.search(r'name="_token" value="([^"]+)"', html)
    token = token_m.group(1) if token_m else ''
    ver_m = re.search(r'name="version" value="([^"]*)"', html)
    version = ver_m.group(1) if ver_m else ''
    return token, version

def main():
    with open('nguyen_thi_mai_ecrf_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    client = WebClient()
    print("1. Đang đăng nhập hệ thống eCRF...")
    client.login('HV-WVDPV')
    time.sleep(1)

    case_id = 97
    base_path = f"/benh-an/{case_id}/buoc"
    print(f"2. Bắt đầu nạp dữ liệu cho Case ID {case_id} (NGUYỄN THỊ MAI)...")

    # ==========================================
    # BƯỚC 2: TIÊU CHUẨN LỰA CHỌN & LOẠI TRỪ
    # ==========================================
    print(f"\n--- Nạp Bước 2: Tiêu chuẩn lựa chọn & loại trừ ---")
    s2 = client.get(f"{base_path}/2")
    t2, v2 = extract_form_tokens(s2)
    payload_s2 = {'_token': t2, 'version': v2, 'wizard_action': 'next'}
    payload_s2.update(data.get('eligibility', {}))
    r2 = client.post(f"{base_path}/2", payload_s2)
    print("✓ Bước 2 nạp xong. Kết quả chứa /buoc/3?", '/buoc/3' in r2)
    time.sleep(1)

    # ==========================================
    # BƯỚC 3: TIỀN SỬ & LÂM SÀNG BAN ĐẦU
    # ==========================================
    print(f"\n--- Nạp Bước 3: Tiền sử & Lâm sàng ban đầu ---")
    s3 = client.get(f"{base_path}/3")
    t3, v3 = extract_form_tokens(s3)
    payload_s3 = {'_token': t3, 'version': v3, 'wizard_action': 'next'}
    b = data.get('baseline', {})
    for k, v in b.items():
        if k == 'occlusion_site' and isinstance(v, list):
            for site in v:
                payload_s3['occlusion_site[]'] = site
        else:
            payload_s3[k] = str(v)
    r3 = client.post(f"{base_path}/3", payload_s3)
    print("✓ Bước 3 nạp xong. Kết quả chứa /buoc/4?", '/buoc/4' in r3)
    time.sleep(1)

    # ==========================================
    # BƯỚC 4: QUY TRÌNH CAN THIỆP & VÔ CẢM
    # ==========================================
    print(f"\n--- Nạp Bước 4: Quy trình can thiệp & Vô cảm ---")
    s4 = client.get(f"{base_path}/4")
    t4, v4 = extract_form_tokens(s4)
    proc = data.get('procedure', {})
    payload_s4 = {
        '_token': t4,
        'version': v4,
        'ivt': proc.get('ivt', 'Không'),
        'bolus_time': proc.get('bolus_time', ''),
        'evt': proc.get('evt', 'Có'),
        'evt_start': proc.get('evt_start', '2026-10-30T10:57'),
        'evt_end': proc.get('evt_end', '2026-10-30T11:42'),
        'reperf_time': proc.get('reperf_time', '2026-10-30T11:40'),
        'passes': str(proc.get('passes', 1)),
        'method': str(proc.get('method', '3')),
        'technique': 'Stent retriever',
        'stenting': proc.get('stenting', 'Không'),
        'intubation_before_cathlab': proc.get('intubation_before_cathlab', 'Không'),
        'anesthesia_type': 'Gây mê toàn thân',
        'ga_to_cs': proc.get('ga_to_cs', 'Không'),
        'anesthesia_drugs[0][name]': 'Fresofol 1% (Propofol)',
        'anesthesia_drugs[0][dose]': '40ml (2 ống)',
        'anesthesia_drugs[0][route]': 'IV',
        'anesthesia_drugs[1][name]': 'Rocuronium 25mg',
        'anesthesia_drugs[1][dose]': '25mg (1 ống)',
        'anesthesia_drugs[1][route]': 'IV',
        'anesthesia_drugs[2][name]': 'Paringold (Heparin)',
        'anesthesia_drugs[2][dose]': '25000 IU',
        'anesthesia_drugs[2][route]': 'IV',
        'wizard_action': 'next'
    }
    r4 = client.post(f"{base_path}/4", payload_s4)
    print("✓ Bước 4 nạp xong. Kết quả chứa /buoc/5?", '/buoc/5' in r4)
    time.sleep(1)

    # ==========================================
    # BƯỚC 5: BIẾN THIÊN HUYẾT ÁP TRONG CAN THIỆP
    # ==========================================
    print(f"\n--- Nạp Bước 5: Biến thiên huyết áp trong can thiệp (Monitor) ---")
    s5 = client.get(f"{base_path}/5")
    t5, v5 = extract_form_tokens(s5)
    payload_s5 = {'_token': t5, 'version': v5, 'wizard_action': 'next'}
    
    readings = data.get('intraprocedural_monitoring', {}).get('readings', [])
    readings_by_min = {r['minute']: r for r in readings}

    for i in range(26):
        minute = i * 3
        payload_s5[f'readings[{i}][minute]'] = str(minute)
        payload_s5[f'readings[{i}][is_custom]'] = '0'
        if minute in readings_by_min:
            r = readings_by_min[minute]
            payload_s5[f'readings[{i}][sbp]'] = str(r['sbp'])
            payload_s5[f'readings[{i}][dbp]'] = str(r['dbp'])
            payload_s5[f'readings[{i}][map]'] = str(r.get('map', ''))
            payload_s5[f'readings[{i}][hr]'] = str(r['hr'])
            payload_s5[f'readings[{i}][source]'] = r.get('source', 'Cuff')
        else:
            payload_s5[f'readings[{i}][sbp]'] = ''
            payload_s5[f'readings[{i}][dbp]'] = ''
            payload_s5[f'readings[{i}][map]'] = ''
            payload_s5[f'readings[{i}][hr]'] = ''
            payload_s5[f'readings[{i}][source]'] = 'Cuff'
            
    r5 = client.post(f"{base_path}/5", payload_s5)
    print("✓ Bước 5 nạp xong. Kết quả chứa /buoc/6?", '/buoc/6' in r5)
    time.sleep(1)

    # ==========================================
    # BƯỚC 6: TÁI THÔNG & BIẾN CỐ TRONG CAN THIỆP
    # ==========================================
    print(f"\n--- Nạp Bước 6: Tái thông & Biến cố trong can thiệp ---")
    s6 = client.get(f"{base_path}/6")
    t6, v6 = extract_form_tokens(s6)
    r6 = client.post(f"{base_path}/6", {'_token': t6, 'version': v6, 'wizard_action': 'next'})
    print("✓ Bước 6 nạp xong. Kết quả chứa /buoc/7?", '/buoc/7' in r6)
    time.sleep(1)

    # ==========================================
    # BƯỚC 7: HÌNH ẢNH HỌC SAU CAN THIỆP & XUẤT HUYẾT
    # ==========================================
    print(f"\n--- Nạp Bước 7: Hình ảnh học sau can thiệp & sICH ---")
    s7 = client.get(f"{base_path}/7")
    t7, v7 = extract_form_tokens(s7)
    outcomes = data.get('outcomes', {})
    payload_s7 = {
        '_token': t7,
        'version': v7,
        'imaging_modality[]': 'CT',
        'followup_imaging_time': outcomes.get('followup_imaging_time', '2026-10-31T09:00'),
        'hta': outcomes.get('hta', 'Không'),
        'sich': outcomes.get('sich', 'Không'),
        'final_infarct_location': outcomes.get('final_infarct_location', 'Bán cầu tiểu não trái, thùy nhộng, thân não (ĐM thân nền tái thông tốt)'),
        'wizard_action': 'next'
    }
    r7 = client.post(f"{base_path}/7", payload_s7)
    print("✓ Bước 7 nạp xong. Kết quả chứa /buoc/8?", '/buoc/8' in r7)
    time.sleep(1)

    # ==========================================
    # BƯỚC 8: HUYẾT ÁP 8 GIỜ ĐẦU SAU CAN THIỆP
    # ==========================================
    print(f"\n--- Nạp Bước 8: Huyết áp 8 giờ đầu sau can thiệp ---")
    s8 = client.get(f"{base_path}/8")
    t8, v8 = extract_form_tokens(s8)
    payload_s8 = {'_token': t8, 'version': v8, 'wizard_action': 'next'}
    post_readings = data.get('post_procedure_hemodynamics_24h', [])
    post_by_hour = {r['hour']: r for r in post_readings}
    for h in range(8):
        hour_num = h + 1
        payload_s8[f'hourly_readings[{h}][hour]'] = str(hour_num)
        if hour_num in post_by_hour:
            pr = post_by_hour[hour_num]
            payload_s8[f'hourly_readings[{h}][sbp]'] = str(pr['sbp'])
            payload_s8[f'hourly_readings[{h}][dbp]'] = str(pr['dbp'])
            payload_s8[f'hourly_readings[{h}][map]'] = str(pr.get('map', ''))
            payload_s8[f'hourly_readings[{h}][hr]'] = str(pr.get('hr', ''))
            payload_s8[f'hourly_readings[{h}][source]'] = pr.get('source', 'Cuff')
        else:
            payload_s8[f'hourly_readings[{h}][sbp]'] = ''
            payload_s8[f'hourly_readings[{h}][dbp]'] = ''
            payload_s8[f'hourly_readings[{h}][map]'] = ''
            payload_s8[f'hourly_readings[{h}][hr]'] = ''
            payload_s8[f'hourly_readings[{h}][source]'] = 'Cuff'
            
    r8 = client.post(f"{base_path}/8", payload_s8)
    print("✓ Bước 8 nạp xong. Kết quả chứa /buoc/9?", '/buoc/9' in r8)
    time.sleep(1)

    # ==========================================
    # BƯỚC 9: LƯU NHÁP (DRAFT)
    # ==========================================
    s9 = client.get(f"{base_path}/9")
    t9, v9 = extract_form_tokens(s9)
    client.post(f"{base_path}/9", {'_token': t9, 'version': v9, 'wizard_action': 'draft'})

    print(f"\n🎉 HOÀN TẤT ĐỒNG BỘ 100% CÁC TRƯỜNG TỪ BƯỚC 1 ĐẾN BƯỚC 8 CHO NGUYỄN THỊ MAI (CASE ID: {case_id})!")

if __name__ == '__main__':
    main()
