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

# L-shaped pair of perpendicular wings, identified in official photos 1/4/7/8.
add(0,0,0,150,122,2.4)
add(-4,29,2.3,126,34,3.8)
add(-50,-8,2.3,34,102,3.8)
add(-28,6,2.3,18,20,3.8)
add(-4,29,6,124,32,67)
add(-50,-8,6,32,100,67)
# Front concave circulation joint and simple visible corner glazing.
add(-28,6,6,16,19,67)
for row in range(5):
 z=10+row*12.2
 for x in np.linspace(-10,51,9):
  window(float(x),12.8,z,5.0,7.3)
  window(float(x),12.8,z+8.2,5.0,1.7)
  detail(float(x),12.8,z+6.0,5.3,2.2,.85)
 window(-28,-3.5,z+3.0,12,4.8)
 # Outside long wing face is actually visible in official aerial and oblique photos.
 for y in np.linspace(-46,30,10):
  if y < -40:continue
  window(-66,float(y),z,5.0,7.3,'left')
  window(-66,float(y),z+8.2,5.0,1.7,'left')
for x in np.linspace(-14,55,10):add(float(x),12.3,6,1.3,2.4,64)
for y in np.linspace(-50,34,11):add(-66.4,float(y),6,2.4,1.3,64)
# Far end elevation photographed in photo 7: three window bays and adjacent narrow stair strip.
for row in range(5):
 z=10+row*12.2
 for x in [-57,-49,-41]:window(x,-58,z,5.1,7.3)
 window(-61,-58,z+8,3.2,1.8)
# Bay-like entrance at the outside corner; balcony-like window bands above.
add(-67,-49,17.5,8,17,54.8)
for z in [22,34.2,46.4,58.6]:
 window(-71,-49,z,13,5.3,'left')
window(-28,-3.7,7.2,12,10)
window(-66.7,-49,6.3,2.0,10.6,'left')
# Courtyard steps and long outside end steps remain attached to the plinth.
stairs(-28,-18,2.3,18,12,5.4,8)
stairs(-53,-57,2.3,29,8,3.7,6)
# Rim and independently supported solar canopies documented on both arms.
for x,y,w,d in [(-4,29,125,33),(-50,-8,33,101)]:
 add(x,y,72.7,w,d,1.3)
solar(8,28,74,90,28)
solar(-50,-20,74,28,64)
# Blue glazed lift tower visible near inner rooftop corner, modelled as an exterior solid.
add(-29,30,73,12,13,16)
for z in [75,80,85]:
 window(-29,23.5,z,9.5,3.2)
 window(-35,30,z,10,3.2,'left')
add(-29,30,89,12.8,13.8,1.2)
# Unobserved rear walls remain plain rather than mirrored invented windows.

result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and len(mesh.split(only_watertight=False))==1,'Expected one watertight boundary'
mesh.export(OUT/'model.stl');print('model.stl',mesh.extents.tolist(),'mm;',len(mesh.faces),'faces')
