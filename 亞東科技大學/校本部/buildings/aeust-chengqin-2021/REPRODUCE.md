# 重建候選模型

使用 Python 3.13.9、requirements.txt 所列版本及 Blender 5.2.2 LTS 的 `bpy` 模組。生成器不需下載參考圖片。輸出單位是 mm，沒有真實建築的 1:N 比例。原 STL 不會被生成器覆寫。

在模型包目錄執行：

```text
python -m pip install -r requirements.txt
python -B source/build_model.py --output-dir qa/fresh-rebuild
python -B qa/independent_geometry_qa.py qa/fresh-rebuild/model.stl --json qa/fresh-screen.json --negative-controls
```

完整浮點篩查會如實回傳 20 個近共面共享接觸旗標及 exit 1。請保留新報告，並對同一 STL 與同一次報告執行逐旗標精確補證：

```text
python -B qa/flag_diagnosis.py qa/fresh-rebuild/model.stl qa/fresh-screen.json --json qa/fresh-exact-flags.json
```

補證只覆核原報告標出的三角對，不代表對未標出三角對執行了精確演算；完整三角對篩查仍是浮點演算。不得把兩者改稱全面精確幾何證明，或將原報告改成通過。詳細範圍見 [QA 說明](qa/README.md)。

已有的 STL、場景與預覽可在不重複渲染的情況下驗證：

```text
python -B qa/verify_reproducibility.py
```

這會在暫存目錄重新生成 STL，逐 byte 比對，讀回既存 `scene.blend` 比對有向三角多重集合，核對八張 PNG、場景及 STL 雜湊，並在記憶體重新執行場景函式，比對材質、逐面指定、相機、燈光及設定。它不重新渲染，也不宣稱已完成八圖渲染重現。另可執行 `python -B qa/run_controls.py` 重建小型合成負例。

如需重新建立場景與八張圖，先另複製一份 source/、parameters.json、requirements.txt 與模型 STL 至全新工作目錄，建立對應 models/v1/、previews/v1/ 和 qa/，再執行：

```text
python -B source/render_preview.py
```

渲染腳本使用 Cycles CPU、4 執行緒、32 samples、1000×780、seed 0、無降噪；它會覆寫該新工作目錄的 `scene.blend` 與預覽，因此不宜直接拿凍結候選包測試。`save_version=0` 關閉 .blend1 備份。Blender 資源目錄須是可寫目錄；受管 Windows 環境以 `BLENDER_USER_RESOURCES` 指到工作目錄內。`Material.use_nodes`／`World.use_nodes` 在此版本只產生預告棄用警告，沒有執行失敗。

八個鏡頭使用模型本地座標：front／rear 斜視、long-front／long-rear 兩長邊、end-negative-x／end-positive-x 兩端、top 與 connector 近看。connector 是局部特寫，容許畫面裁去其餘主體；其餘七圖應包含全模型與底板。攝影機位置與取景尺度完整存於 source/render_preview.py 和 previews/v1/render-manifest.json。

作者共渲染兩輪八圖：首輪發現牆面材質誤用窗色及斜視取景過緊，第二輪修正展示設定。首輪雜湊、鏡頭與日誌保留在 qa/，沒有多存一套過期預覽。獨立覆核僅再渲染前視一張，解碼像素完全相同；沒有八圖全重渲染。沒有使用切片器產生刀路或 G-code，也沒有實體試印。


## 發布 metadata 與嚴格失敗的重現

固定候選的原始渲染可能包含本機路徑 metadata。發布版執行 `python -B qa/sanitize_publication_metadata.py`：只去 PNG File 文字欄、清理保存場景 FileSelectParams.dir 目錄，並匿名化日誌路徑；不重新渲染、改像素或幾何。Pillow／zstandard 版本列在 requirements.txt。公開渲染 manifest 的圖像／場景 SHA 已更新，原候選 manifest 以 CANDIDATE-RENDER-MANIFEST.json 保留，二者以 IDAT／像素及場景解壓差異證據連結。

獨立嚴格檢查的原 exit 1／36 支撐旗標保留，不能以原作者較寬面積容差的結果取代。其 1/131072 mm 倒角量化微差判讀，以及公開可執行檢查與限制，見 [獨立覆核入口](qa/release-review/README.md)。重建數位檔案不等於切片或試印。
