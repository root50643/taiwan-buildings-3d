# 誠勤大樓候選：20 旗標來源與局部精確補證獨立覆核

分項判定：**GO；本分項無阻擋。** 本報告僅覆核原浮點旗標的來源、局部精確解釋、守門控制及文案範圍；全模型幾何、來源外觀、重建及場景／預覽由其他獨立覆核分項負責，不能由此報告推定通過。

- 固定候選提交：`4116148c135d8a67a444ce8bf33fb64aba3e06a3`。
- STL SHA-256：`4e73e7094c83de47c19bcc6121fee575c1360b285d597773d983a873f46b7f5a`。
- 原浮點 QA 報告 SHA-256：`9d7253369d81df71bdbdb40d4c0576d2452fe7eeed26d9bbf9e52c5933a94f23`。
- 輸入為父代理建立的候選副本；本分項前後逐檔雜湊相同。原候選及遠端未改動。

## 自寫獨立檢驗

`audit_flags.py` 以標準函式庫 `struct` 直接讀取 binary STL 的 2,936 個三角形紀錄，不以作者 JSON 取代座標，也不匯入作者的 exact classifier。每個 float32 座標提升成 Python float 後以 `Fraction` 原值精確表示，沒有移點、捨入、縮小旗標集合或容差門檻。

針對原報告全部 20 個唯一 face pair，另寫的檢驗計算兩個未正規化有理數法向量及所有頂點對另一平面的精確帶號值。每對均為非平行平面；在每個三角形中，所有非零帶號值同號，因此三角形與另一平面之交集正是零帶號頂點的凸包。兩邊的零頂點集都恰好等於 STL 中真正共享座標：10 對有一個共享頂點，10 對有兩個共享頂點形成同一條邊。由此獨立證明這 20 對不會在共享拓樸外相交，無需以近共面容差當作豁免。

`diagnosis.json` 及 `diagnosis-verified.json` 各 20 列逐列核對：完整原 flag（包含 kind 與原浮點交長）、原 face index、兩個三角形的實際原始 STL 座標、共享座標、輸入 STL 雜湊、原 QA 報告雜湊及分類全部一致。最終 guarded 診斷另綁定實際交付的 `flag_diagnosis.py` 雜湊。重新執行原診斷後，完整 `pairs` 陣列與候選 guarded 診斷完全相同，並未只比較 `passed` 欄位。

另外用 `verify_shared_indices.py` 重新載入 STL，確認 `process=True` 與 `process=False` 的每個三角形順序及座標完全相等；兩份診斷共 40 列的共享頂點索引及其座標也逐一與新載入網格相等，結果在 `shared-index-results.json`。此輔助載入只核對 metadata；上述精確證明仍完全來自原始 binary STL 讀取。

這個自寫證明刻意只接受上述非平行、同側／零頂點條件。其他情況會回報未證明，而不自行放寬接受。六個小控制包括合法共享邊、合法共享頂點、真正穿越、共面重疊、近共面合法邊及近共面穿越；均符合預期，真正穿越及共面重疊不會被此證明接受。

## 實際控制重跑

將作者交付的診斷及控制程式原樣執行，所有新輸出均寫入本 `flag-audit/`，不寫入候選包：

- 真正 STL／原報告的診斷 exit 0，20/20 原旗標各覆蓋一次，10 邊、10 頂點。
- 8 個分類／退化控制符合預期。
- 7 個實際 CLI 控制符合預期：合法共享邊 exit 0；錯誤輸入雜湊、空旗標、正反重複 pair、超界索引、退化 mesh 及真正穿越均 exit 1。
- 新增 6 個實際 CLI guards：同一面配對、負索引、布林索引、浮點索引、三元素 pair、非字典 flag，全部 exit 1、`invalid_flag_face_pair`、診斷 0 對，且不給成功結果。

這些是局部分類／防護控制，不是新一輪全模型幾何 QA、切片、G-code 或實體試印。

## 原始失敗與限制的保留

已實際閱讀候選的 `README.md`、`REPRODUCE.md`、`PRINTING-LIMITS.md`、`qa/README.md`、`qa/CHECKER-METHOD.md`、`qa/flag-diagnosis/README.md`、`qa/validation-events.json` 及兩支診斷／控制程式。

原 `qa-report.json` 的 `passes_numerical_pair_screen` 與 `passes_bounded_geometry_screen` 仍為 false，20 個原旗標全部保留。QA README、重建文件和事件表明示原 CLI exit 1，沒有把局部 exact 診斷取代原浮點結果；兩份診斷同時保留初始及 guarded 證據。

文件明示：只有已標出 20 對做有理數補證，其餘配對仍是浮點篩查；795 切層是 0.2 mm 中點取樣，不是連續 Z 證明；0.4 mm 侵蝕不是任意位置最小壁厚；支撐包絡不是噴嘴／橋接模擬；沒有切片器刀路、G-code、材料／冷卻／黏著／強度驗證或實體試印。沒有看到把原數值失敗改寫成全面精確或全面可列印的文案。

## 審查過程可追溯性

第一次自寫審查腳本誤以不存在的 `passes_all_checks` 欄位檢查原總 gate，導致審查摘要一項 false；真正欄位為 `passes_bounded_geometry_screen`，其值是 false，符合原失敗保留要求。已保留第一次結果 `initial-auditor-wrong-field-results.json`，更正欄名後重跑；候選資料未改。這是審查腳本的欄名錯誤，不能作為候選的失敗或已修正紀錄。

完整逐對精確帶號值、原 STL 座標、候選診斷逐列核對、候選前後檔案雜湊及控制結果在 `flag-audit-results.json`。實際 CLI 輸出在 `rerun-diagnosis.json`、`rerun-controls.json`、`guard-controls/`、各額外 guard 的 `.result.json` 及 stdout／stderr。可重現命令：

```powershell
$env:PYTHONPATH='${OPTIONAL_DEPENDENCY_DIR}'
& '${PYTHON}' -B -X utf8 .\audit_flags.py
```

本分項不要求改動候選。整體放行仍應由主覆核報告合併其他分項後，限定同一固定提交及 STL 雜湊決定。
