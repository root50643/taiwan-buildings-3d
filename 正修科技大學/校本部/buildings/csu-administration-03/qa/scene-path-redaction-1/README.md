# 壓縮場景保存目錄：發現、最小修正與銜接

首版 `6e683682473c2d1dbdf221b47270e0c909bd6eb0`／Library v2發布後，補做全檔、gzip及所有BLEND zstd frames解碼掃描，發現v1／v2各一個私人主機目錄。**修正前完整二進位掃描false、兩個findings。** 原text／PNG衛生檢查沒有解壓BLEND內層，原回條的排除私人路徑宣告範圍不足；保留原報告，不把初版13項true或「排除」宣告當作完整二進位證明。沒有憑證模式命中，STL與其他檔未見私人主機路徑。

獨立BHead／SDNA解析定位兩者皆為DATA區塊 `FileSelectParams.dir[1282]`，SDNA 849、結構2280 bytes，區塊header位於176204，title[96]為存檔對話框標題；目錄欄位是解碼offset **176332..177614**。另核 `FileGlobal.filename[1024]` 為空，這不是外部模型／圖片引用。公開記錄只有原值長度、hash與欄位定位；實際目錄與原場景備份保留於交付包外私人工作區。

[最小遮蔽manifest](redaction-manifest.json)記錄每個場景原／新整檔及解碼SHA。目錄欄位置為相對目錄 `//` 加NUL填補；每場景解碼42 bytes改變，全部落在該char array內，**欄位外解碼bytes完全相同**。三個zstd資料frames及解碼分段邊界保留，未受影響的兩個資料frames連壓縮bytes也相同；只重壓受影響frame並更新seektable的壓縮大小。原壓縮level未知，新受影響frame用level3；不宣稱整個壓縮檔或所有壓縮bytes相同。

| 場景 | 原SHA256（歷史） | 新SHA256 |
|---|---|---|
| models/v1/scene.blend | `18736d0ee70384fba9a20f83d3632b9a237c0f1d01f1d4eaf28ec85bf837e750` | `fc0c4ac3a4106a8f7c28ec4b526d6cac33ec433297329c69e7dbccea76be99a3` |
| models/v2/scene.blend | `b9b0cf0a1411b4c29a69656888610223d5952a6b0fbb8b91c58b30bf6908c056` | `d852f85363988a986e7ed225ebfeb39433e9e8fe6a1d8e48fb8d09f6fec0f01c` |

原build／render manifest、原獨立GO、初版發布驗證及Library v2回條均維持其固定時點。新scene hash由本映射銜接，不能當成舊檔仍逐位元相同。STL、生成器、現用參數、G-code、預覽及原數值／旗標保持；嚴格製造false、未實印、支撐清除／尖緣／翹曲／膠合未驗的限制全部延續。沒有重渲染、重切片或把原失敗改成passed。

[真正新舊場景的語義比較](semantic-comparison-corrected.json)在每次bpy載入前後守門原／新已知SHA，且要求兩者不同。每場景物件、mesh、camera、light、materials、worlds、render settings、frame1／2 transforms及external references九類簽章一致；只是只讀開啟及記憶體frame求值，未保存場景或渲染。

第一次語義比較恰逢作者整合staging，原輸入位置已被更新，實際讀到兩份新版。保留其[原無效報告](invalid-attempt/semantic-comparison.json)及[原因](invalid-attempt/semantic-comparison-invalid-notice.json)，**不採為原／新等效證據**；原報內passed=true只是new／new相等，沒有改寫該歷史旗標。歷史工具加停止保護，原／交付腳本hash與僅移除guard後AST相同的映射見[provenance](invalid-attempt/provenance.json)。正確比較改用固定原副本，並加前後SHA檢查；不能拿首次結果冒稱已驗原檔。

[獨立覆核](independent/README.md)另以固定6e Git blob、自行推導SDNA欄位及手動zstd框架解析核對，確認其他解碼bytes完全相同；八個索引與原13項true報告也保持。[匯入manifest](independent/import-manifest.json)記錄15檔全部來源／交付bytes與SHA相同。獨立API檢查原先包含runtime `ID.session_uid`而得到false，原報完整保留；同一old場景重載控制確認37個runtime ID改變而其他簽章相同，修正版只明示排除此欄位，十類簽章一致。執行環境的DLL載入失敗與後續唯讀成功摘要另見[environment note](independent/environment-execution-note.json)。

[本次發布增量與全包解碼掃描](release-validation.json)由[validate_scene_metadata_release.py](../../source/validate_scene_metadata_release.py)產生，檢查403個首版檔、只允許六個metadata／說明異動，以及現包raw／gzip／全部BLEND dataframes的有限路徑與憑證模式掃描。它不重跑幾何、製造、切片或渲染；沒有將嚴格false改為true。

此發布檢查的[第一次輸出](invalid-attempt/release-validation-self-output-reference.json)把當下尚未生成的自身報告連結判為斷鏈，故passed=false；其餘八項（包括完整解碼掃描）均true。保留原輸出，修正程式只略過「正要寫出的自身報告」這個循環輸入，其餘本地連結照常驗證；另立新輸出，沒有修改原false或製造旗標。

## 可重做的固定來源遮蔽

工具 [redact_scene_paths.py](../../source/redact_scene_paths.py)限定上述兩個原SHA及已核SDNA欄位，輸出到來源之外的新staging資料夾，不原地修改來源。依賴見[scene-metadata-requirements.txt](../../source/scene-metadata-requirements.txt)。需先從原6e68368提交取出兩個原場景到獨立 `<ORIGINAL_MODEL_ROOT>/models/v1/scene.blend` 與 `models/v2/scene.blend`，勿覆蓋現用場景；原值備份目錄須放在交付包外。

```text
python -B source/redact_scene_paths.py --input-root ORIGINAL_MODEL_ROOT --staging-root NEW_STAGING_ROOT --private-root PRIVATE_OUTSIDE_DELIVERY
python -B source/compare_scene_semantics.py --input-root ORIGINAL_MODEL_ROOT --staging-root NEW_STAGING_ROOT --report-name FRESH_SEMANTIC_REPORT.json
```

這是固定來源的metadata工具，不是通用任意BLEND修復器；對現用已遮蔽場景重跑會因原SHA不符而停止。原 `source/validate_publication.py` 已標為6e首版歷史入口，在本修正目錄存在時停止，避免把舊固定輸入驗證冒用於現版。

下載目前artifact即可作現用場景完整性核對，不需要Git、私人原檔或bpy：

```text
python -B qa/scene-path-redaction-1/independent/check_current_scene_paths.py --package-root . --output FRESH_CURRENT_REPORT.json
```

在保留6e原Git物件的clone另可執行發布差異與解碼掃描；輸出不得覆寫舊報：

```text
python -B source/validate_scene_metadata_release.py --output FRESH_RELEASE_REPORT.json
```
