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
# Narrow teaching bar with monumental open entrance and a raised central roof bay.
add(0,0,0,93,150,3)
add(0,7,27,68,119,89)
# Keep a rear ground-level core; foreground colonnade remains genuinely open.
add(0,21,2.8,68,91,26)
add(0,-45,25,77,23,4)
add(0,-51,3,68,4,24)
for x in [-23,23]:arch_cut(x,-51,3,17,22,6)
cut(0,-51,3,17,6,21)
# Front face, four upper rows and a tall central glazed strip.
for z in [39,59,79,99]:
 cut(-25,-52.5,z+4,11,3.8,5)
 cut(25,-53.4,z-3,12,2.3,16)
 for x in [-10,10]:cut(x,-52.5,z-7,6,3.8,17)
for x in [-15,15]:add(x,-53,28,2,3.2,96)
add(0,-44,115,23,23,9)
cut(0,-55.5,116,12,3,6)
add(0,-44,123,28,27,2)
add(0,7,115,72,121,2)
# Side is visible obliquely but individual windows are poorly resolved: restrained rhythm.
for z in [40,60,80,100]:
 for y in [-29,-5,19,43]:cut(34,y,z,3.2,12,9)
step(0,-66,77,5)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
