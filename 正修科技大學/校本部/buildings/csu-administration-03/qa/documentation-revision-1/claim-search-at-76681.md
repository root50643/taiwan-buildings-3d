# 固定 76681 候選：文字／數字宣稱搜尋與修正建議

基準提交：`76681c5dcedc88d684946780e795d7914a88c075`。本次只讀取該提交的 Git blobs，不依賴後續可能變動的工作樹；沒有修改 repo、STL、G-code、舊 QA 或正式獨立覆核原檔。建議供作者另作文件修正，不是本子任務的製造核准。

已完整讀取 `2026-10-18/task-7/csu-76681/INDEPENDENT-CSU-REVIEW.zh-TW.md`。以下關於實測門凹、真正 G-code 門頂線與接合覆蓋條件的數字均引自該正式獨立覆核，不假稱本次重新量測或重切片。

## 搜尋範圍與方法

- 固定模型套件共 **337 個追蹤檔**：111 JSON、88 gzip JSON/JSONL、36 STL、25 TXT、23 PNG、22 PY、18 LOG、6 Markdown、4 G-code、2 BLEND、2 INI。
- 對 **184 個一般文字檔**作數字與詞句搜尋，再人工讀取命中上下文；另解壓搜尋 **88 個 gzip**、搜尋 **4 個 G-code 註解**，合計276個可讀文字／壓縮payload。其餘61項為STL、PNG與BLEND二進位資產；本次沒有重跑幾何或重新OCR，不能稱搜尋了它們的全部內文。
- 關鍵詞包括 `0.45`、`0.65`、`door_recess_depth`、`maximum_shallow_facade_recess`、`4 mm`、公差、tolerance、bridge、門凹、no-support、support disabled、免支撐、`16.6`。初掃57個檔案有467個廣義命中；數值座標、耗絲小數、切片線寬及數值演算法容差等假陽性已分開，不列作錯誤。
- 88個gzip與4個G-code註解未找到這些待更正的敘事性舊句；它們仍是原始證據，不能因此刪除或改旗標。
- 本機 `rg` 不存在，故以 Python 讀取 `git ls-tree`／`git cat-file --batch` 的固定物件搜尋。一次後續補充唯讀查核因 `exec-server transport disconnected` 未執行；前述完整搜尋已完成，不受其影響。

## 應修正或新增補註的現行宣稱

以下行號都屬固定76681版本，修文後會位移。

