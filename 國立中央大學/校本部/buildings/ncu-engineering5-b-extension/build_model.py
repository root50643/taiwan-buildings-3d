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
# Independent 2014-2015 B extension wing, not old AB round hall or C block.
add(0,0,0,150,63,3)
add(-4,4,2.8,125,28,61)
# Tall end core, recessed full-height glazed strip and roof stair-head step.
add(62,4,2.8,12,30,65)
add(51,4,2.8,10,30,65)
# Deep projecting frame on long front with double-height top-storey frame.
add(-6,-15,3,116,4,60)
for x in range(-56,45,13):
 for z,h in [(6,9),(19,9),(32,9),(45,16)]:cut(x,-15,z,10,6,h)
# Balcony/floor connections tie front colonnade to recessed main facade.
for z in [3,17,30,43,61]:add(-6,-12,z,116,10,1.8)
# Actual window bays recessed behind frame, no hidden through-chambers.
for x in range(-56,45,13):
 for z in [7,20,33,47]:cut(x,-10,z,8.5,3,7)
# Full-height strip at the higher core, robust fin spacing.
cut(52,19,8,9,3,52)
for x in [49,52,55]:details.append(box(x,19,8,1.1,3.5,52))
# Opposite long facade photographed: repeated classroom windows and horizontal louvers.
for x in range(-56,45,13):
 for z in [8,20,32,44,56]:cut(x,18,z,8.5,3,6)
for z in [15,27,39,51]:
 for dz in [0,1.4]:add(-6,18.5,z+dz,115,1.1,.9)
# Roof sloping canopy/photovoltaic-like cover shown in rear photo, simplified continuous band.
parts.append(profile([(-66,63), (47,63),(47,65),(-66,66)],6,25))
# Unknown narrow ends and connection to old B block remain a flat cut-off; old building excluded.
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
solid=solid.scale((-1,1,1)) # Match long-frame facade end orientation in contractor photograph.
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
