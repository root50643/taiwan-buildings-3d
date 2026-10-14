"""南神禮拜堂：1957建物／修復前外觀來源限定近似。
Final units mm; X east, Y north. At4mm per estimated metre, main body27m,
rear nave22m and west RC vestibule5m are cross-year image/repair-drawing
bounded interpretations, not survey measurements or official dimensions.
"""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def hull(v):return Manifold.hull_points(v)
def arch(x,y,z,w,h,d):
 r=w/2;p=[(-r,0),(r,0),(r,h-r)]+[(r*np.cos(a),h-r+r*np.sin(a)) for a in np.linspace(0,np.pi,25)[1:]]
 return CrossSection([p]).extrude(d).rotate((90,0,0)).translate((x,y+d/2,z))
def end_arch(x,y,z,w,h,d):return arch(0,0,z,w,h,d).rotate((0,0,90)).translate((x,y,0))
def cyl(x,y,z,r,h,n=64):return Manifold.cylinder(h,r,r,n).translate((x,y,z))
# Separate model, not the surrounding U-shaped campus buildings.
add(0,0,0,150,86,3)
add(-48,0,2.8,20,54,42.7)
add(6,0,2.8,88,40.5,42.7)
# A true double-pitched roof, with a tiny robust flat ridge rather than a needle.
parts.append(hull([(x,y,z) for x in [-38.6,51] for y,z in [(-21,45.1),(21,45.1),(21,46.2),(.7,60.8),(-.7,60.8),(-21,46.2)]]))
# Western RC vestibule plateau, verified as an entire flat field in 2015
# orthophoto; western rose facade is a raised screen over this flat segment.
add(-48,0,45.1,20,54,1.2)
for y in [-26.3,26.3]:add(-48,y,46.0,20,1.4,1.2)
# Continuous eaves and storey belts fused to the main walls.
for y in [-20.65,20.65]:
 for z in [4,25.8,44.6]:add(-4,y,z,109,1.5,1.3)
add(-59.4,0,25.8,1.6,55,1.3)
for y in [-27.4,27.4]:
 for z in [4,25.8,44.6]:add(-48,y,z,20,1.5,1.3)
# Western rose-window front, central pitched outline and lower side shoulders.
add(-58.3,0,3,1.8,54.8,43.8)
parts.append(hull([(x,y,z) for x in [-59.2,-56.1] for y,z in [(-19,45.7),(19,45.7),(19,50.7),(0,61.2),(-19,50.7)]]) ^ box(-57.65,0,0,5,45,60.8))
# Western strong vertical pilaster divisions, following photographed five bays.
for y in [-26.6,-18,-9.2,9.2,18,26.6]:add(-59.45,y,3,1.7,1.15,43.8 if abs(y)>19 else 47.4)
# Front arched windows: two pairs each floor; rose and paired upper lights.
for y in [-22.2,-13.7,13.7,22.2]:
 for z,h,w in [(9,12.5,5.9),(32,9.0,4.8)]:
  parts.append(end_arch(-59.7,y,z-.5,w+1.1,h+1,1.3));cuts.append(end_arch(-60.0,y,z,w,h,2.5))
  for dz in [3.8,7.4]:
   if dz<h-2:details.append(box(-58.85,y,z+dz,.7,w-.3,.65))
  details.append(box(-58.85,y,z,.7,.65,h-2.3))
# Rose is shallow backed relief with an inner ring and 12 petal-like radial ribs.
rose_y=0;rose_z=37.8;rose_r=7.1
rose=Manifold.cylinder(2.1,rose_r,rose_r,96).rotate((0,90,0)).translate((-60.0,0,rose_z));cuts.append(rose)
for r in [7.75,2.0]:
 depth=1.8 if r>7 else .85; inner=r-1.1 if r>7 else r-.75
 ring=(Manifold.cylinder(depth,r,r,96)-Manifold.cylinder(depth+.1,inner,inner,96).translate((0,0,-.05))).rotate((0,90,0)).translate(((-59.6 if r>7 else -58.6),0,rose_z));details.append(ring)
for angle in np.linspace(0,360,12,endpoint=False):
 p=[(1.5,0),(2.5,-.75),(4.3,-.9),(5.9,-.55),(6.8,0),(5.9,.55),(4.3,.9),(2.5,.75)]
 outer=CrossSection([p]);petal=(outer-outer.offset(-.5)).extrude(.75).rotate((0,90,0)).rotate((angle,0,0)).translate((-58.55,0,rose_z));details.append(petal)