| 位置 | 固定版現況 | 建議 |
|---|---|---|
| `README.md:20` | 「立面窗戶以最深0.45 mm…」將普通窗與入口的淺凹描述混在同段；0.45不是現有STL最大凹深。 | 明列**普通窗凹約0.4 mm、入口門凹約0.65 mm（獨立raw-STL實測0.650001526 mm）**。門廊填實／淺凹的製造簡化仍保留，不再泛稱所有凹面最深0.45。 |
| `parameters.json:12` | `entrance.door_recess_depth=0.45`。 | 改為反映固定件約0.65 mm的**聲明／量測欄位**或另加固定件實測欄位；明說現有生成器沒有讀取此key，不能讓人以為改此值會控制門深。此次不需要改幾何。 |
| `parameters.json:14` | `manufacturing.maximum_shallow_facade_recess=0.45`。 | 最大淺凹含入口約0.65 mm；普通窗另列約0.4 mm。明示此欄是固定件說明，現有生成器未讀取整個manufacturing物件。`minimum_design_wall=1.6`只可當設計意圖，不是屋簷尖邊／全域壁厚實測保證。 |
| `README.md:18` | 已正確寫「沒有裝配公差」，但後句只說兩邊各外伸4 mm可作對中參考。 | 保留人工置中／平面膠合；補明**X/Y四邊4 mm只是名義外伸，不是±4 mm允許偏移**。截角使無旋轉且40×28 mm頂台全覆蓋的純幾何條件為`|Δx|+|Δy|≤1 mm`；這也不是製造公差、膠厚或強度承諾。建議試放、保持48沿X／36沿Y、必要時用臨時對中記號或治具。 |
| `README.md:22` | 已有不能免支撐及真機重切條件，但只泛稱窗凹頂緣等小懸空；「窗凹紋只0.4」本身適用普通窗。 | 保留普通窗0.4，另點名**入口門頂有16.6 mm實際Overhang perimeter**；深度0.65不代表橋跨0.65。此風險不能由背後實心、零Bridge infill或no-support零支撐數豁免。 |
| `QA.md:17,19,21,23,25` | 淺凹／水平小懸空與auto45總數已有保留，但未點明實測門深或唯一Overhang perimeter的實際長度。 | 新增正式勘誤段與獨立報告引用：前面Y=−29.200000763、背面Y=−28.549999237、深0.650001526；背後同線約46.55 mm實體，**不是0.65 mm薄牆**，仍有門頂成形／支撐意義。列16.6 mm門頂線與auto45門區支撐條件。不要覆寫原raw旗標。 |
| `qa/v2/QA-NOTES.md:16` | 最大單投影最小外接矩形寬0.650002，並已正確寫「不是橋跨證書」。 | 這句應保留；其後另列門深與門頂真路徑，避免讀者把0.650002當實際橋跨。**包絡窄寬／門凹深／G-code路徑長度是三種不同量。** |
| `qa/v2/QA-NOTES.md:22–27` | 原始no-support唯一overhang、auto45總支撐數與修正audit已有正確指向。 | 加正式獨立核對：門頂模型線`(-8.3,-28.975,20.2)`至`(8.3,-28.975,20.2)`，長16.6 mm，當時WIDTH0.4／HEIGHT0.4。auto45門凹區305支撐／介面段、45沉積strata；最高支撐頂Z19.8、STL門頂下表面Z20。名義0.2 gap不等於證明料線接觸、無下垂或容易拆。 |
| `source/qa/README.md:19,21` | 「預設關閉支撐、另附auto45」本身正確，也提到另有修正audit。 | 補註原runner仍呼叫歷史audit及硬編no-support限制，若用auto45必須讀修正audit／新增勘誤；不能把原runner完成當所有profile的支撐語義正確。可只加工具勘誤；若改工具，另留原source/hash並建立新驗證，不改舊執行輸出。 |
| `source/qa/run_slice.py:36,42` | 接受任意`--profile`，卻固定呼叫原`audit_gcode.py`，固定輸出「no-support slicing only」。 | 這是現有可執行工具的通用說明錯誤，對auto45尤其不符。最小文件路線：明確標記原工具屬歷史語義，正式引用修正audit；或新版本依embedded config產生說明並用新輸出資料夾驗證。不要重寫當時summary。 |
| `source/qa_audit_gcode.py:6` | 修正版docstring仍說「this run deliberately disables support」，雖然:132/:165已按實際config判斷。 | 此為現用修正版的殘留說明，應改中性文字「read actual embedded support state」。若動source，只變文案也會改hash，需另作當前工具綁定，不覆寫原修正audit宣稱它當時用過新hash。 |

### 參數的控制範圍

固定生成器 `source/build_model.py` 的門體前面來自:98的`e['depth']+0.4`，門凹刀具在:101硬編為中心Y=−28.9、深0.7；它沒有用`entrance.door_recess_depth`。普通前／後窗刀具在:77–78、:86、:89、:93–94也是硬編中心／0.6刀具深，與外牆相交後約0.4凹深，並非讀`relief.window_depth`。

現有程式**未讀取**`entrance.door_recess_depth`、整個`relief.*`、整個`manufacturing.*`及`parapet.inset`。`base.*`、主要`wings.*`、`center.*`、`clerestory.*`、`roof.*`、`parapet.height/thickness`與其餘入口尺寸則確有讀取；但多處派生幾何仍硬編常數，例如翼厚27、柱梯位置／尺寸、窗列及山牆Y位置，不能宣稱全部已參數化。本輪宜以註記揭露，無需為文件補正重寫生成器、改模或重建全部歷史QA。

