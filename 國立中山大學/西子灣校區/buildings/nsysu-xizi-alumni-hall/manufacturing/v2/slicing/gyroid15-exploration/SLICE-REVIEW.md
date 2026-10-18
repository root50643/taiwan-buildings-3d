# 六件 v2 實際切片覆核

> 歷史候選執行紀錄的公開衍生副本：私人路徑已遮罩；當時狀態、失敗、數值及原候選hash保留。當前GO與公開檔案SHA範圍見[公開版本說明](../../../../PUBLICATION.md)。

本目錄為私有切片覆核證據；未寫入候選目錄、未推送、未連接或執行實體印表機。
六件 STL 已逐件依 `inputs-build-report.json` 的固定 SHA-256 核對，切片前後均一致。
原單件 v4 STL 與原有幾何 false / exit 1 結果沒有變更。

## 實際執行

- 官方 Windows portable PrusaSlicer **2.9.6**；下載、EXE SHA 與原始來源 URL 見 `tool-provenance.json`。
- `--help`、`--help-fff` 均 exit 0；此版本不支援 `--version`，實際 exit 1 日誌保留於相鄰 `manufacturing-tools`。版本依 `--help` banner 與 EXE metadata 確認。
- 六次 `--info`、六次 `--export-gcode`、六次 G-code 分析均 exit 0。完整 argv、輸入 SHA、耗時、stdout/stderr 見各件 `commands-and-result.json` 及日誌。
- 每件 `--info` 均回報 `manifold = yes`、`number_of_parts = 1`；面數 340 / 308 / 310 / 224 / 406 / 28 與輸入一致。CLI 沒有曝露完整修補 counter，不能據此聲稱已證明「切片器未進行任何修補」。原 STL 幾何品質應以獨立幾何檢查為準。
- stdout/stderr 未出現 warning、error、浮空或需要外部支撐的警告文字。`Searching support spots`、`Alert if supports needed`、`Calculating overhanging perimeters` 是實際進度訊息，沒有當成警告或實體列印成功證據。

固定實切設定為 `geometry-review-0.4mm-0.15mm-no-support.ini`，SHA-256
`f7293ef8e22e06890d880524ffa8fb67c9aa7bc2f3c5ede2accb63c364706e24`。
0.4 mm 噴嘴、0.15 mm 首層及均層、指定 0.45 mm 線寬、三壁、上下四實心層、15% gyroid、3 mm brim、220 × 220 × 200 mm 幾何床域；支撐、支撐自動產生、強制支撐層、raft 均關閉。
舊 0.2 mm INI 只屬準備紀錄，**不是本次實切設定**。
目前例 profile 為 PLA、噴嘴 / 首層 200°C、床 / 首層床溫 0°C、generic Marlin2；這些僅作幾何 review，正式機器須以自己的材料溫度、黏床及安全啟停 profile 重新切片，不能直接上機。

CLI 形式（每件均獨立 data directory、獨立 G-code；精確路徑已存 JSON）：

```text
prusa-slicer-console.exe --datadir <part>/cli-data --info <fixed-part.stl>
prusa-slicer-console.exe --datadir <part>/cli-data --load <0.15mm-profile.ini> --threads 2 --center 110,110 --export-gcode --output <part>/geometry-review-NOT-MACHINE-READY.gcode <fixed-part.stl>
```

## 實際 G-code 結果

表中層數只計有正向 XY 擠出的層；支撐數為實際 `TYPE` 與正擠出線解析結果。
六件首層均有正向 XY 路徑，Z = **0.15 mm**，未使用 G2/G3 圓弧。

| 件號 / 內容 | 擠出層數 | 支撐線段 | Bridge infill 線段 | 最長連續無前層路徑掃掠覆蓋的跨度 mm | STL 高度 mm | 最大擠出 Z mm |
|---|---:|---:|---:|---:|---:|---:|
| 01 底座及一樓，正印 | 89 | 0 | 2002 | 7.231843 | 13.400000 | 13.35 |
| 02 二樓樓板，倒印 | 11 | 0 | 749 | 8.467213 | 1.600000 | 1.65 |
| 03 二樓上段，正印 | 69 | 0 | 444 | 8.429512 | 10.400000 | 10.35 |
| 04 三樓樓板，倒印 | 11 | 0 | 720 | 8.358594 | 1.600000 | 1.65 |
| 05 三樓主體及玻璃角量體，正印 | 133 | 0 | 507 | 7.760989 | 20.000000 | 19.95 |
| 06 三樓斜向護欄，正印 | 21 | 0 | 0 | 0 | 3.200001 | 3.15 |

