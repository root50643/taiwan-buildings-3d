# 元培模型作者端根接診斷：可攜交審證據

本包只適用於 STL SHA256 `f7ccaa9bbb042ec8880ad5f63faec349227a22116f6992f12c5f8bc81167c31a`（5028 面）。這是作者端有界診斷，並非獨立幾何審核、全方向最小壁厚證明、切片路徑或實體試印保證。

## 原始結果

`evidence/` 內 9 個 JSON 為最新有效結果的逐位元副本；原數值、限制與原面 ID 均未改動。`FINAL-AUTHOR-DIAGNOSTIC.json` 是當時的原始索引，其中原腳本名稱與 SHA 是歷史溯源資訊，不是本可攜包的腳本清單。本包現行檔案清單與雜湊見 `PORTABLE-MANIFEST.json`。

必須保留：64 筆高損的真角外損非零；178 筆殘餘短弦是混合凹凸微接縫，不能改稱純凸角；柱底部分托接；上梁跨空；首實體短弦不能被較長內向根或跨空氣的再入射段取代。原面 1311 的近入口立面方向會先出實體再入射；只有其實際 1311／4476 共凸邊方向另有連續根證據。

## 輸入與依賴

- Python 3.11 或更新版本，套件版本見 `requirements.txt`。
- 使用者另提供上述 SHA 的 `model.stl`。本子包不重複收錄模型。
- 64 族／代表弦／截面根重播另需同一模型的 `layer-component-check.json`。須為嚴格 canonical 檢查產生的 169 層、280 個原始有效 Polygon WKT 報告；本腳本不重建或取代那個 canonical 檢查。
- 179 重播使用隨附 `current-179-root-evidence.json` 的固定樣本目錄；它不自行產生全表面密點，也不重新選出全部短弦。全密掃描及樣本選取應另外審核。
- 入口交會重播使用隨附代表弦目錄的原面／樣本資訊。
- 64 族腳本已直接帶入定位構件必需的數值配準矩陣，不需要來源照片。包內不含來源圖檔、來源圖片路徑或私人工作目錄。

## 執行

從本子包目錄執行，將示例路徑換成實際輸入與新的輸出目錄：

```
python -m pip install -r requirements.txt
python scripts/replay_warning_roots.py --model ../model.stl --layer-report ../layer-component-check.json --output ./replay-warning
python scripts/replay_179_roots.py --model ../model.stl --output ./replay-179
python scripts/replay_entry_junction.py --model ../model.stl --output ./replay-entry
```

每個腳本先檢查模型 SHA。所有 acceleration 三角以精確座標及原繞序對照；不 repair、簡化或重建替代網格。輸出不能指向 `evidence/` 或其子目錄，以免覆寫交付證據。

## 歷史依賴與封裝驗證

這些可攜腳本不讀任何舊版幾何、歷史診斷報告或私有路徑。原本以文字前綴執行舊腳本的 helper 已整理成獨立 `original_geometry.py`；只使用當前模型。原始結果內少量 `prior_sha_correspondence_by_exact_surface_point` 欄位僅保留歷史面號溯源，重播不據此量測。

本次封裝已核對 JSON 複製雜湊、有限數值格式、程式語法、CLI help 與依賴／路徑清單，另只執行入口單點 smoke test，所得 JSON 數值與原交付完全一致。未重跑 179 點或 991 代表弦／64 族／58 根等完整程序，不能宣稱整套可攜版本已完成重播。後續完整重播輸出與交付結果須由審核者比較。
