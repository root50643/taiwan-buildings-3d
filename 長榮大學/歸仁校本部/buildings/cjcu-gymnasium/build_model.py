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
# Gymnasium: circular entrance front and broad longitudinal barrel roof.
# Dimensions are exterior visual estimates; rear service elevation is deliberately plain.
add(0,0,0,132,150,3)
add(0,12,2.8,112,98,39.2)
# Three-level rounded entrance wall blends into low rectangular side shoulders.
parts.append(Manifold.cylinder(51,45,45,circular_segments=144).translate((0,-9,2.8)) ^ box(0,-40,2.6,100,37,52))
# Actual two-storey central entrance portico remains genuinely open.
cut(0,-52,3,44,29,28)
for x in [-12,12]:details.append(Manifold.cylinder(28.7,1.7,1.7,circular_segments=24).translate((x,-49,2.8)))
# Entrance glazing/doors sit on the rear plane of that recess.
for x in [-15,0,15]:cut(x,-37.5,4,10,2.8,12)
for x in [-15,0,15]:cut(x,-37.5,20,11,2.8,7)
# Narrow upper window rhythm follows the curved front, not a flat pasted facade.
for angle in [-51,-40,-29,-18,-7,7,18,29,40,51]:
 cuts.append(box(0,-45,35,3.4,3,10).rotate((0,0,angle)).translate((0,-9,0)))
# Lower flank openings and shoulder windows, directly seen in official photos.
for x in [-51,-43,43,51]:
 for z in [8,21]:cut(x,-37,z,3.6,3,6.7)
for x in [-35,35]:
 for z in [8,21]:cut(x,-38,z,3.2,6,6)
# Roof barrel spans the full arena width; continuous solid vault has no interior cavity.
r=108.; half=57.; roof_z=lambda x:42+math.sqrt(r*r-x*x)-math.sqrt(r*r-half*half)
poly=[(-half,41.6),(half,41.6)]+[(float(x),roof_z(float(x))) for x in np.linspace(half,-half,81)]
parts.append(profile(poly,13,100))
# 2020 roof renewal introduced visible light guides; only coarse geometric domes shown.
# Approximate positions are not a claim to a measured device inventory.
for x in [-40,-20,0,20,40]:
 for y in [-25,-10,5,20,35,50]:
  parts.append(Manifold.sphere(1.7,circular_segments=16).translate((x,y,roof_z(x)-.5)))
# Entrance steps and broad ground apron.
for i in range(4):details.append(box(0,-64+i*2.5,2.8,48,2.8,.7+.5*i))
# Unseen rear windows/rooftop service equipment intentionally omitted.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
