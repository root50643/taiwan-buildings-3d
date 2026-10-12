"""Photo-informed NUU exterior miniature. Millimetres, front = -Y.
Proportions are estimates, not survey dimensions. No interior modeled.
Run python build_model.py. See README.zh-TW.md for evidence and limitations.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, OpType, Mesh, CrossSection
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
# Northern gateway including central booth; one ensemble, not two counted buildings.
add(0,0,0,150,64,2.4)
# Asymmetric end walls and tall name pylon at the right when seen from outside campus.
add(-60,3,2.3,7,23,34)
add(-55,3,2.3,6,21,31)
add(57,4,2.3,12,22,57)
add(56,-8,2.3,19,5,25)
add(64,0,2.3,5,18,25)
# Round paired gate supports.
for x in [-44,40]:
 for y in [-8,12]:parts.append(cyl(x,y,2.2,1.7,32))
# Central glazed booth and its substantial canopy cap.
add(0,-1,2.3,16,20,19)
add(0,-1,21.1,20,24,2)
for y in [-11.2,9.2]:
 cut(0,y,8,13,1.6,10)
for x in [-8.1,8.1]:cut(x,-1,7,1.5,14,11)
# Four columns between booth cap and main gateway canopy.
for x in [-7,7]:
 for y in [-8,8]:add(x,y,22.8,2.3,2.3,11.6)
# Curved plan canopy, shallow coffers with solid bottoms as visible from above.
# Each short segment follows the observed gentle bowed frontage.
def yy(x):return .00125*x*x
def arc_strip(xmin,xmax,ymin,ymax,z,h):
 xs=np.linspace(xmin,xmax,57)
 polygon=[[x,yy(x)+ymin] for x in xs]+[[x,yy(x)+ymax] for x in xs[::-1]]
 parts.append(CrossSection([np.asarray(polygon)]).extrude(h).translate((0,0,z)))
arc_strip(-71,71,-16,16,34,1.5)
for y in [-15,0,15]:arc_strip(-70.5,70.5,y-.85,y+.85,35.2,2.8)
for x in range(-70,71,10):add(x,yy(x),35.3,1.7,31.5,2.7)
# Solid end walls connect to the canopy where circular columns are absent.
add(-62,3,33.3,11,25,2)
add(57,4,33.3,16,25,2)
# Attached, blank architectural name plaques; no invented logo lettering.
add(56,-11,11,16,1.4,4.3)
add(57,-7.2,42,8,1.0,12)
solid=Manifold.batch_boolean(parts,OpType.Add)
if cuts:solid=solid-Manifold.batch_boolean(cuts,OpType.Add)
if solid.status().name!='NoError':raise RuntimeError(solid.status())
m=solid.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.apply_scale(150/mesh.extents.max());mesh.apply_translation([0,0,-mesh.bounds[0,2]])
if not mesh.is_watertight or len(mesh.split(only_watertight=False))!=1:raise RuntimeError('Require a single watertight boundary')
mesh.export(OUT/'model.stl');print(mesh.extents.tolist(),len(mesh.faces))
