# 旺宏館製造參考檢查選項

本頁提供同一建築套件的局部填縫版，已完成一套[PrusaSlicer 2.9.6真實參考切片](slice-reference-2.9.6/README.zh-TW.md)及[最終獨立增量覆核](../publication/independent-review-8758/FINAL-INCREMENTAL-REVIEW.zh-TW.md)。結論為**有條件 GO，可附製造條件交付代表模型**；不是全棟硬支撐拆除或真機列印放行。G-code為 **NOT-MACHINE-READY**，未試印。

根目錄原R2（STL SHA `00f6bbdd09196fba873d843bb9d50a1c3aad4e19e760978333dce6f49740627c`）保留作外觀與幾何對照，其生成器、STL、OBJ、場景及四張預覽保持原位。**本次切片只適用下列填縫版／`6801…`**，沒有對原R2切片，也沒有新增建築套數。兩版的預覽與QA不能互相移稱通過；版本與備份脈絡見[公開證據說明](../publication/PUBLIC-EVIDENCE.zh-TW.md)。

先讀[列印操作條件](PRINT-CONDITIONS.zh-TW.md)、最新切片與獨立覆核。A–G、C0／D0座標見[regions.json](regions.json)；[區域圖](region-map.png)是**2026-10-18切片前的幾何定位圖**，圖內「未切片」僅屬當時階段，後續證據見本頁連結，不作切片結果。F微縫禁支撐／介面，G的0.8 mm浮雕須核實際路徑。

目前未辨認出已證明完全封閉且不可達的實際支撐，但未證明全域無困料。B／C／G只查已分離小片的有限退路，原位剪分、工具和拆力仍未證；A／D／E、C0門廊／D0平台的全面清除未驗證。不能把原40個幾何疑點當40個實際困支撐，也不一律要求可溶。若實際工具不能安全分離／退出，或需薄肋承力，停止該硬拆方案；替代可溶方案須驗證雙／多材料設備、整個可能困住骨架與介面皆可溶，以及逐區實際進液／交換／排出和清除確認。名義開口不等於液路已驗證，必要時才處理對應局部分件。

## 填縫版下載與實際預覽

檔案：[STL](fill-hidden-gaps/model.stl)、[生成器](fill-hidden-gaps/build_variant.py)、[場景](fill-hidden-gaps/scene.blend)、[實際 STL 預覽](fill-hidden-gaps/previews/front.png)。尺寸仍為 150 × 124 × 68 mm。

STL：198,784 bytes；SHA-256：`6801f9c41c9fd986df4167523ec36195e715d6a38a680c09aff002cba1351b2a`。

下圖、此目錄的場景與下列變體QA均綁定此`6801…` STL；根目錄四圖屬原R2／`00f6…`。

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| [![填縫版6801實際正面預覽](fill-hidden-gaps/previews/front.png)](fill-hidden-gaps/model.stl) |  |  |

生成器鎖定並保留原 R2 原始碼，只在原切除之後加 12 塊入口格柵背肋及 8 塊後窗台背微縫填料。參數見操作條件與 QA 的 20 筆填料帳。實際新增體積 153.3999374 mm³；淨變化 153.3999322 mm³，約原體積 0.03765%。入口 fin 最前平面、X 寬與 bay 邊界保留，格柵側／背面及斜視凹槽外觀會改變。這是製造簡化，不能稱所有可見表面完全不變，也不是建築準確度改善；後棟主要量體、層間輪廓與屋頂沒有重新設計。

## 實跑檢查及未通過項目

