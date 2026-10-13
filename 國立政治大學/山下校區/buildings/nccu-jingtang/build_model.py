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
# Four-storey crescent teaching block; actual curve is retained, not faceted classroom boxes.
add(0,0,0,150,110,3)
parts.append(prism(arc_poly(65,43),2.8,54.2))
# Small rear central lecture/stair appendage follows the public plan.
add(0,39,2.8,26,25,44)
# Open curved forecourt is left entirely unfilled above the base.
for deg in range(9,180,13):
 th=math.radians(deg)
 for z in [8,21,34,47]:
  r=43.5;x=r*math.cos(th);y=-28+r*math.sin(th)
  cuts.append(rotated_box(x,y,z,7.1,6,6.8,deg+90))
  details.append(rotated_box(x,y,z,1.2,4.3,6.8,deg+90))
for deg in range(2,180,13):
 th=math.radians(deg);r=42.7
 parts.append(rotated_box(r*math.cos(th),-28+r*math.sin(th),3,2.5,4.5,54,deg+90))
# Continuous curved roof/eave and stiff connected crown. No imaginary court roof.
parts.append(prism(arc_poly(67,40.5),56.8,1.7))
parts.append(prism(arc_poly(66,63.8),58.2,1.3))
# Central entry canopy follows the inner curve with side piers.
add(0,8,13.5,23,13,1.8)
for x in [-9,9]:add(x,7,3,2.6,2.6,11.5)
step(0,0,22,4)
# Curved outer rear wall kept plain where contemporary photo coverage is weak.
add(0,39,46.2,29,27,1.8)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
