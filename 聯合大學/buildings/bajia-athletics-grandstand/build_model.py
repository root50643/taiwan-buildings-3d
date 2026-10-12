"""Photo-informed NUU exterior miniature. Millimetres, front = -Y.
Proportions are estimates, not survey dimensions. No interior modeled.
Run python build_model.py. See README.zh-TW.md for evidence and limitations.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, OpType, Mesh
OUT=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def cyl(x,y,z,r,h,n=64):return Manifold.cylinder(h,r,r,n).translate((x,y,z))
def hull(points):
 m=trimesh.convex.convex_hull(np.asarray(points));return Manifold(Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
def hip(x,y,z,w,d,rise):
 # Convex hipped roof with a short ridge in the longer direction.
 p=[[x+sx*w/2,y+sy*d/2,z] for sx in [-1,1] for sy in [-1,1]]
 if w>d:p += [[x-(w-d)/2,y,z+rise],[x+(w-d)/2,y,z+rise]]
 else:p += [[x,y-(d-w)/2,z+rise],[x,y+(d-w)/2,z+rise]]
 parts.append(hull(p))
def gable(x,y,z,w,d,rise):
 parts.append(hull([[x+sx*w/2,y+sy*d/2,z] for sx in [-1,1] for sy in [-1,1]]+[[x-w/2,y,z+rise],[x+w/2,y,z+rise]]))
def stair_x(x0,x1,y,z0,z1,width,n=18):
 for i in range(n):
  x=x0+(x1-x0)*(i+.5)/n;h=(z1-z0)*(i+1)/n
  add(x,y,z0-.1,abs(x1-x0)/n+.15,width,h+.1)
def stair_y(x,y0,y1,z0,z1,width,n=18):
 for i in range(n):
  y=y0+(y1-y0)*(i+.5)/n;h=(z1-z0)*(i+1)/n
  add(x,y,z0-.1,width,abs(y1-y0)/n+.15,h+.1)
def beam(a,b,w):
 a=np.array(a);b=np.array(b);v=b-a;length=np.linalg.norm(v)
 m=trimesh.creation.cylinder(radius=w/2,height=length,sections=12);T=trimesh.geometry.align_vectors([0,0,1],v/length);m.apply_transform(T);m.apply_translation((a+b)/2)
 parts.append(Manifold(Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32))))
add(0,0,0,150,88,2.4)
# Solid lower rooms, exterior viewing terrace and rear grandstand.
add(0,5,2.3,104,45,17)
add(0,-19,18.8,111,9,2)
add(0,14,19,104,27,18)
# Open seating recess bounded by end cores; visible stepped terraces.
cut(0,-.5,29,80,15,17)
for i in range(5):add(0,-8+i*3,27+i*1.7,75,3.3,2.2)
# Left rounded stair/side core and right rectangular core.
parts.append(cyl(-47,-6,2.3,10,46))
add(48,-3,2.3,13,30,47)
add(0,26,2.3,106,3,46)
# Broad canopy and three visible shallow upper truss peaks.
add(0,1,49,118,58,2.5)
for x in [-36,0,36]:
 beam((x-18,-23,51),(x,-23,56),1.6);beam((x,-23,56),(x+18,-23,51),1.6)
add(43,19,49,14,15,18)
add(43,19,66.8,18,19,2)
# Long side stairs from foreground up to upper rear, not a smooth ramp.
stair_y(-64,-35,29,2.4,49,12,31)
stair_y(64,-35,29,2.4,49,12,31)
for x in [-64,64]:
 for i in range(31):add(x+( -5.5 if x<0 else 5.5),-35+64*(i+.5)/31,2.3,1.2,2.2,2+46.6*(i+1)/31)
# Lower facade fenestration and attached robust viewing rails.
for x in [-33,-15,3,21,39]:cut(x,-17.8,5,14,1.6,10)
for x in np.arange(-51,52,8):add(float(x),-23,20.6,1.2,1.5,4.2)
add(0,-23,24,106,1.5,1.2)

solid=Manifold.batch_boolean(parts,OpType.Add)
if cuts:solid=solid-Manifold.batch_boolean(cuts,OpType.Add)
if solid.status().name!='NoError':raise RuntimeError(solid.status())
m=solid.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.apply_scale(150/mesh.extents.max());mesh.apply_translation([0,0,-mesh.bounds[0,2]])
if not mesh.is_watertight or len(mesh.split(only_watertight=False))!=1:raise RuntimeError('Require a single watertight boundary')
mesh.export(OUT/'model.stl');print(mesh.extents.tolist(),len(mesh.faces))
