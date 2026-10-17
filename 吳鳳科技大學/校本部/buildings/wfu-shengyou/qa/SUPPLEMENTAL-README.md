# 外層工具補充與單份還原

主科學 PUBLIC-COPY-MAP.json 保持原bytes。SUPPLEMENTAL-COPY-MAP.json 收25個補充邏輯位置，其中7個工具／參照表沿用主包既有canonical bytes，只新增18個unique檔案，沒有第二份restorer或generic scanner依賴。

從building根目錄使用同一安全入口，在自己的既存父目錄下建立全新輸出：

```sh
python -B qa/restore_scientific_layout.py --public-root . --copy-map qa/SUPPLEMENTAL-COPY-MAP.json --out /your-owned-directory/wfu-supplemental
```

還原後 qa/tools/full-package-privacy-v1/ 內有原scanner、test、六個精確hash綁定的sibling依賴及reference表；原程式與固定來源hash未改。以還原後scanner執行時，--public-root仍指向待查的building根目錄、--copy-map-sha256填主科學map的實際SHA、--out放該根目錄以外的新結果檔。scanner只驗本棟與歷史controls兩個已聲明的精確界線，不批准發布或證明能偵測所有秘密。

SUPPLEMENTAL-RESTORE-PROOF.json記錄本次正常／-O各25檔實際還原、逐檔hash及exact fileset驗證；主科學1528 logical完整還原另見 restore-replay/public-restore-proof.json，新247-member controls兩模式safe extraction／bitwise重建見 new-controls-replay/replay-proof.json。沒有額外渲染或幾何重跑。
