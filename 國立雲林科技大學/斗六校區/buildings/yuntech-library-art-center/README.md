# 圖書館暨藝術中心建築群

國立雲林科技大學／斗六校區。本件為公開來源推估的外觀縮模，不是測繪成果。涵蓋範圍：圖書館高層長條量體、階退低層藝術中心及前伸入口翼的整體外觀近似；不含藝術雕塑、景觀植栽及室內空間。

## 最新來源限定前面六材質外觀版（2026-10-20）

![圖書館前立面外觀](appearance/previews/front.png)

[配色、來源界線與四視角](appearance/README.md) · [表面色 3MF](appearance/library-appearance.3mf) · [可編輯場景](appearance/scene.blend)

只改善2008官方照片13013可登錄的前面與左端藝術中心雨棚；背面、屋頂與右入口保持中性。原STL與歷史QA保留，不是新增幾何。[原單色正背合圖](previews/front-rear.png)


[頂視圖](previews/top.png) · [正面大圖](previews/front.png) · [背面大圖](previews/rear.png)

## 下載與重建
- [可列印模型 model.stl](model.stl)：單位毫米，含底座最大邊不超過150毫米，本件尺寸約 150 × 112 × 70 毫米。
- [可編輯場景 scene.blend](scene.blend)：直接匯入交付STL的可編輯網格；[參數建模腳本](build_model.py)是幾何重建來源。
- [依賴版本](requirements.txt) · [來源及年代](sources.json) · [逐檔SHA256](SHA256SUMS)

Python 3.12安裝 requirements.txt 後執行 python build_model.py。Blender 4.3.2執行 blender -b -t 2 -P render_preview.py，會由實際STL生成正、背、頂視圖並保存scene.blend。各建物獨立縮放，不能直接視為共同校園比例。

## 保留的外觀
- 官方1–2、4–9樓平面支持不規則79.45公尺外輪廓、上層72.70公尺長條、右側伸出翼與逐層退縮。
- 保留長條高層方窗、其下水平窗帶、端部挑高玻璃區、前方三級露臺、長形屋頂採光槽及方形屋頂採光罩。
- 藝術中心是同一建築群低層的一部分；沒有另把圖書館、校史館及藝術中心算成三棟模型。

## 推估與範圍限制
- 後續設備界線：校方113年度（2024年度）校務基金決算總說明第14頁列有圖書館屋頂108.29kWp太陽光電建置工程。本模型屋頂仍依2021空拍，這批新增光電及支架未納入；報告年度不是精確施工／完工日，板片配置仍待新屋頂照片核實。 [校方決算總說明](https://acxweb1.yuntech.edu.tw/webppr/P11319GENINFO_C.PDF#page=14)
- 立面依2008–2014實拍，2021官方空拍核屋頂量體；2025校圖仍列同址。不是2026逐扇門窗現況測繪，後來小幅改窗／機電變動未能排除。
- 層高、露臺立面窗高、玻璃分格與樹木遮蔽的低層側翼小窗是比例估計。官方樓層含挑空／夾層，不按九排等高窗虛構九個普通樓層。
- 屋頂採光槽與方形採光罩保留主要輪廓，內部結構、細框、植栽、旗桿、冷氣、管線、宣傳布條、文字與雕塑省略。
- 校方舊平面題名「圖書館暨專業大樓」，網頁代碼AL與2025校圖TL是版本差異，本件不另新增同址建物。

## 列印與驗證
底座朝下、STL單位選毫米。大窗退凹、入口雨棚、露臺及採光罩斜面仍需切片檢查；細窗格以連回牆體的背襯浮雕表示，不是獨立透明玻璃。 數位檢驗並不等於Cura／PrusaSlicer實際工具路徑或實體試印，沒有保證可印或免支撐。

- [原STL／重建／Blend驗證](validation.json)：原始面法向、繞序、正體積、水密、每邊兩面、頂點link單環、單一連通表面及無分離內腔殼均通過。
- [逐層驗證](layer-check.json)：z=0.071毫米起，每0.2毫米共350層；節點degree2、各環與合成Polygon均valid，遇invalid會失敗退出，沒有buffer(0)或make_valid修補。
- [0.8毫米參考寬度薄特徵篩檢](thin-feature-check.json)：每1毫米取樣，0.4毫米半徑opening最大面積損失 0.095%。只屬局部平面輔助篩檢，不是全面最小壁厚分析。
- [總結](qa-summary.json) · [原網格驗證腳本](validate_model.py) · [0.2毫米輪廓腳本](check_layers.py) · [薄篩腳本](check_thin_features.py)

驗證命令依序為 python validate_model.py、python check_layers.py、python check_thin_features.py。只有三項exit 0且validation／layer-check的checks全true才算這一版通過。

參考照片、平面與PDF的權利仍屬各原作者／機關，本資料夾只分享自建幾何、腳本、實際STL渲染與來源連結。
