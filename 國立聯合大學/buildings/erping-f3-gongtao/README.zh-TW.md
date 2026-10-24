# F3 公弢樓｜可列印外觀近似模型

## 8 材質外觀版（2026-10-21）

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正面與來源支持區域<br>![正面](appearance/previews/front.png) | 未見外側背面中性<br>![背面](appearance/previews/rear.png) |  |

[來源界線與四視角](appearance/README.md) · [表面色 3MF](appearance/nuuf3-appearance.3mf) · [可編輯場景](appearance/scene.blend)

依官方雙照配置淡灰牆、深灰既有格柵與灰藍窗凹背；關閉入口採奶油色，原跨入口窗梃保留並同色。照片未證實 PV 頂面，屋頂維持中性，不沿歷史腳本猜測深藍電池板。 原 STL 與歷史 QA 不變；這是外觀改善，不是新增幾何。[原單色正面](previews/front.png)／[原單色背面](previews/rear.png)


二坪山校區，官方相簿照片比對版。這是照片辨識後獨立建模的外觀小模型，並非建築測量、竣工圖或精確復原。

## 檔案

- `model.stl`：毫米單位的可列印網格，底座一體成形。
- `scene.blend`：由該 STL 匯入的預覽場景；棚架、窗格及階梯都存在於 STL，非渲染貼圖。
- `build_model.py`：幾何原始碼；`requirements.txt`：Python 套件。
- `render_preview.py`：Blender 預覽程式；`previews/front.png`、`previews/rear.png`：實際 STL 正／背面圖。
- `validate_model.py`、`validation.json`：網格檢查程式及結果。
- `evidence.json`：參考照片標題、官方來源網址與證據限制。

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| ![實際 STL 正面預覽](previews/front.png) | ![實際 STL 背面預覽（證據不足處簡化）](previews/rear.png) |  |

## 辨識特徵

四層方整長面、深豎柱與成組直向格柵、左端服務窗帶、中央突出入口及短梯、圓形刻線廣場、向前下行的寬階梯、架高太陽能棚。

## 比例與不確定處

含底座外尺寸約 150 × 106 × 76.2 mm，最長邊 150 mm。每棟各自縮放方便列印，與其他校舍並非共同縮尺。

完整後面、屋頂俯視及是否另有背側附樓未確認；側後保持簡化實牆。棚頂以平板及粗化支柱近似照片，不是結構復原。

照片被樹木或其他建築遮蔽的細部沒有足夠資訊，未以虛構設備、窗洞或新附樓補齊。基地高程、階梯級數與實際長寬高皆為近似。屋頂及側後仍需要現況補照才能提高精度。

## FDM 列印建議

- 以平底朝下；建議 0.4 mm 噴嘴、0.16–0.20 mm 層高、3 道外壁。
- 格柵單肋 0.8 mm、屋頂支柱 1.2 mm、頂板 1.2 mm；圓環刻線寬 0.8 mm。
- 門廊、屋簷及太陽能棚下方有懸空和跨距，請於切片軟體檢視支撐與橋接；建議手動支撐並檢查拆除空間。
- 不建議直接縮小，細格柵與凹刻可能消失。
- 尚未實體試印。封閉網格及單一連通檢查不代表所有列印機都可免支撐成功。

## 重建

安裝 `requirements.txt` 後執行 `python build_model.py`。檢查方式為 `python validate_model.py model.stl --longest-edge 150 --output validation.json`。Blender 4.x 執行 `blender -b -P render_preview.py` 可重建預覽與場景。

## 官方參考

- [設計學院館舍相簿](https://secretary.nuu.edu.tw/p/132-1003-1100.php?Lang=zh-tw)
- [公弢樓外觀 (4)](https://secretary.nuu.edu.tw/var/file/3/1003/gallery/0/1100/gallery_1100_2269019_27329.jpg)
- [公弢樓外觀 (5)](https://secretary.nuu.edu.tw/var/file/3/1003/gallery/0/1100/gallery_1100_9662340_27329.jpg)

公開照片僅作研究引用，權利歸原權利人；套件不附原始照片，也不替任何來源授予授權。
