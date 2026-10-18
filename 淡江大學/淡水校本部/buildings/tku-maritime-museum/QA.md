# v3 數位檢查與條件式交付

STL SHA-256：`42097fab9a62dccd4042ba18bc49d3c5b9a44e66ff71e91962e68b56d74bc8b1`，64,584 bytes。候選外包絡148 × 140 × 130 mm，共1290個三角面、647個按座標焊接的頂點。

| 檢查 | 實際結果 | 證據與範圍 |
|---|---|---|
| 封閉流形／法向／單連通／體積 | 邊界邊0、非流形邊0、退化面0、面連通分量1、方向一致、正體積836906.213565635 mm³ | qa/independent/candidate-v3-algorithm-v2.json；僅焊接相同座標，沒有修洞或重建表面 |
| 自交 | 14062對AABB候選面對，實際檢查交會0 | 平面交線區間＋共平面Shapely交集，扣除合法共享拓樸；容差1.48e-6mm，屬數值方法 |
| 厚度 | 1290條面重心內法線均有出口，min1.599998mm，1%1.599998mm，低於1.2mm為0 | 完整射線CSV.gz、定點厚度CSV及geometry-probes-v3.json。有限樣本，非全域最薄證明 |
| 懸垂與通道 | 139個下朝面、1536.1793mm²投影，5條直徑3mm工具掃掠路徑通過 | 只是外部工具通道，未生成實際支撐；詳細限制見PRINTING-LIMITS.md |
| 生成器重建 | STL位元組完全相同 | qa/publication/rebuild-scene-preview-binding.json |
| 場景／預覽 | Blend僅1個模型網格，float32三角面與STL相同；十張PNG雜湊符合當次渲染manifest並綁定此STL；沒有檔案影像材質 | qa/publication/rebuild-scene-preview-binding.json、previews/render-manifest.json |
| 像素／外觀 | 兩主圖雜湊相符，九圖親看，v2多面預覽親看 | qa/independent-source-review.md及獨立候選視覺摘要；後端／下緣是保守估算 |

初輪v1的五條短厚度弦與翼根窄縫已保留，修正前STL、生成器、參數、build report及兩張預覽在qa/history/v1。v1原自交演算法另報兩對旗標，原報告未改動；其逐座標診斷顯示同一斜面在STL float32精度下的近共平面共享點，被原先過嚴平行門檻誤分。v2演算法新增點到平面共平面判斷，保留原負控並加入該情境，7項控制全部通過。修正後演算法分別重跑原v1及新v2並保存新檔，沒有人工改為passed。

執行過程另有geometry-probe首次因缺少networkx而失敗，錯誤記錄保留；補充實際剖面時改用剖面線段頂點鄰接計算，不修改原報告。Blender初次在sandbox載入DLL失敗，改在核准的執行模式載入；渲染時非必要遠端資產附加模組缺cattrs，raw log保留，所有十張圖及scene仍成功產生並另做實際網格核對。這些環境問題沒有被當成模型通過證據。

未切片、未試印。自交容差、厚度重心射線與工具掃掠均有數值及覆蓋限制，不能宣稱全域厚度、免支撐或實際支撐可移除。本節保留原作者的數位檢查紀錄；最終交付依下節公開獨立覆核及支撐條件。

v2曾在入口橋後方窗槽頂面找到兩個無開放cardinal射線面，原紀錄與模型保留於qa/independent及qa/history/v2。v3僅省略這個被橋遮住的左側下排窗刻槽；重跑139/139下朝面重心均有至少一個開放水平射線。最終v3資料、完整射線、厚度定點和工具通道均以v3檔名另存；沒有覆寫v1/v2旗標。

## 發布前獨立覆核補充

[獨立覆核摘要](qa/public-review/README.md)對固定STL重新執行幾何、歷史、來源、支撐與重建核對。約1.60mm僅為面心內法線採樣最低弦長，不是全域最小壁厚。14條支撐工具路徑中兩條碰撞原false保留：橋端(-90,-4,8.4)向-X，以及煙囪前(0,41,95)向+Y。可行替代與操作條件見PRINTING-LIMITS.md；未生成實際支撐、切片或試印，不保證支撐可移除。

公開包保留原失敗及數值，僅刪除私人路徑／PNG文字時間metadata。原候選綁定報告代表去識別前檔案雜湊；當前公開場景與預覽以qa/publication/rebuild-scene-preview-binding.json為準，STL與影像IDAT不變。
