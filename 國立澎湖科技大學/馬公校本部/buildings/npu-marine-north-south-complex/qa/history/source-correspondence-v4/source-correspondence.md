# 來源平面與候選模型對照

這是七頁官方平面與候選生成碼的對照，不是實測復原或製造通過證明。疊圖只含原創數位描線與候選輪廓，未嵌入來源 PDF/照片像素。原始來源 SHA 與逐頁目視結果見 `source/plan-review.json`。本檢查不修改幾何。

檢查輸入：`build_model.py` SHA-256 `5b8707c4d7fc2a48adea8d3b04fa24fe696edaf0654c111b107e4e9242ec7a77`；`plan-trace.json` SHA-256 `176b633c5fb48135c5e236c732ee23c5673393dc9b375951d2322eb52a8c6467`。生成碼 N/NU/S/H/B 與 trace 的五組 literal 座標均一致：`True`。

## 直接支援的關係

- 北棟四層、南棟三層；北主條與右腿、南 L 主體均保留。
- 北入口上方的左側突出翼自模型 3F 開始，1F/2F下方保留柱廊通空。
- 國際會議廳與大廳相連，只有低體與獨立坡頂；沒有把2F/3F頂蓋投影誤當樓層，也沒有延伸到4F。
- 橋只有二樓一條長豎段再右轉進南短翼；院地與橋下通空，主橋長度約束吻合。

## 座標與偏差

候選南2F→北2F平移為 `[217, 261]` 像素，獨立描線為 `[218,261]`；x差 `-1` 像素，在約±2像素手動描圖容差內。候選橋轉折中心約 `[88.9, 91.1]` mm，對照約 `[88.8,91.4]` mm；這些是北主條100mm規格下的模型座標，不是建築尺寸。

南端樓梯目前候選 x範圍 `[140, 145.7]` mm，來源描線約 `[140.0,145.7]` mm；中心差 `0.00` mm。初版 `136.5..142.8` 的約−3.2mm位移是原始未通過旗標，必須保留。當前判定：`WITHIN_MANUAL_TRACE_TOLERANCE`。

初版候選橋轉折省略了官方圖上向左與向下的短凸，保留主要 L 路徑；原始旗標保留。南1F圖明確畫出的側邊外部入口附屬在初版未建模，是已知次要構件省略，不能改稱未知設備。放大像素可見上端與下端兩處短踏步線，中段為長平行邊線、箭頭與回折/弧形平台，形態更像低矮入口無障礙坡道；不能據此做二樓高層外梯。若補低矮平台/短階/坡道足跡，1-2mm起伏也只能明示為模型估計。南內角小翼深度比獨立描線短約1mm。會議廳以八頂點扇形簡化，向左範圍約少0.6mm、圖下緣約少1.1mm，細節入口/階梯未逐一復刻。

## 七頁對照

當前橋短凸狀態：`RESTORED_IN_CURRENT_CANDIDATE`。當前南側入口附屬狀態：`LOW_RELIEF_ADDED_HEIGHTS_AND_ROUTE_SIMPLIFIED`。08低入口附屬保留約x159.5..175.4/y83..127的包絡與兩短階，z0.4..2mm全為估計；其環形足跡大幅簡化原圖回折、中段側支與下部弧形平台，不能宣稱完整坡道動線或無障礙規範相符。

### 北棟第 1 頁

- Long bar + image-right return：`SUPPORTED_APPROXIMATE_OUTLINE`。N polygon preserves long bar100 x34.1 and short return to48; independent trace about100 x34.1 and47.7.
- Lobby-connected fan conference hall, single occupied level：`SUPPORTED_TOPOLOGY_HEIGHT_ESTIMATED`。H is unioned only into north-lower z0..11; separate roof z11..15. No additional room body at z18 or above.
- Entrance beneath west upper wing：`SUPPORTED_VOID_COLUMNS_ESTIMATED`。N has no filled body in x0..22,y34.1..48; six enlarged columns and narrow ground ties are explicitly generated. Exact count/thickness not measured.
- Fine fan shell/entry steps：`SIMPLIFIED`。H is an eight-vertex approximation; source polygon has secondary stairs/entrances. Image-left extent model41.2 versus trace41.8 and south depth about1.1mm shorter.

### 北棟第 2 頁

