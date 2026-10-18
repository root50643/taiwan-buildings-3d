> 本文保留 e45f8d6 原候選的結果。R2 最新修訂及風險請讀 [RISK-FOLLOWUP.md](risk-followup-e45f8d6/RISK-FOLLOWUP.md)；文中舊 layer-check 對應 `risk-followup-e45f8d6/input-layer-check.json`，根目錄檔案已更新為 R2。

# 旺宏館候選：原始 STL 擴充幾何篩查

2026-10-18。這是固定候選的篩查證據，供獨立覆核；沒有執行正式切片、G-code 檢查或試印。

- 原件 `main 08604e70212673240173660584236e361221533f` STL SHA-256：`801b9d6dedd0b8242dfea97938207b435c48f741a5d76195dcd7157881e29fa0`。
- 本候選 STL SHA-256：`9c90c8b6b6f99076f2096783e78b793404fb81df88ee270d2eb02f21290e24b8`。

實際前後布林體積與七層截面差量另見 [`geometry-delta.md`](geometry-delta.md) 及 [`geometry-delta.json`](geometry-delta.json)。其中廣入口 crop 包含已改的橢圓邊緣，確有差量；只有明確限定的核心入口與樓梯 crop 無差量。後棟布林對稱差約 `0.000009 mm³`，原先嚴格門檻的 false 結果保留，不泛稱全區座標完全相同。

## 原始失敗與另立補證

[`extended-checks-initial.json`](extended-checks-initial.json) 的 `hard_geometry_checks_passed=false` 原樣保留：浮點自交篩查留下 37 筆疑點。原件的 [`original-extended-checks.json`](original-extended-checks.json) 同樣保留 34 筆疑點及 false 結果；沒有把它們改成 passed。

另立的 [`exact-intersections.json`](exact-intersections.json) 使用實際儲存的 STL float32 座標，無變值地轉成共用 2 次方比例整數；平面符號判定用 Python 整數，交點與共面裁切用 `fractions.Fraction`。候選的 **45,366 組** AABB 交疊三角形全部檢查，包含相鄰面，只有落在實際共享頂點或邊內的接觸獲准：**0 筆非法接觸／自交**。初報 37 筆皆未獲精確判定確認，為浮點近共面容差造成的疑點。

原件另立 [`original-exact-intersections.json`](original-exact-intersections.json)，38,409 組、0 筆非法接觸，原初報 34 筆亦均未獲確認。兩種判定各有 12 組控制案例：非相鄰交叉、共面重疊、重複面、不相鄰點接觸、共享頂點卻另有穿交、共享邊卻重疊，以及分離／正常共享邊／正常共享頂點等，皆符合預期。

精確補證針對儲存三角形的接觸性質，仍受程式實作正確性限制；控制案例不是形式化驗證，也不證明建築準確度或可列印性。

## 原始 STL 拓樸

`extended_checks.py` 直接解析 binary STL，僅依完全相同座標建立拓樸，沒有修補或容差焊接。候選為 3,874 面、1,921 頂點、單一面連通殼，體積 `406815.46177862445 mm³`；每邊兩面、頂點鄰接單環、相鄰邊方向、正體積、原始法線與三角形非退化皆通過。這些結果不會抵銷以下薄特徵或支撐警示。原件同方法拓樸亦通過。

## 薄特徵及支撐警示保留

| 同方法篩查 | 原件 | 候選 |
|---|---:|---:|
| 各三角形中心法線向內射線樣本 | 3,270 | 3,874 |
| 法線弦長小於 0.8 mm 樣本 | 204 | 198 |
| 最短樣本弦長 mm | 0.0206947 | **0.00624769** |
| 警示面積 mm² | 626.599 | 535.772 |
| 朝下且法線距 -Z 小於 45° 的面數（扣除底面） | 375 | 573 |
| 上列朝下面積 mm² | 2498.075 | 2661.309 |
| 其中心垂直射線最大空隙 mm | 59 | 59 |

兩檔所有中心射線皆找到出口；各筆警示的面索引、位置、方向、弦長或垂直空隙在初報 JSON 完整保留。網格面數及取樣位置不同，不能用警示數變少推斷可印性改善。

候選最短弦樣本為 `(-12.7892917, -6.49393082, 52.7333323) mm`，向內方向 `(-0.23733448, -0.97142799, 0)`，弦長 `0.00624769247 mm`，來源三角形面積 `0.0958960 mm²`。新增屋頂及高側窗帶端部另有約 0.03–0.4 mm 樣本。這些微薄端部列為**未解風險**，本次固定候選未為此修改幾何。

法線弦是每面中心的有限樣本，**不是完整 3D 最小壁厚證明**；角落、尖端及不同方向仍可能更薄。另已核對主程式實跑的 [`layer-check.json`](../layer-check.json)：340 個 0.2 mm 水平樣本輪廓皆閉合，但 **156 層有 0.8 mm XY 開運算薄特徵警示**，原始 stdout 見 [`layer-screen-raw.txt`](layer-screen-raw.txt)。這些警示保留，不能被本報告的單殼或自交補證覆蓋。

朝下面積與垂直下射線僅協助找懸垂位置；長空隙可能屬狹窄屋簷，短橋亦可能可印。未計算橋跨、支撐可達性／拆除、材料、冷卻、附著或變形，不能據此直接判定支撐必需或可印通過。

## 重跑

在模型套件目錄，以 Python 3 + numpy + shapely 執行；本次環境為 Python 3.13.9、numpy 2.5.4、shapely 2.1.2，實際完整版本亦記錄於各 JSON。

```text
python qa/extended_checks.py --self-test-only --output qa/controls-new-run.json
python qa/extended_checks.py --output qa/extended-checks-new-run.json
python qa/exact_intersections.py --initial-report qa/extended-checks-new-run.json --output qa/exact-intersections-new-run.json
```

原件對照可對兩支程式另外傳 `--stl /path/to/original/model.stl`，並使用新的輸出檔名。請勿覆寫既有初報。重建雜湊及 Blender 場景一致性由套件原有 `validate_model.py` 的另立候選驗證記錄負責；本擴充程式不重建模型或渲染。