G-code 的 0.15 mm Z 量化與 STL 幾何尺寸不同：兩片 1.6 mm 樓板的擠出層頂為 1.65 mm，其他件約少 0.05 mm。
02 / 04 / 06 的最大移動 Z 為 5 mm，是預設開始碼抬頭；不能當作成品高度。其他件最大移動 Z 與最大擠出 Z 相同。
組裝的實際高度、膠縫與配合會受此量化、首層壓實及機器校準影響。

| 件號 | 實際正擠出 XY 範圍，含 brim，mm |
|---|---|
| 01 | [32.284, 56.554] → [187.716, 163.446] |
| 02 | [35.675, 60.233] → [183.856, 159.751] |
| 03 | [35.785, 61.828] → [183.745, 158.249] |
| 04 | [35.723, 68.526] → [183.686, 151.476] |
| 05 | [47.278, 68.561] → [172.133, 151.503] |
| 06 | [91.222, 86.439] → [128.208, 134.306] |

六件均在本次 220 mm 方形分析床域內。首層路徑已逐圖實際查看，六圖合集為
`six-parts-first-layer-contact-sheet.png`；各件原始 1400 px 圖及逐層 TYPE 統計在各件目錄。
圖片顯示實際 G-code 中心線，不能證明床黏著、噴頭補償或成形品質。

## Bridge infill 的原座標定位與跨度

`classify_bridge_paths.py` 對每條實際 Bridge infill 線，減去**前一層全部正向 XY 擠出路徑**的半徑 0.225 mm 掃掠聯集，再量每一段連續差集長度。
沒有把一整條橫跨多條 infill 的線長當成跨度；第一層視為有床面支持。
固定 0.45 mm 掃掠寬為本次明示的幾何假設，不是觀測到的實體塑料寬度。
圓形 buffer 使用每象限 16 段，最大半徑多邊形近似差約 0.000271 mm；本數值不含真機擠出偏差。

另外在前層及當層中面取 STL 實心輪廓，並以保存的 print-to-assembled transform 反投影至固定原單件 v4，檢查橋接中心線是否位於原實心量體上方。
02–06 的前層原 STL 名義輪廓外中心線總長均為 0。
01 大部分橋接亦位於名義內部；但 **Z 12.3 mm 有五條局部短線，各約 0.2250002 mm 位於前層名義輪廓外**，合計 **1.125001035 mm**，當層輪廓外合計 **0.375000984 mm**。
位置為原列印座標 X 約 -16.753 至 -14.948、Y 約 -1.922 至 0.861 mm；該層最長無前層路徑覆蓋的連續跨度為 0.451111 mm。
這些非零量保留，沒有寫成全部橋接皆在輪廓內或改動任何原幾何 gate。

整體最大約 **8.47 mm** 的連續跨度在 02 的內填充上方；原有大露台底板未以原單件方向跨空列印。
逐線 G-code 行號、原 XY、差集長度、最大跨度兩端、取樣 Z、與原 v4 的關係均存各件 `bridge-location-diagnosis.json`，摘要為 `bridge-location-summary.json`。
這是規劃路徑的幾何分析，不是橋接試印、下垂測試或噴嘴動力學模擬。

## 失敗與限制保留

- `classify_bridge_paths-attempt01.py` 以原三角平面線段直接 polygonize，在 Z 2.325 mm 未接合成閉輪廓而 **exit 1**。原腳本、重現日誌及失敗 JSON 已保留。修正為依 mesh topology 的 `trimesh.section` 接合閉輪廓；未修補 STL、未調整原 QA 門檻。
- `audit-parser-self-check.json` 為明示的合成 parser fixture：有支撐時能檢出兩條支撐、同時將 Bridge infill 分開；它不是切片或列印實驗。
- 支撐全關且 G-code 支撐為零，本身不能證明模型不需要支撐；本方案需併看六件獨立幾何結果及上述外輪廓/連續跨度證據。
- 此六件方案沒有需要從 7.2 mm 通道抽出的支撐塊。一般單噴頭 FDM 仍需能在所選材料及設定下處理約 **8.47 mm 內填充橋接**、0.45 mm 規劃線寬、薄護欄及 0.15 mm 層高，並由操作者確認黏床與裝配。
- 本設定的 marlin2 僅是通用幾何分析輸出。G-code **不是可直接送往任意真機的成品**；使用者需以目標機器的實際安全起止碼、溫度、速度與行程設定重新切片。
- 未進行實體列印、切除支撐、膠合或裝配測試；不得據此宣稱已試印成功。

工具 ZIP、解壓程式與 data directories 位於相鄰 `manufacturing-tools`，不屬模型與 Library 備份內容。
