# 檢查狀態

**外觀／幾何／配色檢查完成；FFF 實際切片待驗。** 各檢查只覆蓋其聲明範圍。

- [來源外觀人工比對](source-appearance-review.json)：可辨量體／材質逐項說明，非測量、攝影測量或像素疊圖吻合測試。
- [來源與不確定性](../sources.json)：兩張官方原圖完整實看；第三張局部 HOLD。原圖未隨包。
- [生成時幾何](build-geometry.json)：四件、各一個連通閉合網格、正體積、零面積三角形 0。
- [重入 STL、接觸與解析截面](geometry-validation.json)：精確 float32 對照、六組裝配配對、主件 36 個解析旗標保留。解析篩檢不等於實際切片。
- [3MF 交換格式](exchange-validation.json)：5 檔 lib3mf 2.5.0 嚴格匯入，0 警告；頂點／三角形順序逐項相同，9 材質與分面指定保留；單色修改回存測試通過。SDK 另存有量化，測試回存不發行。
- [乾淨目錄重建](rebuild-validation.json)：相同工具與字型版本下重新生成的 geometry.json、4 STL、5 3MF SHA 相同。不外推不同版本重建。
- [場景重開核驗](scene-validation.json)：網格及分面指定精確一致；組裝矩陣 float32 誤差量化。沒有嵌入照片、字型或腳本。
- [預覽生成紀錄](render-manifest.json)：四視角 1400×1000／128 samples；[像素及去中繼資料檢查](preview-validation.json) 保留色域資訊與原 IDAT／像素值。

通用表面色可編輯，不等於多噴頭映射或獨立閉合色體。沒有 GUI 匯入、試印、真機校準、支撐可清或黏結強度的宣稱。母版組裝狀態不能直接用作整件無支撐列印佈局。
