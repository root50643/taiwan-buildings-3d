# 切片覆核證據區：非真機通用列印檔

本目錄所有 G-code、INI、CLI 紀錄及路徑圖只供重現與覆核，**不是已校準、可直接用於任意真機的列印檔**。主要交付是 [六件 STL、生成器、設定與操作說明](../README.md)。請依實際印表機與材料重新切片，核對溫度、床區、黏床、速度、冷卻及啟停碼。

- [100% rectilinear 固定條件](solid100-confirmed/SLICE-REVIEW.md)：獨立 GO 路徑，六件支撐擠出0；01保留19條短橋，非零橋接。
- [15% gyroid 探索](gyroid15-exploration/SLICE-REVIEW.md)：保留8.467213mm缺口的原紀錄，GO不採用此條件。

generic Marlin2、示例 PLA 200°C、床溫0°C；不得視為真機設定建議。未實體試印或試組裝。公開副本已遮罩私人路徑並加警語，非註解命令不變；歷史候選SHA與當前公開SHA的範圍見 [PUBLICATION.md](../../../PUBLICATION.md)。
