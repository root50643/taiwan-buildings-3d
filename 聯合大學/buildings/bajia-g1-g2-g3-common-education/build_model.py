"""國立聯合大學 G1/G2/G3 共教組：照片判讀近似模型，單位 mm。
執行：python build_model.py。非實測；三棟共用列印底座。
"""
from pathlib import Path
import json
import numpy as np
import trimesh
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; detail=[]
def box(a,b,c,d,e,f):
 m=trimesh.creation.box([b-a,d-c,f-e]);m.apply_translation([(a+b)/2,(c+d)/2,(e+f)/2]);return m
def add(*v):parts.append(box(*v))
def cut(*v):cuts.append(box(*v))
def wedge(a,b,c,d,z,h):
 p=[[x,y,k] for x in [a,b] for y,k in [(c,z),(d,z),(c,z+.9),(d,z+h)]]
 return trimesh.convex.convex_hull(p)
def stair(a,b,c,d,z,h,n=12):
 for i in range(n):add(a,b,c+(d-c)*i/n,c+(d-c)*(i+1)/n+.1,z,z+h*(i+1)/n)
def solar(a,b,c,d,z,h,cols=10,rows=3):
 parts.append(wedge(a-1,b+1,c-1,d+1,z-.6,h+.35))
 for i in range(cols):
  for j in range(rows):
   x=a+(b-a)*i/cols;y=c+(d-c)*j/rows;dy=(d-c)/rows-.5
   zz=z+.9+(h-.9)*(y-c)/(d-c)
   parts.append(wedge(x,x+(b-a)/cols-.55,y,y+dy,zz-.22,.65+(h-.9)*dy/(d-c)))
def corridor(a,b,y,back,zbase,top):
 add(a,b,y,back,zbase,top)
 for z in np.arange(zbase+2.5,top-6,10):
  for x in np.arange(a+2,b-5,14):
   cut(x,min(x+11,b-2),y-.2,y+3.5,z,z+6.2)
   # bonded mullions and balcony edges added after subtraction
   detail.append(box(x,min(x+11,b-2),y+.05,y+1.0,z-.15,z+1))
   detail.append(box(x+5,x+5.8,y+2.8,y+3.8,z-.1,z+6.3))
# 底座及示意坡地。前方 -Y；不是測量地形。
add(-75,75,-54,54,0,3)
add(-65,63,16,49,2.8,8)
add(-66,66,-19,15,2.8,5)
# G1：弧形前緣教室及連續屋頂景觀平台。
# 多段小量體相互交疊，形成可列印的緩弧前立面。
for i in range(20):
 x=-49+i*4.7;front=-43+3.3*((x+2)/47)**2
 add(x,x+4.85,front,-23,2.8,12)
 add(x,x+4.85,front-.4,-22.8,11.7,13.1)
 add(x,x+4.85,front-.4,front+.8,13,14.2)
 if i%4!=3:cut(x+.55,x+4.1,front-.2,front+1.05,5.2,10.1)
# G1 landscaped terrace extends back, curved paving represented by low relief.
add(-49,45,-30,-18,3,12.8)
for x,y,r in [(-29,-29,3.3),(-3,-31,3.4),(23,-28,3.0)]:
 m=trimesh.creation.cylinder(radius=r,height=1.2,sections=32);m.apply_translation([x,y,13.3]);parts.append(m)
# broad paved curved path: bonded low rings represented by small strips
for i in range(26):
 x=-46+i*3.4;y=-32+5*np.sin((x+46)/88*np.pi)
 add(x,x+3.6,y,y+2.2,12.5,13.25)
# Left access stair toward terrace; supported solid steps.
stair(-59,-50,-45,-19,3,10,12)
# G2：中棟，三層長外廊、左右不對稱端部。
corridor(-49,48,-14,9,4.8,37)
# lower left terrace pavilion and windows
add(-65,-49,-19,9,4.8,17);add(-65.5,-48,-20,10,16.7,18.2)
cut(-62,-52,-19.2,-17.8,8,14)
add(-65.5,-64.2,-20,10,18,19.5);add(-65.5,-49,-20,-18.8,18,19.5)
# Tall flat stair/elevator tower at G2 western end, inset openings.
add(-49,-37,-17,7,4.8,51)
for z in [9,20,31]:cut(-49.2,-46.9,-14,-6,z,z+7)
cut(-44,-42,-17.2,-15.7,42,44.3)
# Tower terraces project west in side view.
for z in [18,29,40]:
 add(-53,-48,-15,6,z,z+1.5)
 add(-53,-51.8,-15,6,z+1.4,z+2.7)
