# 高雄醫學大學圖書二館 v5：獨立數位檢查

## 結論與身份

本件在明列的有限數位檢查範圍內通過獨立覆核；原數值程式的 `strict_passed=false` 完整保留。這不是零 flag、連續全域壁厚證明、結構認證或實體試印通過。未試印。

- STL SHA-256：`276fb42c47b0152feb14f9c7851413ea18fa6be20fd86ed73669ddabef69dd7d`
- 原 Blend SHA-256：`133bd65f7bf38ad4f46311feb2463c4e4d23792b7b028e002282a8108c6fb555`
- 作者凍結清單 SHA-256：`936a31f1f65ef3f2a1e8dc688f0f4b5ce4dc51d0aecb2380e0c7726d2364a04c`，共 830 檔。
- 原始 23,920 三角面，單一表面；外包尺寸約 122 × 135 × 102.4 mm。名義 1:200，尺寸與樓高有來源估計及製造調整。

作者正式結果與隔離的首次獨立結果分別保留。獨立幾何檢查以一般 Python、`-O` 各自執行，沒有沿用作者結果作為本件通過證據，也沒有修補或重新網格化 STL。

## 原網格與有限厚度篩查

1. 原 STL 拓樸、法線、單一封閉表面及尺寸檢查通過。
2. 原面閉 AABB 廣相完整涵蓋 385,351 對候選，包含鄰面與共面，精確相交記錄 197,917 對允許接觸，0 壞對。完整接觸記錄隨附。
3. XY 切層間距 0.2 mm，三組偏移為 0.031、0.071、0.137 mm，共 1,536 層及 12,350 個原 Polygon。每個 Polygon 個別接受半徑 0.4 mm 侵蝕與開運算，不以全層平均掩蓋窄根；0 消失、0 分裂、0 失敗。最大個別面積損失 0.0073103339926951704，低於 0.01 門檻。未修輪廓、挪層位或忽略小構件。
4. 每個原三角面 10 條原法線射線，共 239,200 條。最短數值首弦 1.1173969793855305 mm，0 條小於 0.8 mm。每模式仍有 1 個原數值 flag，見下一節。

兩模式完整原 CSV、flags、shorts、切層細節、接觸與精確事件細節皆保留，壓縮只用無損 XZ/GZIP。作者與獨立的 28 項科學檔案比較結果見 `independent/author-independent-science-comparison.json`；執行時間與其報告 hash 引用的差異明列，沒有改寫任何原輸出。

## 唯一原 flag 的精確補證

每模式的原 face 3872 / sample 0 有 `original_crossings_not_alternating_enter_exit`。數值程式記錄 6 個交點，其原結果及原 aggregate 的 `strict_passed=false` 不變。

補證逐條核對該次原 CSV 的 239,200 列與 lossless hexfloat 點、法線、起點、方向，再以同一實際原射線做有理數精確分類。尤其原 `x_hex=0xe.000000000000001p-1` 保持原值，沒有換成理想的 x=7、重建另一射線、移動樣本或引用他件豁免。精確原三角接觸有 4 個，全部開區間的 inside/outside 分類與見證均公開；首段實體弦長平方恰為 `7569/16` mm²，即 21.75 mm，符合 0.8 mm 門檻。

這是對這個 hash、這兩次原始執行、這一個實際 flagged 樣本的有限補證。`independent/QA-RESULT.json` 的 bounded 通過與原 strict=false 同時存在；不得把它讀成原數值檢查全部嚴格通過。

## 原碼、場景與九張預覽

原碼重建 STL 與 color-regions JSON 均逐 byte 相等。由原 renderer 建立並儲存後重新開啟的場景，和原 Blend 的本件使用狀態集相等：純量 RNA、網格／材質指定、socket／連線、Noise texture/color mapping 及內建色帶、攝影機、渲染、可見性與集合。不是任意 Blender RNA 全狀態序列化的宣稱。記憶體初建與儲存重開之間的 Blender runtime 差異另有原報告；原始與重建兩個已儲存場景的比較沒有忽略不同欄位。

原 Blend 與 STL 的有向世界座標三角形精確相等；各視角也再次檢查。只有一個建築 mesh，無 modifier、隱藏替代幾何、外部照片貼材或圖像材質。

獨立覆核從同一原 Blend 每視圖只重渲一次，共 front、rear、west、east、south、north、top、entry-detail、roof-detail 九圖；Blender 4.3.2、Cycles CPU、64 samples、單執行緒、固定 seed、1000 × 780、關閉降噪。九圖解碼 RGBA 與所有保留 metadata 相同。公開 PNG 只移除工具白名單內的 File／時間文字，原 IDAT、RGBA、色彩 chunks 不變，清理前後 hash 逐張綁定。原 raw PNG 及 routine 日誌私存；公開原 raw hash 不表示原 raw 檔有公開。

來源覆核對同一最終 STL／Blend／九張原圖逐一 GO，再與獨立清理後九圖綁定。參見 `source-appearance/PUBLIC-SOURCE-REVIEW.md`、`independent/source-appearance-binding.json` 與 `preview-binding/`。

## 工具與控制

沿用已驗證工具，不改原幾何／相交／射線／切層計算。凍結前僅窄補 Noise mapping 與其內建 ColorRamp 狀態比較；舊版 hash、原碼與差異保留在控制 archive。實際材質採 NoiseFac → MixRGB → BaseColor，沒有圖片。

一般／`-O` 各有 aggregate 26、原描述與 flag 30、archive 65、PNG 10、本件 mapping 32、固定案例後檢 24 項控制。幾何正負控制與相交廣相對照另附完整結構化輸入／輸出。改色、位置、插值、mapping、socket 或連線等變造必須被拒絕。固定案例後檢的政策控制不代替真幾何執行。

所有本件 fresh 與正式作者／獨立 run 所引用的合成控制，以 `controls/controls.tar.xz` 和逐成員 index 集中保存，安全驗證／解包／逐 byte 重建均經一般與 `-O` 驗證。刻意損壞的壓縮拒絕 fixture 保留原 bytes；symlink 提取負例不跟隨、只記錄描述與生成方式。routine stdout/stderr 保留私人 hash，不散佈數千個 fixture。

## 歷史與製造限制

本件表示建築師 2005 作品的早期完成外觀；來源照片確切日期未知，不是 2026 現況調查。四層主體、南高服務核、北入口與西北可見梯有來源支持。西側上層圓窗的 1+2+4 指由北往南的開口分組，不是樓層編號；低層開口簡化。東側圓窗有證但完整分組不明，南面接合也不完整，因此維持低細節。官方資料的年份／地下四層／梯一等衝突不直接轉成建築事實。

玻璃列印為有厚度的實體殼；渲染透明不能保證普通單材實物透明。內部樹狀柱與樓梯等簡化、粗化，無完整室內。屋頂、樓板、樓梯需要支撐，內部支撐清除與樹脂排液仍有製程風險；普通 FDM 可達性及強度未實測。來源不混用老館藥食園或年代不明的現代設備。來源照片、PDF、正射影像不包含在公開資料。

完整界線另見模型根目錄 `ESTIMATES-AND-SIMPLIFICATIONS.md`、`PRINTING-LIMITS.md` 和 `REPRODUCE.md`。
