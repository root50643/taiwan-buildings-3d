# 中央太空及遙測研究中心館｜有限實照彩色增補

## 範圍與原幾何保留

只為原三層U院太遙館補材料，不併入另列二期。原5977頂點／11966三角面、transform及尺寸完全不變；原STL、OBJ、scene.blend、scripts、三舊圖與QA保留。彩色另有3MF／BLEND／五圖；雙README第一章留原表加彩表，首頁／校級鎖定代表不變。

## 實際讀到的來源與失敗界線

本輪親看原sources列的[01前院實照](https://upload.wikimedia.org/wikipedia/commons/4/46/2026.08.14_ROC-NCU_Center_for_Space_and_Remote_Sensing_Research_01.jpg)與[05屋塔／碟面實照](https://upload.wikimedia.org/wikipedia/commons/6/67/2026.08.14_ROC-NCU_Center_for_Space_and_Remote_Sensing_Research_05.jpg)。正式原始連結仍以原sources.json及此包來源核對為準。只有01、05成功讀取，不宣稱讀了03、04或全四張；校方無障礙CSR圖回503後已停止，沒有繞過或把失敗當成無外觀證據。

照片為原記錄總統府經Commons公開實照，來源作者／授權依既有sources；既有01記8月14、05記8月13而共同檔名14日的差異保留，不自行校正時區或拍攝日，也不把檔名當新查證時間。本輪沒有重驗所有來源頁／EXIF或重讀防災圖冊，不稱完整2026現況。來源照片不包入公開檔。

## 有據材料與未知範圍

原向前翼端、內院牆淺灰米磁磚家族，原突出箱遮陽與門廊米灰。原窗背灰藍綠不透明窗／簾proxy；箱遮陽裡暗凹及入口為暗影空間，不是額外長條玻璃。未知外側後牆及廣大平屋頂中性，照片只見局部屋面鋪裝不足整頂定色。

屋塔及右小屋可見前／側牆淡米白，簡化帽檐材料家族近似；未見後牆中性。原粗實階梯灰金屬代理，不改造成實照開放細梯／扶手。原加厚不透明碟與支座近白灰；01可見背架、05可見凹面，但本模型仍平滑粗碗，不補背格、饋源細杆、纜線或操作設備，不是可運作天線模型。

照片人物、車、文字／徽標、空調、欄杆、屋頂草皮與原不存在窗都不添加。顏色未校正日照曝光，不是官方色票或精確材料測量；粗化幾何與遮擋處僅材料連續近似，不稱逐面調查。

## 重建與限制

Blender4.3.2：`blender -b -t 1 --python-exit-code 1 -P build_appearance.py`；原scene.blend/model.stl同目錄。Cycles CPU32samples固定seed0；獨立clean目錄重建。3MF原頂點／三角不切分，純base material。PNG去除文字時間／本機路徑；BLEND做語義檢核，不要求容器byte相同。見[審核](appearance-review/)。

保留原天線最高邊緣／薄特徵QA警示，抽樣不是全向壁厚或正式切片。箱遮陽、懸碟和階梯需支撐評估，未試印、不保證免支撐，3MF不含特定AMS映射。
