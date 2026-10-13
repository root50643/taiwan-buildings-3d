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
# MCUT library FRONT SEGMENT: two actual photographs establish central porch,
# tall asymmetric service towers, stacked curved balconies and five broad bands.
add(0,0,0,150,68,3)
add(0,9,2.8,135,35,122)
# Broad deep entry portal, left rear service tower and broad slit-window front screen.
cut(0,-8,3,90,22,27)
maincut=cuts.pop();parts[-1]=parts[-1]-maincut
add(-56,9,2.8,22,35,133)
add(-52,-10,2.8,24,8,124)
for z in [13,39,65,91,117]:cut(-52,-14,z,16,3,2.5)
# Right projecting vertical sign tower, deliberately no copied lettering.
add(56,-3,2.8,24,46,145)
for z in [26,44,62,80,98,116,134]:cut(56,-26,z,15,3,3.8)
cut(56,-26,138,13,3,7)
# Five broad framed glazed strips above two-level recessed entrance.
for z in [33,49,65,81,97]:
 cut(-3,-9,z,70,4,10)
 for x in range(-35,32,7):details.append(box(x,-9,z,1.0,4.2,10))
 details.append(box(-3,-9,z+6,70,4.2,1.0))
 add(-3,-10,z-2,71,3,2)
# Top individual square windows, each with a projecting boxed surround.
for x in [-27,-5,17]:
 add(x,-9,113,11,3,9)
 cut(x,-11,114.4,8,3.4,6.2)
# Curved projecting balconies in the narrow recess beside the sign tower.
for z in [49,65,81,97]:
 cut(38,-9,z-2,12,4,13)
 # Solid lower semicircular balcony parapet backed by facade; open center recess.
 disk=Manifold.cylinder(3.2,6.0,6.0,circular_segments=48).translate((38,-11,z))
 disk=disk ^ box(38,-16,z-.1,14,12,3.4)
 details.append(disk)
 # Rounded sturdy rim, tied into facade at both ends, rather than fragile rail wires.
 outer=Manifold.cylinder(4.8,6.0,6.0,circular_segments=48).translate((38,-11,z+1))
 inner=Manifold.cylinder(5.2,4.7,4.7,circular_segments=48).translate((38,-11,z+1))
 details.append((outer-inner)^box(38,-15,z,14,9,7))
# Lower tall glazed pier below the curved balconies.
add(38,-2,2.8,14,21,48)
for z in [10,18,26,34,42]:
 cut(38,-12.5,z,10,3.5,6)
 details.append(box(38,-12.5,z,1,3.6,6))
# Portal recessed wall and broad projecting entry canopy.
for x in [-28,-17,-6,5,16,27]:
 cut(x,2,5,9,3,12)
 cut(x,2,21,9,3,5)
add(-4,-16,30,87,23,2.1)
# Three diagonal canopy hangers, visible in the farther oblique photograph.
for x in [-34,-4,26]:
 a=np.array([x,-25,31]);b=np.array([x,-8,46]);v=b-a
 # sturdy square rod generated in the YZ profile, fused into canopy and facade
 pts=[(-25,30.7),(-23.7,30.7),(-6.7,46.5),(-8,46.5)]
 details.append(CrossSection([pts]).extrude(1.6).rotate((90,0,90)).translate((x-.8,0,0)))
for i in range(4):add(-4,-30+i*1.7,2.8,83,1.9,.6+i*.65)
# The rear flat plane is a sectional backing. Original footprint not reconstructed.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
