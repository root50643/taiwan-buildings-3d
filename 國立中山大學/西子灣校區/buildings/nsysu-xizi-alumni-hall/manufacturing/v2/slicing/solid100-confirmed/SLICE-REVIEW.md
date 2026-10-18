# 六件 v2：100% rectilinear 保守列印方案的實際切片證據

> 歷史候選執行紀錄的公開衍生副本：私人路徑已遮罩；當時狀態、失敗、數值及原候選hash保留。當前GO與公開檔案SHA範圍見[公開版本說明](../../../../PUBLICATION.md)。

建議製造條件為：**使用固定六件 STL 的既定列印方向、0.4 mm 噴嘴、0.15 mm 首層及均層、0.45 mm 指定線寬、100% rectilinear infill，支撐及 raft 全關閉**。
兩片樓板已在 STL 中倒印，無需再次翻面；各件分開列印，再依原 transform 組裝。
此方案把原大露台底板拆為床面上的薄片，沒有需要從約 7.2 mm 通道抽出的支撐塊，也不以長達約 8.47 mm 的內填充橋接能力為前提。
這是已實際切片並量化路徑的候選方案，**不是實體試印或任意真機可直接執行的 G-code**。

原單件 v4 STL、六件 STL、原 QA 的 false / exit 1 結果均未改動。六件輸入 SHA 在切片前後逐一比對固定 `inputs-build-report.json` 一致。
相鄰 `slicer-review-staging` 的 15% gyroid 實切完整保留為探索方案，沒有改寫為失敗。

## 工具、設定與實際執行

- 官方 portable PrusaSlicer **2.9.6**。`tool-provenance.json` 有來源、版本 banner、下載 ZIP 大小 / SHA、EXE SHA。未系統安裝、改 PATH、啟 UI 或連接印表機。
- 明確設定：`geometry-review-0.4mm-0.15mm-solid-rectilinear-no-support.ini`。
  SHA-256 `7c300f9ea4a193facecf8c88c8aee94da19630b79f5d1cfb56da204fb4966442`。
- 與 15% 設定的序列化鍵值差異**只有** `fill_density: 15% → 100%`、`fill_pattern: gyroid → rectilinear`，見 `profile-diff.json`。
- 其他條件維持三壁、上下各四實心層、3 mm brim、220 × 220 × 200 mm 幾何床域、ASCII G-code。支撐、支撐自動生成、強制支撐層、raft 均關閉。
- 目前例 profile 的材料標記為 PLA、噴嘴 / 首層溫度 200°C、床 / 首層床溫 0°C、generic Marlin2。這些只是幾何 review 用的示例值，不是為此模型推薦的真機材料、熱床或黏著條件；正式機器必須以自己的溫度、黏床及啟停 profile 重新切片。
- 六次 `--info`、六次 `--export-gcode`、六次 G-code audit 全 **exit 0**；橋接定位與前層掃掠差集診斷亦 **exit 0**。精確 argv、各件固定 SHA、stdout / stderr 與 return code 均保存在各件目錄及 `slicer-run-summary.json`。
- 六件 `--info` 均回報 `manifold=yes`、`number_of_parts=1`，面數 340 / 308 / 310 / 224 / 406 / 28 與固定輸入一致。CLI 沒有曝露完整修補 counter，沒有據此宣稱切片器完全未修補；網格品質仍以獨立幾何檢查為準。
- CLI stdout / stderr 未出現 warning、error、浮空或需外部支撐的警告文字。`Searching support spots`、`Alert if supports needed`、`Calculating overhanging perimeters` 是實際程序進度，不能當成實體成形證據。

```text
prusa-slicer-console.exe --datadir <part>/cli-data --info <fixed-part.stl>
prusa-slicer-console.exe --datadir <part>/cli-data --load <solid-profile.ini> --threads 2 --center 110,110 --export-gcode --output <part>/geometry-review-NOT-MACHINE-READY.gcode <fixed-part.stl>
```

## 路徑、支撐及剩餘短橋接

六件首層皆有正向 XY 擠出，Z 均 **0.15 mm**；六件所有支撐 TYPE 與支撐正擠出線數皆 **0**。
首層圖 `six-parts-first-layer-contact-sheet.png` 及六張獨立 1400 px 圖，均來自本次實際 G-code。
圖片是路徑中心線證據，不能證明黏床或首層壓實品質。

| 件號 | 正擠出層數 | Bridge infill 線段 | 最長連續無前層路徑掃掠覆蓋段 mm | STL 高度 mm | 最大擠出 Z mm | 最大移動 Z mm |
|---|---:|---:|---:|---:|---:|---:|
| 01 底座及一樓，正印 | 89 | **19** | **0.225000058** | 13.400000 | 13.35 | 13.35 |
| 02 二樓樓板，倒印 | 11 | 0 | 0 | 1.600000 | 1.65 | 5.00 |
| 03 二樓上段，正印 | 69 | 0 | 0 | 10.400000 | 10.35 | 10.35 |
| 04 三樓樓板，倒印 | 11 | 0 | 0 | 1.600000 | 1.65 | 5.00 |
| 05 三樓主體及玻璃角量體，正印 | 133 | 0 | 0 | 20.000000 | 19.95 | 19.95 |
| 06 三樓斜向護欄，正印 | 21 | 0 | 0 | 3.200001 | 3.15 | 5.00 |

