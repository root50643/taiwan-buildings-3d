# 國立中央大學鴻經館｜有限正面彩色增補

## 原模型與鎖定圖保留

758頂點／1512三角面／transform與150×113×111.8mm完全不變，只給既有三角面材質。原STL、OBJ、scene.blend、建模／預覽script、三張原圖及QA不動。雙README第一章另添彩色比較，首頁／校級代表圖不變，舊單色圖不稱已上色。

## 直接讀到的色證

[校方無障礙地圖](https://love.adm.ncu.edu.tw/NCU_counsel/NCU-barrier-free/)明確HJB鴻經館綁定與[官方實照](https://love.adm.ncu.edu.tw/NCU_counsel/NCU-barrier-free/images/HJB/1.jpg)，可見館名字樣、前突入口與窗高帶／進退立面。照片未標拍攝日，不移用原Commons2013-06-01、2025防災表或2026現況。本次未需取得Commons，亦未重試此前失敗的防災PDF，不能稱本次讀過它們。

## 色域與照片裁切

照片直接支持紅褐磚前牆與入口亭、灰綠／灰藍主窗表觀、較淡窄窗帶、灰台階。只對原前向各退縮wallplane與已見凹入return作同材質族近似；不把整個立體六面染紅。顏色未經校正，是sRGB展示近似，不是官方色票／真材規格。

來源照片裁去頂部、左端受遮擋，因此上方超出照片的原前牆面延用已見前牆材質族只屬推估，並非逐層／全高已直接核實；無可靠照片到模型z分界，未硬切新面假裝精確。未知屋頂、寬背、外側盡端和底座中性。原高低翼／高度／深度／後輪廓仍目測近似。

窄高窗帶含玻璃／窗簾／空調的混合表觀，淡灰綠不透明proxy不是實際玻璃色、百葉或空調構造。主窗與門亦是粗化不透明凹部代理，不加透明／反射／室內。原面沒有框／招牌／磚縫邊界則省略，不造金字、空調、植栽或欄杆。

## 重建與驗證

Blender4.3.2，原scene.blend、model.stl及build_appearance.py同目錄：

    blender -b -t 1 --python-exit-code 1 -P build_appearance.py

另產appearance.blend／appearance.3mf／appearance-materials.json與五張appearance圖，不覆蓋原scene/previews。PNG無文字metadata；Core3MF每原面同色base material，不改mesh，無AMS／設備／耗材映射，切片器彩色匯入支援另核。

獨立geometry／materials／3MF、逐圖和clean rebuild見appearance-review，BLEND只語義等價非容器byte保證。原QA抽樣非全向壁厚或切片保證；入口簷、凹窗上緣與細槽仍需切片／支撐評估。未實體試印，不保證免支撐可印。

來源原圖／PDF及私人研究材料不公開隨包。
