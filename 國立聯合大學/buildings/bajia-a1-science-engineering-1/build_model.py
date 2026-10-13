"""A1 理工學院一館. Photo-informed approximate miniature, millimetres.
Requires numpy, trimesh, manifold3d. Source images are linked, not redistributed.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold
OUT=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def gable(x,y,z,w,d,r,axis='y'):
 pts=[[x+sx*w/2,y+sy*d/2,z] for sx in [-1,1] for sy in [-1,1]]
 pts+=([[x,y-d/2,z+r],[x,y+d/2,z+r]] if axis=='y' else [[x-w/2,y,z+r],[x+w/2,y,z+r]])
 parts.append(Manifold.hull_points(pts))
def hip(x,y,z,w,d,r):
 parts.append(Manifold.hull_points([[x+sx*w/2,y+sy*d/2,z] for sx in [-1,1] for sy in [-1,1]]+[[x,y,z+r]]))
def windows_y(xs,y,zs,w=3.3,h=3):
 for x in xs:
  for z in zs:cuts.append(box(x,y,z,w,1.2,h))
def windows_x(x,ys,zs,w=3.3,h=3):
 for y in ys:
  for z in zs:cuts.append(box(x,y,z,1.2,w,h))
# Single bed-facing plinth, plus shallow courtyard terraces.
add(0,0,0,150,148,2.4)
add(0,44,2.3,132,32,3)
add(0,33,2.3,83,8,1.9)
add(0,28,2.3,83,3,1.1)
# Three main wings around the courtyard. Front is negative Y.
add(0,51,2.3,132,25,44)
for x in [-52.5,52.5]:
 add(x,2,2.3,27,104,43)
 # Lower forward end and four-storey terminal pavilion.
 add(x,-45,2.3,27,24,35)
 add(x,-59,2.3,27,18,31)
 # Reduced horizontal roof cornice, shallow enough for FDM.
 add(x,-59,32.6,28.4,19.4,1.4)
 # Hipped perimeter roof represented as solid low cap around recessed center.
 hip(x,-59,34,27.5,19,3)
 cuts.append(box(x,-59,35,15,9,5))
 # Main gabled roof and two raised clerestory ridges.
 gable(x,10,45,28.4,77,4.5)
 for yy in [-10,25]:
  add(x,yy,48.5,9,19,1.6)
  gable(x,yy,50,10,20,1.6)
 # Solar-array strips represented as 0.8 mm raised panels on roof slopes.
 for xx in [x-8,x+8]:
  p=box(xx,10,47.2,8,67,.8)
  # At this height panel lies within roof on its inner side, so remains joined.
  parts.append(p)
 # Long facade window rhythm: 5 storeys, paired bays.
 for xx in [x-13.5,x+13.5]:windows_x(xx,np.arange(-29,36,7),[7,14.5,22,29.5,37],4.2,3.6)
 for zz in [6,13,20,27]:
  windows_y([x-5,x,x+5],-68, [zz],3.4,4)
 # Tall front glazing recess with integral mullions.
 cuts.append(box(x,-68,5,12,1.4,11.5))
 for v in [-4,0,4]:add(x+v,-68.15,5,0.9,.55,11.5)
 add(x,-68.15,10.2,12,.55,.9)
 # Front shade panel supported against facade.
 add(x,-68.4,17.1,14,1.2,1.1)
# Rear cross wing gabled roof / central dormer.
gable(0,51,46,133.4,26.4,4,'x')
for x in [-35,35]:
 add(x,51,49.4,27,7,1.8);gable(x,51,51,28,8,1.4,'x')
 add(x,44.7,48.5,31,7,.9)
add(0,49.8,46,16,27,5)
gable(0,49.8,50.8,17,28,2,'x')
windows_y(np.arange(-57,61,7),64,[8,15.5,23,30.5,38],4.2,3.6)
windows_y([-33,-26,26,33],38.5,[8,15.5,23,30.5,38],4.2,3.6)
windows_y([-19,-12,-5,2,9,16],38.5,[38],4.2,3.6)
# Rear-corner stair towers with retained openings under hip caps.
for x in [-61,61]:
 add(x,54,44,7.6,8,10)
 cuts.append(box(x,54,51,9,5.4,2.2))
 hip(x,54,54,10,10,3.1)
# Courtyard central projection, prominent entrance facade.
add(0,34,5,43,12,26)
add(0,27.6,5,18,3,22)
windows_y([-17,-12,12,17],28,[11,18,25],2.5,3.8)
windows_y([-5,0,5],26,[8,16,22],3.2,3.3)
add(0,25.2,13,20,2.2,1.4)
# Offset smaller energy-engineering entrance block in front.
add(-9,-54,2.3,40,24,28)
gable(-9,-54,30,42,26,5,'x')
add(15,-51,2.3,8,20,32)
add(15,-51,33,7,7,4)
cuts.append(box(15,-51,35.5,8,4.2,1.8))
hip(15,-51,37,9,9,2.4)
windows_y(np.arange(-25,10,5.5),-66,[6,13,21],3.2,3.8)
windows_y(np.arange(-25,10,5.5),-42,[7,14,22],3.2,3.8)
cuts.append(box(15,-61,5,4,1.2,24))
for z in [9,16,23]:add(15,-61.15,z,4,.55,.9)
# Low connective walkways; solid underside is a deliberate print simplification.
for x,w in [(-36,12),(36,33)]:
 add(x,-50,2.3,w,4,5)
 gable(x,-50,7.1,w+1,5,1,'x')
# Short entrance steps and paths, no tiny standalone landscape ornaments.
for i in range(4):add(-9,-68-i*1.1,2.3,16,1.2,2.2-i*.5)
for i in range(4):add(36,-62-i*1.1,2.3,15,1.2,2.2-i*.5)
# Shallow rooftop panel-grid grooves, sized for 0.4 mm FDM nozzles.
for x in [-52.5,52.5]:
 for xx in [x-8,x+8]:
  for yy in range(-20,43,7):cuts.append(box(xx,yy,47.65,7.5,.65,.5))
  cuts.append(box(xx,10,47.65,.65,66,.5))
for x in [-35,35]:
 for xx in range(int(x-12),int(x+13),6):cuts.append(box(xx,44.7,49.05,.65,6.5,.5))
 cuts.append(box(x,44.7,49.05,30,.65,.5))
shape=Manifold.batch_boolean(parts, __import__('manifold3d').OpType.Add)
shape=shape-Manifold.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
# Add glazing mullions after subtraction so they remain visible. Each is
# anchored into the back of its shallow recess, rather than a floating strip.
mullions=[]
for x in [-52.5,52.5]:
 for dx in [-4,0,4]:mullions.append(box(x+dx,-67.8,4.8,.85,1.5,12))
 for z in [8.5,12.2]:mullions.append(box(x,-67.8,z,12.4,1.5,.85))
for z in [9,16,23]:mullions.append(box(15,-60.75,z,4.2,1.2,.85))
shape=shape+Manifold.batch_boolean(mullions,__import__('manifold3d').OpType.Add)
m=shape.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('Exported',len(mesh.faces),'triangles',mesh.extents,'mm; watertight',mesh.is_watertight)
