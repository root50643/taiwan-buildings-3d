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
# L life application building: 2024-10-19 full long elevation and event side view.
add(0,0,0,150,120,3)
add(-4,23,2.8,123,67,91)
# Left projecting circulation bay forms seven open-front balcony bands.
add(-53,-14,2.8,26,17,91)
for z in [14,26,38,50,62,74,86]:
 cut(-53,-23,z,20,8,7)
 add(-53,-24,z-2,29,4,1.8)
# Main middle facade has inset paired windows in concrete frames, seven visible levels.
for z in [9,21,33,45,57,69,81]:
 for x in [-28,-13,2,17,32]:
  cut(x,-10.5,z,10.7,5,7.0)
  details.append(box(x,-10.9,z,1.05,5.5,7.1))

for z in [18,30,42,54,66,78,90]:add(0,-12,z,88,3.5,1.8)
for x in [-35.5,-20.5,-5.5,9.5,24.5,39.5]:add(x,-12,3,1.8,3.5,88)
# Clear two-level glazed central entrance panel interrupts lower regular bays.
cut(4,-10.8,9,23,5.5,21)
for x in [-5,4,13]:details.append(box(x,-11.2,9,1.3,6,21))
for z in [16,23]:details.append(box(4,-11.2,z,23,6,1.3))
add(4,-17,9,30,15,2)
# Far rounded circulation end: upper curved glazing and open parapet.
parts.append(Manifold.cylinder(88,17,17,circular_segments=96).translate((47,6,3)))
for z in [13,25,37,49,61,73]:
 ring=Manifold.cylinder(6,17.5,17.5,circular_segments=96)-Manifold.cylinder(7,15.2,15.2,circular_segments=96).translate((0,0,-.5))
 cuts.append(ring.translate((47,6,z))^box(47,-4,z,40,24,6))
 for deg in range(190,351,30):
  a=math.radians(deg);details.append(box(47+16.1*math.cos(a),6+16.1*math.sin(a),z,1.4,1.4,6.1))
# Right end stair openings and paired small windows, actually visible in event photograph.
for z in [13,25,37,49,61,73]:
 cut(57.5,44,z,10,17,7)
 details.append(box(58,44,z-.2,1.2,17.2,1.6))
 cut(57.5,29,z+1,5,8,3.4)
 cut(63,9,z+1,8,9,3.4)
# Top rounded parapet band has open intervals and stout supports.
ring=(Manifold.cylinder(2,17.8,17.8,circular_segments=96)-Manifold.cylinder(3,15.5,15.5,circular_segments=96).translate((0,0,-.5))).translate((47,6,95))
parts.append(ring)
for deg in range(0,360,45):
 a=math.radians(deg);add(47+16.5*math.cos(a),6+16.5*math.sin(a),90,1.8,1.8,6)
add(-6,23,93,122,69,1.7)
# Basement parking portal at right end, no interior fabricated.
cut(58,43,3,10,22,8)
step(4,-27,37,5)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
