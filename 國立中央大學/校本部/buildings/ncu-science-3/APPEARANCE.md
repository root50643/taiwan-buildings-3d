# 中央科學三館｜有限正面彩色增補

## 範圍與原幾何保留

原934頂點／1880三角面、transform及尺寸不變，只指定原每三角材料。保留原STL、OBJ、scene.blend、建模／預覽script、三舊圖與原QA。彩色另有3MF、BLEND、五視圖，雙README第一章保留原圖再加彩表，不換首頁／校級鎖定代表。

## 直接讀到的實景

[校方無障礙校園頁](https://love.adm.ncu.edu.tw/NCU_counsel/NCU-barrier-free/)SB3標科學三館，其[入口近照](https://love.adm.ncu.edu.tw/NCU_counsel/NCU-barrier-free/images/SB3/1.jpg)僅259×194，不足單獨代表完整正面。另正常取得並親看[Commons完整正面照片](https://upload.wikimedia.org/wikipedia/commons/1/1a/NCU_Science_Building_III.JPG)，可見四層正面、左廊柱、中央凹口、右窗帶及排氣塔，與官方入口粉灰材料相符，並非只由局部粉牆外推。

[Commons檔案來源頁](https://commons.wikimedia.org/wiki/File:NCU_Science_Building_III.JPG)，既有sources記錄作者SSR2000、CC BY-SA3.0／GFDL及2013-06-01 EXIF；本輪未重新驗證EXIF或授權頁全文，不把該日期升格為新查證拍攝日。官方近照拍攝日未知。本輪未重讀原防災圖冊；非當代完整現況或歷史色彩復原，來源照片不包入公開檔。

## 有據色彩與省略

原正面牆、柱及可見凹口回牆粉灰，原窗背為深灰綠不透明proxy，中央較退縮窗背依入口近照以稍淺灰綠近似。窗／簾／室內明暗均合併，非實際透明玻璃或窗框構造。照片灰綠水平磁磚細帶缺乏原獨立三角界線，完全省略，不切面也不任意整條牆染綠。

原五組排氣柱淺灰、帽灰，只粗化已有設備，不補管線或機電精細配置。未知外側、背面、平屋頂中性；下層或右側被植栽／車輛遮擋處只是相同材料家族近似，不稱逐面看見。入口門金字／格線、空調、窗框、院景仍省略，不新畫原模型不存在的玻璃面。

色值為低飽和照片近似，未校正曝光光線，不是官方色票或材質實測；原凹口與窗帶粗化不改，彩色不等於精確立面。

## 可重現與檢核

Blender4.3.2：`blender -b -t 1 --python-exit-code 1 -P build_appearance.py`，原scene.blend/model.stl同目錄。Cycles CPU32samples固定seed0，獨立clean目錄重建；3MF原頂點／三角不切分，純base material。PNG移除文字時間／本機路徑；BLEND做語義幾何材料檢核，不要求容器byte相同。見[審核](appearance-review/)。

原QA仍為幾何／XY抽樣非全域壁厚或正式切片，深廊、懸板及帽蓋需支撐評估，未試印，不保證免支撐。STL無色正常；3MF顯示依軟體base material支援，不含特定AMS映射。
