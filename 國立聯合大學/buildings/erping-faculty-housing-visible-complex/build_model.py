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
add(0,0,0,110,150,2.4)
# Long six-storey housing bar and lower side wing, observable joined grouping.
add(14,7,2.3,41,116,91)
add(-30,-11,2.3,47,61,38)
add(-27,-17,2.3,45,36,21)
# Rounded stair tower at front-right, bands cut as open exterior bays.
parts.append(cyl(34,-46,2.3,15,98))
add(26,-41,2.3,21,21,101)
for row in range(6):
 z=7+row*14.5
 # Recesses stop at solid core, leaving robust rounded balcony bands.
 cuts.append((cyl(34,-46,z,15.6,9)-cyl(34,-46,z-.2,12.8,9.4)) ^ box(45,-46,z-.1,23,35,9.2))
 for x in [2,18]:cut(x,-51.3,z,11,1.6,8)
for y in np.arange(-36,60,17):
 for row in range(6):cut(34.7,float(y),7+row*14.5,1.6,12,8)
# Short side wing and deep stair terraces visible in front.
for x in [-47,-31,-15]:
 for z in [7,25]:cut(x,-41.8,z,11,1.6,10)
add(-30,-43,20,49,6,1.8)
# Broad entry stair and two side flights outside lower wing.
stair_y(10,-68,-52,2.4,8,30,9)
stair_y(-46,-63,-43,2.4,20,11,14)
stair_y(-46,-42,-12,20,39,11,17)
# Roof parapets and three long solar arrays visible in aerial view.
for x in [-5,33]:add(x,7,93,1.7,116,2.3)
for y in [-50,64]:add(14,y,93,40,1.7,2.3)
for x in [1,13,25]:
 add(x,12,93.2,9,90,2.1)
 for y in np.arange(-28,57,9):cut(x,float(y),94.8,10,.7,.9)

solid=Manifold.batch_boolean(parts,OpType.Add)
if cuts:solid=solid-Manifold.batch_boolean(cuts,OpType.Add)
if solid.status().name!='NoError':raise RuntimeError(solid.status())
m=solid.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.apply_scale(150/mesh.extents.max());mesh.apply_translation([0,0,-mesh.bounds[0,2]])
if not mesh.is_watertight or len(mesh.split(only_watertight=False))!=1:raise RuntimeError('Require a single watertight boundary')
mesh.export(OUT/'model.stl');print(mesh.extents.tolist(),len(mesh.faces))
