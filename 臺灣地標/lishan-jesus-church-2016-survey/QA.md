# 驗證範圍

`QA.json` 檢查有限座標、正面積、封閉／一致繞向、單一連通分量、邊鄰接、STL 重開封閉，以及 3MF 單位／網格／材質一致性。`review/model-independent-check.json` 額外核對來源主尺寸、低翼高、修補屋面區域、通廊真正空隙、W9 工程上移、側翼門可見外緣及未知後塔細節排除。

九視圖需獨立人工查看，不能由幾何程序代替；結果在 `review/geometry-visual-review.json` 與 `review/openings-visual-review.json`。乾淨重建比對在 `REBUILD-QA.json`；BLEND 重開比對在 `BLEND-QA.json`。

這些是數位檔案與約定建模範圍驗證，不代表原建築完整測量、精密歷史復原、結構安全或物理試印通過。
