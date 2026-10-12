# 故宮南院主館＋至美橋｜150 mm 外觀列印模型

以館方與建築師刊登的實景及園區圖重建的桌上型外觀詮釋，非測繪複製品。保留墨韻樓、飛白館相互交織的流線量體，以及連向入口的彎曲至美橋。交付的是單一封閉、連通實體，無室內空腔；不是只有方盒的替代品。

## 範圍與尺寸
- 整體約 150 × 150 × 26.84 mm，含 3 mm 平底底座；精確網格包圍盒列於 validation.json。毫米制，比例未經實測。
- 墨韻樓為平面轉折、寬度與高度皆變化的連續曲面；飛白館以另一條曲線交織，並保留厚化的鋼構節奏、玻璃水平分格與梯形入口。
- 至美橋含彎曲橋面、沿外緣升起的拱、19 根厚化吊桿與內緣連續扶手。
- 只做原有主館與橋的外觀；官方園區圖上的第 2 館擴建、周邊湖區建築、樹木與藝術品不在範圍。

## 可驗證來源及估形範圍
查閱日期：2026-10-11。只記錄來源連結，未散布任何參考照片。
1. 館方建築與至美橋介紹，含實景：https://south.npm.gov.tw/AboutUs/Info.htm
2. 已檢視的館方全景與橋身照片：https://south.npm.gov.tw/uploads/Info-pic-00.jpg 、https://south.npm.gov.tw/uploads/Info-pic-01.jpg
3. 館方園區平面圖：https://south.npm.gov.tw/Visit/ParkIntroduction/Plan.htm
4. 已檢視的館方平面示意圖：https://south.npm.gov.tw/uploads/original/%E5%8D%97%E9%99%A2%E5%9C%92%E5%8D%80%E5%B9%B3%E9%9D%A2%E5%9C%9620250613.jpg
5. 姚仁喜｜大元建築工場，2015 年完工主館資料：https://www.krisyaoartech.com/zh-tw/projects/cultural/PALACE-MUSEUM-SOUTHERN-BRANCH
6. 建築師雜誌刊登設計團隊作品說明與實景：https://www.twarchitect.org.tw/works/%E6%95%85%E5%AE%AE%E5%8D%97%E9%99%A2/
7. 已實際檢視的入口、屋頂與全景照片：https://www.twarchitect.org.tw/web2015/wp-content/uploads/2016/08/201608a1-1.jpg 、https://www.twarchitect.org.tw/web2015/wp-content/uploads/2016/08/201608a1-2.jpg 、https://www.twarchitect.org.tw/web2015/wp-content/uploads/2016/08/201608a1-3.jpg

由官方園區圖核對曲線相對方位，搭配正、側景觀照片估算量體。園區圖為旅遊示意圖，不能當實測圖。未取得精確工程平面、剖面或每個背面角度；曲率、各段寬高、橋與館距離、細柱數量、中庭與屋頂收邊屬估形。此模型不對 36,000 多片外牆圓盤逐片復刻。主館高度與橋高為桌上模型辨識而概略配置，不宣稱精確比例或施工可用。

## 為單件 FDM 作的必要變更
- 主館內部實心；玻璃做封閉背板，附有浮雕分格紋理。中庭為露天凹處，並非封閉室內空腔。
- 橋面下填實至共同底座，避免長跨度懸空列印；這是列印支承改造，現實的至美橋並非實心堤道。
- 橋拱直徑約 2.1 mm、吊桿直徑約 1.4 mm、內側扶手直徑約 1.32 mm，均比真實比例厚。拱與吊桿之間保留向外貫通的空隙，不是內部封閉空腔。
- 飛白館外框厚約 1.1 mm 並與館體相交融合；無獨立貼片、透明玻璃或飄浮零件。

## 列印與搬運
建議平底朝下，PLA、0.4 mm 噴嘴、0.16–0.20 mm 層高、3 道壁。橋拱、吊桿上緣及局部入口外框可能需要支撐；先檢視逐層切片和支撐可達性，勿直接當成免支撐模型。橋構件比主館脆弱，移除支撐和搬運時只握底座，避免捏橋欄或吊桿。尚未切片、試印或作機械強度測試。網格合法不等於每台 FDM 都能成功列印，縮小後細件尤其容易損失。

## 檔案及可重建性
- model.stl：最終毫米制單體網格。
- scene.blend：該 STL 匯入後的可編輯網格，附展示相機／燈光；地板不屬列印件。內嵌 build_model.py。
- build_model.py：原始解析幾何。安裝 requirements.txt 後執行 python build_model.py。
- validate_model.py：python validate_model.py model.stl --output validation.json。
- verify_rebuild.py：在新的暫存資料夾執行相同來源，逐位元比較 STL SHA-256，生成 rebuild_check.json。
- render_preview.py：blender -b -t 3 -P render_preview.py。previews/front.png、rear.png 均由實際 STL 算繪；重跑算繪程式可另生成 elevation.png。
- checksums.sha256：交付檔案校驗碼。

驗證包含原始 STL 法向、網格法向一致、每邊雙面、每點單環鏈結、單一表面連通元件、正體積、零面積、底面及最大尺寸。沒有獨立封閉內殼；使用 Manifold 實體布林，但檢查不獨立保證所有自交，也未驗證印表機公差。

重建自檢可執行 python verify_rebuild.py；scene_check.json 另核對 blend 中的列印網格面數、尺寸，以及嵌入來源是否與交付程式一致。
