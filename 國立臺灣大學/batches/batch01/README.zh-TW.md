# 國立臺灣大學校總區：首批五件外觀研究模型

此批不是全臺大完成清單。五件均為公開照片的簡化外觀模型；不是等比例校園沙盤、現況測量或BIM。每件獨立以最長150 mm設計。

## 本批
- [總圖書館](../../校總區/buildings/ntu-main-library/README.zh-TW.md)：含北側鐘塔，背面與深度簡化。
- [第一行政大樓歷史前棟](../../校總區/buildings/ntu-administration/README.zh-TW.md)：不含南側增建。
- [文學院歷史館舍](../../校總區/buildings/ntu-liberal-arts/README.zh-TW.md)：不含研究大樓及人文館。
- [舊總圖書館／校史館歷史前棟](../../校總區/buildings/ntu-old-main-library/README.zh-TW.md)：不含後棟與後續擴建。
- [農業陳列館](../../校總區/buildings/ntu-agricultural-exhibition/README.zh-TW.md)：圓瓦屏風改作較粗、有背牆的淺孔。

每資料夾包含獨立可重建Python來源、STL、OBJ、Blender、三張實際STL預覽、繁體中文說明及完整驗證紀錄。來源照片沒有重新散布。

## 驗證
五件皆經原始STL法向與繞向、水密、正體積、每邊二面、頂點連結單環、單一連通表面、無分離封閉內殼、150 mm最長邊、來源重建SHA256及Blender/STL幾何比對。細節見各 validation.json。

預覽直接由STL匯入Blender製作，背面刻意無裝飾，避免杜撰。通過網格檢查不等同實際列印；仍須切片檢查與局部支撐。尚未做完整三角自交掃描或試印。

## 來源與清冊延續
- [官方建物索引，2026-08-17版本標題](https://cpo.ntu.edu.tw/map/C_01_list.pdf)
- [官方校園地圖入口](https://visitorcenter.ntu.edu.tw/News_Content_n_6190_s_13289.html)
- [官方互動地圖](https://map.ntu.edu.tw/)

索引包含校總區、水源及城中校區，也有開放空間、合署建物、外部機構與醫院。不能直接把索引列數當獨立校舍總數；另需逐項確定行政歸屬、建築分棟與存續狀態。校外校區尚須獨立清冊。本批尚未完成這些工作，詳見 remaining-queue.json。

下一批優先：人文館、綜合體育館、博雅教學館、普通教學館、第一學生活動中心、新月台。先補多角度公開外觀及地圖量體證據，再製模；不以名稱生成假想建築。

來源工具延用同庫國衛院竹南院區建模驗證方法；本批模型幾何為另行製作。原始來源照片及原建築設計之第三方權利未隨此模型轉授。
