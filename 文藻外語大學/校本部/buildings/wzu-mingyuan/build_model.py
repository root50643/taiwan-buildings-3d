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
# Mingyuan: two open courts, three longitudinal wings and high central gate pavilion.
add(0,0,0,150,120,3)
# Outer long wings and far crossbar define two courts; ground voids are preserved.
for x in [-56,56]:add(x,2,2.8,24,79,34)
add(0,35,2.8,136,16,34)
add(0,3,2.8,24,74,37)
# Open front gallery bridges across courts at the upper level.
for x in [-28,28]:
 add(x,-30,18,32,8,2)
 add(x,-33.5,20,32,1.4,2)
 for xx in [x-13,x,x+13]:add(xx,-31,3,1.8,2.2,16)
# Inner courtyard balcony openings on both wings and centre prong.
for x in [-44,-12,12,44]:
 for y in [-18,-4,10,24]:
  for z in [7,24]:cut(x,y,z,3.5,10,9)
# Entrance circular wall windows on the twin flank pavilions.
for x in [-56,56]:
 cuts.append(Manifold.cylinder(4,5.2,5.2,circular_segments=48).rotate((90,0,0)).translate((x,-36.5,12)))
 # Upper gallery behind the little gable stays open to the front, supported by piers.
 cut(x,-37.5,24,18,7,9)
 gable(x,0,36.5,29,82,8)
# Rear roofs lower; omitted unknown small rooftop services.
hip(0,35,36.5,139,21,4)
# Central tall orange pavilion with deep ground passage, open through to central walkway.
cut(0,-29,3,18,20,13)
cut(0,-36,26,20,4,5)
add(0,-34.5,23,26,3,1.6)
gable(0,-24,40,30,28,8)
# Behind pavilion central prong is roofed; both neighboring courts remain open to sky.
gable(0,9,39.5,27,40,7)
# Low steps at central portal.
for i in range(4):add(0,-48+i*2,2.8,27,2.3,.8+i*.65)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
