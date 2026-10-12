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
  for xx in np.arange(-w/2+1,w/2,2.6):path([[x+xx,y+yy,zz(xx,yy)-.15] for yy in np.linspace(-d/2,d/2,21)],.40)
 path([[x+xx,y,zz(xx,0)+.45] for xx in np.linspace(-w/2,w/2,25)],.85)
 # Short, substantial swallowtail ends continue naturally from the roof ridge.
 for side in [-1,1]:
  points=[[x+side*(w/2-3),y,eave+rise+up*.6],[x+side*w/2,y,eave+rise+up],[x+side*(w/2+1),y,eave+rise+up+2.6]];path(points,1.1)
def finish():
 body=m.Manifold.batch_boolean(parts,m.OpType.Add)
 if cuts:body=body-m.Manifold.batch_boolean(cuts,m.OpType.Add)
 assert body.status()==m.Error.NoError,body.status()
 body=body.as_original().set_tolerance(.02).simplify(.02)
 mm=body.to_mesh();tm=trimesh.Trimesh(vertices=mm.vert_properties[:,:3],faces=mm.tri_verts,process=True)
 # Resolve sub-micron Boolean intersection slivers before binary STL quantization.
 tm.merge_vertices(digits_vertex=5);tm.update_faces(tm.unique_faces());tm.update_faces(tm.nondegenerate_faces(height=1e-7));tm.remove_unreferenced_vertices()
 assert tm.is_watertight and tm.is_winding_consistent
 a.output.parent.mkdir(parents=True,exist_ok=True);tm.export(a.output)
 print(a.output.name,'triangles',len(tm.faces),'dimensions',tm.extents.tolist(),'watertight',tm.is_watertight,'euler',tm.euler_number)
# Penghu Tianhou Temple. Three halls and TWO open courts, rising back uphill.
# Front photograph: polygonal stairs; three-bay entrance; low side pediments.
add(0,0,1.5,110,150,3)
# Three ascending landscape levels, no sealed voids beneath the halls.
add(0,6,5,100,125,4.2)
add(0,22,7,100,94,4.2)
add(0,48,9,100,42,4.2)
# Multi-angled stair apron, a specific characteristic of this temple.
for j in range(5):
 w=88-j*6;front=-71+j*2.7;back=-48.0;ch=8
 pts=[[-w/2+ch,front],[w/2-ch,front],[w/2,front+ch],[w/2,back],[-w/2,back],[-w/2,front+ch]]
 parts.append(m.CrossSection([pts]).extrude(1.0+j*1.2).translate((0,0,3)))
# Front three-bay hall is intentionally recessed between robust square columns.
add(0,-40,16.5,62,22,21)
for xx in [-27,-10,10,27]:add(xx,-52,16,2.3,2.3,20)
add(0,-52,25.5,59,2.5,2.0)
# All portals are open surface niches. We do not reconstruct interior worship space.
for xx,w in [(-19,12),(0,13),(19,12)]:cuts.append(box(xx,-52.6,15.3,w,8.5,14.5))
# Doors, lintel, and carved panel rhythm simplified as merged relief.
for xx in [-10,10]:add(xx,-52.6,17,1.6,1.3,16)
add(0,-53.0,24.1,15,.8,2.3)
# Three roof sections: raised central bay and two slightly lower side bays.
curve_roof(0,-40,25,28,27.5,8.5,4.2)
for sx in [-1,1]:curve_roof(sx*23.5,-40,22,28,26.4,7.0,3.5)
# Low protective front wings flank the main portico; gable-like wavy parapets.
for sx in [-1,1]:
 xx=sx*42;add(xx,-37,15.5,16,29,19)
 curve_roof(xx,-36,18,28,24.7,5.0,1.8,False)
 cuts.append(arch(5.6,12,3).translate((xx-sx*3,-52.7,6)))
 # front panel frames and lattice represented as shallow relief, not perforation.
 add(xx+sx*3,-51.7,15,5.7,1.0,9)
 for zz in [12.5,15,17.5]:cuts.append(box(xx+sx*3,-52.0,zz,3.8,1.1,.75))
 # curved pediment facing front, matching the low side gables in official photos.
 ridge=[]
 for t in np.linspace(-1,1,17):ridge.append([xx+t*8,-52,25+4.5*(1-abs(t))**2])
 path(ridge,.9)
 ring_y(xx,-52.0,26,1.5,.7,1)
# Side protective halls connect all three primary halls but leave courtyards open.
for sx in [-1,1]:
 add(sx*43,13,18,14,94,24)
 # Short intersecting side-roof sections with a visible roofline at each court.
 for yy,dep,zz in [(-13,24,26),(21,28,28),(50,27,32)]:
  # Ridge direction along the depth of temple.
  before=len(parts);curve_roof(0,0,dep,18,zz,4.8,1.4,False)
  for q in range(before,len(parts)):parts[q]=parts[q].rotate((0,0,90)).translate((sx*43,yy,0))
 # White side-wall vertical relief panels, conservative exterior rhythm.
 for yy in [-36,-18,1,20,39,56]:
  cuts.append(box(sx*50.1,yy,17.5,1.1,7.0,10))
# Main sanctuary, taller than the entrance but lower than two-storey Qingfeng pavilion.
add(0,4,22,70,31,28)
curve_roof(0,4,77,37,35,10.0,4.0)
for xx in [-24,-12,0,12,24]:cuts.append(box(xx,-12,22,7.6,3.0,14))
for xx in [-30,-18,-6,6,18,30]:add(xx,-12.0,23.0,1.6,1.1,17)
# Second courtyard rises to the rear pavilion; steps run across its center.
for j in range(4):add(0,27.3+j*1.8,9.2+j*.6,35,2.1,1.8+j*1.2)
# Qingfeng pavilion: two-storey rear building with strong upper window rhythm.
add(0,52,27,87,23,36.2)
add(0,52,28.7,89,24,1.3)
curve_roof(0,52,93,29,44.5,8.0,2.7)
for yy in [39.8,64.0]:
 for xx in [-34,-22,-11,0,11,22,34]:
  cuts.append(box(xx,yy,34.8,5.4,2.0,8))
  cuts.append(box(xx,yy,18.5,5.4,2.0,9))
# Ridge crests are restrained continuous relief; fine dragon limbs are omitted.
finish()
