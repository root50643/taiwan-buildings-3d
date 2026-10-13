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
# Long red-brick assembly hall; seven paired bays and a genuine open arcade.
add(0,0,0,150,66,3)
add(0,4,2.8,138,38,22)
# Front arcade separated from backing wall by 5.4 mm clear depth.
add(0,-20,3,138,2.4,16)
add(0,-16,3,140,11,1.6)
for c in [-57,-38,-19,0,19,38,57]:
 for dx in [-4.5,4.5]:
  x=c+dx
  arch_cut(x,-20,4.5,6.8,11.7,3.5)
  arch_trim(x,-21.1,4.5,6.8,11.7)
  # Door and window backs retain the observed alternating rhythm.
  cut(x,-15,5.0 if dx<0 else 9.0,5.2,2,9.4 if dx<0 else 5.4)
 # Stone plinths reinforce every principal arcade pier.
 add(c+9.5,-20,3.2,3.8,4.3,2.8)
# Continuous horizontal cornice.
add(0,-20,18.0,141,3.8,1.6)
add(0,23,23.7,140,2.5,1.5)
# Asymmetrical roof cross-section: low arcade side and high rear eave.
poly=[(-22,18.8),(24,24.3),(24,25.5),(1.8,37),(-22,20)]
roof=CrossSection([poly]).extrude(140).rotate((90,0,90)).translate((-70,0,0))
parts.append(roof)
add(0,1.8,36.1,140,1.5,1.2)
# Rear: tall arched windows, alternating bay widths from public rear photograph.
for c in [-57,-38,-19,0,19,38,57]:
 for dx in [-4.5,4.5]:
  w=arch(c+dx,22.6,5.5,5.8,16,4.8)
  cuts.append(w)


# Both gable end walls, with tall central arches and lower aisle entrance.
for side in [-1,1]:
 x=side*69.3
 # Both ends retain the same documented three-arch centre, but the rectangular
 # flank windows and arcade-side opening are separate elements, never mirrored grids.
 parts.append(CrossSection([[(-21,3),(24,3),(24,25.5),(1.8,37),(-21,20)]]).extrude(2.1).rotate((90,0,90)).translate((x-1.05,0,0)))
 for y,h in [(-1,24),(6.5,24),(14,20.5)]:
  cuts.append(arch(y,0,5.5,4.4,h,4.2).rotate((0,0,90)).translate((x,0,0)))
 # Rectangular flank window beside the aisle and at rear corner, with solid transom.
 for y in [-8,20.5]:
  cut(x,y,5.5,4.4,4.1,11)
  cut(x,y,20,4.4,4.1,6.3)
 # Corner aisle passage enters the long arcade, same corridor on both ends.
 cuts.append(arch(-16.5,0,4.5,6,11.6,4.4).rotate((0,0,90)).translate((x,0,0)))
 # Tall centre piers and lower exterior corner piers.
 for y in [-21,-5,17.5,24]:
  add(x+side*.8,y,3,2.9,2.3,21 if y in [-21,24] else 28.5)
  add(x+side*1.1,y,15.5,3.5,3.3,1.7)
 cut(x+side*1.0,2,32,3.5,2.7,3)
# End-specific platform: the photographed B end has a ramp landing alongside
# the arcade entrance. D retains steps; no conjectured matching ramp is added.
add(71,-10,3,5,22,1.4)
# Steps contiguous with base, main covered arcade retained.
for z,d in [(3.0,2.4),(3.6,1.8)]:add(0,-24+d/2,z,138,d,0.8)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
