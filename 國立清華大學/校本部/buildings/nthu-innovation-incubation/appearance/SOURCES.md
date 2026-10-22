# 配色來源與辨識範圍

## 九典聯合建築師事務所官方完工作品
[清華大學創新育成中心](https://www.bioarch.com.tw/work/清華大學創新育成中心/)；頁列作品年度 2011–2016、狀態完工。此為設計建築師來源，不能稱校方擁有照片。檢閱日 2026-10-22，不等於拍攝日。

親看以下三份原始 JPEG 全圖及原灰模：
1. [湖側整體斜視](https://www.bioarch.com.tw/storage/2024/11/%E6%8A%95%E5%BD%B1%E7%89%871-18.jpg)：1920×1080、778581 bytes，SHA256 `f90fd3df173f385fc956cd798de4c18f4fe879cd9445de77f10622243d5069f1`。辨高棟磚框與低翼深灰簷；畫面左側鄰棟不納入。
2. [院落高棟斜視](https://www.bioarch.com.tw/storage/2024/11/%E6%8A%95%E5%BD%B1%E7%89%873-15.jpg)：1920×1080、500892 bytes，SHA256 `b0047cc007f73301a3b91697158c8e0ad9770da952daba41a9e7295074879054`。確認上部磚框、玻璃與不透明分帶；遠方台積館不混入。
3. [院落及低翼拼圖](https://www.bioarch.com.tw/storage/2024/11/%E6%8A%95%E5%BD%B1%E7%89%874-14.jpg)：1920×1080、717911 bytes，SHA256 `d70934be3adff715590da0c73481abb659ae6c41626b1f9dc2531be9ca9a844f`。右半辨低翼深灰簷前緣，左半院落不當成第二棟或另一日期。

三張上層 EXIF 與 nested ExifIFD 皆空；DateTimeOriginal、DateTimeDigitized、DateTime 未提供。原始 XMP 只有 DocumentID／InstanceID／DerivedFrom／CreatorTool，沒有 CreateDate／ModifyDate／MetadataDate。toolkit 的 2012/02/06 是軟件版本時間，URL 2024/11 是路徑，作品 2011–2016 是作品年度；皆不可推成原照攝影日。因此拍攝日期未知，不稱 2026 同期測繪。

## 原面與材質映射
原資料固定參照 `2764ddf7a1221e9d6ecd8402ede80cfd8fb54fbb`。STL SHA256 `299656bf3e4e9e65d94a0b4ace96512a289698820cc020f28dca4207076ba5da`；Git blob `f39ce13bbba2feaca97167ac419d3d8ee959a244`。原 Blender 為 Printable_NTHU、8666 三角、唯一 Warm stone preview only，所有 material index 0；實際 bytes、原三角座標與順序皆驗證。

以三頂點完整有限平面域與前向法向 ny < -0.99 選面，epsilon 0.0002 mm，不以 centroid 或泛 bbox 染色：
- 高棟內退實心橫帶 y=16、x[-63,63]、z[97.7,101]：2 面。
- 高棟頂部外框前臉 y=14.5、x[-65,65]、z[101,103]：6 面。
- 左右外框柱前臉 y=14.5、x[-64.25,-61.75] 或 [61.75,64.25]、z[38,103]：各 2 面；實選到 z101，上段與頂框融合。
- 低翼簷前臉 y=-61、x[-66,66]、z[35,37.2]：2 面。

高棟 12 面共 973.47537 mm²，低翼 2 面共 290.40009 mm²。#B7866D 暖磚與 #424A4D 深灰金屬僅未校正視覺代理。這不是完整磚框／玻璃／葉片材質復原：未能完整分選的角面、窄框與未知範圍維持中性，不為補齊配色擴染。

照片只供私有研究辨識，不隨成品或 ZIP 重散布。原模型幕牆細分與實景不完全一致，兩翼深度及低層邊界仍是歷史近似，不以本次材質推認幾何精確。
