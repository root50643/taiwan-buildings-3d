# 中信金融管理學院早期女生宿舍暨演講廳：獨立 QA

最終 v11 通過有限範圍的獨立幾何、來源重建、場景與影像綁定驗證。原數值檢查每模式各 9 個旗標，原 dense 與 aggregate 的 **strict false 完整保留**。每一原 runhex 旗標另以精確有理數逐事件分類成功，沒有理想射線替代、移動樣本或通用豁免。未實際試印。

STL SHA-256：`fa05503ab8ea54036a9312d4a2d263545c7b01bd61bbe07108558b4ea5974db6`

## 已實際確認

- normal 與 Python -O 各自 fresh 執行；16,096 原三角面，200 × 125 × 58.245586395 mm，單一外表面；原儲存法線、面向、邊與頂點連結通過。
- 每模式 179,377 對閉 AABB 原面候選全數精確完成，含鄰面、共面；不允許交集 0 對，保留全部 118,122 筆實際允許接觸。
- 每模式 160,960 條原面射線，低於 0.8 mm 的弦 0，最短數值首段實體弦 0.911758423 mm。完整 CSV 與 1,931,520 個原十六進位描述值逐一核對，完整重算旗標集合及原因。
- 9 原 flags 各自綁回同一 CSV row、原 origin/direction/point/normal 十六進位資料，精確分類全部正向原三角面接觸與開區間；最小 flagged exact 首弦約 7.066173553 mm。原 strict false 未改為 true。
- 固定 0.2 mm XY 層距，偏移 0.031/0.071/0.137 mm，共 874 層、3,273 個原 Polygon；逐 Polygon 0.4 mm erosion/opening 全部有效、存活且不分裂，個別最大損失 0.532777021%，門檻 1%。
- source 重建 STL 與 color-regions 逐 byte 一致；兩份 saved Blend 同版本重新載入後的材質、相機、可見性與完整允許場景狀態一致。
- 原 Blend evaluated world 有向三角形多重集合吻合 STL，每個視角再次核對；CPU、單執行緒、64 samples、seed 0、無 denoising，沒有照片貼圖或替代網格。
- 九個原視圖各獨立重渲一次，解碼 RGBA 及保留 metadata 一致。公開 PNG 只刪明列 File/時間文字；IDAT、保留 chunk/CRC、色彩及像素不變。原始 PNG 的整檔 bytes 不作可重現承諾。
- 作者與獨立完整科學內容一致。原交集/精確診斷報告可因耗時及所綁交集報告 hash 不同；兩份原報告均完整保留，未改寫成相同。

## 證據與重播

- [最終獨立結果](independent/QA-RESULT.json)、[作者原 strict-false aggregate](candidate-v11/full-qa-summary.json)
- [獨立兩模式 science](independent/geometry/)、[作者 science](candidate-v11/)，含原 CSV、flags、逐 Polygon 與 exact 事件
- [場景重建](independent/source-scene-audit.json)、[九圖重渲](independent/blend-rerender-audit.json)、[來源/圖hash綁定](independent/source-appearance-binding.json)
- [原 byte 公開複製及私人省略 ledger](PUBLICATION-BINDING.json)、[完整證據覆蓋](EVIDENCE-COVERAGE.json)
- [controls 封包](controls/controls.tar.xz)、[索引](controls/controls-index.json)、[normal/-O 安全解包及逐byte重建](controls/replay-verification.json)

在 qa 目錄執行 `python -B tools/archive_verify.py --archive controls/controls.tar.xz --index controls/controls-index.json --out NEW_CONTROL_TREE`；輸出須全新、父目錄由執行者擁有且非群組/其他人可寫。依封包 ARCHIVE-SCOPE.json 重播。normal/-O 每模式 aggregate 26、descriptor/flag 30、archive 65、PNG 10 控制全過；本件 postflight 政策另有24項 fresh控制。每一模型模式還有12通用fixture/30子執行、2,736精確predicate、36個AABB暴力比對與48相交子程序控制。既有工具中的舊專案標籤只是通用程式/封包layout名稱，沒有繼承其他模型結果。

`python -B tools/run_full_qa.py --stl ../models/v11/model.stl --expected-sha256 fa05503ab8ea54036a9312d4a2d263545c7b01bd61bbe07108558b4ea5974db6 --expected-longest-mm 200 --out NEW_QA` 可重做數值檢查；因原9旗標，預期原 aggregate 返回非零且 strict false。每模式再用 `tools/diagnose_recorded_cpp_rays.py`，傳入該模式的原STL、原dense報告、flags、raw報告與intersections報告，對完整9原runhex作精確補證，不能刪旗標或將原 strict 改成 true。

## 範圍與限制

這是建築師 2001 年原作完工早期外觀的來源受限模型，照片拍攝期未詳，並非 2026 現況測繪。北短翼未知面保持簡化；軸向、層高與尺寸為比例估計。外窗、拱圈、根部與支柱有明列製造加厚/圓角，非實物厚度；挑檐與平台等仍可能需支撐。有限切層/射線及exact旗標補證不證明所有方向最小厚度、強度、切片策略或實際可印性。原照、歷史失敗、私路徑與完整執行log不公開；正式來源審核另見 [source-appearance](source-appearance/SOURCE-APPEARANCE-REVIEW.md)。
