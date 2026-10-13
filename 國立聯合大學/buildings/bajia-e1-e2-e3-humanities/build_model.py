"""NUU E1/E2/E3 photo-interpreted FDM miniature. Run with numpy, trimesh, manifold3d.
Millimeter geometry, no surveyed dimensions or asserted common campus scale.
"""
from pathlib import Path
import json, math
import numpy as np
import trimesh
import manifold3d
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];postparts=[]
def box(x0,x1,y0,y1,z0,z1):
 m=trimesh.creation.box([x1-x0,y1-y0,z1-z0]);m.apply_translation([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2]);return m
def add(*args):parts.append(box(*args))
def cut(*args):cuts.append(box(*args))
def prism(points,z0,z1):
 n=len(points);v=[[x,y,z] for z in [z0,z1] for x,y in points];f=[]
 for i in range(1,n-1):f.extend([[0,i+1,i],[n,n+i,n+i+1]])
 for i in range(n):j=(i+1)%n;f.extend([[i,j,n+j],[i,n+j,n+i]])
 m=trimesh.Trimesh(v,f,process=True);m.fix_normals();return m
def stairs(x0,x1,y0,y1,z0,z1,n=14):
 for i in range(n):add(x0,x1,y0+(y1-y0)*i/n,y0+(y1-y0)*(i+1)/n+.08,z0,z0+(z1-z0)*(i+1)/n)
def solar(x0,x1,y0,y1,z,cols,rows):
 for i in range(cols):
  for j in range(rows):
   x=x0+(x1-x0)*i/cols;y=y0+(y1-y0)*j/rows
   add(x,x+(x1-x0)/cols-.6,y,y+(y1-y0)/rows-.6,z-.1,z+.8)
def front_windows(x0,x1,y,z,rows=3,spacing=8):
 for k in range(rows):
  for x in np.arange(x0,x1-3,spacing):cut(x,min(x+spacing-1.5,x1),y-.2,y+1.1,z+k*10,z+k*10+6)
# Base and rising rear terrain, united but building identities retained.
add(-75,75,-60,60,0,3)
add(-63,55,24,54,2.8,12)
# E3: rear three-storey framed wing, left solid end and taller right stair tower.
add(-60,36,29,49,11.8,51)
add(-61,-42,27,50,11.8,52)
for z in [16,28,40]:
 for a,b in [(-40,-27),(-25,-9),(-7,10),(12,31)]:cut(a,b,28.7,35,z,z+8.2)
 add(-41,34,27.8,35,z-1.2,z+.2)
 add(-40,33,28.1,29.4,z+.1,z+1.6)
for x in [-42,-27,-9,10,31]:add(x,x+1.8,27.8,35,14,52)
# Slightly raised roof with panel grid.
add(-43,36,27,50,50.7,53)
solar(-40,33,30,48,52.9,10,3)
add(-61,-42,27,50,51.7,53.2);solar(-59,-45,30,48,53.1,2,3)
# High right tower with open front bays; tall terminal head.
add(34,51,26,49,11.8,61)
for z in [16,28,40]:
 cut(36.2,47.8,25.7,31.2,z,z+8)
 add(36,48,25.8,27.1,z,z+1.3)
cut(38,41,25.8,27,53,58);cut(44,47,25.8,27,53,58)
# Characteristic smaller front framing of the lower E3 levels.
add(-9,-7.2,24.8,30,13,40);add(14,15.8,24.8,30,13,40);add(-9,15.8,24.8,30,38.3,40)
# E2: middle long three-storey wing, left projecting lower terrace and roof pavilion.
add(-58,60,-5,16,2.8,36)
# Left lower volume and inset top-floor volume.
add(-60,-22,-9,16,2.8,26)
add(-52,-22,-5,16,25.8,38)
add(-61,-21,-10,17,25.4,27.2)
add(-61,-21,-10,-8.6,27,29);add(-61,-59.6,-10,17,27,29)
add(-53,-20,-6,17,37.7,39.6);solar(-50,-23,-3,14,39.5,4,3)
# Right solar-covered roof, lower than central tower.
add(-5,61,-6,17,35.7,38);solar(-2,58,-3,14,37.9,8,3)
front_windows(-56,-24,-9,6,2,9)
front_windows(-49,-25,-5,30,1,8)
front_windows(14,58,-5,6,3,9)
# Bonded 0.8 mm window mullions in visible E2 glazing, retained after recess cuts.
for x0,x1,y,z,rows,spacing in [(-56,-24,-9,6,2,9),(-49,-25,-5,30,1,8),(14,58,-5,6,3,9)]:
 for k in range(rows):
  for x in np.arange(x0,x1-3,spacing):
   end=min(x+spacing-1.5,x1);mid=(x+end)/2;zz=z+k*10
   postparts.append(box(mid-.4,mid+.4,y-.05,y+1.3,zz-.1,zz+6.1))
   postparts.append(box(x-.1,end+.1,y-.05,y+1.3,zz+2.6,zz+3.4))
