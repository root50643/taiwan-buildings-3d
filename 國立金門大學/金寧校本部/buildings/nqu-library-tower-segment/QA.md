# 數位QA、原嚴格結果與獨立限定裁定

## 原資料與可重跑腳本
全部檢查讀交付原STL，無repair、無buffer(0)/make_valid；源布林及源末段三角化不改讀入STL。`python run_checks.py`逐支重跑，記錄原exit與false。需要Python套件、Blender4.3.2及g++（OpenMP）。完整全密CSV與沿面報告gzip保存，可用Python gzip.open(path,'rt')直接讀；未刪列或降低數值精度。

- 原9032三角、單一連通表面、每邊2面、vertex link單環、原儲存法向、正體積與150mm全部通過。
- 相反共面AABB/法向篩查：0候選、0正面積重疊，門檻詳opposing-faces.json，非無限精度全域定理。
- 0.2mm、起始0.071mm：750層、952原Polygon；輸入個別/組合有效，erosion/opening全保留單核，零分裂/消失。
- 每原面10點共90320；修後原法向首段最小0.999999880791mm，零<0.8mm。這是有限採樣，不是全方位最小壁厚。
- 33條指定原面根射線：新門格背接/寬/底根、新窗框背根、山牆端向下與真法向、加厚谷板、陽台孔上楣、外角板根；首實體段/前外/內中/後air高精度控制全過。根長不跨空氣找遠牆。
- 獨立源重建STL SHA一致；Blend幾何一致；7張實際STL PNG逐byte及逐pixel重建一致。已停用時間/檔案路徑等易變PNG metadata。

## 作者嚴格false原樣保存，另列獨立限定裁定
1. 44筆原Polygon opening損失>1%：36山牆端、8屋面外角，z135.271–136.871mm（非每層都有同數）。最大2.213313498497953%，最少保留97.78668650150205%。原頂點mask與去共線真角mask分列；去共線只用於mask，不改原Polygon/opening。損失均在真角0.41mm內，不能因此自行批准例外。原component-detail passed=false/exit1。
2. 原固定方向parity篩出63旗標；原46「winding回0所以正常」的體積分類撤回。獨審按exact-source原面區間確認作者63個after探點全部落在正長度外表面；面上winding的0或1均不能裁定體積/air。原數值與false/exit1保留，flag-winding中的confirmed只代表數值符合舊預期，不代表不在表面。
3. 擴大全90320射線的完整第一幾何段與後續區間，122條射線有3551原三角沿面區間；第一幾何段無正長度沿面。每段10/50/90%點與三檔原法向±1e-6/1e-5/1e-4mm側偏、前實體段與後段分區，75547點包含10653個沿面點（只留診斷、不判內外）與64894個非沿面控制（63918側偏、854首段、122源外）；64894控制全通。原face/sample以long-double精確重算重心1/3，避免float64起點把沿面誤判37mm材料連續段。沿面本身的winding不作內外結論，沿面長度不作厚度。
4. all-after-boundary-candidates是單探點距面近候選（123），不能代替完整區間（122）；兩口徑不混。原dense-short-chords passed=false/exit1與flag-winding unresolved/exit1保持，新增證據不改原嚴格結果。

## 版本與限制
root已核新增窗/門/孔及屋板底下移0.4mm的外觀；另已完成44角損及沿面證據的獨立驗證與限定裁定，精確範圍見獨立補充；原作者嚴格結果不改寫。舊freeze-v3保持不動。本修版只銃樓段、非全館，窗位與未知面限制詳README/sources。底座朝下，外挑陽台/屋簷/曲牆需支撐檢查；未實印、不保證免支撐、勿任意縮小。

## 獨立密測分類更正（文件增量，幾何未變）
獨審每原面15點共135480點，最小原首段0.9999998807907104mm、零<0.8mm；完整後區間132條沿面／3581原三角段。73個coarse旗標中71個after探點在正長度外表面（涵作者原63全部）；其餘2個是face8717/sample11與face8715/sample12，在t7與t51的共享邊正負法向同點切觸。72個開區間winding控制支持中途仍在材料內，到t58才外；不能把孤立切觸當首出口。21486個沿面側偏控制驗內1/外0。這些是有限原面與指定射線證據，不是全域壁厚或實印保證。原作者46/17只按單點數值分組的解釋已被本節取代；原CSV、JSON與strict false未改。

封包排除意外生成的Python bytecode/cache，不改STL/Blend/PNG。run_checks.py會設定PYTHONDONTWRITEBYTECODE並拒絕公開cache；重跑亦可使用python -B run_checks.py。獨審分類摘要見independent-classification-correction.json。44 opening角損與上述限制已由獨審及root完成限定裁定，原作者結果不改寫。

[獨立修版覆核與限定例外](INDEPENDENT-REVISION-AUDIT.md) · [獨立密面摘要](independent-dense-summary.json)
