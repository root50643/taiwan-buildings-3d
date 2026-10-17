# 重現方法

建議在模型副本中執行，以免改寫隨附的原始證據。使用 toolchain.json 與 requirements.txt 所列版本；所有計算與 Blender 渲染均設定單執行緒。

## 幾何與展示

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -B source/build_model.py --output-dir models/v5
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 blender -b -t 1 --python source/render_preview.py -- v5
```

主模型預期 SHA-256：276fb42c47b0152feb14f9c7851413ea18fa6be20fd86ed73669ddabef69dd7d。

原碼建立單一實體再匯出 STL；Blender 直接讀取同一 STL 的原始三角面與頂點。scene.blend 包含展示材質、相機及兩盞日光，沒有另加建築或以照片貼圖替代模型。九個預覽為 front、rear、west、east、south、north、top、entry-detail、roof-detail；後兩張是有意裁切的局部圖。

## 檢查

qa/tools/run_full_qa.py 會在全新的輸出目錄各跑一次一般 Python 與 -O，保留各階段的原始報告。它要求零數值 flag 才會宣告 strict_passed；本件保留一條數值交點排序 flag，因此原 aggregate 仍為 false。不能把另行精確分類的成功寫回、改成零 flag，或直接忽略非零退出碼。

每一模式的原始 flags、完整 lossless CSV、raw 與 intersections 報告，再由 qa/tools/diagnose_recorded_cpp_rays.py 個別綁定，對該次執行記錄的精確 hex 射線起點/方向逐事件補證。不是重新生成理想射線，也不是挪動樣本。報告中的 finite-ray 範圍限制仍成立。

qa/render-tools/run_source_render_verification.py 重建幾何、比較本件使用的材質/場景狀態、檢查原網格及渲染設定，並可用 --rerender 執行九圖重現。PNG 清理只刪除允許的非視覺文字資訊，逐張驗證 IDAT、解碼像素及保留的色彩 chunks 不變。原始 PNG 仍保留於私人檢查證據。

完整方法不等同連續全表面壁厚證明、結構認證或實體試印。
