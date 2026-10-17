# WFU 生有樓 v13：完整科學證據與安全還原

本目錄保留最終模型的作者 normal／optimized 與獨立 normal／optimized 四來源證據。作者 v12 與 v13 STL 位元組相同，因此 v12 原始科學結果直接綁定 v13；沒有為了發布改寫科學結果。

## 結果界線

- 原 STL SHA-256：8348213614296746732da6a8024821ff48536e847419fe13545dc1ab20730ca0。
- 原始 raw mesh、全部 1,718 個截面層／7,752 個 polygons、209,460 行 dense CSV、33 個原 numerical flags、33 個 exact-ray 診斷與全部 160,122 個原 triangle contacts 均保留。
- 原 numerical strict_passed=false、standard producer exit=1、full-qa-summary 的 normal_optimized_scientific_evidence_identical=false 原樣保留。新獨立比對報告另外說明精確容許的 runtime／interpreter 差異，不改原報告。
- 外觀證書只批准聲明的代表性外觀；不是全方向最小壁厚、切片、製造、實體試印、隱私、授權或發布批准。

## 唯一 canonical bytes 與還原

PUBLIC-COPY-MAP.json 列出每個實際公開檔案的大小與 SHA-256，並列出 author／independent／roster 等邏輯來源的還原位置。同 bytes 的資料只存一次。model v13 的 build_model.py、render_preview.py 與 parameters.json 對應根目錄 source／parameters；v12 同 bytes 的 STL、build_model.py 與 color-regions.json 也有別名。

唯一完整 dense 檔案位於 qa/v12-full/normal/standard/dense/dense-original.csv.xz。它是原 XZ，並非重新壓縮或節錄：

- 壓縮大小 19,156,984 bytes；SHA-256 80cf38d8255e789755e316a24638872db0fb913f2d37795edd3c81349551f550
- 解碼大小 194,500,309 bytes；SHA-256 6408a97da82dc7a1e226225637a415d6cd8ecaecfb962e51454f52bc3067f2b6
- 209,460 筆 data rows，另有一行 header

在 Linux/POSIX 系統，從 building 根目錄執行：

```sh
python -B qa/restore_scientific_layout.py --public-root . --out /your-owned-directory/wfu-restored
```

輸出父目錄必須已存在、由目前使用者擁有，且不可讓群組或其他人寫入。輸出目錄必須全新。工具先檢查全部 canonical bytes，再以逐層 descriptor-relative、O_NOFOLLOW、exclusive-create 寫入，最後逐檔重驗。它拒絕路徑穿越、symlink、FIFO、重複目標、檔案／目錄衝突和 hash 不符；不啟動 Blender、不解壓 CSV、不展開 controls archive。

還原後 author/ 是作者邏輯樹，independent/ 是獨立執行／工具／controls 邏輯樹。這是公開範圍的還原，不是原私有 checkpoint 的全體重建。原兩份 freeze inventory 完整保留，但較早版本模型、歷史科學、私有來源、raw PNG metadata、私有執行記錄與故意帶私有字串的負控 fixtures 依逐檔 omission 記錄留在私有 checkpoint。

## 公開路徑投影與九圖

少數 JSON 僅將已列明的 command argv、source_path 或其他執行位置字串改成公開邏輯位置。PROJECTION-BINDINGS.json 和 copy map 記錄原檔／公開檔 bytes、SHA-256、精確 JSON pointer、原字串 SHA-256 與新值。反向還原宣告的欄位後，所有 JSON 值與型別必須完全相同；不遞迴刪除 key、不改任何數值、strict 結果或 exit。

公開圖片只有作者 qa/render-check/v13/sanitized-previews 的九張 metadata-only clean PNG。原 raw9 與獨立 replay9 的檔案 identity、decoded RGBA、IDAT／保留 chunks 與所有九個 view 的證明另存於原 source binding／render audit 和新 result binding。raw PNG 的位元組與可能含私有 metadata 的原檔留私有；不能把 clean PNG 宣稱為 raw 檔案位元組相同。

完整 source-state JSON 保留原值與 bytes。其中 /render/filepath 是原 Blend 未使用的 generic render default。SOURCE-STATE-DEFAULT-EXCEPTIONS.json 僅以完整檔案 SHA、唯一 encoded byte offset、確定的 JSON pointer／型別／值描述它；其 UTF-8 hex 是驗證描述，不是重寫 source-state。這個精確 scan-only 例外綁定原 Blend、兩模式 SDNA profile 與完整 scene/resource 證明，不是一般路徑白名單。

## 新 controls 與歷史重用

新 controls 保留原 generator、完整逐 case 結果和來源／fixture hashes：capture 40×2、最終 lattice56 parser 79 subtests×2（保留原 69，增加 10）、SDNA 9×2、case-postflight 24×2、source-binding 43×2，以及修正後 privacy r3 162×2。原 2^30 helper 與原 artifact-review 失敗報告明確保留為歷史；最終 helper 只針對本 STL 的 2^56 lattice 窄適配。獨立原始 binary32 逐值證明涵蓋全部 188,514 座標，另有兩模式 exact rational／binary32 byte round trip。各 suite 的實際報告是狀態依據；不要把本段計數當作通過聲明。restore／roster 自身另有雙模式合成負控。

SDNA 的 original fixture generator 為 candidate-sdna-v13/tooling/test_blend_sdna.py，auditor 必須在同一目錄。從還原根目錄執行下列命令，將 CPU 換成目前允許的一個 CPU，輸出使用新的私有暫存目錄：

