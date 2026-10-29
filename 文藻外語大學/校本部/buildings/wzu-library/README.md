# 圖書館大樓｜文藻外語大學

## 模型預覽


| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| ![實際STL正面](appearance/previews/front.png) | ![實際STL背面](appearance/previews/rear.png) |  |

校本部／公開外觀近似模型。每棟独立縮放，最長尺寸含底板150mm；並非各館同一比例。實際尺寸：150.00 × 91.00 × 115.10 mm。


## 最新配色與下載

[八材質通用 3MF](appearance/wzu-appearance.3mf) · [彩色 Blender scene](appearance/scene.blend) · [四視圖、來源及配色界線](appearance/README.md)。正面實照支持紅磚橫帶、青綠玻璃與米白柱檐；未確認側後／屋面中性，原 STL 與歷史 QA 不變，未經 FFF／實體試印。

## 外觀與範圍
八層主體、上段四道連續帶窗、中央招牌框、下段兩層柱廊及退縮陽台、屋頂大出簷、側後服務塔與十字架。

後面窗序及樓梯間深度近似；未納入前庭地下採光罩。

主要依據[校方建築物介紹](https://c005.wzu.edu.tw/category/132558)及[2025-03-12公開PDF第19頁外觀照片](https://c004.wzu.edu.tw/datas/upload/files/Documents/111_1075_%E6%A0%A1%E5%9C%92%E7%81%BD%E5%AE%B3%E9%98%B2%E6%95%91%E8%A8%88%E7%95%AB%E6%9B%B8_1140312.pdf#page=19)。現況表填於2023-12；兩來源照片拍攝日期未註明，不把文件日期當拍攝日期，不宣稱2026完全現況。來源照片、PDF及私用對照不隨模型公開。[完整來源及近似限制](sources.json)。

## 檔案
- [STL](model.stl)／[Blender](scene.blend)／[Python重建](build_model.py)
- [原始STL拓撲、法向、重建SHA及Blend一致性](validation.json)
- [0.2mm輪廓閉合與逐輪廓/合成多邊形有效性](contour-validity-check.json)
- [0.8mm XY薄特徵篩查](thin-feature-check.json)

## 數位檢查與列印限制
單一連接表面殼、正體積、所有邊恰有兩面、vertex-link單循環、無獨立內腔、原始法向一致；Python重建SHA相同，Blend與STL三角形一致。0.2mm實際STL斷面通過閉合及有效性assert，未用buffer修補無效多邊形。

屋頂十字架1.8mm方柱及橫桿角點造成8個薄篩警示層；0.8mm開運算未抹除任何獨立柱，非懸浮細柱。

這些均為數位幾何檢查，未經實際列印或真正列印切片器驗證。建議底板朝下、0.4mm噴嘴、0.2mm層高作為切片起點；簷口、雨遮、格柵及挑空需在切片器檢視支撐、橋接與可拆性；不得據此保證免支撐。

## 重建
Python 3.12，安裝requirements.txt，執行build_model.py；Blender以背景模式執行render_preview.py，產生實際STL預覽與scene.blend。接著依序執行validate_model.py、check_contour_validity.py、check_thin_features.py，退出碼均須為0且validation.json所有checks為true。

STL SHA-256：46fd8857dab8dadca6bc429ef697d4dbfe4a797c0b541347d331480a664c0a3c

[校區圖鑑](../../README.md)／[學校](../../../README.md)

## 歷史單色記錄

原 scene.blend、render_preview.py 與三張單色圖完整保留：正面（歷史檔案留存，不作本頁預覽）、背面（歷史檔案留存，不作本頁預覽）、立面（歷史檔案留存，不作本頁預覽）。它們是原模型重建及製造檢查的歷史證據，最新配色展示與交換檔位於 appearance/。原 8 層薄篩警示仍保留，沒有被本次外觀檢查取代。


