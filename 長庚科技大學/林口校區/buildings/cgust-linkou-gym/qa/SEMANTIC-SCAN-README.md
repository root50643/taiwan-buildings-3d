# 語義掃描工具與單份還原

主科學與原補充map的bytes都保留。本map列15個logical位置，新增9個unique payload，其餘重用原canonical。

    python -B qa/restore_scientific_layout.py --public-root . --copy-map qa/SEMANTIC-SCAN-COPY-MAP.json --out /your-owned-directory/cgust-semantic-scan

還原後執行qa/independent/public-package-privacy-v10-semantic-labels/scan_public_package.py，--public-root仍指向完整building包。此窄版只辨別固定SHA檔案內的測試相對路徑及空檢測標籤，以AST／typed pointer與精確span驗證；真私有值、位置改動或hash不符均拒絕，通用pattern未放寬。原scanner、差異與正負控制保留。

SEMANTIC-SCAN-RESTORE-PROOF.json記錄正常／-O各15檔實際安全還原及全fileset／size／SHA核對。原612檔不變；本步未重跑幾何或渲染，也不批准發布。
