#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, re, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from web_client import WebClient

def parse_html_fields(html):
    fields = {}
    
    # 1. Inputs
    input_matches = re.findall(r'<input\s+([^>]+)>', html, re.DOTALL)
    for tag in input_matches:
        name_m = re.search(r'name=[\"\']([^\"\']+)[\"\']', tag)
        if not name_m:
            continue
        name = name_m.group(1)
        type_m = re.search(r'type=[\"\']([^\"\']+)[\"\']', tag)
        input_type = type_m.group(1).lower() if type_m else 'text'
        
        val_m = re.search(r'value=[\"\']([^\"\']*)[\"\']', tag)
        val = val_m.group(1) if val_m else ''
        
        if input_type == 'radio':
            if 'checked' in tag:
                fields[name] = val
            elif name not in fields:
                fields[name] = None
        elif input_type == 'checkbox':
            if name.endswith('[]'):
                if name not in fields or not isinstance(fields[name], list):
                    fields[name] = []
                if 'checked' in tag:
                    fields[name].append(val)
            else:
                if 'checked' in tag:
                    fields[name] = val
                elif name not in fields:
                    fields[name] = None
        else:
            fields[name] = val

    # 2. Selects
    select_matches = re.findall(r'<select\s+([^>]+)>(.*?)</select>', html, re.DOTALL)
    for stag, sbody in select_matches:
        name_m = re.search(r'name=[\"\']([^\"\']+)[\"\']', stag)
        if not name_m:
            continue
        name = name_m.group(1)
        opt_m = re.search(r'<option\s+[^>]*selected[^>]*value=[\"\']([^\"\']*)[\"\']', sbody)
        if not opt_m:
            opt_m = re.search(r'<option\s+value=[\"\']([^\"\']*)[\"\'][^>]*selected', sbody)
        if opt_m:
            fields[name] = opt_m.group(1)
        else:
            fields[name] = ''

    # 3. Textareas
    ta_matches = re.findall(r'<textarea\s+([^>]+)>(.*?)</textarea>', html, re.DOTALL)
    for tatag, tbody in ta_matches:
        name_m = re.search(r'name=[\"\']([^\"\']+)[\"\']', tatag)
        if not name_m:
            continue
        name = name_m.group(1)
        fields[name] = tbody.strip()
        
    return fields

