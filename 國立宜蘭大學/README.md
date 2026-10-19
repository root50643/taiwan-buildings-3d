# 國立宜蘭大學｜建築外觀3D列印模型

本批新增農林修養室1件，累計6件外觀近似模型；既有5件附件原樣保存。各館獨立比例、毫米；既有五件含底座最長150mm，修養室166mm。全校與全國仍未完成，研究項目不能視為精確棟數。

## 模型圖鑑

| [綜合行政教學大樓](神農校總區/buildings/niu-administration-teaching-complex/README.md) | [經德大樓](神農校總區/buildings/niu-jingde-building/README.md) | [時習大樓](神農校總區/buildings/niu-shixi-building/README.md) |
|---|---|---|
| [![綜合行政教學大樓](神農校總區/buildings/niu-administration-teaching-complex/previews/front.png)](神農校總區/buildings/niu-administration-teaching-complex/README.md) | [![經德大樓](神農校總區/buildings/niu-jingde-building/previews/front.png)](神農校總區/buildings/niu-jingde-building/README.md) | [![時習大樓](神農校總區/buildings/niu-shixi-building/previews/front.png)](神農校總區/buildings/niu-shixi-building/README.md) |

| [體育館（校史近似）](神農校總區/buildings/niu-gymnasium/README.md) | [圖書資訊大樓](神農校總區/buildings/niu-library-information-building/README.md) | [農林修養室（2016修復後近似）](神農校總區/buildings/niu-cultivation-hall-restored/README.md) |
|---|---|---|
| [![體育館（校史近似）](神農校總區/buildings/niu-gymnasium/previews/front.png)](神農校總區/buildings/niu-gymnasium/README.md) | [![圖書資訊大樓](神農校總區/buildings/niu-library-information-building/previews/front.png)](神農校總區/buildings/niu-library-information-building/README.md) | [![農林修養室](神農校總區/buildings/niu-cultivation-hall-restored/previews/v1/front.png)](神農校總區/buildings/niu-cultivation-hall-restored/README.md) |

[神農校總區入口](神農校總區/README.md) · [逐項續接清單](FOLLOW-UP.md) · [研究清單JSON](campus-building-inventory.json) · [五件圖鑑](gallery.png)

行政與南北教學翼合一件建築群；經德、時習、體育館、圖資各一件。館內用途與教室不另計件。每件均有actual STL正背/頂視、可編輯Blend、原始OBJ、程序重建、來源與數位QA。

## 年代及尚缺證據

- 體育館依校史主形態建模：高拱門、角退台、兩層開框及五拱鋸齒頂均有實拍核對，但沿進深與隱藏設備仍估計。2018年百葉/牆面已更新；2025預算記載已裝屋頂光電，本模型未重現光電板陣，不能稱2026屋頂設備完整復刻。
- 圖資以官方跨頁兩面實拍、現行入口照和2F/6F平面核對；未知背窗、斜側窗及屋突明示估計。消防樓層表不直接轉成相同數量的規則窗排。
- 校史照片各自攝影日期未知，PDF建立於2020並不代表全部照片拍於2020。新節能資料的未標棟名照片不拿來猜板陣位置。
- 先前行政、時習等屋頂也須續查後加光電；既有附件沒有改動。[屋頂與年代補充](ROOF-STATUS-NOTE.md)列確切後續來源。

## 全校範圍

官方校地涵蓋神農校總區、城南、五結利澤（松瑞）、金六結實習農場、延文／大礁溪實驗林場、南澳農場、民權眷舍文化教育文創園區。主站五類導覽不足以代表全部校外據點。

電資二館2026-05-05已啟用；第三宿舍不能以預定2027啟用的招募資料當竣工證明。民權新館與日式歷史舊舍修復為不同項目；城南食品創客2025完工驗收後仍須核現況。學生生活中心由審計部資料確認2020-03-02投入使用，但完整外觀模型尚未完成。

依據：[校地資產](https://property.niu.edu.tw/p/412-1005-815.php)、[現行地圖](https://www.niu.edu.tw/p/405-1000-63743,c1051.php)、[電資二館啟用](https://www.niu.edu.tw/p/406-1000-72102,r43.php)、[2025總務會議](https://property.niu.edu.tw/var/file/5/1005/img/514/759657554.pdf)、[學生活動中心完工使用](https://www.audit.gov.tw/p/405-1000-6246,c91.php?Lang=zh-tw)。

## 列印與驗證

毫米、底座朝下。橋、露台、穿堂、弧拱門、開框與挑簷可能需要支撐，先在實際切片器檢查可移除性。既有五件未做Cura/Prusa工具路徑或實體試印，不保證免支撐或直接成功列印。

既有五件有原STL法向/拓樸、每邊兩面、vertex link單環、單一連通表面、重建SHA、saved Blend幾何、0.2mm逐層閉合/Polygon valid、canonical fail-closed v3薄特徵輔助篩檢。

行政模型54.071mm單層opening損失約1.027%，是四個最窄2.3mm矩形屋突的角部圓化損失，已獨立定位並接受警示；不能改寫成全部層零>1%或全面最小壁厚通過。次批兩件沒有>1%抽樣層。opening不是完整壁厚量測。

來源原照片與PDF不隨公開包散布；圖鑑均為actual STL渲染。不是校方官方測繪成果。

[整包驗證](publication-validation.json) · [驗證腳本](verify_publication.py) · [逐檔SHA](SHA256SUMS) · [首批附件保持證據](previous-model-preservation.json)

修養室新增一套，採2016修復後低細節外觀、166mm長單件，已有PrusaSlicer數位QA並有支撐，尚未試印／實拆；4.72mm封頂、8.1mm淺凹走線、5條邊界差異及304條探入受阻見模型頁。舊gallery.png為既有五件合覽。Library未回驗，依使用者取消額外備份門檻而不作本次發布阻擋。既有五件的尺寸／未切片說明不套用到新增修養室。
