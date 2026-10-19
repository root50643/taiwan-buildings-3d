# A1 四工具檔案重開與有界切片驗證摘要

**模型／分色檔案條件 GO；主要 PRINT 的四部件與工具映射通過。無支撐製造路線 NO-GO；開支撐僅完成有限生成比較。** 已實際完成兩次 generic QA 切片，均不是未知機型的送印認證。獨立覆核沒有新增幾何必修。

| 版本 | 固定 SHA-256 | 實際 PrusaSlicer 2.9.6 結果 |
|---|---|---|
| `a1-four-tool-PRINT.3mf` | `7cf863dd73dfa74fefd9522455cc79f01fcf0e58ca348cdda406884a760ee2df` | 一物件、四色組、工具 1/2/3/4 保留；逐組閉合、法向一致、正體積、零退化面、所有邊價數 2。 |
| 八區 EDITABLE `a1-four-tool-prusaslicer.3mf` | `80e665598c3d39e0e0dfb572622b6c44fda4222613b2dea8ed07645625e454de` | 一物件、八部件及 1/4/3/3/3/3/2/1 映射保留；均閉合，仍保留 PV/roof 共四個單精度共線面警示。 |
| `a1-four-tool-core.3mf` | `a9929cb9259c3c18c87b2653af119035e35bbc26f93d72ba4332552b0d3dc5b6` | 可讀幾何，但 Prusa 將 components 轉成八個 objects，沒有明確 extruder 映射；不是主要 Prusa 列印路線。 |

PRINT 由雙精度的同工具區域聯集而成，保留八區編輯檔，沒有用相容 STL 反向重建，也沒有刪除原警示。它移除不必要的相同耗材內界面，沒有重做或加粗原模型外殼。四組面數依序為 14,280／5,600／9,484／5,192，Prusa 實際往返後面數不變。

獨立來源聯集檢查：PRINT 相對原 STL 的對稱體積差約 `2.44e-13 mm³`；實際 Prusa 再輸出後約 `0.0148633 mm³`，最大對應座標差約 `7.626e-6 mm`。後者是切片器座標精度／序列化變化，不能寫成逐點完全相同。原 STL 的 bytes 與 SHA 未變，尺寸維持約 150 × 148 × 57.099998 mm。詳細正負差、逐組邊價數、退化面與體積數值均保存在下列報告。

八區版四個警示已由獨立座標補證定位：原 f64 兩對三角面具有完全相同頂點、反向法向，均是工具 3 的 PV／roof 材料界面。其原面積各約 `1.20537e-6 mm²`；Prusa float32 後共線，不是未配對的外殼洞面，也不是壁厚量測。不能盲刪零面；單獨刪除反而會開邊。八區版保留此限制，主要 PRINT 版以同工具實體聯集避免該界面。

R1 曾有磚紅區 52 零面積面與 24 條四重邊，不能只憑小體積差接受。R2 把材料選區端點對齊原 STL 的 float32 精度後，原磚紅非流形問題消失；未改母體、未降低原外形精細度。R1 原始失敗檔、日誌與精確執行命令仍保存於本機獨立覆核資料，未用改門檻覆蓋失敗。

## 可公開獨立證據

- [PRINT 報告](prusaslicer-print/PUBLIC-PRINT-INDEPENDENT-REVIEW.md)、[PRINT 數據](prusaslicer-print/PUBLIC-PRINT-SUMMARY.json)、[原 STL 聯集補證](prusaslicer-print/independent-source-union.json)。
- [八區編輯檔報告](prusaslicer-editable-r2/PUBLIC-R2-INDEPENDENT-REVIEW.md)、[數據](prusaslicer-editable-r2/PUBLIC-R2-SUMMARY.json)、[四個界面旗標座標](prusaslicer-editable-r2/independent-interface-probe.json)。

驗證使用現有 `prusa-slicer-console.exe` 2.9.6，執行檔 SHA `7fd50b52d1cc3da87dbcb71e45e764412dd45688bea028f351333e86d9769704`。實際重新讀入／匯出 exit 0，stderr 空，來源檔雜湊前後不變。八區 native 檔另外以「不帶外部 INI、只讀內嵌設定」實際開啟，確認四噴嘴 entries、四種顏色及 `single_extruder_multi_material=0`；PRINT 使用相同內嵌 config bytes。精確本機 argv、raw logs、effective.ini 與 roundtrip 檔留在本機證據，公開摘要使用相對路徑重現命令。

