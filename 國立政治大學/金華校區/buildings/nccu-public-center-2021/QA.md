# 驗證範圍與狀態

本件採用的原始 binary STL SHA256：
`8ad969e0135c2dfcd505cc85a1a79b78c9982cac3f8b9fe6f0525de9a34a367e`

獨立審閱已完成，並接受下述四條原射線共面邊界個案的限定例外。原始 strict=false 與完整入口非零退出保持不變；不能寫成「全部通過」或「保證能印」。完整倉庫中的[獨立稽核摘要](../../../inventory/qa/nccu-public-center-2021-review.md)保存結論、受審版本與限制。

原正式完整候選僅由原受審 217 檔候選更新文件狀態及機械雜湊綁定；本精簡配送另調整外層驗證入口及明列唯一外置的完整密集診斷 CSV。原科學檢查器、模型、圖像及所有保留的數值證據不變。原受審 freeze-manifest SHA256 為 `2ed92764046c592ba9a0c2f91ca6a329dd46257a45ff8c512fb7154b8af58df2`；該完整候選的模型、七張預覽、程式及數值證據不變，原 strict=false 也不改寫成 true。精簡版的程式差異僅限明列的外層重建／配送／彙總流程，科學計算程式仍以原 hash 硬釘。

## 原始幾何

- 30,186 個原始有向三角面，15,087 個精確座標頂點，45,279 條邊。
- 每條邊恰有兩面，方向一致；每個頂點 link 為單一 cycle。只有一個封閉表面，沒有內部獨立殼。
- 原始有向體積約 925,945.889 mm³，為正；完整外包 150 × 130 × 126.868088 mm。
- 直接讀取 little-endian float32 STL，不 repair、不 weld 容差、不座標取整、不補面、不刪面。共同頂點僅用完全相同座標索引。
- 自交門以可一一還原的 dyadic 整數格與精確有理數運算檢查全部閉 AABB 候選。共頂／共邊面也不跳過；只容許交集精確等於原共享點或整條原共享邊，其他接觸、穿插或共面面積重疊拒絕。細面不過濾。

## 0.2 mm 切層與 0.8 mm 開運算

三個起始 offset 為 0.031、0.071、0.137 mm，共 1,903 層及 4,338 個原始 Polygon。每個 Polygon 含洞資訊獨立檢查，沒有全層平均豁免。

原切片有效，半徑 0.4 mm 侵蝕與開運算有效，無消失、無分裂。最大個別面積損失為 0.9495046763%，低於 1%。完整逐層、逐 Polygon 資料及原始面索引在 qa/sections。

這是三個有限 XY 切層排程，不是全方向最薄壁或真實切片工具路徑的證明。

## 原面法向十點檢查

每個原始三角面取固定十組 barycentric 權重，共 301,860 個樣本，沿原面法向測原始 mesh 的材料／空氣區間。完整 CSV 在已審完整包無損保留；本精簡配送只外置這一個可再生完整診斷檔，gzip 與解壓 SHA256 均保留。全部四旗標原始 rows、短弦／失敗檔與逐點補證仍隨包配送。

- 小於 0.8 mm 的原法向短弦：0。
- 最小第一材料弦長：約 0.919886514 mm。
- 四個共面邊界旗標仍存在；`strict_passed=false` 保留，沒有改法向、平移射線或放鬆門檻。
- 根部修正是源設計的連續實體增厚：南端斜窗後緣深入牆體，玻璃淺凹縮短，保留西向可見玻璃、斜石材翼與頂面。沒有用平均損失掩蓋局部薄片。

共面旗標不是單憑「看起來夠厚」就豁免。逐點診斷須以原射線對全部原三角面精確重算 transverse 交點與共面邊界區間，分開列材料、表面邊界及空氣，並核原 CSV 完備性。qa/boundaries/ray-boundary-evidence.json 保存四點的完整診斷；diagnose_boundaries.py 可重跑。check_root_repairs.py 使用 root-repair-fixtures.json 重查先前 20 條原射線，證明連續根部已實際修厚；這項歷史對照不取代當前全模型十點檢查。其診斷不會覆寫 strict=false。限定接受只適用於本頁所列 STL 的原面 10272、17099、17100、17101，各 sample 0；不適用於任何新射線、修改後幾何、未採樣位置或其他短弦。四點補證與獨立遍歷一致，接受的是明列邊界個案，不是放鬆 0.8 mm 根部門檻或全域厚度豁免。

