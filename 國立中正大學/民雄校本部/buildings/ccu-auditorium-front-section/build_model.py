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

# Front elevation and the adjoining porch only. No claim to reproduce auditorium back.
add(0,0,0,150,72,3)
add(0,15,2.8,46,28,88)
for x in [-38,38]:add(x,14,2.8,30,26,81)
for x in [-62,62]:add(x,17,2.8,18,23,65)
# Two superimposed gables, stone-edged and substantial, backed by structural mass.
gable(0,13,88,49,31,17)
gable(0,-7,53,69,13,24)
add(0,-4,3,65,16,51)
# The front gable is recessed glazed infill, not an open hole.
cuts.append(profile([(-28,55),(28,55),(0,74)],-13.5,2.7))
for x in [-17,0,17]:details.append(box(x,-14,55,1.6,2.7,15 if x==0 else 8.5))
details.append(box(0,-14,62,39,2.7,1.5))
# Paired sloping cornices with real section depth; beams fuse to roof surface.
def slope_beam(x1,z1,x2,z2,y,d,t):
 import math
 dx=x2-x1;dz=z2-z1;L=math.hypot(dx,dz)
 parts.append(Manifold.cube((L,d,t)).translate((0,-d/2,-t/2)).rotate((0,-math.degrees(math.atan2(dz,dx)),0)).translate((x1,y,z1)))
for yy,ww,zz,hh in [(-14,69,53,24),(-1,49,88,17)]:
 for off in [0,1.5]:
  slope_beam(-ww/2,zz+off,0,zz+hh+off,yy,2.8,1.9)
  slope_beam(0,zz+hh+off,ww/2,zz+off,yy,2.8,1.9)
# Tall four-pier front porch and balcony beam retain the deep open void.
add(0,-20,38,78,14,4.6)
for x in [-36,-13,13,36]:add(x,-25,3,3.8,5.5,36)
for x in [-36,36]:add(x,-13,3,3.8,5,36)
# Stairs and doorway behind porch.
for i in range(6):add(0,-32+i*1.5,2.8,74,2.0,.8*(i+1))
cut(0,-12,7,56,2.8,30)
for x in [-24,-12,0,12,24]:details.append(box(x,-12.4,7,1.5,2.6,30))
for z in [16,27]:details.append(box(0,-12.4,z,56,2.6,1.5))
# Side masses show four floors of grouped windows and alternating stone bands.
for x in [-38,38]:
 for z in [15,29,43,58]:
  cut(x,1, z,17,3,10)
  details.append(box(x,0.5,z+4.5,17,3,1.25))
  for dx in [-5.6,0,5.6]:details.append(box(x+dx,0.5,z,1.25,3,10))
  add(x,-.2,z-2,29,1.5,1.6)
for x in [-62,62]:
 for z in [12,26,40,54]:
  cut(x,5.5,z,9,3,8.8);details.append(box(x,5.3,z,1.5,3,8.8))
  add(x,5,z-2,18,1.3,1.5)
# Solid square caps and small high ventilation openings seen in the upper pediment.
for x in [-49,49]:add(x,11,82.5,9,29,5.5)
cut(0,-2.5,91,4,3,4)
for x in [-21,-7,7,21]:cut(x,-12.5,47,9,2.5,3.5)
# Rear is the plain sectional cutoff, not the actual theatre exterior.
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
solid=solid ^ box(0,0,0,300,300,106.2)
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert str(solid.status())=='Error.NoError' and solid.volume()>0 and len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
