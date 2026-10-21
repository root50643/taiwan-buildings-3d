# 東吳大學外雙溪白色大拱校門｜公開照片外觀近似

![真實最終網格前斜視](previews/front.png)

臨溪路上王大閎設計的**完整單跨白色校門門架**，不是蘇州三拱舊校門，也不是望星橋旁三面入口標誌。以2003、2010、2013、2019年的正面照片、拍攝日期未知的完整後斜面，以及文化部託管文章的完整原圖交叉取形；不是2026現況測繪。

## 交付
- `model.stl`：194×40×153.5mm，單一閉合連通網格，毫米、無色。
- `model.3mf`：與STL相同的三角座標和面順序，5組可編輯逐面材質。不是耗材映射、多噴頭設定或已完成切片的列印檔。
- `scene.blend`：同一真實網格、可改色材質、燈光和相機；無外部貼圖、參考照片、連結庫或內嵌執行腳本。
- `previews/`：front前右斜、rear後斜、elevation正立面、top頂視、left_oblique前左斜，全部1200×1200，由最終網格渲染，不是AI概念圖。
- `build_model.py`、`render_model.py`、`rebuild.py`：參數生成、渲染、全包核心重建；`glyphs.json`為可攜的文字輪廓，重建不需字型檔。
- `qa*`、`verify_*.py`：原三角拓樸、全局切層、局部實體／空氣／薄件、材質編輯往返、獨立重建、來源終審及檔案hash。

## 外觀與取捨
保留兩根有折面及斜切柱頭的深矩形柱、完整厚楣板、一個寬淺拱、直立側段、連續帽線和拱緣帶。前方中央凸出方牌及紅白簡化圓徽；正面觀者由左至右是**「學 大 [徽] 吳 東」**，由右至左讀「東吳大學」。**後面沒有校名字、徽章或另一塊凸牌**；高處後斜視可能看見前方牌高出帽線的一小段背緣，並非在後面複製一塊牌。

四字採Noto Serif CJK TC Bold的可重建字形替代，不宣稱復刻孫科集字書法。徽章只保留白底與兩道紅色環線，不杜撰細小英文、中文或圖案。字型細襯線與細紅環均可能需要較精細製程或縮放取捨。

全部尺寸、曲線、倒角、深度及隱蔽接合是照片比例推估，**沒有實測比例、工程圖或結構驗證**。門體外寬180mm、最高150mm（不含底板），柱深22mm、楣板深11.6mm僅是此展示模型的取值。低灰底板194×40×3.5mm是為連接兩柱而添加的**列印／展示平台，不是現場台基或道路復原**。不建警衛室、商店、欄杆、車輛、路燈、溝渠、路面標線或可移動門扇。

## 列印限制
**未實印，不能稱為免支撐模型。**大跨拱底、凸帽線、字體、徽章牌、柱頭薄端均需切片、擺向與支撐評估。單一水密網格並不保證強度、懸垂可印性或薄件保留；全局切層也可能掩蓋附著在厚牆上的細字／環線。所有警告原樣保留在[QA](QA.md)。

## 重建
已驗證Python3.12.14、`requirements.txt`套件和Blender4.3.2。完全重建不需網路或原始照片。
```sh
python -m pip install -r requirements.txt
python build_model.py
blender -b -t 8 --python-exit-code 1 --python render_model.py
python qa_model.py
python check_features.py
python verify_exchange.py
blender -b -t 8 --python-exit-code 1 --python verify_scene.py
blender -b -t 8 --python-exit-code 1 --python verify_render.py
python rebuild.py --output ../rebuilt-scu-gate
python verify_package.py
```
`rebuild.py`要求全新空輸出位置，核對STL、3MF、mesh/palette和全部五PNG bytes相同。Blend檔本身不要求每次容器bytes相同，但原座標、面順序、材質、變換、材質編輯重存重開與確定性重新渲染皆已驗證。`prepare_glyphs.py`僅供另有fontTools及指定Noto字型時重新擷取輪廓，常規重建不執行。

本包先經隔離建模及獨立審查，再納入校園模型圖鑑。正式分類為`東吳大學/外雙溪校區/buildings/scu-waishuanghsi-main-gate`，去重詳`qa/deduplication.json`。變更模型後必須重做QA及來源hash終審，不可沿用本版證據。
