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

def roundedbox(x,y,z,w,d,h,r=2):
 pts=[]
 for cx,cy,angle in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
  for a in np.linspace(angle,angle+90,9):pts.append((x+cx+r*math.cos(math.radians(a)),y+cy+r*math.sin(math.radians(a))))
 return CrossSection([pts]).extrude(h).translate((0,0,z))
# Administration building FRONT BLOCK / PORTICO SECTION, based on 2024 photographs.
# Back plane is an intentional cut; the unverified full rear building is excluded.
add(0,0,0,150,62,3)
# Broad front stair terrace, continuous across the frontage.
for i in range(7):add(0,-27+i*1.75,2.8,137,2.1,.65*(i+1))
add(0,-6,2.8,137,34,4.7)
# Four-storey recessed wings, not folded into the central overhanging porch.
for side in [-1,1]:
 add(side*51,8,7.1,34,24,44)
 for z in [10,20,30,40]:
  for x in [side*40,side*49,side*59]:cut(x,-4,z,6.6,3,6)
  add(side*51,-4.3,z-1.2,34,1.1,1.1)
 for x in [side*35,side*66]:add(x,-6,7,1.8,4.6,44.5)
 add(side*51,7,50.2,37,29,1.8)
# Central core sits well behind the six giant full-height columns.
add(0,11,7.1,70,23,55)
# Recessed double-height glazed entrance and middle band windows.
cut(0,-.5,8.5,63,2.3,15)
for x in range(-29,30,6):details.append(box(x,-1.3,8.5,1.1,2.1,15))
for z in [12.5,18.2]:details.append(box(0,-1.3,z,63,2.1,1.1))
for x in [-26,-13,0,13,26]:cut(x,-.5,27,10,2.5,5.3)
# Two upper storeys are cantilevered forward over the deeply open lower portico.
add(0,1,35,73,41,27)
for z in [39,53]:
 for x in [-28,-14,0,14,28]:
  cut(x,-19.5,z,11,3.1,5.5 if z==39 else 3.2)
  details.append(box(x,-19.8,z,1.1,2.4,5.5 if z==39 else 3.2))
# Six cylinders: actual round giant-order columns visible in 2024 fronts.
for x in [-36,-21.6,-7.2,7.2,21.6,36]:column(x,-19,7,1.55,57)
# Roof has broad cantilever eaves, with small connected corbels.
add(0,0,62,86,46,2.1)
for x in [-36,-21.6,-7.2,7.2,21.6,36]:add(x,-19,59.8,2.5,7,3)
add(0,7,63.8,54,17,2.5)
# The low sign panel is backed, rather than tiny text which would not survive printing.
add(0,-.5,24,26,1.4,2.1)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
