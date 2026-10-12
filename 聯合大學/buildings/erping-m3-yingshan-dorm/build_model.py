"""Original exterior miniature geometry; dimensions in millimetres.
Public official exterior photos inform this approximation. Front is -Y.
Run this file from any directory after installing requirements.txt.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, OpType, CrossSection
OUT=Path(__file__).resolve().parent
parts,cuts,details=[],[],[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def detail(x,y,z,w,d,h):details.append(box(x,y,z,w,d,h))
def polygon(points,z,h):
 points=np.asarray(points,float)
 area=np.sum(points[:,0]*np.roll(points[:,1],-1)-np.roll(points[:,0],-1)*points[:,1])
 if area<0:points=points[::-1]
 return CrossSection([points]).extrude(h).translate((0,0,z))
def beam(p1,p2,w=1.2):
 p1=np.array(p1,float);p2=np.array(p2,float);v=p2-p1;length=np.linalg.norm(v);z=v/length
 ref=np.array([0,0,1]) if abs(z[2])<.95 else np.array([0,1,0]);x=np.cross(ref,z);x=x/np.linalg.norm(x);y=np.cross(z,x)
 transform=np.column_stack([x,y,z,p1]);return Manifold.cube((w,w,length)).translate((-w/2,-w/2,0)).transform(transform)
def window_front(x,y,z,w,h,depth=1.1,mullions=1):
 cut(x,y,z,w,depth,h)
 for k in range(1,mullions+1):detail(x-w/2+w*k/(mullions+1),y+.05,z-.05,.8,depth+.15,h+.1)
 detail(x,y+.05,z+h*.72,w+.1,depth+.15,.8)
def flat_rim(x,y,z,w,d,h=1.8,t=1.2):
 add(x,y-d/2+t/2,z,w,t,h);add(x,y+d/2-t/2,z,w,t,h)
 add(x-w/2+t/2,y,z,t,d,h);add(x+w/2-t/2,y,z,t,d,h)
def roof_panel(x,y,z,w,d,slope=2.2):
 parts.append(box(0,0,0,w,d,1.4).rotate((slope,0,0)).translate((x,y,z)))
 for xx in np.arange(-w/2+6,w/2,7):cuts.append(box(float(xx),0,1.0,.65,d+1,.6).rotate((slope,0,0)).translate((x,y,z)))
 for yy in np.arange(-d/2+6,d/2,7):cuts.append(box(0,float(yy),1.0,w+1,.65,.6).rotate((slope,0,0)).translate((x,y,z)))
# M3 影山樓: long slab, individual polygonal bay windows, unequal stair end towers,
# bridge at the middle visible storey, and open rooftop framing seen in photos 4–6.
add(0,0,0,150,76,2.4)
add(0,7,2.3,136,32,55.7)
add(-61,6,2.3,19,36,67)
add(62,7,2.3,14,32,65)
# Shallow open parapets on both raised end cores, not hidden hollow interiors.
flat_rim(-61,6,69.0,19,36,1.8,1.3)
flat_rim(62,7,67.0,14,32,1.8,1.3)
# Main repeating bay silhouettes have solid clipped corners, with individually recessed windows.
for x in [-36,-25,-14,-3,8,19,30]:
 for row in range(5):
  z=4.6+row*10.2
  pts=[(x-4.7,-8.5),(x+4.7,-8.5),(x+4.7,-10.5),(x+3.1,-13.0),(x-3.1,-13.0),(x-4.7,-10.5)]
  parts.append(polygon(pts,z,8.5))
  # Overhanging sill/cap has the same faceted plan, modest 0.4 mm projection.
  pts2=[(x-5.1,-8.5),(x+5.1,-8.5),(x+5.1,-10.7),(x+3.4,-13.4),(x-3.4,-13.4),(x-5.1,-10.7)]
  parts.append(polygon(pts2,z+7.8,1.0))
  window_front(x,-13.05,z+3.0,5.4,4.5,1.0,1)
  # Two visibly splayed side panes; cutters go only into the bay's outside surface.
  for side in [-1,1]:
   angle=-side*32.6
   cuts.append(box(0,0,z+3.0,2.0,1.0,4.5).rotate((0,0,angle)).translate((x+side*3.95,-11.75,0)))
# End entrance strip has broad flat ribbon windows and a tall recessed stair opening.
for row in range(5):
 z=5.0+row*10.2
 window_front(46,-9.1,z+2.6,16.1,5.6,1.15,3)
 cut(62,-9.1,z+1.0,5.8,3.1,8.2)
 window_front(-46,-9.1,z+.5,9.0,9.0,1.2,2)
# The right entrance is level with a documented elevated approach bridge.
cut(46,-9.15,24.9,16,1.5,9.5)
for x in [40,46,52]:detail(x,-9.1,24.9,.9,1.6,9.6)
add(46,-10.3,34.5,18.2,4.2,1.2)
add(46,-21.4,23.4,18.2,25.4,1.9)
# Simplified supports beneath the photographed walkway keep the miniature robust.
for x in [38,54]:
 for y in [-31,-16]:add(x,y,2.3,1.8,1.8,21.3)
for x in [37.5,54.5]:
 for y in [-32,-26,-20,-14]:add(x,y,25.1,1.2,1.2,4.2)
 add(x,-22.4,28.5,1.2,22.8,1.2)
# The visible lateral branch terminates before neighboring buildings.
add(62,-16.8,23.4,18,9.4,1.9)
add(69.7,-16.8,2.3,1.8,1.8,21.3)
# Main roof parapet and the smaller documented top-of-stair rectangular box.
flat_rim(-1,7,57.7,130,32,2.7,1.3)
add(48,10,57.7,11,12,16.0)
flat_rim(48,10,73.4,11,12,1.5,1.2)
# Open grid: no invented solar sheet covering this clearly exposed official-photo structure.
for x in [-56,-44,-32,-20,-8,4,16,28]:
 for y in [-5,3,11,19]:add(x,y,58.0,1.3,1.3,4.2)
for y in [-5,3,11,19]:add(-14,y,61.5,88,1.3,1.3)
for x in [-56,-44,-32,-20,-8,4,16,28]:add(x,7,61.5,1.3,25.3,1.3)
for x in [-50,-26,-2,22]:
 for y in [-5,19]:parts.append(beam((x-6,y,58.1),(x+6,y,61.9),1.1))
# Plaque and contrasting edge band are shallow physical relief, without microscopic lettering.
add(46,-9.7,54.1,16,1.8,3.5)
add(36.1,-9.6,24.0,1.2,1.4,33.5)
# Back and unseen end details remain plain instead of copying the front elevation.

# The opposite end has the documented broad arched recess and louvered panel.
arch=[(-61+6.5*np.cos(t),58+6.5*np.sin(t)) for t in np.linspace(0,np.pi,32)]
arch.append((-54.5,58))
cuts.append(polygon(arch,0,.65).rotate((90,0,0)).translate((0,-11.5,0)))
cut(-61,-11.9,54.7,13,.9,1.6)
cut(-61,-11.9,8,12,1.0,43.5)
for zz in np.arange(9,51,2.0):detail(-61,-11.9,float(zz),12.1,1.1,.8)
# Right return elevation now verified by accommodation-centre exterior photo 5.
for row in range(5):
 z=5+row*10.2
 cut(68.7,-1.5,z+1,1.3,9.0,7.7)
 cut(68.7,11,z+2.5,1.3,5.4,5.9)
 detail(68.7,-1.5,z+3,1.4,9.1,.85)

# Union and carve all architectural relief into a single printable boundary.
result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(str(result.status()))
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
if not mesh.is_watertight or len(mesh.split(only_watertight=False))!=1:
 print([(x.volume,x.bounds.tolist()) for x in mesh.split(only_watertight=False)])
 raise RuntimeError('Expected one watertight connected boundary.')
mesh.export(OUT/'model.stl');print('Exported',mesh.extents.tolist(),'mm;',len(mesh.faces),'triangles')
