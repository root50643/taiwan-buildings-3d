# 正修科技大學圖書科技大樓：原面有限玻璃代理外觀

既有模型的特徵級有限改善，不是新增建築、全館彩色復原或測繪。僅1396個完整原面指定低飽和灰青不透明代理色：兩弧冠窗28面，加D筒上段側玻璃1368面（672／696）；面積656.9861150828764 mm²，其餘29354面中性。色值非實測RGB，不模擬透明／反射／逐窗格。

- [彩色3MF](csu-library-technology-appearance.3mf)：單網格、全部原頂點與原面、兩個獨立可改材質。
- [可編輯Blender](scene.blend)：原面不變；隔離副本實改材質／頂點、保存／重開檢查。
- [正面](previews/front.png)・[左側](previews/left.png)・[右側](previews/right.png)・[背面](previews/rear.png)・[俯視](previews/top.png)
- [可重建來源ZIP](rebuild-source.zip)：解壓後依序執行 appearance/source/build_appearance.py、verify_exchange.py，再用 Blender --background --python 執行 render_appearance.py、verify_scene.py。numpy、lib3mf 2.5.0、Blender 4.3.2。

## 有限範圍
逆原150°旋轉與1.209283792097708等比縮放，以實叉積外法向及全部三頂點測試110個有限平面／原48-chord段；local容差3e−5。沒有centroid近似、切三角、分割或新增玻璃幾何。普通32窗因白肋／冷氣混界拒絕；壁畫、下D筒樹遮域、框、環、灰頭、百葉、opaque牆、低閱讀台、屋頂、底座與其他面均不染。證據色界不宣稱材料接縫。原模型未描繪壁畫，本次未刪改藝術圖紋。

## 原件與驗證界線
原STL30750三角／15373頂點，原native為單中性材質；全有向原面與全頂點域精確比對。交付原座標exact。SDK另存的隔離編輯副本可能float32微量化，報告記實際誤差，不宣稱其位元不變。完整44原件另存備份original-model/，原STL／Blend／全部QA bytes保留。本次只改外觀；原2017外觀加2024輪廓交叉近似與43m／43.8m、1.5m地景假設、PV未建、背細窗等限制照留。

歷史製造QA不是本次重跑：274層／406Polygon整層maxloss0.09308526834768534%，不能掩兩棚柱36跨層樣本（不是36柱）maxloss7.628528051248996%、minretained92.37147194875101%。作者123000點825短弦min0.0015362113610166088mm；獨立307500點2383短弦min0.000768105913145mm，其中2342二面根、41三面頂角另根，三面首出口min2.3460531046648656mm。原strictfalse／exit1與限定SHA例外如實保留，非全部嚴格通過、非全向厚度保證、非免支撐或實印PASS。完整歷史QA為準。

## 來源與權利
見[SOURCES.md](SOURCES.md)與[LICENSE-NOTICE.md](LICENSE-NOTICE.md)。原影像只私下觀察，不附照片、裁圖、貼圖、壁畫或原刊文字。2024來源不等於2026現況。私有技術完成不等於公開發布授權。
