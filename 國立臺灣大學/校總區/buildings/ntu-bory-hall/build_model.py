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
# E6 Bory Hall, seven floors; public 2010 NTU and builder exterior images.
add(0,0,0,150,86,3)
add(0,6,2.8,138,53,101)
add(0,6,103,142,57,1.7)
# Large two-storey opening with documented round freestanding exterior core.
cut(10,6,3,55,65,29)
details.append(Manifold.cylinder(30,9,9,circular_segments=64).translate((-3,-9,2.8)))
# Recessed glass field spans three middle floors, continuing to ground at left.
cut(0,-20.5,32,75,6,43)
cut(-28,-20.5,3,18.8,6,29.3)
for x in [-28,-14,0,14,28]:details.append(box(x,-18.6,32,.85,3.4,43))
for z in [33,47,61,74]:details.append(box(0,-18.6,z,75,3.4,1.6))
for z in [40,54,68]:details.append(box(0,-18.6,z,75,3.4,.8))
for x in [-34,-28,-22]:details.append(box(x,-18.6,3,.85,3.4,29))
for z in [10,20,30]:details.append(box(-28,-18.6,z,17,3.4,.8))
# Narrow coded-window rhythm rather than generic broad classroom windows.
for z in [6,20,34,48,62,76,90]:
 xs=list(range(-63,64,7))if z>=76 else [-63,-56,-49,-42,42,49,56,63]
 for x in xs:cut(x,-20.5,z,3.1,3.2,9.2)
# Repeated light horizontal stone bands, backed/fused on all outer walls.
for z in range(6,102,4):
 for x,w in [(-54,30),(54,30)]:add(x,-20.7,z,w,1,.75)
 if z>=76:add(0,-20.7,z,138,1,.75)
 for x in [-69,69]:add(x,6,z,1,54,.75)
# Visible short end has grouped slits separated by broad blank strips.
for z in [6,20,34,48,62,76,90]:
 for y in [-12,-6,0]:cut(-69,y,z,3,2.6,9.2)
# Reverse and opposite end unobserved details omitted rather than mirrored.
# Solid exterior entry stair. No interior or small undercroft fixtures reproduced.
for i in range(4):add(8,-36+i*2,3,94,2.4,.65*(i+1))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
