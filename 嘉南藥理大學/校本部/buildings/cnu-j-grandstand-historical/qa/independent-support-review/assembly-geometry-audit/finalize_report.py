from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
D=json.loads((H/'geometry-summary.json').read_text('utf-8'))
S=D['interface_z_surfaces'];G=D['interface_gap_measurements_mm']
# Simulated dry seating is derived from measured faces. It is explanatory,
# not an alteration to or a physical fit claim about the fixed candidate.
post_shift=26-min(S['column_shoulder_z_surfaces_mm'])
roof_shift=max(S['column_shoulder_z_surfaces_mm'])+post_shift-min(S['roof_shoulder_z_surfaces_mm'])
frame_shift=max(S['roof_shoulder_z_surfaces_mm'])+roof_shift-min(S['frame_shoulder_z_surfaces_mm'])
dry={'status':'Analytical illustration only; no physical dry fit',
  'column_z_shift_mm':post_shift,'roof_z_shift_mm':roof_shift,'frame_z_shift_mm':frame_shift,
  'mast_top_after_gravity_shoulder_seating_mm':max(S['frame_axis_z_surfaces_mm'])+frame_shift,
  'meaning':'The nominal 0.05 mm shoulder glue films do not hold themselves open. For nominal placement use gap-filling adhesive plus temporary alignment/height fixtures; gravity seating instead makes a small disclosed manufacturing height change. No clip/press-fit/physical contact or adhesive-strength guarantee is made.'}
(H/'dry-seating-interpretation.json').write_text(json.dumps(dry,indent=2,ensure_ascii=False)+'\n','utf-8')
parts=D['parts']; rows=[]
for n,r in parts.items():
    t=r['exact_topology']; rows.append(f"| `{n}` | {t['triangles']} | {t['signed_volume_mm3']:.6f} | {r['exact_AABB_candidate_count']} | {len(r['unexpected_intersections'])} |")
