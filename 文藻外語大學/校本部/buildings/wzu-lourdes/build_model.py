"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. No survey or interior data used.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def gable(x,y,z,w,d,h):parts.append(profile([(x-w/2,z),(x+w/2,z),(x,z+h)],y,d))
def arch(x,y,z,w,h,depth):
 r=w/2; spring=z+h-r
 pts=[(x-r,z),(x+r,z),(x+r,spring)]
 pts += [(x+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,25)[1:]]
 return profile(pts,y,depth)
def arch_cut(x,y,z,w,h,depth):cuts.append(arch(x,y,z,w,h,depth))
def arch_trim(x,y,z,w,h):
 # Backed relief ring, fused into the wall, not a separate floating shell.
 details.append(arch(x,y,z,w+1.7,h+.85,1.7)-arch(x,y-.1,z-.2,w,h+.2,2.3))
def hip(x,y,z,w,d,h):parts.append(CrossSection.square((w,d),center=True).extrude(h,scale_top=(.72,.03)).translate((x,y,z)))
def column(x,y,z,r,h):parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
def step(x,y,w,n=3):
 for i in range(n):add(x,y+i*1.4,2.8,w,1.7,.7*(i+1))
# Remaining Lourdes hall: short surviving western return and longer eastern return.
# 2005-demolished western building is not restored. Footprint follows current published outer outline.
add(0,0,0,150,124,3)
# Far/main bar and asymmetric remaining returns form an open court.
add(0,34,2.8,134,20,56)
add(-56,11,2.8,22,50,56)
add(56,-6,2.8,22,84,56)
# Rear centre ceremonial entry rises above adjacent wings.
add(0,27,2.8,31,34,61)
cut(0,27,3,22,37,17)
# Central trio of tall panes, roof columns and deep portal survive in actual 2023 inventory photo.
for x in [-10,0,10]:
 for z in [25,43]:
  cut(x,10,z,7,3.4,11)
  details.append(box(x,10,z+5,7,3.1,1.1))
# Galleries on courtyard-facing wings are genuine deep recesses divided by piers.
for x,ys in [(-45,[-7,8,23]),(45,[-39,-24,-9,6,21])]:
 for y in ys:
  for z in [6,24,42]:cut(x,y,z,7,11,11)
# Main bar courtyard-facing galleries flank the central ceremonial volume.
for x in [-40,-25,25,40]:
 for z in [6,24,42]:cut(x,24,z,10,5,11)
# Distinct low traditional tiled roofs and higher central hipped roof.
hip(0,34,58,142,27,7)
for x,cy,dep in [(-56,11,57),(56,-6,91)]:hip(x,cy,58,29,dep,7)
hip(0,27,63.5,38,42,10)
# Thickened shallow upswept eave ends at the central entrance.
parts.append(profile([(-21,64),(-17,62.5),(17,62.5),(21,64),(21,65.5),(17,64),(-17,64),(-21,65.5)],8,4))
# Forecourt steps stop at centre of open passage; no courtyard is filled with a solid building.
for i in range(4):add(0,3+i*1.5,2.8,28,1.8,.8+i*.65)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