CLI `--export-3mf` 不保存完整 print profile，不能用其輸出替換原 project 後宣稱設定仍完整。主候選另保留原 native project 與 reference INI；有效設定已實際讀回，但其中噴嘴、料徑、偏移、床面等均是檔案檢查佔位。

## 後續獨立實切結果

獨立覆核固定於 `c6983ff34091addf36166c7b7ce05d764a76ad8e`，只用主 PRINT 做一次 support-off、一次 support-on，皆由 PrusaSlicer 2.9.6 CLI 完成且 exit 0。未以 EDITABLE 的製造結果替代主檔。這次文件增量未重切、未改三個 3MF、場景、相容 STL、生成器或原 13 檔。

診斷設定為四個虛擬實體工具、0.4 mm 噴嘴、0.2 mm 層高、名義線寬 0.45 mm、Arachne、3 周界及 15% rectilinear 填充；零偏移只代表共同 QA 座標，未量測實機。四工具的模型正擠出 G1 段數依序為 **473126／31818／147843／30448**。兩次皆有 **285 個模型出料 Z、最高 Z57.0 mm**，比來源頂點低約 0.10 mm；支撐版 354 個總出料 Z 含支撐層。

- **support-off：NO-GO。** 原 stdout 明列 `Floating bridge anchors, Long bridging extrusions` 與 `Consider enabling supports`。exit 0 不會消除該製造阻擋；reference INI 與 3MF 中關閉支撐仍只是匯入佔位，不能當推薦路線。
- **support-on：僅支撐生成比較。** 唯一一次 snug／自動 45°／everywhere／上下接觸距離 0.2 mm／XY 間距 0.3 mm／3 介面層比較新增 **40,041** 段支撐／介面正擠出 G1，原警告未再出現。兩個支撐 extruder 設定值 0 都指目前模型工具，不是第五工具或獨立支撐材；尚未證明全區受托、支撐可達與可拆、材料可靠黏結。

兩次仍各有 **6,991 段 Bridge、878 段 Overhang 正擠出 G1**；48／556 是 TYPE 註解區塊數。最長帶 Bridge 標籤的 114.332 mm 移動在 Z1.8 底板填充，不能當成已量得的自由無支撐跨度。

有界抽核為 13 個指定層、每次 28,469 個料道中心線中點。Z8.1 的原 39 個工具 3 旗標完整保留；在兩側 ±0.0001 mm 以相同 654 點診斷均無超界，支持該截面貼近原門廊屋頂頂點時的算法敏感性，未把原旗標刪成全綠。另在約 0.825 mm 窗片發現工具 4 的 8 段料道，在約 0.6 mm 灰帶發現工具 3 的 1.2 mm 長、0.6 mm 寬 Arachne 線。這不涵蓋全部 422 個玻璃殼、所有色帶、連續最小壁厚或所有材料界面。

完整選存報告、數據、原旗標與去除私人路徑的 stdout 副本見 [獨立切片證據索引](independent-slicing-review/README.zh-TW.md)。診斷 G-code 仍含工具、移動、擠出及風扇命令，即使停用溫度自動命令與機器宏，也不是可送印檔；僅本機保存，不公開交付或提供所謂通用安全 G-code。

## 真機前仍須處理

四主色占滿四工具。獨立支撐耗材須先合併一個模型色、騰出工具（例如 glass 改工具 3、工具 4 給支撐），或有另經驗證的硬體方案；目前比較使用模型材料支撐。機型、噴嘴與材料確定後，須重新切片，校準工具偏移／註冊、有效床面、停泊／碰撞、清料與材料黏結／冷卻／收縮，並檢查庭院、門廊／塔亭、窗洞及屋簷下支撐的接近、移除與損件風險。若實際支撐無法清理，再依具體部位考慮最小分件或製造簡化；目前沒有證據要求整棟改形。

**未驗範圍：** GUI 點選、全部細色區與全部懸伸的料道覆蓋、實機工具頭校準／碰撞、材料黏結、獨立支撐耗材路線、支撐移除、機型專用 G-code、物理試印，以及其他品牌切片器的相同工具映射。此環境沒有可用的 native GUI 自動化入口，GUI 結果維持未驗。
