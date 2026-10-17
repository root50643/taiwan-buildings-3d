# 重現

Python3.12.14、NumPy2.3.5、manifold3d3.5.4、Shapely2.2.0；Blender4.3.2／Cycles CPU，g++14.2／C++17。完整版本紀錄見toolchain.json與requirements.txt。原碼不讀來源照片或PDF，場景沒有外部照片貼圖。

## 原CAD與九視圖

在新根目錄中放入source/與parameters.json，並使用安裝上述依賴的Python。每次輸出目錄必須是新的，build_model.py會拒絕覆蓋已有版本。

```sh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python -B source/build_model.py --output-dir models/v15
blender --background --threads 1 --python-exit-code 1 --python source/render_preview.py -- v15
```

重建結果應為47,770個原始三角形、219×107×119毫米，STL SHA256為46649566e965a049e6e333e9d82b075407c8e926e55c9034f11fbe3dbdf15a5d。輸出模型尺寸使用毫米，不代表真實建築比例。v14補上既有B端面材質，v15再調整小天井鏡頭；v12至v15的STL逐byte相同。

參數、建模原碼、色彩選面規則、渲染原碼及saved Blend均需與凍結版本匹配。不得拿後修補STL或其他版本場景代替原件。模型中的玻璃是代表色材質與實心／凹槽幾何，沒有以透明度假冒開孔。

九張原圖固定1000×780、100%解析度、CPU64 samples、單執行緒、seed0、無降噪。相機鍵是固定驗證介面的紙面軸向名稱，並非地理方位：

- front：街端C／A斜視
- rear：校園D／A／B斜視
- east／west：紙右／紙左
- north／south：紙上／紙下
- top：俯視
- courtyard-gallery：大天井
- courtyard-arcade：小端孔朝街框

前七張ORTHO／50mm，兩張院內PERSP／20mm。全部相機位置、目標、投影與焦距固定於原碼與render-manifest.json。saved Blend的初始姿態為front。

## 全量數位檢查

完整指令與必要前置條件見qa/VERIFICATION-INTEGRATION.md。所有幾何、Blender及大型壓縮工作都必須序列執行，使用同一qa/.heavy.lock及單CPU親和性。主流程是：

```sh
python -B qa/tools/run_full_qa.py --stl models/v15/model.stl --expected-sha256 46649566e965a049e6e333e9d82b075407c8e926e55c9034f11fbe3dbdf15a5d --expected-longest-mm 219 --out qa/NEW-FULL-RUN
python -B qa/render-tools/run_source_render_verification.py --author-root "$PWD" --version v15 --expected-stl-sha256 46649566e965a049e6e333e9d82b075407c8e926e55c9034f11fbe3dbdf15a5d --out qa/render-check/NEW-SOURCE-RENDER-RUN --rerender
```

全量幾何wrapper會分別執行normal與-O，包含原始拓樸、三組0.2毫米XY截層、每個原三角形10條法線射線、完整原三角形精確相交、完整射線CSV綁定及控制案例。失敗報告、非零exit、flags與原始actual-hex資料必須保留，不能在彙整中覆蓋成通過。

若數值射線仍有crossing／parity flags，先保留strict=false。只有在全部其他前置條件已通過、零短射線且所有原始flag都以同次實際記錄hex射線完成精確分類時，才能另列有界補證結論。程序與限制見qa/EXACT-RECORDED-RAY-SUPPLEMENT-ENTRY.md；這不改變原嚴格結果，也不是對任意射線或全域最薄壁的保證。

來源重建與影像重現分別核對：CAD重新生成的STL逐byte相同；原STL三角形在saved Blend中沒有改變；原碼重新建場景的完整可檢查狀態相同；九張再渲染圖的decoded RGBA8及清理規則後剩餘PNG metadata完全一致。原PNG另保留原始檔雜湊，不能用只看縮圖代替檢查。

本次作者預檢實際省略--rerender，僅驗原碼、場景與PNG控制，並保留full_nine_view_rerender_verified=false。正式九圖再渲染由獨立驗證單獨完成一次；在該結果取得前，不宣稱完整影像重現已通過。上面的含--rerender指令保留供完整重現使用。

最終場景也須接受normal／-O負控制：未改場景應接受，錯誤samples、denoising、鏡頭、view-set、source material或其他相機定義應以預期實質理由拒絕。控制案例證明工具能偵測指定錯誤，不等於模型本身已通過。
