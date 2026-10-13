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
# Uni-President Health Research Building; public exterior jointly used by NCKU/NHRI.
add(0,0,0,150,142,3)
# Main mass: gently rounded front, rectangular long returns, attached low entrance.
add(0,6,2.9,111,85,99)
# Rounded eastern face rotated to face preview front; no equipment on roof.
parts.append(M.cylinder(99,38,38,64).scale((1,0.46,1)).translate((0,-36,2.9)))
add(-45,-33,2.9,21,47,103)
add(45,-33,2.9,21,47,103)
# Seven front levels: recessed window strips follow the cylinder arc.
for z in [9,22,35,48,61,74,87]:
 for ang in [-56,-28,0,28,56]:
  a=np.deg2rad(ang);xx=38*np.sin(a);yy=-36-17.48*np.cos(a)
  # Tangent-facing short recesses approximate the curved glazing ribbon.
  cut=box(0,0,z,11,2.8,7.7).rotate((0,0,-ang*.46)).translate((xx,yy,0));cuts.append(cut)
# Main long-side punched openings; top row is recessed blind panels, same shallow depth.
for z in [9,22,35,48,61,74,87]:
 for yy in [-13,1,15,29,41]:
  if not (z in [9,22] and yy in [1,15,29]):cuts.append(box(-55.6,yy,z,2.5,7.3,8.2))
  cuts.append(box(55.6,yy,z,2.5,7.3,8.2))
# Attached two-storey entry block off the side, evident in aerial/ground views.
add(-61,15,2.9,17,39,29)
recess(-61,-4.6,8,10,12,2)
add(-61,-9,21,20,13,1.6)
# Roof oval parapet visible in oblique aerial; details consolidated and simplified.
outer=M.cylinder(3.6,34,34,64).scale((1,.42,1)).translate((0,-30,101.4))
inner=M.cylinder(5,31,31,64).scale((1,.42,1)).translate((0,-30,101.3))
parts.append(outer-inner)
add(0,25,101,40,28,5)
# Rear not clearly photographed: keep plain rather than invent service installations.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
