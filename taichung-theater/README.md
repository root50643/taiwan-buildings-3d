# 臺中國家歌劇院｜150 mm 外觀列印模型

本模型以官方外觀照片重新建立幾何，是桌上型外觀詮釋，非實測、工程模型或館方授權複製品。單一封閉連通實體，沒有室內空腔；門窗以外露淺凹表現。所有尺寸以毫米為單位。

## 辨識重點及範圍
- 方整外邊界中保留連續曲牆、瓶口狀玻璃立面、上寬下收再外張的不等寬曲線。
- 主要玻璃凹槽深約 4 mm，有實際建入 STL 的窗格浮雕，並非僅貼圖；少量呼吸孔以淺凹點表現。
- 屋頂四組縮頸曲面、空中花園起伏及後方機能量體作概略表示。
- 含 150 × 116 × 3 mm 平底底座。整體約 150 × 116 × 59.5 mm；以 validation.json 為準。

## 照片來源與不確定性
檢視日期：2026-10-11。參考照片只用於觀察，未收入交付檔案。
1. 場館官方「建築設計」：https://www.npac-ntt.org/about/architecture/design
2. 官方側面曲牆實景：https://www.npac-ntt.org/images/img-build-new-03.jpg
3. 觀光署主外觀照片：https://www.taiwan.net.tw/att/1/big_scenic_spots/pic_A12-00235.jpg
4. 場館官方空中花園：https://www.npac-ntt.org/about/architecture/venue
5. 已檢視的屋頂照片：https://www.npac-ntt.org/dispUploadBox/PJ-/Ckeditor/20200303150605451.jpg

正面及左側以可見照片估形；其餘後、右側未有完整正投影，屬低可信度補形。屋頂曲面位置、大小、窗格數量及呼吸孔位置均為估計。未取得測繪平面圖或現場尺寸，不宣稱固定比例。內部 58 面曲牆與 29 洞窟並未重建，僅表達外牆輪廓。沒有將空間作錯誤的貫通孔洞。

## 可列印性與限制
- 建議平底朝下，PLA、0.4 mm 噴嘴、0.16–0.20 mm 層高，3 道壁；填充由切片器決定。
- 窗格寬約 0.72 mm，僅浮雕在實心背板上；深凹部上緣、屋頂口緣可能需局部支撐。呼吸孔約 1.36 mm，縮小後可能消失。
- 小於真實尺度的細節做厚化與省略。沒有細欄杆、樹木、招牌字或獨立透明片。
- 封閉網格不代表任何機器都能無支撐列印；未實際切片、試印或測試支撐移除。請先看切片逐層預覽。禁止把數位驗證視為實物列印保證。

## 檔案及重建
- model.stl：毫米制單體最終列印網格。
- scene.blend：以最終 STL 匯入的可編輯網格，附相機、燈光與非列印展示地板；另嵌入 build_model.py。
- build_model.py：參數化重建來源。安裝 requirements.txt 後執行 python build_model.py。
- render_preview.py：執行 blender -b -t 4 -P render_preview.py，直接讀取 STL 產生正、背面圖及 blend，重跑可額外生成正投影圖。
- validate_model.py：執行 python validate_model.py model.stl --output validation.json。
- validation.json、rebuild_check.json、checksums.sha256：網格與可重建性報告及交付檔案校驗碼。

網格檢查包含座標、零面積、法向一致、每條邊雙面、每點單環鏈結、連通性、正體積及底面。構造使用 Manifold 實體布林；其外表面只有一個連通元件，沒有獨立封閉內殼。驗證不獨立證明所有幾何自交，也未作列印機公差測試。

重建自檢可執行 python verify_rebuild.py；scene_check.json 另核對 blend 中的列印網格面數、尺寸，以及嵌入來源是否與交付程式一致。