## 應保留的歷史證據與新增勘誤

| 不應就地改寫的檔案／欄位 | 理由與勘誤方式 |
|---|---|
| `qa/v1/source-snapshot/parameters.json:12,14`的0.45；v1 source、STL、build-report、288層失敗 | 它們是當時來源／生成證據。保留原bytes，由新勘誤說明同樣的未用聲明與實際幾何差異；不把v1失敗改成v2通過。 |
| `qa/v2/slicing/body-auto45/slice-summary.json:47,53` | :47是當時audit stdout的錯句快照，:53是runner硬編的錯limits。兩者錯誤都應保留；新勘誤明確列這兩處，正式交接連到既有修正audit及實際config／支撐數。不要僅修其中一處後假稱原結果完整正確。 |
| `qa/v2/slicing/body-auto45/gcode-audit.json:13168`、`audit.log:176` | 原錯誤「Support was deliberately disabled」是已保存失敗；`corrected-audit/gcode-audit.json`及`auto-support-evidence-validation.json`已另存。應引用後兩者，不改G-code、不改原輸出。 |
| `source/qa/audit_gcode.py:6,160` | 這是沿用原audit的固定來源，也被原切片證據綁定。可以保留為歷史工具並加勘誤；若要更新活躍runner，另留歷史source副本／明確新版本與hash，不能抹去錯源。 |
| v1與v2真正no-support基準的`gcode-audit.json`／`audit.log`／`slice-summary.json`中no-support句 | 對這些基準本來屬實，**不要全包搜尋取代**。其零支撐不證明無需支撐的限制仍必須保留。 |
| `body-original-downward-flag-review.json`的0.6500015258789062、raw點、97層／806面／28.04 mm²、71屋蓋短弦 | 原量測與篩檢不錯，不能以門深勘誤覆寫成新的橋跨或把false改true。只新增解釋不同量的界線。 |
| `.ini`及G-code中的`extrusion_width=0.45`、首層寬0.45、`dont_support_bridges`、演算法`*_tolerance_*` | 不是門凹0.45，也不是接合製造公差；不要因相同數字／單字而修改。 |
| `previews/v2/render-manifest.json`、`qa/v2/visual-source-review.json`、`final-evidence-validation.json`、`auto-support-evidence-validation.json`、`models/v2/build-report.json`既有輸入hash及當時current=true | 它們綁定76681的原始來源／參數。文件／註記／docstring修改會改current來源hash，不能直接換hash假稱原執行使用新來源。應另加**文件勘誤後的綁定／驗證回條**，明示哪些文案改了、三STL與原G-code仍相同、哪些舊驗證只對原提交成立。 |

正式勘誤應至少保留：原提交76681、修改檔／行／原聲明、門凹精確值與普通窗值、未用key說明、16.6 mm真路徑及支撐／清除限制、4mm與純幾何1mm條件的區別、三STL及原G-code SHA不變。不要以「只是文件錯字，完全無製造意義」概括：門頂確有成形與支撐風險。

## 正式獨立review的引用檔案清單

建議放入獨立子目錄並保留相對結構，清楚寫它覆核的是**固定76681的幾何／原始證據**；新文件提交只是完成其必修勘誤，不能讓獨立review看似審過後續未審的新幾何。以下主報告直接引用的10項與主報告本身不可缺：

