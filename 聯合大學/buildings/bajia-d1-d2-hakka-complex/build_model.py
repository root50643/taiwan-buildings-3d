"""NUU Bajia D1/D2: photo-interpreted printable massing, millimeters.
Run: python build_model.py (numpy, trimesh, manifold3d).
No surveyed dimensions; placement/back elevations are approximate.
"""
from pathlib import Path
import json
import numpy as np
import trimesh
OUT=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x0,x1,y0,y1,z0,z1):
 m=trimesh.creation.box([x1-x0,y1-y0,z1-z0]);m.apply_translation([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2]);return m
def add(*a): parts.append(box(*a))
def cut(*a): cuts.append(box(*a))
def stairs(x0,x1,y0,y1,z0,z1,n=12):
 for i in range(n):
  a=y0+(y1-y0)*i/n;b=y0+(y1-y0)*(i+1)/n+.08
  add(x0,x1,a,b,z0,z0+(z1-z0)*(i+1)/n)
def panels(x0,x1,y0,y1,z,cols,rows):
 # Solid bonded panel tiles rather than floating roof equipment.
 for i in range(cols):
  for j in range(rows):
   a=x0+(x1-x0)*i/cols;b=y0+(y1-y0)*j/rows
   add(a,a+(x1-x0)/cols-.65,b,b+(y1-y0)/rows-.65,z-.1,z+.75)
# Shared base; raised rear plinth represents slope only schematically.
add(-75,75,-59,59,0,3)
add(-66,64,5,51,2.8,8)
# D1: front low long block, inset upper corridor, stepped terrace, solid east end.
add(-60,60,-33,-10,2.8,29)
# upper recessed arcade; left pavilion and right end wall retained
for a,b in [(-26.4,-8),(-6.4,12),(13.6,32),(33.6,38)]:cut(a,b,-34,-27,18,26.8)
for x in [-28,-8,12,32]:add(x,x+1.6,-33.4,-26,17.8,27.3)
# lower projecting terrace/occupied base and long parapet
add(-20,39,-43,-26,2.8,15)
add(-21,40,-44,-26,14,16.5)
add(-20,39,-44,-42.6,16.3,18)
add(38,39.5,-43,-27,16.3,18)
# recognisable staircase to terrace, supported solid for print
stairs(-32,-20.5,-53,-31,3,17,14)
# left roof / lower central roof / raised solid end
add(-61,-28,-34,-9,28.3,30.1)
add(-28,40,-30,-9,28.2,29.6)
add(39,61,-34,-9,28.3,31)
panels(-57,-31,-30,-12,30.0,4,3)
panels(-25,37,-25,-12,29.5,8,2)
panels(42,58,-30,-12,30.9,3,3)
# shallow actual facade pockets, not display-only textures
for xa,xb in [(-56,-35),(-16,-2),(2,16),(20,35)]:
 ya=-33.15 if xa < -30 else -43.15
 cut(xa,xb,ya,ya+1.2,7,12.6)
 for x in np.arange(xa+3,xb,3.8):add(x,x+.8,ya+.1,ya+1.4,6.8,12.9)
cut(-56,-35,-33.2,-32,20,25.8)
for x in np.arange(-52,-35,4):add(x,x+.8,-33.1,-31.8,19.8,26)
# right end billboard shallow frame, no invented lettering
add(42,58,-34,-32.9,19,26.5);cut(43.2,56.8,-34.2,-33.6,20.2,25.3)
# D2: rear three-storey framed corridor, taller vertical tower to its left.
add(-53,56,24,46,7.8,46)
# two floor recesses in right portion; outer deep frame and three piers
for z in [12,24,36]:
 for a,b in [(-6.2,11),(12.8,31),(32.8,50)]:cut(a,b,23.7,30,z,z+7.5)
