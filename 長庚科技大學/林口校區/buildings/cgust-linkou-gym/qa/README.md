# CGUST 林口體育館：v10 精確數位驗證資料

本目錄的結論限於此份代表性模型的數位資料。STL SHA-256 為
`66f0516f35df2df734b6d8a4d37a8f93b73e5685fd47b0b7d74ff15c88ccf978`。
最大尺寸 222 mm；5176 個原始三角面；每模式 795 層、3950 個原始截面多邊形、51760 條原始採樣射線。

原數值結果完整保留：0 條短射線、10 個數值 flags，numerical strict=false，standard producer exit=1。作者 normal/optimized 原始「scientific evidence identical=false」也未改寫。後續精確有理數診斷及四來源對照是額外證據，沒有升級原嚴格數值結果。

作者幾何檢驗保留在原 v9 路徑；V9-V10-EXACT-GEOMETRY-BINDING.json 證明 v9 與 v10 STL 完整 bytes 相同。獨立 v10 檢驗另保留其真正執行路徑與模式。所有原始 lossless CSV、contacts、sections、flags、exact-ray details 和選入 control fixtures/results 均由 PUBLIC-COPY-MAP.json 逐檔綁定，僅完全相同 bytes 才共用 canonical。

## 檔案與復原範圍

- PUBLIC-COPY-MAP.json：精確 canonical 檔案及 logical restore aliases
- PROJECTION-BINDINGS.json：23 個 JSON 的精確 runtime/path/key metadata 投影；其餘 typed 值不變，原 bytes/SHA 仍私人保存
- SCIENTIFIC-COVERAGE.json：四來源完整科學樹的選入與私留明細
- EXACT-OMISSIONS.json：所有明列 omission；不聲稱完整歷史或私人研究可由公開資料復原
- runtime-log-bindings/：原 stdout structured values、原 exits、進度計數及非空 warnings/error diagnostics 的精確承接
- NEW-CONTROLS-SELECTION.json 與 NEW-CONTROLS-STAGING-MAP.json：本案新增 controls 的精確選擇，不把歷史通用測試結果冒充為本案模型通過
- fixture-rebuild/：小型私人 PNG fixtures 的實際 byte reconstruction 證據；其他 cache/state reconstruction 證據保留在相應工具目錄
- DUAL-MODE-SEAL-PROOF.json：normal 與 optimized 小型 recipe/map/projection seal 的真實執行與完全相同輸出

restore_scientific_layout.py 與 roster_primitives.py 保持既驗證原 bytes。復原工具只依精確 map 建立 logical layout，不解壓、修補或重寫科學資料。metadata-projection aliases 復原的是已明列投影的公開 JSON；其私人原始 bytes 不在公開範圍。

兩個 scene-state canonical 保持原 bytes；原 saved state 與 constructed-memory state 不被宣稱相同。來源照片、PDF、研究原件、raw PNG private metadata、private API inventory、原 runtime captures 及私人編排檔不在公開 payload。clean9 PNG 只代表已證實的 metadata-only cleanup。

原歷史 controls 九檔沿固定原 SHA 引用；歷史豁免只對該不可變歷史 domain 生效，不套用到本案。完整 package privacy、實際 logical restore、technical release 與使用者 publication 授權各自是後續獨立門檻；本 roster 不給 publication GO。

有限截面與射線不能證明任意方向的全域最小壁厚、實體試印成功、製造適性、量測精確比例，或建築目前狀況。來源/外觀證書的代表性模型限制仍完整適用。