- Second-floor bridge at right-return end：`SUPPORTED`。B starts near(88.9,48), runs to(88.9,91.1), then right to x106.2. Source approximately(88.8,47.7) to(88.8,91.4) to106.4.
- Bridge turn nubs：`RESTORED_IN_CURRENT_CANDIDATE`。見保留旗標 BRIDGE_ELBOW_STUBS_OMITTED
- Conference hall projection, not 2F room：`SUPPORTED`。Roof is a low separate part; no hall room stacked with upper floors.
- West porch remains unfilled at 2F：`SUPPORTED`。Upper west wing begins at z18, corresponding to modeled3F; lower piloti extend through two modeled levels.

### 北棟第 3 頁

- West occupied wing above porch：`SUPPORTED_APPROXIMATE_OUTLINE`。NU includes x0..22,y34.1..48 from z18; source independent trace width22.2 and end y48.
- Hall radial roof projection：`SUPPORTED_INTERPRETATION_ROOF_ESTIMATED`。Low polygon roof, no hall3F room. The rendered roof slope is a design estimate; plans only constrain horizontal fan shell/roof.

### 北棟第 4 頁

- Fourth floor bar and end wings：`SUPPORTED`。NU spans z18..36 across two model stories; bar does not incorrectly shorten at4F.
- No hall extension at4F：`SUPPORTED`。H roof ends atz15; hall does not extend to the main roof.
- Roof fins and parapets：`ESTIMATE_NOT_MEASUREMENT`。Heights37.2/38.3/43mm are explicit generated estimates, not extracted from this plan.

### 南棟第 1 頁

- Principal L body and inner stair/lobby return：`SUPPORTED_APPROXIMATE_OUTLINE`。S preserves53.6mm total width,34.1mm mainleg width,68.9mm body length; west return is simplified.
- No ground-floor bridge room：`SUPPORTED`。Bridge startsz9; no common slab or body fills the courtyard/undercroft.
- Exterior1F entry ramp/short stairs/platform：`LOW_RELIEF_ADDED_HEIGHTS_AND_ROUTE_SIMPLIFIED`。見保留旗標 SOUTH_EXTERNAL_ENTRY_APPENDAGE
- Southern terminal stair position：`WITHIN_MANUAL_TRACE_TOLERANCE`。見保留旗標 SOUTH_TERMINAL_STAIR_POSITION

### 南棟第 2 頁

- Bridge enters left tip of short wing：`SUPPORTED`。B right end x106.2 shares the S western edge around y88.9..93.3.
- Shared scale and two-plan registration：`WITHIN_MANUAL_TRACE_TOLERANCE`。Candidate translation[217, 261]; independent trace[218,261]. Difference in x is -1px; declared uncertainty2px.
- Bridge elbow small branches：`RESTORED_IN_CURRENT_CANDIDATE`。見保留旗標 BRIDGE_ELBOW_STUBS_OMITTED
- Inner west return and grid projection：`SIMPLIFIED`。Return endsy102.7 versus trace103.7; grid/roof projection below is omitted as secondary roof detail, not occupied room evidence.
- Terminal stair：`WITHIN_MANUAL_TRACE_TOLERANCE`。見保留旗標 SOUTH_TERMINAL_STAIR_POSITION

### 南棟第 3 頁

- Three-story L：`SUPPORTED_HEIGHT_ESTIMATED`。S bodyz0..27 is three9mm model stories; floor count supported, height unknown.
- No3F bridge：`SUPPORTED`。Bridge lid top17.5 is below modeled3F startingz18; no bridge stacked to3F.
- Terminal stair and small corridor-end protrusions：`SIMPLIFIED_WITH_RETAINED_FLAG`。Terminal stair remains part of S; small corridor-end protrusions are simplified and the stair displacement flag remains in QA history.

## 估計與補證界線

模型9mm層距、北入口六柱及加厚尺寸、橋下9mm、會議廳11mm主殼/15mm屋頂最高點、屋面鰭片與女兒牆、窗與實心放大欄杆節奏、橋柱位置均是顯示與製造用估計。官方平面沒有完整尺寸鏈或屋頂施工高度。這些值不得美化為測量結果、共同真實層高或2026現況。

來源相符不等於網格/接合/薄壁/支撐可達性/切片通過；未實印與試合不得宣稱成功。色區或預覽有色也不證明四色可列印。圖像採Pillow原創繪製，檔內只含通用Software說明，不記錄私人路徑。
