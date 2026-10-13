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
# SC Meiho building: tall thin main block lifted above a two-level open base.
add(0,0,0,150,100,3)
# Source shows the narrow end and a much longer side; axis x is long side.
add(0,11,24,132,52,64)
# Rear circulation spine grounds the volume; front two levels remain visibly open.
add(0,31,2.8,132,12,22)
for x in [-61,-20,20,61]:add(x,-13,3,3.8,4.8,22)
for x in [-61,61]:add(x,13,3,3.8,4.8,22)
add(0,6,13,132,61,2.4)
# The open base side is cut away rather than painted as glazing.
# Five main classroom rows and asymmetric long window strips.
for z in [29,41,53,65,77]:
 for x in range(-55,57,17):cut(x,-15,z,11,3.5,5)
 for y in [-4,12,27]:cut(66,y,z,3.5,8,5)
# Long side has continuous sunshade ledges and paired window modules.
for z in [38,50,62,74,86]:add(0,-15.5,z,133,3.2,1.4)
# Oversailing roof and small narrow parapet vents seen in upper photograph edge.
add(0,11,87.5,139,59,2.3)
for x in range(-64,66,8):add(x,-18,89.5,1.4,1.5,2.8)
add(0,11,92,139,59,1.5)
step(22,-28,38,3)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
