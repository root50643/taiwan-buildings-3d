"""Photo-informed exterior miniature. Units mm; no survey precision claimed.
Python 3.12; pip install numpy==2.5.4 trimesh==5.1.1 manifold3d==3.5.4
Run python build_model.py from any working directory. Output beside this file.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold as M, CrossSection as C
OUT=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h):return M.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def prism(points,depth,y):return C([points]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def gable(x,y,z,w,d,h):return prism([(x-w/2,z),(x+w/2,z),(x,z+h)],d,y)
def hip(x,y,z,w,d,h):
 pts=np.array([[x+sx*w/2,y+sy*d/2,z] for sx in [-1,1] for sy in [-1,1]]+[[x-w/2+min(w,d)*.38,y,z+h],[x+w/2-min(w,d)*.38,y,z+h]])
 return M.hull_points(pts)
def arch(x,y,z,w,h,d):
 r=w/2; spring=z+h-r
 pts=[(x-r,z),(x+r,z)]+[(x+r*np.cos(t),spring+r*np.sin(t)) for t in np.linspace(0,np.pi,25)]
 return prism(pts,d,y)
def disk(x,y,z,r,d):return M.cylinder(d,r,r,48).rotate((90,0,0)).translate((x,y+d/2,z))
def recess(x,y,z,w,h,d=1.6):cuts.append(box(x,y,z,w,d,h))
def arcrecess(x,y,z,w,h,d=1.6):cuts.append(arch(x,y,z,w,h,d))
# Science south / physics high wing; shared low entrance and north wing excluded.
add(0,0,0,150,132,3)
# L-shaped mass framing the banyan court, read from external map and aerial photo.
add(0,-29,2.9,132,40,109)
add(45,6,2.9,42,94,109)
# Five upper staggered projecting deep sunshade boxes. Solid backing, no interiors.
patterns=[
 (46,[(-48,25),(-14,34),(21,26),(50,25)]),
 (59,[(-51,19),(-24,29),(10,35),(48,30)]),
 (72,[(-47,31),(-12,28),(19,24),(48,28)]),
 (85,[(-53,18),(-27,29),(8,35),(46,34)]),
 (98,[(-46,34),(-8,34),(27,29),(54,17)])]
for row,(z,bays) in enumerate(patterns):
 for j,(xx,w) in enumerate(bays):
  add(xx,-51,z,w,7,11.5)
  # Unequal, offset frame widths are a defining observed facade feature.
  recess(xx,-54.6,z+1.4,w-8,8.4,4)
  # One or two thickened louvre strips, not a repeated uniform window array.
  sides=[-1,1] if (row+j)%2==0 else [1]
  for side in sides:
   for dz in [2,3.8,5.6,7.4,9.2]:add(xx+side*(w/2-2.5),-55,z+dz,3.5,1.5,.8)
# Three lower storeys; podium at left as seen, without shared connecting pavilion.
add(-37,-51,2.9,44,13,31)
for z in [8,21]:
 for x in [-50,-37,-24]:recess(x,-57.6,z,6,8,2)
for z in [7,20,33]:
 for x in [2,17,32,47,60]:recess(x,-49.1,z,7,8.8,2.1)
# Main flat entrance canopy joins main wall and podium.
add(2,-56,18.5,45,18,1.8)
# The photographed court face: regular punched apertures, not staggered boxes.
for z in [8,21,34,47,60,73,86,99]:
 for x in [-55,-43,-31,-19,-7,5,17]:recess(x,-8.9,z,5.7,8.2,2)
 for yy in [-1,11,23,35,47]:cuts.append(box(23.9,yy,z,2,5.7,8.2))
# Short northern end has a central vertical glazing slit and sparse end windows.
for z in [12,25,38,51,64,77,90,103]:recess(45,53.1,z,5,8.5,1.8)
for x in [32,38]:recess(x,53.1,63,4,8,1.8)
add(35,15,111,27,28,8)
# Unseen outer return is plain; rooftop equipment omitted.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
