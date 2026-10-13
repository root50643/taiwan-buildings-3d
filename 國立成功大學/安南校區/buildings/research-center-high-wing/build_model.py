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
# Higher wing only, from architect's exterior views 2/4. Not the complete complex.
add(0,0,0,150,72,3)
add(-4,2,2.9,127,44,66)
# Six principal facade tiers and the taller stepped west-end mass.
add(-45,2,68.5,36,44,12)
add(-3,2,68.5,48,44,5.5)
add(44,8,68.5,12,19,7)
# Openly recessed facade bays, not interior rooms.
for zz in [7,17,27,37,47,57]:
 for xx in [-54,-42,-30,-12,0,12,25,37,49]:recess(xx,-20.1,zz,9.3,6.6,2.6)
# Full-height alternating solid bands and deeper projecting end frame.
for xx in [-61,-25,17,56]:add(xx,-21,3,2.2,3,66)
for zz in [17,27,37,47,57,67]:add(-3,-21.3,zz-1.2,124,3.8,1.2)
recess(-42,-20.1,72,7,4,2)
recess(-4,-20.1,68,24,3.5,2)
# End elevation apertures visible in architect's corner image.
for zz in [9,22,35,48,61]:cuts.append(box(-67.6,3,zz,2,16,7))
# Inner-facing elevation partly evidenced; simplified repeated shallow bands.
for zz in [7,17,27,37,47,57]:
 for xx in [-48,-29,-10,9,28,47]:recess(xx,24.1,zz,14,6.4,1.6)
# No joining bridges, low wing or shared curved canopy in this component model.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
