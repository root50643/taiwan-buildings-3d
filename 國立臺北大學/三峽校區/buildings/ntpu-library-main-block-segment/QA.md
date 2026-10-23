# QA 範圍、空腔判定與保留告警

## Raw STL，不修復後冒稱通過

本次 v11 重建為 60,180 三角、29,720 精確相等座標焊點，325 × 155 × 99.625 mm 展示外包尺寸。`qa-topology.json`：非有限值、零面積、重面、非雙邊、邊方向錯、頂點 link 錯及法線非正點積均 0；每邊兩面且方向相反，每頂點 link 是單環。

**原「必須 1 個連通表面」的 gate 沒有通過，也沒有改寫成通過。** 本件有 1 個正向外邊界及 7 個反向封閉橋內腔邊界，共 8 個表面分量。原 gate 真實失敗記錄保存在 `qa/original-single-shell-gate.txt`、`qa/original-single-shell-topology.json`；原驗證程式 `qa_single_shell_reference.py` 可在 STL 的另存副本目錄用 `--out` 重跑，不應覆寫交付 QA。

新的適用判準另見 `qa/cavity-validation.json` 與獨立源形/技術審：每腔必須是來源支持的玻璃橋內空間，具有負 signed volume 與正確 winding、嚴格被唯一外殼包含且腔彼此不接觸/相交；不能把 boolean 殘片或偶然接縫稱作建築空腔。早期草稿的 tiny 接縫腔和誤讀玻璃頂投影造成的假階橋已在建構幾何層面排除，**未從輸出 STL 偷刪面或補洞**。

額外把分殼重新做布林減法時，雙差集產生 74 三角／約 −7.61×10⁻⁶ mm³ 的數值殘餘，報告原樣保留，**不稱 exact boolean 等價通過**；此非 raw STL 的殼或被偷刪的殘面。實體判定採 raw 原三角完整 signed 邊界分割、嚴格包含、互不相交與跨殼 SAT 零接觸。

五條平橋分屬 3F–7F，另兩條來源可辨的踏步/座階橋連 3F↔4F、5F↔6F。平面圖中某些均格斜條是下層玻璃頂投影，不重複建成 4F↔5F / 6F↔7F 階橋。

## 全局與局部空實檢查

`qa-layers.json` 使用未四捨五入截線：每 0.2 mm 加最高點下 0.001 mm，共 **499 層**，所有輪廓及 parity 結果有效。**82 層／2072 個正連通區未能存活 0.8 mm 侵蝕測試**；完整保留所有告警，沒有細欄、屋簷尖端等豁免，也不把此結果稱作最小壁厚通過。

`qa/feature-validation.json` 直接讀相同 raw STL：19 空/實點、4 無阻射線、7 局部剖面、2 實際射線厚度。核中庭 2F 以上、兩層低翼上方、局部 B1、低屋露臺、井口/下層底、湖向架空段、7F 退縮，以及 1.25 mm 大道板和 0.55 mm 採光頂片。腔內部另由 cavity-aware 報告與真網格內視佐證。

## 格式與可編輯性

- `qa/exchange-validation.json`：STL / 3MF 頂點座標和面序相同；八個真材質全部逐面指派。lib3mf strict 讀取 **warnings 0**；實改一個材質 RGB/alpha、存檔再讀，其餘材質/alpha/面指派不變。SDK 寫回最大座標誤差約 0.0000153 mm。半透明頂不是 STL 透明功能。
- `qa/scene-validation.json`：Blender 真開 scene，核全頂點/面/材質/identity transform；實改一頂點和一材質，存檔重開確認，未改部位保持。沒有來源照片、外部貼圖或嵌入程式。
- `qa/render-reopen-validation.json`：重開交付 Blend，原 front 相機重渲 PNG bytes 相同。
- `qa/isolated-rebuild.json`：在全新空目錄重建，4 threads；4 核心資料檔和 5 張 PNG 共 9 檔 bytes 全相同。報告僅在實跑成功後成立。
- `qa/detail-render-validation.json`：入口、湖軸、真階橋內與長向中庭近景。只改相機及 QA-only studio 補光，不切/隱藏/增加建築 mesh，不將補光另存進主 scene。

## 明確不適合直接製造

細 guard post 約 0.325 mm、頂格約 0.375 mm、採光頂片 0.55 mm。簷、橋、大道、細欄需要材料/方向/支撐設計。**密閉橋腔有 SLA 困樹脂和 FFF 封閉內支撐難以移除的問題**；本次沒有擅自添加排孔、開口或可拆結構來湊單殼。未實印、未完成 slicer 製程驗證，不宣稱直接可列印、可透光印製或結構安全。可拆/排液列印版需要另行設計，不在本次全樓替代範圍。

## 歷史與封包

舊完整 target（含 appearance）依固定 commit/tree/blob 與逐檔 SHA 私有保留，可 remote recovery。原包 root `SHA256SUMS` 的 README 行是既有 stale 值，不能稱原 checksum 全閉合；原件不改，本次新包 checksum 另行完全閉合。這不是再次單色上色，也不增加模型套數。

`SHA256SUMS` 包含交付來源、程式、真網格、預覽和 QA；ZIP 逐 member actual bytes、CRC、檔案集合都要驗證，並從 ZIP 解包執行重建閉環。原圖/原圖紙不入包。最終獨審、hash 與 ZIP 未封定前不稱 LOCAL READY，未 main stage / commit / push。
