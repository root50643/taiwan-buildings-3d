# 臺北市立大學天母體育館A棟：校級QA摘要

對象：2012天母體育館A棟單棟外觀模型，v6。STL SHA256：f93ed0ab95e13707d390f480174f63e31086b48041fc7a7a873975cad8892a8c。尺寸210 × 152 × 63.8 mm，24,112個原三角面。只涵蓋本件指定版本，不延用其他建築的數據或豁免。

## 已完成的有限數位檢查

- 原STL封閉、法向一致、單一連通表面；原始拓樸／頂點連結檢查及退化、重複面檢查通過。
- 297,696個閉AABB候選對包含相鄰面與共面，全部精確完成，零不允許相交。
- 每原面十點，共241,120條原法線射線，零短弦、零flags，最小首段實心弦0.901098 mm。
- 957個原切層Polygon全部通過窄根與侵蝕檢查，最大opening loss 0.085328%。
- 完整normal及Python -O兩模式strict pass；科學證據原bytes保留，未移動樣本、降低門檻或替換理想射線。正負控制及安全重建工具另附。
- 源碼重建、保存Blend的evaluated世界座標有向三角形與原STL相符，場景無外部來源照片貼圖。
- 七張主視圖及兩張局部圖共九張獨立重播。在指定工具鏈、相同相機／渲染政策及相同純metadata清理後比對公開乾淨PNG；歷史raw圖及新重播raw圖不宣稱整檔bytes相同，所有保留chunks與像素皆須保持。
- 九圖另有獨立來源外觀審核；保留北面遮蔽、比例估計與製造修形等限制。

[完整獨立QA](../../天母校區/buildings/utaipei-tianmu-gymnasium-a-2012/qa/README.md) · [作者完整摘要](../../天母校區/buildings/utaipei-tianmu-gymnasium-a-2012/qa/final-v6/full-qa-summary.json) · [來源外觀審核](../../天母校區/buildings/utaipei-tianmu-gymnasium-a-2012/qa/source-audit/SOURCE-APPEARANCE-AUDIT.md)

## 限制

有限法線射線與XY切層不證明全方向最小厚度或材料強度。本件不是測繪或BIM，不含室內、B／C館、全校或博愛校區。北面遠段及屋頂尺寸均保留推估。窗框、梯欄、粉檐及採光帽角部有製造加厚／修形，並非已量測構造。尚未實體試印，帽緣、主屋檐及雨遮須另在實際切片器配置支撐；任意縮放、空心化或重網格化需重新QA。

本摘要為公開證據索引；精確適用範圍、重播方法及原報告以[完整QA](../../天母校區/buildings/utaipei-tianmu-gymnasium-a-2012/qa/README.md)為準。
