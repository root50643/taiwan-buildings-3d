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
# Three-storey humanities hall with broad upper band over deep two-storey porch.
add(0,0,0,150,103,3)
add(0,12,2.8,130,62,65)
# Thick continuous top band projects in front of the tall lower columns.
add(0,-21,46,130,20,22)
# Lower front wall is recessed, with tall entrance glazing behind four high piers.
cut(0,-19,3,120,7,42)
for x in [-39,-13,13,39]:details.append(box(x,-29,3,3.8,5,43.2))
# Side paired pilasters reinforce a deep facade, instead of a texture on a box.
for x in [-61,-50,50,61]:details.append(box(x,-28,3,2.6,6,43.2))
for x in [-58,-46,46,58]:
 for z in [8,28]:cut(x,-15,z,8.5,3,12)
cut(0,-15,4,61,3,34)
for x in [-26,0,26]:details.append(box(x,-15,4,1.7,3.5,34))
details.append(box(0,-15,19,61,3.5,1.7))
# Upper long meeting-room band: three grouped windows divided by thick blank piers.
for x,w in [(-52,19),(0,58),(52,19)]:
 cut(x,-31,50,w,3,14)
 for xx in np.arange(x-w/2+2,x+w/2,6):details.append(box(float(xx),-31,50,1.4,3.5,14))
# Lateral wall treatment backed by official oblique facade photo: giant shallow pilasters.
for y in [-9,7,23,39]:
 add(-65,y,3,2,3,42)
 for z in [8,28]:cut(-65,y+6,z,3,8,11)
step(0,-40,98,4)
# Main depth/roof/unknown rear simplified, no invented courtyard or separate rear wing.
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
