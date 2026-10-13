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
# Eight-level P building, contractor two actual photographs and 2013 dated view.
add(0,0,0,150,100,3)
# Main classroom bar and rear part of the receding right-hand circulation wing.
add(-20,9,2.8,91,48,79)
add(37,24,2.8,30,18,79)
# Tall right brick stair tower, paired leaves with open stair landings between.
add(57,-2,2.8,9,13,87)
add(64,28,2.8,8,12,85)
for z in [14,26,38,50,62,74]:
 add(60,12,z,14,30,2.1)
 add(65,12,z+1.8,1.5,26,3)
# Actual large stepped double-height ground/first-floor voids, not dark applied windows.
cut(-1,-11,3,31,22,22)
cut(18,-11,3,19,24,34)
cut(-47,-11,3,31,21,10)
# Deep horizontal window pockets, six bays, upper five levels and staggered low rows.
for z in [27,39,51,63,75]:
 for x in [-56,-42,-28,-14,0,14]:
  if z==27 and x==14:continue
  cut(x,-15,z,10.8,7,7.2)
  details.append(box(x,-14.4,z+1,1.05,7.0,6.2))
for x in [-56,-42,-28]:cut(x,-15,15,10.8,7,7.2)

# Visible right recess has open projecting galleries with continuous low rails.
for z in [26,38,50,62,74]:
 add(37,5,z,28,22,2.0)
 add(36,-5.3,z+1.8,27,1.5,3.0)
 cut(37,15,z+4,22,3.6,6.1)
# Off-center monumental roof polygon and deep projecting soffit.
poly=[(-67,-19),(27,-19),(54,-3),(54,34),(-67,34)]
parts.append(CrossSection([poly]).extrude(2.8).translate((0,0,82)))
# Rear pixels are not available; subdued blank mass, no invented window repeat.
add(-48,26,84.5,15,8,6)
for z in [86,88]:cut(-48,21.8,z,11,1.8,1)
# Broad stepped route stays below open passage. Side stair as solid approximate terrain.
for i in range(7):add(8,-34+i*2.1,2.8,44,2.5,(i+1)*1.2)
# Inner stair visible beyond lower void: small flight with 1mm treads.
for i in range(8):add(16,-3+i*1.6,3,14,2,1.5*(i+1))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
