# 交付內容與完整性

本件僅含臺北市立大學天母校區體育館 A 棟一套原創外觀模型。模型與建築限制見 [README](README.md)，作者及獨立驗證的範圍與結果見 [QA 總說明](qa/README.md)。

- `models/v6/`：原始 STL、Blender 場景及對應程式／參數快照。
- `source/`、`parameters.json`、`requirements.txt`、`toolchain.json`：可重現的生成與渲染來源。
- `renders/`：七張主視圖及兩張局部圖，以及清理與重播雜湊綁定。
- `qa/`：原始科學結果、獨立驗證、來源外觀審核、通用檢查工具及集中封裝的正負控制。
- `sources.json`：來源連結、原始檔雜湊與用途。來源照片、PPT、圖面及地圖不隨包散布。

`qa/author-freeze-v6.json` 原樣保留作者交付驗證時的 76 檔快照索引；它也列出未隨公開包散布的原始 PNG 等私人輸入，因此不是公開檔案白名單。公開實際檔案集合、大小及 SHA-256 以 `PACKAGE-MANIFEST.json` 為準。例行執行日誌省略項另列雜湊，不會改寫科學 JSON／CSV 的結果。

在乾淨解包目錄執行：

```sh
python -B verify_package.py
```

這項輕量檢查只驗證交付檔案集合與內容雜湊，不重跑幾何或渲染，也不代表實體試印成功。總 manifest 不把自己的雜湊寫進自身；應以取得交付時提供的 manifest 雜湊或外層恢復包雜湊核對它。驗證前不要在此目錄加入其他檔案；重建和重播請使用另一份副本。
