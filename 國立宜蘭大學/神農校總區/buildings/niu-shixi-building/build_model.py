"""NIU 時習大樓: original exterior miniature from official multi-view photographs
and official five-storey evacuation plans. Millimetres; approximate proportions.
The U court, rounded projecting galleries, porch and stair-end masses are retained.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];late=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def rounded_landing(z,h,r=9.5):
 # D-shaped balcony, with its straight edge penetrating the central bar.
 pts=[(-r,-5),(r,-5),(r,7)]+[(r*math.cos(t),7+r*math.sin(t)) for t in np.linspace(0,math.pi,41)[1:]]
 return CrossSection([pts]).extrude(h).translate((0,0,z))
add(0,0,0,150,111,3)
# A broad front bar with two rear wings and a deep, genuinely open U-shaped court.
add(0,-20,2.8,136,41,57.2)
for x in [-45,45]:add(x,22,2.8,29,43,57.2)
# End stair boxes seen in the official floor plans, enlarged to printable thickness.
for x in [-27.5,27.5]:
 add(x,41,2.8,10,13,59.2)
 add(x,41,60.8,11.5,14.5,1.6)
 # Two vertically separated slit groups on the exposed end of each stair block.
 for z in [9,20,31,42,53]:cut(x,47.8,z,2.3,2.3,6)
# Front entrance steps and two-bay portico; ground portal is real open relief.
cut(0,-37,5.0,23.0,9.5,9.2)
add(0,-43,15.2,28,11.5,3.0)
for x in [-12,0,12]:add(x,-46.5,5.0,2.5,2.5,10.6)
for k in range(5):add(0,-51+k*1.35,2.9,30,1.6,.65*(k+1))
# Original broad rectangular front windows, with prominent full-height piers.
for floor in range(5):
 z=6+10.8*floor
 for x in [-60,-47,-34,-21,-8,8,21,34,47,60]:
  if floor==0 and abs(x)<14:continue
  cut(x,-40.1,z,10.1,3.4,6.4)
  late.append(box(x,-39.3,z+4.8,10.2,1.8,1.0))
for x in [-67,-53.5,-40.5,-27.5,-14.5,14.5,27.5,40.5,53.5,67]:add(x,-40.3,3,1.7,1.6,57.3)
# Upper and lower floor bands remain stout and connected.
for z in [14.8,25.6,36.4,47.2,58]:add(0,-20,z,137,42,1.4)
# Side-end square windows and horizontal slits, following the different elevations.
for x in [-68,68]:
 for floor in range(5):
  z=6+10.8*floor
  for y in [-32,-18,-4]:cut(x,y,z,2.8,9.4,6.2)
for x in [-59.5,59.5]:
 for floor in range(5):
  z=6+10.8*floor
  for y in [10,26,37]:cut(x,y,z,2.6,10.8,4.5)
# U court galleries: deep openings framed by floor slabs and parapets, not a filled box.
for x in [-30.5,30.5]:
 for floor in range(5):
  z=6+10.8*floor
  for y in [8,21,34]:cut(x,y,z+1.3,5.2,10.0,6.3)
for x in [-45,45]:
 for floor in range(5):
  z=6+10.8*floor
  for xx in ([x] if x>0 else [x-6,x+6]):cut(xx,43.7,z,8.5 if x>0 else 7.3,2.7,3.0)
# Central rounded balconies project into court; one joined D-shape per level.
for floor in range(1,5):
 z=3+10.8*floor
 slab=rounded_landing(z,1.7)
 outer=rounded_landing(z+1.6,2.5)
 inner=rounded_landing(z+1.5,2.8,r=7.8)
 # Open toward the building face, each solid 1.7mm side is attached to the slab.
 late.extend([slab,outer-inner])
# Curved fifth-floor canopy and paired full-height piers, visible in the old full photograph.
parts.append(rounded_landing(58.8,1.9,r=10.2))
for x in [-9.6,9.6]:add(x,7.7,3,2.3,3.2,57.3)
for x in [-24.5,-16.5,16.5,24.5]:add(x,0.5,3,1.7,2.5,57.5)
# Court-facing wall slits and the narrow grouped windows alongside the balcony.
for floor in range(5):
 z=6+10.8*floor
 for x in [-22,-13,13,22]:cut(x,.0,z,2.6,3.0,6.0)
 cut(0,0,z,13,3.0,5.4)
# Roof retains the twin stair upstands and taller centre service core.
add(0,-9,59.7,19,18,5.3)
for x in [-67,67]:add(x,-20,59.7,1.7,41,2)
add(0,-40,59.7,136,1.7,2)
for x in [-45,45]:
 for xx in [x-14,x+14]:add(xx,22,59.7,1.7,43,2)
 add(x,43,59.7,29,1.7,2)
# Ground court platform and broad side steps mirror the concave circulation space.
add(0,3,2.9,58,9,1.5)
for x in [-23,23]:
 for k in range(5):add(x,12+k*1.5,2.9,7.5,1.7,1.5-.22*k)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in late:solid=solid+p
print('components',[(p.volume(),p.bounding_box()) for p in solid.decompose()]);assert len(solid.decompose())==1
m=solid.simplify(1e-5).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj');print('dimensions_mm',mesh.extents,'watertight',mesh.is_watertight,'faces',len(mesh.faces))
