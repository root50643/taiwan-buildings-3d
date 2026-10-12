"""Photo-referenced exterior miniature. Units: mm. Front: -Y.
Run python build_model.py with the pinned requirements. No private data or reference images.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, OpType, Mesh
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def detail(x,y,z,w,d,h):details.append(box(x,y,z,w,d,h))
def cyl(x,y,z,r,h):parts.append(Manifold.cylinder(h,r,r,48).translate((x,y,z)))
def window(x,y,z,w,h,side='front',depth=1.0):
 if side=='front':cut(x,y,z,w,depth*2,h)
 elif side=='rear':cut(x,y,z,w,depth*2,h)
 else:cut(x,y,z,depth*2,w,h)
def solar(x,y,z,w,d):
 # Shallow roof slab and robust posts reproduce visible roof canopy; no equipment.
 for xx in np.linspace(x-w/2+2,x+w/2-2,max(2,int(w/16))):
  for yy in [y-d/2+2,y+d/2-2]:add(float(xx),yy,z,1.5,1.5,3.8)
 add(x,y,z+3.5,w,d,1.4)
 for xx in np.arange(x-w/2+7,x+w/2,8):cut(float(xx),y,z+4.5,.6,d+.2,.8)
 for yy in np.arange(y-d/2+7,y+d/2,8):cut(x,float(yy),z+4.5,w+.2,.6,.8)
def stairs(x,near_y,z,width,run,rise,n):
 for i in range(n):add(x,near_y+i*run/n,z,width,run/n+.2,rise*(i+1)/n)
def solid_prism_polygon(points,depth,y):
 # Convex profile polygon in XZ, extruded along Y.
 vertices=np.array([[x,yy,z] for yy in [y-depth/2,y+depth/2] for x,z in points],dtype=np.float32)
 mesh=trimesh.convex.convex_hull(vertices)
 parts.append(Manifold(Mesh(np.asarray(mesh.vertices,dtype=np.float32),np.asarray(mesh.faces,dtype=np.uint32))))

# One connected two-wing complex, per the official current map and aerial photographs.
# M10 is the wing nearest M6 / the round dining hall. The connecting bay is preserved.
add(0,0,0,150,106,2.4)
add(0,1,2.3,144,98,1.8)
# Circular landscape forecourt is a shallow attached ring; it is not a separate shell.
ring=Manifold.cylinder(.9,24,24,100)-Manifold.cylinder(1.1,19,19,100).translate((0,0,-.1))
parts.append(ring.translate((0,-21,3.9)))
# Each wing is authored in a local coordinate system, then rotated to the photographed V.
for side in [-1,1]:
 start_parts=len(parts);start_cuts=len(cuts);start_details=len(details)
 # 6 upper window rows above a shaded, columned ground storey.
 add(0,2.5,4,65,12,5.6)
 add(0,0,9.3,65,21,48.7)
 add(0,0,58,66,22,1.3)
 # Facade fins: increased to 1.0 mm for a small FDM model.
 for x in np.linspace(-30.5,30.5,27):
  add(float(x),-11.0,9.1,1.0,2.5,50.1)
  add(float(x),11.0,9.1,1.0,2.5,50.1)
 # Window recesses are only external relief, with solid backing.
 for row in range(6):
  z=11+row*7.5
  for x in np.linspace(-29.33,29.33,26):
   window(float(x),-10.5,z,1.4,4.8,depth=.8)
   window(float(x),10.5,z,1.4,4.8,'rear',depth=.8)
 # Roof vertical service enclosure silhouette only, no equipment or internals.
 add(side*24,1.5,59.1,12,15,6.8)
 window(side*24,-6,61,5.0,2.0)
 # Narrow end walls and visible tall outer-edge screening.
 add(side*32,-.3,4.0,1.6,22.2,55.2)
 for x in [-24,-8,8,24]:cyl(x,-9.7,4,1.05,5.7)
 # Ground facade has simple deep shadow strips behind the columns.
 for x in [-20,-10,0,10,20]:window(x,-3.5,4.5,6,3.8,depth=.65)
 angle=-side*24.0;cx=side*38.0;cy=8.0
 for seq,start in [(parts,start_parts),(cuts,start_cuts),(details,start_details)]:
  for j in range(start,len(seq)):seq[j]=seq[j].rotate((0,0,angle)).translate((cx,cy,0))
# The central link consists of visible open exterior frames between wings, not a filled tower.
for z in [9.2,16.8,24.3,31.8,39.3,46.8,54.3,58.5]:
 add(0,21,z,17,17,1.2)
for x in [-7,-2.3,2.3,7]:
 for y in [13,28]:add(x,y,9.2,1.05,1.1,50.5)
# Inner-ground porch: sturdy columns and a linked shallow entrance canopy.
add(0,13,8.9,24,14,1.5)
for x in [-9,0,9]:cyl(x,7.0,4.0,1.05,5.2)
stairs(0,-5,2.3,22,8,1.8,4)
# Documented near-corner approach stairs, simplified as solid treads.
for x in [-65,65]:stairs(x,-26,2.3,10,10,1.8,4)

result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and len(mesh.split(only_watertight=False))==1,'Expected one watertight boundary'
mesh.export(OUT/'model.stl');print('model.stl',mesh.extents.tolist(),'mm;',len(mesh.faces),'faces')
