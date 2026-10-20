# 驗證紀錄

- 原始二進位 STL：只合併完全同座標頂點，不補洞、不刪面、不修法向。1,520 面、750 頂點；零退化／重複面，每邊兩相反方向面，每頂點 link 為單一環，單封閉連通殼、正體積。
- 全域 0.2 mm 高度截面加最上端 0.001 mm：615 層，輪廓有效，每正面積連通區保留原始輪廓後作 0.4 mm 侵蝕均非空，無薄特徵豁免。
- 局部獨立檢查：實際 STL 裁出外凸窗框，另單獨裁窗梃及中橫桿，隔離帽簷外緣及柱凹槽肋，使用水平／法向截面作 0.8 mm 篩查。本次抽樣局部失敗截面 0，並不等同完整最小壁厚證明。
- 3MF 與 STL 三角頂點／次序一致；lib3mf strict 零警告、合法流形，七種材質對應及單材質修改另存重開驗證通過。
- Blender 單模型網格與各面材質逐一核對；修改一材質另存重開不影響其他材質或幾何。無外部貼圖、連結或內嵌腳本。
- 五張預覽由交付網格直接渲染，所有頂點在畫面內。重開交付 scene.blend 重繪前視角，移除僅時間／文字 PNG metadata 後位元一致。
- 獨立目錄重建 STL、3MF、mesh.json、palette.json、設計參數逐位元一致；verify_package.py 綁定所有 QA 到交付雜湊。

沒有實體試印、未做特定切片器支撐分析，也沒有真實尺寸測量。高柱穩定、上緣橋接、挑簷與圓角末端需另判斷。抽樣截面測試不可宣稱全模型免支撐或所有局部厚度足夠。

數值報告：qa-topology.json、qa-layers.json、qa/local-features.json、qa/exchange-validation.json、qa/scene-validation.json、qa/render-manifest.json、qa/render-reopen-validation.json、qa/isolated-rebuild.json。另見 qa/source-review.md 的獨立實景審查。
