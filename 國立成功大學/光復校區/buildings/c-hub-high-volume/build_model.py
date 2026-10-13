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
# A042 C-Hub exposed-concrete HIGH VOLUME ONLY; low connector and adjacent old hall omitted.
# The uneven upper edges and flared/folded facades follow public exterior photographs,
# with approximate dimensions rather than measured wall angles.
add(0,0,0,112,94,3)
def loft(lower,upper,top):
 return M.hull_points(np.array([[x,y,2.9] for x,y in lower]+[[x,y,top] for x,y in upper]))
parts.append(loft([(-43,-25),(-9,-17),(-9,26),(-42,28)],[(-50,-32),(-7,-23),(-7,29),(-46,32)],150))
parts.append(loft([(-15,-17),(39,-11),(39,28),(-15,26)],[(-10,-24),(46,-15),(43,32),(-10,29)],136))
# Irregular, non-repeating facade openings, coarsened at miniature size.
for x,z,w,h in [(-37,119,2.4,17),(-26,67,5,8),(-18,98,4,6),(-30,31,4.4,7)]:
 # Deep enough to reach the sloped exterior, never enclosed pockets.
 cuts.append(box(x,-29,z,w,18,h))
for x,z,w,h in [(4,44,13,9),(24,75,10,12),(13,105,6,7),(32,114,4.5,5),(29,36,5,5),(5,85,4,5)]:
 cuts.append(box(x,-21,z,w,18,h))
# Ground glazing sits behind a thick irregular concrete frame; no interior built out.
cuts.append(prism([(-21,4),(25,4),(25,26),(4,22),(-21,13)],19,-20))
# Sparse side windows independently seen in street/oblique photographs.
for y,z,w,h in [(6,82,7,8),(18,55,4.5,6),(5,118,4,5)]:cuts.append(box(44,y,z,17,w,h))
# Plain unverified rear and roof, and no roof installations.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
