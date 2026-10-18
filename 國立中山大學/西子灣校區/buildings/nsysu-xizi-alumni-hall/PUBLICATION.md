# 公開版本與歷史證據範圍

本公開版本基於已獨立 GO 的固定候選 `b627db61613b2b8e1b143adc93eac940132a4df1`，安全整合到最新 main；保留原單件及六件變體，合計一套。**七個正式 STL 及所有失敗 STL 均與候選逐位元組相同**，沒有因公開化更改模型或放寬檢查。

## 公開副本做了什麼

- 執行紀錄、JSON、G-code 註解的私人本機路徑改成 `<WORKSPACE>`、`<MODEL_PACKAGE>` 等明示占位符。這些是原執行的來源說明，不能把占位符直接當作可執行路徑。
- PNG 只移除文字／來源路徑 metadata，所有 IDAT 像素資料塊位元組相同，沒有重渲染。三份 Blend 只清除一個私人路徑字串；全部其他解壓資料位元組、mesh、矩陣及失敗 Euler 殘差均不變，清理後可開啟。
- 每份 G-code 加上覆核用途警語，非註解的所有 G-code 命令保持不變。所有 G-code 均在 [切片覆核證據區](manufacturing/v2/slicing/README.md)，不是通用真機檔。
- 公開入口改為推薦六件方案，新增固定 SHA 獨立摘要、實體未測限制與當前校驗清單。原候選、未遮罩原始紀錄及真正失敗仍保存於私人 Library 最終自足備份；不公開第三方原始照片／PDF或憑證。

## 哪些雜湊檢查什麼

目前公開檔案以各層 `SHA256SUMS` 校驗，根目錄的 [SHA256SUMS](SHA256SUMS) 覆蓋公開模型套件；[PUBLICATION-FILES.json](PUBLICATION-FILES.json) 對照候選與公開副本。六件 [models/SHA256SUMS](manufacturing/v2/models/SHA256SUMS) 保持受審固定值。

`STAGING-MANIFEST.json`、`qa/original-preservation.json`、`qa/manufacturing-package-audit.json` 及歷史報告中原 SHA、檔案大小、原164檔未改、場景／圖片 hash 等欄位，是**固定候選執行當時**的資料，不是宣稱去私人路徑公開副本仍逐檔等同未遮罩候選。其原數值、旗標、失敗與退出碼未改；因公開化改變的文字／metadata 應使用公開清單的新 SHA。原先「待覆核／不發布」敘述在歷史報告中保留為當時狀態，當前發布與 GO 狀態以本文件及 [獨立摘要](INDEPENDENT-REVIEW.md) 為準。

## 可重跑入口

使用模型根目錄 `source/build_model.py --output-dir 自選新目錄` 重建原 v4，或 v2 根目錄的 `source/build_split.py --output-dir 自選新目錄` 重建六件；公開副本的兩入口已在獨立輸出目錄重建，七個 STL bytes／SHA 全部符合固定候選。完整操作見 [模型 README](README.md) 和 [v2 README](manufacturing/v2/README.md)。歷史協調程式記錄原目錄配置，不是可攜式入口；重切請用 v2 README 的明確 CLI 範例及自己的輸出目錄。

來源日期與近似限制未變：照片拍攝日未知；PDF metadata 日期不是測繪或刊登日；外部高度由照片估算，不是公尺立面尺寸。未聲稱已驗證2026現況或精密測繪比例。所有版本尚未實體試印、拆 brim、乾組或膠合。
