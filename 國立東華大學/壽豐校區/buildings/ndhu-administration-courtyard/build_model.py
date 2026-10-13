"""東華行政大樓與北側廊亭 — 2006–2020 reference approximation.
Official 2026 evacuation plan is used for wing boundaries only, not proof that old
facade photos are current. Miniature-mm original CSG; no imported external meshes.
"""
from pathlib import Path
import math,numpy as np,trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
P={'base_mm':[150,148,2.5],'main_wall_top':43.5,'tower_top':70.9,'min_support':1.8}
parts=[];cuts=[];after=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cyl(x,y,z,r,h,n=64):return Manifold.cylinder(h,r,r,n).translate((x,y,z))
def gable(x,y,z,w,d,rise,along='x'):
 if along=='x':
  cs=[(-d/2,0),(d/2,0),(d/2,1.2),(0,rise+1.2),(-d/2,1.2)]
  m=CrossSection([cs]).extrude(w).rotate((90,0,90)).translate((x-w/2,y,z))
 else:
  cs=[(-w/2,0),(w/2,0),(w/2,1.2),(0,rise+1.2),(-w/2,1.2)]
  m=CrossSection([cs]).extrude(d).rotate((90,0,0)).translate((x,y+d/2,z))
 parts.append(m)
def radial_cut(cx,cy,r,ang,z,w,d,h):
 a=math.radians(ang);return box(0,0,z,w,d,h).rotate((0,0,ang-90)).translate((cx+r*math.cos(a),cy+r*math.sin(a),0))
add(0,0,0,*P['base_mm'])
# Unequal three wings leave the north courtyard open.
add(0,-39,2.4,112,25,41.1)
add(-51,4,2.4,24,82,33.1)
add(51,-7,2.4,24,60,33.1)
gable(0,-39,43.1,115,28,7.0)
gable(-51,4,35.0,27,83,6.2,'y')
gable(51,-7,35.0,27,60,6.2,'y')
# Central high dormer/clerestory strip, on both north and south long roof faces.
add(-6,-39,43.3,77,26.1,7.8)
for xx in np.arange(-41,32,7.4):
 for side in [-1,1]:cuts.append(box(xx,-39+side*13.05,44.5,4.8,2.1,5.3))
# Principal horizontal mouldings: robust, integral and subordinate to the three wings.
for z in [11.0,19.1,27.2,35.3,43.2]:add(0,-39,z,113,26,1.0)
for z in [11.0,19.1,27.2,35.3]:add(-51,4,z,25,83,1.0)
for z in [11.0,19.1,27.3,35.3]:add(51,-7,z,25,61,1.0)
# Taller eastern tower at the short wing's north tip.
tx,ty=51,26
add(tx,ty,2.4,26,26,45.6)
add(tx,ty,47.6,23.0,23.0,11.3)
add(tx,ty,58.6,24.4,24.4,1.8)
for z in [11.0,19.1,27.2,43.2,47.8]:add(tx,ty,z,26.8,26.8,1.1)
# Open top crown with four connected splayed piers; stepped cap is thick, not a point.
for sx in [-1,1]:
 for sy in [-1,1]:
  # Each diagonal pier is a prism tapering slightly inward at top.
  pts=[(sx*8.1-2.0,60.0),(sx*8.1+2.0,60.0),(sx*6.5+2.0,66.5),(sx*6.5-2.0,66.5)]
  pier=CrossSection([pts]).extrude(4.0).rotate((90,0,0)).translate((tx,ty+sy*8.1+2.0,0));parts.append(pier)
add(tx,ty,66.2,21.2,21.2,1.8);add(tx,ty,67.8,18.0,18.0,1.8);add(tx,ty,69.4,15.8,15.8,1.5)
# Tower lower tall windows, then vertical fluted belfry recesses on exposed sides.
for z in [4.1,12.1,20.2,29.0,37.1]:
 for xx in [-8,8]:cuts.append(box(tx+xx,ty+13.0,z,3.6,2.1,5.5))
 for yy in [-8,8]:cuts.append(box(tx+13.0,ty+yy,z,2.1,3.6,5.5))
 for xx in [-2.0,2.0]:
  if z<27:continue
  cuts.append(box(tx+xx,ty+13,z,1.8,2.0,5.2))
