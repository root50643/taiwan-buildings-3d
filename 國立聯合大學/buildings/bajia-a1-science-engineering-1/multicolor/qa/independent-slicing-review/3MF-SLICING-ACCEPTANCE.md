# 聯大八甲 A1：3MF／四工具實切獨立覆核

固定候選 `c6983ff34091addf36166c7b7ce05d764a76ad8e`。本輪只在獨立審查目錄寫入成果，未改候選、推送、上傳 Library 或使用 wrapper。

**檔案／工具分區示範：條件 GO。無支撐列印路線：NO-GO。支撐比較：有限條件成立，尚非真機放行。**

## 固定輸入與範圍

| 檔案 | SHA-256 | 此輪結論 |
|---|---|---|
| a1-four-tool-PRINT.3mf | `7cf863dd73dfa74fefd9522455cc79f01fcf0e58ca348cdda406884a760ee2df` | 四部件及工具映射經實際 CLI 重開／再匯出保留；本輪切片僅用此主檔。 |
| a1-four-tool-prusaslicer.3mf | `80e665598c3d39e0e0dfb572622b6c44fda4222613b2dea8ed07645625e454de` | 八細區及指定工具經 CLI 重開保留，維持 EDITABLE 的四個同工具 PV／屋面量化界面警示；不把它當主列印檔。 |
| a1-four-tool-core.3mf | `a9929cb9259c3c18c87b2653af119035e35bbc26f93d72ba4332552b0d3dc5b6` | Core 顏色交換檔，無 Prusa 工具指定。實際重開成八個 objects，各 volume 的 extruder metadata 缺省，不能宣稱保留四工具映射。 |

三個原輸入在全部操作後 SHA 不變。模型閉合、正體積、原殼聯集和同工具界面消除的完整幾何判定由同輪獨立 `geometry-audit` 報告負責；本子報告不冒稱重算該全部幾何。

## 實際 3MF 重開

可讀取並執行 PrusaSlicer **2.9.6 console**，可執行檔 SHA `7fd50b52d1cc3da87dbcb71e45e764412dd45688bea028f351333e86d9769704`。先實讀 `--help`、`--help-fff`，保存原文後依其優先序使用明列 QA 設定。三種輸入皆實際 import/export，exit 0。

PRINT 為 `unit="millimeter"`、一個 resource object、一個 build instance，四組 inclusive triangle ranges 各覆蓋一次，沒有漏面或重複覆蓋：

| 同一物件中的部件 | 指定工具（1-based） | 面數 | 無支撐版實際正向擠出 G1 moves | 出料 Z 範圍 mm |
|---|---:|---:|---:|---|
| 01-light-wall | 1 | 14,280 | 473,126 | 3.2–54.0 |
| 02-brick | 2 | 5,600 | 31,818 | 3.2–31.0 |
| 03-slate | 3 | 9,484 | 147,843 | 0.2–57.0 |
| 04-glazing | 4 | 5,192 | 30,448 | 5.2–41.6 |

G-code 的 `T0…T3` 是上述工具 1…4 的零基索引，不是少一個噴頭。未以「四工具總擠出非零」取代具體部位核對。

EDITABLE 順序為 light_frames／glass／pv／roof／dark_facade／plinth／brick／wall，映射 **1／4／3／3／3／3／2／1**，重開後相同。Core 的九個 resources（八個網格加一個 components 父件）及單一 build instance 經 Prusa 匯入後成為八個 objects，沒有專屬工具指定。README 已分清這些用途；本輪未將 Core 顯示色當成標準化噴頭映射。CLI 再匯出的 roundtrip 不保留原始完整 profile 區塊，不能把它當跨切片器通用設定保證。

父任務已實查本環境只有 browser 控制入口：`cua.getState()` 回 `apps=[]`，原生 API disabled，`listWindows` 不存在。故 **GUI 可編輯工具 UI 未驗證**；這不等於程式未安裝，也不影響此輪實際 CLI 證據。

## 有界切片，僅兩次

以 4 個虛擬實體工具、0.4 mm nozzle、0.2 mm first/layer、名義 0.45 mm 寬、Arachne、3 perimeters、top/bottom 4、15% rectilinear、無裙邊／brim／raft／wipe tower 作診斷。四個 0x0 offsets 只是共同座標的 QA 約定，**沒有測定任何實機 offset**。溫度全為 0、`autoemit_temperature_commands=0`，start/end／filament／toolchange 等機器宏清空，machine limits ignore；逐行解析確認沒有 M104/M109/M140/M190/M141/M191、G28、M218、M500 類儲存命令或機器 limits 指令。這些診斷檔仍含 T/G1 等工具路徑，明標 **DO NOT PRINT / NOT MACHINE READY**，未送到機器。

1. **support-off：exit 0，12.08 秒。** 原始 stdout 明確報 `Floating bridge anchors, Long bridging extrusions`、`Consider enabling supports`。保留 warning，不能因 exit 0 放行無支撐製造。
2. **support-on：exit 0，14.72 秒。** 僅加一次 snug、自動 45°、everywhere、0.2 mm 上下接觸距離、0.3 mm XY 間距及 3 interface layers 比較。`support_material_extruder=0` 與 interface=0 表示使用當前模型材料，**不是第五工具、不是獨立支撐材料**。這次日誌沒有原 stability warning，但仍有橋接／懸伸料道，不據此宣告全支撐 PASS。

