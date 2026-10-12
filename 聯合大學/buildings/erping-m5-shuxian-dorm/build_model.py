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

# Five-storey long facade with two-storey entrance recess at the left.
# Full-width exterior source: official dorm centre exterior photo 2.
add(0,0,0,150,94,2.4)
add(0,10,2.3,132,50,2.9)
cyl(-59,-18.5,2.3,2.8,2.9)
add(0,10,5.0,130,48,63)
# External entry porch is cut from the two lowest storeys; no indoor plan.
cut(-44,-14,5,36,15,25)
# One documented cylindrical column supports the broad upper overhang.
details.append(Manifold.cylinder(28.0,2.6,2.6,48).translate((-59,-18.5,2.3)))
# The two entrance walls remain behind the porch and carry the sign band.
detail(-44,-6.7,16.8,32,2.2,4.2)
window(-44,-6.6,6.0,27,10.1)
window(-44,-6.6,22.2,27,7.0)
for x in [-55,-49,-43,-37,-31]:
 detail(x,-6.7,6,.85,2.2,10.3)
 detail(x,-6.7,22.1,.85,2.2,7.2)
detail(-44,-8.0,18.0,14,1.2,2.0)
# Actual left portal ceiling grid becomes robust shallow ribs.
for x in [-56,-48,-40,-32]:add(x,-14,28.8,1.1,13,1.4)
for y in [-19,-14,-9]:add(-44,y,28.8,35,1.1,1.4)
# Long facade: grouped windows, upper transoms and alternating horizontal sun screens.
for row in range(5):
 z=7+row*12.0
 for j,x in enumerate([-57,-46,-35,-24,-13,-2,9,20,31,42,53]):
  if row<2 and x< -25:continue
  window(x,-14,z,7.3,6.3)
  window(x,-14,z+7.3,7.3,2.0)
  detail(x,-14,z+6.35,8.3,2.3,.9)
  if (j+row)%3!=0:
   # Louver-like architectural screen represented as shallow, wall-backed ridges.
   add(x,-15, z-.2,7.4,2.4,3.8)
   for zz in [z+.6,z+1.8,z+3.0]:cut(x,-16.3,zz,6.7,.75,.5)
# Dark re-clad upper-left corner is a shallow projecting volume, not a new storey.
add(-51,5,55.5,29,39,12.5)
# Avoid hidden duplicate recesses: exterior top windows are cut through the new cladding.
for x in [-57,-46]:window(x,-14.7,56,7.3,9.0,depth=1.5)
# Left circulation strip and horizontal side windows seen down the approach lane.
add(-66,14,5,7,42,63)
for z in [8,20,32,44,56]:
 window(-69.5,14,z,29,6.5,'left')
 detail(-69.5,14,z+4.2,2.2,30,.85)
# Low entrance steps; no floating handrails.
stairs(-44,-31,2.3,34,13,2.9,5)
# Documented low roof canopy, strengthened posts and slightly exaggerated panel seams.
add(0,10,67.7,132,50,1.2)
solar(0,10,68.5,132,49)
# Rear and hidden right elevations intentionally plain. Depth is a stated estimate.

result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and len(mesh.split(only_watertight=False))==1,'Expected one watertight boundary'
mesh.export(OUT/'model.stl');print('model.stl',mesh.extents.tolist(),'mm;',len(mesh.faces),'faces')
