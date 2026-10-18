# 嘉藥 J 司令台：最終增量文件及設定覆核

固定候選：`7cf0563a06858137f51751600348a35198c8f6f2`。比較的原獨立審查候選：`3a9a6041c5fde9ef2d6e9e96b02f24f025c8be5a`。本項只審公開說明、設定、引用及既有證據的身分；沒有重跑不變的完整幾何、重新渲染或重新切片，亦沒有實物驗證。

**結論：本項無必修發布阻擋，可依既有固定 STL 與製造條件 GO。** 主要入口沒有把舊長向主體切片誤作可用印法，亦沒有將數位幾何證據提升為實際列印、拆支撐或膠合保證。最終整包及 Library 身分仍由整合審查核對；本項沒有直接操作 Library、修改候選或發布。

## 實際核對與文件位置

| 核對事項 | 實際文件位置與判斷 |
|---|---|
| 舊長向診斷仍不放行 | `README.md:3,38`、`qa-summary.json:10,27`、`qa/manufacturing-review/README.md:3,5,21` 及 `manufacturing/reviewed-support/README.md:3` 均明示拒絕。exit 0／無 warning 沒有取代可印判定。 |
| 短向橋接與橋下支撐 | `README.md:38,46`、製造 README `:23`、新製造入口 `:8–17` 明示短向實際 XY 路徑、保留橋下可拆支撐，角度只適用保存方向，真機須重切逐層看。 |
| 正確尺度與填充 | `README.md:36`、製造 README `:37`、新製造入口 `:13–15` 清楚區分 100% 尺寸與 15% stars 填充，記錄 PLA、0.4 mm 噴嘴、0.2 mm 層、0.45 mm 名義線寬、3 周壁及 250 × 210 mm 床；沒有 brim。 |
| 剩餘橋接風險 | `README.md:40`、製造 README `:25`、新製造入口 `:36–39` 保留主體 8.224913 mm、屋棚 8.036027 mm 內部橋接；屋棚 2.600011 mm 槽橋並非最大值。未具相應能力須改填充／實心層並重切。 |
| 有限支撐檢查與側拆 | `README.md:42`、製造 README `:29–33`、新製造入口 `:40–48` 將原 83,924 點與新 95,890 點分開，保留 580 旗標、三段側路、4.5 × 9.4 mm 外槽和約 1.2 mm 淺凹限制。明示逐段破碎側拆，未證完整工具／抓住的碎塊、其他支撐、黏附或拆除力。工具無安全通路時須改支撐後重切。 |
| 膠合與高度 | `README.md:15,30,32`、製造 README `:13,15,17`、新製造入口 `:49–52` 保留 50 留隙膠合定位接口、清槽／象腳、十柱與棚同時乾排、補隙膠及治具。53.4 mm 名義高與約 53.25 mm 自然肩部落座分析值有區分，沒有稱為試合實測。 |
| 件數、總覽與未驗證 | `README.md:19–26,50`、新製造入口 `:21–24,54–56` 清楚是四種幾何、22 物理件；總覽勿整印。未試印、實拆支撐／brim、試合、膠強度、抗彎與運送強度的限制及屋棚翹曲、細框搬動風險都有保留。 |
| 舊 pass 的優先級 | `qa/history/README.md:3–12`、製造 README `:5`、`qa/independent-support-review/INTEGRATION-README.md:3,20` 及 `qa-summary.json:27–30` 明確界定舊原始 pass 與舊候選報告的歷史身分。`qa/README.md` 的 acceptance 是幾何檢查；現行主體印法入口明示不同的條件判定，沒有錯連作無條件製造 pass。 |

舊獨立報告仍稱修正版位於當時審查區，並仍指向舊提交；整合說明明示這是歷史證據，現行 README 另直接連到 `manufacturing/reviewed-support/README.md`，不存在需要藉修改歷史報告掩蓋的矛盾。`qa-summary.json:2` 保留作者封存時「待最終增量覆核」狀態；本報告是其後新增審查證據，沒有把它誤讀成新完成的全量檢查。

## 機械綁定檢查

- 本機實際 HEAD 為固定候選；16 份審查文件／設定逐位元組符合該提交，讀取前後不變。
- 實際 INI 相對原主體 profile 只有 `bridge_angle: 0 → 90` 與 `dont_support_bridges: 1 → 0`，其餘設定未變。新 profile 與整合的獨立參考 profile 位元組相同，SHA-256 為 `c387a77a029149fa376a76f6930fae75f4317e4682774401ef79119243362d69`。
- 實讀設定為 `support_material=1`、`fill_density=15%`、`fill_pattern=stars`、0.4 mm 噴嘴、0.2 mm 層、3 周壁、0.45 mm 線寬、250 × 210 mm 床、`brim_width=0`；起終碼為明示診斷註解，公開說明沒有稱為可直接送機檔。
- 四個列印 STL 再核 SHA 均與上一輪獨立固定值相同；本項沒有以此重複宣稱全量幾何已重跑。
- 全包 Markdown 的 42 個本機連結皆存在；`qa-summary.json` 引用的 14 份報告 SHA 全數符合實檔。現行三個主要入口的局部 Git 差異另保存，沒有只讀作者 `passed` 欄位。

詳細輸入 SHA、設定值、逐條定位與機械檢查在 [document-audit-results.json](document-audit-results.json)，實際差異在 [public-document-diff.patch](public-document-diff.patch)，核對程式在 [audit_documents.py](audit_documents.py)。兩個初始唯讀批次曾因 exec-server transport disconnected 在程序建立前遭拒；稍後的小批次成功，沒有把暫時通道故障誤報成檔案遺失。本項沒有剩餘環境阻擋。