for xx in [-8,8]:cuts.append(box(tx+xx,ty-13.0,38.0,3.6,2.1,4.7))
for side in [-1,1]:
 for q in [-5.4,0,5.4]:
  cuts.append(box(tx+q,ty+side*11.55,46.0,2.8,5.1,10.3))
  cuts.append(box(tx+side*11.55,ty+q,46.0,5.1,2.8,10.3))
# North courtyard semicircular glazed hall, capped by a drum-like meeting room.
parts.append(cyl(0,-27,2.4,13,26.8))
parts.append(cyl(0,-27,28.8,13.8,1.6))
for a in [25,55,90,125,155]:
 cuts.append(radial_cut(0,-27,13,a,4.0,4.2,2.4,12.1))
 cuts.append(radial_cut(0,-27,13,a,21.0,3.3,2.0,5.4))
# South broad curved portico, deep entrance between stout walls, not an interior hall model.
parts.append(cyl(0,-49.6,2.4,17.0,24.0))
parts.append(cyl(0,-49.6,26.0,17.6,1.5))
cuts.append(box(0,-64.7,2.5,15.8,9.8,15.4))
for a in [215,245,275,305,325]:cuts.append(radial_cut(0,-49.6,17,a,20,2.8,1.9,4.5))
# Main south and north facades; exclude the occupied central hall interfaces.
for side in [-1,1]:
 for z in [4.1,12.2,20.3,28.4,36.5]:
  for xx in np.arange(-47,50,8.0):
   if abs(xx)<16 and z<28:continue
   if side>0 and ((xx<-38 and z<43) or (xx>38 and z<43)):continue
   cuts.append(box(xx,-39+side*12.6,z,3.5,2.1,5.6))
# Ground north facade beyond foyer has paired smaller windows, no invented full glass wall.
# Western long wing outside and courtyard windows; eaves/gable retained at end.
for xx in [-63.1,-38.9]:
 for z in [4.1,12.2,20.3,28.4]:
  for yy in [-24,-13,-2,9,20,31,40]:
   if yy<-23 and xx>-40:continue
   if yy>=40 and xx>-40 and z<20:continue
   cuts.append(box(xx,yy,z,2.1,3.7,5.6))
# West wing attic side openings and northern gable round vent.
vent=Manifold.cylinder(2.4,1.7,1.7,32).rotate((90,0,0)).translate((-51,46.2,38.3));cuts.append(vent)
# East wing outside/court has lower windows. Do not bore buried tower or main intersections.
for xx in [38.9,63.1]:
 for z in [4.1,12.2,20.3,29.2]:
  for yy in [-23,-12,-1,9]:
   if yy<-23 and xx<40:continue
   cuts.append(box(xx,yy,z,2.0,3.6,5.5))
# Northern end extension and recessed terraces of the long wing.
add(-48,48,2.4,28,22,17.4)
add(-48,48,19.5,29.5,23.5,1.7)
add(-43,46,21.0,18,15,5.0)
add(-43,46,25.7,20,17,1.7)
for xx in [-59,-51,-43]:cuts.append(box(xx,59.0,4.0,3.4,2.0,6.0))
# Open north colonnade links the unequal ends, plus the octagonal pavilion at the east end.
add(0,62,2.4,126,7.5,1.2)
add(0,62,10.1,126,7.5,1.8)
for xx in np.arange(-61,64,10.2):parts.append(cyl(xx,62,3.3,1.25,7.1))
parts.append(cyl(51,62,2.4,10.2,1.5,8))
for a in np.arange(22.5,360,45):
 ar=math.radians(a);parts.append(cyl(51+8.3*math.cos(ar),62+8.3*math.sin(ar),3.6,1.2,7.2))
parts.append(Manifold.cylinder(3.3,11.0,3.2,8).translate((51,62,10.4)))
# Main entry steps, small and merged into the continuous base.
for i in range(3):add(0,-67.5-i*1.5,2.4,25,4.5,2.1-i*.6)
solid=parts[0]
for p in parts[1:]:solid+=p
for c in cuts:solid-=c
for p in after:solid+=p
assert len(solid.decompose())==1,[(s.volume(),s.bounding_box()) for s in solid.decompose()]
m=solid.simplify(.001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,len(mesh.faces),mesh.is_watertight)
