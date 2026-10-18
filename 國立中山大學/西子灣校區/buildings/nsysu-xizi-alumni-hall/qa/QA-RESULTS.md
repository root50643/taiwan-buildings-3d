# 西子樓候選 v4 實測 QA

> 歷史候選執行紀錄的公開衍生副本：私人路徑已遮罩；當時狀態、失敗、數值及原候選hash保留。當前GO與公開檔案SHA範圍見[公開版本說明](../PUBLICATION.md)。

本候選可供獨立覆核；**不能宣稱嚴格總 gate 全部通過或免支撐可印**。
原幾何 CLI 為 **exit 1 / `passes_bounded_geometry_screen=false`**；
最終重建／場景整合 CLI 也保留 **exit 1 / `pass=false`**，原因與量化如下。
未執行切片、G-code 或實體試印。

固定輸入為 [models/v4/model.stl](../models/v4/model.stl)，SHA-256
`05c1714f8b363075a2eb72cde39d21ef06eb0720f1b46336579eb48edbb1444f`。
外框 150 × 101.46141815185547 × 47 mm，底面 z=0，+Z 向上，3 mm 底板。
這是獨立展示尺度，並非測繪比例或真實建築公尺尺寸。

| 實測項目 | 結果與證據 |
| --- | --- |
| 基本封閉實體 | 637 vertices、1,302 triangles；watertight、winding consistent、1 個 edge-connected component；正體積 226,135.58374502356 mm³。邊界邊、非流形邊／vertex link、退化／重複三角形均 0。 |
| 原浮點自交 screen | 列舉全部 846,951 對，13,689 對 AABB 重疊進入 narrow phase；留下 **146 旗標**，原 false／exit 1 保留。 |
| 原座標精確補充診斷 | 146/146 逐對核對 STL binary32 座標：**23 分離、31 僅合法共邊、92 僅合法共點，0 真正越界交集**。診斷 exit 0，但不覆寫原自交 false 或總 gate。 |
| XY 切層 | 0.2 mm midpoint 共 235 層，均非空且閉合；每個實際材料區域分別檢查。 |
| 固定薄特徵 screen | 0.8 mm 寬（0.4 mm erosion），**0 層核心消失或分裂，pass**。此判定不等於每點最小壁厚證明。 |
| 固定支撐 screen | 45°、0.2 mm reach、0.01 mm² 面積容差；**4 層失敗，false 保留**，如下表。這是真實露台／上層外懸的幾何風險，不能歸因為微小數值誤差。 |
| 獨立重建 | 重新執行最終生成器，完整 STL bytes 與原檔相同；source/parameters 原始 SHA 與 build report 一致。 |
| Blender 與預覽綁定 | scene 的有向 triangle multiset 轉 binary32 後與 STL 相同，print transform 為 identity；scene/STL/八 PNG 雜湊全部相符；來源 `create_scene` 狀態與 saved scene 相同；無第三方 image datablock。 |
| 最終八面 framing | 八面均完整包含 print mesh。首次 terraces 超框的真實失敗已保留，後僅該張 ortho scale 185→195 重渲染，其他七圖與原 scene/STL bytes 未變。 |
| 嚴格單位數值比較 | `METRIC` / `MILLIMETERS`；`abs(scale_length-0.001)<1e-12` **仍 false**，完整驗證 exit 1 保留。原值與 binary32/ULP 診斷如下。 |

## 四個支撐風險層

| z mm | 超出前層 45° 包絡面積 mm² | 取樣上邊界到前層最大距離 mm |
| --- | ---: | ---: |
| 13.5 | 3168.106371946914 | 23.962841304070253 |
| 14.9 | 795.7474874045755 | 8.924462722176967 |
| 25.5 | 2179.2573156515246 | 34.62345540523529 |
| 26.9 | 145.59794701539903 | 1.2102160851335484 |

距離以 ≤0.1 mm 間隔沿邊界取樣，低估上界 0.05 mm；這不是可橋接跨度、
噴嘴路徑或印表機能力驗證。[print-risk-measurement.json](print-risk-measurement.json)
保留原 STL 每個非底板向下三角面的座標、精確法向量、45° 判定，以及共邊
水平底面 patch 的標高、面積與 bounding box。開放露台須保留；使用者需要
在目標切片器規劃支撐、橋接與支撐移除空間，不能把大面積過懸失敗說成通過。

## 146 個自交旗標的原座標診斷

