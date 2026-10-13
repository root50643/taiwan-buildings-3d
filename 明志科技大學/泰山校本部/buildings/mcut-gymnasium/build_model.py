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
# Actual exterior photographs: TASA and MCUT. Flat front roof line, curved depthwise barrel.
add(0,0,0,150,145,3)
# Tall principal volume with true open ground-level front porch.
add(-10,8,2.8,106,107,87)
cut(-10,-40,3,96,25,15)
for x in [-55,-12,35]:details.append(Manifold.cylinder(17,2,2,circular_segments=24).translate((x,-49,2.8)))
# Three lower glazed bands and two deep upper gallery recesses.
for z,h in [(20,14),(38,13),(56,12)]:
 cut(-10,-45.5,z,101,3.0,h)
 for x in range(-56,38,8):details.append(box(x,-45.8,z,1.1,3.4,h))
 for zz in [z+5,z+10]:details.append(box(-10,-45.8,zz,101,3.4,1.0))
for z in [35,53]:add(-10,-48.5,z,106,7,1.6)
# Upper volume first; two genuinely deep open balconies with glass at back.
add(-10,7,88,106,105,17)
cut(-10,-44,71,102,17,35)
# Backed upper glazing lies at recess back y=-35.5, never at railing plane.
for z,h in [(73,10),(88,16)]:
 cut(-10,-35.5,z,100,2.4,h)
 for x in range(-56,38,8):details.append(box(x,-35.5,z,1.0,2.6,h))
 details.append(box(-10,-35.5,z+h/2,100,2.6,1.0))
for z in [71,85]:
 details.append(box(-10,-43,z,108,18,1.8))
 details.append(box(-10,-51.2,z+1.5,108,1.2,2.4))
# Round front structural columns join balcony and roof, restored after recess cuts.
for x in [-60,-12,39]:
 details.append(Manifold.cylinder(35,1.9,1.9,circular_segments=24).translate((x,-49,71)))
# Depthwise curved upper hall and roof: cross-section in YZ rotated to extrude X.
yvals=list(np.linspace(-53,64,49));top=[106+7*(1-((y+2)/64)**2) for y in yvals]
poly=[(-53,103),(64,103)]+[(float(y),float(z)) for y,z in zip(yvals[::-1],top[::-1])]
parts.append(CrossSection([poly]).extrude(110).rotate((90,0,90)).translate((-65,0,0)))
roof=[(float(y),float(z)) for y,z in zip(yvals,[t-.2 for t in top])]+[(float(y),float(z+2)) for y,z in zip(yvals[::-1],top[::-1])]
parts.append(CrossSection([roof]).extrude(118).rotate((90,0,90)).translate((-69,0,0)))
# Left solid side screen with tall recessed glazed opening, visible in contractor photo.
add(-62.5,6,3,3,105,85)
cut(-64,11,18,3.5,45,42)
for y in [-8,1,10,19,28]:details.append(box(-64, y,18,3.7,1.1,42))
for z in [27,38,49]:details.append(box(-64,11,z,3.7,45,1.1))
# Tall asymmetric stair/logo tower at right; sign is blank raised plaque, no logo copying.
add(53,-4,2.8,24,102,115)
add(53,-56,88,19,3,24)
# Rear recess strip inferred from the visible narrow side; unseen rear remains plain.
add(66,20,3,6,48,103)
for z in [14,32,50,68,86]:cut(69,20,z,3,38,10)
# Entry platform and steps limited to the building footprint, not neighboring plaza.
for i in range(4):add(-10,-65+i*3,2.8,105,3.3,1+i*.8)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
