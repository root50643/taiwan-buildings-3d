# 輔仁大學・淨心堂

## 模型預覽


| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| ![淨心堂白色門柱與柱帽前臉限域代理](appearance/previews/front.png) |  |  |

## 白色前門柱與柱帽限域配色（2026-10-22）

[五視角、來源與限制](appearance/README.md) · [彩色3MF](appearance/fju-immaculate-conception-chapel-appearance.3mf) · [可編輯Blender](appearance/scene.blend)


僅兩厚門柱與四柱帽前臉16個完整原面配色，共702.20000267mm²；其餘1662面中性。全頂點有限平面域，不切面、不擴塗柱側、帽頂側與棕暗帽底，窗格／玻璃、屋面、側背保持中性。FJAC自拍JPEG三EXIF日期皆2008-09-08 09:50:53、無XMP；Commons2009上傳非拍攝，不宣稱2026現貌。原幾何另含2013鳥瞰與2017入口配置，後方聖言樓不納入。未校準目視近似，非官方色號或材料鑑定。原1678面座標／面序／STL與歷史QA不變、不增套；未實體試印，照片不分發。


新莊校本部；官方校圖編號 49。這是公開照片導向的整棟外觀近似研究模型，並非精密測繪或BIM。


## 外觀依據與範圍
扇形收尖主體、斜置側翼、突出正面高窗與深直立肋柱、前階梯、粗化屋頂Alpha／十字架符號。後方高層聖言樓不納入。

## 必讀的證據缺口
外觀主要反映2008／2013年已確認形態，2017年入口與公開平面配置補證；2025活動只能證明使用，不證明外觀完全未變。後方立面、精確進深及屋頂高程未經測量，保守簡化。內部平面僅用來判斷外包絡，不建立內部房间或隱藏空腔。屋頂符號及窗格厚度已放大；非裝飾藝術品複製。

每件獨立估計比例；含底座最長邊150 mm。模型預覽直接匯入交付的 model.stl；沒有用替代美化模型渲染。顏色僅為展示材質。

## 檔案與重建
- model.stl：原始交付列印網格
- scene.blend：由相同STL匯入、可編輯網格與展示鏡頭
- build_model.py、requirements.txt：可重建來源
- render_preview.py：以Blender 4.3.2以上產生展示及Blend
- validate_model.py、validation.json：原始法向、邊/頂點流形、單殼、正體積、重建SHA及Blend一致檢驗
- check_contour_validity.py：0.2 mm間距原始STL截面封閉／多邊形有效性，不修補輪廓
- thin_canonical_v2.py：0.8 mm參考寬度的形態篩檢，使用共邊一致插值
- sources.json：逐來源與年代／用途

使用Python 3.12建立虛擬環境，安裝requirements.txt後依序執行build_model.py；再以blender -b -t 2 -P render_preview.py產生圖片與場景；執行validate_model.py、check_contour_validity.py及thin_canonical_v2.py。

## 列印注意
底座平放。階梯、屋簷、柱廊、窗口凹槽及突出構件可能需要支撐；先用自己的切片器檢查懸空與橋接，按噴嘴／材料調整。0.8 mm篩檢不是全表面壁厚分析，也不是列印機路徑模擬。尚未做真正切片驗證或實體試印，不能保證可印。縮小會讓窗格、檐角及宗教符號變脆。

## 來源
- [輔仁宗輔中心：淨心堂簡介](https://www.religion.fju.edu.tw/aboutFju.jsp?labelID=19)：官方建築用途、1979年與扇形聖堂敘述；本次網頁直接取回部分失敗，web文字已確認
- [Wikimedia：淨心堂斜正面](https://commons.wikimedia.org/wiki/File:FJU_Religion03.jpg)：實際檢視；EXIF 2008-09-08；FJAC自攝公開原件
- [Wikimedia：校園鳥瞰](https://commons.wikimedia.org/wiki/File:FJU_be-view00.jpg)：實際檢視；2013-02-02；確認低層淨心堂與後方聖言樓分開
- [中研院宗教地景GIS：淨心堂](https://gisrl.ascdc.sinica.edu.tw/religiontw/?q=node%2F665)：實際檢視2017-10-26公開張貼樓層平面圖照片及入口；扇形收尖後段、側翼及前端突出空間
- [輔仁百年校慶：淨心堂音樂會](https://anniversary.fju.edu.tw/anniversary/f5bd8baA3168)：2025年場所仍供活動使用；不作幾何證據

原始第三方照片僅用於私下核對，沒有包入發布資料；幾何自行撰寫，未擷取他人3D資產。
