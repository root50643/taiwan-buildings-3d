# 臺北市立大學天母體育館 A 棟：獨立 QA

結論：本件最終 v6 的 normal 與 Python -O 原網格檢查均 strict pass；兩模式科學證據一致，作者與獨立執行的完整同模式數值檔亦逐 byte 一致；精確相交報告只差執行耗時，兩份原報告均完整保留。這是有界幾何驗證，尚未實際試印。

STL SHA-256：`f93ed0ab95e13707d390f480174f63e31086b48041fc7a7a873975cad8892a8c`

## 已實際確認

- 原始 24,112 面，210 × 152 × 63.799999237 mm，單一外表面；原法線、面向、邊與頂點連結全過。
- 297,696 對精確閉 AABB 候選全部完成，含鄰面與共面；不允許交集 0 對。完整 181,078 筆允許接觸事件保留。
- 每模式 241,120 條原面射線，低於 0.8 mm 的弦 0、數值旗標 0，最短首段實心弦 0.901097603 mm。完整原 run 十六進位描述保留；每模式 2,893,440 個描述值經重算驗證。
- 三組固定偏移的 0.2 mm XY 切層，共 957 層、957 個原 Polygon；逐 Polygon 失敗 0，最大 opening 損失 0.085328%。
- 原始 source 重建 STL 與 color-regions 逐 byte 一致；兩份 saved Blend 重新載入後完整場景狀態相同，九個相機定義一致。
- 原 saved Blend 的 evaluated world 有向三角形多重集合逐面吻合 STL；九個視角各自再檢查幾何。CPU、單執行緒、64 samples、seed 0、無 denoising，沒有照片貼圖或替代網格。
- 九張獨立重渲圖的解碼 RGBA 與所有保留 metadata 一致。公開 PNG 只刪明列非視覺文字欄；IDAT、保留 chunk 與 CRC 原 byte 不動。原始 PNG 全檔 bytes 不作可重現承諾。

## 證據與重播

- 作者完整科學證據：[final-v6/full-qa-summary.json](final-v6/full-qa-summary.json)
- 獨立總結：[independent/QA-RESULT.json](independent/QA-RESULT.json)
- 獨立 normal / optimized：[independent/geometry/](independent/geometry/)
- 場景與九圖：[independent/source-scene-audit.json](independent/source-scene-audit.json)、[independent/blend-rerender-audit.json](independent/blend-rerender-audit.json)
- 完整科學 producer JSON、CSV、逐 Polygon 詳情與精確事件均保留原 byte；公開複製清單見 [PUBLICATION-BINDING.json](PUBLICATION-BINDING.json)。
- 完整最終 synthetic 證據壓在 [controls/controls.tar.xz](controls/controls.tar.xz)，搭配 [controls/controls-index.json](controls/controls-index.json)，不把數千 fixture 散放。封包已在 normal/-O 驗證，安全解包，兩模式重建 bytes 一致。

在 qa 目錄執行 `python -B tools/archive_verify.py --archive controls/controls.tar.xz --index controls/controls-index.json --out NEW_CONTROL_TREE`，輸出路徑須全新且父目錄由使用者擁有、非群組或其他人可寫。其後可依封包的 ARCHIVE-SCOPE.json 重播工具正負控制；解包樹保留作者 final-v6 與獨立 independent/geometry 的完整 run controls。聚合、CSV旗標、封包、PNG 每模式分別 26、30、65、10 項皆過。各模型模式另含 12 個通用 fixture／30 次 gate 子執行，以及 2,736 個精確 predicate、36 個 AABB 暴力比對與48個相交子程序控制。

## 必須保留的限制

有限原法線射線與三組切層不證明全方向最小厚度、材料強度、實際噴嘴路徑、免支撐或實物可列印性。尚未實際試印；縮放、空心化或改形後須重新驗證。

建築總尺寸、曲率與部分比例為來源約束估計；北面樹後、遠端與完整波形仍未知。窗框加厚、外梯護牆延伸、帽角抬高與底面截平、粉檐平端和局部降低均為明列製造修形，不是實測構造。來源外觀結論與逐項限制另見同包來源審核。原照片、PPT、PDF及歷輪失敗證據留在私人研究資料，不公開。
