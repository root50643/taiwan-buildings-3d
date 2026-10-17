# 補充工具與單份還原

主科學PUBLIC-COPY-MAP.json的原bytes不變。此補充map列69個logical位置，只有50個新unique payload，其餘以同bytes canonical復原；沒有第二份歷史archive或reference表。

從building根目錄，在自己擁有的既存父目錄下指定全新out：

    python -B qa/restore_scientific_layout.py --public-root . --copy-map qa/SUPPLEMENTAL-COPY-MAP.json --out /your-owned-directory/cgust-supplemental

還原後的qa/independent/public-package-privacy-v10-canonical-table/scan_public_package.py使用已明列canonical table位置；舊scanner及差異保留。scanner的--public-root仍指向building主包，結果放外部新路徑。不要直接解壓歷史malformed controls fixtures。歷史豁免僅對其固定domain生效，沒有擴及本模型。

SUPPLEMENTAL-RESTORE-PROOF.json保留正常／-O各69檔實際安全還原、全fileset與逐檔hash。主1269 logical完整還原與新controls恢復另有原證據；本步沒有重跑幾何或渲染。這些檢查不批准公開，也不證明實體列印成功或任意方向全域最小壁厚。
