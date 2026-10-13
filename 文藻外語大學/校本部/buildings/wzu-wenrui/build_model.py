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
# Ten-storey Wenrui: long classroom elevation and perpendicular narrow tower end.
add(0,0,0,150,86,3)
add(-10,3,2.8,110,42,111)
for z in [16,27,38,49,60,71,82,93,104]:
 for x in [-56,-40,-24,-8,8,32]:
  if not(x==32 and z<71):cut(x,-18,z,10,3.2,5.5)
for x in [-63,-31,1,23]:add(x,-18.4,14,2.4,2.2,101)
# Four prominent framed window groups on the narrow, perpendicular right end.
for z in [71,82,93,104]:
 cut(45,2,z,3.5,26,6)
 add(46,2,z-1.5,4,29,1.5)
 add(46,2,z+6,4,29,1.5)
 for y in [-5,4,11]:details.append(box(45,y,z,3.2,1.1,6))
add(25,5,114,32,30,15)
add(-10,3,113,114,47,2.2)
# Upper corner structural pier with narrow recessed vertical slot.
add(44,23,14,3,5,100)
cut(45.5,23,73,2,2,32)
# Low pavilion extends outward from tower end and is raised on stout pillars.
add(47,-3,14,46,54,53)
for y in [-27,20]:add(67,y,3,3,3,12)
for x in [26,66]:add(x,-28,3,3,3,12)
add(47,-3,66,50,58,2.8)
# Genuine undercroft and backed screen relief on both visible faces.
cut(47,-30,17,37,4,11)
cut(47,-30,30,38,3,32)
for x in range(29,67,2):details.append(box(x,-30.6,30,1.1,3.4,32))
cut(70,-3,17,4,44,11)
cut(70,-3,30,3,45,32)
for y in range(-24,20,2):details.append(box(70.6,y,30,3.4,1.1,32))
# Open terrace rails remain attached to rooftop and are thickened for printing.
add(71,-3,68.6,1.2,57,2.2)
add(47,-31,68.6,49,1.2,2.2)
add(47,25,68.6,49,1.2,2.2)
for i in range(5):add(47,-39+i*2,2.8,38,2.3,.7+i*1.0)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
