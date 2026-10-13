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
# Official building ID 15: auditorium and attached Yong-Su chapel in ONE model.
# Angled public entrance fronts the polygonal main hall; auxiliary gallery turns beside it.
add(0,0,0,150,140,3)
poly=[(-65,-15),(-65,20),(-43,52),(-12,52),(8,29),(8,-1),(-14,-26),(-45,-26)]
parts.append(CrossSection([poly[::-1]]).extrude(55).translate((0,0,2.8)))
# Single shallow polygonal roof slab outlines the hall, no fabricated pitched megastructure.
parts.append(CrossSection([poly[::-1]]).offset(1.8).extrude(2).translate((0,0,57.3)))
# East gallery wing, ground setback and upper continuous glazing.
add(32,29,3,60,14,33)
for x in [6,20,34,48,61]:add(x,15,3,2.4,2.4,32)
for z in [17,34]:add(32,19,z,62,12,2)
for x in [10,24,38,52]:cut(x,22,23,10,3,8)
# Build main entrance facade in local coordinates then rotate toward southeast.
ip,ic,idt=len(parts),len(cuts),len(details)
add(0,0,2.8,49,37,62)
# Distinct stepped asymmetric gable, round window and lower narrow window row.
ped=[(-26,62),(26,62),(26,78),(18,79),(18,82),(6,89),(6,85),(-2,85),(-2,90),(-17,87),(-17,84),(-26,85)]
parts.append(profile(ped,-18.5,5.2))
cuts.append(Manifold.cylinder(4,3.0,3.0,circular_segments=48).rotate((90,0,0)).translate((2,-18.5,81)))
for x in [-20,-13,-6,1,8,15,22]:cut(x,-20,54,3.2,5,8)
# Heavy portal frame and tall gridded upper glazing.
cut(0,-18.5,27,38,4.5,21)
for x in range(-15,16,5):details.append(box(x,-18.6,26.8,1.1,5.2,21.4))
for z in [33,40]:details.append(box(0,-18.6,z,39,5.2,1.1))
add(0,-23,3,31,12,22)
cut(0,-29,3,24,5,16)
hip(0,-23,24.5,37,14,3.7)
# Side bands from the visible brick/stone horizontal accents.
for z in [68,73,78]:
 for x in [-25,25]:add(x,-21,z,5,2,1.2)
for i in range(4):add(0,-34+i*1.6,2.8,39,1.9,.8+i*.7)
for arr,start in [(parts,ip),(cuts,ic),(details,idt)]:
 for j in range(start,len(arr)):arr[j]=arr[j].rotate((0,0,45)).translate((6,-10,0))
# Attached chapel sits beside main hall, with flat cap and distinctive recessed cross/window face.
add(-46,-32,2.8,32,29,58)
add(-46,-32,60,35,32,2)
for x in [-58,-50,-42,-34]:cut(x,-46.5,46,4,3,8)
for x in [-56,-36]:
 cut(x,-46.5,24,6,4,16)
 details.append(box(x,-46.5,23.8,1.1,4.5,16.4))
# Cross as shallow facade relief; part of the chapel, not an added freestanding cross.
add(-46,-47,32,1.5,1.4,8)
add(-46,-47,36,6,1.4,1.5)
for x in [-56,-36]:cuts.append(Manifold.cylinder(3,3.2,3.2,circular_segments=40).rotate((90,0,0)).translate((x,-45.3,11)))
cut(-46,-46.5,3,10,4,11)
hip(-46,-49,16,25,10,2.8)
for i in range(3):add(-46,-56+i*2,2.8,27,2.3,.7+i*.7)
# Far side and roof service details not documented by sources remain plain.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
