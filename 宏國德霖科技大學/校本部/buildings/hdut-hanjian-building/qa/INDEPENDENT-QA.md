# 宏國德霖科技大學罕見樓 v14：獨立數位檢查

## 結論與身份

本件在下列有限數位檢查範圍內通過獨立覆核；原數值程式的 `strict_passed=false` 完整保留。這不是零 flag、連續全域壁厚證明、結構認證或實體試印通過。尚未試印。

- STL SHA-256：`bcfb73e933ef1f590246cfd05f6480b2a5c0d4d4d9e4e878b25bec965393002b`
- 原 Blend SHA-256：`43b53624de7bb72b35fb4e7a54ca0b83a62611799839cc9845a24fb9983bf62f`
- 作者原凍結清單 SHA-256：`e362cef388c9562016f7421accf41ce43b50897a34802f69567e829ee28c52a1`，共 771 檔。
- 獨立 runner 只轉換凍結清單的資料排列，771 個原成員的路徑、大小與 hash 不變，並額外凍結原清單本身，共 772 檔。映射證明見 `independent/original-freeze-adapter-binding.json`。
- 原始 9,266 三角面，單一表面；外包尺寸約 222.5 × 125 × 114.9000015 mm。名義 1:400，含 2.4 mm 整合基座，混合公布設計值、明示估計與製造調整。

作者正式幾何結果仍使用 v12 路徑；v14 的 STL 與其逐 byte 相同，綁定見 `V14-SAME-STL-BINDING.json`。作者與隔離的首次獨立結果分別保存。獨立檢查以一般 Python、`-O` 各自執行，沒有把作者結果當作本件獨立執行，也沒有修補或重新網格化 STL。

## 原網格與有限厚度篩查

1. 原 STL 拓樸、存儲法線、單一封閉表面及尺寸檢查通過。原座標相等定義連接；沒有四捨五入、焊接、刪面或修法線。
2. 原面閉 AABB 廣相完整涵蓋 113,319 對候選，包含鄰面與共面；有理數精確相交得到 72,499 對允許接觸，0 壞對。完整接觸記錄隨附。
3. XY 切層間距 0.2 mm，三組偏移為 0.031、0.071、0.137 mm，共 1,724 層、11,462 個原 Polygon。每個 Polygon 個別接受半徑 0.4 mm 侵蝕與開運算，不以全層平均掩蓋窄根；0 消失、0 分裂、0 失敗。最大個別面積損失 0.00759308194969616，低於 0.01 門檻。沒有修輪廓、挪層位或忽略小構件。
4. 每個原三角面 10 條原法線射線，共 92,660 條。最短數值首弦 1.2263002399762626 mm，0 條小於 0.8 mm。每模式仍有 3 個原數值 flag，見下一節。

兩模式完整原 CSV、flags、shorts、切層細節、接觸與精確事件皆保留，壓縮只用無損 XZ/GZIP。作者與獨立的 28 項科學檔案比較見 `independent/author-independent-science-comparison.json`；執行時間與其報告 hash 引用的差異明列，沒有改寫原輸出。

## 三個原 flag 的精確補證

以零起算 face/sample：9020/0、9059/0、5416/2。三者都有原 crossing 進出不交替與原三角 parity 控制失敗；前兩者另有近重合或反向 crossing。原 flag 清單、完整數值事件及 aggregate 的 `strict_passed=false` 不變。

補證逐條核對各次原 CSV 全部 92,660 列，直接取其 lossless hexfloat 點、法線、起點與方向，用同一實際原射線做有理數精確分類。沒有改成理想線、重新生成 descriptor、移動樣本或引用他件豁免。全部原面精確事件及每個開區間的 inside/outside/boundary 分類和見證都公開；boundary 區間沒有被當成實體內部。

9020/0 與 9059/0 的首段實體弦長平方均為
`19537597487503616962665508907351559451973567643649/51380916937414555718098294900181824909778878464` mm²，弦長約 19.500001907348633 mm。5416/2 的首段實體弦長平方恰為 9 mm²，即 3 mm。各自均以精確平方比較符合 0.8 mm 門檻。

這是對固定 STL hash、兩次原始執行、全部三個實際 flagged 樣本的有限補證。`independent/QA-RESULT.json` 的 bounded 通過與原 strict=false 同時存在，不代表原數值檢查全部嚴格通過。有限法線射線及有限切層仍不能證明任意位置、方向的全域最小壁厚。

## 原碼、場景與九張預覽

