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
# Taiwan Literature lecture hall E107 / GIS E007, former hall035.
add(0,0,0,150,110,3)
add(0,1,2.9,130,75,36)
parts.append(gable(0,0,38,81,138,22).rotate((0,0,90)))
# Tall glazed central bays and end door rhythm observed in two restored exterior photos.
for x in [-52,-20,-9,2,13,24,52]:
 for dx in [-3,0,3]:
  for z in [8,12.8,17.6,22.4,27.2]:recess(x+dx,-36.6,z,2.1,3.7,1.8)
# Wider glass frontage lies under a shallow continuous secondary eave.
# Roof slab cross section in y,z, then rotate about z so it runs along x.
parts.append(prism([(-43,31),(-36,34),(-36,35.6),(-43,32.6)],118,0).rotate((0,0,90)))
# Main exposed left end: tall corner window and high gable vent.
for yy in [-19]:
 for dy in [-3.6,0,3.6]:
  for z in [10,15,20,25,30]:cuts.append(box(-65.1,yy+dy,z,1.8,2.6,4))
for yy in [-2,1,4]:cuts.append(box(-69.1,yy,44,1.8,1.7,7))
# Timber siding relief simplified as shallow bands only on the photographed gable end.
for z in [9,14,19,24,29,34]:add(-65.4,0,z,1,73,.65)
# Low exterior base, broad front steps and two solid piers.
for z,w,d,yy in [(3,85,15,-42),(4.5,79,11,-40),(6,72,7,-38)]:add(0,yy,z,w,d,1.6)
for xx in [-36,37]:add(xx,-37,3,3,4,29)
# Small mapped end projection, kept plain and distinct from nearby red-brick buildings.
add(-67,25,2.9,9,21,24)
parts.append(gable(-67,25,26,11,23,6))
# Rear windows and detailed ridge ornaments unverified and omitted.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
