#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, re, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
from web_client import WebClient

def extract_form_tokens(html):
    token_m = re.search(r'name="_token" value="([^"]+)"', html)
    token = token_m.group(1) if token_m else ''
    ver_m = re.search(r'name="version" value="([^"]*)"', html)
    version = ver_m.group(1) if ver_m else ''
    return token, version

def submit_case_94():
    client = WebClient()
    print("1. Đăng nhập eCRF...")
    client.login('HV-WVDPV')
    
    case_id = 94
    base_path = f"/benh-an/{case_id}/buoc"
    
    # ---------------------------------------------
    # BƯỚC 4: QUY TRÌNH CAN THIỆP & VÔ CẢM
    # ---------------------------------------------
    print("\n=== NẠP BƯỚC 4 ===")
    s4 = client.get(f"{base_path}/4")
    t4, v4 = extract_form_tokens(s4)
    payload_s4 = {
        '_token': t4,
        'version': v4,
        'ivt': 'Không',
        'bolus_time': '',
        'evt': 'Có',
        'evt_start': '2026-10-28T11:46',
        'evt_end': '2026-10-28T12:40',
        'reperf_time': '2026-10-28T12:35',
        'passes': '6',
        'method': '2c',
        'technique': 'Kết hợp (Aspiration + Stent retriever)',
        'stenting': 'Không',
        'intubation_before_cathlab': 'Không',
        'anesthesia_type': 'Gây mê toàn thân',
        'ga_to_cs': 'Không',
        'anesthesia_drugs[0][name]': 'Fresofol 1% (Propofol)',
        'anesthesia_drugs[0][dose]': '20ml',
        'anesthesia_drugs[0][route]': 'IV',
        'anesthesia_drugs[1][name]': 'Fentanyl',
        'anesthesia_drugs[1][dose]': '0.1mg/2ml',
        'anesthesia_drugs[1][route]': 'IV',
        'anesthesia_drugs[2][name]': 'Nicardipine',
        'anesthesia_drugs[2][dose]': '20mg',
        'anesthesia_drugs[2][route]': 'IV',
        'anesthesia_drugs[3][name]': 'Lidocain hydroclorid',
        'anesthesia_drugs[3][dose]': '80mg (4ml)',
        'anesthesia_drugs[3][route]': 'Tiêm tại chỗ',
        'anesthesia_drugs[4][name]': 'Paringold (Heparin)',
        'anesthesia_drugs[4][dose]': '25000 IU',
        'anesthesia_drugs[4][route]': 'IV',
        'wizard_action': 'next'
    }
    r4 = client.post(f"{base_path}/4", payload_s4)
    print("Bước 4 nạp xong. Kết quả chứa /buoc/5?", '/buoc/5' in r4)
    time.sleep(1)

    # ---------------------------------------------
    # BƯỚC 5: HUYẾT ÁP MONITOR PHÒNG CAN THIỆP
    # ---------------------------------------------
    print("\n=== NẠP BƯỚC 5 ===")
    s5 = client.get(f"{base_path}/5")
    t5, v5 = extract_form_tokens(s5)
    
    with open('tran_minh_hao_ecrf_data.json', 'r') as f:
        data = json.load(f)
    readings = data.get('intraprocedural_monitoring', {}).get('readings', [])
    readings_by_min = {r['minute']: r for r in readings}

    payload_s5 = {'_token': t5, 'version': v5, 'wizard_action': 'next'}
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
    print("Bước 5 nạp xong. Kết quả chứa /buoc/6?", '/buoc/6' in r5)
    time.sleep(1)

    # ---------------------------------------------
    # BƯỚC 6: BIẾN CHỨNG & THUỐC CAN THIỆP
    # ---------------------------------------------
    print("\n=== NẠP BƯỚC 6 ===")
    s6 = client.get(f"{base_path}/6")
    t6, v6 = extract_form_tokens(s6)
    r6 = client.post(f"{base_path}/6", {'_token': t6, 'version': v6, 'wizard_action': 'next'})
    print("Bước 6 nạp xong. Kết quả chứa /buoc/7?", '/buoc/7' in r6)
    time.sleep(1)

    # ---------------------------------------------
    # BƯỚC 7: HÌNH ẢNH 24H & sICH
    # ---------------------------------------------
    print("\n=== NẠP BƯỚC 7 ===")
    s7 = client.get(f"{base_path}/7")
    t7, v7 = extract_form_tokens(s7)
    payload_s7 = {
        '_token': t7,
        'version': v7,
        'imaging_modality[]': 'CT',
        'followup_imaging_time': '2026-10-29T11:56',
        'hta': 'Không',
        'sich': 'Không',
        'final_infarct_location': 'Bán cầu não trái (thùy thái dương đỉnh trái, thùy trán trái, thùy đảo trái)',
        'wizard_action': 'next'
    }
    r7 = client.post(f"{base_path}/7", payload_s7)
    print("Bước 7 nạp xong. Kết quả chứa /buoc/8?", '/buoc/8' in r7)
    time.sleep(1)

    # ---------------------------------------------
    # BƯỚC 8: HUYẾT ÁP 8 GIỜ ĐẦU SAU CAN THIỆP
    # ---------------------------------------------
    print("\n=== NẠP BƯỚC 8 ===")
    s8 = client.get(f"{base_path}/8")
    t8, v8 = extract_form_tokens(s8)
    
    # 8 giờ đầu sau can thiệp:
    # H1: 120/80 (MAP 93, HR 140)
    # H2: 116/67 (MAP 83, HR 119)
    # H3: 122/68 (MAP 86, HR 111)
    # H4: 129/69 (MAP 89, HR 103)
    # H5: 136/70 (MAP 92, HR 96)
    # H6: 142/72 (MAP 95, HR 101)
    # H7: 148/74 (MAP 99, HR 106)
    # H8: 154/76 (MAP 102, HR 112)
    hourly_data = [
        (1, 120, 80, 93, 140),
        (2, 116, 67, 83, 119),
        (3, 122, 68, 86, 111),
        (4, 129, 69, 89, 103),
        (5, 136, 70, 92, 96),
        (6, 142, 72, 95, 101),
        (7, 148, 74, 99, 106),
        (8, 154, 76, 102, 112)
    ]
    payload_s8 = {'_token': t8, 'version': v8, 'wizard_action': 'next'}
    for idx, (hour, sbp, dbp, map_val, hr) in enumerate(hourly_data):
        payload_s8[f'hourly_readings[{idx}][hour]'] = str(hour)
        payload_s8[f'hourly_readings[{idx}][sbp]'] = str(sbp)
        payload_s8[f'hourly_readings[{idx}][dbp]'] = str(dbp)
        payload_s8[f'hourly_readings[{idx}][map]'] = str(map_val)
        payload_s8[f'hourly_readings[{idx}][hr]'] = str(hr)
        payload_s8[f'hourly_readings[{idx}][source]'] = 'Cuff'
        
    r8 = client.post(f"{base_path}/8", payload_s8)
    print("Bước 8 nạp xong. Kết quả chứa /buoc/9?", '/buoc/9' in r8)
    time.sleep(1)

    # ---------------------------------------------
    # BƯỚC 9: KẾT CỤC XUẤT VIỆN & VIÊM PHỔI PISCES
    # ---------------------------------------------
    print("\n=== NẠP BƯỚC 9 ===")
    s9 = client.get(f"{base_path}/9")
    t9, v9 = extract_form_tokens(s9)
    payload_s9 = {
        '_token': t9,
        'version': v9,
        'nihss_post': '20',
        'nihss_24h': '20',
        'nihss_discharge': '20',
        'discharged_at': '2026-10-30T13:15',
        'los': '2',
        'extubation_hours': '',
        'neuro_worse': 'Có',
        'in_hospital_death': 'Không',
        'toast': 'Căn nguyên tim',
        'reintubation': '0',
        'pisces_sys_fever': '1',
        'pisces_resp_sputum': '1',
        'pisces_resp_rale': '1',
        'pisces_resp_gas': '1',
        'pneumonia': 'Có',
        'pneumonia_onset': '2026-10-28T14:11',
        'pneumonia_type': 'Viêm phổi liên quan đột quỵ  (SAP)',
        'antibiotic_use': 'Có',
        'antibiotic_name': 'Nerosyn (Ampicillin/Sulbactam) + Amikacin',
        'notes': 'Bệnh nhân nam 76 tuổi, tiền sử THA, rung nhĩ mạn tính. Nhồi máu não cấp giờ thứ 9 do tắc ICA trái và MCA M1 trái, can thiệp lấy huyết khối hút REACT 71 kết hợp Solitaire X 4x20 (Solumbra) 6 passes, tái thông TICI 2c. Sau can thiệp hôn mê, thở máy qua NKQ, biến chứng viêm phổi liên quan đột quỵ (SAP), phù não diện rộng trên CT 24h. Ngày 30/10/2026 gia đình xin chuyển viện lên Bệnh viện Bạch Mai điều trị tiếp.',
        'wizard_action': 'draft'
    }
    r9 = client.post(f"{base_path}/9", payload_s9)
    print("Bước 9 nạp xong. Độ dài phản hồi:", len(r9))
    print("🎉 ĐÃ HOÀN TẤT ĐỒNG BỘ CẢ 9 BƯỚC CHO CASE ID 94!")

if __name__ == '__main__':
    submit_case_94()
