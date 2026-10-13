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
# M9: seven-bay end elevation, tall side fins, external stairs.
add(0,0,0,150,108,3)
add(0,8,2.8,132,74,75)
add(0,8,77,139,81,2.2)
# Seven bays. Upper windows have shallow pointed crowns under a flat roof.
for x in [-57,-38,-19,0,19,38,57]:
 for z,h in [(7,9),(22,11),(39,6),(50,12)]:
  cut(x,-29,z,15,3,h)
  details.append(box(x,-28.5,z,1,2,h))
  if h>9:details.append(box(x,-28.5,z+h/2,15,2,.9))
 cuts.append(profile([(x-7.5,65),(x+7.5,65),(x+7.5,74),(x,76),(x-7.5,74)],-29,3))
 for xx in [x-3.8,x,x+3.8]:details.append(box(xx,-28.5,65,.9,2,9))
 details.append(box(x,-28.5,69.5,15,2,.9))
for x in [-66.5,-47.5,-28.5,-9.5,9.5,28.5,47.5,66.5]:add(x,-29.5,3,2.5,3,75)
# Deep flat entrance canopy and prominent solid flight to raised entry.
add(0,-32,34,23,10,1.7)
for i in range(18):add(0,-49+i*1.13,2.8,23,1.5,(i+1)*1.04)
for x in [-12.4,12.4]:
 for i in range(18):add(x,-49+i*1.13,2.8,1.4,1.5,(i+1)*1.04+1.8)
# Side elevation seen through trees: long raised wall with regular narrow fins.
for x in [-66,66]:
 for y in [-22,-9,4,17,30,41]:
  add(x,y,18,3.5,1.6,59)
  cut(x,y+4,24,2,4,42)
# Unseen back left intentionally blank. No roof plant or interior rooms.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
