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
# Gate guardhouse and integrated curved tower. Separate sign wall is excluded.
# Source: university-supplied NTNU exterior photograph and actual rear photo 2024-10-19.
def ellipse(rx,ry,h,z,x=0,y=0):return Manifold.cylinder(h,1,1,circular_segments=96).scale((rx,ry,1)).translate((x,y,z))
add(0,0,0,110,95,3)
# Ground booth, curved glazed public-facing front; deep carved openings remain backed.
parts.append(ellipse(24,18,36,2.8,y=-3))
# Door and glass subdivisions on front, with thick mullions.
cut(-5,-20,3,10,7,27)
for x in [-17,8,18]:
 for z in [7,19,29]:cut(x,-19,z,7,7,7)
for z in [7,19,29]:cut(23,-4,z,6,15,7)
# Tall oval concrete fin/tower with inclined top edge; relative depth is an estimate.
parts.append(ellipse(18,12,146.5,2.8,y=7))
# Inclined top plane cuts original circular extrusion without taking a site mesh.
cuts.append(box(0,7,145,130,100,50).rotate((0,-9,0)))
# Overhanging curved band: open top around the tower, robust 2mm roof slab beneath.
outer=ellipse(38,25,19,0,y=-2);inner=ellipse(35.8,22.8,24,2.2,y=-2)
ribbon=(outer-inner-box(-25,20,-1,42,25,30)).rotate((3,-12,0)).translate((0,0,43))
parts.append(ribbon)
# Rear/right downward-curving terminal pier, integral with the canopy.
terminal=(ellipse(38,25,54,2.8,y=-2)-ellipse(35.8,22.8,57,2.5,y=-2))^box(32,10,2.8,16,29,57)
parts.append(terminal)
# Two broad supporting piers beneath the outer lip, documented simplification.
add(-26,-9,2.8,3,5,40.5)
# A small recessed shaft slot is observed above the lower band.
cut(14,-3,63,3.2,4,8)
# No tiny embossed letters/emblem: emblem represented by attached geometric medallion.
parts.append(Manifold.cylinder(1.1,5,5,circular_segments=48).rotate((90,0,0)).translate((-3,-4.4,112)))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.apply_scale(150.0/max(mesh.extents))
mesh=trimesh.Trimesh(np.asarray(mesh.vertices,dtype=np.float32),np.asarray(mesh.faces),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
