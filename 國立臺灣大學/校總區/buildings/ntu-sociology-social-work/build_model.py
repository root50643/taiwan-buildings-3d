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
def shallow_arch(x,y,z,w,h,depth,rise):
 pts=[(x-w/2,z),(x+w/2,z),(x+w/2,z+h-rise)]
 pts += [(xx,z+h-rise+rise*(1-((xx-x)/(w/2))**2)) for xx in np.linspace(x+w/2,x-w/2,31)[1:]]
 return profile(pts,y,depth)
# E9: distinct from neighboring National Development hall E10.
add(0,0,0,150,88,3)
add(0,7,2.8,136,58,61)
# Projecting central stair bay with broad horizontal floor bands.
add(0,-24,3,38,8,65)
for z in [25,39,53]:
 cut(0,-28,z,20,3.5,9)
 details.append(box(0,-28.1,z-1,38,3,2))
 for x in [-6,0,6]:details.append(box(x,-27.5,z,.9,2,9))
# Central low gable and circular medallion are supported by official front photo.
add(0,-24,64,46,8,6)
gable(0,-24,69.5,26,8,5)
cuts.append(Manifold.cylinder(3,2.2,2.2,circular_segments=40).rotate((90,0,0)).translate((0,-26.5,69.5)))
# Low broad portal uses a shallow segment, not a semicircular arch.
add(0,-27,3,43,12,19)
cuts.append(shallow_arch(0,-33,3.3,30,14.5,3.6,3.8))
for x in [-11,-5.5,0,5.5,11]:details.append(box(x,-31.8,2.8,1,2,13.5))
for z in [8,13]:details.append(box(0,-31.8,z,30,2,1))
add(0,-33,21,45,2,1.5)
step(0,-38,42,4)
# Photo-observed wall/window groupings; trees hide tiny details which are not fabricated.
for x in [-54,-38,38,54]:
 for z in [20,31,42,53]:
  cut(x,-22,z,9,3,7)
  details.append(box(x,-21.6,z+3.7,9.6,2,.9))
for x in [-58,58]:cuts.append(Manifold.cylinder(3,3.2,3.2,circular_segments=40).rotate((90,0,0)).translate((x,-20.7,9)))
for side in [-68]:
 for y in [-15,-2,11,24,32]:
  for z in [20,31,42,53]:cut(side,y,z,3,7,7)
 for z in [18,29,40,51,62]:add(side,7,z,2,58,1.3)
 for y in [-19,-6,7,20,33]:add(side,y,18,2,1.2,45)
# Rear omitted rather than copying the entrance.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
