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
# S45: 1975 B hall only. Adjacent historic A / Meteorology hall excluded.
add(0,0,0,150,105,3)
add(0,11,2.8,131,68,83)
add(0,11,85,133,70,1.2)
# Five tall, round-headed vertical window stacks, grouped 3+2 on the main facade.
for x in [-38,-25,-12,25,38]:
 arch_cut(x,-23,8,7.5,67,3)
 outer=arch(x,-23.4,7,9.2,69,2.8);inner=arch(x,-24,7.8,7.5,67.3,4)
 details.append(outer-inner)
 for z in [19,31,43,55,67]:details.append(box(x,-22.7,z,8,2,2))
 # Ground stack grille, solid-backed and visibly thickened.
 for xx in [x-2,x,x+2]:details.append(box(xx,-22.5,8,.8,2,15))
# The photographed right side contains another vertical group; count/depth approximate.
for y in [-7,10,27]:
 a=arch(0,0,8,7.5,67,3).rotate((0,0,90)).translate((65.5,y,0));cuts.append(a)
 for z in [19,31,43,55,67]:details.append(box(65,y,z,2.5,8,2))
# Tall portal in the left half, front and both side arches open to the exterior.
add(-25,-34,3,56,35,34)
cuts.append(arch(-25,-35,3.05,44,29,38))
# Side openings meet the front portal void, never become concealed hollow shells.
for x in [-53,3]:cuts.append(arch(0,0,3.05,23,29,4).rotate((0,0,90)).translate((x,-34,0)))
# Portal roof and piers remain substantial, but need support below the arches.
step(-25,-47,48,4)
# A hall and connecting low wing are omitted, not merged into a fictitious B-hall facade.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
