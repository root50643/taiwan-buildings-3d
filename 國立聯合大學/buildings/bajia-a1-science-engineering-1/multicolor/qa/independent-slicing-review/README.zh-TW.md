# 獨立實切覆核：選存證據

固定候選 `c6983ff34091addf36166c7b7ce05d764a76ad8e`，主 PRINT SHA-256 `7cf863dd73dfa74fefd9522455cc79f01fcf0e58ca348cdda406884a760ee2df`。這裡選存既有獨立覆核的報告與數據，未重新切片、重建或渲染，也未改模型及設定。

**模型／分色檔案條件 GO；無支撐製造路線 NO-GO；開支撐只完成生成比較，尚非真機放行。** 四模型色已用滿四工具；獨立支撐耗材須合併一色騰出工具，或另有驗證過的硬體方案。實機仍須重切、校準、驗證黏結及支撐可移除性。

- [實切報告原文](3MF-SLICING-ACCEPTANCE.md)：固定輸入、兩次 CLI 切片、警告與最小後續。
- [機器可讀結論](slicing-acceptance-summary.json)：有限 GO、NO-GO、層高與未驗範圍。
- [料道解析與原 39 個旗標](toolpath-analysis.json)、[兩個薄區抽核](thin-feature-probes.json)、[Z8.1 截面兩側敏感性診斷](midplane-sensitivity.json)。抽核不是所有 422 個玻璃殼或全部支撐的覆蓋證明。
- [無支撐 stdout 公開副本](slice-support-off.stdout.PUBLIC.txt)、[開支撐 stdout 公開副本](slice-support-on.stdout.PUBLIC.txt)：保留警告及處理行，只將私人 runtime／輸出路徑替換為標明的佔位字樣。
- [來源與轉換雜湊](evidence-provenance.json)：五個報告／JSON 為逐 bytes 複製；stdout 列出原 SHA 與公開副本 SHA。

這是選存快照，原報告末尾列出的完整 argv、raw 執行紀錄、設定及幾何審查仍在獨立本機證據中，並非每個檔都包含於此目錄。診斷 G-code 仍含工具選擇、移動、擠出及風扇命令；即使停用溫度自動命令與機器宏，也不可送印，且不在公開包中。JSON 中的 G-code 名稱、行號與 SHA 僅供追溯，不是可用送印檔。
