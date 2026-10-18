# 壓縮 BLEND 路徑修正：獨立唯讀覆核

本目錄支援固定 `6e683682473c2d1dbdf221b47270e0c909bd6eb0` 原場景至新場景的最小 metadata 修正。結論為 **獨立覆核通過**：每件只改 `FileSelectParams.dir[1282]` 的 42 個解碼 bytes；兩件各一個原私人主機目錄，修正後為 `//` 加 NUL 填滿。這是檔案選擇／保存對話框歷史，不是 GLOB filename，也不是模型幾何。

初版 13 項 true 與 Library v2 回條保留歷史原貌。其 raw-byte／文字／PNG scanner 沒有解碼壓縮 BLEND 內層，故漏掉兩處；這次明確記錄 **before binary scan=false／2 findings，after=true／0**，沒有硬改舊 passed。

## 證據

- [總 byte／原檔綁定檢查](independent-summary.json)：old bytes 直接由固定 Git blob 讀取，沒有使用當時已被新檔覆蓋的 repo 檔案作 old。
- [v1](v1-independent-byte-review.json)、[v2](v2-independent-byte-review.json)：獨立 BHead32 walk 及 SDNA NAME／TYPE／TLEN／STRC 解析；各欄位大小總和與 struct TLEN 完全相符，再導出 dir offset 176332、capacity1282、struct2280、SDNA849。所有其他解碼 bytes 完全相同。
- 手動解析 zstd frame descriptor、三 byte block headers，核對三個 data frame 與末尾 seek table。未改 data frames 的原壓縮 bytes 完全相同；只重壓包含 dir 的 data frame，seek entries 對應新壓縮長度，解碼邊界相同。沒有宣稱重現未知的原壓縮等級。
- [獨立 bpy 語義比較](independent-semantic-comparison-corrected.json)：原、新 SHA 各自守門且彼此不同；四個實際載入對應 v1 old/new、v2 old/new，未 save／render。物件、mesh 座標／拓樸、camera、light、材質、world、render及外部依賴等十類一致。
- [目前交付檔案獨立檢查](current-artifact-check.json)：只需現有兩個 BLEND 與 redaction manifest，**不需要 Git、私人原件或 bpy**；獨立解析全部 frame／seek entries、SDNA dir 與 GLOB，核對固定 SHA 及解碼 privacy scan。
- [既有檔案／索引範圍](tracked-scope-check.json)：原 395 個模型檔只有聲明的六個 metadata／說明／歷史 guard 路徑可變，其餘與八個發布索引保持；歷史 13-true 報告逐位元保留。

## 保留的失敗與修正

初次獨立語義 signature 包含 `ID.session_uid`，導致每件 37 個 runtime ID 差異；該 [false 報告](invalid-attempt/semantic-with-session-uids.json) 與當時 [checker](invalid-attempt/check_semantics_with_session_uid.py) 均保留。逐 leaf 比較只有 session_uid 不同，修正版只增加此 runtime 欄位的明示排除。另以**同一份 SHA 固定的 old v2 連續 open_mainfile 兩次**為控制：37 個 session UID 改變，而全部其餘 signature data 一致。RNA 原說明及實際控制數字都在修正報告，不把舊 false 改為 true。

最初 sandbox DLL loader 無法載入 bpy，沒有讀取場景；之後透過獲允許的唯讀重跑完成實際比較。亦保留原判定流程的環境／開發失敗摘要，不在公開證據內放入原始絕對路徑載入 trace。作者另外的 new-vs-new semantic attempt 不能作等效證據；本獨立 old/new SHA 守門與固定 Git byte 比較避免此混淆。

## 重做

Python 3.13 與 zstandard0.24.0 可在下載的目前 artifact 執行：

```text
python check_current_scene_paths.py --package-root MODEL_ROOT --output FRESH_REPORT_JSON
```

預設 manifest 是模型根下 `qa/scene-path-redaction-1/redaction-manifest.json`，亦可明示 `--manifest`。只讀取現有場景與 manifest，輸出不得覆寫。

有保留 Git 物件的 clone 可用 `scene_path_independent_driver.py --repo REPO_ROOT --package-root MODEL_ROOT --staging NEW_ROOT --output FRESH_DIRECTORY` 重做原／新 exact byte 與 frame 比較；NEW_ROOT 需有模型相對兩場景與 `manifest.json`。`check_semantics_readonly.py` 另外需要 bpy5.2.2及獨立舊、新根；兩者有固定 SHA 守門。原 BLEND 含私人目錄，不放入 Library；需要重做舊場景 API 比較時，從固定 Git blob 在本機私人暫存區建立唯讀副本。

所有工具及報告都沒有改寫 repo、Git、場景、幾何、STL、G-code、PNG或參數，也未重渲染／切片；metadata修正不構成新的實體列印、支撐拆除或膠合驗證。