for y in [-2.4,0,2.4]:cuts.append(end_arch(-59.3,y,51.0,1.5,5.6 if y==0 else 4.3,3.0))
# West front pedimented entrance is backed, with real deep doorway.
add(-59.9,0,4.4,2.8,14,19)
cut(-60.3,0,5.1,3.4,10,15.5)
parts.append(hull([(x,y,z) for x in [-62.1,-58.5] for y,z in [(-8.4,23.0),(8.4,23.0),(0,27.3)]]))
add(-60.3,0,22.7,4.2,17.5,1.1)
# Recess inside the triangular pediment, kept firmly backed.
cuts.append(hull([(x,y,z) for x in [-62.3,-61.45] for y,z in [(-5.9,24.2),(5.9,24.2),(0,26.5)]]))
for i in range(5):add(-65.2+i*.85,0,2.8,1.1,16.8,.65+i*.35)
# Seven upper arched windows, six lower flanking the central door.
xs=[-33,-20.5,-8,4.5,17,29.5,42]
for y in [-20.25,20.25]:
 for x in xs:
  for z,h,w in [(30,10.5,5.2),(8,14.0,7.0)]:
   if z==8 and x==4.5:continue
   parts.append(arch(x,y,z-.5,w+1.05,h+1,1.1));cuts.append(arch(x,y,z,w,h,2.0))
   for dz in ([3.8,7.6] if z==30 else [4,8,11]):details.append(box(x,y+(.7 if y<0 else -.7),z+dz,w-.3,.65,.65))
   details.append(box(x,y+(.7 if y<0 else -.7),z,.65,.65,h-2.5))
 # Lower blind arcade moulding spans each structural bay, backed by wall.
 for x in xs:
  frame=arch(x,y,5.8,13.0,19.6,1.4)-arch(x,y,5.7,11.5,18.7,1.6)
  parts.append(frame)
 for x in [-39.25,-26.75,-14.25,-1.75,10.75,23.25,35.75,48.25]:add(x,y,26.4,1.0,1.1,18.5)
 # Substantial central open porch: inner arch passes through the projecting roof.
 add(4.5,y+(-3 if y<0 else 3),3,12.4,7.0,23.8)
 cuts.append(arch(4.5,y+(-3 if y<0 else 3),4.4,8.4,18.7,8))
 cut(4.5,y,4.4,8.2,3.0,15.5)
 add(4.5,y+(-3 if y<0 else 3),26.4,14.0,8.0,1.6)
 for i in range(4):add(4.5,y+((-8.4+i*.85) if y<0 else (8.4-i*.85)),2.8,14,1.1,.5+i*.4)
 # West stair vestibule is a distinct mostly solid bay, not an eighth nave bay.
 for z in [10,19,32]:cuts.append(arch(-49,-27 if y<0 else 27,z,3.3,5,1.8))
# Eastern half-round sanctuary (only the eastern semicircle protrudes).
apse=cyl(50,0,2.8,19.5,36.6)^box(62,0,2.7,24,46,37)
parts.append(apse)
# Shallow half-conical copper roof, neither dome nor full cone apex.
cone=Manifold.cylinder(8,20.5,2.0,96).translate((50,0,39.0))^box(62,0,38.9,25,48,9)
parts.append(cone)
# Horizontal circular sanctuary belts, fused into the back.
for z in [3.8,24.1,38.5]:parts.append(cyl(50,0,z,20.2,1.2)^box(62,0,z-.1,25,48,1.5))
# Alternating blind/true arched sanctuary bays along the curved east wall.
for deg in [-72,-36,0,36]:
 a=np.radians(deg);c=np.array([50+19.5*np.cos(a),19.5*np.sin(a)])
 # Start arch in Y-facing plane, rotate normal toward the local radial direction.
 for z,h,w in [(7.0,15.0,6.8),(27.0,9.2,5.5)]:
  if deg==-72 and z==7:continue
  depth=1.2 if z==7 or deg in [-72,0,72] else 2.0
  cutshape=arch(0,0,z,w,h,depth).rotate((0,0,deg-90)).translate((float(c[0]),float(c[1]),0));cuts.append(cutshape)
# Two observed upper sanctuary windows retain backed fine glazing division.
for deg in [-36,36]:
 a=np.radians(deg)
 for z,h,w in [(27.4,7.8,.65),(31.2,.65,4.9)]:
  v=box(0,0,z,w,.5,h).rotate((0,0,deg-90)).translate((50+18.7*np.cos(a),18.7*np.sin(a),0));details.append(v)
# East small gable lights above sanctuary roof.
for y in [-2.4,0,2.4]:cuts.append(end_arch(50.8,y,50.2,2.15,5.0 if y==0 else 3.8,3.0))
# Southeast low attached room, retaining individual flat roof and two east lights.
add(56.8,-21.4,2.8,14.4,9.2,22)
add(56.8,-21.4,24.5,15.3,10.1,1.6)
for y in [-23.6,-19.2]:cuts.append(end_arch(64.2,y,9.2,3.4,9.1,1.8))
# High rectangular bell tower at north side of sanctuary, flat and not pointed.
add(58.5,23.0,2.8,17,17,77.2)
add(58.5,23.0,79.3,19,19,1.7)
for x in [50.5,55.85,61.15,66.5]:
 for y in [15.0,31.0]:add(x,y,3,1.4,1.4,78.8)
for y in [15.0,20.35,25.65,31.0]:
 for x in [50.5,66.5]:add(x,y,3,1.4,1.4,78.8)
# Twelve roof-cap pier tips, widened locally to2.4mm and rooted into cap.
for x,y in sorted({(x,y) for x in [50.5,55.85,61.15,66.5] for y in [15,31]} | {(x,y) for x in [50.5,66.5] for y in [15,20.35,25.65,31]}):add(x,y,80.7,2.4,2.4,1.1)
for z in [25.8,44.6,53.3,78.8]:
 add(58.5,23.0,z,18.4,18.4,1.0)
for y in [14.5,31.5]:
 for x in [53.2,58.5,63.8]:cuts.append(arch(x,y,62.7,3.9,13.5,.7))
 for z in ([47] if y==14.5 else [8,29,47]):cuts.append(arch(58.5,y,z,3.8,8,1.8))
for x in [50,67]:
 for y in [17.7,23.0,28.3]:cuts.append(end_arch(x,y,62.7,3.9,13.5,.7))
 for z in ([47] if x==50 else [8,29,47]):cuts.append(end_arch(x,23.0,z,3.8,8,1.8))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for p in cuts:solid=solid-p
for p in details:solid=solid+p
assert len(solid.decompose())==1,[(p.volume(),p.bounding_box()) for p in solid.decompose()]
m=solid.simplify(.00001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight,len(mesh.faces))
