> 本文保留 e45f8d6 原候選的結果。R2 最新修訂及風險請讀 [RISK-FOLLOWUP.md](risk-followup-e45f8d6/RISK-FOLLOWUP.md)；文中舊 layer-check 對應 `risk-followup-e45f8d6/input-layer-check.json`，根目錄檔案已更新為 R2。

# 旺宏館候選來源吻合覆核

2026-10-18。已實看候選 `previews/front.png`、`roof.png`、`elevation.png` 及變更後 `build_model.py`，對照本工作環境先前實看的建築師 R-03、B-02 原像素。這是來源吻合覆核，**不是外部發布核准、幾何 QA 或列印合格判定**。未修改模型。

| 項目 | 結果與限制 |
|---|---|
| 後高前低分段屋面 | 有來源支撐。生成器現在沿 y-z 定義屋面，從前段 y=-30、z=39.8 向後 y=-7、z=50.8 升高，修正舊 x-z 三角屋脊的主要方向；較低前段亦保留。節點高度、折接位置、前緣小幅上翹都是候選估計，不能聲稱測繪曲率。 |
| 頂層退縮、弧形露台 | 有來源支撐。預覽可見上層較下部橢圓收小，外側有連續可讀的平台帶；來源只證明照片可見的弧側，不證明實物露台整圈連通或候選寬度精確。 |
| 高側窗帶 | 來源可支持它位於主降坡後緣、形成高位弧形帶，並非屋頂設備新增樓層。候選表現成較窄的弧帽/凹槽；照片的帶較寬且連續彎曲，候選寬度、端點及後棟交接仍是低細節估計，不能稱已精確復原。沒有來源理由再補不明量體。 |
| 色彩與分格 | 藍灰色只協助辨識候選上層與屋面；不代表實際材質、透明度或玻璃分格。來源並未支持候選每個分格。 |
| 後棟 | 本版明確 deferred，未以 6F 全高外推。現有淺開書形與深 L 形/內凹弧的差距仍留待跨樓層來源對應後處理，不能宣稱本版已修正。 |

整體判斷：本次前棟的三項方向性改變可作為來源支持的低細節候選，仍應保留高度、曲線、露台連通及高側窗帶形狀的估計聲明。未實際切片、未試印；支撐、薄特徵及幾何檢查須以另立驗證記錄為準。

來源：[建築師項目頁](https://www.archasia.asia/projects/nthu-learningcenter)、[R-03 原圖](https://cdn.prod.website-files.com/6871392ea22dedab1d41e5cb/6881f45ace041d79e8525603_1.3.18R-03.webp)、[B-02 原圖](https://cdn.prod.website-files.com/6871392ea22dedab1d41e5cb/6881f50afcdd0f348c08eb4e_1.3.18B-02.webp)。照片年代仍依前份 [獨立來源覆核](INDEPENDENT-SOURCE-REVIEW.md) 的限制，不宣稱 2026 現況。

## 固定本次所看檔案

| 檔案 | SHA-256 |
|---|---|
| `build_model.py` | `30e00961538e09e75f6948becd42f2d12ff633b64fb154af7b2821bf8ef28221` |
| `previews/front.png` | `3f32747bc2fd8e0a6b61a9b7816eac594c0ba954efc8abb55f0247e07060fbef` |
| `previews/roof.png` | `9c72fb23555f01359f6237422aed5cf608e472a51b1665c4274b02ee2a2ace55` |
| `previews/elevation.png` | `0273d6eea1e86dc41c136b85ecdbf9310b804ebccc9edd7afd8aebb56e0a18e4` |
