# 國立故宮博物院北部院區正館｜150 mm 外觀微縮模型

## 模型範圍與辨識特徵
- 成品尺寸約 **150 × 91 × 45.8 mm**，含厚 2.4 mm 平底展示座。STL 單位為 mm。
- 臺北市士林區的北院正館：中央盝頂樓亭、後排兩座小亭、向前突出的兩端樓亭、長向館舍立面、成對前階及中央斜面採光罩。
- 一體式實體；沒有室內、地下空間或封閉內腔。門窗均用朝外的淺凹浮雕表示。採光罩亦為實體斜坡，非透明薄殼。
- 已實際查看市府正面照片、廣角照片，以及青年日報刊載、文化部提供的空拍照片後建立幾何。詳見 sources.md。
- 這是照片判讀後重新建立的概略外觀模型，**不是測繪復刻、精確縮尺模型或官方模型**。館舍進深、各樓亭相對位置、階高及背面比例為推估；背面採簡化量體，沒有補畫不可見的門窗或設備。
- 僅含主館與緊鄰前階，未加入天下為公牌坊、華表大道、園林、旗桿、車輛或其他院區建物。舊照片只作沿革比對；沒有混入1965年未擴建版本或未來整建構想。
- 為 FDM 調整飛簷曲線，合併斗拱及細欄杆、厚化屋脊；省略雕刻、書法、牌匾文字及瓦片紋理。模型中的14級前階與門窗節奏不代表現地精確數量。

## 列印建議（尚未實際切片或試印）
- 起始設定：PLA、0.4 mm 噴嘴、0.16–0.20 mm 層高、3 道外牆、12–18% 填充。
- 維持原方向，展示座平面貼列印平台。底座已足夠寬，是否加 brim 依平台附著狀況決定。
- 屋簷下方做短斜面以降低懸垂，但部分飛簷、屋脊及突出浮雕仍可能需要局部支撐。請先完整檢查切片預覽的孤島、懸垂與薄線；不保證免支撐。
- 欄杆採實心矮牆及約 1.05 mm 方柱；屋頂尖端最低直徑約 0.9 mm，脊飾約 1.15 mm；嵌入式窗框約 0.8 mm。採光罩浮雕肋寬約 0.52 mm，屬貼附細節，切片時可能弱化。
- 不建議直接縮小。若改尺寸或噴嘴，需重新檢查飛簷、屋脊及細節可印厚度。
- 封閉、連通的 STL 只代表數位網格基本健全，不等於支撐分析、完整切片驗證或實體試印成功。

## 檔案
- model.stl：唯一列印用模型。
- build_model.py：可編輯、可重建的參數化 Python 原始碼。
- scene.blend：同一 STL 的 Blender 場景；含相機、燈光與非列印用展示地板。列印僅使用 model.stl。
- previews/front.png、rear.png、elevation.png：直接由實際 STL 產生的前斜視、後斜視及正面預覽，未添加其他建築幾何。
- render_preview.py：重建 Blender 場景與預覽。
- validate_model.py、validation.json：封閉性、連通性、面向、所有邊兩面共用、頂點鄰域、尺寸、體積與平底檢查。
- verify_rebuild.py、rebuild_validation.json：實際重新執行原始碼，比對 STL SHA-256、原始二進位法線、閉合殼層及水平截面。
- verify_blend.py、blend_validation.json：比對 Blender 中的模型三角形與 STL，並記錄來源校驗碼。
- SHA256SUMS.txt：各交付檔案的內容校驗碼。
- requirements.txt：固定 Python 相依版本。

## 重建
先在自己的 Python 環境安裝 requirements.txt 中的套件，執行：

    python build_model.py
    python validate_model.py model.stl --output validation.json
    python verify_rebuild.py
    blender -b -t 6 -P render_preview.py
    blender -b scene.blend -P verify_blend.py

亦可使用 python build_model.py --output 自訂路徑.stl。Blender 場景以毫米顯示；此腳本使用 Blender 4.x 的 STL 匯入操作。

## 權利與限制
本交付不包含參考照片、網站原檔或第三方圖說，亦不授予建築設計、商標或照片的權利。若要公開散布、商用或宣稱官方關聯，請另外確認適用權利與許可。未發布至 GitHub 或其他公開網站。
