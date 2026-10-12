"""國衛院竹南行政大樓：公開照片推估之外觀展示模型，非測繪復刻。Units mm."""
from pathlib import Path
import math,json
import numpy as np
import trimesh
from manifold3d import Manifold
OUT=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def tf(p,cx,cy,angle):return p.rotate((0,0,angle)).translate((cx,cy,0))
def wing(cx,cy,w,d,h,angle=0,solid_end=5):
 # Three principal facade masses follow the gently bent public-map footprint.
 local=[];neg=[]
 local.append(box(0,0,2.4,w,d,h))
 local.append(box(0,0,2.4+h-.6,w+1.0,d+1.0,1.2))
 # Upper continuous stone margin above grid of recessed windows.
 # Four upper rows above the publicly visible ground-storey colonnade.
 n=max(4,round((w-2*solid_end)/6.4));pitch=(w-2*solid_end)/n
 for side in [-1,1]:
  for i in range(n):
   x=-w/2+solid_end+pitch*(i+.5)
   for j in range(4):
    z=10+j*6.1
    if z+4.5<2.4+h-2:
     neg.append(box(x,side*d/2,z,pitch-1.25,1.1,4.5))
  # Continuous sills/ribs survive FDM, actual integral shallow relief.
  for z in [9.1,15.2,21.3,27.4,33.5]:
   if z<2.4+h-1.4: local.append(box(0,side*(d/2+.25),z,w-2*solid_end,.7,.8))
 for yy in [-4,2,8]:
  if cx < -40 and abs(yy)<d/2-2:
   for z in [10,16.1,22.2,28.3]:
    if z+4<2.4+h-3:neg.append(box(-w/2,yy,z,1.1,3.1,4))
 for p in local:parts.append(tf(p,cx,cy,angle))
 for p in neg:cuts.append(tf(p,cx,cy,angle))
 # North-side low stone colonnade. Small true bridges, thick piers.
 for x in np.arange(-w/2+2,w/2-1,6.1):
  parts.append(tf(box(x,-d/2-3,2.35,1.6,1.8,7.8),cx,cy,angle))
 parts.append(tf(box(0,-d/2-3,9.2,w,2.1,1.1),cx,cy,angle))
 # Gallery pavement bonds the piers to the shared base.
 parts.append(tf(box(0,-d/2-1.5,2.3,w+1,6.2,.65),cx,cy,angle))
add(0,0,0,150,56,2.4)
# Main long bar: lower western bay, prominent middle block, short eastern wing.
wing(-46,2,43,23,32,0,4)
wing(-1,2,49,24,37,0,5)
wing(46,-1.2,43,23,33,-8,4)
# Recessed connecting seam: front glazing between the high masses.
add(24,-.1,2.35,5,21,30.5)
for z in np.arange(5,31,3):cuts.append(box(24,-10.6,z,3.2,1.1,2.1))
# Higher blank wall on middle left edge and descending roof silhouette.
add(-23,2,2.35,3.6,24.6,40.4)
parts.append(Manifold.hull_points([[-23,-10,39],[-23,14,39],[23,-10,35],[23,14,35],[-23,-10,41.6],[-23,14,41.6],[23,-10,37.6],[23,14,37.6]]))
# Entrance marker and short shallow steps, not landscaping or internal circulation.
add(-8,-11.1,2.35,9,1.1,7.5)
for x in [-10,-6]:cuts.append(box(x,-11.7,3.1,2.7,1.0,5.9))
add(-8,-12,9.0,11,2.0,1.1)
for i in range(3):add(-8,-14-i*1.1,2.35,13,1.2,1.2-i*.3)
# Conservative plain low roof boxes; no security/mechanical details.
add(-1,5,38.5,10,8,2.0)
shape=Manifold.batch_boolean(parts,0)
shape=shape-Manifold.batch_boolean(cuts,0)
mesh=shape.to_mesh()
tm=trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:,:3],faces=np.asarray(mesh.tri_verts),process=True)
tm.export(OUT/'model.stl');tm.export(OUT/'model.obj')
print('Built',tm.extents,len(tm.faces),'watertight',tm.is_watertight)
