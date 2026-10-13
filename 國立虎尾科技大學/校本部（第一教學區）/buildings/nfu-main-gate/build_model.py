"""Original NFU existing main gate and guardhouse exterior study.
2025 admissions photos and official gallery. Approximate mm; no adjacent teaching tower.
Back of guardhouse is an explicitly simplified unseen elevation. Tiger sculpture excluded.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, OpType, Mesh64
OUT=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def curved_wall(cx,cy,r,thick,a0,a1,z,heights,n=64):
 verts=[];faces=[]
 for i in range(n+1):
  t=i/n;ang=a0+(a1-a0)*t
  for rr,zz in [(r-thick/2,z),(r+thick/2,z),(r+thick/2,z+heights(t)),(r-thick/2,z+heights(t))]:verts.append((cx+rr*math.cos(ang),cy+rr*math.sin(ang),zz))
 for i in range(n):
  for j in range(4):
   a=i*4+j;b=i*4+(j+1)%4;c=(i+1)*4+(j+1)%4;d=(i+1)*4+j
   faces.extend([(a,b,c),(a,c,d)])
 faces.extend([(0,2,1),(0,3,2),(4*n,4*n+1,4*n+2),(4*n,4*n+2,4*n+3)])
 mesh=trimesh.Trimesh(verts,faces,process=False);mesh.fix_normals()
 parts.append(Manifold(Mesh64(np.array(mesh.vertices),np.array(mesh.faces,dtype=np.uint64))))
add(0,0,0,150,76,3)
# Left sculptural screen: low street edge rises into a curved vertical sail.
curved_wall(-67,16,35,3.0,-math.pi/2,0,2.8,lambda t:13+32*min(t/.94,1)**2)
# Low extension of the left name wall is a continuation of the sweep.
add(-70.5,-19,2.8,7,3.0,13)
# Right guardhouse: compact block and curved street-facing signage plane.
add(48,5,2.8,44,27,25)
add(48,-8.6,2.8,44,7,25)
# Curvature observed at front canopy and parapet; no tower behind is included.
curved_wall(48,67,78,3.0,math.radians(253),math.radians(287),2.8,lambda t:39-5*max(0,(t-.08)/.92))
# Canopy follows same broad arc and merges into guardhouse.
curved_wall(48,67,80,6.0,math.radians(254),math.radians(286),19.0,lambda t:2.7)
# Street-facing low glazing, under the projecting curved canopy.
for x in [33,39,45,51,57,63]:
 y=67-math.sqrt(78**2-(x-48)**2)
 cut(x,y,7.4,4.4,8.0,8.8)
# Low sill with stout printable edge.
add(48,-9.5,5.6,41,4.0,1.6)
# Campus-side pedestrian doorway visible at the inner side of guardhouse.
cut(26.5,0,3.0,4.5,7,16)
# A plain roof is intentional: source does not establish rear utilities.
add(48,5,27.1,44.8,27.8,1.4)
# Low paving threshold: no unsupported flagpoles or traffic barrier.
add(0,-2,2.8,144,67,1.0)
solid=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
assert solid.status().name=='NoError';assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.volume,len(mesh.faces),mesh.is_watertight)
