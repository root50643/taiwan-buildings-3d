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
# Two-storey courtyard library. Court presence is documented; court dimensions estimated.
add(0,0,0,150,142,3)
add(0,0,2.8,124,116,38)
cut(0,0,3,55,47,45)
# External high colonnade: inset wall fields and tall robust piers, open beneath canopy.
for y in [-1,1]:
 cut(0,y*55,3,115,10,33)
 for x in range(-55,56,11):details.append(box(x,y*57,3,1.8,8,35))
for side in [-1,1]:
 cut(side*59,0,3,9,104,33)
 for y in range(-48,49,12):details.append(box(side*61,y,3,1.8,1.8,35))
# Backed fine screen surfaces are shallow recess arrays rather than submillimetre lattice.
for x in range(-52,53,11):
 for z in [7,15,23,31]:cut(x,-50.2, z,6.4,1.7,5.5)
# Roof parapet ring, open to sky, no concealed inner cavity.
parts.append(box(0,0,40,127,119,2)-box(0,0,39.9,55,47,2.3))
# Front clock on parapet; no tiny hands or lettering fabricated.
parts.append(Manifold.cylinder(1.1,2.1,2.1,circular_segments=48).rotate((90,0,0)).translate((0,-60,39.8)))
step(0,-66,75,4)
# Interior garden sculpture, pool and undocumented window layout omitted.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
