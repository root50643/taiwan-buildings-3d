# 照片近似彩色外觀增補

這是既有「行政大樓弧形入口及前庭行政翼（局部）」的材質增補，不是擴建或新幾何版本。原模型 2,839 頂點、5,734 三角面、150 × 87 × 104 mm 及全部座標／面索引保持不變。無新增文字、門窗、植栽或後立面。

## 來源與不確定性

- [教育部網站所載校方 113 年度報告](https://ws-proj.moe.edu.tw/001/Upload/568/relfile/13271/17377/accab4cb-8092-4855-9d38-65f37b5a9f0f.pdf)：印刷頁 12（PDF 第 13 頁）空照佐證大色塊。既有來源紀錄的 PDF metadata 建立日為 2025-04-02，非照片拍攝日期。
- [104 行政大樓近景](https://guide.104.com.tw/backend/media/origin/school/703.jpg)：第三方照片，支持前牆灰粉褐、塔面暖米、翼片混凝土灰、深綠玻璃及銀灰框，不是官方塗裝規格。
- 兩圖實際拍攝日期未知；未宣稱 2026 現況，未嵌入第三方圖片、PDF 或貼圖。
- sRGB 色值是視覺近似，不是色卡校正或建築材料測定。玻璃為不透明色彩代理，原厚框／欄緣仍是列印幾何簡化，不新增透明板或真實欄杆。
- 不支持的背部終止面及大片主屋頂使用中性灰；原平底座並非草坡，亦保留中性灰。

## 原檔保留與格式

原 `model.stl`、`scene.blend`、`render_preview.py` 及 `previews/*.png` 保留，尤其首頁鎖定的 `previews/front.png` 不更動。新 `appearance.blend` 和 `appearance.3mf` 使用同一原始網格；3MF 只增加逐三角面 base-material 屬性，沒有重新取樣／切割／修補網格。沒有因配色而分割成列印多零件，非特定 AMS／多噴頭配置；軟體須支援 3MF 材質顯示，實際切片機台的工具與耗材映射仍需自行檢查。

## 可重現步驟

從此目錄使用 Blender 4.3.2 執行：

```sh
MALLOC_ARENA_MAX=2 LP_NUM_THREADS=1 OMP_NUM_THREADS=1 blender -b -t 1 --python-exit-code 1 -P build_appearance.py
blender -b --python-exit-code 1 -P verify_color_geometry.py -- scene.blend appearance.blend appearance-geometry-QA.json appearance.3mf
```

第一步只寫新 appearance 檔與 `appearance/` 彩圖，不寫原 STL／scene／原預覽。固定 CPU Cycles、32 samples、seed 0、單執行緒；PNG 去除非內容的 Cycles 計時欄位。3MF 固定 ZIP 時間與完整 double 精度座標，保留原 float32 網格精確值。Blender 容器可能有儲存 metadata 差異，clean rebuild 另比對幾何與材質語義，不假稱 BLEND 二進位相同。

## 驗證範圍

本次驗證新增材質、原網格不變、3MF 同幾何與材質、四視圖及獨立 clean rebuild。原數位 QA 的 1,977 個短段／最短約 0.01331 mm 等限制仍保留，見原 README、QA.md；本次不是新的全方向厚度保證。未試印，不保證免支撐／必印成功或真實建築安全。