因此完整 `python -B run_checks.py --out ../nccu-public-center-full-replay` 仍以非零狀態結束，並在外部資料夾保存完整 CSV、新報告及當次有序 stages。`validate_model.py --integrity-only` 仍須指定精確完整 CSV，只供全證據綁定負控制；新 `--delivery-only` 只驗配送，絕非列印通過入口。

## 原始 STL、Blend 與預覽

scene.blend 只有一件建築 mesh，頂點及有向原三角面與 STL 完全相同，沒有 modifier、隱藏替代模型、文字／曲線幾何、parent transform、集合實例、貼圖或內嵌來源圖。保存後重開核對，並掃描外部資源、packed data、自訂屬性與檔案瀏覽器路徑。

隔離資料夾重新執行 build_model.py，要求 STL、材質區資料及 build report byte-identical；再用 Blender 重建七個預覽，要求 PNG bytes 一致。Blend 容器可能有序列化差異，因此比對的是原有向面而非聲稱 Blend 檔案必須 byte-identical。

PNG 驗證實際解碼、各 chunk CRC、固定非文字 chunk 白名單，無文字／EXIF 路徑中繼資料。

## 可重跑入口與負控制

完整入口：`python -B run_checks.py`。Python 以 `-O` 啟動時，子 Python 檢查保留 `-B -O`；必要條件不用 assert。Blender 必須使用 `--python-exit-code 1`，另以刻意 Python 例外證明非零退出。

- 原 topology、切層、dense 工具用正常 box 與缺面、重面、反向面、分離殼、內殼、頂點觸碰、薄根、薄板、小島及破損 binary 等控制，兩種 Python 模式合計 30 次。
- 精確自交控制含共面重疊、非共面穿插、共享點但交叉、共享邊但重疊、極瘦面、近而不交、斜向幾何及頂點順序置換，並以 brute-force 交叉檢查 broad phase。
- 彙總負控制在隔離副本改 README、PNG、checker、STL、報告，加入內層同名排除檔、gzip 私人路徑及 PNG 文字 metadata；要求具名失敗原因與非零退出。
- 控制的合成 STL 由原碼在臨時資料夾重建；公開包只有一個建築 STL，保存控制 JSON／壓縮證據與完整重建原碼。

所有當前 README、PNG、checker、參數、來源、報告及壓縮證據需重新做內容雜湊綁定，不能只讀舊 passed JSON。freeze manifest 與 SHA256SUMS 再覆蓋完整白名單負載；不把原始來源圖、私人研究板、操作筆記或 bytecode 打進公開候選。

尚未實體試印。建築尺寸是來源比例近似，有限數值檢查不是測繪精度保證，也不是無支撐列印保證。

## 精簡配送新增外層門

- compact-cache.json 明列唯一外置檔與兩種 SHA、大小、原 STL、原七個科學檢查器及 dense 報告的受審身份。reference/full-release 保留原已審 manifest／validation 的原 bytes。
- replay_dense_cache.py 先核硬釘原 manifest 與輸入身份；在隔離目錄調用未改的科學 checker。只在預期 exit 1、完整報告欄位及四旗標／short 證據、gzip／解壓雙 hash 全精確相符後原子輸出。編譯器 binary hash 可另記平台差異，但不能豁免任一 CSV hash 或科學值。
- validate_model 預設完整模式缺／錯 CSV 都具名非零，full_evidence_verified=false。delivery-only 可獨立返回配送完整，但 full_evidence_verified/current_science_replayed 均為 false；既有舊 passed 檔不會被當成本次完成。
- 完整 run_checks 在新外部目錄逐門重跑並保存 current-run.json。它核對精確新 CSV、全部必需階段順序、各階段實際退出碼及新寫出的報告；只有完整到達已定義的四旗標嚴格失敗狀態，才記 current_science_replayed=true。該欄位表示已重跑，不是 strict pass。
- 新負控制涵蓋缺／錯完整 CSV、偽 metadata 重綁、假舊成功報告與未找到編譯器的無關 exit 1；全都必須拒絕。原九個配送／隱私／stale evidence 控制也保留。
- 只省去大型再生資料的配送；逐 Polygon、全原面 pair、四旗標原 rows、原短弦／失敗證據與全部原科學碼不移除。完整診斷檔可用 README 單一公開命令獨立重建，不依賴私人儲存或登入。
