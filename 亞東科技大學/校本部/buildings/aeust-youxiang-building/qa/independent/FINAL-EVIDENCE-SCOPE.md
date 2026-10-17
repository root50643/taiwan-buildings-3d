# 亞東有庠 v15：獨立證據範圍與保留限制

本說明整理已完成的獨立審查與公開封裝必須保留的限制；不改寫作者或獨立工具的原始結果，也不代替最後的公開檔案與封裝驗證。

## 科學結果

凍結 STL 為 47,770 個三角面，模型外接尺寸為 219 × 107 × 119 mm，SHA256 為 `46649566e965a049e6e333e9d82b075407c8e926e55c9034f11fbe3dbdf15a5d`。正常與 `-O` 模式的完整獨立審查均完成。

原數值結果的 `strict=false` 與 26 筆警示完整保留。這 26 筆都有對應的 exact recorded-ray 逐筆補證及原始事件／接觸資料；完成的是有明確範圍的補充驗證，不是一般警示豁免，也不是把原嚴格失敗改成通過。完整 477,700 筆 CSV、全部 flags／short records、sections、每筆 exact contacts 與 actual-hex 證據仍須按原 bytes 公開。有限射線與切片證據不能推論任意位置的全域最小壁厚。

作者與獨立資料另有完整原 bytes 比對。原通用 full-qa-summary 中未完成比較而留下的 false 欄位保持原樣；它不能被重新解讀為已實測出科學資料不同，也不能被本說明改寫。

## 外觀、重建與實體限制

模型表達早期代表性外觀，所有建築尺寸均為估計。兩個天井、非平行翼部、巨大框架與玻璃盒等主要特徵保留。視圖方向使用模型 local axis，不是實測地理方位。不得套用其他校舍或其他案例的年代與尺寸結論。

獨立保存 Blend 的九視圖重播已完成，沿用 CPU、單 thread、64 samples、固定 seed，未使用 denoising 或 OIDN。公開九張 PNG 僅清理 metadata；原含私有 metadata 的 PNG 以私留原件與 hash 記錄。作者先前 preflight 的 `full_nine_view_rerender_verified=false` 仍保留，它與後來完成的獨立九圖重播屬不同階段。

本案尚未實際試印。幾何、來源、場景與影像驗證不構成實體列印成功、耐用度或任意材料／機器設定的保證。

## 唯一未回收的歷史進度 metadata

早期獨立工作進度檔 `WORK-STATE.json` 的一個舊版本未能回收原 bytes：3814 bytes，SHA256 為 `6e3f0b0e1e31a2e0385ecf3b66bad84158d4d1afaa0a231e60096740f8f17faf`。保留的是原歷史 descriptor 與如實的 missing 記錄，不能稱為已備份原檔或全歷史恢復；`all_historical_retained=false` 必須明示。

這個獨立進度 metadata 不屬於作者凍結的 3690 個科學交付成員，也不屬於 runner adapter 的 3691 個凍結成員。其歷史缺口與目前凍結科學原件、完成的正式審查、控制來源及目前 payload 覆蓋分開記錄。任何其他缺檔、未知 HOLD 或科學證據缺口都不能套用這個單一 descriptor 的處理。

## 四份 handoff 控制副本

四份 handoff fixture 中的完整 dense CSV 是原 schema-control producer 建立的相同科學來源副本，不是負控或壞壓縮。它們只能在固定 path、壓縮 bytes／SHA、producer／control／freeze graph 全部吻合時，以 `duplicate_reproduction_or_scratch` 私留原件。

作者兩模式與獨立兩模式的四份 canonical 完整 CSV 仍是強制公開項，並必須通過原公開 helper 的實際完整 streaming privacy scan。副本處置不增加通用 512 MiB 解碼上限，不免除 privacy scan，也不變更原 `strict=false` 或任何科學判定。原 generator 的 HOLD 報告與後續兩個狹義 adapter 的衍生結果分別保留，不得混稱為原工具一次完整通過。