1. `INDEPENDENT-CSU-REVIEW.zh-TW.md`
2. `identity-and-author-receipt.json`
3. `agent-source/SOURCE-IDENTITY-SCOPE-REVIEW.zh-TW.md`
4. `agent-source/source-evidence-verification.json`
5. `independent-rebuild.json`
6. `agent-geometry/INDEPENDENT-CSU-GEOMETRY-REVIEW.zh-TW.md`
7. `agent-geometry/independent-csu-geometry.json`
8. `independent-scene-check.json`
9. `independent-front.png`
10. `agent-manufacturing/MANUFACTURING-REVIEW.zh-TW.md`
11. `agent-manufacturing/independent-csu-manufacturing.json`

為保留完整22項自足證據包，還應連同下列11項：

12. `final-verification.json`
13. `evidence-manifest.json`
14. `finalize_review.py`
15. `verify_identity_rebuild.py`
16. `independent_scene_check.py`
17. `agent-geometry/independent_csu_geometry.py`
18. `agent-manufacturing/independent_csu_manufacturing.py`
19. `verification-helpers/independent_contact_check.py`
20. `verification-helpers/independent_raw_topology.py`
21. `rebuild.stdout.log`
22. `rebuild.stderr.log`（原為0 bytes，仍保留）

原獨立ZIP：`csu-administration-independent-review-76681c5.zip`，**635,610 bytes／22項／SHA256 `ca2d4aef2153115ba8ccbc54812cea1b1330232184d8fb4e01388951defdda4e`**。本次唯讀核算此ZIP的SHA；沒有再次下載、上傳或將它直接加入repo。主報告原檔SHA：`725121b9a1ae1af8a8b0ef32bbe4ad8ac809b28a0479d0506d50a35ac0841b8e`。外層`delivery.json`不在22項ZIP內，且含主機絕對檔案位置，不建議原封公開；可另造公開相對路徑回條。

### 原獨立包的主機路徑問題

**不要將原ZIP原封放進公開repo或交付Library。** 唯讀搜尋在以下11個內檔發現主機home絕對路徑；只有路徑位置列於此，未複製私人路徑文字：

| 原檔 | 行號 |
|---|---|
| `agent-geometry/independent-csu-geometry.json` | 108、197 |
| `agent-geometry/independent_csu_geometry.py` | 11 |
| `agent-manufacturing/independent-csu-manufacturing.json` | 1576、1626、1672 |
| `agent-manufacturing/independent_csu_manufacturing.py` | 13 |
| `agent-source/source-evidence-verification.json` | 8、20、32、44、56、68 |
| `finalize_review.py` | 5 |
| `identity-and-author-receipt.json` | 2732–2735 |
| `independent_scene_check.py` | 6 |
| `verification-helpers/independent_contact_check.py` | 13 |
| `verification-helpers/independent_raw_topology.py` | 12 |
| `verify_identity_rebuild.py` | 6 |

只在**新增公開副本**中作可稽核路徑遮蔽／相對化，原獨立資料夾與ZIP不動。另建公開副本manifest，列原ZIP SHA、原檔SHA、公開副本SHA、改動類型及行號；保留`evidence-manifest.json`作「原reviewer包manifest」，不能宣稱遮蔽後檔案仍與原manifest逐位元組一致。程式若相對化，僅能聲明公開副本便於讀取；獨立覆核實際執行的是原版腳本。源數值、原旗標座標、失敗狀態、算法及結果不應因路徑清理改變。

## 固定幾何與交付界線

- body：`e388dff1247334ec5e79530e45a1b7e5e85d1a630aff0a9d6d53720f1362ee6c`
- roof：`7d1c8840ee11649ec4c57984ff1a0cc2c2a3916f37fc21888e7ead0f631fed04`
- assembly：`6d3a8796831cd83bd7e012664dd8f094b6e700998031e71db38567fc1ecff416`

本次沒有寫入以上檔案、沒有重建／重切、沒有改公開計數、沒有push或發布。一次非必要補充查核曾因transport斷線未執行，並非自動核准拒絕；其後服務已恢復，草稿落盤與讀取已驗證。沒有剩餘執行阻擋，正式修改與新增公開副本仍由父任務處理。
