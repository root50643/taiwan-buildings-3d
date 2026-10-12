# 蓮池潭龍虎塔｜可列印外觀微縮模型

## 先下載列印檔

[下載龍虎塔 STL：dragon_tiger_pagodas_150mm.stl](https://github.com/root50643/taiwan-landmark-buildings-3d/releases/download/v1.0.0/dragon_tiger_pagodas_150mm.stl)。此檔以 Release v1.0.0 附件提供，GitHub 原始碼 ZIP 不包含 model.stl。下載後請改名為 model.stl，置於本 README 所在目錄，再執行下列驗證、預覽或重建流程。STL 位元組及既有驗證雜湊均未變更。


## 模型內容
- 成品尺寸：150 × 124 × 109.5 mm，含底座。
- 七層、十二角雙塔、簡化翹簷及欄杆、可辨識的龍／虎身形與張口入口、共同平底座。
- 動物是厚實、玩具式的辨識性簡化雕塑，非原雕塑精雕復刻。獸口為朝外開放的凹口，沒有內部閉合空腔殼。未製作完整九曲橋。
- 一體式、單一連通封閉實體，最長邊 150 mm。

## 列印起始建議（尚未切片實測或試印）
- FDM 可由 0.4 mm 噴嘴、0.16–0.20 mm 層高、3 道外牆、12–18% 填充與 PLA 起步。
- 原方向直立、平底貼平台；必要時增加 3–5 mm brim。
- 重簷下方、獸口頂部、龍角與獸首局部有懸垂，建議支撐預覽後使用局部樹狀支撐。塔簷厚化約 1.2 mm；龍角頂端直徑 1.8 mm、塔尖末端直徑 1.6 mm；牙齒和獸身凸紋仍需低速與冷卻。拆支撐時避免拉扯屋簷和牙齒。
- 請先檢查全高度切片路徑、懸空、薄壁與支撐拆除空間，再試印。不要直接縮小，縮放後應重新檢查所有細節。

## 檔案與重建
- model.stl：唯一列印實體，單位 mm。
- build_model.py：參數化原始碼，可重新產生 STL。
- scene.blend：由同一 STL 匯入的 Blender 場景，包含相機、燈光及非列印地板。編輯建模參數後應先重建 STL，再執行預覽腳本。
- previews/front.png、rear.png、elevation.png：實際 STL 的前斜視、後斜視與正向視角。沒有照片貼圖，也沒有添加只在預覽中存在的建築細節。
- render_preview.py：Blender 預覽腳本；使用無雜訊的工作室顯示。場景材質只是預覽色，STL 本身不含材質。
- validate_model.py、validation.json：數位檢查程式及結果。
- rebuild_check.json：重建前後 STL SHA-256 一致性結果。
- requirements.txt：Python 套件版本。sources.md：公開參考來源及不確定性。

安裝 requirements.txt 後執行 python build_model.py。執行 python validate_model.py model.stl --output validation.json 檢查；以 Blender 4.x 執行 blender -b -P render_preview.py 產生場景和預覽。單張預覽可設定環境變數 VIEW=front 或 VIEW=rear。Blender 場景以 mm 顯示單位，匯出時只選 Printable_STL_mm，勿把地板、相機和燈光一起匯出。

## 檢驗範圍
已檢查：單一連通邊界面、封閉網格、面向一致、每條邊恰有兩面、頂點鄰域為單一環、無退化三角面、正體積、平底接觸、尺寸與可重建雜湊。單一連通封閉邊界面沒有獨立的內部空腔殼。以上不是完整幾何自相交證明，也不等同切片測試或實體試印；未聲稱已試印成功。

本包是重新建立幾何的外觀微縮模型，非官方模型、測繪模型或結構模型。每座均以獨立成品大小設計，彼此不是共同比例，不能從模型反推真實尺寸。參考照片不隨包分發；若需商業散布或使用，請自行確認建築、雕塑、商標及其他適用權利。
