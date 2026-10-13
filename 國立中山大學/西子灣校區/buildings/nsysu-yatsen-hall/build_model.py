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

def low_arch(x,y,z,w,h,depth):
 pts=[(x-w/2,z),(x+w/2,z),(x+w/2,z+h*.45)]
 pts += [(x+w/2*math.cos(t),z+h*.45+h*.55*math.sin(t)) for t in np.linspace(0,math.pi,33)[1:]]
 return profile(pts,y,depth)
def xy_poly(points,z,h):return CrossSection([points]).extrude(h).translate((0,0,z))
# Yat-sen Hall: theatre block and deep entrance colonnade, no auditorium interior.
# Official 1F/RF safety plans constrain the nearly-square footprint.
add(0,0,0,150,145,3)
# Lower foyer body behind free-standing portico.
add(0,5,2.8,132,112,35.5)
# White colonnade has a central projecting tetrastyle entrance and side returns.
for x in [-62,-45,45,62]:column(x,-55,3,1.75,35)
for x in [-33,-11,11,33]:column(x,-64,3,2.1,35)
# Recess broad lower doorway bays; no generic flush window box.
for x in [-58,-43,-24,0,24,43,58]:
 cut(x,-51,5,12,4.5,13)
 cut(x,-51,23,12,4.5,10)
for z in [20,35.5]:add(0,-54,z,132,8,2.4)
add(0,-58,35.4,71,18,2.8)
# Cof­fer beams under the projecting canopy are fused to its soffit.
for x in [-30,-20,-10,0,10,20,30]:add(x,-58,33.8,1.6,18,1.8)
# Solid brick balcony parapet wraps canopy and keeps rooftop deck open.
add(0,-66,38,71,1.6,6.5)
for x in [-34.7,34.7]:add(x,-58,38,1.6,17,6.5)
# Upper broad brick front screen with the large curved recess seen in all 3 photos.
add(0,4,37.8,132,108,35)
cuts.append(low_arch(0,-50,46,71,16,17))
# Recess is real: framing behind at y=-42 rather than filling to front plane.
for x in [-24,0,24]:details.append(box(x,-42,46,1.8,4.5,11.5))
# Side lower gallery relief, checked against footprint but fine door rhythm approximate.
for side in [-1,1]:
 for y in [-32,-9,14,37]:
  cut(side*66,y,6,3.7,17,12)
  cut(side*66,y,23,3.7,17,9)
  add(side*66.5,y-10.5,3,1.8,2.0,35)
# Stepped roof stage volume supported by main theatre block; roof back is simplified.
add(0,15,72.5,74,75,4.5)
add(0,15,77,77,78,1.5)
for x in [-65,65]:add(x,4,72.5,1.8,108,2)
# Rear service entrance and the two shallow corner risers shown in floor plan.
for x in [-55,55]:add(x,59,3,16,10,33)
for x in [-48,-24,0,24,48]:cut(x,61,7,10,2.7,13)
# Entrance staircase, rising into the portico but preserving column bases.
for i in range(6):add(0,-70+i*1.5,2.8,80,1.9,.4+i*.65)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
