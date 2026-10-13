"""Original photo-based 國立虎尾科技大學經國體育館正面入口段. Millimetres.
Partial facade only: cut depth 20mm is illustrative, not a surveyed full gym.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, OpType
OUT=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
add(0,0,0,150,62,3)
# Rear cut plane is intentionally blank: this is not the unseen rear elevation.
add(0,12,2.8,140,20,68)
# Main facade side buttresses, observed flanking recessed window bands.
for x in [-61,61]:add(x,-1,2.8,13.5,10,66.5)
# Tall front face of upper gym volume, with three actual glazing strips.
# 28 top lights; 27 lower lights; tall main panes plus transoms in middle band.
for z,h,n in [(61.7,3.0,28),(47.6,3.1,27),(43.6,2.7,27)]:
 lo=-51.0;hi=51.0; pitch=(hi-lo)/n
 for i in range(n):cut(lo+(i+.5)*pitch,2.1,z,pitch-1.15,3.0,h)
# Front roof fascia and source-visible short cantilever ribs.
add(0,5,69.1,146,34,3.3)
for x in [-70,-48,-32,-16,0,16,32,48,70]:add(x,-4,65.0,1.5,12,4.7)
# Projecting entrance canopy, open underneath, supported by two main columns.
add(0,-8.5,31.5,136,31,3.2)
add(0,-23.1,33.5,136,2.8,7.0)
for x in [-18.5,18.5]:add(x,-14.0,9.4,3.4,3.8,22.5)
# Entrance glass is recessed, grouped by door openings, not painted on.
for lo,hi in [(-53,-23),(-16,16),(23,53)]:
 for i in range(5):
  p=(hi-lo)/5;cut(lo+(i+.5)*p,2.0,10.0,p-1.2,3,16.3)
# Taller door transom and solid mullion spine are retained in geometry.
for x in [-44,-32,0,32,44]:add(x,.7,9.7,1.3,2.1,16.8)
add(0,.5,23.3,108,2.8,1.3)
# Raised arrival terrace and nine visible broad stair risers.
add(0,-6.25,2.8,135,18.5,7.0)
for x in [-60,60]:add(x,-20.5,2.8,24,11,7.0)
for i in range(9):add(0,-28.2+i*1.5,2.8,88,1.8,.78*(i+1))
# Four sloping stair cheekwalls simplified to stepped solid parapets.
for x in [-46.5,-20.5,20.5,46.5]:
 for i in range(9):add(x,-28.2+i*1.5,2.8,1.8,1.85,2.0+.78*(i+1))
# Side balcony arrival parapets, stout for printing rather than thin rail rods.
for x in [-59,59]:add(x,-24.0,9.5,16,1.4,3.2)
# Union additions before cutting recesses: openings leave back wall, no inner shell.
solid=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
assert solid.status().name=='NoError';assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.volume,len(mesh.faces),mesh.is_watertight)
