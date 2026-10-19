"""Original source-outline/model correspondence; no source raster pixels used.
Reproduce from a candidate package with: python source/compare_plans.py
Requires Pillow. Reads source/plan-review.json and source/plan-trace.json only;
build_model.py is parsed as text/AST, never executed here.
"""
from pathlib import Path
import ast, hashlib, json, math
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin

HERE=Path(__file__).resolve()
if HERE.parent.name=='source':
    ROOT=HERE.parent.parent
else:
    ROOT=HERE.parent/'candidate'/'國立澎湖科技大學'/'馬公校本部'/'buildings'/'npu-marine-north-south-complex'
QA=ROOT/'qa'; PREVIEW=ROOT/'previews'; QA.mkdir(exist_ok=True); PREVIEW.mkdir(exist_ok=True)
trace_path=ROOT/'source'/'plan-trace.json'
build_path=ROOT/'source'/'build_model.py'
trace=json.loads(trace_path.read_text(encoding='utf-8'))
review=json.loads((ROOT/'source'/'plan-review.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=build_path.read_text(encoding='utf-8')
ast_values={}
for node in ast.parse(build).body:
    if isinstance(node,ast.Assign):
        for target in node.targets:
            if isinstance(target,ast.Name) and target.id in ['N','NU','S','H','B']:
                ast_values[target.id]=ast.literal_eval(node.value)
name_map={'N':'north_main_plan_100mm','NU':'north_upper','S':'south','H':'hall','B':'bridge'}
code_trace_match={k:json.dumps(ast_values[k])==json.dumps(trace[v]) for k,v in name_map.items()}

R={
 'north':[(0,0),(100,0),(100,47.7),(86.9,47.7),(86.9,34.1),(0,34.1)],
 'north_upper':[(0,0),(100,0),(100,47.7),(86.9,47.7),(86.9,34.1),(22.2,34.1),(22.2,48),(0,48)],
 'south':[(106.4,80.7),(160,80.7),(160,93.6),(159.8,93.6),(159.8,149.6),(145.7,149.6),(145.7,162.7),(140,162.7),(140,149.6),(125.7,149.6),(125.7,103.7),(106.4,103.7)],
 'hall':[((x-297)/4.95,(y-525)/4.95) for x,y in review['pages'][0]['hall_plan_envelope_approx_px']],
 'bridge':[(86.4,47.7),(91.1,47.7),(91.1,89.4),(106.4,89.4),(106.4,94.1),(91.1,94.1),(91.1,98.3),(86.4,98.3),(86.4,94.1),(82,94.1),(82,89.4),(86.4,89.4)]
}
M={k:trace[v] for k,v in [('north','north_main_plan_100mm'),('north_upper','north_upper'),('south','south'),('hall','hall'),('bridge','bridge')]}
def box(poly):
    return [min(p[0] for p in poly),min(p[1] for p in poly),max(p[0] for p in poly),max(p[1] for p in poly)]

source_bridge_center=[88.8,91.4]
candidate_bridge_center=[(M['bridge'][0][0]+M['bridge'][1][0])/2,(M['bridge'][2][1]+M['bridge'][4][1])/2]
source_stair=[140,145.7]
# Terminal stair uses the two deepest corner x coordinates in the actual polygon.
deep=max(p[1] for p in M['south'])
actual_stair_x=sorted(p[0] for p in M['south'] if abs(p[1]-deep)<1e-8)
actual_stair_center=sum(actual_stair_x)/len(actual_stair_x)
stair_shift=actual_stair_center-sum(source_stair)/2
translation=trace['south_2F_to_north_2F_translation_px']
bridge_stubs_restored=min(p[0] for p in M['bridge'])<84 and max(p[1] for p in M['bridge'])>96
low_access_added="id='08-south-low-access'" in build
low_access_outline=[(162.2,83),(169.5,83),(169.5,122),(175.4,122),(175.4,127),(162.2,127),(162.2,123),(159.5,123),(159.5,120),(162.2,120),(162.2,92),(159.8,92),(159.8,89),(162.2,89)]
flags=[
 {'id':'SOUTH_TERMINAL_STAIR_POSITION','status':'DEVIATION_REQUIRES_REVIEW' if abs(stair_shift)>.5 else 'WITHIN_MANUAL_TRACE_TOLERANCE','source_x_mm':source_stair,'model_x_mm':actual_stair_x,'center_shift_x_mm':round(stair_shift,3),'significance':'The original x136.5..142.8 candidate was displaced about -3.2 mm (13 source pixels); retain this original flag even after a correction.','original_candidate_x_mm':[136.5,142.8],'original_candidate_center_shift_x_mm':-3.2},
 {'id':'BRIDGE_ELBOW_STUBS_OMITTED','status':'RESTORED_IN_CURRENT_CANDIDATE' if bridge_stubs_restored else 'KNOWN_SIMPLIFICATION','original_status':'OMITTED_IN_INITIAL_CANDIDATE','source':'The official 2F plans show a short image-left nub and a short image-down nub at the elbow.','model':'Current B polygon includes the two short nubs.' if bridge_stubs_restored else 'Candidate bridge polygon keeps the principal L only.','limit':'Restoring the main horizontal outline does not turn the manual trace into an exact dimensioned footprint.'},
 {'id':'SOUTH_EXTERNAL_ENTRY_APPENDAGE','status':'LOW_RELIEF_ADDED_HEIGHTS_AND_ROUTE_SIMPLIFIED' if low_access_added else 'KNOWN_OMISSION_IN_INITIAL_CANDIDATE','original_status':'OMITTED_IN_INITIAL_CANDIDATE','source':'South1 PNG approximately x614..684,y347..585 shows exterior entrance platforms, two short tread bands, long parallel ramp-like lines/arrows and a curved/reversing lower landing. This cannot be read as a multistorey external stair from the source.','model':'08-south-low-access adds a separate low ring/ramp footprint, two short step sets and links at1F, approximate boundsx159.5..175.4,y83..127,z0..2mm.' if low_access_added else 'The initial build_model.py omitted this appendage. Terminal stair and estimated roof fins are different features.','limit':'The current ring greatly simplifies the source reversals, mid-side branch and curved lower landing. Only low entry topology and approximate envelope are represented; no exact continuous accessible route or2F connection is asserted. No readable level heights or long continuously stepped flight are supplied.','conservative_reconstruction':'Separate low1F entry platform/short steps/reversing-ramp footprint only. Step solid thickness1.2-2mm and0.4mm rises are explicit display estimates, never measured.','source_envelope_approx_model_units':[[162,82.6],[175.4,127]]},
 {'id':'SOUTH_WEST_RETURN_DEPTH','status':'APPROXIMATE_SIMPLIFICATION','source_y_max_mm':103.7,'model_y_max_mm':round(M['south'][-1][1],3),'delta_mm':round(M['south'][-1][1]-103.7,3),'limit':'Short stair/lobby return appears about 1 mm shallower than the independent trace; no dimension chain supports precision.'},
 {'id':'HEIGHTS_AND_DETAILS_ESTIMATED','status':'ESTIMATE_NOT_MEASUREMENT','items':['9 mm model story pitch','north porch column count and enlarged thickness','9 mm bridge undercroft and 17.5 mm lid top','hall shell 11 mm / roof peak 15 mm','roof fins, parapets, blind windows, solid enlarged railing bands','bridge pier locations']},
 {'id':'SOURCE_BOUNDARY','status':'NOT_A_MANUFACTURING_PASS','limit':'Outline correspondence does not prove mesh validity, physical fit, accessible supports, slicer success, printed success or multiple-material feasibility.'}
]

pages=[
 {'source':'north','page':1,'checks':[{'feature':'Long bar + image-right return','result':'SUPPORTED_APPROXIMATE_OUTLINE','evidence':'N polygon preserves long bar100 x34.1 and short return to48; independent trace about100 x34.1 and47.7.'},{'feature':'Lobby-connected fan conference hall, single occupied level','result':'SUPPORTED_TOPOLOGY_HEIGHT_ESTIMATED','evidence':'H is unioned only into north-lower z0..11; separate roof z11..15. No additional room body at z18 or above.'},{'feature':'Entrance beneath west upper wing','result':'SUPPORTED_VOID_COLUMNS_ESTIMATED','evidence':'N has no filled body in x0..22,y34.1..48; six enlarged columns and narrow ground ties are explicitly generated. Exact count/thickness not measured.'},{'feature':'Fine fan shell/entry steps','result':'SIMPLIFIED','evidence':'H is an eight-vertex approximation; source polygon has secondary stairs/entrances. Image-left extent model41.2 versus trace41.8 and south depth about1.1mm shorter.'}]},
 {'source':'north','page':2,'checks':[{'feature':'Second-floor bridge at right-return end','result':'SUPPORTED','evidence':'B starts near(88.9,48), runs to(88.9,91.1), then right to x106.2. Source approximately(88.8,47.7) to(88.8,91.4) to106.4.'},{'feature':'Bridge turn nubs','result':flags[1]['status'],'flag':'BRIDGE_ELBOW_STUBS_OMITTED'},{'feature':'Conference hall projection, not 2F room','result':'SUPPORTED','evidence':'Roof is a low separate part; no hall room stacked with upper floors.'},{'feature':'West porch remains unfilled at 2F','result':'SUPPORTED','evidence':'Upper west wing begins at z18, corresponding to modeled3F; lower piloti extend through two modeled levels.'}]},
 {'source':'north','page':3,'checks':[{'feature':'West occupied wing above porch','result':'SUPPORTED_APPROXIMATE_OUTLINE','evidence':'NU includes x0..22,y34.1..48 from z18; source independent trace width22.2 and end y48.'},{'feature':'Hall radial roof projection','result':'SUPPORTED_INTERPRETATION_ROOF_ESTIMATED','evidence':'Low polygon roof, no hall3F room. The rendered roof slope is a design estimate; plans only constrain horizontal fan shell/roof.'}]},
 {'source':'north','page':4,'checks':[{'feature':'Fourth floor bar and end wings','result':'SUPPORTED','evidence':'NU spans z18..36 across two model stories; bar does not incorrectly shorten at4F.'},{'feature':'No hall extension at4F','result':'SUPPORTED','evidence':'H roof ends atz15; hall does not extend to the main roof.'},{'feature':'Roof fins and parapets','result':'ESTIMATE_NOT_MEASUREMENT','evidence':'Heights37.2/38.3/43mm are explicit generated estimates, not extracted from this plan.'}]},
 {'source':'south','page':1,'checks':[{'feature':'Principal L body and inner stair/lobby return','result':'SUPPORTED_APPROXIMATE_OUTLINE','evidence':'S preserves53.6mm total width,34.1mm mainleg width,68.9mm body length; west return is simplified.'},{'feature':'No ground-floor bridge room','result':'SUPPORTED','evidence':'Bridge startsz9; no common slab or body fills the courtyard/undercroft.'},{'feature':'Exterior1F entry ramp/short stairs/platform','result':flags[2]['status'],'flag':'SOUTH_EXTERNAL_ENTRY_APPENDAGE'},{'feature':'Southern terminal stair position','result':flags[0]['status'],'flag':'SOUTH_TERMINAL_STAIR_POSITION'}]},
 {'source':'south','page':2,'checks':[{'feature':'Bridge enters left tip of short wing','result':'SUPPORTED','evidence':'B right end x106.2 shares the S western edge around y88.9..93.3.'},{'feature':'Shared scale and two-plan registration','result':'WITHIN_MANUAL_TRACE_TOLERANCE','evidence':f'Candidate translation{translation}; independent trace[218,261]. Difference in x is {translation[0]-218}px; declared uncertainty2px.'},{'feature':'Bridge elbow small branches','result':flags[1]['status'],'flag':'BRIDGE_ELBOW_STUBS_OMITTED'},{'feature':'Inner west return and grid projection','result':'SIMPLIFIED','evidence':'Return endsy102.7 versus trace103.7; grid/roof projection below is omitted as secondary roof detail, not occupied room evidence.'},{'feature':'Terminal stair','result':flags[0]['status'],'flag':'SOUTH_TERMINAL_STAIR_POSITION'}]},
 {'source':'south','page':3,'checks':[{'feature':'Three-story L','result':'SUPPORTED_HEIGHT_ESTIMATED','evidence':'S bodyz0..27 is three9mm model stories; floor count supported, height unknown.'},{'feature':'No3F bridge','result':'SUPPORTED','evidence':'Bridge lid top17.5 is below modeled3F startingz18; no bridge stacked to3F.'},{'feature':'Terminal stair and small corridor-end protrusions','result':'SIMPLIFIED_WITH_RETAINED_FLAG','evidence':'Terminal stair remains part of S; small corridor-end protrusions are simplified and the stair displacement flag remains in QA history.'}]}
]

out={
 'status':'SOURCE_COMPARISON_COMPLETE_WITH_RETAINED_DEVIATIONS',
 'review_date_utc':'2026-10-19',
 'source_pixels_in_figure':False,
 'inputs':{'build_model.py_sha256':sha(build_path),'plan-trace.json_sha256':sha(trace_path),'plan-review.json_sha256':sha(ROOT/'source'/'plan-review.json')},
 'model_code_trace_literal_match':code_trace_match,
 'source_coordinate_accuracy':'Manual trace about2 rendered pixels; modeled dimensions are normalized mm display coordinates, not measured building dimensions.',
 'coordinate_registration':{'source_south2_to_north2_px':[218,261],'candidate_translation_px':translation,'delta_px':[translation[0]-218,translation[1]-261],'declared_tolerance_px':2,'within_tolerance':all(abs(a-b)<=2 for a,b in zip(translation,[218,261]))},
 'bridge_elbow':{'source_centerline_mm':source_bridge_center,'model_centerline_mm':candidate_bridge_center,'difference_mm':[round(a-b,3) for a,b in zip(candidate_bridge_center,source_bridge_center)]},
 'pages':pages,
 'retained_flags':flags,
 'estimated_dimensions_not_asbuilt':True,
 'source_trace_polygons_model_units':R,
 'candidate_polygons_model_units':M,
 'current_low_1f_access':{'present':low_access_added,'source_approx_envelope_only':[[162,82.6],[175.4,127]],'model_outer_outline':low_access_outline,'source_route_is_not_exactly_reconstructed':True,'platform_step_thickness_mm_estimated':[1.2,2],'step_rise_mm_estimated':.4,'base_z_mm':0},
 'limits':['No source raster page/photograph is embedded in the original comparison image.','This pass examines supplied7plan pages and the candidate generation code; exterior photographic color/material matching was handled separately by the parent.','No geometry is modified by this comparison script.','Manufacturing QA, slicer QA and physical print/fit must be judged separately.']
}
(QA/'source-correspondence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

md='''# 來源平面與候選模型對照

這是七頁官方平面與候選生成碼的對照，不是實測復原或製造通過證明。疊圖只含原創數位描線與候選輪廓，未嵌入來源 PDF/照片像素。原始來源 SHA 與逐頁目視結果見 `source/plan-review.json`。本檢查不修改幾何。

'''
md+=f"檢查輸入：`build_model.py` SHA-256 `{out['inputs']['build_model.py_sha256']}`；`plan-trace.json` SHA-256 `{out['inputs']['plan-trace.json_sha256']}`。生成碼 N/NU/S/H/B 與 trace 的五組 literal 座標均一致：`{all(code_trace_match.values())}`。\n\n"
md+='''## 直接支援的關係

- 北棟四層、南棟三層；北主條與右腿、南 L 主體均保留。
- 北入口上方的左側突出翼自模型 3F 開始，1F/2F下方保留柱廊通空。
- 國際會議廳與大廳相連，只有低體與獨立坡頂；沒有把2F/3F頂蓋投影誤當樓層，也沒有延伸到4F。
- 橋只有二樓一條長豎段再右轉進南短翼；院地與橋下通空，主橋長度約束吻合。

## 座標與偏差

'''
md+=f"候選南2F→北2F平移為 `{translation}` 像素，獨立描線為 `[218,261]`；x差 `{translation[0]-218}` 像素，在約±2像素手動描圖容差內。候選橋轉折中心約 `{candidate_bridge_center}` mm，對照約 `[88.8,91.4]` mm；這些是北主條100mm規格下的模型座標，不是建築尺寸。\n\n"
md+=f"南端樓梯目前候選 x範圍 `{actual_stair_x}` mm，來源描線約 `[140.0,145.7]` mm；中心差 `{stair_shift:.2f}` mm。初版 `136.5..142.8` 的約−3.2mm位移是原始未通過旗標，必須保留。當前判定：`{flags[0]['status']}`。\n\n"
md+='''初版候選橋轉折省略了官方圖上向左與向下的短凸，保留主要 L 路徑；原始旗標保留。南1F圖明確畫出的側邊外部入口附屬在初版未建模，是已知次要構件省略，不能改稱未知設備。放大像素可見上端與下端兩處短踏步線，中段為長平行邊線、箭頭與回折/弧形平台，形態更像低矮入口無障礙坡道；不能據此做二樓高層外梯。若補低矮平台/短階/坡道足跡，1.2-2mm實體厚度與0.4mm階差也只能明示為模型估計。南內角小翼深度比獨立描線短約1mm。會議廳以八頂點扇形簡化，向左範圍約少0.6mm、圖下緣約少1.1mm，細節入口/階梯未逐一復刻。

## 七頁對照

'''
md+=f"當前橋短凸狀態：`{flags[1]['status']}`。當前南側入口附屬狀態：`{flags[2]['status']}`。08低入口附屬保留約x159.5..175.4/y83..127的包絡與兩短階，實體厚度1.2..2mm、階差0.4mm全為估計；其環形足跡大幅簡化原圖回折、中段側支與下部弧形平台，不能宣稱完整坡道動線或無障礙規範相符。\n\n"
for page in pages:
    md+=f"### {'北' if page['source']=='north' else '南'}棟第 {page['page']} 頁\n\n"
    for c in page['checks']:
        md+=f"- {c['feature']}：`{c['result']}`。{c.get('evidence','見保留旗標 '+c.get('flag',''))}\n"
    md+='\n'
md+='''## 估計與補證界線

模型9mm層距、北入口六柱及加厚尺寸、橋下9mm、會議廳11mm主殼/15mm屋頂最高點、屋面鰭片與女兒牆、窗與實心放大欄杆節奏、橋柱位置均是顯示與製造用估計。官方平面沒有完整尺寸鏈或屋頂施工高度。這些值不得美化為測量結果、共同真實層高或2026現況。

來源相符不等於網格/接合/薄壁/支撐可達性/切片通過；未實印與試合不得宣稱成功。色區或預覽有色也不證明四色可列印。圖像採Pillow原創繪製，檔內只含通用Software說明，不記錄私人路徑。
'''
(QA/'source-correspondence.md').write_text(md,encoding='utf-8')

# Original linework chart. Only above numeric polygon traces enter this canvas.
W,H=2500,1820
img=Image.new('RGB',(W,H),'#f8fafc');d=ImageDraw.Draw(img)
def font(size,bold=False):
    for name in (['arialbd.ttf','DejaVuSans-Bold.ttf'] if bold else ['arial.ttf','DejaVuSans.ttf']):
        try:return ImageFont.truetype(name,size)
        except OSError:pass
    return ImageFont.load_default()
F=font(29); SM=font(24); TITLE=font(48,True); SUB=font(32,True)
BLUE='#1367ac'; RED='#d9443a'; PURPLE='#7b3faa'; GREY='#475569'; GREEN='#1f8067'
d.text((55,35),'NPU Marine complex | source trace vs candidate',font=TITLE,fill='#13243a')
d.text((58,103),'Original linework only; no source PDF or photograph pixels. All dimensions are normalized model mm.',font=F,fill=GREY)

def panel(rect,title,bounds):
    x0,y0,x1,y1=rect
    d.rounded_rectangle(rect,radius=18,fill='white',outline='#cbd5e1',width=2)
    d.text((x0+24,y0+17),title,font=SUB,fill='#13243a')
    l=x0+70;t=y0+80;r=x1-28;b=y1-115
    a,c,e,f=bounds
    sc=min((r-l)/(e-a),(b-t)/(f-c))
    cx=(l+r)/2;cy=(t+b)/2
    def T(p):return (cx+(p[0]-(a+e)/2)*sc,cy+(p[1]-(c+f)/2)*sc)
    for x in range(math.ceil(a/10)*10,math.floor(e/10)*10+1,10):
        A=T((x,c));B=T((x,f));d.line([A,B],fill='#edf1f5',width=1)
        d.text((A[0]-10,b+8),str(x),font=font(18),fill='#64748b')
    for y in range(math.ceil(c/10)*10,math.floor(f/10)*10+1,10):
        A=T((a,y));B=T((e,y));d.line([A,B],fill='#edf1f5',width=1)
        d.text((l-43,A[1]-10),str(y),font=font(18),fill='#64748b')
    return T

def dashed(points,color,width=5,dash=12,gap=8):
    for p,q in zip(points,points[1:]):
        dx=q[0]-p[0];dy=q[1]-p[1];ln=math.hypot(dx,dy)
        if not ln:continue
        pos=0
        while pos<ln:
            end=min(pos+dash,ln)
            d.line([(p[0]+dx*pos/ln,p[1]+dy*pos/ln),(p[0]+dx*end/ln,p[1]+dy*end/ln)],fill=color,width=width)
            pos+=dash+gap

def linepoly(T,poly,color,dash=False,width=5):
    pts=[T(p) for p in poly+[poly[0]]]
    if dash:dashed(pts,color,width)
    else:d.line(pts,fill=color,width=width,joint='curve')

T=panel((45,175,1340,1600),'A | joined 2F plan, low hall/entry from 1F',(-48,-10,181,168))
for key in ['north','hall','bridge','south']:
    linepoly(T,R[key],BLUE,True,6);linepoly(T,M[key],RED,False,4)
if low_access_added:
    source_entry_envelope=[(162,82.6),(175.4,82.6),(175.4,127),(162,127)]
    linepoly(T,source_entry_envelope,GREEN,True,3)
    linepoly(T,low_access_outline,RED,False,3)
    linepoly(T,[(163.6,89),(168.1,89),(168.1,122.8),(163.6,122.8)],RED,False,2)
    p=T((161,129));d.text(p,'Low1F entry',font=font(18),fill=GREEN)
    p=T((161,133));d.text(p,'envelope only',font=font(18),fill=GREEN)
for text,pos in [('North 4F body',(27,17)),('Hall 1F',(-33,17)),('2F bridge',(87,72)),('South 3F L',(130,117))]:
    p=T(pos);d.text((p[0],p[1]),text,font=SM,fill='#27364b')
d.text((80,1537),'Blue dashed: independent approximate source trace   Red: generated model',font=SM,fill=GREY)

T=panel((1380,175,2455,715),'B | two 2F plans register at the bridge',(79,45,109,101))
linepoly(T,R['bridge'],BLUE,True,7)
# Southern duplicate trace, transformed with independently read +218,+261px.
south_raw=[(397,433),(416,433),(416,599),(478,599),(478,618),(416,618),(416,637),(397,637),(397,618),(379,618),(379,599),(397,599)]
south_bridge=[((x+218-265)/4.05,(y+261-499)/4.05) for x,y in south_raw]
linepoly(T,south_bridge,PURPLE,True,4);linepoly(T,M['bridge'],RED,False,4)
d.text((1408,650),'N2 blue / S2 purple: +218,+261 px; model red',font=SM,fill=GREY)

T=panel((1380,750,2455,1165),'C | entrance wing starts at modeled 3F',(-4,26,29,52))
# Original excerpt of the upper west wing only, avoiding out-of-panel linework.
small=[(0,26),(22.2,26),(22.2,48),(0,48)]
model_small=[(0,26),(22,26),(22,48),(0,48)]
linepoly(T,small,BLUE,True,6);linepoly(T,model_small,RED,False,4)
p=T((2,39));d.text(p,'Open below 3F',font=SM,fill=GREEN)
d.text((1408,1103),'Outline supported; story heights and six columns estimated',font=SM,fill=GREY)

T=panel((1380,1200,2455,1600),'D | terminal stair position retains original flag',(129,145,151,166))
source_stair_poly=[(140,149.6),(145.7,149.6),(145.7,162.7),(140,162.7)]
original_stair=[(136.5,149.6),(142.8,149.6),(142.8,162.8),(136.5,162.8)]
model_stair=[(actual_stair_x[0],149.6),(actual_stair_x[-1],149.6),(actual_stair_x[-1],deep),(actual_stair_x[0],deep)]
linepoly(T,source_stair_poly,BLUE,True,6);linepoly(T,original_stair,'#b77819',True,3);linepoly(T,model_stair,RED,False,4)
d.text((1408,1533),f'Current center delta: {stair_shift:+.2f} mm; ochre = initial candidate',font=SM,fill=GREY)

d.text((58,1640),'Retained initial flags: bridge elbow stubs; south low1F entrance ramp/short steps/platform.',font=F,fill='#9a4f08')
d.text((58,1693),'Estimated: heights, roof slopes, columns, fins and window rhythm. Source match does not prove printability or physical fit.',font=F,fill=GREY)
d.text((58,1742),'Trace tolerance is about 2 image pixels; no real-world measured dimensions or 2026 as-built claim.',font=F,fill=GREY)
meta=PngImagePlugin.PngInfo();meta.add_text('Software','Original vector plan correspondence; source raster pixels excluded')
img.save(PREVIEW/'plan-comparison.png',pnginfo=meta)
print(json.dumps({'current_stair_flag':flags[0],'code_trace_match':code_trace_match,'outputs':['qa/source-correspondence.json','qa/source-correspondence.md','previews/plan-comparison.png']},ensure_ascii=False))
