# 弘光科技大學｜食品技藝大樓（F棟）



## 實際 STL 預覽

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| ![正面](previews/front.png) | ![背面](previews/rear.png) | ![俯視](previews/top.png) |



## 模型範圍

保留五排高長百葉框、側面直格柵、頂部水平帶、地面雨棚。百葉全部為與牆體融合的浮雕，不是漂浮片。

未知後側及部分屋頂設備從簡；整體進深、坡地與階梯為視覺近似。校方渲染只作輔證，未取得或轉用既有3D網格。

每棟獨立視覺比例，最長邊含底板150 mm；不是測量、BIM或施工圖。尺寸：150.00 × 103.00 × 83.00 mm。

2026查閱校方名錄仍列此棟，不等同2026完整實拍確認。



## 下載與重建

- [STL](model.stl)

- [Blender可編輯場景](scene.blend)

- [Python重建程式](build_model.py)

- [依賴](requirements.txt)

- [幾何驗證](validation.json)

- [0.2 mm截面閉合及Polygon有效性](valid-sections.json)

- [0.8 mm XY薄特徵篩查](thin-feature-check.json)



Python 3.12安裝requirements.txt後執行 python build_model.py；Blender執行 blender -b -t 2 -P render_preview.py；python validate_model.py；python check_valid_sections.py model.stl .；python thin_canonical_v2.py。



## 驗證與列印限制

原始STL單表面殼、每邊兩面、vertex-link單環、法向與繞序、正體積、150 mm尺寸、重建SHA256與Blend三角幾何一致均通過。415層0.2 mm截面逐環與合併Polygon皆閉合有效，不使用修補。

0.8 mm XY形態開運算篩查最大面積損失比例 0.000743；此值不是最薄壁厚保證。設計獨立肋/框一般至少1 mm，窗上牆面浮雕可更淺。

挑簷、深凹廊、懸挑平台需在實際切片軟體檢查支撐、橋接及方向。尚未正式切片或實體試印，不承諾任何機型無支撐直接列印。



## 公開來源

- [主辦單位實際照片](https://www.taichungjobfair.com/地點-弘光科技大學Ｌ棟生活應用大樓-location-hungkuang-university-building-l)：照片旗幟標示2024；頁面活動更新為2025，拍攝日未提供

- [前項原圖URL](https://images.cdn-files-a.com/uploads/8927069/2000_663088cb047f0.jpg)：2024旗幟可見

- [校方現行建物名錄及3D渲染輔證](https://www.hk.edu.tw/學校環境介紹/)：2026-10-13查閱；縮圖路徑2025/05，非拍攝日

來源照片、原始PDF、網站模型/貼圖不隨此檔案包公開。僅含自行建立的簡化幾何與來源連結。



## 完整SHA256

STL: f6da2b555c5e75e62ea3d166f559cbc01262d42c327104456761decbe0103ee6

重建STL: f6da2b555c5e75e62ea3d166f559cbc01262d42c327104456761decbe0103ee6

詳見 [SHA256SUMS](SHA256SUMS)。