hashrows='\n'.join(f"{r['sha256']}  {r['file']}" for r in parts.values())+'\n'
(H/'FIXED-STLS.sha256').write_text(hashrows,'utf-8')
rep='''# 嘉南藥理 J 司令台：獨立組裝與幾何覆核

固定提交：`3a9a6041c5fde9ef2d6e9e96b02f24f025c8be5a`。本分項結果為 **GO：未發現需要改 STL 的幾何／裝配阻擋**；整體列印放行仍以主審的來源、重建、場景及實際切片／支撐審查為準。沒有修改原候選、遠端或既有 QA；沒有實體試印、試合、膠合或強度測試。

## 固定輸入與範圍

讀取實際 `parts/` 八個 STL、`model.stl`、`assembly.json`、`parameters.json` 及生成器。四個 `*-print.stl` 才是四類供應印向；四個 `*-assembly.stl` 用於組裝位置。總覽是 22 個獨立封閉體，不能把總覽非單連通當作單件失敗，也不能把四類零件的檢查聲稱成已逐件列印 22 件。

份數、位置與面集合獨立比對為主體 1＋棚 1＋下柱 10＋上框 10＝22 件。柱／框的 X 位置同為 −81、−63、−45、−27、−9、9、27、45、63、81 mm。將原組裝 STL 平移並量化成總覽所用 binary32 後，**5396 個三角形及每個頂點與總覽完全一致**，最大原順序座標差為 0；無缺件、額外件或錯列。

八個固定 SHA-256 見 [FIXED-STLS.sha256](FIXED-STLS.sha256)；總覽 SHA-256 是 `a759a7e25e8a4818e1802668d51c1d21db88b312200ddc1406dbb968aee5343f`。

## 獨立數值檢驗

未匯入候選 QA 函式，未先修補、重網格化、平移歸一或減面。從 STL 原 binary32 有限座標轉成共同整數格；對所有確實 AABB 相交的三角配對，以整數／分數平面切割區間、共面包含與邊相交做精確分類，允許合法共頂點／共邊。九個陽／陰控制案例全部符合預期。這是可稽核演算法的有限座標驗證，並非外部形式證明。

| STL | 面數 | 正體積 mm³ | 全 AABB 候選配對 | 非法交集 |
|---|---:|---:|---:|---:|
'''+ '\n'.join(rows)+'''

上述八件均為單連通、封閉、方向一致；精確邊／頂點 link 檢查未見非流形、重面或退化面。總覽另外完整檢查 68,378 組 AABB 配對，亦無非法交集，連通分量恰為 22 件。所有 231 對原組裝實體另作 Boolean 相交，交集皆空、最大體積 0 mm³；沒有用寬鬆容差把非零實質重疊消除。Boolean 結果與精確總覽表面交集檢查相互補充。

四對組裝／列印 STL 以自行指定正旋轉矩陣及平移比對，行列式均 +1。主體直立、棚沿 X 軸翻轉 180°、柱及框沿 Y 軸轉 −90°後平放。每個對應三角座標最大差不超過 0.000007630 mm，與各自 binary32 匯出量化相容；沒有鏡射或形狀更換。不能把它寫成兩種印向 STL 位元組相同。

## 50 個接口與可組裝性

以另一套精確軸線／三角面投影求交，逐一量測 10 個主體槽、10 個棚底槽與 30 個棚上槽；在 JSON 明列的鍵中段高度，使用兩條中心軸線找出實際鍵與槽的兩側面，沒有只抄參數。最小實測總 XY 間隙為 **0.399996996 mm**，最小單側間隙 **0.199998498 mm**；浮點儲存造成微小尾差。這些是 50 槽指定截面的數值補證，不是任意位置／印件粗糙表面的全域間隙證明；另核生成器中的直壁矩形接口與原 STL 的零碰撞。各鍵與槽均同向、平行，直向外開，不需把斜框穿過棚板。依序主體→10 下柱→棚→10 上框，未見幾何上的插合障礙；實際列印尺寸與膠接仍需乾試。

| 實測位置 | 間隙／厚度 mm |
|---|---:|
| 下柱腳與主體槽底 | 0.299999237 |
| 柱頂鍵與棚底槽頂 | 0.149997711 |
| 上框鍵與棚上槽底 | 0.150001526 |
| 各級肩座的名義間隙 | 約 0.049999237 |
| 上下對位盲槽之間的棚板實體 | 2.000000000 |

這些是**有間隙的膠接定位，不是卡扣、壓配或已實體貼合**。名義肩座 0.05 mm 膠縫不會自行懸空保持。若讓各級肩座乾式自然接觸，依量得座面估算，柱約降低 0.05 mm、棚累計降低 0.10 mm、上框累計降低 0.15 mm，最高約 53.25 mm；這是微小製造落座差，不能聲稱實體仍精確保持數位 53.4 mm。計算及原座面在 [dry-seating-interpretation.json](dry-seating-interpretation.json) 與 [geometry-summary.json](geometry-summary.json)。

要保持名義位置與膠膜，先全十列對位乾試，使用適合材質的慢乾補隙膠，配合臨時平行高度／位置治具，再分階段固定。勿硬壓棚板強迫十柱入槽；清理毛邊並以真機尺寸決定是否需要局部修整。若允許肩座自然落座，應接受並保留上述很小的實體高度差。幾何通過不保證膠強度、抗摔或長期承載。

## 薄特徵、列印與搬動條件

從原 STL 局部精確線面相交測得下柱側厚 2.799999952 mm、上框側厚 2.200000048 mm、桅杆平面內寬 3.0 mm，兩支斜撐的真正垂直截寬分別約 1.800000150／1.799999677 mm；棚面實體 2.400001526 mm、對位槽間 web 2.0 mm。這些是明列位置的幾何厚度補證，**不是任意方向全域最小壁厚證明或強度保證**。實看 unique-print-parts 與 front 預覽，與上述分件／印向及重複件配置一致。

柱與框必須依供應印向側躺；不要用總覽把細框直立列印。主體仍有真實前緣挑出及外開淺凹口，須依主審切片條件支撐，不能稱免支撐。192×60 mm 棚片可能翹曲，需平整首層、可靠附著、妥善冷卻後再取件及乾試；不要藉膠合硬拉平嚴重翹曲。上框雖加粗，取件／去 brim、夾持、對位與搬動仍可折斷，應扶住框腳或主體，不能抓桅杆提整件。未實際拆支撐、試印、試合或測膠強度的限制必須保留。

完整原座標結果與所有 231 對、50 槽均在 [geometry-summary.json](geometry-summary.json)；每件 exact 報告獨立保存。原作者 passed／失敗檔未覆寫，獨立結果與其資料分開。
'''
(H/'GEOMETRY-REVIEW.md').write_text(rep,'utf-8')
manifest={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in H.iterdir() if p.is_file() and p.name!='EVIDENCE-MANIFEST.json'}
(H/'EVIDENCE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n','utf-8')
print(json.dumps({'result':'GO for independent geometry and assembly subreview','fixed_print_sha256':{k:v['sha256'] for k,v in parts.items() if k.endswith('-print')},'dry_seating':dry},indent=2))
