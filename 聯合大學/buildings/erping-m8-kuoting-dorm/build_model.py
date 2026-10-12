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

# Squat rectangular block, front annex and central entry from official photos 2/3/4.
add(0,2,0,150,108,2.4)
add(-40.25,8,2.3,58.5,81,5.8)
add(46.25,8,2.3,46.5,81,5.8)
add(6,16.5,2.3,34,64,5.8)
add(0,15,8,128,62,68)
# Low left front annex has a sloping upper edge and small strip windows.
add(-44,-22,8,38,19,24)
solid_prism_polygon([(-63,30),(-25,30),(-25,34),(-63,36)],19,-22)
for x in np.linspace(-59,-29,7):
 window(float(x),-31.5,15,2.7,6)
 window(float(x),-31.5,26,2.7,4)
# Main five-storey photographed window rhythm. Exclude the entrance grid zone.
for row in range(5):
 z=11+row*12.0
 for x in [-56,-48,-40,-32,28,36,44,52,60]:
  if row<2 and x< -25:continue
  window(x,-16,z,5.0,7.5)
 # Right long side has actual grouped windows visible in photo 2.
 for y in [-9,0,9,18,27,36,43]:window(64,y,z,5.0,7.3,'right')
# Left side is mostly blank, punctuated by high thin windows (photo 3).
for row in range(4):
 for y in [-4,7,18,29,40]:window(-64,y,17+row*12,4.0,2.1,'left')
# Tall glazed strip left of the central lattice; supported shallow mullions.
window(-16,-16,11,10,58)
for z in np.arange(13,70,7.0):detail(-16,-16,z,10.4,2.2,.9)
detail(-16,-16,10,.9,2.2,59)
# Hall entrance has eight columns by seven rows of recessed square panes.
add(5,-17,22,30,3.0,35)
for x in np.linspace(-7.2,17.2,8):
 for z in np.linspace(24,53,7):window(float(x),-18.5,float(z),2.35,3.2,depth=.9)
# Open exterior entrance recess, not an interior floor plan.
cut(5,-18,8,29,8,13.0)
window(5,-13.9,9,24,10)
add(5,-19,20.5,31,8,1.6)
for x in [-10,20]:add(x,-19,8,2.5,5.0,13)
# Main approach: long stair between robust low planter/retaining walls.
stairs(6,-46,2.3,29,30,5.7,12)
for x in [-11,23]:add(x,-31,2.3,2.0,31,3.7)
# Upper glazed sixth-storey addition and shallow arched/gabled roof silhouette.
add(0,15,75.7,128,62,11.5)
# Window bands include slim frames, represented by recesses in the solid exterior.
for x in np.linspace(-59,59,18):
 roof_z=float(np.interp(abs(x),[0,22,45,66],[98,97,94,89]))
 window(float(x),-17,78,4.6,roof_z-79.8,depth=2.0)
for y in np.linspace(-10,40,9):window(64,float(y),78,4.4,7.4,'right')
# Profile follows the gentle rise to a central crest seen in official rooftop photos.
profile=[(-66,87),(66,87),(66,89),(45,94),(22,97),(0,98),(-22,97),(-45,94),(-66,89)]
solid_prism_polygon(profile,65,15)
# Robust horizontal glazing bars in the documented roof lantern.
for x in np.linspace(-59,59,18):
 roof_z=float(np.interp(abs(x),[0,22,45,66],[98,97,94,89]))
 for z in [80.5,84.5,88.5,92.5]:
  if z+.8<roof_z-1.8:detail(float(x),-16,z,4.8,3.4,.8)
# Shallow roof panel seams. No guessed rooftop equipment.
for x in np.arange(-56,57,8):
 roof_z=float(np.interp(abs(x),[0,22,45,66],[98,97,94,89]))
 cut(float(x),15,roof_z-.25,.55,66,.65)
# The front outer rim stays continuous to protect the fine panel cuts.
# Rear elevation is not photographed and is intentionally plain.

result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and len(mesh.split(only_watertight=False))==1,'Expected one watertight boundary'
mesh.export(OUT/'model.stl');print('model.stl',mesh.extents.tolist(),'mm;',len(mesh.faces),'faces')
