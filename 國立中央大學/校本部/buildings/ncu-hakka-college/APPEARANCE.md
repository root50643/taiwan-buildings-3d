# 國立中央大學客家學院｜有限實照彩色增補

## 原模型與代表圖不變

原1,183頂點／2,422三角面／transform／150×132×113mm完全不變，只設定既有三角面的材質；未加新面、構件或改尺度。原STL、OBJ、scene.blend、建模與預覽script、原三張圖與QA保留。兩README第一章加獨立彩圖，不改首頁／校級代表圖，不把舊單色圖稱已上色。

## 已讀實照及排除

- [承包商中央大學工程專案](https://www.reiju.com.tw/product/detail/09015)包含光電與客家兩棟。實讀其中檔名「客家學院 (2).jpg」實景，辨識紅磚高翼、端塔、前方客家山牆小屋與院落；其餘09015.jpg、C-11.jpg、C-13.jpg、C.jpg主體為光電，不能將白格陣／藍玻璃套入客家模型。
- [校方無障礙地圖](https://love.adm.ncu.edu.tw/NCU_counsel/NCU-barrier-free/)的HSB客家學院與[庭院實照](https://love.adm.ncu.edu.tw/NCU_counsel/NCU-barrier-free/images/HSB/1.jpg)支持低翼庭院側色域。
- 照片拍攝日均未標，不把工程2011日期、原研究Commons2012日期或防災表日期移植為本次圖像日期；不稱完整2026現況或完工原色復原。原sources.json引用與不確定性保留；本次沒有依賴未讀Commons。

## 色彩範圍

低飽和紅褐磚面只在來源支持的高翼前側、端塔前、小屋前與可見側／低翼庭院側；米白原框架、薄簷、山牆與小屋柱廊；暗灰藍只用原窗凹背，不把入口陰影當玻璃。灰褐只用來源可見既有坡屋頂，未知大平屋頂／寬背面／底座保持中性。顏色為未校正sRGB近似，並非官方色票或材質性能；玻璃不透明代理，未作真實反射或窗簾。

不造磚縫、瓦片、屋脊獸、精細山牆浮雕、題字、空調、樹木車輛。照片細框／石基若原面不可區分就省略，不任意切新面。原小屋間隔、低翼深度與屋頂平面仍目測粗化；此補色不修造其幾何。

## 重建及驗證

原scene.blend、model.stl與build_appearance.py放同目錄，使用Blender4.3.2：

    blender -b -t 1 --python-exit-code 1 -P build_appearance.py

產出獨立appearance.blend／appearance.3mf／appearance-materials.json／五張appearance圖，不改previews。新PNG移除text metadata。Core3MF逐原三角面同色base material，沒有新增幾何或AMS／耗材設定；切片器匯入支援需個別確認。

獨立原geometry、材料、3MF與逐圖審核及乾淨重建證據見appearance-review。BLEND只語義等價，不宣稱容器byte相同。原幾何抽樣／薄特徵限制仍見README與原QA，不等於完整壁厚或切片保證；山牆、廊道、突出端塔平台與簷需支撐評估。未實體試印，不保證免支撐可印或結構安全。

來源照片/PDF與私人材料不公開隨附。
