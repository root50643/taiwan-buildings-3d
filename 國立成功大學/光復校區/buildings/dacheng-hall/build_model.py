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
# One long building, not the entire former military barracks ensemble.
add(0,0,0,150,49,2.8)
add(0,3,2.7,140,29,27.5)
add(0,3,29.9,142,31,1.6)
add(0,3,31.3,142,31,1.0)
# North-facing monumental six-column portico.
add(0,-14,2.7,39,12,1.4)
for i in range(4):add(0,-19.5+i*.8,2.8+i*.35,39,4-i*.6,.5)
for x in [-17,-10.2,-3.4,3.4,10.2,17]:
 add(x,-17,3.9,4,4,2.3)
 parts.append(M.cylinder(23.1,1.55,1.38,32).translate((x,-17,5.8)))
 add(x,-17,28.1,4.1,4.1,1.4)
add(0,-14,29.2,40,12.7,2.2)
parts.append(gable(0,-14,31.3,40,12.7,9))
# Recessed round-top center pediment window.
arcrecess(0,-20.4,32.3,5.5,5.6,1.7)
# Front main wall arcade: shallow relief protects the slender historic openings.
for x in [-63,-54,-45,-36,-27,27,36,45,54,63]:
 arcrecess(x,-11.6,5,7.1,10.7,2.2)
 arcrecess(x,-11.6,19,7.1,10.8,2.2)
 add(x,-12.0,17.4,7.8,1.3,2.1)
# Three arched bays behind the portico.
for x in [-12,0,12]:
 arcrecess(x,-11.6,5,8.5,10.7,2.2)
 arcrecess(x,-11.6,19,8.5,10.8,2.2)
add(0,-12,17.4,38,1.3,2.1)
# Other long facade seen in the university's 2025 photo, simplified rhythm.
for x in [-63,-54,-45,-36,-27,-18,-9,0,9,18,27,36,45,54,63]:
 arcrecess(x,17.6,5,7.1,10.7,2.2)
 arcrecess(x,17.6,19,7.1,10.8,2.2)
 add(x,18.0,17.4,7.8,1.3,2.1)
# Central modest entry on this long facade, not a duplicate monumental portico.
add(0,18,3.5,10,2,14.5)
arcrecess(0,19.1,5,7,10,2)
add(0,18.7,18,11,3,1.2)
for x in [-70,70]:
 for yy in [-6,3,12]:
  for z,h in [(5,10.7),(19,10.8)]:cuts.append(arch(yy,0,z,6.4,h,2.2).rotate((0,0,90)).translate((x,0,0)))

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
