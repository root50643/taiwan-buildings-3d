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
# Administration main block only: adjacent Science and Social Science wings excluded.
# Main footprint proportions checked against official 1F/7F/RF diagrams.
add(0,0,0,150,132,3)
# Ground body behind the tall four-column loggia, not flush-filled frontage.
add(0,9,2.8,118,87,61.4)
# Side stair bulges are evident in official ground/upper plans.
for s in [-1,1]:
 parts.append(Manifold.cylinder(58,7,7,circular_segments=48).translate((s*57,6,3)))
# Actual sheltered portico is 9 mm deep at miniature scale.
for x in [-54,-18,18,54]:column(x,-44,3,2.05,61)
for x in [-42,-30,-6,6,30,42]:add(x,-41,29,1.35,2.7,34)
for z in [27,39,51,62]:add(0,-41,z,113,9,2.2)
# Backing window recesses distinguish ground doorway and upper glazing.
cut(0,-34.6,3,30,3,21)
for x in [-44,-26,26,44]:
 for z in [7,18,30,42,54]:cut(x,-34.5,z,13,2.4,7.3)
for x in [-10,10]:
 for z in [30,42,54]:cut(x,-34.5,z,14,2.4,7.3)
# Semicircular balcony on central bay, with genuinely recessed top and thick rim.
poly=[(18*math.cos(t),-38-14*math.sin(t)) for t in np.linspace(math.pi,0,49)]
parts.append(xy_poly(poly,29,2.4))
outer=xy_poly(poly,31,4.4)
inner=[(16.4*math.cos(t),-37.5-12.4*math.sin(t)) for t in np.linspace(math.pi,0,49)]
parts.append(outer-xy_poly(inner,30.9,5))
# Oversailing upper brick box; continuous projecting soffit.
add(0,4,63,134,110,2.6)
add(0,4,65.4,130,107,23)
# Upper glazed band and brick piers, observed on frontal and corner photographs.
for x in range(-58,59,12):
 cut(x,-49.7,67,10.5,3.0,7)
 details.append(box(x,-50,67,1.0,2.0,7))
# Prominent central shallow arch below name parapet; small end slots.
cuts.append(low_arch(0,-50,78,34,6.7,7))
for x in [-60,60]:cuts.append(low_arch(x,-50,78,6.5,3.8,3.2))
# Side upper glazing with matching horizontal band; rear apertures are simplified.
for side in [-1,1]:
 for y in [-36,-20,-4,12,28,44]:cut(side*65,y,67,3,12,7)
for z in [10,23,36,49]:
 for x in [-48,-30,-12,12,30,48]:cut(x,52.5,z,12,2.7,7)
for x in range(-54,55,18):cut(x,57.5,68,14,2.8,7)
# The 1F and 2F rear-center void is exterior and cannot be filled by a plain box.
cut(0,49,3,40,38,24)
# The next level retains a shallower notch before upper floors span across it.
cut(0,53,27,40,24,12)
# Open roof lightwell indicated from 3F through RF; internal rooms not reconstructed.
cut(0,3,29,29,23,70)
# Shallow parapets and two stair heads from roof plan, heights approximate.
for x in [-64,64]:add(x,4,88,1.5,107,2.4)
for y in [-49,57]:add(0,y,88,130,1.5,2.4)
for x in [-36,36]:add(x,5,88,13,18,5)
# Three broad entrance steps under portico.
for i in range(4):add(0,-57+i*2,2.8,78,2.6,.6+i*.8)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
