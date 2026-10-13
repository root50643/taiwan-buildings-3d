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
# E61: only the five-wave entrance section, NOT the whole 178 m long complex.
add(0,0,0,150,95,3)
add(0,6,2.8,130,64,48)
# Five shallow barrel-profile roofs observed in front and oblique photos.
for x in [-52,-26,0,26,52]:
 pts=[(x-13.3,49),(x+13.3,49)]
 pts += [(xx,51+4.5*(1-((xx-x)/13.3)**2)) for xx in np.linspace(x+13.3,x-13.3,33)]
 parts.append(profile(pts,6,68))
 # Front paired windows flank broad pale solid panels.
 for xx in [x-8.6,x+8.6]:
  for z in [6,21,36]:
   cut(xx,-26,z,6.2,2.5,10)
   details.append(box(xx,-25.6,z,1,1.8,10))
   details.append(box(xx,-25.6,z+6,5.8,1.8,.9))
 # Three little roof-end vents, enlarged as backed recesses.
 for xx in [x-2.5,x,x+2.5]:cut(xx,-28,52.5,1.2,3,1.2)
for x in [-65,-39,-13,13,39,65]:add(x,-26.7,3,1.8,2.5,49)
for x in [-52,-26,0,26,52]:
 if x!=0:add(x,-27,3,11,2,43)
# Modest rectangular entry and flat projecting canopy, not a grand invented portico.
cut(0,-26,4,15,3,13)
for x in [-5,0,5]:details.append(box(x,-25.6,4,.9,2,13))
add(0,-29,17,30,10,1.7)
step(0,-38,32,4)
# Side vertical piers and windows supported by public oblique photo, simplified rhythm.
for x in [-65,65]:
 for y in [-17,-3,11,25,35]:
  add(x,y,3,2.2,2,48)
  for z in [8,23,38]:cut(x,y+4,z,2,6,9)
# Rear section cut-off is deliberately plain; remaining long hall not included.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
