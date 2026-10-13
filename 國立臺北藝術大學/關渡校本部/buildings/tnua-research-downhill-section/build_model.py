"""北藝大研究大樓下坡端量體段；原創近似，不是全棟。單位毫米。
-Y: 2018/2023 照片中六窄窗＋兩側窄窗的下坡端。
+Y: 長翼截斷面；+X: 連體關係未明的一側，保守封面不杜撰窗列。
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def profile_y(poly,x,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,90)).translate((x-depth/2,0,0))
add(0,0,0,114,150,3)
# Downhill front six visible horizontal window tiers; two brick tiers below four gray.
add(0,-27,2.8,86,40,90.2)
# Cropped first three bays of the adjacent long wing; remainder not reconstructed.
add(0,21.5,2.8,86,57,84.2)
# Tall flat-topped core and two unequal-height shoulders.
add(0,-16,92.8,86,18,31.2)
add(0,-35,92.8,57,24,19.2)
for x in [-37,37]:add(x,-36,92.8,12,22,8.0)
# Six primary openings under the lean-to roof, and eight in each of the lower gray rows.
central=[-22.5,-13.5,-4.5,4.5,13.5,22.5]
for x in central:cut(x,-47,98.2,3.8,4,11.2)
for z in [47.5,64.5,81.5]:
 for x in [-36]+central+[36]:cut(x,-47,z,3.8,4,11.2)
# Two broad lower glazing bays flank the central brick pier; outer slots stay narrow.
for z in [7.2,25.2]:
 for x in [-15,15]:cut(x,-47,z,11.2,4,12.3)
 for x in [-36,36]:cut(x,-47,z,3.8,4,11.8)
for z in [7.1,25.1]:
 for x in [-15,15]:
  details.append(box(x,-45.7,z,1.2,2.8,12.6))
  details.append(box(x,-45.7,z+8.1,11.3,2.8,1.2))
# Distinct center pier + projecting side shoulders, not repeated generic square windows.
add(0,-47.1,2.8,5.0,1.6,38.5)
for x in [-29,29]:add(x,-47.1,2.8,3,1.6,39)
# Front one-way red-tile roof supported by triangular concrete cheeks.
roof=[(-53,111.1),(-27,120.9),(-27,123.7),(-53,113.9)]
parts.append(profile_y(roof,0,61))
for x in [-30,30]:parts.append(profile_y([(-51,111),(-26,111),(-26,125),(-51,116.0)],x,3.6))
# Eave roll and broad brackets are thickened and fused to roof / front wall.
parts.append(Manifold.cylinder(63.5,1.7,1.7,28).rotate((0,90,0)).translate((-31.75,-53,112.5)))
for x in [-26,-17.3,-8.7,0,8.7,17.3,26]:
 parts.append(profile_y([(-51,110.5),(-45,104),(-45,112),(-51,114)],x,2.2))
# Open-topped parapet, coarse round coping and principal three coping spans.
add(0,-16,123.5,86,18,2)
for y in [-24.3,-7.7]:
 add(0,y,125,86,1.8,2.7)
 for x in [-39,-13,13,39]:add(x,y,126,2.2,2.8,3.6)
 parts.append(Manifold.cylinder(83,1.25,1.25,24).rotate((0,90,0)).translate((-41.5,y,129)))
for x in [-42.1,42.1]:add(x,-16,125,1.8,18,4)
# The two low corner shoulder coping rolls are visibly lower.
for x in [-37,37]:
 add(x,-36,100.5,12,22,1.6)
 parts.append(Manifold.cylinder(12,1.2,1.2,24).rotate((0,90,0)).translate((x-6,-46,102.2)))
# Northwest-facing side of the high core: isolated upper slot and paired small windows.
cut(-43,-14,109,4,3.0,10)
for y in [-21,-11]:
 for z in [88,72]:cut(-43,y,z,4,3.3,8.7)
# Three photographed long-wing bay groups nearest the front blank transition.
# Each upper group has four narrow slots; lower rows use two broader panes.
for center in [14,28,42]:
 for yy in [center-4.5,center-1.5,center+1.5,center+4.5]:cut(-43,yy,70,4,1.6,12.8)
 for z in [11,30,49]:
  for yy in [center-3.3,center+3.3]:cut(-43,yy,z,4,5.0,12)
for yy in [6.8,21,35,49]:add(-43.5,yy,2.8,1.8,3.0,66)
# One lower attached bay and its two isolated openings before the tower corner.
add(-45,-14,2.8,5.6,18,56)
for z in [18,38]:cut(-48,-14,z,3,4.7,10)
# Low long-wing parapet and round rail, without unobserved roof equipment.
for x in [-42.1,42.1]:
 add(x,21.5,86.5,1.8,57,2.5)
 parts.append(Manifold.cylinder(55,1.55,1.55,24).rotate((90,0,0)).translate((x,49,90.5)))
for y in [-6,49]:add(0,y,86.5,86,1.8,2.6)
# Attached side stair is represented only at the local building edge, no full terrain.
for i in range(15):add(-51,-49+i*6.3,3,7.0,6.7,2+i*3.4)
# Plain cropped rear and unobserved connected side intentionally lack invented detail.
solid=parts[0]
for p in parts[1:]:
 assert p.status().name=='NoError',p.status()
 solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert solid.status().name=='NoError'
assert len(solid.decompose())==1,[(p.volume(),p.bounding_box()) for p in solid.decompose()]
m=solid.simplify(.00001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('dimensions_mm',mesh.extents,'watertight',mesh.is_watertight,'volume',mesh.volume)
