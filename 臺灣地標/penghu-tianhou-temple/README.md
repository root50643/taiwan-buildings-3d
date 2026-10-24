# 澎湖天后宮｜150 mm 可列印外觀縮景

研究與建模日期：2026-10-11。

成品外廓（含底座）：110 × 150 × 58.9 mm。STL 單位為毫米。

## 模型預覽

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正面<br>![正面](previews/front.png) | 背面<br>![背面](previews/rear.png) |  |

## 建模範圍與辨識特徵
保留三川殿、正殿與二層清風閣所形成的三殿二院，以及兩側護龍／廊道、前低後高的地勢、多角形前階。正面依官方照片辨識三開間門面、中央與兩側分段翹脊、低側翼、方柱與側門；未以單棟普通廟屋替代整體配置。

燕尾、屋脊及瓦面採加厚輪廓。精細龍飾、剪黏、刺花、彩繪與碑刻沒有逐一複刻；門窗以實體淺凹與浮雕表達。院落向天空開放，殿內則填實，不製作神像、內部祭祀空間、香爐、人群或燈籠線。

## 尺寸依據與推估
未取得可用的完整量測圖與屋頂俯視資料，沒有設定宣稱精確的建築比例尺。平面由官方三殿二院介紹，配合正面及側面照片推估，並統一到 150 mm 長邊。殿深、兩院距離、後殿外窗與左右牆面節奏屬保守簡化；精確修復應另取得授權測繪圖。宗教文化地圖的平面示意圖與部分內頁照片目前回傳未授權提示，未使用該圖像推定細節，也未繞過限制。

## FDM 列印建議
底座平放，建議 0.4 mm 噴嘴、0.16 mm 層高、3 道外牆及 12–18% 填充起試。瓦條是約 0.8 mm 直徑的連體浮雕，屋簷有厚化，但有外挑及急升的燕尾；請檢查屋簷、前柱廊與屋脊端部的局部支撐。優先使用容易拆除的外側樹狀支撐，避免密集支撐卡入兩個院落。門面細紋、淺凹窗及瓦面可能需小層高才能顯示。拆支撐時握住基座，不要扳燕尾。

## 公開來源

- https://www.penghu-nsa.gov.tw/TravelInformationSceneryDetailC001200.aspx?Cond=73eae1ff-0b2f-4bfd-b1b3-b37f0c611a31&Language=1028
  - 澎湖國家風景區公開外觀側照；核對正面分段屋脊、多角形前階、側牆及低側翼。
- https://view.boch.gov.tw/NationalHistorical/itemspage.aspx?id=81
  - 文化資產局正面照片、三殿二院及二層清風閣文字。
- https://taiwangods.moi.gov.tw/html/landscape/1_0011.aspx?i=62
  - 內政部文字確認三殿二院、前低後高、多角石階、潮州風格與方柱。平面圖及部分照片回傳未授權提示，未當作已看過的參考圖。

## 檔案內容
- model.stl：毫米單位的單一可列印外觀模型，底面 Z=0。
- build_model.py：原創參數化 Python 建模程式，可修改數字重建模型。
- editable.blend：由最終 STL 匯入的可編輯網格，已設定毫米單位。可列印物件名稱為「Print-ready exterior (mm)」。相機不是列印物件。
- previews/front.png、previews/rear.png：直接渲染最終 STL 的完整正面／背面斜視圖，沒有另外加上無法列印的裝飾。
- source_review.json：公開參考來源、採用特徵與推估範圍。
- validate_model.py、validation.json：非修改式幾何、原始法線與原始程式重建檢查。
- check_blend.py、blend_validation.json：檢查 Blender 網格與最終 STL 的幾何一致性。
- requirements.txt、SHA256SUMS.txt：套件版本及檔案摘要。

## 重建與編輯
需要 Python 3.12，先執行：

    python -m pip install -r requirements.txt
    python build_model.py
    python validate_model.py

需要重新製作 Blender 檔與預覽時，使用 Blender 4.3 或相容版本：

    blender -b -t 4 -P render_preview.py
    blender -b editable.blend -P check_blend.py

可用 --output 指定另存 STL，例如 python build_model.py --output revised.stl。修改後請重跑驗證。Blender 檔是可編輯網格；建築尺寸與程序性修改以 build_model.py 為主。

## 驗證與限制
數位驗證確認：單一連通外邊界、水密、面繞向一致、原始 STL 法線與頂點順序一致、每條邊恰有兩個相鄰面、各頂點的鄰接面形成單一環、無退化三角面、正體積、平整接地、最長邊 150 mm。原程式重新輸出的標準化三角形摘要相符；.blend 的可列印網格也與 STL 一致。模型沒有封閉的空腔內殼。外廊或裝飾下方若有對外通孔，不是破面或封閉空腔。

尚未實際切片或試印。數位檢查不等於實體列印保證；未另以獨立三角面交叉演算法證明所有自交情況，主體採 manifold3d 實體布林建立。請先用自己的切片軟體檢查支撐、薄壁、橋接、耗材量及列印時間。不要未檢查就縮小模型；細節會一起變薄。

此為公開外觀的桌上型建築縮景，不是測繪圖、修復工程模型或精密等比例複製品。參考照片僅供觀察，未隨包附送，也沒有使用他人 STL／3D 資產。預覽為單色材質，不代表實際建築配色。正面／背面是模型視角標示，未宣稱精確地理方位。
