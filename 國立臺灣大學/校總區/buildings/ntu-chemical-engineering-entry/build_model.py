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
# M8 documented central entrance facade around the three-arch portico.
# Whole east/west extensions and southern connecting laboratory are excluded.
add(0,0,0,150,79,3)
add(0,8,2.8,138,38,43)
# Two tall storeys with curved projecting window hoods, a broad blind panel at right.
for x in [-64,-53,-42,-31,-20,-9,2,13,24,35,64]:
 for z in [6,25]:
  cut(x,-11,z,5.7,3,13)
  details.append(box(x,-10.5,z+8,5.3,2,1))
  # Solid shallow arched hood: visible camber preserved without delicate thin trim.
  pts=[(x-4,z+13),(x+4,z+13),(x+4,z+14)]+[(float(x+4*t),z+14+1.4*(1-t*t))for t in __import__('numpy').linspace(1,-1,17)[1:]]
  details.append(profile(pts,-12,4))
 for z in [5,24]:add(x,-11.3,z,7.3,1.8,1)
# Thin grey piers frame each repetitive bay; plain right wall is deliberately retained.
for x in [-69.5,-58.5,-47.5,-36.5,-25.5,-14.5,-3.5,7.5,18.5,29.5,40.5,69.5]:add(x,-11.4,3,1.2,1.8,41)
add(0,8,44,140,40,2)
# Ventilated upper roof enclosure in the 2026-published exterior photos.
add(0,8,45,139,38,5.4)
for x in [-61,-43,-25,-7,11,29,47,65]:cut(x,-11,46,13,2.7,2.4)
add(0,8,50.1,144,44,1.5)
# Three broad shallow entrance arches; actual solid stair treads, no wire railings.
cut(13,-11,3,37,4,19)
for x in [2,13,24]:details.append(box(x,-10.8,3,1.2,2.3,19))
add(13,-23,24,44,28,2.5)
for x in [-9,5.7,20.3,35]:add(x,-36,3,2.3,3.1,23)
add(13,-36,19,46,3.1,7.5)
for x in [-1.7,13,27.7]:
 pts=[(x-6.1,3),(x+6.1,3),(x+6.1,21)]+[(float(x+6.1*t),21+2.8*(1-t*t))for t in __import__('numpy').linspace(1,-1,25)[1:]]
 cuts.append(profile(pts,-36,5))
for i in range(5):add(13,-38+i*1.5,3,41,1.8,.65*(i+1))
# Rear/end elevations are plain bounded study faces, not invented complete wings.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