```sh
taskset -c CPU python -B independent/candidate-sdna-v13/tooling/test_blend_sdna.py --blend author/models/v13/scene.blend --out NEW_PRIVATE_SDNA_NORMAL
taskset -c CPU python -B -O independent/candidate-sdna-v13/tooling/test_blend_sdna.py --blend author/models/v13/scene.blend --out NEW_PRIVATE_SDNA_OPTIMIZED
```

兩模式所有 18 個原 fixture bytes 的實際重建比對在 rebuild-proof.json。6 個未改動的候選 Blend aliases 指向同一公開原 Blend；12 個故意修改或損壞的負控 Blend 不公開。逐 case 原 hash／原結果與原 generator 都保留。其固定私有工作位置的執行 wrapper 留私有，不影響原 generator 重播。

capture 原 generator 保留 selected-Python 契約。公開位置特別放在 qa/independent-tools；其相對位置要求 building 根目錄有 modeling-toolchain/.venv/bin/python。還原後則在還原根目錄建立相同環境，再用該 interpreter 執行 independent/independent-tools/test_capture_process.py，--baseline 指向 independent/reuse-preflight-v1，--out 必須新目錄。baseline 的 28 個原 tools／verification／render-tools 全部依 copy map 還原。所需依賴與版本見作者 requirements.txt、toolchain.json。此處不自動安裝或變更環境。

public privacy r3 checker 只將 BLEND_PATH 與 CSV_PATH 改為 building 根目錄的公開 canonical 位置；控制 generator 只同步 checker SHA／bytes pins。所有 r3 scanner、mask、bounds、predicates 及 162 cases 不變，兩模式公共版 controls 另行實跑。原 checker/test 與完整 diff 私存；SOURCE-ADAPTATION.json 綁定兩版來源。

qa/controls-history 保留前案已完成的九個原檔，包括 16,730-member archive、index、selection、完整 packaging result、三個 allowlists、原 packager 和 prior replay。其 AEUST case identity 是歷史測試資料，不能當作 WFU 科學批准。WFU 的新 history replay 另外提供當次來源與真實雙模式重播證明。

新的小 controls archive 不重複加入主公開包。主包保留唯一 canonical generator／results，加上精確 selection、index、雙模式安全解包與 bitwise rebuild 證明。依該 selection 從主包 canonical bytes 建立全新臨時 staging tree，再以原 build_controls_archive.py --root STAGE --index INDEX --out NEW_ARCHIVE 重建；結果必須符合 index 的 archive SHA。確切 staging mapping 與已完成的重建結果以 NEW-CONTROLS-SELECTION.json 和相鄰 replay proof 為準。先執行同一 restore 入口，將 --copy-map 指向 qa/NEW-CONTROLS-STAGING-MAP.json，即可只建立該小 selection；不重複完整 science。

原 result-binding 主程式會驗證全部 1,014 個作者 inventory 成員，因而需要完整私有 checkpoint 才能重跑完整 main gate；公開包仍保留其原 generator／43-case controls、最終報告的精確投影與來源 bytes binding。不能以公開歷史 omission 略過該原檢查。

公開的 final-v13-r1/independent-runner.py 是原封不動的通用 CLI 原碼，綁定其實際執行 SHA。完整幾何／source／九圖重現需要原 runner input selection 的 raw PNG 等私有 checkpoint 資料、指定 Blender 與環境，不能拿僅公開還原樹冒充全部原輸入。此案已完成的唯一獨立九圖執行以 execution ledger 為準；此處的重現說明不表示又執行另一輪。

CONTROL-PAYLOAD-COVERAGE.json 逐檔列出原 controls inventories 的全部 3,499 個持久檔案，明確區分選入與私有 omission。capture 的 injected fixtures／runtime 原件、SDNA 反例、較早工具修訂與原失敗結果均有原 hash 與留存說明；不宣稱公開包可以 bytewise 還原全部原 controls 輸入。原 generator 自行清除的暫存 fixtures 依完整逐 case 結果與 generator 追溯，沒有虛構其持久原檔 hash。所有模型科學檔案仍按四來源完整 roster 保存。

## r2 精確公開 metadata

完整字節掃描正確拒絕 firstseal 的私有 runtime labels 後，本修訂只處理明列 metadata。138 個 routine stdout 共 39,887 bytes 經逐欄核對，所有 passed/error/short_samples、expected/verified、gate 與 138 個原 exit 已完整存在於 22 份原結構化 JSON；它們只留私有原件、SHA、逐檔分類及引用，不重複加入公開包。分類及必要 JSON 清單在 runtime-stdout-audit-v1，沒有省略唯一科學數值、flags 或 exit。

兩個歷史 inventory path keys 與相應 coverage／omission labels 使用明列 public logical alias；原 label SHA、原完整 JSON SHA 與原 bytes 私留。只有這兩個 key 可按固定 parent pointer 改名，所有對應值與 JSON 型別必須反向完全相等。SDNA 四份原報告及兩個同 bytes stdout aliases 只將已批准的 generic defaults 描述改成明示 utf8-hex: 字串；解碼即可恢復原描述，buffer hashes、offsets 和其餘值不變。原 Blend 和完整 scene-state 科學 bytes 不改，也不增加掃描例外。source-binding controls 僅十個已列 error pointers 的 runtime path labels 改公開 alias。

唯一 restore/primitives 原 source SHA 維持不變；r2 sealer 另以 normal/-O 各 29 個小型 controls 驗證（保留原 15，增加 14）。firstseal 原 source、manifest、真正失敗的全包 scan 與先前還原結果完整私留，不混當 r2 最終 proof。
