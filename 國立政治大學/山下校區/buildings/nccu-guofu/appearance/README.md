# 政大果夫樓：兩個可見瓦坡限域配色

原1020面中，僅主屋朝前庭坡10面、左翼朝前庭內坡9面，合計19個完整原三角面採低飽和灰綠瓦代理 #647B60；其餘1001面採中性 #AAA79F。中性表示未確認，不代表實物均灰色。本件是果夫樓，並非達賢圖書館；不是全棟材質復原或2026現況。

![前庭兩坡](previews/front.png)

[背視](previews/rear.png) · [正立面](previews/elevation.png) · [側視](previews/side.png) · [俯視](previews/top.png)

## 來源與選面
親看官方政大記憶網正面、側面原圖（頁圖說2009），及2025入口輔照。正面檔EXIF DateTime為2009:05:08 11:04:05，不能當獨立拍攝時間認證；側面無日期EXIF，年代依官方圖說。2025僅補充觀察，不據此宣稱2009色值持續不變。頁面文字「綠瓦灰牆洗石子外牆」與歷史照片支持灰綠瓦外觀；色值未校色、非儀器測色或指定塗料。

設 t=(z−27.2)/4，epsilon=0.0002mm。每個三角全部三頂點需滿足0≤t≤1及同一精確坡平面/梯形範圍：主坡 y=6+9.7t、|x|≤67.5−18.9t（10面，815.5810mm²）；左內坡 x=−36.5−15.035t、|y−2|≤24−7.68t（9面，425.1106mm²）。總1240.6916mm²。不以重心或包圍盒選面，不切面，不增加頂點。所有屋脊、簷口、其他坡（含背坡、兩翼外坡及右翼內坡）、牆窗、入口和底板均中性，不因相連而擴染。

## 檔案及重建
[彩色3MF](nccu-guofu-appearance.3mf) · [可編輯Blender](scene.blend) · [面映射](face-materials.json) · [色盤](palette.json) · [來源](SOURCES.md) · [權利](LICENSE-NOTICE.md) · [重建ZIP](rebuild-source.zip) · [校驗碼](SHA256SUMS)

保留原STL全部座標、1020三角面序與拓撲，尺寸150×82×31.2mm。原native單Warm stone材質，本次additive不改原件或歷史製造QA。

重建目錄為model.stl及appearance/source/；Python依requirements.txt安裝，執行build_appearance.py、verify_exchange.py、verify_material_boundaries.py，再用Blender 4.3.2+執行render_appearance.py、verify_scene.py。包含strict 3MF零警告、真正單材質編輯存檔重開及Blender同項驗證。乾淨重建3MF/映射/色盤/五PNG逐byte相同，Blend僅語義一致，不宣稱binary決定性。未切片器、多色FFF或實體試印；非工程測繪或施工模型。
