# 北醫信義校區教學大樓：獨立 QA

最終 v3 通過有限範圍的獨立幾何、來源重建、場景與影像綁定驗證。原數值檢查每模式各 1 個旗標，原 dense 與 aggregate 的 **strict false 完整保留**。該原 runhex 旗標另以精確有理數逐事件分類，沒有理想射線替代、移動樣本或通用豁免。未實際試印。

STL SHA-256：`057835e4338de2033879b701b40c9554c904a95b72efd16e253b284b56867c91`

## 已實際確認

- normal 與 Python -O 各自 fresh 執行；15,734 原三角面，整體含底座尺寸 220 × 70 × 38.650001525878906 mm，單一外表面；原儲存法線、面向、邊與頂點連結通過。
- 每模式 465,075 對閉 AABB 原面候選全數精確完成，含鄰面、共面；不允許交集 0 對，保留全部 151,365 筆實際允許接觸。
- 每模式 157,340 條原面射線，低於 0.8 mm 的弦 0，最短數值首段實體弦 1.1850876040433869 mm。完整 CSV 與 1,888,080 個原十六進位描述值逐一核對，完整重算旗標集合及原因。
- 本件唯一 flag 為 original face 11297 / sample 0。原 origin/direction/point/normal 十六進位資料綁回同一 CSV row，精確分類全部正向原三角面接觸與開區間；保守 exact 首弦約 31.950000047683716 mm。原 strict false 未改為 true。
- 固定 0.2 mm XY 層距，偏移 0.031/0.071/0.137 mm，共 580 層、4,737 個原 Polygon；逐 Polygon 0.4 mm erosion/opening 全部有效、存活且不分裂，個別最大損失 0.5963999238198402%，門檻 1%。
- source 重建 STL 與 color-regions 逐 byte 一致；兩份 saved Blend 同版本重新載入後的材質、相機、可見性與完整允許場景狀態一致。
- 原 Blend evaluated world 有向三角形多重集合吻合 STL，每個視角再次核對；CPU、單執行緒、64 samples、seed 0、無 denoising，沒有照片貼圖或替代網格。
- 九個原視圖各獨立重渲一次，解碼 RGBA 及保留 metadata 一致。公開 PNG 只刪明列 File/時間文字；IDAT、保留 chunk/CRC、色彩及像素不變。原始 PNG 的整檔 bytes 不作可重現承諾。
- 作者與獨立完整科學內容一致。原交集/精確診斷報告可因耗時及所綁交集報告 hash 不同；兩份原報告均完整保留，未改寫成相同。

## 證據與重播

- [最終獨立結果](independent/QA-RESULT.json)、[作者原 strict-false aggregate](candidate-v3/full-qa-summary.json)
- [獨立兩模式 science](independent/geometry/)、[作者 science](candidate-v3/)，含原 CSV、flags、逐 Polygon 與 exact 事件
- [場景重建](independent/source-scene-audit.json)、[九圖重渲](independent/blend-rerender-audit.json)、[來源/圖 hash 綁定](independent/source-appearance-binding.json)
- [原 byte 公開複製及私人省略 ledger](PUBLICATION-BINDING.json)、[完整證據覆蓋](EVIDENCE-COVERAGE.json)
- [controls 封包](controls/controls.tar.xz)、[索引](controls/controls-index.json)、[normal/-O 安全解包及逐 byte 重建](controls/replay-verification.json)

在 qa 目錄執行 `python -B tools/archive_verify.py --archive controls/controls.tar.xz --index controls/controls-index.json --out NEW_CONTROL_TREE`；輸出須全新、父目錄由執行者擁有且非群組/其他人可寫。依封包 ARCHIVE-SCOPE.json 重播。normal/-O 每模式 aggregate 26、descriptor/flag 30、archive 65、PNG 10 控制全過；本件 postflight 政策另有 24 項 fresh 控制。每一模型模式還有 12 通用 fixture/30 子執行、2,736 精確 predicate、36 個 AABB 暴力比對與 48 相交子程序控制。既有工具中的舊專案標籤只是通用程式/封包 layout 名稱，沒有繼承其他模型結果。

`python -B tools/run_full_qa.py --stl ../models/v3/model.stl --expected-sha256 057835e4338de2033879b701b40c9554c904a95b72efd16e253b284b56867c91 --expected-longest-mm 220 --out NEW_QA` 可重做數值檢查；因原 1 旗標，預期原 aggregate 返回非零且 strict false。每模式再用 `tools/diagnose_recorded_cpp_rays.py`，傳入該模式的原 STL、原 dense 報告、flags、raw 報告與 intersections 報告，對該原 runhex 作精確補證，不能刪旗標或將原 strict 改成 true。

## 範圍與限制

這是2021–2022修復後、依2023–2024公開影像建立的主體簡化外觀，不宣稱2024之後完整現況。照片已見短端依場地推定為 NW；另一 SE 端未知面保持簡化，實面不代表已證實無窗。校方82 m總長與歷史4.5 m層高保留原語義，進深、屋頂、電梯等為比例估計。77道格柵、七拱、圓角、接根、加厚與樓梯坡段是製造簡化，非實物原尺寸或構件數；通廊、拱廊、短橋和挑檐仍可能需支撐。模型不含廣場鐘樓、歷史大雨庇、未定年PV或未知屋頂設備。

有限切層/射線及 exact 旗標補證不證明所有方向最小厚度、強度、切片策略或實際可印性。原照、歷史失敗、私路徑與完整執行 log 不公開；來源審核另見 [source-appearance](source-appearance/PUBLIC-SOURCE-REVIEW.md)。
