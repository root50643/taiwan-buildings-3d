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

# U-shaped brick dormitory; the freestanding round dining hall is not included.
add(0,0,0,150,136,2.4)
add(0,44,2.3,134,29,2.5)
add(-53,0,2.3,28,117,2.5)
add(53,0,2.3,28,117,2.5)
add(0,26,2.3,20,12,2.5)
add(0,44,4.7,132,27,63)
add(-53,0,4.7,26,115,63)
add(53,0,4.7,26,115,63)
# Back of the open courtyard: three bays each side of the taller central gabled tower.
for row in range(5):
 z=8+row*11.4
 for x in [-34,-23,-12,12,23,34]:
  window(x,30.5,z,5.8,6.8)
  detail(x,30.1,z+6.8,7.6,2.8,1.0)
# Central stack of shallow polygonal bays and extra top-storey gable.
add(0,28,4.7,18,7,73)
for z in [8,19.4,30.8,42.2,53.6,65.0]:
 window(0,24.5,z,14,7.2)
 detail(0,24.4,z+7.2,18.5,2.6,1.0)
# Ground entrance canopy and six broad approach steps.
add(0,19,13.4,24,14,1.5)
for x in [-10,10]:add(x,13,4.7,1.5,1.5,9)
stairs(0,4,2.3,23,19,2.5,6)
# Inner-facing projecting window bays, five rows and seven bays per side.
for side in [-1,1]:
 for y in [-47,-35,-23,-11,1,13,25]:
  add(side*39.5,y,7,3.2,8.8,57.2)
  for row in range(5):
   z=8+row*11.4
   window(side*38.0,y,z,6.7,7.3,'side')
   detail(side*37.9,y,z+7.3,3.8,9.5,1.1)
 # Narrow vertical end-wall windows photographed on otherwise blank gable ends.
 for z in [9,20.4,31.8,43.2,54.6]:window(side*53,-57.5,z,4,5)
 # Outer long side is partially documented; keep simple observed window rhythm.
 for y in [-42,-21,0,21,42]:
  for z in [10,21.4,32.8,44.2,55.6]:window(side*66,y,z,5.5,7,'side')
# Roofs are closed solid hipped masses above solid cores, not inner cavities.
def hip(x,y,w,d,z,rise):
 pts=[(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z),(x,y-d/2+w/2,z+rise),(x,y+d/2-w/2,z+rise)]
 m=trimesh.convex.convex_hull(np.asarray(pts))
 parts.append(Manifold(Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32))))
for x in [-53,53]:
 hip(x,0,28.4,117.4,67.4,10.4)
 # Three small roof dormers look inward and outward, as in the aerial photo.
 for y in [-35,0,35]:
  for side in [-1,1]:
   xx=x+side*7.7
   add(xx,y,69.2,10,14,6.0)
   window(xx+side*5.0,y,70.6,10,3.4,'side',depth=.8)
   solid_prism_polygon([(xx-5.7,75.0),(xx+5.7,75.0),(xx,79.0)],15,y)
# Flat rear crossbar roof with low parapet and higher central gable.
add(0,44,67.5,82,27,1.2)
for yy in [31.1,56.9]:add(0,yy,68.5,82,1.2,1.8)
solid_prism_polygon([(-11,77),(11,77),(11,78),(0,84),(-11,78)],20,34)
# Far-back details are simplified; no invented indoor layout or resident information.

result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and len(mesh.split(only_watertight=False))==1,'Expected one watertight boundary'
mesh.export(OUT/'model.stl');print('model.stl',mesh.extents.tolist(),'mm;',len(mesh.faces),'faces')
