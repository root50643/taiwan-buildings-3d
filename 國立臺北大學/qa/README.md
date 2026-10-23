# 首批獨立數位幾何審核（歷史快照）

> 2026-10-23：圖資大樓已同 identity 替代為全組近似；以下單殼/150mm/415層是舊主體段結果，不適用新版。新版為1連通solid與7閉橋腔，原單boundary gate FAIL如實保留、cavity-aware另驗；非直接列印就緒。請見[現行圖資大樓 QA](../三峽校區/buildings/ntpu-library-main-block-segment/QA.md)。

兩件原始STL均通過：單一連通表面殼、每邊兩面、vertex link單環、正體積、法向與繞序、含底座最大150mm。獨立暫存重建的STL SHA與交付原件一致；saved Blend實際網格與交付STL一致。

- 圖書館主體段：415個0.2mm層
- 心湖會館：158個0.2mm層
- 共573層輪廓degree2閉合，個別與組合Polygon有效
- 0.8mm參考寬度形態opening，以1mm層距輔助篩檢：最大損失分別0.1946%、0.5217%

[逐件SHA與獨立重建／輪廓／薄特徵結果](independent-audit-summary.json)

這不是實體試印、全面壁厚保證或Cura/Prusa實際工具路徑。本件的屋頂、跨橋、露臺等仍須實際切片檢查支撐與橋接。模型內的model-info保留凍結當時的審核狀態；本頁提供後續獨立審核結果，不改寫凍結附件。

[返回學校圖鑑](../README.md)
