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
# History department, single long former barracks block; six-column entrance.
add(0,0,0,150,66,3)
add(0,0,2.9,140,39,36)
add(0,0,38,142,41,2)
parts.append(hip(0,0,39,139,38,7))
# Continuous two-tier arcaded exterior: deep recesses stop at solid backing wall.
for xx in [-64,-54,-44,-34,-24,24,34,44,54,64]:
 arcrecess(xx,-19.6,7,7,12,7)
 arcrecess(xx,-19.6,24,7.3,11,7)
 add(xx,-19.5,21,7.4,1.2,2.3)
for xx in range(-64,65,10):
 arcrecess(xx,19.6,7,7,12,7)
 arcrecess(xx,19.6,24,7.3,11,7)
 add(xx,19.5,21,7.4,1.2,2.3)
# Main portico: projecting plinth, six tall Tuscan columns and triangular pediment.
add(0,-23,3,39,16,2)
add(0,-23,4.8,36,14,1.7)
for xx in [-16,-9.6,-3.2,3.2,9.6,16]:
 add(xx,-27,6,3.6,3.6,1.7)
 parts.append(M.cylinder(29,1.35,1.2,32).translate((xx,-27,7)))
 add(xx,-27,35,3.4,3.5,1.9)
add(0,-25,36.5,38,12,3)
parts.append(gable(0,-25,39,39,12,10))
parts.append(gable(0,-31.1,40.5,31,1.5,6))
recess(0,-19.6,7,5.5,10,2)
recess(0,-19.6,24,5.5,7,2)
# Two secondary rear balcony portals shown in the rear photographs.
for xx in [-44,36]:
 add(xx,21,19.6,10,5,2)
 for x in [xx-4.6,xx+4.6]:add(x,20.4,5,1.3,2.5,15)
 add(xx,21,21,9.5,1.3,2)
# Short end arcades: five openings per tier, visibly different from the long frontage.
for yy in [-14,-7,0,7,14]:
 for zz,hh in [(7,12),(24,11)]:
  a=arch(0,0,zz,5.3,hh,6).rotate((0,0,90))
  cuts.append(a.translate((-70.1,yy,0)))
  cuts.append(a.translate((70.1,yy,0)))
# Central end balconies and a shallow arched pediment opening.
for xx in [-71,71]:
 add(xx,0,20,4,9,1.4)
 add(xx,0,21,1.2,9,2)
arcrecess(0,-31.85,41,4.6,3.8,1.7)
# Ornament is deliberately simplified, not a facsimile of stone carving.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