[flag-diagnosis.json](flag-diagnosis.json) 保留每對三角形原座標、原旗標、
shared topology、Fraction plane cuts／interval／clip 與分類；輸入 SHA、
raw/processed triangle order、float32 可表示性與非退化 guard 皆符合。
[flag-summary.json](flag-summary.json) 保留量化摘要：146 個原旗標均為
`noncoplanar_contact_or_crossing`；81 對的六個 normalized vertex-to-plane
殘差均 ≤1e-6 mm。其餘不能概括成全部只是近共平面；逐對精確算術才是
判斷合法接觸的依據。沒有改旗標、門檻、STL 座標或原報告。

精確補充僅涵蓋原 146 對；其他對仍是完整 AABB 浮點 screen。這不是
全網格精確算術形式證明，也不是列印通過證據。

## 原單位 strict false 的量化

Saved scene 原值為 `0.0010000000474974513`，精確值
`8589935/8589934592`，binary32 bits `0x3a83126f`；它恰等於來源
`0.001` 轉為 binary32，**與預期 binary32 相差 0 ULP**。該處 ULP 是
`1/8589934592`（約 1.1641532182693481e-10）。

與數學 1/1000 的差為 `51/1073741824000`，即 `51/125 = 0.408 ULP`；
與 Python binary64 literal 的差為 `54760833/1152921504606846976`
（約 4.749745128457272e-11），所以原 1e-12 比較確實失敗。
[scene-unit-diagnosis.json](scene-unit-diagnosis.json) 直接讀原 saved scene；
[scene-unit-quantization.json](scene-unit-quantization.json) 以 Fraction 量化。
據此可把單位表示法旗標作非阻擋判讀，**但 strict false／exit 1 原樣保留**。
沒有改 scene 單位或 bytes，沒有放寬比較式。

## 真正失敗與修正紀錄

- `attempt-01/` 保留原生成器、參數、STL、build report 與本次實際 generic QA／診斷：五個負體積內腔及退化面導致失敗；診斷 guard 拒絕退化輸入，未把旗標解讀成通過。
- `attempt-02/` 保留原生成器、參數、STL 與當時 build report；修掉被合併房間遮住的低樓層 tower 凹窗後，float32 cap 仍退化。這版未另跑本次 generic QA，不能宣稱跑過。
- `attempt-03/` 保留 v3 source/parameters/STL/build report 與實際 generic QA。v3 封閉單殼，但 z15.1–18.1 的 16 層出現 1 材料區→2 erosion cores；`thin-neck-localization.json` 以原 STL Fraction 切線定位二樓斜向 rail `[1482,550]→[1434,604]` 的末端窄楔。
- v4 在該末端加入 2.4 mm square joint，充分接入 room 外牆，維持露台開放；固定 0.8 mm 薄核心失敗由 16 層降為 0。生成器頂部 bevel 延伸到牆面外並只切外露 tower 上部，消除實際退化／封閉內腔；未在 QA 修網格。
- `reproducibility-attempt-01.*` 與失敗腳本保留首次 units false 與 terraces 左框超出約 4.46 px 的結果。最後只修 terraces 一張；原 units 斷言與失敗旗標保留。最終 [reproducibility.json](reproducibility.json) 再次實際重建並驗證所有 scene/preview 綁定。

## 工具、控制與剩餘限制

原 geometry checker SHA-256 仍為
`0c0ca4e69386b2a5d7a531415eb4ca3ca16c599177c8ffdd8cfee37ed657b43c`。
[byte-provenance.json](byte-provenance.json) 證明其未變，最終 reproducibility
腳本也與首輪失敗腳本逐 byte 相同；保留 LF／CRLF，避免 Git text normalization
破壞 SHA 綁定。方法與重跑命令見 [CHECKER-METHOD.md](CHECKER-METHOD.md)。
主控制、精確診斷的 8 算例與 7 CLI guards、風險工具的 5 算例均符合預期；
其中薄桿／過懸的預期失敗有保留原 exit 1。

名義設計為 rail/parapet 1.2 mm、柱 1.8 mm、slab Z 1.6 mm、端塊 2.4 mm、
凹窗 relief 0.55 mm；這些是加厚的模型參數，非建築測繪壁厚。切層核心測試
可能漏過附著尖端、細 Z 特徵或每點局部薄處。150 mm 底板仍須預留 brim／
bed exclusions；支撐、層高、噴嘴、縮放、黏床、翹曲、材料與支撐移除需要
目標切片器／實體確認。來源幾何忠實度與建築身分另依來源說明及獨立覆核，
本數位 QA 不證明已驗證的 2026 現況或精密比例。
