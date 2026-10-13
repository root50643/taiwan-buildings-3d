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
# A039 L-shaped exterior only: exclude adjoining A040 to north and A038 accounting to west.
add(0,0,0,150,116,3)
add(0,28,2.9,136,30,57)
add(51,-5,2.9,34,86,57)
# Upper three framed rows on the court-facing long bar.
for x in [-58,-45,-32,-19,-6,7,20,33]:
 for z in [34,43,52]:recess(x,12.9,z,8.5,5.8,2.6)
# Tall recessed public ground/entrance zone under the upper floors; retain solid back.
for x in [-53,-31,-9,13]:recess(x,12.8,5,15,21,6)
# Entrance projecting portal and two substantial posts, no enclosed interior spaces.
add(21,6,28,31,15,3)
for x in [7,35]:add(x,6,2.9,3.5,10,28)
# Public external stair is coarsened into stout steps and a low curved edge.
for i in range(8):add(-4+i*1.1,4-i*1.0,3+i*1.6,8,8,1.9)
# Brick short-end volume has irregular small openings and one projecting window bay.
for x,z,w,h in [(44,10,6,8),(58,18,3,4.5),(46,29,5,7),(58,39,3,4.5),(47,48,4.5,5),(60,53,3,3)]:recess(x,-48.1,z,w,h,2.6)
add(45,-49,38,15,7,8)
recess(45,-52.6,40,11,4.5,2)
# Long side of short return photographed from campus path; simple external windows.
for y in [-36,-22,-8,6,20,34]:
 for z in [8,20,32,44,53]:cuts.append(box(68.1,y,z,2.4,7,5))
# Back facing adjacent A040 kept plain; no bridging geometry transferred from that model.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