def audit_case(client, case_meta):
    cid = case_meta['case_id']
    result = {
        'meta': case_meta,
        'steps': {},
        'step_missing': {},
        'missing_summary': []
    }
    
    furthest_step = 9
    for step in range(1, 10):
        url = f"/benh-an/{cid}/buoc/{step}"
        try:
            html = client.get(url)
            f = parse_html_fields(html)
            f = {k: v for k, v in f.items() if k not in ['_token', 'version', 'csrf-token', 'viewport', 'wizard_action']}
            result['steps'][f'step_{step}'] = f
        except Exception as e:
            # print(f"Note: case {cid} step {step} error: {e}")
            result['steps'][f'step_{step}'] = {}
            if furthest_step == 9:
                furthest_step = step - 1
        time.sleep(0.15)

    s1 = result['steps'].get('step_1', {})
    s2 = result['steps'].get('step_2', {})
    s3 = result['steps'].get('step_3', {})
    s4 = result['steps'].get('step_4', {})
    s5 = result['steps'].get('step_5', {})
    s6 = result['steps'].get('step_6', {})
    s7 = result['steps'].get('step_7', {})
    s8 = result['steps'].get('step_8', {})
    s9 = result['steps'].get('step_9', {})
    
    # 1. BƯỚC 1: HÀNH CHÍNH
    s1_miss = []
    if not s1.get('treating_doctor'): s1_miss.append('Bác sĩ điều trị')
    phone = s1.get('phone_90day', '')
    if not phone or phone in ['0000000000', '0900000000', '0123456789']:
        s1_miss.append('SĐT theo dõi 90 ngày')
    if not s1.get('admitted_at'): s1_miss.append('Ngày giờ vào viện')
    if not s1.get('evt_at'): s1_miss.append('Ngày can thiệp')
    if s1_miss:
        result['step_missing']['b1'] = s1_miss
        result['missing_summary'].append(f"Bước 1 (Hành chính): Thiếu {', '.join(s1_miss)}")

    # 2. BƯỚC 2: TIÊU CHUẨN LỰA CHỌN
    s2_miss = []
    for k in ['inc_age', 'inc_ais_lvo', 'inc_bp_data', 'inc_consent', 'inc_hospital', 'exc_hemorrhage', 'exc_mrs4', 'exc_access', 'exc_missing', 'exc_pretreated', 'exc_reintervene']:
        if s2.get(k) is None:
            s2_miss.append(k)
    if s2_miss:
        result['step_missing']['b2'] = s2_miss
        result['missing_summary'].append(f"Bước 2 (Lựa chọn/Loại trừ): Chưa hoàn thiện {len(s2_miss)} tiêu chuẩn")

    # 3. BƯỚC 3: TIỀN SỬ & LÂM SÀNG
    s3_miss = []
    if not s3.get('height') or not s3.get('weight') or not s3.get('bmi'):
        s3_miss.append('Chiều cao / Cân nặng / BMI')
    if not s3.get('arrival_time'):
        s3_miss.append('Giờ đến viện')
    if not s3.get('last_known_well'):
        s3_miss.append('Giờ khởi phát (LKW)')
    if not s3.get('sbp_admission') or not s3.get('dbp_admission'):
        s3_miss.append('Huyết áp vào viện')
    if not s3.get('glucose'):
        s3_miss.append('Đường huyết vào viện')
    if not s3.get('nihss_admission'):
        s3_miss.append('NIHSS vào viện')
    if not s3.get('aspects'):
        s3_miss.append('Điểm ASPECTS')
    if not s3.get('occlusion_site[]') or len(s3.get('occlusion_site[]', [])) == 0:
        s3_miss.append('Vị trí tắc mạch')
    if not s3.get('collateral_status'):
        s3_miss.append('Tuần hoàn bàng hệ')
    if s3.get('htn') is None or s3.get('dm') is None:
        s3_miss.append('Tiền sử bệnh nền (THA/ĐTĐ/Rung nhĩ)')
    if s3_miss:
        result['step_missing']['b3'] = s3_miss
        result['missing_summary'].append(f"Bước 3 (Lâm sàng): Thiếu {', '.join(s3_miss)}")

    # 4. BƯỚC 4: QUY TRÌNH CAN THIỆP & VÔ CẢM
    s4_miss = []
    if not s4.get('evt_start'): s4_miss.append('Giờ chọc mạch (EVT start)')
    if not s4.get('reperf_time'): s4_miss.append('Giờ tái thông mạch')
    if not s4.get('evt_end'): s4_miss.append('Giờ kết thúc EVT')
    if not s4.get('passes'): s4_miss.append('Số lần kéo/hút huyết khối')
    if not s4.get('method'): s4_miss.append('Độ tái thông mTICI (method)')
    if not s4.get('technique'): s4_miss.append('Kỹ thuật can thiệp')
    if not s4.get('anesthesia_type'): s4_miss.append('Phương pháp vô cảm')
    if s4_miss:
        result['step_missing']['b4'] = s4_miss
        result['missing_summary'].append(f"Bước 4 (Can thiệp): Thiếu {', '.join(s4_miss)}")

    # 5. BƯỚC 5: BIẾN THIÊN HA TRONG CAN THIỆP
    s5_readings = 0
    for k, v in s5.items():
        if re.match(r'readings\[\d+\]\[sbp\]', k) and v and str(v).strip() and str(v) != '0':
            s5_readings += 1
    result['step5_readings_count'] = s5_readings
    if s5_readings == 0:
        result['step_missing']['b5'] = ['Chưa có chuỗi HA monitor phòng can thiệp (0 mốc)']
        result['missing_summary'].append('Bước 5 (Monitor HA can thiệp): Chưa có số liệu huyết áp monitor (0 mốc)')

    # 6. BƯỚC 6: BIẾN CHỨNG & THUỐC CAN THIỆP
    meds_count = 0
    for k, v in s6.items():
        if re.match(r'meds\[\d+\]\[name\]', k) and v and str(v).strip():
            meds_count += 1
    result['s6_meds_count'] = meds_count

    # 7. BƯỚC 7: HÌNH ẢNH 24H & sICH
    s7_miss = []
    if not s7.get('followup_imaging_time'): s7_miss.append('Thời điểm chụp hình ảnh sau 24h')
    if not s7.get('imaging_modality[]') or len(s7.get('imaging_modality[]', [])) == 0:
        s7_miss.append('Phương pháp chụp (CT/MRI)')
    if not s7.get('hta'): s7_miss.append('Chuyển dạng xuất huyết (ECASS)')
    if s7.get('sich') is None: s7_miss.append('Xuất huyết có triệu chứng sICH')
    if not s7.get('final_infarct_location'): s7_miss.append('Vị trí tổn thương nhồi máu cuối')
    if s7_miss:
        result['step_missing']['b7'] = s7_miss
        result['missing_summary'].append(f"Bước 7 (CĐHA sau can thiệp): Thiếu {', '.join(s7_miss)}")

    # 8. BƯỚC 8: HUYẾT ÁP 8 GIỜ ĐẦU SAU CAN THIỆP
    s8_readings = 0
    for k, v in s8.items():
        if re.match(r'hourly_readings\[\d+\]\[sbp\]', k) and v and str(v).strip() and str(v) != '0':
            s8_readings += 1
    result['step8_readings_count'] = s8_readings
    if s8_readings == 0:
        result['step_missing']['b8'] = ['Chưa có chuỗi HA 8 giờ sau can thiệp (0 mốc)']
        result['missing_summary'].append('Bước 8 (HA sau can thiệp): Chưa có chuỗi huyết áp 8 giờ đầu (0 mốc)')
    elif s8_readings < 8:
        result['step_missing']['b8'] = [f'Mới có {s8_readings}/8 mốc HA']
        result['missing_summary'].append(f'Bước 8 (HA sau can thiệp): Mới có {s8_readings}/8 mốc huyết áp')

    # 9. BƯỚC 9: KẾT CỤC XUẤT VIỆN & VIÊM PHỔI PISCES
    s9_miss = []
    if not s9.get('nihss_24h'): s9_miss.append('NIHSS 24h')
    if not s9.get('nihss_discharge'): s9_miss.append('NIHSS ra viện')
    if not s9.get('discharged_at'): s9_miss.append('Ngày ra viện')
    if not s9.get('los'): s9_miss.append('Thời gian nằm viện (LOS)')
    if not s9.get('mrs_discharge'): s9_miss.append('Thang mRS ra viện')
    if not s9.get('toast'): s9_miss.append('Phân loại căn nguyên TOAST')
    if s9.get('in_hospital_death') is None: s9_miss.append('Tử vong trong viện')
    if s9.get('neuro_worse') is None: s9_miss.append('Thần kinh xấu đi')
    if s9.get('pneumonia') is None: s9_miss.append('Viêm phổi trong viện')
    if s9_miss:
        result['step_missing']['b9'] = s9_miss
        result['missing_summary'].append(f"Bước 9 (Kết cục xuất viện): Thiếu {', '.join(s9_miss)}")

    return result

