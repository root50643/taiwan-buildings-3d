# 官方實景來源與限制

親看日2026-10-22。第三方實拍tile僅私存研究，不隨公開包重製。

1. [南華官方地面VR圖書館W](https://vr360.nhu.edu.tw/VR360/index.html#W)；[pano.xml](https://vr360.nhu.edu.tw/VR360/pano.xml)，node1 title=圖書館/customnodeid=W。datetime=2023/9/18 下午02:41是節點欄位，不是認證攝影時刻。原圖模板 `https://vr360.nhu.edu.tw/VR360/tiles/node1/cf_0/l_2/c_{x}/tile_{y}.jpg`，x,y=0..2。9塊完整拼接可讀入口無盡藏、紅瓦與灰端框；紅布條非建材。
2. [南華官方航拍](https://vr360.nhu.edu.tw/aerialphoto/index.html)；[pano.xml](https://vr360.nhu.edu.tw/aerialphoto/pano.xml)，node5。1970/1/1是無效預設，拍攝年月未知，系統發布年也非攝影日。原圖模板 `https://vr360.nhu.edu.tw/aerialphoto/tiles/node5/cf_0/l_3/c_{x}/tile_{y}.jpg`，x=1,2，y=2,3。左下方L形圖書館與地面同立面/前廣場對照，大型白覆蓋、橫肋與前紅坡清楚可見；不混用畫面中其他粉牆建物。
3. 原build_model.py、sources.json及歷史限制原封保留。後側全立面未獨立證實，牆/玻璃混材不擴染。

固定原件commit `986c043b71df7c098434fe615a12cba2cfa35403`，路徑`南華大學/大林校本部/buildings/nhu-wujinzang-library`。原35檔實bytes對GitSHA核驗。STL Git blob `4fcce7df39b57fb25b4150ff9d3a90b0c3ef1aa0`；SHA256 `99af38ad78e375e04fae9217193b2c9f22335a646d1679c05e3ab7641a3a5d75`。native親查單mesh、4378面、唯一Warm stone材質。
