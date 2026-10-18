# 已失敗的三件原型：不可列印

本目錄只保留真實失敗歷程，正式方案在 [v2](../v2/README.md)。未產生完整三件方案，不能使用此處的 A-failed.stl。

原構想於 z13.4、25.4 切成三段，並向上段加底板以承接房間外伸。然而直接使用 Manifold.split_by_plane 再匯出 binary32 STL，在第一件 A 即失敗：第一試 430 faces、22 components、watertight=false。第二試明示加 0.00001 mm 幾何 simplify（沒有調 QA 門檻），仍 384 faces、1 component、watertight=false。兩試的原 source、parameters、A STL 及實際錯誤輸出均留在 qa/attempt-01、attempt-02。

沒有把它們修成通過，也沒有把未完成的 B／C 當已驗證。改採 v2 的原網格盒形交集及五高度帶／六物理件，不加底板、不封露台；原 v4 與其全部 false／exit 1 未改。
