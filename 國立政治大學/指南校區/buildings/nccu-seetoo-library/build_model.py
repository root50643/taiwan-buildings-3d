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

def prism(poly,z,h):return CrossSection([poly]).extrude(h).translate((0,0,z))
def rotated_box(x,y,z,w,d,h,deg):return box(0,0,0,w,d,h).rotate((0,0,deg)).translate((x,y,z))
# Full main building only; lakeside reading house and the joining bridge are separate.
# As-built external outline follows public floor plans, including the large diagonal corner.
add(0,0,0,150,132,3)
poly=[(-64,-50),(64,-50),(64,48),(-8,48),(-64,3)]
# Actual multi-height composition: lower glazed floor, deep doubled fins, thin glass band, upper fins.
parts.append(prism(poly,2.8,63))
# Remove broad perimeter recess bands to make genuine shadow galleries.
for z,h in [(4,6),(31,6)]:
 cut(0,-50,z,124,10,h)
 cut(64,0,z,9,91,h)
 cut(26,48,z,70,8,h)
# Large double-height concrete screen on the entrance/west elevation.
for z,h in [(11,19),(39,24)]:
 cut(5,-50,z,103,13,h)
 for x in [-45,-36,-27,-18,-9,0,9,18,27,36,45]:
  # Broad canted panels, fused to recessed backing. True recesses are preserved.
  panel=[(x,-51),(x+6.7,-47),(x+6.7,-41.2),(x,-45.2)]
  details.append(prism(panel,z,h))
# Glazed band mullions, attached through the back and floor strips.
for z,h in [(4,6),(31,6)]:
 for x in range(-59,63,6):details.append(box(x,-47,z,1.2,5,h))
# Main entrance portico projects to the right, with a truly open undercroft.
add(57,-53,24,24,20,8)
for x in [49,65]:add(x,-59,3,2.7,2.7,22)
# Sawtooth entrance screen returns above portico.
for x in [49,57,65]:cut(x,-63,26,5.3,3,4.5)
# Other elevations are wood-finned glazing in real photographs, not the solid front screen.
for z,h in [(11,19),(39,24)]:
 cut(64,-2,z,8,97,h)
 for y in range(-45,47,5):details.append(box(62.5,y,z,6,1.5,h))
 cut(27,48,z,69,8,h)
 for x in range(-5,62,5):details.append(box(x,46,z,1.5,6,h))
# Large diagonal lake-facing facade: deep recessed glazing and connected vertical fins.
a=np.array([-64.,3.]);b=np.array([-8.,48.]);v=b-a;length=float(np.linalg.norm(v));u=v/length;deg=math.degrees(math.atan2(v[1],v[0]))
for z,h in [(4,6),(11,19),(31,6),(39,24)]:
 c=(a+b)/2;cuts.append(rotated_box(c[0],c[1],z,length-6,7,h,deg))
 for t in np.arange(5,length-4,5):
  p=a+u*t;details.append(rotated_box(p[0],p[1],z,1.5,6,h,deg))
# Lake/side elevations show two visible courses per deep screen zone.
for z in [21,50.5]:
 details.append(box(63,-2,z,4,97,1.6))
 details.append(box(27,47,z,70,4,1.6))
 c=(a+b)/2;details.append(rotated_box(c[0],c[1],z,length-3,4,1.6,deg))
# Two terraced lower reading-room bays at the lake facade.
for x,y in [(-38,26),(-16,42)]:
 add(x,y,3,18,15,19)
 add(x,y,21.5,21,18,1.5)
 cut(x,y+7.5,7,14,3,12)
 for dx in [-4,4]:details.append(box(x+dx,y+7.3,7,1.1,2.5,12))
# Roof deck is covered, not an invented open court. Only coarse external monitors retained.
parts.append(prism(poly,65.3,1.5))
add(36,25,66.5,24,15,5)
for y in [-29,-19,-9,1,11,21]:
 parts.append(profile([(-20,66.4),(20,66.4),(20,68.2),(-20,67.1)],y,2.0))
# Bare service elevations and small unseen roof equipment are deliberately omitted.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
