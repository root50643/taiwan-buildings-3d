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
# E Business: central tall glazing, two deeply recessed balcony stacks and oversailing cap.
add(0,0,0,150,100,3)
add(0,12,2.8,86,48,118)
# Central curtain-wall strip projects slightly in front of parallel balcony stacks.
add(0,-16,3,15,11,119)
cut(0,-21.5,8,11,2.4,109)
for x in [-3.5,3.5]:details.append(box(x,-21.5,8,1,2.6,109))
for z in range(12,117,9):details.append(box(0,-21.5,z,11,2.6,1))
# Two stacks, eight pronounced inset balcony openings.
for x in [-22,22]:
 for z in range(10,114,13):
  cut(x,-12,z,20,10,9)
  details.append(box(x,-12,z-.9,21,12,1.8));details.append(box(x,-17,z,21,2,2.5))
# End screens are shallow and have sparse small perforations, not generic window grids.
for x in [-39,39]:
 add(x,-14,4,8,5,115)
 for z in [18,34,83,99]:cut(x,-17,z,3,2.5,4)
# Broad projecting lintel/cap and a small arched rooftop core.
add(0,9,120,94,55,3)
add(0,16,122.7,31,22,6)
parts.append(arch(0,16,125,22,14,18))
arch_cut(0,6.5,127,8,9,2.5)
# Horizontal side fins at roofline.
for z in [108,114,120]:add(0,12,z,96,48,1.7)
cut(0,-16,3,12,12,8)
step(0,-34,35,4)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
