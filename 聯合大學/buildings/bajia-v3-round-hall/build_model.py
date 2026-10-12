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
add(0,0,0,150,135,2.4)
# Two-storey elliptical drum, completely separate from M6 behind it.
parts.append(cyl(0,6,2.3,1,43,112).scale((57,46,1)))
# Core ellipse above accidentally scales placement: use origin-local geometry below.
parts.pop();parts.append(Manifold.cylinder(43,1,1,112).scale((57,46,1)).translate((0,6,2.3)))
# Open roof parapet, united with solid occupied core; no enclosed interior cavity.
outer=Manifold.cylinder(4,1,1,112).scale((58,47,1)).translate((0,6,45))
inner=Manifold.cylinder(6,1,1,112).scale((55.5,44.5,1)).translate((0,6,44.5))
parts.append(outer-inner)
for deg in [-165,-135,-105,-75,-45,-15,15,45,75,105,135,165]:
 t=np.deg2rad(deg);x=57*np.cos(t);y=6+46*np.sin(t);ang=np.degrees(np.arctan2(np.sin(t)/46,np.cos(t)/57))-90
 for z in ([30] if deg == -75 else [9,30]):cuts.append(box(0,0,z,13,2.2,10).rotate((0,0,float(ang))).translate((float(x),float(y),0)))
# Left-side tall rectilinear tower and cap.
add(-32,12,2.3,18,21,68)
add(-32,12,56,20,23,2)
add(-32,12,69.8,17,20,10)
cut(-32,.9,57,10,1.6,10)
# Low square front entrance annex and terrace.
add(18,-41,2.3,40,27,19)
add(18,-41,21,43,29,2)
cut(18,-54.7,4.5,23,1.8,14)
for x in [10,18,26]:add(x,-54.6,4.4,1.2,1.8,14.3)
add(18,-56,18,40,3,2)
# Two external side access stairs rising to second-storey terrace.
stair_y(-59,-30,10,2.4,25,10,22)
stair_y(59,-30,10,2.4,25,10,22)

solid=Manifold.batch_boolean(parts,OpType.Add)
if cuts:solid=solid-Manifold.batch_boolean(cuts,OpType.Add)
if solid.status().name!='NoError':raise RuntimeError(solid.status())
m=solid.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.apply_scale(150/mesh.extents.max());mesh.apply_translation([0,0,-mesh.bounds[0,2]])
if not mesh.is_watertight or len(mesh.split(only_watertight=False))!=1:raise RuntimeError('Require a single watertight boundary')
mesh.export(OUT/'model.stl');print(mesh.extents.tolist(),len(mesh.faces))