for x in [-8,11,31,50]:add(x,x+1.8,23.6,30.3,10,46.5)
for z in [11.5,23.5,35.5,45]:add(-8,53,23.1,31,z,z+1.7)
# balcony parapets; supported by floor slab
for z in [13.1,25.1,37.1]:add(-7,51,23.3,24.5,z,z+1.4)
# Tower has large framed voids and tall flat upper head
add(-31,-9,19,44,7.8,58)
for z in [11,24,37]:cut(-27,-12,18.7,23,z,z+8)
# High side window recess (interpretation of visible high window band)
cut(-9.3,-7.9,26,40,51,55)
# Frontward two-level entrance pavilion, broad roof terrace, awning
add(-55,-27,7,27,7.8,32)
add(-56,-26,6,28,31,33.2)
for x0,x1 in [(-53,-42),(-40,-29)]:cut(x0,x1,6.7,8.2,10,18)
cut(-27.3,-25.8,10,23,23,29)
# Porch canopy is thick and braced by side posts for FDM
add(-55,-27,1.5,9,18,19.8)
add(-54,-52.4,2.2,8,7.8,18.4);add(-29.6,-28,2.2,8,7.8,18.4)
# Terraced landing and approach stair distinct from D1 stair
add(-61,-25,-2,8,6.5,9.5)
stairs(-64,-56,-11,8,3,9.5,8)
# main roof / solar array relief
add(-8,57,23,47,45.8,47.5)
panels(-5,52,28,44,47.4,8,3)
# Right end supported exterior stair profile, widened at miniature scale
stairs(53,61,10,25,8,24,12)
add(53,61,23,27,23,25)
# rooftop porch parapet, low solid substitutes for fragile original railing
add(-56,-26,6,7.3,33.1,34.6)
add(-56,-54.7,6,28,33.1,34.6)
# Minimal rear treatment: blank surfaces deliberately avoid invented window counts.
mesh=trimesh.boolean.union(parts,engine='manifold')
mesh=trimesh.boolean.difference([mesh,*cuts],engine='manifold')
# Coarse bonded mullions are added AFTER recess subtraction, anchored to
# window-pocket backs, floor and head. Only a few visible-grid divisions.
mullions=[]
for xa,xb,y,z0,z1 in [(-56,-35,-33.05,7,12.6),(-56,-35,-33.05,20,25.8),(-16,-2,-43.05,7,12.6),(2,16,-43.05,7,12.6),(20,35,-43.05,7,12.6)]:
 for x in np.arange(xa+3.5,xb-1,4.5):
  mullions.append(box(x,x+.8,y,y+1.3,z0-.15,z1+.15))
 zm=(z0+z1)/2
 mullions.append(box(xa-.15,xb+.15,y,y+1.3,zm-.4,zm+.4))
mesh=trimesh.boolean.union([mesh,*mullions],engine='manifold')
mesh.remove_unreferenced_vertices();mesh.export(OUT/'model.stl')
manifest={'name_zh':'國立聯合大學八甲校區客家研究學院 D1 前棟＋D2 後棟','components':[{'code':'D1','name_zh':'客家研究學院前棟','features':['低長條館','退縮露台','寬外階梯','東端實牆與看板框']},{'code':'D2','name_zh':'客家研究學院後棟','features':['高直立塔','前凸兩層門廳','雨棚','矩形框架廊道']}],'units':'mm','longest_edge_mm':150,'common_campus_scale':False,'method':'Photo-interpreted simplified miniature, not survey/BIM. Shared base unifies print, not building identity.','uncertainties':['Back elevations simplified without invented exact window counts.','Relative footprint and inter-building spacing approximate.','Slope represented by stepped plinth; no surveyed heights.','No assertion about unseen physical connections.'],'excluded':['E3 華語文學系背景建築','其他前景屋頂'],'print_design':{'base_mm':3,'thin_facade_members_min_mm':0.8,'structural_posts_min_mm':1.6,'warning':'Recess ceilings and canopy require slicer support review; not physically print-tested.'}}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(mesh.extents)
