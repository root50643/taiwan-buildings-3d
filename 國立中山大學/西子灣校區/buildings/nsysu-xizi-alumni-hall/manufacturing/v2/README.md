# 西子樓六分件製造方案

建議使用這六個已定向 STL，**分開列印、最後膠合**。本次已實際執行 PrusaSlicer 2.9.6 切片與路徑分析，並經[獨立重切及固定 SHA 覆核 GO](../../INDEPENDENT-REVIEW.md)，確認指定條件下沒有生成結構支撐工具路徑。尚未實體試印、拆 brim、乾組或膠合試作。原整件 v4 及全部原始 `false / exit 1` 保留；原單件仍需支撐，分件結果不能推回單件。

![組回外觀](previews/assembled.png)

歸檔報告中的原暫存名稱與交付包重跑入口，請見[歷史證據的路徑對照](EVIDENCE-READING.md)。

公開副本只清除私人路徑及影像／場景中的私人路徑 metadata；固定六件與原單件 STL 位元組未變。歷史報告、原始候選 hash 與公開檔案 hash 的範圍見[公開版本說明](../../PUBLICATION.md)。

[六件 STL 與固定 SHA](models/SHA256SUMS) · [編輯場景](scene.blend) · [分解圖](previews/exploded.png) · [列印方向與編號](previews/print-orientations.png) · [設計與量化](DESIGN-REPORT.md) · [實切報告](slicing/solid100-confirmed/SLICE-REVIEW.md)

## 普通單噴頭 FFF 的明確條件

1. 保持 100% 尺寸，每次列印一件，按供應 STL 的 z=0 面貼床。02、04 已倒印定向，**不要再次自動躺平或翻轉**；只需 XY 置中。
2. 使用可穩定輸出 **0.4 mm 噴嘴、首層及正常層 Z 增量 0.15 mm、一般線寬 0.45 mm**的機器；本次以 220 × 220 mm 床面置中分析，含 3 mm brim 的擠出路徑都在床內。其他機器須依可用床面及禁印區重切、核對範圍。
3. 本次保守路徑為 **100% rectilinear infill、3 壁、上下各 4 層、3 mm brim、支撐與 raft 關閉**。這會增加耗材；通用切片估計總長 94.96786 m、體積 228.42 cm³、22h44m06s，並非實機時間或實重。
4. 先選你實際機型、PLA 材料與溫度／黏床／啟停設定，再手動套用以上幾何設定並重新切片。附帶完整 INI/G-code 使用 generic Marlin2、示例 PLA 200°C、床溫 0°C，**僅為可核對的切片證據，不是已校準的真機檔**。

兩片樓板厚約 1.6 mm，另保留原模型 0.15 mm 的床面薄階；0.15 mm 首層可解析它。不要縮小、改成厚首層或擅加 raft。0.15 mm 層離散使本次擠出最高 Z 相較 STL 約為 −0.05／+0.05／−0.05／+0.05／−0.05／−0.05 mm；膠膜與實機公差也會改變最終高度。這是外觀代表模型，沒有緊配合銷或測繪尺寸承諾。

## 為何不用在 7.2 mm 通道拆支撐

原外懸起點在約 z13.4、14.85、25.4、26.85。現在於 13.4／15／25.4／27 分成五個高度帶；兩片 1.6 mm 樓板從另一面貼床印，房間外伸變成床面特徵。最上層斜向欄牆再獨立成第六件，避免把兩個不連通物體假稱一件。

六件印時都沒有上方另一層露台遮住操作空間。實際六份 G-code 的支撐 TYPE 與支撐擠出全部為零；原未改 checker 六件的 0.8 mm 薄核心及 45° 支撐旗標也均零，另以 0.15 mm 切層及高度事件補檢。**這個結論不是只因把切片器支撐設成關閉。**

需要處理的是每件床面外露的 brim：取件後先在開放空間沿外緣分段修除，扶住大片實體，避免拿 1.2 mm 欄牆或細柱作施力點。06 欄牆的所有底邊與 brim 在裝配前均可從外側接近；沒有整塊支撐要擠過約 7.2 mm 的通道。床面釋離、brim 接觸及拆除力仍須實機確認；若你的重切結果新增結構支撐，需另行確認可達與可移除，不適用本次零支撐路徑結論。

## 分件與組裝

| 件 | 固定列印檔 | 方向／裝配 |
| --- | --- | --- |
| 01 | [底座與一樓](models/01-base-floor1-upright.stl) | 正印，組裝基準 |
| 02 | [二樓樓板](models/02-floor2-slab-inverted.stl) | 已倒印；完工後翻回，接於 01 |
| 03 | [二樓上部](models/03-floor2-upper-upright.stl) | 正印，接於 02 |
| 04 | [三樓樓板](models/04-floor3-slab-inverted.stl) | 已倒印；完工後翻回，接於 03 |
| 05 | [三樓與玻璃角塔](models/05-floor3-main-and-tower-upright.stl) | 正印，接於 04 |
| 06 | [三樓斜翼欄牆](models/06-floor3-diagonal-rail-upright.stl) | 正印，最後接於 04 的斜向外緣 |

