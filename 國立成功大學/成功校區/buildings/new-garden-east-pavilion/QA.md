# 驗證範圍與重跑

此為 1.0.0 正式交付版，已通過 [獨立審核的限定條件](INDEPENDENT-REVIEW.zh-TW.md)。STL、Blend、六張預覽、全部程式及數值證據與受審版本完全相同；正式化僅更新說明與必要的檔案雜湊綁定。所有報告綁實際 STL、檢查程式與 helper／C++ 來源。數值篩檢不等於所有方向最小壁厚證明或實機試印。

## 保留的結果

- 原始二進位 STL 有 4,158 面、2,081 個精確座標頂點，單一封閉有向表面。檢查儲存法線、邊兩面鄰接、頂點 link 閉環、繞序、正體積與 150 mm 最大尺寸。沒有修補、刪面、四捨五入或近似焊接。
- 自 z=0.071 mm 起每 0.2 mm 剖切，共 156 層。每一原始 Polygon 個別做半徑 0.4 mm 開運算，不得消失或分裂；個別面積損失不超過 1%，實測最高約 0.472%。不能以大底座平均掩蓋小孤島。
- 每一原始面取十個固定重心座標，共 41,580 個原法向樣點。1,430 點首材料區間小於 0.8 mm，最短約 0.400 mm。因此 `dense-short-chords.json` 的 `passed` 與 `all_first_chords_ge_0p8mm` **維持 false**，嚴格診斷程式退出碼為 1。完整 CSV、所有短點、首材料、後續空氣與全部交點均保留。
- 這 1,430 點皆落在明確限定的背靠實體浮雕：主廳門窗重疊橫框、西服務及南設備槽百葉、屋突百葉／頂帶、東南轉角窗端。`root_rules.py` 固定每類區域與方向，不能搜尋最長或最有利射線。
- 每點從原表面向內 0.00001 mm，再沿固定方向到預定背襯平面；檢查整段連續材料、完整根部首材料、出界後空氣與可能回入、背襯在原法向正反兩側的合計材料跨度。最短連續根部約 9.208 mm、背襯跨度最小約 19.600 mm。這些數字不能替代原始短弦，亦不把短弦改稱為 0.8 mm 厚牆。
- 全部 7,150 條完整查詢對每個原始三角面做邊界重疊檢查，另有 43,163 個長雙精度 solid-angle winding 材料／空氣／回入控制；未省略失敗或不確定點。固定根部檔綁原短點與 CSV，區間檔綁固定根部檔；座標、法向與面／樣點身分須來自當前 STL。
- 六個幾何負控制保留原輸入與失敗報告：刪面、重複面、反轉面、額外封閉殼、0.6 mm 薄根、上層 0.6 mm 小 Polygon。
- 新負控制覆蓋改預覽、README 私人路徑、空檢查器、增刪配送檔、子目錄同名清單、改短點／根部與遺漏樣點、變動 checker 卻沿用舊報告重新封裝，以及 Python `-O` 和 Blender 的失敗退出碼。
- 實際 Blend 僅一網格、無修改器、identity 變換，全部有向原始三角面與 STL 一致。隔離建模重建 STL 位元組一致；固定 Blender 4.3.2、CPU 單執行緒、固定種子重播六張 PNG 亦一致。材質僅輔助辨識，不新增幾何。

## 驗證收到的封裝（唯讀）

```
python validate_model.py
```

也可將從獨立交付管道取得的 manifest SHA-256 傳給 `--expected-manifest-sha256`。預設 gate 不更新報告：必須完整檔案集與大小／SHA-256 一致、無新增或遺漏檔、檢查器與報告來源吻合、當前預覽／Blend／細節檔符合報告，並有通過的竄改負控制。`SHA256SUMS` 不自含；manifest 不自含，外部 pin 才是獨立的信任起點。

## 在可寫副本重新執行數值檢查

不要在原封裝中直接重跑產生報告的程式。使用副本，環境須有 `requirements.txt` 套件、g++（C++17／OpenMP）及 Blender 4.3.2：

```
python check_raw_mesh.py
python check_component_detail.py
python check_negative_controls.py
python check_dense_surface.py
```

最後一行預期退出 1，原因必須仍是 1,430 個原始短法向；不能盲目忽略其他錯誤。確認上述完整結果後續跑：

```
python check_fixed_roots.py
python check_root_intervals.py
blender --python-exit-code 1 -b scene.blend --python probe_scene.py
python check_reproducibility.py --render
```

若要重建模型和場景，亦只在工作副本執行 `python build_model.py` 及 `blender --python-exit-code 1 -b -t 1 --python render_preview.py`。Python 檢查不依賴可被 `-O` 移除的 assert；Blender 指令必須保留 `--python-exit-code 1`。

`seal_package.py` 是明確的作者封裝操作，不能用來「驗證」收到的凍結包。它不會補跑過期數值報告；變更 checker 必須先重跑相應報告。首次建立竄改測試夾具可用 `seal_package.py --author-bootstrap` 與 `check_gate_negative_controls.py --author-bootstrap`，這是作者預檢，不是正式凍結通過。之後重新封裝、以無旗標的 `check_gate_negative_controls.py` 重測正式 gate，再封裝最終報告；交付前只用無旗標 `validate_model.py` 驗證。

隱私掃描綁所有實際配送檔；只排除根目錄自身報告、manifest 與 SHA 清單的循環雜湊，再由 manifest 綁定。PNG 僅允許解析度及固定採樣資訊，不附來源照片、原始圖面、私人路徑或內部審查紀錄。所有深挑簷、格梁與凹槽上緣仍須切片檢查支撐；沒有特定機型 G-code，也沒有完成實機列印。
