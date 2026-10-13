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
# Millennium dormitory, two roof-end towers and rounded off-centre stair bay.
add(0,0,0,150,86,3)
add(0,7,2.8,134,45,75)
# Paired end roof towers, central taller brick tower, stepped parapets.
add(-58,9,77.4,18,27,13)
add(58,9,77.4,16,27,13)
add(-8,9,77,23,25,23)
for x in [-58,58]:hip(x,9,90,19,29,2.8)
hip(-8,9,99.8,25,28,3)
# Central rounded bay projects in front; use actual circular mass rather than box.
parts.append(Manifold.cylinder(82,10,10,circular_segments=80).translate((-8,-10,3)))
# Seven ranks of small windows, avoiding blanked openings behind curved bay.
for z in [8,17,26,35,44,53,62,71]:
 for x in [-58,-47,-36,-25,12,23,34,45,57]:cut(x,-15.5,z,5.5,3,4.5)
# Distinct horizontal belts on lower storeys; upper remains primarily brick field.
for z in [14,23,32]:add(0,-16,z,134,1.5,2.3)
# Curved bay bands and shallow glazing indicators, all relief tied into solid bay.
for z in [16,27,38,49,60,71]:
 details.append((Manifold.cylinder(2,10.5,10.5,circular_segments=80)-Manifold.cylinder(2.2,9,9,circular_segments=80).translate((0,0,-.1))).translate((-8,-10,z)))
 for a in [210,240,270,300,330]:
  t=math.radians(a);x=-8+10*math.cos(t);y=-10+10*math.sin(t)
  # Fine pane mark as broad shallow cuts; no interiors are represented.
  cuts.append(Manifold.cylinder(4,1.3,1.3,circular_segments=16).translate((x,y,z+3)))
# Observed end wall openings, sparse single windows.
for z in [8,17,26,35,44,53,62,71]:
 for y in [-7,9,23]:cut(67,y,z,3,5,4.5)
# Stepped entrance portico, no adjacent Wenrui or convent geometry included.
cut(-8,-20,3,12,6,8)
add(-8,-22,11.5,25,10,1.6)
for x in [-19,3]:add(x,-25,3,2,2,9)
for i in range(4):add(-8,-35+i*2,2.8,30,2.3,.8+i*.8)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