先按 01→02→03→04→05 乾組，用大片房間外牆及樓板輪廓對齊，再以適合實際材料的接著劑按廠商方式膠合。06 最後裝，避免前面操作壓壞。不要以細欄牆定位或夾持。無額外插銷、磁鐵、卡扣或改變外形的填充；組裝矩陣及各件實際外框在 [build-report.json](models/build-report.json)。分解圖中的間距僅為說明，實際接面相貼；印向總覽也不是六件同床排版。

## 實測結果與保留旗標

- 六件均封閉流形、正體積、各一個連通實體。全部 0.2 mm 原檢查的薄核心與支撐旗標為零；0.15 mm 及高度事件補檢亦無大懸垂。[原 checker 結果](qa/bounded-check/SIX-PARTS-QA.md)
- 新六件仍有 93 個數值自交旗標：9 分離、24 僅共邊、60 僅共點；精確原座標診斷無越界交集。01–05 的原 CLI 仍 exit 1，06 為 exit 0，沒有改旗標或門檻。微超數學 45° 的浮點面另有量化，沒有稱所有面數學 ≤45°。
- 六份 Info／切片／路徑 audit 均 exit 0。100% 設定保留 01 的 19 條 Bridge infill，其餘五件為零；依前層實際正擠出線以半線寬 0.225 mm 掃掠量測，最長連續缺口約 **0.225000058 mm**。仍有局部極短邊界疊邊，不能寫所有橋接為零。[逐線證據](slicing/solid100-confirmed/bridge-location-summary.json)
- 先前 15% gyroid 的最長內部缺口約 8.467213 mm，未經實機橋接驗證，未採作普通 FDM 的默認條件；完整探索輸出保留於 [探索報告](slicing/gyroid15-exploration/SLICE-REVIEW.md)。
- 六件組回後 AABB 與原 v4 相同，體積總差約 +0.000109749 mm³；採樣最大表面差約 0.000000824 mm。這是分割／STL 量化的有限採樣證據，非所有點的形式化 Hausdorff 上界。六件可獨立重建位元組一致，沒有新增底板、封閉露台或重畫建築。
- 六件場景逐面與交付 STL 相符，組裝矩陣及三圖 framing 實測符合。初次場景的 Euler 半轉殘差造成嚴格矩陣 false，已保存於 qa/scene-attempt-01；改用精確四元數半轉後以**相同 checker**重驗通過，未改比較式。[場景檢查](qa/render-scene-validation.json)

原整件 SHA `05c1714f8b363075a2eb72cde39d21ef06eb0720f1b46336579eb48edbb1444f` 未變。歷史製造階段的原候選 164 檔全部未改，見當時的[保留證據](qa/original-preservation.json)；公開副本文字／metadata 變更依 [PUBLICATION](../../PUBLICATION.md) 及目前公開清單，不宣稱公開164檔仍全同未遮罩候選。 原四層真懸垂、146 旗標及單位比較 false／exit 1 仍在原模型資料夾。

設計測試的 `qa/design-probe/assembled-union-verification.stl` 有兩個零面積三角形，是失敗輔助產物，**不可列印**；正式路徑只使用 models/ 下六件。v1 三件原型失敗、首次橋接解析與準備腳本失敗也有保留，沒有把它們寫成成功。

## 重建與重切

在本 v2 根目錄，以原模型 requirements 的 Python 環境執行；重跑 G-code 路徑圖片 audit 另需 [requirements-review.txt](requirements-review.txt) 的 Pillow，場景使用 Blender 5.2.2 LTS／同版 bpy：

```text
python -B source/build_split.py --output-dir output/rebuilt
python -B source/verify_split.py --output-dir output/geometry
```

原 checker 可從這裡逐件執行 `python -B ../../qa/independent_geometry_qa.py models/檔名.stl --json output/該件.json`。原旗標不因補充精算而變成通過。

重建本次幾何切片證據可用 [官方 PrusaSlicer 2.9.6](https://github.com/prusa3d/PrusaSlicer/releases/tag/version_2.9.6)，例如將其 CLI 完整路徑代入：

```text
prusa-slicer-console --datadir output/local-data --load slicing/solid100-confirmed/geometry-review-0.4mm-0.15mm-solid-rectilinear-no-support.ini --threads 2 --center 110,110 --export-gcode --output output/01.geometry-review.gcode models/01-base-floor1-upright.stl
```

這是重現切片證據的指令；正式列印仍須使用自己的機器與材料設定。每件 argv、exit、CLI 文字與 G-code 的去私人路徑副本都在 slicing/ 下。工具 ZIP／EXE 的版本及雜湊已記錄，未把外部工具、憑證或第三方原始照片放入模型包。尚未進行任何實體試印、brim 拆除力或膠合強度試驗；已完成獨立數位覆核，公開結論限上述製造條件。