# Deeper middle façade bays and solid piers.
for z in [6,16,26]:
 cut(-21,-7,-5.2,.4,z,z+7.5)
 add(-21,-7,-5.5,-4.1,z-.3,z+1)
add(-23,-21,-6,1,3,39)
# E2 tall central open stair tower, broad horizontal landings.
add(-7,13,-10,16,2.8,46)
for z in [6,16,26,36]:
 cut(-4.5,10.5,-10.2,-3.5,z,z+7.5)
 add(-4.5,10.5,-10.2,-8.8,z-.1,z+1.2)
 # Supported diagonal stair profile deep inside the actual cutout.
 for i in range(8):postparts.append(box(-3.8,9.8,-7.4+i*.56,-6.8+i*.56,z-.1,z+1+i*.74))
# E1 low curved classroom wing: curved terrace retained as physical mesh.
def front(x):return -42+.0018*(x-4)**2
def back(x):return -23+.0018*(x-4)**2
xs=np.linspace(-13,67,33)
for a,b in zip(xs[:-1],xs[1:]):
 pts=[(a,front(a)),(b+.015,front(b)),(b+.015,back(b)),(a,back(a))]
 parts.append(prism(pts,2.8,14))
 # Broad slab and printable solid low parapet replace fine metal rails.
 parts.append(prism([(a,front(a)-.7),(b+.015,front(b)-.7),(b+.015,back(b)+.4),(a,back(a)+.4)],13.6,15.7))
 parts.append(prism([(a,front(a)-.6),(b+.015,front(b)-.6),(b+.015,front(b)+.7),(a,front(a)+.7)],15.5,17.5))
 # inset window pockets through front exterior, with 1.3 mm remaining top/bottom.
 if a>-9 and b<64:cuts.append(prism([(a+.45,front(a)-1),(b-.35,front(b)-1),(b-.35,front(b)+1),(a+.45,front(a)+1)],5.4,11.3))
# End walls and the broad foreground stair.
add(-14,-12,-42.3,-21,14,17.5)
stairs(-14,3,-57,-32,3,15.7,17)
# stair side cheeks, solid supporting triangular prisms omitted to preserve open treads.
# E1 rear small upper terrace and second broad stair, visible on right.
add(52,68,-14,2,3,24)
add(51,69,-15,3,23.5,25.4)
add(67.5,69,-15,3,25.2,27);add(51,69,1.7,3,25.2,27)
stairs(52,63,-29,-11,15,25.4,12)
# Short terrace bridges are supported solid abstractions at this scale.
add(34,51,-22,-17,12.5,15.5);add(35,37,-21,-17,3,13)
add(57,62,0,9,23,25.2)
# Photo-invisible rear elevations intentionally remain undecorated.
mesh=trimesh.boolean.union(parts,engine='manifold')
mesh=trimesh.boolean.difference([mesh,*cuts],engine='manifold')
mesh=trimesh.boolean.union([mesh,*postparts],engine='manifold')
# Remove sub-micron sliver triangles introduced by adjacent curved segments.
mf=manifold3d.Manifold(manifold3d.Mesh(np.asarray(mesh.vertices,dtype=np.float32),np.asarray(mesh.faces,dtype=np.uint32))).simplify(.003).to_mesh()
mesh=trimesh.Trimesh(np.asarray(mf.vert_properties)[:,:3],np.asarray(mf.tri_verts),process=True)
mesh.remove_unreferenced_vertices();mesh.export(OUT/'model.stl')
manifest={'name_zh':'國立聯合大學八甲校區人文與社會學院 E1前棟＋E2中棟＋E3後棟','components':[{'code':'E1','name_zh':'人文與社會學院前棟','features':['低矮弧形階梯教室翼','大露台','寬外階梯']},{'code':'E2','name_zh':'人文與社會學院中棟','associated_department':'臺灣語文與傳播學系','features':['三層長翼','中央開口樓梯塔','左端退台']},{'code':'E3','name_zh':'人文與社會學院後棟','associated_department':'華語文學系','features':['後側高台上三層柱廊','右端高塔','屋頂太陽能板']}],'units':'mm','longest_edge_mm':150,'common_campus_scale':False,'method':'Photo-interpreted simplified miniature; not survey, BIM, or measured replica.','uncertainties':['Relative footprint, levels and spacing estimated from photographs.','Unseen rear elevations simplified.','Base slope represented by stepped plinth.','Fine railings replaced with thick parapets; solar panels rendered as bonded relief.'],'print_design':{'base_mm':3,'minimum_parapet_mm':1.3,'minimum_posts_mm':1.8,'note':'Deep corridor and stair-tower overhangs require slicer support review. No physical print test.'}}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(mesh.extents)
