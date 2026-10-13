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
# Activities centre: asymmetrical exposed concrete facade and projecting round-window tower.
add(0,0,0,150,89,3)
add(0,8,2.8,132,54,94)
# Left side wing gallery bays stacked behind the tower.
for z in [27,47,67,87]:
 for x in [-56,-39]:cut(x,-19,z,13,5,9)
# Narrow perforated ground level screen behind left galleries.
for x in range(-61,-33,5):
 for z in [7,13,19]:cut(x,-19,z,3,3,3)
# Centre tall window strips alternate with narrow ventilation slots underneath.
for z in [30,50,70,90]:
 for x in [-9,3,15,27]:
  cut(x,-19,z,10,3.3,7 if z<90 else 5)
  cut(x,-19,z-6,8,3.3,2.5)
# Right wall is relatively plain and has only paired horizontal openings.
for z in [34,59,84]:
 for x in [44,61]:cut(x,-19,z,10,3.3,3)
# Projecting circulation tower, circular window openings visibly recessed, not through building.
add(-24,-22,2.8,18,14,102)
for z in [15,37,59,81]:
 cuts.append(Manifold.cylinder(4.5,4.4,4.4,circular_segments=48).rotate((90,0,0)).translate((-24,-26.7,z)))
# Entrance broad undercut below sign/header, retains right pier and core.
cut(7,-19,3,35,10,19)
add(6,-22,22,39,6,3)
for i in range(5):add(8,-36+i*2,2.8,22,2.3,1+i*1.3)
# Side rear return documented only in partial view, plain planes elsewhere.
add(-53,8,96,23,36,3)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
