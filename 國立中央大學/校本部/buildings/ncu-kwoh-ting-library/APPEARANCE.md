# 中央國鼎圖書資料館｜有限彩色外觀增補

## 原模型與代表圖不變

原2,538頂點／5,132三角面／transform／150×105×145.8mm完全不變。原STL、OBJ、scene.blend、建模和原渲染腳本、三張原預覽及原QA全保留。兩README加彩色比較，不更改學校／校區／首頁代表圖；原單色圖不冒稱已上色。新增appearance.blend／appearance.3mf／五張appearance圖與可重現script。

## 官方照片與色彩範圍

已實讀[校方無障礙地圖](https://love.adm.ncu.edu.tw/NCU_counsel/NCU-barrier-free/)的LIB_KT中文國鼎圖書館項目，明確連到[國鼎外照](https://love.adm.ncu.edu.tw/NCU_counsel/NCU-barrier-free/images/LIB_KT/1.jpg)。館名、圓柱中央、雙高翼、低翼和弧入口可辨；不是國鼎光電大樓、總圖或中正館。來源日期未知，不能把原模型另一Commons照片的2013-09-30 EXIF套到這張校方照片，也不把2025防災表日期當拍攝日。

雙翼可見正面為淺灰板／磚，中央前柱帶灰褐，窗帶與翼窗暗藍灰不透明代理；原上部框架／棚架深灰，低弧廳灰粉褐石面近似，原細簷棕褐。保留原表面，不生成石紋、磁磚縫、牌字、空調、欄杆或天際反射。入口上方淡粉米小板原網格缺可分面界線，本次省略，避免以任意三角面補造假框。前階灰色。

未知後柱、側後外牆、水平屋頂和人工底座中性。棚架屬現有同類可見構件的近似材色，並非逐面調查；不把深灰鋪滿屋頂。sRGB只是低解析實照的未校準顯示近似，渲染轉linear；不代表施工色卡或真玻璃物性。來源照片只留私人研究，不附公開包。

## 重建／格式

Blender4.3.2，原scene.blend/model.stl與script同目錄：

```sh
MALLOC_ARENA_MAX=2 LP_NUM_THREADS=1 OMP_NUM_THREADS=1 blender -b -t 1 --python-exit-code 1 -P build_appearance.py
blender -b --python-exit-code 1 -P verify_color_geometry.py -- scene.blend appearance.blend appearance-geometry-QA.json appearance.3mf
```

只產生新增appearance，不覆寫原件。Cycles CPU32samples/seed0/單執行緒，PNG清除所有文字metadata但保留IDAT，3MF原頂點面索引與base材料、完整double座標和固定ZIP時間；無Boolean、重採樣或拆面。兩次獨立重建比script／3MF／materialJSON／PNG byte，BLEND比幾何材質語義不保證容器byte。需支援3MF材質的軟體，不含AMS耗材／多噴頭機台映射。

## 保留的近似與QA限制

原側後深度、中央柱後部接合為估計，不代表實測圓形平面。窗帶與棚架已原模型加厚，這次不增新現況或樓高精度聲稱。原146層1mm pitch／半徑0.4mm（直徑0.8mm）XY開運算不是全面全向最薄壁或slicer驗證；細框、棚架和屋緣仍要支撐／縮尺檢查。未實體試印，不保證免支撐、必然可印或結構安全。