原碼重建 STL 與 color-regions JSON 均逐 byte 相等。由原 renderer 建立、儲存後重新開啟的場景，和原 Blend 的本件使用狀態集相等，包括純量 RNA、網格／各面材質指定、socket／連線、Noise texture/color mapping 及內建色帶、相機、渲染、可見性與集合。這不是任意 Blender RNA 全狀態序列化的宣稱。記憶體初建與儲存重開之間的 runtime 差異另有原報告；兩個已儲存場景的比較未忽略不同欄位。

v14 將所有原面頂點都納入材質區域判定，中性實牆統一色，避免質心判定或共面三角材質分區造成假斜線。獨立來源重建保留這個實際規則。原 Blend 與原 STL 的有向世界座標三角形精確相等，各視角也再次檢查；只有一個建築 mesh，沒有 modifier、隱藏替代幾何、外部照片貼材或圖像材質。

獨立覆核從同一原 Blend 每視圖只重渲一次，共 front、rear、west、east、south、north、top、courtyard-gallery、courtyard-arcade 九圖。七張外部視圖固定 ORTHO／50 mm，兩張院內視圖固定 PERSP／20 mm；每張相機位置、目標及 projection/lens 必須與凍結 manifest 及源碼 camera_specs 一致，不接受任意相機。

使用 Blender 4.3.2、Cycles CPU、64 samples、單執行緒、固定 seed、1000 × 780、關閉降噪。九圖解碼 RGBA 與所有保留 metadata 相同。公開 PNG 只移除工具白名單內的 File／時間文字，原 IDAT、RGBA、色彩 chunks 不變，清理前後 hash 逐張綁定。原 raw PNG 及 routine 日誌私存；公開 raw hash 不表示 raw 檔有公開。

來源覆核對同一最終 STL／Blend／九張原圖逐一 GO，再與獨立清理後九圖綁定。見 `source-appearance/PUBLIC-SOURCE-REVIEW.md`、`independent/source-appearance-binding.json`、`preview-binding/`。

## 工具與控制

沿用最新已驗證工具，不改原幾何、相交、射線、切層、PNG 核心或 Noise mapping 狀態比較。28 檔中 23 檔逐 byte 不變；5 個展示相關檔只窄適配本件九視圖名、兩種固定 projection/lens policy、來源 camera_specs 和公開 manifest 欄位保留。原碼、before、diff、hash 與固定工具清單隨附。

一般／`-O` 各有 aggregate 26、原 descriptor/flag 30、archive 65、PNG 10、Noise mapping 32、九視圖 batch manifest 34、最終場景 policy 12、固定案例後檢 24 項控制。幾何正負例及相交廣相對照另有完整結構化輸入／輸出。缺／多視圖、projection/lens 變造、非正面相機位置變造、材質與 render 設定變造均應被拒絕。固定案例政策測試不代替真幾何執行；場景控制不額外重渲圖片。

所有 fresh 與正式作者／獨立 run 的合成控制集中於 `controls/controls.tar.xz`，含逐成員 index 和精確原路徑映射。安全驗證／解包／逐 byte 重建均經一般與 `-O` 驗證。刻意損壞的壓縮拒絕 fixture 保留原 bytes；symlink 提取負例不跟隨，保留描述與生成方式。routine stdout/stderr 只在省略 ledger 記錄私人原檔 hash。

## 歷史與製造限制

表示 2016 完成、2017-09-17 照片約束的主體完成外觀，採最終方案 C，不混用提案 A/B、2018 景觀改善、2020 室內裝修或年代未定的屋頂 PV；不是 2026 現況調查。

81.90 m 與 20.30 m 是局部結構軸距，不是 footprint；45.4 m 的公布測高基準未定，未硬湊成模型最高點。西背面與南側遮蔽部位低細節／保守封閉，是明示未知，不表示真建物沒有窗。庭院、穿廊保留開放；樓梯、池橋與景觀等有明示省略。沒有竣工測繪精度的承諾。

細欄、板、柱、接合有製造粗化，尖角與端部接合曾在原 CSG 中調整；失敗舊版保留，正式原 STL 沒有事後修復。玻璃為有厚度實體，渲染色彩不保證普通單材實物透明。前橋廊、深廊、陽台與高框大跨需支撐及後處理，支撐可達性、內部清除、樹脂排液、收縮與強度未實測。未試印，也不保證切片成功或任一設備可印。

完整界線另見根目錄 `ESTIMATES-AND-SIMPLIFICATIONS.md`、`PRINTING-LIMITS.md`、`REPRODUCE.md`。來源照片、PDF、正射影像不公開。私人路徑／token pattern 掃描有明列範圍，場景可保留通用 `/tmp/` 渲染預設或已判定低風險的通用 UI 欄位，不宣稱零路徑或一般秘密偵測保證。
