# 大仁科技大學 A行政圖資大樓：歷史限域外觀層

既有模型的局部材質改善，新增模型套數為零；不是整樓全彩復原，也不是2026現況調查。

- [三材質3MF](tajen-admin-library-appearance.3mf) · [可編輯Blender](scene.blend) · [材質表](palette.json) · [逐面對照](face-materials.json)
- [正面](previews/front.png) · [左面](previews/left.png) · [右面](previews/right.png) · [背面](previews/rear.png) · [頂面](previews/top.png)
- [來源與年代](SOURCES.md) · [授權說明](LICENSE-NOTICE.md) · [重建原始碼包](rebuild-source.zip)

4096個原三角面保留座標與面序，原STL bytes完全不動。僅官方照片支持的東低翼連續粉色外皮162面／1420.309600平方毫米，以及南／東實有凹入暗窗背288面／3082.914176平方毫米；合計450面／4503.223776平方毫米，其餘3646面維持中性。147有限群組全部三頂點須在同一有限平面及邊界內，實際叉積法向吻合；逐組驗證canonical原面序，4個原本無面的群組維持0面。不以中心點選取、切面、重三角化或新增玻璃。

主南立面粉牆因原三角形跨越實景下白帶，整片維持中性，避免非實景的三角斜色縫。東高牆灰白帶、屋頂、後方、未確認西面、框／凹口側壁、深低翼大凹口背面及底座皆中性。不是前景C活動中心；不把C的筒頂當成A屋頂。粉牆與暗窗背均是不透明展示代理，色彩未校色，不代表精確RGB、廠商色號或真實透明光學。

## 原始幾何與製造警示完整保留
原模型是照片近似，不是完整圖面測繪。北方未知窗省略、屋頂尺度高度不確定、柱廊粗略且部分推測。本次配色不修復原幾何或製造限制。原39局部截面損失、1054作者短首段樣本、2331獨立密樣短首段仍然存在；長支撐根不能抹去短首段，非角點損失不為零。南／東窗淺浮雕與東帶最小尺度限制保留。原QA.md早期pending與independent-review.md後續serial402接受屬不同歷史階段，不能改寫成這次無條件全通過。本輪未重跑完整壁厚、自交、切片器或實體試印，交換材質／拓撲檢查不等於製造保證。

## 重建與交換驗證
appearance上層保留原model.stl，安裝source/requirements.txt；執行 `python source/build_appearance.py`、`python source/verify_exchange.py`，再用Blender執行 `source/render_appearance.py` 與 `source/verify_scene.py`。固定Cycles CPU種子生成完整五圖，PNG移除時間metadata。乾淨重建比較3MF、map、palette及五圖bytes；Blend比較真頂點與材質語義，不宣稱Blend二進位一致。兩格式皆實際編輯材質存讀，Blend另實際編輯頂點存讀並從交付檔reopen render核對。
