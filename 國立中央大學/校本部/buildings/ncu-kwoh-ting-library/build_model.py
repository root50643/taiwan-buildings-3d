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
# Tiered Ding-shaped frontage. Side/back depth approximate, rear deliberately plain.
add(0,0,0,150,105,3)
# Lower outer wings, higher twin piers and projecting cylindrical center.
add(0,13,2.8,117,57,110)
for x in [-34,34]:add(x,-7,2.8,25,49,125)
parts.append(Manifold.cylinder(143,27,27,circular_segments=96).translate((0,0,2.8)))
# Rounded center glazing bands: shallow backed circumferential recesses, front half only.
for z in [36,54,72,90,108,124,135]:
 ring=Manifold.cylinder(6.4,27.2,27.2,circular_segments=96)-Manifold.cylinder(7,24.5,25.4,circular_segments=96).translate((0,0,-.2))
 cuts.append(ring.translate((0,0,z))^box(0,-22,z-.1,60,42,7))
# Upper crown glazing has broad vertical mullions, backed into cylindrical envelope.
for a in range(210,331,20):
 t=math.radians(a)
 details.append(Manifold.cylinder(11,1.1,1.1,circular_segments=12).translate((26.4*math.cos(t),26.4*math.sin(t),131)))
# Paired frontal windows and narrower outer slots.
for x in [-34,34]:
 for z in [13,31,49,67,85,103]:cut(x,-31.2,z,11,3,9)
for x in [-51,51]:
 for z in [10,29,48,67,86]:cut(x,-15.5,z,4.4,3,10)
# Stepped cornices and corner rooftop pergolas from frontal image, robust printable section.
for x in [-34,34]:add(x,-7,127,28,51,2)
for x in [-51,51]:
 add(x,7,112,17,42,1.6)
 for y in [-10,22]:add(x,y,113.5,14,1.6,8)
 for xx in [x-6,x,x+6]:add(xx,6,121,1.5,34,1.7)
# Low curved entrance pavilion projects in front of the cylindrical tower.
porch=Manifold.cylinder(34,40,40,circular_segments=96).scale((1,.47,1)).translate((0,-21,2.8))
parts.append(porch)
cut(0,-39,3,36,8,17)
for x in [-28,28]:cut(x,-36,5,4,7,14)
# Robust cornice strips on front curved entry and upper core.
parts.append((Manifold.cylinder(1.8,41,41,circular_segments=96).scale((1,.47,1))).translate((0,-21,36)))
for x in [-18,18]:details.append(box(x,-36,27,1.8,3,7))
step(0,-47,72,4)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
