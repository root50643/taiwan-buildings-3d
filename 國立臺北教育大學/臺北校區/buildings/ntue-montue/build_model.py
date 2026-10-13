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
# MoNTUE: north fin wall, south brick wall/colonnade, and stepped east stair.
# Plan length 35.3m and nominal depth14.4m guide ratios, not survey dimensions.
add(0,0,0,150,81,3)
# Recessed ground floor, with glass represented by backed cavities.
add(0,2,2.8,134,45,16)
# Main upper box stops short of the eastern stairhead.
add(-8,0,18,118,55,41)
add(59,0,3,18,55,63)
# North continuous double-height glazing, deeply recessed behind vertical fins.
cut(-11,-27.5,21,112,7,34.5)
# Angled metal sun fins. 24 fins: regularized visible spacing, print-thickened.
for x in [-64+4.6*i for i in range(24)]:
 parts.append(box(0,0,0,1.4,6.5,37).rotate((0,0,-12)).translate((x,-29,19)))
add(-11,-28,18,114,5,2.1)
add(-11,-28,56.5,114,5,2.0)
# Glazing lower rows are backed recesses and broad real structural piers.
for x in range(-60,41,10):
 cut(x,-20.5,4,8.4,3.8,12)
 cut(x,24.5,4,8.4,3.8,12)
# South colonnade open in front of the set-back glazed ground floor.
add(0,29,17,137,10,2.1)
for x in [-63,-51,-39,-27,-15,-3,9,21,33,45,57,66]:column(x,30,3,1.1,15.6)
# Upper south brick face: sparse two slit openings left and small square right.
for z in [33,45]:cut(-49,27.5,z,14,3.6,2.2)
cut(49,27.5,50,3.1,3.6,3.1)
# West end glass return, visible in the north-front photograph and plan.
cut(-67,-10,22,5.5,27,32)
for y in [-20,-10,0]:details.append(box(-66.5,y,22,3,1.2,32))
# East stair face: separated deep recessed balconies, never a generic window grid.
for z in [8,27,45]:cut(68,9,z,6.2,6.5,12)
for z in [27,45]:details.append(box(66.8,9,z,3.6,6.5,2.3))
# The projecting north-east corner window, with simplified asymmetric ear surround.
add(67,-21,23,9,11,25)
cut(71.5,-21,26,2.8,7,19)
cut(67,-26.5,26,6.8,3,19)
# Faceted thick outline of Walls Have Ears: explicitly simplified, self-authored.
ear=CrossSection([[(-28,22),(-31,25),(-31,46),(-27,50),(-17,50),(-17,47),(-27,45),(-27,27),(-18,24),(-18,21)][::-1]]).extrude(3.2).rotate((90,0,90)).translate((70,0,0))
parts.append(ear)
# Roof terrace, hollow at top rather than an invented solid penthouse.
cut(-8,0,57.2,113,49,9)
# High stair head has its own inset terrace visible in the 2017 rooftop photograph.
cut(59,0,63.5,13,49,8)
# Small roof service box on the far western side observed in the same photograph.
details.append(box(-52,9,56.8,20,17,10))
details.append(box(-52,9,66.1,21,18,1.2))
# Side entrance small slab is integrated with stair, no separate detached bridge.
add(69,11,17,8,15,1.8)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
