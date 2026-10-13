"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. Public plan outlines guide massing; interiors are not reconstructed.
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
# Zhishan: eight storeys, asymmetrical entry recess, broad canopy, narrow side slits.
add(0,0,0,116,103,3)
add(0,6,2.8,98,72,114)
# First storey right entry is recessed; upper floors bridge above it.
cut(25,-31,3.0,45,17,14)
# Entry glazing backs the open recess.
for x in [9,23,37]:cut(x,-22.5,4,10,4,11)
# F3-F5: four broad primary glazed groups per row. F6-F8: visibly narrow groups.
# Plans p39-40 show eight upper room subdivisions, but leftmost tree-hidden
# window openings are NOT inferred from room counts: six discernible groups retained.
for z in [33,47,61]:
 for x in [-36,-17,2,21]:
  cut(x,-30,z,16,4.4,7.6)
  # Broad connected glazing: do not turn fine glass mullions into brick piers.
for z in [75,88,101]:
 for x in [-20.25,-10.75,-1.25,8.25,17.75,27.25]:
  cut(x,-30,z,6.8,4.4,7.8)
  # Left two plan subdivisions remain unfenestrated because of tree occlusion.
# Low floor glazing and distinctive long right hand opening above entry canopy.
for x in [-37,-24,-11]:cut(x,-30,19,9.5,4.5,7.5)
cut(23,-30,19,39,6,8.3)
# Highest row short horizontally divided clerestory slots.
for x,w in [(-1,28),(25,16)]:cut(x,-30,112,w,4,2.1)
# Wide slightly sloping canopy anchored into wall and two stout rear supports.
canopy=CrossSection([[(-33.5,-6),(-30,-8),(-20,-11),(0,-13.5),(20,-11),(30,-8),(33.5,-6),(33.5,10.5),(-33.5,10.5)]]).extrude(2.5).translate((14,-34,17))
parts.append(canopy)
for x in [-15,43]:add(x,-30,3,2.3,7,15.5)
# Front entrance steps curve gently at left using broad overlapping blocks.
for i in range(4):add(15,-45+i*2,2.8,61,2.8,.65*(i+1))
# Observed narrow side: separated slim vertical slots at floor/stair levels.
for y in [-14,18]:
 for z in [10,24,38,52,66,80,94,108]:cut(49,y,z,3.8,2.6,6.8)
# Rear facade has a narrow projecting left stair strip with paired windows,
# and wider classroom windows; distant lower obscured portions simplified.
add(39,43,14,18,7,102.8)
for z in [20,34,48,62,76,90,104]:
 for x in [-31,-8,15]:cut(x,42,z,16,4.5,8)
 for x in [35,43]:cut(x,46.5,z,4.5,4,8)
# Low roof border only, equipment not observed and omitted.
for y in [-30,42]:add(0,y,116.2,99,1.6,1.5)
for x in [-49,49]:add(x,6,116.2,1.6,73,1.5)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
solid=solid.scale((150/117.7,)*3) # Entire model, including base, scaled to 150 mm maximum.
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