def main():
    with open('vt_cases_list.json', 'r', encoding='utf-8') as f:
        cases_list = json.load(f)
        
    output_path = 'audit_all_50_vt_cases_results.json'
    
    # Load already audited cases if available
    audited_map = {}
    if os.path.exists('audit_vt_9_cases_results.json'):
        with open('audit_vt_9_cases_results.json', 'r', encoding='utf-8') as f:
            for item in json.load(f):
                audited_map[item['meta']['case_id']] = item
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            for item in json.load(f):
                audited_map[item['meta']['case_id']] = item
                
    print(f"Pre-loaded {len(audited_map)} already audited cases.")
    
    client = WebClient()
    print("Đang đăng nhập eCRF...")
    client.login('HV-WVDPV')
    
    total = len(cases_list)
    for idx, case_meta in enumerate(cases_list):
        cid = case_meta['case_id']
        if cid in audited_map and len(audited_map[cid].get('steps', {})) >= 7:
            print(f"[{idx+1}/{total}] Case {case_meta['stt']} (ID: {cid}, {case_meta['name']}): Already audited.")
            continue
            
        print(f"[{idx+1}/{total}] Auditing Case {case_meta['stt']} (ID: {cid}, Study: {case_meta['study_id']}, {case_meta['name']})...")
        res = audit_case(client, case_meta)
        audited_map[cid] = res
        print(f"       -> Missing: {len(res['missing_summary'])} bước | S5: {res.get('step5_readings_count')} mốc, S8: {res.get('step8_readings_count')}/8")
        
        # Save progress
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(list(audited_map.values()), f, ensure_ascii=False, indent=2)
            
    # Final sorted save by original order
    final_ordered = []
    for c in cases_list:
        if c['case_id'] in audited_map:
            final_ordered.append(audited_map[c['case_id']])
            
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_ordered, f, ensure_ascii=False, indent=2)
        
    print(f"\n🎉 Audit hoàn tất toàn bộ {len(final_ordered)} ca Việt Tiệp! Đã lưu file: {output_path}")

if __name__ == '__main__':
    main()
