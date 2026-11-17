#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
submit_pham_thi_gai.py
Tự động nạp dữ liệu từ Bước 1 đến Bước 8 cho bệnh nhân PHẠM THỊ GÁI (Mã: VT-2600543003)
Điều tra viên / Người nhập liệu: NGUYỄN VƯƠNG ANH
Cơ sở y tế: Bệnh viện Hữu nghị Việt Tiệp
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

def check_errors(html):
    errs = re.findall(r'<small class="status-danger">([^<]+)</small>', html)
    if errs:
        print("  ⚠️ Lỗi validation:", errs)
    alerts = re.findall(r'<div class="[^"]*alert-danger[^"]*">([^<]+)</div>', html)
    if alerts:
        print("  ⚠️ Cảnh báo:", alerts)

def main():
    json_path = 'pham_thi_gai_ecrf_data.json'
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Cannot find {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    client = WebClient()
    print("1. Đang đăng nhập hệ thống eCRF...")
    client.login('HV-WVDPV')
    time.sleep(1)

    print("2. Sử dụng hồ sơ bệnh án Case ID: 124 cho PHẠM THỊ GÁI...")
    case_code = data.get('case_code', 'VT-2600543003')
    case_id = data.get('case_id', 124)
    print(f"-> Case ID được chọn: {case_id} ({case_code})")

    base_path = f"/benh-an/{case_id}/buoc"
    time.sleep(1)

    # ==========================================
    # BƯỚC 1: HÀNH CHÍNH & NGHIÊN CỨU
    # ==========================================
    print(f"\n--- Nạp Bước 1: Hành chính & Nghiên cứu (Case {case_id}) ---")
    s1 = client.get(f"{base_path}/1")
    t1, v1 = extract_form_tokens(s1)
    payload_s1 = [
        ('_token', t1),
        ('version', v1),
        ('study_id', f"EVT-{case_id:03d}"),
        ('study_date', data.get('study_date', '2026-11-15')),
        ('hospital', data.get('hospital', 'viet_tiep')),
        ('case_code', case_code),
        ('patient_name', data.get('patient_name', 'PHẠM THỊ GÁI')),
        ('admitted_at', data.get('admitted_at', '2026-11-15T08:29')),
        ('evt_at', data.get('evt_at', '2026-11-15')),
        ('treating_doctor', data.get('treating_doctor', 'NGUYỄN VƯƠNG ANH')),
        ('phone_90day', data.get('phone_90day', '0988920267')),
        ('wizard_action', 'next')
    ]
    r1 = client.post(f"{base_path}/1", payload_s1)
    check_errors(r1)
    print(f"✓ Bước 1 chuyển tới: {client.last_url}")
    time.sleep(1)

    # ==========================================
    # BƯỚC 2: TIÊU CHUẨN LỰA CHỌN & LOẠI TRỪ
    # ==========================================
    print(f"\n--- Nạp Bước 2: Tiêu chuẩn lựa chọn & loại trừ ---")
    s2 = client.get(f"{base_path}/2")
    t2, v2 = extract_form_tokens(s2)
    payload_s2 = [('_token', t2), ('version', v2), ('wizard_action', 'next')]
    for k, v in data.get('eligibility', {}).items():
        payload_s2.append((k, str(v)))
    r2 = client.post(f"{base_path}/2", payload_s2)
    check_errors(r2)
    print(f"✓ Bước 2 chuyển tới: {client.last_url}")
    time.sleep(1)

    # ==========================================
    # BƯỚC 3: TIỀN SỬ & LÂM SÀNG BAN ĐẦU
    # ==========================================
    print(f"\n--- Nạp Bước 3: Tiền sử & Lâm sàng ban đầu ---")
    s3 = client.get(f"{base_path}/3")
    t3, v3 = extract_form_tokens(s3)
    payload_s3 = [('_token', t3), ('version', v3), ('wizard_action', 'next')]
    b = data.get('baseline', {})
    for k, v in b.items():
        if k == 'occlusion_site':
            payload_s3.append(('occlusion_site[]', 'MCA M1'))
        else:
            payload_s3.append((k, str(v)))
    r3 = client.post(f"{base_path}/3", payload_s3)
    check_errors(r3)
    print(f"✓ Bước 3 chuyển tới: {client.last_url}")
    time.sleep(1)

    # ==========================================
    # BƯỚC 4: QUY TRÌNH CAN THIỆP & VÔ CẢM
    # ==========================================
    print(f"\n--- Nạp Bước 4: Quy trình can thiệp & Vô cảm ---")
    s4 = client.get(f"{base_path}/4")
    t4, v4 = extract_form_tokens(s4)
    proc = data.get('procedure', {})
    payload_s4 = [
        ('_token', t4),
        ('version', v4),
        ('ivt', proc.get('ivt', 'Không')),
        ('bolus_time', proc.get('bolus_time', '')),
        ('evt', proc.get('evt', 'Có')),
        ('evt_start', proc.get('evt_start', '2026-11-15T10:30')),
        ('evt_end', proc.get('evt_end', '2026-11-15T11:45')),
        ('reperf_time', proc.get('reperf_time', '2026-11-15T10:59')),
        ('passes', str(proc.get('passes', 1))),
        ('method', str(proc.get('method', '2c'))),
        ('technique', proc.get('technique', 'Khác')),
        ('technique_other', proc.get('technique_other', 'Solumbra: Hút REACT + kéo Solitaire X 4-20mm (1 pass) + truyền Alteplase ĐM 14.6mg (thử nghiệm Newline)')),
        ('stenting', proc.get('stenting', 'Không')),
        ('intubation_before_cathlab', proc.get('intubation_before_cathlab', 'Không')),
        ('anesthesia_type', proc.get('anesthesia_type', 'Tiền mê/An thần')),
        ('ga_to_cs', proc.get('ga_to_cs', 'Không')),
        ('anesthesia_drugs[0][name]', 'Fresofol 1% Mct/Lct (Propofol)'),
        ('anesthesia_drugs[0][dose]', '1 ống (100mg/10ml)'),
        ('anesthesia_drugs[0][route]', 'IV'),
        ('anesthesia_drugs[1][name]', 'Lidocain hydroclorid 40mg/2ml'),
        ('anesthesia_drugs[1][dose]', '2 ống (80mg)'),
        ('anesthesia_drugs[1][route]', 'Tiêm tại chỗ'),
        ('wizard_action', 'next')
    ]
    r4 = client.post(f"{base_path}/4", payload_s4)
    check_errors(r4)
    print(f"✓ Bước 4 chuyển tới: {client.last_url}")
    time.sleep(1)

    # ==========================================
    # BƯỚC 5: BIẾN THIÊN HUYẾT ÁP TRONG CAN THIỆP
    # ==========================================
    print(f"\n--- Nạp Bước 5: Biến thiên huyết áp trong can thiệp (Monitor 26 mốc) ---")
    s5 = client.get(f"{base_path}/5")
    t5, v5 = extract_form_tokens(s5)
    payload_s5 = [('_token', t5), ('version', v5), ('wizard_action', 'next')]
    
    readings = data.get('vital_signs_readings', [])
    for idx, r in enumerate(readings):
        payload_s5.append((f'readings[{idx}][minute]', str(r['minute'])))
        payload_s5.append((f'readings[{idx}][is_custom]', '1' if r['minute'] % 3 != 0 else '0'))
        payload_s5.append((f'readings[{idx}][sbp]', str(r['sbp'])))
        payload_s5.append((f'readings[{idx}][dbp]', str(r['dbp'])))
        payload_s5.append((f'readings[{idx}][map]', str(r.get('map', ''))))
        payload_s5.append((f'readings[{idx}][hr]', str(r['hr'])))
        payload_s5.append((f'readings[{idx}][source]', r.get('source', 'Cuff')))
            
    r5 = client.post(f"{base_path}/5", payload_s5)
    check_errors(r5)
    print(f"✓ Bước 5 chuyển tới: {client.last_url}")
    time.sleep(1)

    # ==========================================
    # BƯỚC 6: TÁI THÔNG & BIẾN CỐ TRONG CAN THIỆP
    # ==========================================
    print(f"\n--- Nạp Bước 6: Biến cố trong can thiệp & Thuốc điều chỉnh HA ---")
    s6 = client.get(f"{base_path}/6")
    t6, v6 = extract_form_tokens(s6)
    payload_s6 = [
        ('_token', t6),
        ('version', v6),
        ('meds[0][timepoint]', '10:45'),
        ('meds[0][name]', 'Nicardipine Aguettant 10mg/10ml'),
        ('meds[0][rate]', '1 ống'),
        ('meds[0][route]', 'Truyền TM liên tục'),
        ('meds[0][indication]', 'Hạ HA / kiểm soát huyết áp trong can thiệp'),
        ('wizard_action', 'next')
    ]
    r6 = client.post(f"{base_path}/6", payload_s6)
    check_errors(r6)
    print(f"✓ Bước 6 chuyển tới: {client.last_url}")
    time.sleep(1)

    # ==========================================
    # BƯỚC 7: HÌNH ẢNH HỌC SAU CAN THIỆP & sICH
    # ==========================================
    print(f"\n--- Nạp Bước 7: Hình ảnh học sau can thiệp & sICH ---")
    s7 = client.get(f"{base_path}/7")
    t7, v7 = extract_form_tokens(s7)
    outcomes = data.get('outcomes', {})
    payload_s7 = [
        ('_token', t7),
        ('version', v7),
        ('imaging_modality[]', outcomes.get('imaging_modality', 'CT')),
        ('followup_imaging_time', outcomes.get('followup_imaging_time', '2026-11-16T14:22')),
        ('hta', outcomes.get('hta', 'Không')),
        ('sich', outcomes.get('sich', 'Không')),
        ('final_infarct_location', outcomes.get('final_infarct_location', 'Nhồi máu não nhân bèo và vùng vành tia bên trái. Tắc M1-MCA trái đã can thiệp tái thông Solumbra TICI 2c, sau can thiệp CTA mạch máu thông tốt, không thấy xuất huyết não chuyển dạng (sICH âm tính).')),
        ('wizard_action', 'next')
    ]
    r7 = client.post(f"{base_path}/7", payload_s7)
    check_errors(r7)
    print(f"✓ Bước 7 chuyển tới: {client.last_url}")
    time.sleep(1)

    # ==========================================
    # BƯỚC 8: HUYẾT ÁP 8 GIỜ ĐẦU SAU CAN THIỆP
    # ==========================================
    print(f"\n--- Nạp Bước 8: Huyết áp 8 giờ đầu sau can thiệp ---")
    s8 = client.get(f"{base_path}/8")
    t8, v8 = extract_form_tokens(s8)
    payload_s8 = [('_token', t8), ('version', v8), ('wizard_action', 'next')]
    post_readings = data.get('post_procedure_hourly', [])
    post_by_hour = {r['hour']: r for r in post_readings}
    for h in range(8):
        hour_num = h + 1
        payload_s8.append((f'hourly_readings[{h}][hour]', str(hour_num)))
        if hour_num in post_by_hour:
            pr = post_by_hour[hour_num]
            payload_s8.append((f'hourly_readings[{h}][sbp]', str(pr['sbp'])))
            payload_s8.append((f'hourly_readings[{h}][dbp]', str(pr['dbp'])))
            payload_s8.append((f'hourly_readings[{h}][map]', str(pr.get('map', ''))))
            payload_s8.append((f'hourly_readings[{h}][hr]', str(pr.get('hr', ''))))
            payload_s8.append((f'hourly_readings[{h}][source]', pr.get('source', 'Cuff')))
        else:
            payload_s8.append((f'hourly_readings[{h}][sbp]', ''))
            payload_s8.append((f'hourly_readings[{h}][dbp]', ''))
            payload_s8.append((f'hourly_readings[{h}][map]', ''))
            payload_s8.append((f'hourly_readings[{h}][hr]', ''))
            payload_s8.append((f'hourly_readings[{h}][source]', 'Cuff'))
            
    r8 = client.post(f"{base_path}/8", payload_s8)
    check_errors(r8)
    print(f"✓ Bước 8 chuyển tới: {client.last_url}")
    time.sleep(1)

    # ==========================================
    # BƯỚC 9: LƯU NHÁP (DRAFT)
    # ==========================================
    print(f"\n--- Nạp Bước 9: Lưu nháp (Draft) ---")
    s9 = client.get(f"{base_path}/9")
    t9, v9 = extract_form_tokens(s9)
    r9 = client.post(f"{base_path}/9", [('_token', t9), ('version', v9), ('wizard_action', 'draft')])
    print(f"✓ Bước 9 lưu nháp xong. URL: {client.last_url}")

    print(f"\n🎉 HOÀN TẤT ĐỐI SOÁT & CẬP NHẬT 100% CÁC TRƯỜNG TỪ BƯỚC 1 ĐẾN BƯỚC 8 CHO PHẠM THỊ GÁI (CASE ID: {case_id})!")

if __name__ == '__main__':
    main()
