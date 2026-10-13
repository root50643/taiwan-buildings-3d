"""C1立德樓公開外觀近似模型。Units millimetres, standalone display scale.
Observed: 8-storey front/right grid, 13 front window bays, entrance porch/stairs,
raised rooftop canopy. Rear notch is a schematic inference from campus map.
Source URLs and every major simplification are in README.zh-TW.md.
Requires numpy,trimesh,manifold3d; no network/download required.
"""
from pathlib import Path
import manifold3d as md
import trimesh
import numpy as np
P=Path(__file__).resolve().parent
adds=[];cuts=[]
def box(x,y,z,dx,dy,dz,collection=None):
 if collection is None: collection=adds
 m=md.Manifold.cube((dx,dy,dz)).translate((x,y,z));collection.append(m);return m
# 150 mm base establishes standalone display scale, not a surveyed site scale.
box(-75,-64,0,150,121,3)
# Eight occupied storeys plus simplified partly exposed lower plinth.
box(-70,-43,3,140,92,114)
# Schematic rear-left notch: footprint cue visible on official illustrated map.
box(-70,23,3,44,27,121,cuts)
# Front 13-bay facade and right ten-bay facade. Window recess depth 0.9 mm.
pitch=10.35
for floor in range(8):
 z=10+floor*13.7
 for bay in range(13):
  x=-66.2+bay*pitch
  if floor==0 and bay in (5,6,7): continue
  box(x,-43.5,z,8.5,1.4,6.6,cuts)
 for bay in range(10):
  y=-39+bay*8.5
  box(69.1,y,z,1.4,6.8,6.6,cuts)
# Entrance doorway represented as a deep blind recess, no unsupported interior.
box(-10,-43.5,7,20,3.0,12,cuts)
body=md.Manifold.batch_boolean(adds,md.OpType.Add)-md.Manifold.batch_boolean(cuts,md.OpType.Add)
adds=[]
# Continuous projecting cream piers and mullions, identifiable in all source views.
for i in range(14): box(-68+i*pitch,-43.65,3,1.35,.8,113)
for i in range(11): box(69.65,-41+i*8.5,3,.8,1.25,113)
for floor in range(8):
 z=10+floor*13.7
 for bay in range(13):
  x=-66.2+bay*pitch
  if floor==0 and bay in (5,6,7): continue
  # Twin glazing panes split by printable mullion, with bottom sill and A/C mass.
  box(x+4,-43.6,z,.65,1,6.6)
  box(x,-43.7,z,8.5,1.1,.7)
  box(x+.5,-44,z+.5,2.5,1.35,2.4)
 for bay in range(10):
  y=-39+bay*8.5
  box(69,y+3,z,1,.65,6.6)
  box(69,y,z,1.1,6.8,.7)
  box(69.05,y+.45,z+.5,1.35,2.2,2.3)
# Upper two pale storeys translated into shallow continuous spandrel relief.
for z in (89.7,103.4):
 box(-70,-43.8,z,140,1.0,2.0)
 box(69.8,-43,z,1.0,92,2.0)
# Front porch: tall two-pier canopy, lower entrance lintel, upper sign fascia.
box(-25,-48,7,3,6,29)
box(22,-48,7,3,6,29)
box(-26,-48,33,52,6,5.6)
box(-16,-47,18,32,4.5,2.4)
# Broad stair, nine printable solid treads into entrance.
for i in range(9): box(-18,-61+i*1.7,3,36,18-i*1.7,.5*(i+1))
# Large side cheek blocks following the stairs.
for i in range(9):
 for x in (-21,18):box(x,-61+i*1.7,3,3,1.9,.5*(i+1)+1)
# Rooftop canopy: solid-backed instead of fragile unsupported real metal lattice.
box(-68,-41,116.5,136,88,1.5)
box(-68,-41,118,136,88,1.5)
# Raised shallow panel seams preserve observed segmented canopy, fused throughout.
for x in np.linspace(-66,64,18):box(float(x),-41,119.3,.65,88,.6)
for y in np.linspace(-40,45,12):box(-68,float(y),119.3,136,.65,.6)
# All additions unioned; unseen rear facades intentionally undecorated.
body=md.Manifold.batch_boolean([body]+adds,md.OpType.Add)
body=body-md.Manifold.cube((44,27,125)).translate((-70,23,3))
m=body.to_mesh();mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=True)
mesh.export(P/'model.stl')
mesh.export(P/'model.ply')
print('Triangles',len(mesh.faces),'Bounds',mesh.bounds,'watertight',mesh.is_watertight)
