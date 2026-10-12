from pathlib import Path
import argparse, math
import numpy as np
import manifold3d as m
import trimesh
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=HERE/'model.stl');a=p.parse_args()
parts=[];cuts=[]
def box(x,y,z,w,d,h):return m.Manifold.cube((w,d,h),True).translate((x,y,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def hull(pts):return m.Manifold.hull_points(pts)
def cyl(x,y,z,r,h,r2=None,n=64):return m.Manifold.cylinder(h,r,r if r2 is None else r2,n).translate((x,y,z))
def ball(x,y,z,r):return m.Manifold.sphere(r,12).translate((x,y,z))
def path(pts,r):
 for aa,bb in zip(pts,pts[1:]):parts.append(m.Manifold.batch_hull([ball(*aa,r),ball(*bb,r)]))
def ring_y(x,y,z,r,thick=0.9,depth=.9):
 outer=m.Manifold.cylinder(depth,r,r,40).rotate((90,0,0)).translate((x,y+depth/2,z));inner=m.Manifold.cylinder(depth+2,r-thick,r-thick,40).rotate((90,0,0)).translate((x,y+depth/2+1,z));parts.append(outer-inner)
def arch(w,h,depth):
 r=w/2;pts=[[-r,0],[r,0]]+[[r*math.cos(t),h-r+r*math.sin(t)] for t in np.linspace(0,math.pi,17)]
 return m.CrossSection([pts]).extrude(depth).rotate((90,0,0)).translate((0,depth,0))
def gable(x,y,w,d,eave,rise):
 pts=[[x+xx,y+yy,z] for xx in [-w/2,w/2] for yy in [-d/2,d/2] for z in [eave-1.5,eave]]+[[x-w/2,y,eave+rise],[x+w/2,y,eave+rise]]
 parts.append(hull(pts))
def curve_roof(x,y,w,d,eave,rise,up=2.5,tiles=True):
 # Solid closed swept roof, with print-thickened eaves and supported curved ridge.
 nx=24;ny=20;xs=np.linspace(-w/2,w/2,nx+1);ys=np.linspace(-d/2,d/2,ny+1);v=[];f=[]
 def zz(xx,yy):return eave+rise*(1-abs(yy)/(d/2))**1.75+up*(abs(xx)/(w/2))**7
 for level in [0,1]:
  for xx in xs:
   for yy in ys:v.append([x+xx,y+yy,(eave-1.8 if level==0 else zz(xx,yy))])
 n=(nx+1)*(ny+1)
 for i in range(nx):
  for j in range(ny):
   q=i*(ny+1)+j;r=q+ny+1
   f.extend([[n+q,n+r,n+r+1],[n+q,n+r+1,n+q+1],[q,r+1,r],[q,q+1,r+1]])
 boundary=[i*(ny+1) for i in range(nx+1)]+[nx*(ny+1)+j for j in range(1,ny+1)]+[i*(ny+1)+ny for i in range(nx-1,-1,-1)]+[j for j in range(ny-1,0,-1)]
 for aa,bb in zip(boundary,boundary[1:]+boundary[:1]):f.extend([[aa,bb,n+bb],[aa,n+bb,n+aa]])
 tm=trimesh.Trimesh(vertices=v,faces=f,process=True);tm.fix_normals();parts.append(m.Manifold(m.Mesh(np.asarray(tm.vertices,dtype=np.float32),np.asarray(tm.faces,dtype=np.uint32))))
 # Tile crests and ridge are fused into the same surface; no loose strips.
 if tiles:
  for xx in np.arange(-w/2+1,w/2,2.6):path([[x+xx,y+yy,zz(xx,yy)-.15] for yy in np.linspace(-d/2,d/2,13)],.40)
 path([[x+xx,y,zz(xx,0)+.45] for xx in np.linspace(-w/2,w/2,25)],.85)
 # Short, substantial swallowtail ends continue naturally from the roof ridge.
 for side in [-1,1]:
  points=[[x+side*(w/2-3),y,eave+rise+up*.6],[x+side*w/2,y,eave+rise+up],[x+side*(w/2+1),y,eave+rise+up+2.6]];path(points,1.1)
def finish():
 body=m.Manifold.batch_boolean(parts,m.OpType.Add)
 if cuts:body=body-m.Manifold.batch_boolean(cuts,m.OpType.Add)
 assert body.status()==m.Error.NoError,body.status()
 body=body.as_original().set_tolerance(.005).simplify(.005)
 mm=body.to_mesh();tm=trimesh.Trimesh(vertices=mm.vert_properties[:,:3],faces=mm.tri_verts,process=True)
 a.output.parent.mkdir(parents=True,exist_ok=True);tm.export(a.output)
 print(a.output.name,'triangles',len(tm.faces),'dimensions',tm.extents.tolist(),'watertight',tm.is_watertight,'components',len(tm.split(only_watertight=False)))
# Deyue tower only. Proportions checked against the 2025 restoration photo.
# Model is an original solid exterior miniature, not surveyed conservation CAD.
add(0,0,2,70,68,4)
add(0,0,8,47,44,8.2)
add(0,0,72,43,40,120.2)
# The notably large almost blank lower field is retained, not filled with fake windows.
for z,w,d,h in [(14,46,43,2.2),(17,45.5,42.5,1.1),(92,46,43,1.8),(94,45,42,1.0),(130,47,44,2.3)]:add(0,0,z,w,d,h)
for sx in [-1,1]:
 for sy in [-1,1]:add(sx*20,sy*18.5,72.7,3.2,3.1,115.5)
# Overhanging roof with bevelled corners and robust corbels.
pts=[[xx,yy] for xx,yy in [(-25,-19),(-21,-24),(21,-24),(25,-19),(25,19),(21,24),(-21,24),(-25,19)]]
plate=m.CrossSection([pts]).extrude(4).translate((0,0,132));parts.append(plate)
for ang in [0,90,180,270]:
 for xx in [-15,15]:parts.append(hull([[xx-1.8,-20,125],[xx+1.8,-20,125],[xx-1.8,-24,132.3],[xx+1.8,-24,132.3],[xx-1.8,-18,132.3],[xx+1.8,-18,132.3]]).rotate((0,0,ang)))
add(0,0,136.1,49,47,1.3)
# Roof terrace is shallow and open to sky, no sealed internal cavity.
for sy in [-1,1]:add(0,sy*22,140,48,3.0,7)
for sx in [-1,1]:add(sx*23,0,140,3.0,42,7)
# Characteristic low crenels with small observation recesses.
for ang in [0,90,180,270]:
 for xx in [-20,-13,-6,6,13,20]:
  parts.append(box(xx,-22,145.8,4.8,3.0,8.4).rotate((0,0,ang)))
  cuts.append(box(xx,-23.6,143.5,2.0,1.5,2.1).rotate((0,0,ang)))
# Raised front stone name tablet (left blank at this scale, no false lettering).
add(0,-23.0,145,14.8,2.7,10)
add(0,-24.1,145,12.2,.8,7.5)
# Surface openings: two upper-front square lookout niches and circular gun ports.
for ang,levels in [(0,[82,113]),(180,[50,82,113]),(90,[113]),(270,[113])]:
 for z in levels:
  parts.append(box(0,-20.4,z,8.5,1.8,7.4).rotate((0,0,ang)))
  cuts.append(box(0,-21.4,z,4.9,4,4.8).rotate((0,0,ang)))
  for xx in [-12,12]:
   outer=m.Manifold.cylinder(1.5,2.6,2.6,32).rotate((90,0,0)).translate((xx,-19.8,z));parts.append(outer.rotate((0,0,ang)))
   cut=m.Manifold.cylinder(3.5,1.4,1.4,32).rotate((90,0,0)).translate((xx,-19.0,z));cuts.append(cut.rotate((0,0,ang)))
# Curled eyebrow lintels on the front, attached bas relief rather than floating art.
for z in [88.4,119.5]:
 path([[float(x),-20.65,z+2.2*math.cos(float(x)*math.pi/13)**2] for x in np.linspace(-13,13,41)],.9)
add(0,20.2,20,6.8,1.5,9)
cuts.append(box(0,21,19.5,4.6,3,7.4))
# Base coursing is shallow; the four visible facades remain solid.
for z in [5.3,7.7,10.1]:
 for sy in [-1,1]:cuts.append(box(0,sy*22.0,z,46,.5,.35))
finish()
