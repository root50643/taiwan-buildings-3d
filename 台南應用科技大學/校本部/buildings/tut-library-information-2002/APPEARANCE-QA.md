# 本次外觀重建QA

由原STL重新建立，不沿用先前遺失配色版本的QA。基準commit 8388c665eb19c2857a0f29143a8713b801c3cea1。原STL SHA256 626aa6e3f19698098e05275514aa5b5db876fe8301107c15c253dd65a142d71f。

- 照片實讀，Flickr 9357548628，2002-12-08；SHA256 7e8f88b28b3636041f08e2110c1fc5b75bd6e505b3f6d50104f11a94024b3173。未公開原照片。
- 完整逐面對應記於appearance-mesh.json的source_triangle，Blender同名face attribute亦保留。每原面面積總和及共面距離驗證，單殼、閉合、法向一致；未改原STL。
- 新標準Core 3MF以base materials逐面著色。Blender與lib3mf實際材質編輯／存檔／重開均測試；後者預設6位小數。每邊2面、vertex-link單環、零重複面、零退化、零重合頂點、單殼與Euler數均記錄。沒有以提高精度掩蓋問題。
- 四張1400×1050 PNG由最終配色重繪，四視角像素已開圖檢查；底座完整入框，灰背／頂面為刻意保留未知。
- 原正式QA文件為歷史證據，全部原封保留。本次原source／STL／Blend另跑驗證見appearance-baseline-recheck；跨版本Blender渲染PNG不保證byte一致，須以該報告逐項結果解讀，不修改歷史QA。
- 歷史數字：428層527 polygons；2根入口柱88跨層corner樣本，非88根柱；最大角損3.920441644679209%、保留96.0795583553208%、真角0.41mm外0。作者40600樣本162400控制，獨立6058面×7=42406點169624控制。最低0.853271291207mm僅有限取樣，不是全域最薄證明。
- 尺寸98.8893737793×150×85.6687393188 mm；46m為名義高，非測量。跨年2002/2018/2022/2025，不稱完整2002或2026現況。

未做切片器工具路徑驗證或實體試印。原有列印化簡／例外與所有不確定性保持，未新增批准。

## 最小源包離線重建

解包至新目錄獨立執行rebuild_all.py，幾何／逐面材質／provenance／全部QA／四張PNG bytes與本輪主包完全相同；3MF未壓縮XML相同。實際單材質編輯測試重跑通過。原source重建STL、原Blend和8張原灰模PNG亦重新核對全部通過，完整報告分別見appearance-reproduction-qa.json與appearance-baseline-recheck/original-validation.json。
