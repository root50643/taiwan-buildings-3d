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
# Sports and Leisure Multi-Functional Building, including high teaching/gym
# volume and low pool wing. All exterior massing is an approximate photo study.
add(0,0,0,150,108,3)
# Higher gym/teaching block, lower swimming wing and attached rear glazed wing.
add(-33,-4,2.8,66,70,40.7)
add(31,0,2.8,62,68,23.7)
add(23,36,2.8,80,18,22.6)
# Gentle bowed/folded green roofs, built as substantial closed solids.
parts.append(profile([(-68,42.8),(-55,46.0),(-17,46.0),(2,44.5),(2,46.1),(-17,47.6),(-55,47.6),(-68,44.4)],-4,75))
parts.append(profile([(-1,26.0),(23,29.2),(49,27.7),(66,24.7),(66,26.3),(49,29.3),(23,30.8),(-1,27.6)],0,72))
add(23,36,25.0,84,21,1.5)
# Tall rectangular circulation/service tower at the joint, rising above both roofs.
add(2,-29,2.8,12,20,50.2)
for z in [6,14,22,30,38]:cut(2,-39, z,2.7,2.8,4.2)
cut(5,-39,8,1.2,2.6,32)
# High block clerestory runs around two visible sides with substantial mullions.
cut(-32,-39,36.6,54,3.6,4.2)
for x in range(-57,-4,7):details.append(box(x,-38.2,36.5,1.3,2.1,4.5))
cut(-66,-4,36.6,3.6,57,4.2)
for y in range(-28,27,7):details.append(box(-65.2,y,36.5,2.1,1.3,4.5))
# Two lower levels have irregular recessed windows and deep full-height piers.
for x in [-57,-44,-31]:
 cut(x,-39,6,8,4.3,9.5)
 cut(x,-39,19,8,4.3,6.8)
 add(x-5.2,-40,2.8,2.6,3,13.8)
# Wider entrance on the right of the high block, with small backed sun canopy.
cut(-15,-39,5.1,16,4.8,7.3)
cut(-15,-39,18.1,16,4.8,6.8)
add(-15,-41,12.0,18,5.5,1.3)
for x in [-22,-8]:add(x,-42.4,2.8,1.5,1.8,9.5)
for y in [-29,-15,-1,13,27]:
 cut(-66,y,6,4.2,8,9.5);cut(-66,y,19,4.2,8,6.8)
 add(-67,y-5.2,2.8,3,2.6,13.8)
# Pool wing: six big glazing panels across two levels, heavy shared wall piers.
for x in [14,28,42]:
 cut(x,-34,5.0,11.3,3.6,8.0)
 cut(x,-34,15.0,11.3,3.6,8.1)
 details.append(box(x,-33.1,5,1.1,2,18.1))
# Pool's far end, seen obliquely; retain large glazing recessed behind an end pier.
for y in [-23,-10,3,16,29]:
 cut(62,y,5,3.4,9.8,8);cut(62,y,15,3.4,9.8,7.4)
# Rear attached glazed wing and balcony rhythm visible in official fourth photo.
for x in [-11,2,15,28,41,54]:
 for z in [5,15]:cut(x,45,z,10.3,3.5,8.2)
 details.append(box(x,44.1,5,1.1,2,18.2))
for y in [32,40]:
 for z in [5,15]:cut(-17,y,z,3.6,5.4,8.2)
# Unphotographed high-block rear is kept as broad restrained wall with fewer bays.
for x in [-56,-42,-28]:
 for z in [7,20]:cut(x,31,z,8,2.8,7)
# Visible attached roof heads; no tiny aerials or unsupported railings reproduced.
add(-51,12,45.2,11,10,4.2)
add(-26,17,45.2,10,9,3.1)
add(25,35,26,16,8,3.8)
for i in range(3):add(-15,-47+i*1.35,2.8,21,1.7,.85*(i+1))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