# G2 main roof: two separated inclined solar roofs with a flat gap.
solar(-33,-2,-11,7,37,3.5,6,3)
solar(12,30,-11,7,37,3.5,4,3)
# right external framed staircase, two shifted rectangular frames.
add(47,49,-21,8,4.8,35)
add(61,63,-21,8,4.8,25)
add(53,55,-18,8,24.8,35)
for z in [5,15,25]:add(47,63,-21,8,z,z+1.7)
add(47,55,-18,8,34,36)
# Front-visible anchored stair relief in the two lower open frames.
# These thick treads intentionally face the preview, unlike hidden rear ramps.
for z in [6.5,16.5]:
 for i in range(12):
  x=49+i
  add(x,x+1.1,-20.8,-14.5,z-.2,z+.8+i*.75)
# The small upper frame retains its separate staircase.
for i in range(8):
 x=49+i*.5
 add(x,x+.6,-17.8,-12,26.5,27.3+i*.95)
# G3：後棟，前凸低端塊＋三層長廊與東端高塔。
corridor(-49,45,27,46,7.8,47)
add(-62,-48,19,45,7.8,27)
add(-62.5,-47,18.5,46,26.6,28.2)
add(-62.5,-61.2,18.5,46,28,29.6);add(-62.5,-47,18.5,19.8,28,29.6)
cut(-59,-51,18.3,20,13,22)
stair(-64,-57,6,19,3,11,12)
solar(-48,-22,28,45,47,3.6,5,3)
solar(-7,32,28,45,47,3.6,8,3)
# opposite-end tower and its side landings
add(37,48,23,46,7.8,56)
for z in [16,27,38]:
 add(47,54,24,43,z,z+1.5)
 add(52.7,54,24,43,z+1.3,z+2.7)
cut(40,42,22.8,24.2,47,49.2)
# middle visible short bridge, treated as terrace rather than invented enclosed connector
add(-22,-8,24,29,22,23.7);add(-22,-20.5,21,28,7.8,23.5)
# G2 entrance canopy, anchored by facade and two piers
add(-17,5,-19,-13,14,15.5)
add(-17,-15.5,-19,-13,4.8,15);add(3.5,5,-19,-13,4.8,15)
mesh=trimesh.boolean.union(parts,engine='manifold')
mesh=trimesh.boolean.difference([mesh,*cuts],engine='manifold')
mesh=trimesh.boolean.union([mesh,*detail],engine='manifold')
mesh.remove_unreferenced_vertices();mesh.export(OUT/'model.stl')
manifest={'name_zh':'國立聯合大學八甲校區 G1／G2／G3 共同教育館舍組','components':[{'code':'G1','name_zh':'前排共同教室與景觀平台'},{'code':'G2','name_zh':'中排共同教育委員會館舍'},{'code':'G3','name_zh':'後排教務處館舍'}],'units':'mm','longest_edge_mm':150,'common_campus_scale':False,'method':'Photo-interpreted approximate exterior, not survey/BIM.','print_design':{'base_mm':3,'balcony_rail_solid_min_mm':1.2,'small_bonded_mullions_mm':0.8,'supports':'Review exterior stair frame, terrace overhangs and corridor recess ceilings in slicer.'},'uncertainties':['Building depth and relative spacing inferred.','Rear facades deliberately simplified.','G1 obscured footprint and vegetation simplified.','Terrain shown as schematic stepped plinth.','Internal connections are not reconstructed.'],'excluded':['E1–E3 人文與社會學院','D1–D2 客家研究學院','家具、車輛與植物細枝'],'source_album':'https://secretary.nuu.edu.tw/p/132-1003-1099.php?Lang=zh-tw'}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(mesh.extents)
