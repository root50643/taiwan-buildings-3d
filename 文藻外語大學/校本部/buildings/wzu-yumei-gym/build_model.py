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
# Elliptical gymnasium with genuine open rooftop tennis court, not a solid rooftop block.
add(0,0,0,150,110,3)
def ell(rx,ry,z,h):return Manifold.cylinder(h,1,1,circular_segments=144).scale((rx,ry,1)).translate((0,0,z))
parts.append(ell(65,39,2.8,66))
# Curving belt windows, structural bands and varying long brick piers.
for z,h in [(9,7),(28,10),(48,10)]:
 band=ell(66,40,z,h)-ell(63.2,37.2,z-.1,h+.2)
 # Photo shows a broad brick interruption at the left round end and rear services.
 cuts.append(band ^ box(15,0,z-1,102,100,h+2))
for z in [19,40,63]:details.append(ell(65.8,39.8,z,1.7)-ell(63,37,z-.1,1.9))
# Thickened backed mullions follow the observed curved glazing.
for a in list(range(240,360,12))+list(range(0,121,12)):
 t=math.radians(a)
 for z,h in [(9,7),(28,10),(48,10)]:
  details.append(Manifold.cylinder(h,1.1,1.1,circular_segments=12).translate((64*math.cos(t),38*math.sin(t),z)))
# Roof court floor remains exposed, with engraved boundary and service boxes.
for x in [-34,29]:cut(x,0,68.3,.7,48,.7)
for y in [-24,24,-16,16]:cut(-2.5,y,68.3,63,.7,.7)
cut(-2.5,0,68.3,63,.7,.7)
cut(-2.5,0,68.3,.7,32,.7)
# Open safety screen and heavy elliptical upper ring, 1.6mm piers anchored at both ends.
rim=ell(65,39,80,2)-ell(61.8,35.8,79.9,2.2);details.append(rim)
for a in range(0,360,12):
 t=math.radians(a);column(63.3*math.cos(t),37.3*math.sin(t),68.5,.85,12.2)
# Tall solid equipment/service wall at far narrow end, shown in official aerial.
add(53,0,68.5,17,46,24)
add(53,0,92,19,48,1.7)
for z in [74,86]:add(44.3,0,z,1.2,46,1.2)
# Low equipment pair at opposite end, simplified rather than hidden mechanical detail.
add(-45,0,68.5,19,26,7)
for y in [-7,7]:column(-45,y,75.3,4.4,1.2)
# Main lower entrance and attached stairs below the curved face.
cut(0,-39,3,17,5,11)
details.append(box(0,-38,14,25,12,1.6))
for i in range(5):add(0,-49+i*1.8,2.8,27,2.1,.8+i*.8)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
