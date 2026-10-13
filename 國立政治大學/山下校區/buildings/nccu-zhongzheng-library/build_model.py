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

def arc_poly(ro,ri,a0=0,a1=180,n=80,cx=0,cy=-28):
 aa=np.radians(np.linspace(a0,a1,n+1));return [(cx+ro*math.cos(t),cy+ro*math.sin(t)) for t in aa]+[(cx+ri*math.cos(t),cy+ri*math.sin(t)) for t in aa[::-1]]
# Wan-shou / four-projecting-corner footprint, not a rectangle. Open central lightwell retained.
add(0,0,0,106,150,3)
poly=[(-44,-67),(-25,-67),(-15,-54),(15,-54),(25,-67),(44,-67),(44,-42),(34,-28),(34,28),(44,42),(44,67),(25,67),(15,54),(-15,54),(-25,67),(-44,67),(-44,42),(-34,28),(-34,-28),(-44,-42)]
parts.append(prism(poly,2.8,48))
cut(0,0,3,27,40,55)
# Lower, darker facades have three main window bands; top is a tall white finned crown.
for z in [8,20,32]:
 for side in [-1,1]:
  for y in [-21,-7,7,21]:cut(side*34,y,z,4,11,5)
  cut(0,side*54,z,28,4,5)
# Upper vertical fin crown follows every exposed perimeter segment.
for a,b in zip(poly,poly[1:]+poly[:1]):
 a=np.array(a,dtype=float);b=np.array(b,dtype=float);v=b-a;L=float(np.linalg.norm(v));deg=math.degrees(math.atan2(v[1],v[0]));u=v/L
 for t in np.arange(3,L-1,4.6):
  p=a+u*t;cuts.append(rotated_box(p[0],p[1],40,2.8,4.2,8.7,deg))
# Gridded corner stair screens are backed recesses, not disconnected lattice fragments.
for side in [-1,1]:
 for end in [-1,1]:
  for y0 in [46,52,58,64]:
   for z in [7,13,19,25,31]:cut(side*44,end*y0,z,2.6,4.4,4)
# Four sloped shoulder piers and layered upper roof lip remain integral.
parts.append(prism(poly,50.4,1.6))
cut(0,0,50,27,40,6)
for side in [-1,1]:add(side*13.8,0,51.4,1.3,41.5,1.6)
for y in [-20.3,20.3]:add(0,y,51.4,28.7,1.3,1.6)
# Wide principal entrance steps in the recessed south bay.
for i in range(6):add(-47+i*2,0,2.8,2.4,55,.75*(i+1))
cut(-34,0,3,6,50,10)
for y in [-20,-10,0,10,20]:details.append(box(-34,y,2.8,4,1.5,10.4))
# Rooftop service boxes and the open lightwell are confirmed in the official aerial image.
for x in [-25,25]:
 for y in [-48,48]:add(x,y,51.6,14,15,6)
for side in [-1,1]:
 for y in [-14,0,14]:cut(side*13.5,y,42,3,9,6)
# Back is outline-based with fewer unverified window details; small rooftop service blocks omitted.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
solid=solid.rotate((0,0,90))
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
