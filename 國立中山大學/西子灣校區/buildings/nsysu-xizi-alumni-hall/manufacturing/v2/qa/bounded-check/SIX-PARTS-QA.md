# 六件製造版 v2：逐件原門檻 QA

> 歷史候選執行紀錄的公開衍生副本：私人路徑已遮罩；當時狀態、失敗、數值及原候選hash保留。當前GO與公開檔案SHA範圍見[公開版本說明](../../../../PUBLICATION.md)。

本次只讀取已固定的六件列印姿態 STL，輸入 SHA 均與委派及正式 build report
一致。所有新證據只寫入 `manufacturing-qa-staging/`，未改 candidate、原 v4、
分件生成器或 STL；未重新跑原 v4 或既有 synthetic controls。

**六件基本實體、固定薄核心及固定 45° 切層支撐 screen 全部通過；
原總 gate 仍是五件 exit 1、一件 exit 0。** 原因為前五件共 93 個浮點 pair
旗標，已逐對以原 binary32 座標精確診斷，沒有越界交集。這不是切片或試印。

## 實跑結果

| 件號與列印姿態 | 三角面 | 正體積 mm³ | 切層 | 薄失敗層 | 支撐失敗層 | 原 pair 旗標 | 原 exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 01 底座／一樓，正印 | 340 | 95919.73920719919 | 67 | 0 | 0 | 6 | 1 |
| 02 二樓板，倒印 | 308 | 12998.255278599607 | 8 | 0 | 0 | 10 | 1 |
| 03 二樓上部，正印 | 310 | 53631.66208944377 | 52 | 0 | 0 | 8 | 1 |
| 04 三樓板，倒印 | 224 | 11688.29156629964 | 8 | 0 | 0 | 10 | 1 |
| 05 三樓主體／高量體，正印 | 406 | 51612.343820592425 | 100 | 0 | 0 | 59 | 1 |
| 06 三樓斜向欄牆，正印 | 28 | 285.2918926378422 | 16 | 0 | 0 | 0 | 0 |

每件均 watertight、winding consistent、1 個 edge-connected component、正體積；
邊界邊、非流形邊／vertex-link、退化／重複三角形均 0。每件 print Z 最低
均為 0，各切層均非空且閉合。STL `process=True` 只焊接相同座標，不補洞、
不改 normals、不作修復 boolean。

## 93 個原 pair 旗標

| 件號 | 精確分離 | 僅合法共邊 | 僅合法共點 | 越界交集 | 診斷 exit |
| --- | ---: | ---: | ---: | ---: | ---: |
| 01 | 0 | 2 | 4 | 0 | 0 |
| 02 | 0 | 4 | 6 | 0 | 0 |
| 03 | 0 | 2 | 6 | 0 | 0 |
| 04 | 2 | 3 | 5 | 0 | 0 |
| 05 | 7 | 13 | 39 | 0 | 0 |
| 06 | — | — | — | — | 不需診斷，原旗標 0 |
| 合計 | 9 | 24 | 60 | 0 | |

前五件均核對 SHA、raw/processed triangle order、float32 可表示性、pair 唯一性
與退化 guard；93/93 覆蓋一次。原 `qa-report.json`、stdout/stderr、退出碼及
false 全部保留，精確補充不把原總 gate 改成 pass。原 checker 對全部 triangle
pair 列舉 AABB 後檢查所有重疊者；補充 Fraction 只診斷原旗標，並非本次另做
全 pair 精確證明。各件目錄有完整報告與 `flag-summary.json`。

## 固定支撐 screen 與保留的微量化

未變門檻：0.2 mm midpoint、與鉛直夾角 45°（每層水平 reach 0.2 mm）、
0.8 mm 特徵寬／0.4 mm 各材料區域 erosion、支撐超出面積 >0.01 mm² 才旗標。
所有六件的此支撐失敗層均為 0；本次原座標向下面量化也未找到非底板水平
underface。這解決的是各件指定姿態下的大面積外懸 screen，不能等同物理成功。

另外保留數學 45° 的逐面診斷：03 有 8 面、05 有 16 面微超 45°，最高為
45.00010616264547°，並未刪旗標或改寫成全部面數學 ≤45°。03／05 最大切層
包絡外面積分別為 4.976452885330216e-6、6.402475372313532e-6 mm²，低於
原 0.01 mm² gate；其他四件最大值為 0。

`bevel-departure-bounds.json` 從原 STL binary32 重新算 Fraction 法向量，
以整數平方根構造精確有理數區間包住斜面整個 Z 跨度的 plane slope run 超量：
03 上界 8.344650268555798e-7 mm；05 上界 2.0381774259640713e-6 mm。
軸對齊面原超量分別為 7/8388608 mm 或 1/1048576 mm。斜向 tower 面也有
逐面原座標、精確 normal 與區間端點。此量化支持將微小面角偏差視為量化，
不把大面積支撐失敗隱藏在容差內，亦不覆寫任何原結果。

## 方法、身分與重跑

主檢查器逐 byte 未變，SHA-256：
`0c0ca4e69386b2a5d7a531415eb4ca3ca16c599177c8ffdd8cfee37ed657b43c`。
精確診斷器亦未變：
`c8e9771b1c9dba285ae796e29d806b9f49fd681e06c098965e3cbccd3141b42c`。
版本與固定輸入在 [fixed-inputs.json](fixed-inputs.json) 及各實跑報告；
機器可讀總結為 [SIX-PARTS-QA.json](SIX-PARTS-QA.json)。

於工作根目錄、已安裝原 requirements 的 Python 環境：

```text
python -B manufacturing-qa-staging/run_six_parts_qa.py --models-dir candidate/國立中山大學/西子灣校區/buildings/nsysu-xizi-alumni-hall/manufacturing/v2/models --out manufacturing-qa-staging/NEW-RESULTS
python -B manufacturing-qa-staging/quantify_bevel_departures.py --results manufacturing-qa-staging/NEW-RESULTS --json manufacturing-qa-staging/NEW-RESULTS/bevel-departure-bounds.json
```

協調腳本固定六個 SHA、檢查器 SHA 與結果根目錄，拒絕覆寫現有 attempt；
原始 CLI 未使用調整門檻的參數，也未重新跑已有控制。總協調退出碼仍為 1，
以保留五件原 bounded gate 失敗。`inputs/` 只是這次 staging 的固定副本，
正式模型已有相同六 STL 時不必再重複打包。

## 尚未證明的製程

本次只負責六件受影響幾何的數位 QA；未切片、產生／檢查 G-code、實印、
測橋接、黏床、翹曲、支撐移除或裝配黏合強度。倒印板的表面品質、1.6 mm
薄板翹曲、1.2 mm 欄牆／細柱的操作脆弱性、拼縫定位、膠層／間隙及目標
機台層高／噴嘴仍需相應製程證據。有限切層與 erosion 核心存活不證明每點
最小壁厚或連續高度；第一切層依原 checker 假設由床板支撐。
