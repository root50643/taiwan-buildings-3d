# 國立臺北大學建築模型

本校目前 **3 套**，套件數不等於整棟建築數，非全校完成。此體育館立面段與既有圖書館、心湖會館不同；不是全體育館。

首批2件：心湖會館整體外觀近似、圖書館原雙翼主體段；圖資大樓現已同 identity 升級全組。全校尚未完成；臺北校區與校外範圍仍待接續。首批兩件原含底座最長150mm；圖資大樓升級版展示長325mm，獨立比例，STL採毫米。

| 建築模型 | 建築模型 | 建築模型 |
| :---: | :---: | :---: |
| 心湖會館<br>[![心湖會館](三峽校區/buildings/ntpu-mind-lake-hall/appearance/previews/front.png)](三峽校區/buildings/ntpu-mind-lake-hall/)<br>[檔案與正背預覽](三峽校區/buildings/ntpu-mind-lake-hall/) | 圖書資訊大樓全組<br>[![圖書資訊大樓全組](三峽校區/buildings/ntpu-library-main-block-segment/appearance/previews/front.png)](三峽校區/buildings/ntpu-library-main-block-segment/)<br>[檔案與正背預覽](三峽校區/buildings/ntpu-library-main-block-segment/) | [![國立臺北大學綜合體育館彩色凸窗入口立面段：實際模型預覽](三峽校區/buildings/ntpu-gym-colored-bay-entry-facade-segment/previews/front.png)](三峽校區/buildings/ntpu-gym-colored-bay-entry-facade-segment/README.md)<br>**[國立臺北大學綜合體育館彩色凸窗入口立面段](三峽校區/buildings/ntpu-gym-colored-bay-entry-facade-segment/README.md)** |

- [三峽校區入口](三峽校區/)
- [全校範圍、歷史拆除與未完成工作](inventory/)
- [獨立數位審核摘要](qa/)
- [模型索引](model-index.json)

圖資大樓現含後方低資訊翼、通湖平台與階梯，仍為來源約束的外觀近似，不是完整室內或測繪。

本批是手工參數化外觀近似，未抓取現成3D mesh。來源照片與PDF未重新散布。沒有實體試印，也不宣稱免支撐或保證可印。底座朝下，實際列印前請用切片器檢查屋簷、曲帶、跨橋與露臺。

[心湖會館折面屋頂限定配色外觀與來源界線](三峽校區/buildings/ntpu-mind-lake-hall/appearance/README.md)

[臺北大圖資大樓全組升級與來源界線](三峽校區/buildings/ntpu-library-main-block-segment/README.md)

## 圖書資訊大樓既有全組升級

圖書資訊大樓既有同 identity 全組幾何替代，原已有彩色材質，不新增套數。依2014成品照片及建築師B1–7F公開平面重建雙高翼、雙2F資訊翼與3F露臺、2F湖平台及圓井、局部B1院、中央透明頂、五平橋與兩真階橋；非2026現況/測繪，RF設備與細曲率近似，概念額外低樓層/PV不採。325×155×99.625mm、8材質Blend/3MF與不含材質的STL、5真mesh圖與4近圖，60180面；raw/strict材質/Blend頂點存讀與9檔乾淨重建一致。1連通solid、1正外殼與7負閉橋腔；原single-boundary gate FAIL保留，另cavity-aware獨審通過。499有效切層保留82層/2072薄島告警，SLA困樹脂及FFF封閉橋支撐不可移除風險，未實印、非直接print-ready。

[完整模型與來源](三峽校區/buildings/ntpu-library-main-block-segment/README.md) · [QA與保留告警](三峽校區/buildings/ntpu-library-main-block-segment/QA.md) · [固定歷史42檔](https://github.com/root50643/taiwan-buildings-3d/tree/76586f491e45e5e72d371962efcd5ce69af13689/國立臺北大學/三峽校區/buildings/ntpu-library-main-block-segment)。全校與三峽校區均3套不變，非全校完成；校級原批次QA保留歷史快照，本件現行驗證以新詳頁為準。
