# 南華大學無盡藏圖書館：白覆蓋及前紅坡限域配色

大林校本部既有L形圖書館，不是成均館、校門或其他學校建物。原4378面中，大型金屬覆蓋及九道橫肋頂面190個完整三角採柔白 #D9DAD5；前上層與入口向前紅坡各4面採紅褐 #984A4E。其餘4180面保持中性 #AAA79F。中性意為未確認，不代表實物皆灰色；不是全棟材質復原或2026現況。

![前右視角](previews/front.png)

[後左](previews/rear.png) · [右立面](previews/elevation.png) · [正立面](previews/side.png) · [俯視](previews/top.png)

## 來源與全頂點邊界
親看官方地面VR圖書館node1正面9塊tile完整拼接及官方node5航照原圖拼接。地面節點datetime=2023/9/18 下午02:41是系統欄位，不冒充EXIF攝影日；航照1970/1/1無效預設，確切攝影年未知。不同來源不聲稱同年；不聲稱白頂於2023已存在或2026現況已核。色碼為未校色視覺代理，非實測色票。

模型先逆變換working=(STL/1.5)-(17,2,0)。白覆蓋頂折線(-12.5,30.8)→(-7,31.5)→(-1,31.8)→(1,31.8)→(7,31.5)→(12.5,30.8)，深度y=-20..24。九道橫肋中心y=-19.5+43*i/8，寬0.8，頂高加0.28。5覆蓋段+9×5肋段共50個精確斜面，每個完整三角的全部3頂點必須在同一斜面及x/y支撐內，幾何法向向上且對應斜率。不是bbox或面重心猜測。

紅坡依原hip(0,-25.2,28.1,23.5,8.2,2.4,top=(.92,.17))及hip(0,-32,7.6,14,7.3,1.2,top=(.92,.18))，僅向-Y前斜面，逐頂點核精確斜平面與梯形支撐。端框、頂平面、後坡不染。垂直封邊、肋側面、黑走道、兩側窄屋頂、後端服務箱、粉褐牆、玻璃、布條、玻璃錐亭與未知後壁維持中性，不把實景色界跨入整片牆。全程不切面、不重網格。

## 檔案與重建
[彩色3MF](nhu-library-roofs-appearance.3mf) · [可編輯Blender](scene.blend) · [面映射](face-materials.json) · [色盤](palette.json) · [來源](SOURCES.md) · [權利](LICENSE-NOTICE.md) · [重建來源ZIP](rebuild-source.zip) · [校驗碼](SHA256SUMS)

保留原STL全部座標、4378三角面序及拓撲，尺寸150×141×49.05mm。原native場景唯一Warm stone preview only材質；本補充不改原件、歷史來源或製造QA。重建來源ZIP解壓為model.stl與appearance/source/，安裝requirements後順序執行build_appearance.py、verify_exchange.py、verify_material_boundaries.py，再以Blender 4.3.2+執行render_appearance.py、verify_scene.py。

驗證含lib3mf strict零警告、實際材質修改/存檔/重開、Blender實際材質修改/存檔/重開與其他材質/幾何保留。乾淨重建3MF、映射、色盤及五PNG逐byte比對；Blend僅語義一致，不宣稱binary決定性。3MF為單網格整面表面色，非分色封閉體、G-code或多色FFF保證；未切片器/實體試印。原OSM比例及目估外觀限制不變，不供施工。
