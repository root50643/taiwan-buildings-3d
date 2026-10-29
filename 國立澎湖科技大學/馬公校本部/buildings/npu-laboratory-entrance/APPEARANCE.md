# 實驗大樓入口局部｜彩色外觀增補

## 同一幾何，新增材質

本件仍為入口門廊及後方前兩層立面段，不是全館、不是完整兩層建築。原 1,143 頂點／2,290 三角面／transform／150 × 78 × 81.6 mm 完全不變。原 STL、scene.blend、build_model.py、render_preview.py、五張原預覽與QA紀錄保留，不新增構件、切面、細字、磁磚刻紋或植栽。

原照片可見更高退縮窗帶、山牆、屋面；那些從原模型即排除，本次不加回。背面 y=20、左右 x=±68、上界是人工截斷，配中性灰，不冒稱完整真實側後面。

## 官方照片與色彩限制

[官方實驗大樓導覽](https://www.npu.edu.tw/tour/Details.aspx?Parser=13%2C4%2C34%2C%2C%2C%2C11)所列[入口近景](https://www.npu.edu.tw/df_ufiles/034/s_r0345943(1).jpg)是本次直接視讀配色依據：淡米灰磁磚牆、近白門廊與柱、淡綠灰玻璃、偏暖銀灰框、深灰棕右棚梁、淡灰綠棚板和中性石階。不是海事大樓照片。

導覽頁更新日 2018-09-06，不是拍攝日；照片拍攝日期未知，不能代表2022屋頂工程後或2026現況。RGB為照片近似，不是校準色卡或施工塗裝規格。玻璃/棚板以不透明顏色代理，不是透明材質/室內重建；底座是原人工平板，不畫成真實草坡。來源照片及PDF未包含於公開包。

## 格式與重建

新增 `appearance.blend`、逐三角面 base-material 的 `appearance.3mf`、`appearance/` 五彩圖。3MF保留同一原頂點及面索引，不重新取樣、拆面或Boolean。不提供特定AMS/多噴頭耗材映射；軟體需支援3MF材質顯示，切片時仍需設定機台工具/材料。

使用 Blender 4.3.2：

```sh
MALLOC_ARENA_MAX=2 LP_NUM_THREADS=1 OMP_NUM_THREADS=1 blender -b -t 1 --python-exit-code 1 -P build_appearance.py
blender -b --python-exit-code 1 -P verify_color_geometry.py -- scene.blend appearance.blend appearance-geometry-QA.json appearance.3mf
```

第一步只寫新增appearance檔／新彩圖，不寫原 STL／scene／原預覽。CPU Cycles32 samples、seed0、單執行緒；PNG去除全部文字metadata（含檔案路徑、日期與計時），保留影像IDAT像素。3MF固定ZIP時間及完整double精度座標。Blender容器metadata可能不同，clean rebuild比對其幾何/材質語義，不假稱BLEND二進位必然相同。

## QA與列印限制

原網格/transform不變、3MF與BLEND逐面材質一致、調色sRGB→linear、五視圖及獨立clean rebuild另附檢核。原QA仍適用於同一幾何，但這次不把單純配色說成新增全面厚度保證。原0.8mm opening等數位篩檢不是Cura/Prusa工具路徑驗證；未實體試印，不保證免支撐、必然可印或真實建築安全。門廊頂板、雨棚、挑梁仍需切片支撐/橋接檢查。
