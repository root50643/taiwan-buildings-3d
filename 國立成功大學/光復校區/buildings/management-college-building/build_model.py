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
# A040 U-shaped building exterior only. Adjacent A039 south bar is excluded.
add(0,0,0,150,138,3)
# North long bar and two unequal joined returns, matching public exterior outline.
add(0,44,2.9,136,27,57)
add(-48,4,2.9,31,66,57)
add(52,0,2.9,31,112,57)
add(36,3,2.9,23,40,57)
# Strong outer frame and six rows of shallow windows.
for x in range(-60,65,12):
 for z in [7,16,25,34,43,52]:recess(x,57.6,z,7.4,5.5,2.4)
for x in range(-20,33,12):
 for z in [7,16,25,34,43,52]:recess(x,30.4,z,7.4,5.5,2.4)
for y in [-48,-36,-24,-12,0,12,24,36,48]:
 for z in [7,16,25,34,43,52]:cuts.append(box(67.6,y,z,2.4,7.2,5.5))
# West wing courtyard-facing entry with three rounded projecting balcony fronts.
for y in [-21,-10,1,12,23]:
 for z in [7,16,25,34,43,52]:
  if not(-8<y<10):cuts.append(box(-32.4,y,z,2.4,7,5.5))
add(-31,1,2.9,4,20,54)
for z in [27,36,45]:
 # Solid curved balcony slab joined deeply into the existing west wing; thick printable front.
 parts.append(M.cylinder(3,9,9,48).scale((.7,1,1)).translate((-33,1,z)))
 add(-32,1,z,5,18,4.5)
for z in [32,41,50]:cuts.append(box(-28.9,1,z,2.6,12,4.8))
# Round feature above entry, shallow cavity rather than a through-opening.
cuts.append(M.cylinder(2.5,2.4,2.4,32).rotate((0,90,0)).translate((-29.7,1,22)))
cuts.append(box(-28.9,1,6,2.6,13,8))
for i in range(5):add(-25+i*1.2,1,3,3,25-i,1+i*.65)
# Exterior white floor spandrels represented as robust protruding bands, not painted detail.
for z in [14,23,32,41,50]:
 for y in [-21,-10,12,23]:add(-32.4,y,z,1.4,8.6,2.3)
# Roof planar and back/hidden court faces simplified, not surveyed.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
