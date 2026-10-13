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
# Administrative complex: administrative tower plus Library/ Education wings.
# x is lateral; negative y faces the circular entrance forecourt. Units millimetres.
# Official 1F/RF plans and recruitment drone photo constrain the U-shaped ensemble.
add(0,0,0,150,128,3)
# 10-storey main tower, footprint ratio 41.3m x 21.8m from official roof plan.
add(0,29,2.8,54,28.5,53.6)
# Deep 3-bay facade. Substantial white piers remain between the glazing groups.
for x,w,n in [(-20.6,9.2,4),(0,17,7),(20.6,9.2,4)]:
 # Entire recessed bay is 1.45 mm behind the broad structural piers.
 cut(x,14.35,3,w,2.6,50.3)
 # Backed windows: mullions are >= 1.0 mm rather than separate thin fragments.
 for z in [4.1,9.7,15.3,20.9,26.5,32.1,37.7,43.3,48.9]:
  if x==0 and z<15:continue
  for xx in [x+(i-(n-1)/2)*2.27 for i in range(n)]:cut(xx,15.8,z,1.25,3.0,4.3)
# Main tower central through passage from the official 1F plan; not blind filled.
cut(0,29,3,16.8,34,10.3)
# Upper crown overhang contains the three wide horizontal glazed bands.
add(0,28.8,55.9,56.2,30,7.6)
for x,w,n in [(-20.6,9.2,4),(0,17,7),(20.6,9.2,4)]:
 cut(x,13.9,57.4,w,2.5,3.1)
 for i in range(1,n):details.append(box(x-w/2+i*w/n,13.95,57.4,1.0,1.5,3.1))
# The photographed roof has an open parapet and two stair/elevator heads.
for x in [-27.5,27.5]:add(x,28.8,63.3,1.25,30,1.6)
for y in [14.45,43.15]:add(0,y,63.3,56.2,1.25,1.6)
for x in [-12,12]:add(x,29,63.2,7.5,17.5,3.8)
# Rear windows simplified from plan's opening rhythm; no photographed rear claim.
for z in [4.1,9.7,15.3,20.9,26.5,32.1,37.7,43.3,48.9]:
 for x in [-23,-19,-15,-11,11,15,19,23]:cut(x,43.2,z,2.7,2.8,3.6)
 if z>=15:
  for x in [-6,-2,2,6]:cut(x,43.2,z,2.7,2.8,3.6)
for x in [-19,0,19]:cut(x,43.7,57.4,10,2.8,3.1)
# Five-storey parallel side wings: long axis and asymmetric stair/toilet bulges from plans.
for s in [-1,1]:
 x=s*61
 add(x,0,2.8,15.3,108,27.7)
 # Long wing inward service bays are physically attached, not detached boxes.
 for y in [-37,-17,25,43]:add(x-s*8.4,y,2.8,4.3,6.7,27.7)
 # Windows below crown are vertical groups, observed on the forecourt elevations.
 for z in [4.2,10.0,15.8,21.6]:
  for y in [-48,-43,-28,-23,-13,-8,-3,2,7,12,17,32,37,47]:
   cut(x-s*7.8,y,z,2.6,3.2,4.25)
 # Outer facades inherit window cadence from floorplans and are identified as approximate.
 for z in [4.2,10.0,15.8,21.6]:
  for y in range(-48,50,5):cut(x+s*7.8,y,z,2.6,3.2,4.25)
 # 5F slightly projecting capped end and horizontal window bands.
 add(x,0,29.9,17.1,108.8,6.1)
 for y in [-43,-23,-3,17,40]:
  cut(x-s*8.5,y,31.2,2.8,15,2.8)
  cut(x+s*8.5,y,31.2,2.8,15,2.8)
 # Short end glazing below clean top parapet.
 for y in [-54,54]:
  for z in [4.2,10.0,15.8,21.6]:cut(x,y,z,9.8,2.6,4.25)
  cut(x,y,31.2,11,2.6,2.8)
 # Lower wing passageways indicated in 1F plans remain open end-to-end across width.
 cut(x,-36.5,3,24,9.5,7.8)
 # Open roof parapet and large contemporary solar panel tables on low solid backing.
 for xx in [x-7.9,x+7.9]:add(xx,0,35.8,1.25,108.8,1.5)
 for yy in [-53.8,53.8]:add(x,yy,35.8,17.1,1.25,1.5)
 for y,d in [(-25,53),(43,17)]:
  add(x,y,36,12.2,d,1.2)
  for yy in range(int(y-d/2+3),int(y+d/2),5):cut(x,yy,37.0,11.6,.65,.25)
 add(x,20,35.8,7.2,8.2,3.2)
 # Three-storey enclosed connecting bridges seen in drone and original completion photo.
 add(s*40.5,29,2.8,29,7,18.4)
 for z in [4.2,10.0,15.8]:
  for xx in [s*k for k in [29,34,39,44,49]]:cut(xx,25.3,z,3.2,2.6,4.25)
 # Walkway at ground remains sheltered through open bays below bridge floor.
 for xx in [s*k for k in [33,40,47]]:cut(xx,29,3,5.2,10,4.8)
# Entrance stair is physically joined to base. Landscape and freestanding flags omitted.
for i in range(3):add(0,11-i*1.6,2.8,20,1.9,.6*(3-i))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
