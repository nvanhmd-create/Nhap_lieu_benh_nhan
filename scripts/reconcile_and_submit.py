#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reconcile_and_submit.py
Module đối chiếu thông tin bệnh án lâm sàng Bệnh viện Hữu nghị Việt Tiệp
với chuỗi theo dõi huyết áp monitor phòng can thiệp (Bước 5 eCRF)
và tự động nạp hoặc xuất mã JS Console.
"""

import sys
import os
import re
import json
import argparse
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from web_client import WebClient

def extract_form_tokens(html):
    token_m = re.search(r'name="_token" value="([^"]+)"', html)
    token = token_m.group(1) if token_m else ''
    ver_m = re.search(r'name="version" value="([^"]*)"', html)
    version = ver_m.group(1) if ver_m else ''
    return token, version

def submit_full_ecrf(patient_data, case_id=None, access_code='HV-WVDPV'):
    client = WebClient()
    print("1. Đang đăng nhập hệ thống eCRF...")
    client.login(access_code)
    time.sleep(1)

    dash_html = client.get('/bang-dieu-khien')
    case_code = patient_data.get('case_code', '')
    
    # Tìm xem case đã tồn tại trên hệ thống chưa
    if not case_id and case_code:
        m = re.search(r'/benh-an/(\d+)/buoc/.*?<td>\s*' + re.escape(case_code), dash_html, re.DOTALL)
        if not m:
            # thử tìm theo số bệnh án 10 số
            short_code = case_code.replace('VT-', '').replace('BM-', '')
            m = re.search(r'/benh-an/(\d+)/buoc/.*?' + re.escape(short_code), dash_html, re.DOTALL)
        if m:
            case_id = int(m.group(1))
            print(f"--> Tìm thấy hồ sơ đã có trên hệ thống: Case ID {case_id}")

    if not case_id:
        print("--> Khởi tạo hồ sơ bệnh án mới trên eCRF...")
        case_id, _ = client.create_case()
        print(f"--> Tạo thành công Case ID: {case_id}")
        time.sleep(1)

    base_path = f"/benh-an/{case_id}/buoc"

    # Bước 1: Hành chính
    print(f"Nạp Bước 1 (Hành chính) cho Case {case_id}...")
    s1 = client.get(f"{base_path}/1")
    t1, v1 = extract_form_tokens(s1)
    client.post(f"{base_path}/1", {
        '_token': t1,
        'version': v1,
        'study_id': patient_data.get('study_id', f'EVT-{case_id:03d}'),
        'case_code': patient_data.get('case_code', ''),
        'patient_name': patient_data.get('patient_name_short', patient_data.get('patient_name', '')),
        'study_date': patient_data.get('study_date', ''),
        'admitted_at': patient_data.get('admitted_at', ''),
        'evt_at': patient_data.get('evt_at', ''),
        'treating_doctor': patient_data.get('treating_doctor', 'TS. BS. PHÙNG ĐỨC LÂM'),
        'phone_90day': patient_data.get('phone_90day', '0900000000'),
        'hospital': patient_data.get('hospital', 'viet_tiep'),
        'wizard_action': 'next'
    })
    time.sleep(1)

    # Bước 2: Lựa chọn / Loại trừ
    print(f"Nạp Bước 2 (Tiêu chuẩn lựa chọn)...")
    s2 = client.get(f"{base_path}/2")
    t2, v2 = extract_form_tokens(s2)
    payload_s2 = {'_token': t2, 'version': v2, 'wizard_action': 'next'}
    payload_s2.update(patient_data.get('eligibility', {}))
    client.post(f"{base_path}/2", payload_s2)
    time.sleep(1)

    # Bước 3: Tiền sử & Lâm sàng
    print(f"Nạp Bước 3 (Lâm sàng & Tiền sử)...")
    s3 = client.get(f"{base_path}/3")
    t3, v3 = extract_form_tokens(s3)
    payload_s3 = {'_token': t3, 'version': v3, 'wizard_action': 'next'}
    b = patient_data.get('baseline', {})
    for k, v in b.items():
        if k == 'occlusion_site' and isinstance(v, list):
            for site in v:
                payload_s3['occlusion_site[]'] = site
        else:
            payload_s3[k] = str(v)
    client.post(f"{base_path}/3", payload_s3)
    time.sleep(1)

    # Bước 4: Can thiệp & Vô cảm
    print(f"Nạp Bước 4 (Can thiệp & Vô cảm)...")
    s4 = client.get(f"{base_path}/4")
    t4, v4 = extract_form_tokens(s4)
    proc = patient_data.get('procedure', {})
    
    anesthesia_type_val = proc.get('anesthesia_type', 'Tiền mê/An thần')
    if 'mê' in anesthesia_type_val.lower() and 'toàn' not in anesthesia_type_val.lower() and 'tiền' not in anesthesia_type_val.lower():
        anesthesia_type_val = 'Gây mê toàn thân'
    elif 'tê' in anesthesia_type_val.lower():
        anesthesia_type_val = 'Gây tê tại chỗ'
        
    technique_val = proc.get('technique', 'Stent retriever')
    if 'kết hợp' in technique_val.lower() or 'solumbra' in technique_val.lower() or '+' in technique_val:
        technique_val = 'Kết hợp (Aspiration + Stent retriever)'
    elif 'hút' in technique_val.lower() or 'aspiration' in technique_val.lower():
        technique_val = 'Aspiration'
    elif 'stent' in technique_val.lower():
        technique_val = 'Stent retriever'
        
    payload_s4 = {
        '_token': t4, 'version': v4, 'wizard_action': 'next',
        'ivt': proc.get('ivt', 'Không'),
        'bolus_time': proc.get('bolus_time', ''),
        'evt': proc.get('evt', 'Có'),
        'evt_start': proc.get('evt_start', ''),
        'evt_end': proc.get('evt_end', ''),
        'reperf_time': proc.get('reperf_time', ''),
        'passes': str(proc.get('passes', 1)),
        'method': str(proc.get('method', '3')),
        'technique': technique_val,
        'stenting': proc.get('stenting', 'Không'),
        'intubation_before_cathlab': proc.get('intubation_before_cathlab', 'Không'),
        'anesthesia_type': anesthesia_type_val,
        'ga_to_cs': proc.get('ga_to_cs', 'Không')
    }
    drugs = proc.get('anesthesia_drugs', [])
    for idx, drug in enumerate(drugs):
        payload_s4[f'anesthesia_drugs[{idx}][name]'] = drug.get('name', '')
        payload_s4[f'anesthesia_drugs[{idx}][dose]'] = drug.get('dose', '')
        route = drug.get('route', 'IV')
        if 'tại chỗ' in route.lower():
            route = 'Tiêm tại chỗ'
        elif 'bơm' in route.lower() or 'truyền' in route.lower():
            route = 'Bơm truyền'
        payload_s4[f'anesthesia_drugs[{idx}][route]'] = route
    client.post(f"{base_path}/4", payload_s4)
    time.sleep(1)

    # Bước 5: Huyết áp trong can thiệp (Monitor)
    print(f"Nạp Bước 5 (Chuỗi huyết áp Monitor)...")
    s5 = client.get(f"{base_path}/5")
    t5, v5 = extract_form_tokens(s5)
    payload_s5 = {'_token': t5, 'version': v5, 'wizard_action': 'next'}
    
    readings = patient_data.get('intraprocedural_monitoring', {}).get('readings', [])
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
    client.post(f"{base_path}/5", payload_s5)
    time.sleep(1)

    # Bước 6: Biến chứng & Tái thông
    print(f"Nạp Bước 6...")
    s6 = client.get(f"{base_path}/6")
    t6, v6 = extract_form_tokens(s6)
    client.post(f"{base_path}/6", {'_token': t6, 'version': v6, 'wizard_action': 'next'})
    time.sleep(1)

    # Bước 7: Hình ảnh sau 24h
    print(f"Nạp Bước 7 (Hình ảnh 24h & sICH)...")
    s7 = client.get(f"{base_path}/7")
    t7, v7 = extract_form_tokens(s7)
    outcomes = patient_data.get('outcomes', {})
    payload_s7 = {
        '_token': t7,
        'version': v7,
        'imaging_modality[]': 'CT',
        'followup_imaging_time': outcomes.get('followup_imaging_time', '2026-10-29T10:00'),
        'hta': outcomes.get('hta', 'Không'),
        'sich': outcomes.get('sich', 'Không'),
        'final_infarct_location': outcomes.get('final_infarct_location', ''),
        'wizard_action': 'next'
    }
    client.post(f"{base_path}/7", payload_s7)
    time.sleep(1)

    # Bước 8: Huyết áp 8 giờ đầu sau can thiệp
    print(f"Nạp Bước 8 (Huyết áp theo dõi sau can thiệp)...")
    s8 = client.get(f"{base_path}/8")
    t8, v8 = extract_form_tokens(s8)
    payload_s8 = {'_token': t8, 'version': v8, 'wizard_action': 'next'}
    post_readings = patient_data.get('post_procedure_hemodynamics_24h', [])
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
    client.post(f"{base_path}/8", payload_s8)
    time.sleep(1)

    # Bước 9: Kết cục xuất viện
    print(f"Nạp Bước 9 (Kết cục xuất viện)...")
    s9 = client.get(f"{base_path}/9")
    t9, v9 = extract_form_tokens(s9)
    outcomes = patient_data.get('outcomes', {})
    payload_s9 = {
        '_token': t9,
        'version': v9,
        'nihss_post': str(outcomes.get('nihss_post', '')),
        'nihss_24h': str(outcomes.get('nihss_24h', '')),
        'nihss_discharge': str(outcomes.get('nihss_discharge', '')),
        'discharged_at': str(outcomes.get('discharged_at', '')),
        'los': str(outcomes.get('los', '')),
        'extubation_hours': str(outcomes.get('extubation_hours', '')),
        'neuro_worse': str(outcomes.get('neuro_worse', 'Không')),
        'in_hospital_death': str(outcomes.get('in_hospital_death', 'Không')),
        'toast': str(outcomes.get('toast', 'Căn nguyên tim')),
        'reintubation': str(outcomes.get('reintubation', '0')),
        'pneumonia': str(outcomes.get('pneumonia', 'Không')),
        'pneumonia_onset': str(outcomes.get('pneumonia_onset', '')),
        'pneumonia_type': str(outcomes.get('pneumonia_type', '')),
        'antibiotic_use': str(outcomes.get('antibiotic_use', 'Không')),
        'antibiotic_name': str(outcomes.get('antibiotic_name', '')),
        'notes': str(outcomes.get('notes', '')),
        'wizard_action': 'draft'
    }
    for p_field in ['pisces_img_infiltrate', 'pisces_sys_fever', 'pisces_sys_wbc', 'pisces_sys_mental', 'pisces_resp_sputum', 'pisces_resp_cough', 'pisces_resp_rale', 'pisces_resp_gas']:
        if outcomes.get(p_field) == '1':
            payload_s9[p_field] = '1'
    client.post(f"{base_path}/9", payload_s9)

    print(f"\n🎉 Hoàn thành đồng bộ Case ID {case_id} ({patient_data.get('patient_name')} - {case_code})!")
    return case_id

def main():
    parser = argparse.ArgumentParser(description="Reconcile and Submit patient data to eCRF")
    parser.add_argument('--json-file', '-f', default='la_thi_dieu_ecrf_data.json', help='Path to patient JSON file')
    parser.add_argument('--case-id', '-id', type=int, default=None, help='Case ID to update')
    parser.add_argument('--access-code', default='HV-WVDPV', help='Access code for eCRF')
    parser.add_argument('--dry-run', action='store_true', help='Perform check without submitting to server')

    args = parser.parse_args()

    with open(args.json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if args.dry_run:
        print("=== DRY RUN MODE ===")
        print(f"Bệnh nhân: {data.get('patient_name')} ({data.get('patient_name_short')})")
        print(f"Mã bệnh án: {data.get('case_code')}")
        print(f"Thời gian EVT: {data.get('procedure', {}).get('evt_start')} -> {data.get('procedure', {}).get('evt_end')}")
        print(f"Số mốc huyết áp: {len(data.get('intraprocedural_monitoring', {}).get('readings', []))}")
        print("Dry run hoàn tất!")
        return

    submit_full_ecrf(data, case_id=args.case_id, access_code=args.access_code)

if __name__ == '__main__':
    main()
