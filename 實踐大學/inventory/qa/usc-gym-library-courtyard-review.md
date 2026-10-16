# 實踐大學M＋N＋中央庭院：校級QA資料摘要（重建版）

文件重建時間：2026-10-16T10:23:00Z。本文件依已保存正式模型包中的PUBLIC-INDEPENDENT-QA.md、PUBLIC-INDEPENDENT-QA.json、QA.md、validation.json及原始數值資料重建。它不是遺失文件的原樣副本，也不冒稱於本次重建重新完成獨立幾何、外觀或重渲測試。

## 精確對象

- 一套：臺北校區M體育館＋N圖資大樓＋中央庭院
- STL SHA256：9a23a5c919933e4457a7a8f85440bc00972fb3279183192a61a25938e8a11188
- Blend SHA256：3e55dc70676788ffd0c06d4c89610f6075e2c9a983cec7d6a11cd4b9826c205d
- 正式模型283檔原位元組保留；來源ZIP SHA256：9c8be2b7b2d1caceb9eabf91e853cf5834e261295bf2be1d444636e5b1b844f7

## 保存報告的結論與證據

- 原始STL：10,812面，約200×125×39.12mm；單一閉合表面、正體積，保存報告記錄原始法線／拓樸檢查通過。
- 精確接觸：157,886組閉AABB候選；86,494組合法接觸，非法接觸／共面面積重疊0。保存獨立報告另記錄58,444,266組面對的暴力候選核對。
- 有限原面法線射線：108,120條，最短第一實體弦0.8603973389mm；低於0.8mm者0、旗標0。XZ解壓後完整CSV為70,115,594 bytes，SHA256 b488c118d73944f185eb6744f72b3a819bf9d6a398a0ba76700d195cf7414088。
- 有限XY切層：0.2mm步距，0.031／0.071／0.137mm偏移；587層、3,781個原Polygon。0.8mm opening，失敗0，最大單Polygon損失0.828954%，門檻1%。
- 保存獨立報告記錄源碼重建與同版Blend、7主視圖＋2局部圖的位元一致性。完整普通Python及-O執行／正反控制報告保留在模型包。
- 本次恢復只重新執行唯讀綁定聚合核對（普通Python及-O各89項），兩者全部通過；核對完整CSV解壓後hash、報告／腳本／STL／Blend／PNG綁定，不重新建模或覆寫模型報告。

[保存之獨立QA原文](../../臺北校區/buildings/usc-gym-library-courtyard/PUBLIC-INDEPENDENT-QA.md) · [機器可讀報告](../../臺北校區/buildings/usc-gym-library-courtyard/PUBLIC-INDEPENDENT-QA.json) · [全部檢查與限制](../../臺北校區/buildings/usc-gym-library-courtyard/QA.md) · [模型檔案](../../臺北校區/buildings/usc-gym-library-courtyard/README.md)

## 必須保留的限制

這是公開來源導向、含加厚與細節簡化的外觀展示模型。絕對高度與部分屋面尺寸為估計；不是測繪、BIM、施工圖或完整地下室／室內。有限法線射線及XY切層不能證明全球最小壁厚或實際切片工具路徑。未做實體試印、特定機台／材料／拆支撐測試；大開口、柱廊、V柱上平台及屋檐需要支撐規劃，不宣稱免支撐或無條件可列印。

C棟是另一件既有模型，其漏窗高損失例外不因新增本模型而取消，也不能套用為M＋N模型的豁免。[C棟原始完整警示](../../臺北校區/buildings/usc-c-human-ecology/README.md#漏窗薄屏opening高損失例外與列印警示)。
