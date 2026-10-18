# CSU 54c4：純文字與語義增量覆核

唯讀確認 HEAD 為 `54c4ad2a30e6600e85fbf054d4c384f9e5304748`。本次直接比較 `76681c5dcedc88d684946780e795d7914a88c075` → `54c4ad2a30e6600e85fbf054d4c384f9e5304748` 的實際 Git diff，並讀現用 README、QA、parameters、QA-NOTES、工具說明、文件勘誤及獨立證據匯入 README。只寫本報告；未重作來源研究、渲染、幾何／G-code QA、Library 下載或推送。

**結論：文書增量 GO，未見尚待修正的必修發布阻擋。** 原 76681 所指出的門凹／參數聲明問題已在現用入口與參數修正，歷史必修原文及舊 SHA 的時點亦有清楚界線。不需為消除搜尋命中的舊字句而覆寫歷史報告、旗標或擴大模型變更。

## 逐項確認

| 項目 | 本次文字／語義判斷 |
|---|---|
| 門凹深度 | README、QA、QA-NOTES 與勘誤入口均區分普通窗名義約 0.4 mm、入口名義約 0.65 mm、raw STL 實測 0.650001526 mm。parameters 的 `entrance.door_recess_depth` 與 `manufacturing.maximum_shallow_facade_recess` 已由 0.45 改為 0.65。與門凹深度相關的舊 0.45 均是在描述原錯誤或歷史設定，沒有繼續把所有凹面說成最深 0.45 mm。 |
| 深度不是壁厚 | 門背約 46.55 mm 限定為同線連續材料；文字沒有把 0.65 mm 凹深當薄牆，亦沒有據此宣稱全域厚度。參數 `wall_limit` 另明示 minimum_design_wall 是設計聲明，實心屋簷仍收尖；QA 保留 71 條屋緣短弦與有限取樣界線。 |
| 16.6 mm 路徑 | 現用多個入口列出實際起訖 `(-8.3,-28.975,20.2)` → `(8.3,-28.975,20.2)`、16.6 mm、WIDTH 0.4／HEIGHT 0.4。明示凹深、0.650002 mm 投影寬、面積包絡及 Bridge infill=0 都不能代替路徑或橋接／懸垂評估；沒有把這整條路徑直接說成已驗證的無支撐橋跨。 |
| 真實支撐與去除 | 20,930 支撐＋61,223 介面＝82,153 段與 7,273.39394 mm 耗絲一致；段數非塊數，實際寬／高並非全固定。門區 305 段／45 strata、名義 0.2 mm gap 沒有被說成黏連、成形、去除力或清除已成功。有限小片掃掠不等於完整連架可剪分、工具可達或表面無損。 |
| 參數語義 | `parameter_semantics` 明列控制欄位與 `entrance.door_recess_depth`、`parapet.inset`、`relief.*`、`manufacturing.*` 等聲明欄位。README 與勘誤說明固定座標仍在源碼，修改聲明不會直接改幾何，不宣稱全拘束自由參數模型。此語義與既有生成器讀取方式相容。 |
| 試印與接合 | NOT-MACHINE-READY、真機重切、100% rectilinear 僅為 QA、未試印／拆支撐／brim 清除／尖屋緣成形／膠合強度等限制保留。四邊名義外伸 4 mm 不再暗示 ±4 mm 偏移；`|Δx|+|Δy|≤1 mm` 限定無旋轉、頂台全覆蓋的純幾何條件，並非製造公差。 |

## 歷史報告、SHA 與工具的時點界線

- README 與 `qa/documentation-revision-1/README.md` 把原 build/render manifest、visual-source-review 和原 QA 限定為 76681 固定輸入；原參數另有快照，新參數另由增量校驗綁定。沒有聲稱舊 manifest 曾執行新參數。
- 原 16 張 PNG 的檔案 SHA 因私人 ancillary `File` metadata 清除而改變；入口明示原 manifest 不改、原／新 SHA 由映射銜接。匯入獨立 PNG 的路徑遮蔽亦另有來源／交付映射。其 IDAT、解碼像素及檔案 SHA 的獨立驗證由主責覆核處理，本子覆核只檢查這些說明不混淆歷史與現用身分。
- `qa/independent-76681/INDEPENDENT-CSU-REVIEW.zh-TW.md` 首段固定提交為 76681；匯入 README 明示它不是後續文件或新 HEAD 的整包重審。原「門凹聲明必修」是對當時 0.45 錯誤的判定，現用 README／QA／勘誤已同步修正。兩者在這個脈絡下不矛盾，不需要改原判定或冒稱原審已核新 HEAD。
- `source/qa/README.md`、`source/QA-TOOLING-NOTES.md` 與文件勘誤入口明示舊 snapshot 的 `run_slice.py` 固定 no-support limits／舊 audit docstring 對 auto45 不正確。正式交接指向 corrected audit 及現用說明；不把舊錯句當免支撐證據。
- 實際 diff 中，現用 `source/qa_audit_gcode.py` 僅改 docstring 為按 embedded config 判讀；歷史版另存，舊 corrected audit 綁舊 SHA。文書沒有假稱當時執行過修後 docstring。其去 docstring AST 校驗屬主責的增量驗證，不由本子覆核重跑。
- 匯入 README 將舊 finalizer／identity helper 明示為歷史流程來源，另給新 `reproduce.py` 入口及新輸出規則；沒有把匯入後套件誤稱仍等於舊 337 檔 snapshot。

舊 0.45、no-support 與原必修字句已被標示為歷史／錯誤保留；嚴格 false、六條歧義、71 條真薄尖緣與全部原失敗未被改為通過。未發現需要新增幾何、更換參數策略、重切片或重渲染才能解決的文字問題。

本結論僅確認上述固定差異的文件一致與語義，沿用原有製造條件；它不解除未知真機、去支撐、尖邊、膠合或實印限制。Library v1 作者回條及其固定身分由主責核對，本子覆核未重下載或另宣稱驗收成功。
