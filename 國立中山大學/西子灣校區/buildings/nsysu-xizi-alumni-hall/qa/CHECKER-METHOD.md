# 西子樓候選幾何檢查方法

主檢查器 `independent_geometry_qa.py` 逐 byte 複用既有 Chengqin QA，
SHA-256 固定為 `0c0ca4e69386b2a5d7a531415eb4ca3ca16c599177c8ffdd8cfee37ed657b43c`。
上游方法原文保留於 [UPSTREAM-CHECKER-METHOD.md](UPSTREAM-CHECKER-METHOD.md)；
其中 Chengqin 執行紀錄不是本候選結果。本候選實測見 [QA-RESULTS.md](QA-RESULTS.md)。

從建物套件根目錄執行（新 JSON 檔名可保留既有結果）：

```text
python -B qa/independent_geometry_qa.py models/v4/model.stl --json qa/rerun-report.json --negative-controls
python -B qa/flag_diagnosis.py models/v4/model.stl qa/rerun-report.json --json qa/rerun-diagnosis.json
python -B qa/measure_print_risks.py models/v4/model.stl qa/rerun-report.json --json qa/rerun-print-risks.json
python -B qa/verify_reproducibility.py --version v4 --json qa/rerun-reproducibility.json
```

主檢查需 numpy、trimesh、Shapely；生成器另需 manifold3d。重建／場景腳本
另需 Blender `bpy`；加 `--stl-only` 可只獨立重建，無須 `bpy`。腳本不會重新
渲染預覽，也不執行切片或試印。Blender 本機 DLL 受執行環境權限限制時，
需在允許該 DLL 的 Python／Blender 環境執行。

## 固定判定

- STL 以 `process=True` 重新焊接相同座標；不補洞、不修 normals、不在 checker 做 boolean。
- 基本實體 gate 拒絕邊界邊、非流形邊／vertex link、重複／退化三角形、反向或非正體積、多個 edge-connected components。
- 自交 screen 完整列舉所有 triangle-pair AABB，對重疊 pair 做浮點 narrow phase；不是隨機抽樣。交點容差為 1e-6 mm。
- XY 切層採 0.2 mm midpoint；每個材料區域各自向內 erosion 0.4 mm，即固定 0.8 mm 特徵寬。任一核心消失／分裂即拒絕總 gate。
- 支撐包絡採與鉛直夾角 45°，每層水平 reach 0.2 mm；超出前層包絡面積 >0.01 mm² 即旗標。底部第一切層假設由床板支撐。
- 不修改以上旗標、容差或總 gate。幾何 CLI exit 1 與 false 均保留，補充診斷不改成 pass。

## 補充證據

`flag_diagnosis.py` 僅對原報告列出的 pair，以儲存於 STL 的 binary32 原座標
做 Fraction 有理數運算。它核對 input SHA、raw/processed triangle order、
float32 可表示性、pair 唯一性與非退化 guard。每對輸出原三角形、共用拓撲、
plane cut、精確 interval 或共平面 clip。這不是整張網格的形式精確證明。

`measure_print_risks.py` 直接讀 binary STL，逐面記錄非底板向下面的原座標、
精確法向量與 45° 判定，並把水平底面按共邊分組，量化標高、面積與 XY
bounding box。Bounding box 不等於已驗證的橋接跨度。切層支撐距離的邊界
取樣間隔 ≤0.1 mm，距離低估上界 0.05 mm；不模擬噴嘴路徑或橋接能力。

`verify_reproducibility.py` 於 `qa/` 的受控暫存目錄重新執行生成器，比較
完整 STL bytes；其後核對 scene 的有向三角形 multiset（binary32）、identity
transform、STL/scene/PNG 雜湊、八個 view framing，以及來源 `create_scene`
產生的材質、燈光、相機、單位與 render state。來源 `create_scene` 不渲染或存檔。
首次完整驗證的腳本與失敗報告另保留；最終腳本未調整單位比較式的 1e-12
門檻，因此 Blender binary32 單位值仍留下 strict false／exit 1。
`scene-unit-diagnosis.json` 與 `scene-unit-quantization.json` 另量化原值與 ULP，
不覆寫該旗標。

## 實際小型控制與範圍限制

[control-evidence.json](control-evidence.json) 保留 cube、薄桿、薄頸、過懸、
重疊與僅頂點接觸控制。薄桿 CLI 的預期 exit 1 證明只有薄特徵失敗也會拒絕總 gate。
[diagnosis-controls/controls.json](diagnosis-controls/controls.json) 保留 8 個
精確算例與 7 個 CLI guard／crossing 算例；
[risk-controls/controls.json](risk-controls/controls.json) 保留 5 個風險量化算例。
控制全部符合預期，不代表建物沒有列印風險。可分別執行 `run_controls.py`、
`run_diagnosis_controls.py --json NEW.json`、`run_risk_controls.py` 重跑。

浮點交點容差、切線端點取整與有限 Z 取樣會影響極小接觸／層間特徵。
Erosion 核心存活不證明每一點的最小壁厚、水平 relief 的 Z 厚度、強度或
縮放後可印性。開放露台的水平底面與保守支撐失敗須由目標切片器確認支撐、
橋接、移除空間、床板黏著與材料；未做 G-code、切片預覽或實體試印。
