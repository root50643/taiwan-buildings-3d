"""資訊大樓資訊中心雙層辦公翼與入口段，毫米。
依官方 a3-03/a3-05/a3-07 平面與 2015-09-08 校方多角度實拍自建。
只保留雙層辦公翼、玻璃磚端牆、入口雨棚及相鄰門廳；不含三層教室長翼與國際會議廳。
未見辦公翼內向背面窗高以平面窗位與可見立面近似。屋頂不代表 2026 年設備現況。
"""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
# Base, main 2F office wing (the 1F rooms 101–105 and 2F rooms 201–205).
add(0,8,0,150,82,2.8)
add(0,0,2.6,134,35.5,31.8)
# Tall stair end-wall projection, not a third occupied office floor.
add(-65.8,0,2.6,5.2,37.5,33.6)
# Hallway/foyer projection: only the part between this wing and the source's entry canopy.
add(-37,24,2.6,38,15,25.8)
add(-49.5,23,2.6,13,14.5,29.8)
# Low entrance canopy on two robust round columns; underside remains open.
add(-49.8,39.0,15.7,31,17.4,2.1)
add(-49.8,39.0,17.5,31,17.4,2.6)
# Parapet shallow recess preserves the heavy upturned canopy edge.
cut(-49.8,39.0,18.8,27.4,13.8,2.0)
for x in [-62,-37.5]:parts.append(Manifold.cylinder(14.1,1.6,1.6,32).translate((x,44.5,2.6)))
# Broad glazed entrance and adjacent foyer wall, split into robust major bays only.
for x in [-56,-48,-40,-30,-22]:cut(x,31.45,5.0,5.3,2.5,8.5)
for x in [-35,-26]:cut(x,31.5,18.7,6.0,2.5,6.3)
# 14 main front openings per row: 12 narrow middle openings, wider end bays.
# Deliberately no small door-leaf mullions mistaken for extra structural bays.
for z,h in [(6.2,10.0),(21.6,9.0)]:
 for x in np.linspace(-48,48,12):cut(float(x),-17.8,z,5.5,2.6,h)
 for x in [-59.3,59.3]:cut(x,-17.8,z,10.0,2.6,h)
# Inward office-wall windows located from published plans. Heights are estimated, not measured.
for z,h in [(6.4,9.5),(21.7,8.7)]:
 for x in np.linspace(-6,59,9):cut(float(x),17.8,z,4.4,2.4,h)
# 3 x 3 large glass-block groups at the stair end. Fine individual glass-block grid omitted.
for y in [-10.6,0,10.6]:
 for z in [4.7,13.9,23.1]:cut(-68.5,y,z,2.6,7.5,7.3)
# Coarsened glass-block texture: 3 x 3 cells per group, fully backed. Real finer grid is omitted.
for y in [-10.6,0,10.6]:
 for z in [4.7,13.9,23.1]:
  for yy in [y-1.25,y+1.25]:details.append(box(-67.9,yy,z,.9,.9,7.3))
  for zz in [z+2.4,z+4.9]:details.append(box(-67.9,y,zz,.9,7.5,.9))
# Tall side slits flanking the end-wall panel, observed in the source oblique.
for y in [-17.8,17.8]:
 for z in [6.5,22.0]:cut(-66.6,y,z,2.5,2.2,8.5)
# Far end stair cap: plan fixes narrow projections, side glazing is simplified.
add(63,0,2.6,8,36.7,32.0)
for z in [6.2,21.6]:cut(67.1,0,z,2.4,9.0,9.0)
# Low parapet recess, open to sky; no floating rooftop plant or sealed void.
cut(0,0,33.2,122,28.5,1.8)
# Entry stair with solid risers, 0.6 mm rise and broad treads.
for i in range(5):add(-49.8,48.2-i*1.5,2.6+i*.6,31,3.0,.8)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for d in details:solid=solid+d
assert len(solid.decompose())==1,'Disconnected or enclosed shell'
m=solid.simplify(1e-5).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight)
