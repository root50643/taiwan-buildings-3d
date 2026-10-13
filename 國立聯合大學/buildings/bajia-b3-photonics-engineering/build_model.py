"""B3 光電館. Photo-informed approximate miniature, millimetres.
Source photos linked in manifest; no photographs embedded.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, OpType
OUT=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h): return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h): parts.append(box(x,y,z,w,d,h))
def wy(xs,y,zs,w=4,h=4):
 for x in xs:
  for z in zs: cuts.append(box(x,y,z,w,1.5,h))
def wx(x,ys,zs,w=4,h=4):
 for y in ys:
  for z in zs: cuts.append(box(x,y,z,1.5,w,h))
def beam(a,b,width):
 a=np.array(a);b=np.array(b);v=b-a;length=np.linalg.norm(v)
 m=trimesh.creation.box([width,width,length]);m.apply_transform(trimesh.geometry.align_vectors([0,0,1],v));m.apply_translation((a+b)/2)
 from manifold3d import Mesh
 parts.append(Manifold(Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32))))
# Common grounded base, independent 150 mm miniature.
add(0,0,0,150,90,2.4)
# Main tall photonics wing; front is negative Y. Lower plinth remains visible.
add(32,9,2.3,61,33,55)
add(32,9,56.7,62.6,34.6,1.4)
# The broad left teaching wing is lower and steps back from the tower.
add(-38,15,2.3,69,27,41)
add(-38,15,42.8,70.2,28.2,1.3)
# Slightly advancing inner left bay suggests the curved concave composition.
add(-11,11,2.3,17,31,41)
# Floor bands and integral raised facade frames.
for z in [5,13.5,22,30.5,39]:
 add(-38,.9,z,68,1.6,1.35)
for x in [-69,-51,-33,-15,-4]:add(x,.7,4,1.7,1.8,38)
for x in [-61,-42,-23,-7]:
 for xp in [x-3,x+3]:
  zs=[7,15.5,24,33] if xp<-52 else [24,33]
  wy([xp],-4.5 if xp>-19.5 else 1.5,zs,4.1,4.5)
# Deeper balcony-like recesses between main facade piers.
for x in [-60,-42,-24]:
 for z in [23]:cuts.append(box(x,.9,z,13,2.4,5.8))
# Right wing tall turquoise fins represented by robust raised relief.
for x in [14,29,44]:add(x,-8.3,15,5.2,2.3,40)
for x in [7,21.5,36.5,52]:wy([x],-7.5,[8,17,26,35,44,51],4.5,4.4)
for x in [19,34,49]:
 for z in np.arange(17,53,2.8):add(x,-8.1,float(z),2.6,1.7,.85)
for z in [6,14]:add(32,-8,z,60,1.8,1.5)
# Side facade keeps a generous solid stair-bearing wall.
wx(62.5,[-3,7,20],[8,17,26,35,44,51],3.8,3.7)
# Approximate obscured rear: restrained regular windows, flat service roof.
wy(np.arange(8,60,9),25.5,[8,17,26,35,44,51],4.5,4)
wy(np.arange(-65,-1,9),28.5,[7,15.5,24,33],4.5,4)
wx(-72.5,[9,20],[7,15.5,24,33],4.1,4)
# Cylindrical/ribbed vertical stair tower, partially projecting ahead of facade.
parts.append(Manifold.cylinder(61,5.6,5.6,48).translate((0,-10,2.3)))
for z in [8,17,26,35,44,53]:
 cuts.append(box(0,-15.2,z,6.9,1.4,5.8))
for x in [-4.2,-2.8,2.8,4.2]:add(x,-15.05,3.5,.9,1.4,59.8)
add(0,-10,62.6,12.3,12,1.4)
# Low oval entrance pavilion: print-solid, with shallow panel recesses.
hall=Manifold.cylinder(13.7,1,1,72).scale((24,12,1)).translate((-33,-18,3))
parts.append(hall)
parts.append(Manifold.cylinder(1.3,1,1,72).scale((25,13,1)).translate((-33,-18,16.2)))
# Raised curved parapet gives the entrance pavilion its recognizable rim.
ring=Manifold.cylinder(2.2,1,1,72).scale((24,12,1))-Manifold.cylinder(2.4,1,1,72).scale((22.6,10.6,1)).translate((0,0,-.1))
parts.append(ring.translate((-33,-18,17.2)))
# Short solid neck to main wing; rounded hall glazing is recessed individually.
add(-30,-4,2.3,42,13,13.8)
for theta in np.linspace(np.pi,2*np.pi,11):
 x=-33+23.7*np.cos(theta);y=-18+11.7*np.sin(theta)
 # rectangular shallow apertures on elliptical front, backed by solid core
 c=box(0,0,5.2,3.6,1.5,8).rotate((0,0,float(theta*180/np.pi+90))).translate((x,y,0));cuts.append(c)
# Substantial entrance stair terrace, connected to plinth.
for i in range(3):add(-33,-31-i*1.6,2.3,25,2,1.9-i*.5)
# External switchback stair on right end. All slabs and rails >= 1.2 mm.
# End posts and landings tie each flight into building, without hair-thin rails.
for y in [-7,18]:add(68,y,2.3,1.8,1.8,51.5)
for k in range(11):
 z=4.8+k*4.6;y=-7 if k%2==0 else 18
 add(65.4,y,z,8.8,4,1.4)
 if k<10:
  yn=18 if k%2==0 else -7;zn=z+4.6
  beam((67,y,z+.7),(67,yn,zn+.7),1.5)
  # Closely spaced stair treads anchored to inclined slab.
  for s in range(14):
   t=s/13;yy=y+(yn-y)*t;zz=z+(zn-z)*t
   add(65.4,yy,zz,7.9,2.3,1.2)
  beam((69.25,y,z+2.4),(69.25,yn,zn+2.4),1.25)
  for t in [.1,.5,.9]:
   yy=y+(yn-y)*t;zz=z+(zn-z)*t
   add(69.25,yy,zz,.95,.95,3)
# Rooftop solar/pergola canopy simplified as solid raised panels with stout legs.
for xx in [16,39]:
 for yy in [1,18]:add(xx,yy,57.5,1.6,1.6,3.1)
 add(xx,9.5,60.1,21,22,1.1)
 for y in [2,9.5,17]:cuts.append(box(xx,y,60.8,20,.65,.6))
 for x in [xx-5,xx+2]:cuts.append(box(x,9.5,60.8,.65,21,.6))
# Left roof low equipment cap, no unverified tiny equipment.
add(-12,15,44,8,9,3)
shape=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
m=shape.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('Exported',len(mesh.faces),'triangles',mesh.extents,'mm; watertight',mesh.is_watertight)
