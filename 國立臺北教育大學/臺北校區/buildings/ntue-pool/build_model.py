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
# Swimming and fitness building: observed long facade and L-shaped entry wing.
add(0,0,0,150,101,3)
# Long pool hall and perpendicular entrance/services wing from official plan.
add(0,13,2.8,138,46,31)
add(-53,-6,2.8,32,36,24)
# Front long facade: ten deep screen bays, brick piers project beyond glazing.
for c in [-30,-20,-10,0,10,20,30,40,50,60]:
 cut(c,-10.0,7,7.6,5.5,23)
 # Broad lower glazing and horizontal sunscreens above; density simplified for print.
 details.append(box(c,-9.3,13,8.8,3.8,1.2))
 for z in [17,20,23,26,29]:details.append(box(c,-10.3,z,8.8,4.5,1.05))
for x in [-35,-25,-15,-5,5,15,25,35,45,55]:add(x,-10,3,2.2,5,31)
# Ten visible projecting brick piers; the far-right boundary is the broad brick end wall.
# Low continuous planter base, matching strong horizontal line below glazing.
add(16,-13,3,107,3,3.6)
# Right end is solid brick around two lower windows and narrow+broad upper windows.
for y,w in [(3,7),(15,7)]:cut(69,y,7,3.8,w,10)
cut(69,2,21,3.8,8,10)
cut(69,19,21,3.8,20,10)
# Entrance pavilion grey monumental frame: two side walls and broad top soffit.
# Lower entry glazing remains recessed 19 mm behind the open portal.
add(-53,-26,3,30,5,20)
for x in [-62,-53,-44]:cut(x,-28.5,4,7.4,3.5,16)
for x in [-69,-37]:add(x,-35,3,3.4,25,32)
add(-53,-35,33.5,35.4,27,3)
# Upper rear connector opening and low thick rails, retained as a genuine void.
add(-53,-23,22,31,3,2)
for x in [-65,-53,-41]:add(x,-23,23,1.3,3,9.8)
add(-53,-23,31.8,31,3,1.4)
# Entry steps, broad connected slabs.
for i in range(4):add(-53,-48+i*2.0,2.8,32,2.4,.65+i*.55)
# Flat roof and perimeter parapet from low oblique exterior; unseen equipment omitted.
add(0,13,33.1,139,47,1.5)
for y in [-10,36]:add(0,y,34.2,139,1.5,1.6)
for x in [-69,69]:add(x,13,34.2,1.5,47,1.6)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
