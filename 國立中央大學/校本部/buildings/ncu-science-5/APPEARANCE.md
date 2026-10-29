# 中央科學五館｜有限內院彩色增補

## 範圍與原幾何保留

原1509頂點／3246三角面、transform及尺寸完全不變，只指定原面材料。保留原STL、OBJ、scene.blend、建模／預覽script、三舊圖與原QA。彩色獨立3MF、BLEND及五視圖，雙README第一章保留原表再加彩圖；首頁／校級鎖定代表圖不變。

## 直接讀到的實景

[校方無障礙校園頁](https://love.adm.ncu.edu.tw/NCU_counsel/NCU-barrier-free/)SB5項標科學五館，其[官方實照](https://love.adm.ncu.edu.tw/NCU_counsel/NCU-barrier-free/images/SB5/1.jpg)與[Commons完整內院照片](https://upload.wikimedia.org/wikipedia/commons/a/a4/NCU_Science_Building_V.JPG)皆正常取得並親看。兩照支持內院L形雙翼、低遮屏、轉角陽台及可見通氣柱，不是完整外側四向。

[Commons來源頁](https://commons.wikimedia.org/wiki/File:NCU_Science_Building_V.JPG)的既有sources記錄SSR2000、CC BY-SA3.0／GFDL、2013-06-01 EXIF；本輪未獨立重驗EXIF或授權頁全文，不當新查證拍攝日。官方照片拍攝日未知，本輪未重讀防災圖冊；非2026完整現況或歷史色復原。照片不包入公開檔。

## 色彩分區與未知

主左翼與右上原院側牆柱白灰，原窗背青灰綠不透明窗／簾混合proxy；右低層原遮屏灰粉褐，屏後牆／連接板／屏下支柱白灰。內轉角原陽台板與欄板米白；沒有新增細欄杆。頂端穿透孔保留通孔，reveal屬結構不是假玻璃。

原單一通氣柱淺灰近似，不補機電細節。未知外側、背面、平屋頂中性；原幾何深度、樓層節奏與遮屏粗化不修造新構件。照片中地面亮黃板沒有原獨立區域，完全不添加、不切面；也不建草地、植栽、字、空調、細窗框與管線。

下層樹遮部位僅相同材料家族近似，非逐面看見；低飽和色未校正曝光日照，不是官方色票或材質實測。灰粉屏不等於整棟粉色，未知中性不代表已證實現況灰牆。

## 可重現與檢核

Blender4.3.2：`blender -b -t 1 --python-exit-code 1 -P build_appearance.py`；原scene.blend/model.stl同目錄。Cycles CPU32samples固定seed0；獨立clean目錄重建，3MF沿原三角純base material不切分。PNG移除文字時間／本機路徑；BLEND按語義幾何材料驗證，不要求容器byte相同。見[審核](appearance-review/)。

原QA仍只是幾何／XY抽樣非全域壁厚或正式切片，遮屏、懸陽台與細原柱需支撐／橋接評估，未試印，不保證免支撐。STL無色正常；3MF顯示依軟體材料支援，不含特定AMS映射。
