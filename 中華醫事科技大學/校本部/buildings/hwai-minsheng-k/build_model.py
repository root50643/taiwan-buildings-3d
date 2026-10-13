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
# K: modern ten-storey mass; flat parapets, alternating bands, paired circulation towers.
add(0,0,0,150,106,3)
add(0,11,2.8,98,60,110)
# Left tan shaft and broad pale right-front sign wall are visible, asymmetrical.
add(-52,8,2.8,18,65,120)
add(44,-11,2.8,21,24,116)
add(48,31,2.8,23,27,123)
# Lower two-storey arcade observed beneath foliage; depth explicitly estimated.
cut(-3,-18,3,77,15,16)
for x in [-37,-20,-3,14,31]:details.append(box(x,-23,3,3.2,4,17))
# Eight bands; alternate broad windows and narrow slit/light+AC rows, not identical bays.
for i,z in enumerate(range(24,108,10)):
 cut(-7,-19,z,65,3.4,5 if i in [0,7] else 2.5)
 for x in [-33,-20,-7,6,19]:details.append(box(x,-19,z,1.2,3.6,5 if i in [0,7] else 2.5))
 add(-7,-20,z+5.2,66,2.6,2.1)
# Narrow full-height recessed circulation seam alongside sign wall.
cut(29,-19,22,5,5,88)
for z in range(23,110,10):details.append(box(29,-18.5,z,5.2,4.2,1.2))
for z in range(29,116,17):cut(-53,-24.5,z,7,3.2,8)
for z in [89,105]:cut(43,-23,z,2.8,3,6)
# Right return: tall rectangular windows and three curved projecting balcony ends.
for z in range(25,113,10):
 for y in [3,17,31]:cut(59.5 if y==31 else 49,y,z,3.4,9,6)
for z in [71,84,97]:
 parts.append((Manifold.cylinder(2.0,9,9,circular_segments=48).translate((48,-8,z)))^box(52,-8,z,20,20,2))
 # Backed rounded parapet; solid balcony plate below, no standalone fine railings.
 arc=Manifold.cylinder(3.0,9,9,circular_segments=48).translate((48,-8,z+1.8))-Manifold.cylinder(3.4,7.4,7.4,circular_segments=48).translate((48,-8,z+1.6))
 parts.append(arc^box(52,-8,z+1.8,20,20,3))
add(-4,12,111,91,59,2)
# No aerial roof equipment or concealed rear fenestration is inferred.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
