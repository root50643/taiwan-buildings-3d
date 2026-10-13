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
# E53 Wancai main block and documented front stair/low annex, not all surrounding links.
add(0,0,0,150,120,3)
add(0,11,2.8,136,49,81)
# Upper three-tier facade differs from Linze's two-plus-two composition.
for z in [46,58,70]:
 for center in [-57,-38,-19,0,19,38,57]:
  for dx in [-5,0,5]:
   x=center+dx;cut(x,-13.5,z,3.4,3,9)
   details.append(box(x,-12.7,z+6.5,3,2,.9))
for x in [-57,-38,-19,0,19,38,57]:cut(x,-13.5,37,15,3,3.6)
for z in [35,42,83]:add(0,-14,z,138,3,1.8)
# Right short end with a shallow projecting glazed bay and tall ground slots.
add(69,11,43,5,17,39)
for z in [46,58,70]:cut(71.5,11,z,3,13,9)
for z in [7,19,29]:
 for y in [-7,2,25,31]:cut(68,y,z,3,3,6)
for z in [35,42,83]:add(68.5,11,z,3,51,1.8)
for z in [7,19,28]:
 for x in [47,58]:cut(x,-13.5,z,3,3,6)
# Front entry at raised level; recess is open from front, with solid back.
cut(17,-13.5,3,30,10,28)
# Low left entrance annexe documented in frontal exterior photo.
add(-43,-30,2.8,43,36,27)
cut(-43,-48,9,34,3,17)
for x in [-56,-47,-38,-29]:details.append(box(x,-47.6,9,1.1,2,17))
for x in [-64,-58]:cut(x,-48,6,2.2,3,16)
# Solid flight has real steps; shallow curved landing remains robust and attached.
for i in range(16):add(-6,-53+i*1.65,3,28,1.9,1.1*(i+1))
poly=[(-22,-10),(33,-10),(33,-18)]+[(float(x),-25-3*(1-((x-5.5)/27.5)**2))for x in __import__('numpy').linspace(33,-22,25)]
parts.append(CrossSection([poly[::-1]]).extrude(3).translate((0,0,19)))
# A solid low cheek wall follows the stair; thin railings are omitted.
for x in [-20.6,8.6]:
 for i in range(16):add(x,-53+i*1.65,3,1.4,1.9,2+1.1*(i+1))
add(0,11,83,137,50,2)
for y in [-12,34]:
 for x in [-65,-43,-21,1,23,45,65]:add(x,y,84.5,2.2,2.2,6)
for x in [-65,65]:add(x,11,84.5,2.2,2.2,6)
add(0,11,90,144,57,2)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
