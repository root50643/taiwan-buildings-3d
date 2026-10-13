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
# Delta Building exterior massing from Delta Foundation's verified public photograph.
add(0,0,0,150,109,3)
# Setback middle facade and projecting end volumes, forming the visible shallow recess.
add(-3,9,2.9,126,61,65)
add(-52,10,2.9,28,66,69)
# Rounded outer corners on the right taller architectural screen.
pts=[]
for cx,cy,aa in [(61,-35,-90),(61,27,0),(38,27,90),(38,-35,180)]:
 for ang in np.linspace(aa,aa+90,9):pts.append((cx+5*np.cos(np.deg2rad(ang)),cy+5*np.sin(np.deg2rad(ang))))
parts.append(C([pts]).extrude(76).translate((0,0,2.9)))
# Long horizontal strips on recessed central frontage.
for zz in [16,26,36,46,56]:
 for xx in [-40,-28,-16,-4,8,20]:recess(xx,-21.6,zz,11.1,3.5,2)
# Narrow slit rhythm on the tall right screen; front and return reveal the corner.
for zz in [17,28,39,50,61,71]:
 recess(49,-40.1,zz,24,4,3.4)
 cuts.append(box(66.1,-17,zz,3.4,19,4))
# Visible left return's long glazing; outer wall on front also gets narrow bands.
for zz in [17,28,39,50,61]:
 recess(-52,-23.1,zz,21,4,2)
 cuts.append(box(-66.1,10,zz,2,45,4))
# Ground floor glazed frontage, simplified into shallow window bays.
for xx in [-55,-41,-27,-13,1,15,29]:recess(xx,-23.1 if xx<-38 else -21.6,5,10,9,2)
add(48,-40,3,18,14,12)
recess(48,-47.1,4,10,9,2)
add(48,-40,14.5,24,17,1.5)
# Roof parapets approximate visible raised rectangular forms; no unseen equipment.
add(-27,11,67,18,19,8)
recess(-27,1.4,70,12,3,2)
# Rear and roof shading geometry not resolved by photograph; no fabricated precision.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
