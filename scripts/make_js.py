import json

with open("dong_van_dy_ecrf_data.json", "r", encoding="utf-8") as f:
    d = json.load(f)

readings = d["vital_signs_readings"]

js_header = """/**
 * Script Auto-fill Dữ liệu Biến thiên Huyết áp quanh Can thiệp (Bước 5)
 * Bệnh nhân: ĐỒNG VĂN DY (Mã nghiên cứu: VT-2600543043)
 * T0 = 13:56 (Chọc mạch) -> Tend = 15:17 (Kết thúc EVT)
 * Phương pháp: Nội suy tuyến tính (Linear interpolation) cho các mốc khuyết
 */

(function autoFillStep5() {
    const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;

    const data = """

js_footer = """;

    function setVal(input, val) {
        if (!input) return;
        nativeSetter.call(input, val);
        input.dispatchEvent(new Event("input", { bubbles: true }));
        input.dispatchEvent(new Event("change", { bubbles: true }));
    }

    console.log(`[Auto-fill] Bắt đầu điền ${data.length} mốc huyết áp cho ĐỒNG VĂN DY...`);

    data.forEach((row, idx) => {
        const minInp = document.querySelector(`input[name="readings[${idx}][minute]"]`);
        const sbpInp = document.querySelector(`input[name="readings[${idx}][sbp]"]`);
        const dbpInp = document.querySelector(`input[name="readings[${idx}][dbp]"]`);
        const mapInp = document.querySelector(`input[name="readings[${idx}][map]"]`);
        const hrInp  = document.querySelector(`input[name="readings[${idx}][hr]"]`);
        const srcSel = document.querySelector(`select[name="readings[${idx}][source]"]`);

        if (minInp) setVal(minInp, row.minute);
        if (sbpInp) setVal(sbpInp, row.sbp);
        if (dbpInp) setVal(dbpInp, row.dbp);
        if (mapInp && !mapInp.readOnly && !mapInp.disabled) setVal(mapInp, row.map);
        if (hrInp)  setVal(hrInp, row.hr);
        if (srcSel) {
            srcSel.value = row.source;
            srcSel.dispatchEvent(new Event("change", { bubbles: true }));
        }

        if (row.imputed) {
            console.warn(`[Imputed] Mốc ${row.minute}p (${row.time}): SBP=${row.sbp}, DBP=${row.dbp}, MAP=${row.map}, HR=${row.hr} (Nội suy)`);
        } else {
            console.log(`[Measured] Mốc ${row.minute}p (${row.time}): SBP=${row.sbp}, DBP=${row.dbp}, MAP=${row.map}, HR=${row.hr}`);
        }
    });

    console.log("[Auto-fill] Hoàn tất điền dữ liệu Bước 5 cho ĐỒNG VĂN DY!");
})();
"""

with open("fill_step5_dong_van_dy.js", "w", encoding="utf-8") as f:
    f.write(js_header + json.dumps(readings, indent=2, ensure_ascii=False) + js_footer)

print("Generated fill_step5_dong_van_dy.js cleanly!")
