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
# Dongyong (Dongyin Island) Lighthouse: contemporary public exterior and a
# cropped, approximate cliff terrace. No military facilities or interior rooms.
# Flat display footprint with chamfered corners, exactly 150 mm across.
foot=[[-75,-42],[-68,-50],[64,-50],[75,-39],[75,42],[65,50],[-66,50],[-75,40]]
parts.append(m.CrossSection([foot]).extrude(3))
# Abstracted rocky cliff rises toward the inland stair path at right/rear.
parts.append(hull([[-65,-32,2.6],[-12,-44,2.6],[61,-31,2.6],[68,40,2.6],[-49,43,2.6],[-59,-26,8],[-8,-24,12],[49,12,27],[54,38,33],[-26,30,18]]))
# Small faceted rock shoulders; coarse original terrain, not a surveyed coastline.
for xx,yy,zz,ww,hh in [(49,-17,8,20,14),(15,-29,6,21,9),(-48,15,8,20,12),(26,31,16,22,12)]:
 parts.append(hull([[xx-ww/2,yy-7,2.5],[xx+ww/2,yy-8,2.5],[xx+ww/2,yy+8,2.5],[xx-ww/2,yy+8,2.5],[xx-ww/3,yy-4,zz+hh],[xx+ww/4,yy+3,zz+hh-2]]))
x=-32;y=-15
# Foundation terrace and a curved low parapet seen at the tower foot.
parts.append(cyl(x,y,3,22,8))
parts.append(cyl(x,y,10.5,22,1.5))
# Low perimeter ring with a broad landward gap toward the stair and doorway.
wall=cyl(x,y,12,21.5,4)-cyl(x,y,11.5,20.2,6)
wall=wall-box(x+19,y,14,24,22,9);parts.append(wall)
# White cylinder: broad base, plain tall shaft, corbelled circular gallery.
parts.append(cyl(x,y,10.8,14.6,2.0));parts.append(cyl(x,y,12.4,13.5,44.6))
parts.append(cyl(x,y,55.5,13.5,4.5,17.3));parts.append(cyl(x,y,59,17.5,2.3))
parts.append(cyl(x,y,61,17.7,1.5))
# Low square entrance vestibule attached on inland (right) side.
add(x+15.5,y,21.6,10,12,20)
add(x+15.5,y,32,11,13,1.4)
cuts.append(box(x+21,y,22.6,3,5.3,10.5))
# Conservative tower slit windows, shallow exterior niches only.
for ang,z in [(0,29),(180,43),(90,34)]:
 cut=box(0,-13.5,z,3.2,2.2,6.3).rotate((0,0,ang)).translate((x,y,0));cuts.append(cut)
# Lower lantern drum with porthole service door, then the taller glazed lantern.
parts.append(cyl(x,y,62.2,10.8,13.3))
parts.append(cyl(x,y,75.1,13.3,1.2))
parts.append(cyl(x,y,76,10.6,15.5))
parts.append(cyl(x,y,91,11.6,1.2))
# Window mullions are shallow relief on a solid drum; glass openings are not voids.
for k in range(12):
 angle=2*math.pi*k/12
 parts.append(cyl(x+10.55*math.cos(angle),y+10.55*math.sin(angle),76,.53,15.7,n=12))
# Raised glazing sill ring and central horizontal frame line.
for z in [76.4,83,90.8]:parts.append(cyl(x,y,z,10.9,.65))
add(x,y-10.5,69.1,6,1.7,10)
for xx in [-1.6,1.6]:cuts.append(m.Manifold.cylinder(2,0.72,.72,24).rotate((90,0,0)).translate((x+xx,y-10.1,71.4)))
# Black flared domed roof outline, approximated by a smooth revolved profile.
profile=[[0,0],[11.7,0],[11.1,1.6],[10.1,3.5],[8.5,5.7],[6.4,7.6],[4.7,8.4],[4.7,11],[4.9,11.5],[0,11.5]]
parts.append(m.CrossSection([profile]).revolve(96).translate((x,y,92)))
# Robust single finial stands in for the delicate weather vane, no false arrow.
parts.append(cyl(x,y,103.3,1.05,4.3,.7,n=24));parts.append(ball(x,y,107.6,.7))
# Gallery rails thickened for FDM; real open spacing retained, all tied to deck.
# 16 posts and two fused annular handrails. This creates intentional through-holes.
for k in range(16):
 angle=2*math.pi*k/16;xx=x+16.1*math.cos(angle);yy=y+16.1*math.sin(angle)
 parts.append(cyl(xx,yy,61.9,.72,8.0,n=16));parts.append(ball(xx,yy,70,.86))
for zz in [65.2,69.0]:parts.append(cyl(x,y,zz,16.65,1.0)-cyl(x,y,zz-.2,15.55,1.4))
# Stair descends from the hillside toward the tower. White solid sidewalls follow it.
start=-9;end=54;z0=12.0;rise=23.0;n=18
for j in range(n):
 xx=start+(end-start)*(j+.5)/n;top=z0+rise*(j+1)/n
 add(xx,y,(top+2.7)/2,(end-start)/n+.08,10,top-2.7)
 for sy in [-1,1]:add(xx,y+sy*5.5,(top+5+2.7)/2,(end-start)/n+.12,1.3,top+5-2.7)
# Inland landing, cropped deliberately rather than inventing unverified house layout.
add(58,y,18.5,11,13,31.6)
add(64,y,38.0,1.5,14,7.5)
finish()