**沒有把全部橋接寫為零。** 01 的 19 條 Bridge infill 在 Z = 12.3 mm。
診斷減去前一層實際正向 XY 擠出線的半徑 0.225 mm 聯集後，逐條量每段連續差集，最大為 0.225000058 mm；沒有將整條線長當成跨度。
該值約為本次指定 0.45 mm 線寬的一半，與原 15% 方案約 8.47 mm 的內填充跨度有明確量測差別。
此掃掠寬是規劃線寬的幾何假設，並非觀測到的塑料寬度；圓形 buffer 每象限 16 段，最大半徑近似差約 0.000271 mm。

另用 print-to-assembled transform 核對固定原 v4 STL 的前層實心輪廓。
01 有五條局部短中心線各約 0.2250002 mm 位於前層名義輪廓外，合計 **1.125001035 mm**；當層輪廓外合計 **0.375000984 mm**。
位置 X 約 -16.753 至 -14.948、Y 約 -1.922 至 0.861 mm，原座標、G-code 行號、每段差集及最大段兩端均保留。
這些非零量沒有當成數值誤差歸零，也沒有改動任何原 QA 旗標或門檻。
02–06 沒有 Bridge infill 線；完整定位見各件 `bridge-location-diagnosis.json` 與總表 `bridge-location-summary.json`。

| 件號 | 實際正擠出 XY 範圍，含 3 mm brim，mm |
|---|---|
| 01 | [32.284, 56.554] → [187.716, 163.446] |
| 02 | [35.675, 60.233] → [183.856, 159.751] |
| 03 | [35.785, 61.828] → [183.745, 158.249] |
| 04 | [35.723, 68.526] → [183.686, 151.476] |
| 05 | [47.278, 68.561] → [172.133, 151.503] |
| 06 | [91.222, 86.439] → [128.208, 134.306] |

全部在本次 220 mm 方形床域內。兩片 1.6 mm STL 的層頂為 1.65 mm；其他件約少 0.05 mm，這是 0.15 mm 層高的離散化結果，不能把 G-code 高度與 STL 高度混為一談。
薄片與護欄的移動 Z=5 mm 是開始碼抬頭，不是成品高度。實際膠縫、首層壓實及組裝尺寸仍需操作者確認。

## 耗材與時間的切片器估計

| 件號 | 1.75 mm 料長 m | 體積 cm³ | normal 模式估時 |
|---|---:|---:|---|
| 01 | 39.99097 | 96.19 | 9h 06m 58s |
| 02 | 5.68450 | 13.67 | 2h 22m 07s |
| 03 | 22.35906 | 53.78 | 4h 32m 58s |
| 04 | 5.11733 | 12.31 | 2h 08m 06s |
| 05 | 21.67347 | 52.13 | 4h 30m 38s |
| 06 | 0.14253 | 0.34 | 0h 03m 19s |
| **合計** | **94.96786** | **228.42** | **22h 44m 06s** |

相同固定六件的 15% 探索方案估計 40.35066 m / 97.06 cm³ / 14h 26m 50s。
100% 方案約為其 **2.35 倍耗材、1.57 倍估時**；比較的原始 footer 與加總在 `exploratory-vs-solid-estimates.json`。
這是本次通用分析設定的切片器估計，並非實測機器耗材或工時。
profile 未設定材料密度，G-code 中 `g=0` 代表沒有可用重量估計，不能當成實重。

## 設備條件、失敗紀錄及限制

- 可採一般單噴頭 FDM，不需可溶性支撐設備；須使用上述六件方向、100% rectilinear、支撐關閉，並具備可校準的 0.4 mm 噴嘴 / 0.15 mm 層高能力及適當黏床。
- 通用分析床域為 220 × 220 mm；真機需另核可用床域、排除區、噴頭行程及 brim。100% 填充增加材料與熱累積，材料溫度、流量、速度與冷卻仍需依真機校準。
- G-code 檔名皆含 **NOT-MACHINE-READY**。marlin2、起止碼、溫度及速度是分析設定，未驗證為任意特定真機可安全執行。使用者應在目標切片器選用自己的已校準機器 / 材料設定，保持上述製造條件重新切片。
- 本次準備腳本曾以 Windows 預設 cp950 讀 UTF-8 原始碼而 exit 1，尚未啟動 solid 切片；原因及 explicit UTF-8 修正見 `preparation-attempt01-failure.json`。未改模型或舊探索結果。
- 原探索橋接診斷的線段接合失敗與修正保留在相鄰目錄；本次使用依拓樸接合的已修正程式，未修補 STL 或放寬幾何門檻。
- 沒有實體試印、支撐移除、膠合、裝配、材料翹曲或下垂試驗。此數位證據支持分件製造路徑，不能寫成實體列印成功。

官方工具 ZIP 與解壓程式位於相鄰 `manufacturing-tools`，不應放入候選模型或 Library 備份。
本目錄保存的完整 CLI JSON 是當時真實絕對路徑；搬移證據後可用相同固定 STL 與 INI，重新指定本機的程式、data directory 及輸出路徑重切，不應假設原機器路徑仍存在。