兩次均有 **285 個模型層 Z，最後模型出料 Z=57.0 mm**。支撐版共有 354 個不同輸出 Z，額外者是支撐層；不能稱模型變成 354 層。原殼頂點 57.0999984741 mm 與最後出料 Z 差約 **0.10 mm**，是此設定下保留的頂端層化差，未宣稱逐頂點／逐細節復原。

### 旗標的真實尺度

兩次各有 **48 個 `TYPE:Bridge infill` 註解區塊、556 個 `TYPE:Overhang perimeter` 註解區塊**。這些不是段數。逐行檢出的正向擠出 G1 moves 為：

| 工具 | Bridge infill moves | Overhang perimeter moves | support-on 新增 support／interface moves |
|---:|---:|---:|---:|
| 1 | 921 | 379 | 2,122 |
| 2 | 0 | 105 | 735 |
| 3 | 6,070 | 394 | 23,947 |
| 4 | 0 | 0 | 13,237 |

合計 6,991 bridge moves、878 overhang moves；支撐版額外 40,041 個 support/interface moves。兩路模型各工具／feature 的擠出段數及總長相同，支撐版加上支撐路徑。最長標為 Bridge infill 的單一 G1 為 Z1.8 的 114.332 mm，位於灰色底座上方填充；**這是標籤料道總移動長度，不是已證實的 114 mm 無支撐淨跨**，不能混用。原 stability warning 仍是無支撐路線的實際阻擋。

## 薄區與介面抽核

對 PRINT 的 13 個指定模型層高，依部件自身中層截面抽核實際 deposition 中點，共 **28,469 點／每次切片**；容限為該段寬一半加 0.08 mm，用於層化、斜面及 Arachne 邊緣。原輸出在 Z8.2 的中層 Z8.1 有 39 點超界，全部集中於工具 3。這個高度貼近原有門廊屋頂頂點，Trimesh 精確面截取未納入一個輪廓：該面面積 1417.8163 mm²，兩側 Z8.0999／8.1001 各恢復約 1579.43 mm²。對相同 654 點，兩側各 **0 點超界、最大距離 0**。原 39 旗標與±0.0001 mm 診斷分別保留於 `toolpath-analysis.json`／`midplane-sensitivity.json`，不刪改成全 pass，也不把截面算法敏感性誤判為模型錯色。其他指定面未有超出上述容限的點。

另直接選兩個最窄 bbox 的語意閉殼，對嚴格位於其內的層面交會實際路徑：

- **glass 小窗片**：x[-58.5,-56.95000076]、y[-68.55000305,-66.09999847]、z[8.92500019,9.75] mm，最短 bbox 0.82499981 mm。Z9.4 有工具 **4 的 8 moves**，bbox 內中心線 9.264 mm，沒找到其他工具的交會線；保留實際原始行號與座標。
- **dark_facade 灰帶**：x[10.39999962,11]、y[-66,-64.19999695]、z[3,29.60000038] mm，最短 bbox 0.60000038 mm。Z16.4 有工具 **3 的一條**長 1.2 mm、Arachne 寬 0.6 mm 的外周料道。

這證明兩個指定薄區在此 QA 設定下有對應出料，不是全部 422 個玻璃殼均完整保留、連續最小壁厚或全部界面填滿的證書。0.02 mm selector return 仍只是內部分材邊界，沒有把它宣稱成可獨立印出的薄片。沒有重切 EDITABLE 來混淆主 PRINT 結果。

## 製造門檻與最小後續

**無新增分色幾何／工具映射必修。** 固定主 PRINT 可作四工具可編輯配色示範候選；EDITABLE 與 Core 的用途限制、量化警示必須隨附。

**無支撐製造路線不放行。** 最小後續是保留本次 stability warning，在機型／材料／實際噴頭確定後重切支撐，逐區檢查庭院、門廊／塔亭、窗洞與屋簷下支撐的插入和清理路徑。此輪自動支撐確實產生，尚未做連續可達空間證明、實拆或清理；從照片看得到開口不等於所有支撐可取出。不為通過示範而任意重作原殼。

四個模型顏色已占四工具。若要獨立支撐材，四噴頭內須合併一個模型色（例如 glass 改工具 3、工具 4 給支撐），或另有硬體方案；不能暗加第五工具。各材料需確認同層界面黏結、冷卻和收縮相容，實體多噴頭還需校準註冊、間隙、刮碰／滴料／purge、實際 offset；本輪未試印、未測材料黏結。未決機型下不提供真機溫度或運動設定、不保證跨切片器保留工具指定或精準色號。

## 可復查證據

- `import-and-slice-run.json`、`alternate-import-results.json`：三種輸入與重開後實際映射／範圍、SHA、執行紀錄。
- `support-comparison-run.json`：唯一一次支撐比較及原檔 SHA。
- `toolpath-analysis.json`：全部 G-code 文字與出料 moves 解析、各工具／類型統計、13 面有界抽核及原始 39 旗標。
- `thin-feature-probes.json`：兩指定薄區的來源 bbox、工具、行號和出料座標。
- `midplane-sensitivity.json`：Z8.1 面與兩側敏感性診斷。
- `slice-support-off.stdout.txt`／`slice-support-on.stdout.txt`：原 warning／支撐生成紀錄；stderr 均空。
- `generic-four-tool-QA*-DO-NOT-PRINT.ini`、`effective-support-*.ini`、各 Python 腳本及 `prusa-help*.txt`：可重現的工具和 QA 設定。
- 兩份 `*-QA-DO-NOT-PRINT.gcode` 只作本機診斷留存，SHA 已入 JSON；不得當真機列印交付、不得因本報告而發布。
