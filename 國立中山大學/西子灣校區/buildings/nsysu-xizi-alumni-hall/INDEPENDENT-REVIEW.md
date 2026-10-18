# 西子樓固定 SHA 獨立覆核摘要

2026-10-18 的獨立增量覆核為 **GO，限下列六個固定 STL、供應印向及指定製造條件**。受審候選提交為 `b627db61613b2b8e1b143adc93eac940132a4df1`。公開副本保留這六件及原單件的所有 STL 位元組；場景／PNG metadata 和執行紀錄路徑的公開化另見 [PUBLICATION.md](PUBLICATION.md)。不把數位 GO 當作實體試印成功。

| STL | SHA-256 |
| --- | --- |
| `01-base-floor1-upright.stl` | `bc2ac743cacb4cb9584a62d79df2541b2cb75a463e4bc43d10b2ad9e280f0243` |
| `02-floor2-slab-inverted.stl` | `4440eeca45530769bf11b8e4094c82a0744e6ba160d692fda7fbf9f8f0f30ddd` |
| `03-floor2-upper-upright.stl` | `b1d6d8e1ffa61198adc1898d8fe5ff5f47e7ea011fbc67d1b87108075d80d6e6` |
| `04-floor3-slab-inverted.stl` | `720c05949b35a68535a5aff298507e32b78b2a449335b64a0661eafa749d8957` |
| `05-floor3-main-and-tower-upright.stl` | `8ecc913447812bc613f469be6572bd56f9fdd1de6555a62886b7927ac3507bd1` |
| `06-floor3-diagonal-rail-upright.stl` | `c2527780d644eef28a4a5431a40b6027541123d9c29eef0dc60be83da615b8ea` |

## 獨立結果與保留失敗

- 六件均封閉、單一連通、正體積，獨立重建位元組一致。精確 AABB 候選面對檢查未見越界交集。93 個原數值旗標仍為 9 分離、24 合法共邊、60 合法共點；01–05 原 CLI 仍 false／exit 1，06 為 true／exit 0，沒有更改門檻或改旗標。
- 組回外框約 150 × 101.461418 × 47 mm，體積差約 +0.000109749 mm³。獨立有限截面與表面採樣支持外形保留，並非連續表面的形式化 Hausdorff 證明，也不是實物配合公差。
- PrusaSlicer 2.9.6 六件實際切片並獨立重切，各 exit 0；獨立 G-code 與候選逐行比較僅產生時間不同。支撐 TYPE、支撐正擠出及 raft 均為 0。
- 01 仍有 19 條短 Bridge 線段，其餘五件為 0。按前層宣告線寬掃掠，最大連續缺口 **0.2250010581 mm**；固定半線寬 0.225 mm 法為 0.2250000581 mm。這是預定路徑分析，沒有觀測實際熔料成形。正常 Z 層增量為 0.15 mm；Bridge 可採 slicer 的 thick-bridge 特殊 WIDTH／HEIGHT，不能將全部擠出截面都稱為 0.15 × 0.45 mm。
- 15% gyroid 探索的 8.467213 mm 缺口紀錄保留，但 **GO 不採此路徑**。建議是 100% rectilinear，不是少量稀疏填充。
- `qa/design-probe/assembled-union-verification.stl` 的兩個零面積三角形失敗仍保留，不可列印；只列印 [v2/models 的六件](manufacturing/v2/models/SHA256SUMS)。初次 Euler 場景的矩陣 false 與修正後同 checker 結果均保留。

## GO 製造條件

1. 100% 尺寸、一次一件，使用供應 STL 的 z=0 印向，只允許 XY 置中。02、04 已倒印，切片時不可再翻面或自動躺平；組裝時才翻回。
2. 單噴頭 0.4 mm；首層及正常層 Z 增量 0.15 mm；一般線寬 0.45 mm；100% rectilinear；3 壁；上下各 4 層；3 mm 外側 brim；結構支撐及 raft 關閉。禁止任意縮小或改粗層高後套用本結論。
3. 分件尚未形成上下露台通道時，從外側分段移除 brim，夾持大片牆體，避免向 1.2 mm 欄牆、細柱和 0.15 mm 接觸腳集中施力。無結構支撐要穿過約 7.2 mm 通道抽出；這不是已測拆除力。
4. 01→02→03→04→05 先乾組再依實際材料薄層膠合；02、04 翻回組裝向；06 最後沿 04 斜向外緣裝上。無插銷或壓入配合保證。層量化、翹曲和膠層會影響實際接合與高度。
5. generic Marlin2 G-code 僅為覆核證據，示例 PLA 200°C、床溫 0°C 不是校準真機設定；使用者須按自己的機器、材料、溫度、速度、冷卻、黏床及啟停碼重切，並核對床區和實際路徑。若需新增結構支撐，須另核可達和可移除，不能套用本路徑的零支撐結論。

**尚未實體試印、拆 brim、乾組、膠合或測黏著強度。原單件仍需支撐，本六件結論不能套回原單件。** 兩種交付方式合計一套模型，不計為七棟或七套。

機讀摘要見 [qa/independent-review-summary.json](qa/independent-review-summary.json)；操作入口見 [六件製造說明](manufacturing/v2/README.md)。
