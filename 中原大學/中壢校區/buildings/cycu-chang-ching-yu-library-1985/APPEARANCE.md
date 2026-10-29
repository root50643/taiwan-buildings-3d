# 張靜愚紀念圖書館｜照片近似彩色外觀

## 同一模型，新增材質

沿用原 4,547 頂點、9,110 三角面、transform 與 127.544907 × 150 × 54.610779 mm 外框；不切面、重網格、Boolean或新造構件。原建模腳本、STL、scene.blend、原渲染腳本、九張預覽及鎖定首頁代表圖全部保留。新增 appearance.blend、逐三角面 base-material 的 appearance.3mf 與八張 appearance/ 圖；不變更學校、校區或首頁選圖。

## 來源及年代

[建築師作品頁](https://www.jjpan.com/project/culture/CYCU-Chang-Ching-Yu-Memorial-Library)的南入口、側面和下沉庭公開照片作表面色類別依據，照片拍攝日期未明。[校方報導](https://www.cycu.edu.tw/?p=32874)記述 2014 外牆磁磚修復；相符風格的捐磚不等於證實原始顏料完全一致。因此這是當代照片配色近似，**不是1985原始色復原，也不宣稱2026現況**。完整來源URL與照片雜湊見 appearance-sources.json；來源照片不放入公開包。

庭院照片可見高梯塔同類磁磚，按下沉庭院／長陽台構形對位為北梯核；照片本身未標方位，未逐面驗證背面，塔牆同色是有限的同類材料近似。

灰米粉褐牆為低飽和近似，不是紅磚；灰藍玻璃為不透明代理，不畫反射樹影或室內。深灰只限原有細框面；東西中層淺槽與寬肋為實牆，不當玻璃。柱、階、平台為灰混凝土近似。鋸齒斜板與四角蓋未有可辨近照，採中性灰；下沉庭底與人工底座不憑空畫草坪。RGB為螢幕sRGB近似而非校準色卡，渲染時轉linear。

## 重建

使用 Blender 4.3.2，保留原 scene.blend/model.stl 與下列腳本同目錄：

```sh
MALLOC_ARENA_MAX=2 LP_NUM_THREADS=1 OMP_NUM_THREADS=1 blender -b -t 1 --python-exit-code 1 -P build_appearance.py
blender -b --python-exit-code 1 -P verify_color_geometry.py -- scene.blend appearance.blend appearance-geometry-QA.json appearance.3mf
```

只產生新增 appearance 檔，原件不寫回。CPU Cycles32 samples、seed0、單執行緒。PNG去除所有文字metadata，不夾帶私有路徑或日期；不改IDAT像素。3MF固定ZIP時間及完整double座標；clean rebuild比對3MF／材質JSON／PNG bytes，BLEND按幾何與材質語義比對，不保證其容器二進位完全一致。

## QA與列印範圍

新增檢查只證明幾何保持、材質對應及重建／影像。原 INDEPENDENT-AUDIT.md 與各QA的有限例外和警告全部繼續適用：短首弦、背接細框、屋頂刻線及角損不因上色消失，沒有重新聲稱全向最薄壁通過。3MF軟體須支援base材料顯示；不含特定AMS／多噴頭耗材映射。未實體試印，不保證免支撐、必然可印或結構安全。
