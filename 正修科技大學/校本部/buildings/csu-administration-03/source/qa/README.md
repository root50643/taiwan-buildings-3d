# 原始 STL 與切片檢查工具

**文書勘誤：** 此資料夾的可執行程式是原檢查用的凍結快照。`run_slice.py` 雖接受 auto45 profile，仍呼叫歷史 `audit_gcode.py` 並在 summary 硬編 no-support limits；那兩處不能當作 auto45 的支撐狀態。本輪保留原源碼／原輸出及 SHA，正式交接讀[修正 audit](../../qa/v2/slicing/body-auto45/corrected-audit/gcode-audit.json)、[本輪勘誤與校驗](../../qa/documentation-revision-1/README.md)及[現用工具說明](../QA-TOOLING-NOTES.md)。下列原指令的完成不等於所有 profile 的支撐語義正確。

在模型資料夾執行，使用 Python 3.13、NumPy 2.5.4、Shapely 2.1.2、Trimesh 4.12.2 與 Pillow。產生模型另外需要 Manifold3D；本檢查不修補網格。

```text
python -B source/qa/run_part_qa.py --stl models/v2/parts/body.stl --expected-longest-mm 200 --out qa/fresh-body
python -B source/qa/check_manufacturing_controls.py --out qa/fresh-controls
python -B source/qa/check_intersection_controls.py --out-dir qa/fresh-exact-controls
python -B source/qa/run_slice.py --slicer PRUSA_CONSOLE_EXE --stl models/v2/parts/body.stl --out qa/fresh-slice
```

輸出路徑必須尚未存在，失敗紀錄不得覆寫。`run_part_qa.py` 會平行執行獨立檢查；某個檢查失敗仍保留其餘結果。請讀每個原始報告與旗標，不能把程式完成當作通過。

- `check_raw_mesh.py`：原始 binary STL、原始 float32 座標索引、每邊兩面、頂點鏈單環、方向、單一表面與正體積。
- `check_original_intersections.py`：所有閉 AABB 重疊三角形對，以可逆 dyadic 整數、Python 整數及 Fraction 精確檢查；允許且記錄原有共享頂點／邊，不跳過相鄰面對。
- `check_sections.py`：0.2 mm 間距、0.031／0.071／0.137 mm 三組偏移的原始水平截面。每個多邊形獨立檢查 0.8 mm 侵蝕與開運算；無修補、挪層或面積平均豁免。
- `check_manufacturing.py`：每個原始三角形十條固定重心權重法線射線、原始座標短弦與歧義旗標；另作相同三組偏移的 45 度逐層支撐包絡及底板以上朝下三角面檢查。
- `supplement_*.py`：原旗標位置的補證，保留原失敗狀態；不以替代射線取代原旗標。
- `run_slice.py`：核對已驗證的 PrusaSlicer 2.9.6 console SHA，使用獨立 data 目錄實際切片。預設 0.4 mm 噴嘴、0.2 mm 層高、100% rectilinear，關閉支撐；另附 auto45 profile。Generic G-code 僅作 QA，須依真機重切。

原始 topology、section、exact-contact 及對照程式取自本庫 `c311bc824e91dfa610164924cae51ef47ac8b3ab` 的 `吳鳳科技大學/校本部/buildings/wfu-shengyou/qa/verification/`，逐檔雜湊保留在各報告。切片 audit 取自 `國立中山大學/西子灣校區/buildings/nsysu-xizi-alumni-hall/manufacturing/v2/slicing/solid100-confirmed/audit_gcode.py`；此處使用檔名取代私人絕對路徑。另有 `source/qa_audit_gcode.py` 修正自動支撐時的說明句，原錯誤說明與補正均保留。

有限截面、有限數值射線、精確三角面對檢查，各自只支持明示範圍；不能推論任意方向的全域最小壁厚、擠出成功、強度、黏床、支撐拆除或實體試印成功。v2 嚴格製造檢查仍為 false，請讀 `qa/v2/QA-NOTES.md`。
