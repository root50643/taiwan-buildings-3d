# 原面密點作者診斷

原 STL 5028 面，每面7個固定重心權重點，共35196筆；原始763筆首實體弦短於0.8mm、2筆parity控制旗標原值保存。control-diagnosis.json另用longdouble原三角交點與solid angle診斷，不能將原旗標改為true。

584筆直接或連鎖凸角證據在all-short-bisector-evidence.json.gz。餘179筆以另附qa-roots現版證據為準，其中178含實際凹邊，不是純凸角。法向首段與共同向內根是不同量，後續air與再入實體不計厚。

重播時先解壓兩個CSV。dense-ray.cpp接受原三角二進位及輸出CSV路徑；原三角資料須由model.stl原float32頂點順序直接轉float64，不得重排。其餘Python腳本使用相鄰model.stl及此目錄CSV。腳本重播會寫診斷結果，請在另複本執行。

近共面分片只用於原面關係辨識；原mesh及原面ID不折疊、不repair。全部為作者端有限點診斷，未證全域最薄、切片或實體試印。

nearplanar-individual-short-review.json為嚴格JSON可攜副本：原無限air值Infinity改為字串UNBOUNDED_Infinity，不改首實體段。原bytes完整保留於同名.original.gz；原SHA256 b9f33d45a6c4de7e3ed2f72cc7e136efabc0561604a70ea5338da604500f374e。

## 獨立封裝補充：無後續入射的可攜表示

[逐檔索引](portable-evidence-index.json)列出三份原壓縮證據與嚴格JSON副本。原gz逐位元保留，內部Infinity是Python相容的原證據格式，不是標準JSON。副本只將air_after_mm的正Infinity表示為null並附完整JSON欄位路徑；意思是第一入射／出射後沒有第三交點，後續空氣無界，並非零、缺測或實體厚度無限。所有有限數值與原首實體段不變。
- [all-short-bisector-evidence.json.gz](all-short-bisector-evidence.json.gz)：489筆；[嚴格可攜副本](all-short-bisector-evidence.portable.json)。
- [convex-chain-bisector-evidence.json.gz](convex-chain-bisector-evidence.json.gz)：411筆；[嚴格可攜副本](convex-chain-bisector-evidence.portable.json)。
- [nearplanar-short-edge-classification.json.gz](nearplanar-short-edge-classification.json.gz)：489筆；[嚴格可攜副本](nearplanar-short-edge-classification.portable.json)。

再現環境補充：渲染腳本另使用Pillow與系統NotoSansCJK-Regular.ttc字型；獨立重渲使用Pillow12.3.0及Blender4.3.2，5圖逐bytes一致。請依渲染腳本確認字型路徑，無原圖資產需求。
