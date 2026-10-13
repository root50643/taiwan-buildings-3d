# 國立清華大學｜學習資源中心（旺宏館）

公開外觀照片導出的獨立桌上建築小模型。類別：**外觀近似，不是測繪模型**。校本部；首批的一件，不代表全校已完成。

## 檔案與尺寸
- `model.stl`：可列印單一實體，150.00 × 124.00 × 68.00 mm，含3mm底座，最長150mm。
- `scene.blend`：由實際STL匯入的Blender場景，單一三角網格，可編輯，單位mm。不是保留布林歷史的BIM；參數化重建用Python原始碼。
- `model.obj`：輔助交換網格。
- `build_model.py`：可攜原始碼；`requirements.txt`：依賴版本。
- `previews/front.png`、`rear.png`、`elevation.png`：實際STL渲染，不是參考照片或概念示意圖。正／背是模型顯示方向，非測量方位。
- `validation.json`：原檔驗證；`sources.json`：公開來源與近似紀錄。

## 來源與實際觀察
查閱日期：2026-10-13。來源頁：[校方公開介紹](https://attractions.site.nthu.edu.tw/p/406-1515-187049,r8697.php?Lang=zh-tw)。

官方遠景、橢圓前棟入口端及玻璃入口側的照片像素已檢視。官方文字明列前四層橢圓、後七層ㄑ形、由穿廊連接；模型保留這些量體識別及入口翼三層遮陽格。

參考照片僅以連結列出，**未放入交付檔案、未重新發布**：
- https://attractions.site.nthu.edu.tw/var/file/515/1515/pictures/57/m/mczh-tw700x700_large38206_861788677328.jpg
- https://attractions.site.nthu.edu.tw/var/file/515/1515/pictures/57/m/mczh-tw700x700_large38208_272758677328.jpg
- https://attractions.site.nthu.edu.tw/var/file/515/1515/pictures/57/m/mczh-tw700x700_large38210_831113777328.jpg
- https://alumni.site.nthu.edu.tw/var/file/346/1346/img/2899/130126412.jpg
- https://alumni.site.nthu.edu.tw/var/file/346/1346/img/2899/384599613.jpg

## 近似與缺口
沒有完整俯視或後立面測量，ㄑ角度、深度、棟距均為估計；前棟屋頂用低三角屋面概括，後棟可見正面加入退縮窗帶與突出屋簷，未知背面素面；未有充分證據的屋頂設備方塊已移除。穿廊封成實體，窗戶為淺浮雕；背面無虛構窗洞。入口柱與窗框加粗並融合。前棟外側斜梯、扶牆與分段水平長窗以可見照片近似；樓梯位置、階數與深度未實測。

所有尺寸為獨立150mm尺寸控制，三件不共同比例。沒有室內格局、地下空間、進出控制或設備系統資料。沒有擷取校方Unity、BIM或其他原始3D資產。官方3D導覽只確認公開入口與技術頁，沒有宣稱已逐面走訪其3D場景。

## 列印起點
正立、底座朝下。前棟弧面線槽、入口窗格與檐下凹槽請逐層檢視；柱、框、檐均有實體背襯。屋面採低斜坡，仍需依實際機台判定局部支撐。

可從0.4mm噴嘴、0.2mm層高、3道外牆、15–20%填充起始評估，這些只是建議，非已驗證參數。STL是封閉實體；填充率由切片器決定，未預挖內腔。150mm含底座，請勿再用共同校園比例套用。較細凹槽可按機台調整。

## 驗證結果
`validation.json` 的 passed = true。原始二進位STL法線為單位向量且與面繞向一致；非退化三角面；封閉、邊與頂點流形；單一連通表面，沒有分離的內腔殼；正體積；底面z=0；尺寸150mm；乾淨暫存目錄重建STL的SHA-256一致；Blender與STL三角幾何一致。

尚未跑切片器、尚未實體試印，不宣稱完成支撐最佳化或全面自相交證明。模型及正背面預覽已人工檢視。

## 乾淨重建
需Python 3.12與Blender 4.3.2或較新版。先在虛擬環境安裝requirements.txt；在本資料夾依序執行：

```sh
python -m pip install -r requirements.txt
python build_model.py
blender -b -t 2 -P render_preview.py
python validate_model.py
```

原始碼只依賴同資料夾檔案；不依賴製作機器的絕對路徑。驗證會自行從乾淨暫存目錄重建STL；原檔不經自動修復。


## 發布補充
請併讀[本輪版本與範圍](../../../audits/amendments/round-status-20261013.zh-TW.md)、[首批薄特徵警示與方法](../../../audits/amendments/layer-audit-20261013.zh-TW.md)及[化工館年代說明](../../../audits/amendments/chemical-engineering-era-clarification.zh-TW.md)。旺宏館保留原幾何；台達館及校友體育館採列印修正版，不重複計數。


## 實際STL正背並排

| 正面 | 背面（未見部分按詳頁明示簡化） |
|---|---|
| ![正面](previews/front.png) | ![背面](previews/rear.png) |