- 空目錄重建出相同 STL SHA：[重建記錄](fill-hidden-gaps/qa/rebuild-check.json)。原始三角形是單殼、正體積、每邊雙面且法向一致；3,974 面，體積 407,574.0873 mm³。
- 精確自交補證檢查 45,039 對 AABB 候選、0 非法交點；初篩的 31 個 false／ambiguity 旗標保留。詳見 [原始初篩](fill-hidden-gaps/qa/variant-extended-checks.json) 與 [精確補證](fill-hidden-gaps/qa/variant-exact-intersections.json)。
- 20條固定目標線的原空隙已填，12個bay crop沒有新增／移除。原49個無已測直線出口的固定gap點中，入口9點變實心，其餘40點是幾何抽樣限制，不是40個生成支撐。實際支撐身分與退路以唯一參考切片為準，有限測線不能證明所有支撐可拆。
- [340 個 0.2 mm 幾何截層](fill-hidden-gaps/layer-check.json) 全部閉合，仍有 143 層 opening 警示；薄特徵初篩仍有 180 短弦、支撐初篩 577 向下面。這些是幾何篩查，不是噴嘴路徑或 G-code。
- 以 0.000001 mm³ 嚴格門檻，原 R2 對填縫版的「無移除／填料外完全相等」沒有通過：移除殘量 `5.2452420929e-6 mm³`，填料聯集外新增 `1.2585352629e-5 mm³`，指定填料缺量 `2.0141618505e-5 mm³`；不得寫成零或完全相等。[原始固定測量](fill-hidden-gaps/qa/variant-qa.json) 與 [另立殘量／限定 crop 補證](fill-hidden-gaps/qa/variant-qa-residual-supplement.json) 同時保留。
- [場景補證](fill-hidden-gaps/qa/scene-check-supplement.json) 的全部世界座標三角形在 0.00001 mm 量化後與 STL 相同。初檢因把 Blender float32 的 0.001 儲存值與 Python float64 直接要求相等而 false，原 [失敗 JSON](fill-hidden-gaps/qa/scene-check.json) 及 [初檢程式](fill-hidden-gaps/qa/check_scene_initial.py) 不改；補證明示比較實際 float32 期待值。

以上為2026-10-18變體幾何檢查（`ad7023e`階段）及其原始false／補證；後續`8758edad`已加入唯一參考G-code、實際支撐和細節路徑檢查。可重建、封閉、數位路徑和精確接觸均不等於真機製造通過。操作者須依設備／材料重新核實切片、禁入、分片退出工法與屋緣／浮雕成形；未做液路實驗或物理試印。

## 重現與保留

在套件 Python requirements 環境，從本目錄執行：

```text
python fill-hidden-gaps/build_variant.py
python fill-hidden-gaps/check_layers.py
python fill-hidden-gaps/qa/variant_qa.py --variant fill-hidden-gaps/model.stl --output NEW-qa.json
python fill-hidden-gaps/qa/variant_qa_residuals.py --variant fill-hidden-gaps/model.stl --output NEW-residuals.json
python ../qa/extended_checks.py --stl fill-hidden-gaps/model.stl --output NEW-extended.json
python ../qa/exact_intersections.py --stl fill-hidden-gaps/model.stl --initial-report NEW-extended.json --output NEW-exact.json
```

新增的固定測線、殘量、拓樸與場景證據程式拒絕覆寫既有輸出；其他檢查程式請另給新檔名，不要取代保留紀錄。生成器、截層、區域圖與 renderer 會寫回各自輸出；重跑前先把套件複製到新的工作目錄。場景重建需套件 `requirements-render.txt`，執行 `python fill-hidden-gaps/render_variant.py`；它只重建填縫版單張預覽與場景。區域圖需 `requirements-map.txt`，執行 `python draw_region_map.py`；圖中 C 是原 Z=28.5 mm 實際截面，F 為明示誇張的座標示意。

R2比較報告只更正一段與同檔表／JSON矛盾的尾文：[更正記錄](documentation-correction/correction-record.json)和[修正前Markdown](documentation-correction/r2-geometry-delta-before.md)。R2 JSON、較早e45對main的非零殘量／false及原QA失敗皆保持原位。

既有Library v2已完成官方回讀，對應固定`8758edad`候選；本次加入最終覆核及發布資料的備份新版仍由發布流程辦理，不在本頁預稱完成。回條身分、檔案角色及公開正規化方式見[公開證據說明](../publication/PUBLIC-EVIDENCE.zh-TW.md)。
