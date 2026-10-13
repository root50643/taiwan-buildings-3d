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
# Long pool hall along Y with separately articulated low entrance at front.
add(0,0,0,82,150,2.4)
add(0,12,2.3,62,110,25)
# Gabled roof ridge runs along Y; rotate local roof constructed along X.
roof=hull([[-57,-34,26],[-57,34,26],[57,-34,26],[57,34,26],[-57,0,35],[57,0,35]]).rotate((0,0,90)).translate((0,12,0));parts.append(roof)
# Long side windows documented in aerial and side views.
for y in np.arange(-36,65,10):
 for sx in [-1,1]:cut(sx*31.1,float(y),7,1.8,7.4,14)
for sx in [-1,1]:add(sx*31.6,12,16,1.8,108,1.1)
# Lower flat-roof foyer, raised side wall, deep translucent entrance canopy.
add(0,-53,2.3,65,29,20)
add(22,-53,2.3,22,32,28)
add(-15,-67,2.3,32,10,16)
add(-15,-67,18.1,38,15,2)
cut(-15,-72.2,4,26,1.8,12)
for x in [-25,-15,-5]:add(x,-72.1,4,1.2,1.8,12.1)
cut(22,-69.3,4,12,1.8,18)
# Front arch outline is an attached raised semicircular lintel above solid door.
outer=Manifold.cylinder(1.5,7,7,48).rotate((90,0,0)).translate((22,-69,23))
inner=Manifold.cylinder(3,5.7,5.7,48).rotate((90,0,0)).translate((22,-68.5,23))
parts.append((outer-inner)^box(22,-69,23,16,4,9))

solid=Manifold.batch_boolean(parts,OpType.Add)
if cuts:solid=solid-Manifold.batch_boolean(cuts,OpType.Add)
if solid.status().name!='NoError':raise RuntimeError(solid.status())
m=solid.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.apply_scale(150/mesh.extents.max());mesh.apply_translation([0,0,-mesh.bounds[0,2]])
if not mesh.is_watertight or len(mesh.split(only_watertight=False))!=1:raise RuntimeError('Require a single watertight boundary')
mesh.export(OUT/'model.stl');print(mesh.extents.tolist(),len(mesh.faces))
