# 數位核驗與待審事項

本候選已完成獨立數位核驗，主審接受指定有限例外；原始嚴格結果原樣保留，遠端發布另查紀錄。原STL SHA：86fd4f37381c68e567d5c836d44dafa5bc2378bb05664480fee790693edd003f。

- 原二進位STL、法向、每邊兩面、vertex link、單一表面殼、正體積、≤150mm、獨立參數重建及Blend比對通過。
- 5張actual STL預覽獨立重渲染逐像素／位元組一致。
- 651個0.2mm原始截面有效，逐原Polygon侵蝕／開運算無消失分裂。canonical腳本保持既核SHA；不repair或略除小片。
- strict surface-chords.json仍false：11418原三角各4點，共45672點法向，83首實體弦短於0.8mm（最短0.525mm）。corner-backing.json保留逐點原面/真邊/首段實料後air/連續根，最短內角連續根0.98994mm。這不是自動例外或全域真最小壁厚證明。
- strict component-detail.json仍false：328個原Polygon損失>1%，其中四亭各8、中央鋼冠296。warning-families.json保存每一列、角外損失、原短弦根證據。旋轉包絡不能代替實法向厚度。
- 已完成114180點全原面加密與1060原Polygon真角覆核；沒有用平均層損失取代逐構件。詳見 [獨立補充](independent-review.md)，不以舊83點子集取代新增215短弦。

原始失敗報告保留，不得把qa-summary解讀為全部QA通過。沒有實體試印或切片工具路徑測試。
