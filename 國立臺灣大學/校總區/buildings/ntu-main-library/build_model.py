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
# Central library front with its asymmetrical left bell tower.
add(0,0,0,150,92,3)
add(6,8,2.8,112, 60,43)
# Stepped front volumes observed in the official photograph.
add(6,-25,2.8,34,13,49)
gable(6,-25,51,34,13,6)
for x in [-26,38]:
 add(x,-23,2.8,15,12,47)
 add(x,-23,49,16,13,1.2)
 arch_cut(x,-29,19,6.6,19,1.3);arch_trim(x,-29,19,6.6,19)
 cut(x,-29,40,5,1.4,6)
 for xx in [x-3.8,x+3.8]:add(xx,-29.3,39,1.2,1.5,9)
# Large central projecting gabled frontispiece and great arched window.
add(6,-32,18,27,3,24);gable(6,-32,41.5,27,3,4.5)
arch_cut(6,-33.5,19,12,21,1.8);arch_trim(6,-33.5,19,12,21)
for x in [2,6,10]:details.append(box(x,-33.1,19,1,1,15))
for z in [24,29,34]:details.append(box(6,-33.1,z,11.5,1,1))
# Front entrance arcade is closed-backed shallow relief for printing.
add(6,-34,2.8,38,8,13.5)
for x in [-8,6,20]:arch_cut(x,-38,3,7,11.5,4.5);arch_trim(x,-38,3,7,11.5)
for x in [-20,32]:arch_cut(x,-30,3,5,9,2)
for x in [-43,-36,48,56]:
 for z in [9,20,31]:cut(x,-22,z,3.6,1.6,5)
# Left campanile: public exterior openings, thickened pillars and modest hip cap.
add(-60,3,2.8,13,18,58)
add(-48,8,2.8,15,26,16)
for z in [9,22,36]:arch_cut(-60,-6,z,5,10,1.5)
cut(-60,3,49,8.2,20,7.5)
cut(-60,3,49,15,12.5,7.5)
add(-60,3,57.5,14,19,3);hip(-60,3,60,14,19,3)
for z in [16,33,46]:add(-60,3,z,13.8,18.8,1.2)
# Broad entrance steps; rear intentionally unornamented due limited evidence.
step(6,-43,49)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
