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
# M13: strong vertical concrete piers and four-pier monumental porch.
add(0,0,0,150,77,3)
add(0,5,2.8,136, 40,61)
# Thin roofline and the paired/fluted vertical fins prominent in source photographs.
add(0,5,63,139,43,2)
for x in range(-66,67,12):
 add(x,-16,3,3.2,3,63)
 add(x-1.5,-17,3,.9,2,63)
 add(x+1.5,-17,3,.9,2,63)
# Five window levels; glass represented by shallow solid-backed rectangular recesses.
for x in range(-60,61,12):
 for z in [6,18,30,42,54]:
  cut(x,-15,z,8,2,8)
  details.append(box(x,-15,z,1,1.5,8))
  details.append(box(x,-15,z+4,8,1.5,.9))
# Large elevated front portico spanning roughly three storeys, with visible deep soffit beams.
for x in [-27,-9,9,27]:details.append(box(x,-26,3,3.8,7,39))
details.append(box(0,-25,40,60,23,3.5))
for x in [-24,-12,0,12,24]:details.append(box(x,-25,38.5,1.5,23,2))
step(0,-34,58,5)
# Approximate central rooftop pediment/stair head visible in the source.
add(0,7,64,15,15,7)
gable(0,7,71,17,16,3)
# Side and rear window patterns not visible well enough: deliberately plain.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
