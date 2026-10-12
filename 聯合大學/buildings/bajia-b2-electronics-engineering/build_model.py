"""B2 電子工程館: photo-informed miniature in mm, not surveyed geometry.
Run with numpy, trimesh, manifold3d installed. Front is negative Y.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, OpType
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h): return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h): parts.append(box(x,y,z,w,d,h))
def f(x): return -8+10*(x/70)**2
def local(x,offset,z,w,d,h):
 a=np.degrees(np.arctan(20*x/4900))
 return box(0,0,z,w,d,h).rotate((0,0,a)).translate((x,f(x)+offset,0))
def ribbon(x1,x2,offset,depth,z,h):
 xs=np.linspace(x1,x2,max(4,int((x2-x1)*2)))
 pts=[[x,f(x)+offset] for x in xs]+[[x,f(x)+offset+depth] for x in xs[::-1]]
 return CrossSection([pts]).extrude(h).translate((0,0,z))
def pane(x,z,w=3.3,h=2.4,offset=0): cuts.append(local(x,offset,z,w,1.8,h))
# Bed-facing plinth: separate miniatures share a maximum size, not scale.
add(0,4,0,150,50,2.4)
# Continuous curved volume and flat roof slab. Upper left is cut for staircase.
parts.append(ribbon(-70,70,0,20,2.3,32.8))
parts.append(ribbon(-70.5,70.5,-.6,21.2,35,1.1))
# Full-width recessed balcony/window channels on upper two floors.
for z in [22,28.3]: cuts.append(ribbon(-69,69,-1.5,3.1,z,4.8))
# Retain substantial vertical facade piers, matching the strong bay rhythm.
for x in np.arange(-52,50,7.5):
 details.append(local(x,.4,21.6,1.8,4,13.8))
# Left wing long lower ledges and varied ribbon windows.
for z in [9,15.4]:
 for x in np.arange(-65,49,5.4):
  if not (z==9 and -39<x<-13): pane(x,z,4.3,2.6)
parts.append(ribbon(-68,-43,-1,1.8,13.4,.9))
parts.append(ribbon(-68,-43,-1,1.8,7.4,.9))
# Rear: only broad building mass is known; window rhythm is approximate.
for x in np.arange(-64,65,6.4):
 for z in [6,12.1,18.2,24.3,30.4]: cuts.append(local(x,20,z,3.6,1.6,2.6))
for x in [-70,70]:
 for yy in [8,14]:
  for z in [8,14.5,21,28]:cuts.append(box(x,yy,z,1.5,3,3))
# Distinct tall glazed bays, x=-42 and +8, with integral solid mullions.
for x,z,h,w in [(-42,3.4,31,5.8),(8,4,24.2,8.1)]:
 cuts.append(local(x,-.4,z,w,2.2,h))
 for dx in [-w/2,0,w/2]:details.append(local(x+dx,.15,z,.75,1.5,h))
 for zz in np.arange(z+2.9,z+h,3.7):details.append(local(x,.1,zz,w,1.5,.7))
# Lower glazing spreads rightward from central bay.
for z in [3.6,9.1]:
 cuts.append(ribbon(8,37,-1.2,2.1,z,4.8))
 for x in np.arange(8,39,4):details.append(local(x,.2,z,.7,1.3,4.8))
 details.append(ribbon(8,37,-.35,1.1,z+2.3,.65))
# Main entrance recess and short wide steps, kept shallow for FDM.
for x,w in [(-2,8),(15,10),(28,9)]:cuts.append(local(x,-.2,2.8,w,5,4.9))
for i in range(4):parts.append(ribbon(-7,28,-2.1-i*1.05,1.3,2.3,1.6-i*.36))
# Raised blank signage panel: avoids unreadable sub-nozzle lettering.
parts.append(local(-26,-.55,8.7,23,1.6,4.1))
# Visible vertical louvre stripes alternating with large piers.
for x in [-53,-34,-12,24,39]:
 for z in [16,22.2,28.5]:
  louvre=local(x,.4,z,1.8,3.8,4.5)
  for zz in np.arange(z+.6,z+4.1,.9):louvre=louvre-local(x,-1.45,zz,1.5,.7,.38)
  details.append(louvre)
# Large left upper stair void, retained walls and slab frame.
cuts.append(local(-63,1.2,23,11.5,7,11.7))
# Solid inclined stair flight (printable relief, not fragile individual treads).
for k in range(10):details.append(local(-66+k*.67,1.5,23+k*.53,1,7,1.1))
# Right front stair tower protrudes beyond curve and roof line.
parts.append(local(53,-1.1,2.3,9.4,7.7,36.4))
for z in [4,11,18,25,32]:
 cuts.append(local(53,-4.5,z,6.6,4,4.9))
 for k in range(7):details.append(local(50.5+k*.67,-3.5,z+k*.5,1,3,1.1))
parts.append(local(53,-1.2,38.2,10.5,8.3,.9))
# Lower right terminal wing has an unusually broad horizontal slot.
cuts.append(ribbon(58,70,-1.1,2.5,17,1.8))
parts.append(ribbon(58,70,-1.1,2.2,15.3,1))
# Roof parapet around the curved perimeter and two end walls.
parts.append(ribbon(-70,70,-.3,1,36,1.1))
parts.append(ribbon(-70,70,19.1,1,36,1.1))
for x in [-69.5,69.5]:add(x,f(x)+10,36,1,20,1.1)
# Rectangular service headhouse visible left of center.
add(-33,12,36,7,6,5.1);add(-33,12,40.9,7.5,6.5,.6)
# Solar arrays represented by connected slabs plus engraved panel grid.
for x1,x2,off,dep in [(-53,2,.7,7.2),(12,33,.8,7.2),(-2,23,10,7.1),(61,69,10,7)]:
 parts.append(ribbon(x1,x2,off,dep,36,.9))
 for x in np.arange(x1+3.6,x2,3.6):cuts.append(local(x,off+dep/2,36.52,.5,dep+.1,.7))
 for oo in [off+2.4,off+4.8]:cuts.append(ribbon(x1+.1,x2-.1,oo,.5,36.52,.7))
# Geometrically union all architectural solids, subtract shallow relief,
# then rejoin supported mullions and stair relief.
shape=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
shape=shape+Manifold.batch_boolean(details,OpType.Add)
m=shape.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('Exported',len(mesh.faces),'triangles;',mesh.extents,'mm; watertight',mesh.is_watertight,'components',len(mesh.split()))
