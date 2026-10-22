# 馬偕專校三芝綜合大樓｜QA

## 原始網格
STL SHA256 `6b0713aec0cb19c9e5d73222a56fe2b142c70283b58be5b35b6130da676ae9f0`；27992三角面、13920個精確焊接頂點，單一閉合連通殼、正體積；零非有限值／零面積／重複面／非二鄰邊／方向錯誤／頂點link錯誤。只作精確座標索引，不補洞、平滑、修法線或刪小面來掩飾錯誤。

## 切片、局部薄處與懸挑
原始STL每0.2mm及最高點下0.001mm，共580層，保留浮點輪廓與even-odd巢狀；全部有效且每個正連通面均存活於-0.4mm侵蝕，無薄件豁免。這不是所有局部壁厚的全域證書。
另有五個局部剖面與五個真實網格射線樣本，保留屋頂高差、橘色遮陽片、端玻璃帶、屋簷與入口側牆。詳見 `qa/feature-validation.json`；局部射線不冒稱全表面最薄厚度。向下超45度面3820個、面積約41094.4mm²，含底面；需檢查支撐，沒有實印或免支撐認證。

## 真材料、場景與重建
lib3mf strict讀取零警告，3MF三角座標及面序與STL一致；實際改一個材質RGB與Alpha、存檔重讀，其餘材料／面指派保留，最大座標誤差9.5367432e-07mm。交付8材質全部不透明。
Blend重開核頂點／面／材料，實際改一頂點及一材質顏色與Alpha、存檔重開通過；交付檔保持原狀。沒有外部素材、內嵌照片或腳本。
重開交付Blend重渲染front與交付PNG精確一致。乾淨新目錄重跑generator與五視圖：STL、3MF、mesh.json、palette.json及五PNG，共9檔bytes一致。Blend二進位含內部保存差異，不冒稱不同輸出路徑Blend bytes相同，改以幾何材料讀回驗證。

## 來源與身份
六作者外照、六NLSC原磚及原像素拼圖親看，25來源檔hash核過，六磚重拼與PNG像素精確一致。來源只作研究，不在交付包。教育部原頁核私立專科、三芝校區；非馬偕醫學大學。2019完工不是拍攝日，NLSC2024不是已證實航拍年；選無PV版本。屋脊窄平頂和階梯／欄板為製作加厚，後細窗及坡地收口近似，原始比例未測量。

## 重跑
Python：numpy、trimesh、manifold3d、shapely、rtree；交換驗證另需lib3mf。Blender 4.3.2 CPU Cycles固定seed0、48samples、1200²；渲染strip文字日期metadata，保留像素。
```sh
python build_model.py
blender -b -t 4 --python-exit-code 1 --python render_model.py
python run_all_checks.py --lib3mf-python /path/to/python-with-lib3mf
python rebuild.py --output /new/empty/output
```
本工作環境幾何用 `modeling-toolchain/.venv/bin/python`，lib3mf用預設python；不可誤報同一環境都有lib3mf。獨立外觀終審另見 `qa/independent-appearance-review.json`。庫發布、同步數量與Library狀態由父代理另行處理。
