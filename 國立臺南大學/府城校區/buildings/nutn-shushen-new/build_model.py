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
# New Shushen dormitory, completed exterior in official sustainability photograph.
# Six storeys with visible individual window openings, left grey end wall and right glazed stair.
add(0,0,0,150,84,3)
add(0,5,2.8,128,47,111)
# Tall left end panel and sparse separate side/end apertures.
add(-59,3,3,13,50,114)
for z in [20,38,56,74,92]:cut(-59,-22,z,5.5,3,3.5)
# Photo-visible front: individual nearly-square windows, no inserted paired mullions.
# Top three rows are clear; lower rows only model visible left windows, trees obscure rest.
for z in [98,80,62]:
 for x in [-44,-31,-18,-5,8,21,34,47]:cut(x,-18.5,z,8.2,3.2,8.6)
for z in [44,26]:
 for x in [-44,-31,-18]:cut(x,-18.5,z,8.2,3.2,8.6)
for x in [-44,-31]:cut(x,-18.5,7,8.2,3.2,12)
# Broad white bands in the photo are shallow facade relief, not added free-standing columns.
for z in [94,58,40]:add(-1,-18.8,z,111,1.0,2.3)
for x in [-51,53]:add(x,-18.9,40,2.2,1.1,72)
# Color panels translated to shallow solid relief; top yellow, mid two-storey yellow, lower orange.
for x,z,h in [(-35,94,17),(23,94,17),(-10,59,35),(41,59,35),(-35,41,16)]:
 add(x,-19.1,z,6,1.6,h)
add(0,-19,111,113,1.4,2)
# Projecting glazed stair at the right corner, shallow-backed grid.
add(62,-15,3,12,16,112)
for z in [80,98]:cut(62,-23,z,8.6,3.6,13)
for x in [59,63,66]:add(x,-24,79,1.0,2.3,32)
# Roof parapet and recessed penthouse, with observed water-tank silhouettes.
add(0,5,114,131,50,2.5)
add(15,14,116,46,24,11)
for x,r,h in [(-5,4.7,8),(8,4.7,8),(21,4,6),(33,4.4,7),(45,3.8,6)]:
 column(x,-1,116,r,h)
 add(x,-1,116+h-1,2*r+1,2*r+1,1.1)
# Unseen rear and depth deliberately plain; tiny equipment/railings omitted.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
