"""馬偕醫學大學 K棟，2013 建築師平面／多面照片有界原創近似。All units final mm.
Plan traced at .078 mm/pixel from 2000px third-floor drawing; 133px=6m.
Y+ is downhill facade; drawing north points +X, not +Y. No surveyed height.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold,Mesh,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def poly(points,z,h):return CrossSection([points[::-1]]).extrude(h).translate((0,0,z))
def trace(points):return [((x-1000)*.078,(710-y)*.078) for x,y in points]
def hull(verts):
 return Manifold.hull_points(verts)
add(0,0,0,150,108,3)
# Main rectangular gym: continuous podium, tall two-level hall, near-flat roof.
add(-22.8,14.6,2.8,71.6,63.8,34.6)
add(-22.8,14.6,37.0,73.2,65.4,1.4)
# Downhill facade's white surround projects over the brick podium.
add(-22.8,47.0,14.8,73.2,1.6,23.0)
cut(-22.8,47.6,17,69,2.6,18.4)
# Recessed long glass ribbon: six broad structural bays, fine backed mullions.
for x in np.linspace(-57,11.4,6):details.append(box(x,46.6,17,1.2,.8,18.4))
for x in np.arange(-54.2,11.0,2.85):details.append(box(x,46.4,17,.6,.45,18.4))
for z in [20.5,26.2,31.8]:details.append(box(-22.8,46.4,z,69,.45,.65))
# Exposed lower-storey brick plinth, broad second row and small ground lights.
for x in np.linspace(-54,8,10):
 cut(x,46.65,5,2.6,1.1,3.2)

for x in np.linspace(-50.2,4.6,5):
 cut(x,46.65,9.6,11.3,1.1,4.2)
 for dx in [-3.8,0,3.8]:details.append(box(x+dx,46.25,9.6,.6,.5,4.2))
# Uphill white entrance elevation: five broad bays and two large glazed rows.
for x in np.linspace(-50.2,4.6,5):
 for z,h in [(23.2,5.7),(30.7,5.1)]:
  cut(x,-17.35,z,11.3,1.6,h)
  for dx in [-3.8,0,3.8]:details.append(box(x+dx,-16.65,z,.6,.45,h))
  details.append(box(x,-16.65,z+h/2,11.3,.45,.6))
 cut(x,-17.35,20.1,11.3,1.6,1.4)
for x in np.linspace(-57.05,11.45,6):add(x,-17.8,13.5,1.8,1.7,23.5)
# Entrance doors and substantial stepped approach; not a regular fourth window row.
for x in [-36,-21,-6]:cut(x,-18.0,12.6,10,3.1,5.6)
add(-11,-20.5,12,30,7,1.4)
for i in range(9):add(-11,-29.6+i*.9,2.8,24,1.1,1.0+i*1.05)
# Side equipment channel bounded by brick end blocks, open sky roof tray.
add(-64.2,14.6,2.8,11.4,63.8,28.5)
for y in [-12,41.2]:add(-64.2,y,30.7,11.4,10.4,7.2)
add(-69.3,14.6,30.7,1.6,43,3.0)
for y in [-4,8,20,31]:add(-64,y,31.0,4.6,5,1.7)
for y in [-10,0,10,20,30,40]:
 cut(-69.95,y,7,1.1,3.7,4.0)

cut(-69.95,14.6,25.0,1.1,45,5.2)
for y in np.arange(-7,37,3):details.append(box(-69.5,y,25.0,.5,.6,5.2))
for y in [-17.35,46.55]:
 for z,h in [(23.2,5.6),(31,5)]:cut(-64.2,y,z,3.5,1.5,h)
# Opposite side connector, with its open equipment tray and separate rear tower.
add(21.3,5,2.8,17.4,44,29)
add(20.9,5,31.4,1.5,44,2.2)
for y in [-8,5,18]:add(25.5,y,31.3,4.5,5.5,1.8)
add(31,-16,2.8,35,13,26.5)
for x in [18,25,32]:
 for z in [8,16,23]:cut(x,-22.6,z,5.4,1.4,4.5)
add(40,-14,28.7,15,11,9)
for z in [8,15,23]:
 for x in [19,25,31]:cut(x,27.1,z,3.4,1.2,5)
# Raised pentagonal auditorium. Roof is faceted with measured plan outline;
# heights are image-bounded, and two non-coplanar roof triangles preserve fold.
hp=trace([(1384,261),(1569,133),(1874,327),(1758,731),(1384,729)])
hc=np.mean(hp,axis=0);parts.append(poly([tuple(hc+(np.array(p)-hc)*.82) for p in hp],2.8,8.2))
heights=[39.0,36.8,33.8,32.2,35.5]
verts=[(x,y,10) for x,y in hp]+[(x,y,z) for (x,y),z in zip(hp,heights)]
parts.append(hull(verts)^box(0,0,0,160,130,38.2))
# Deep tall glass recess on the short downhill oblique edge. Cutter crosses
# the real exterior plane, never forming a hidden thin outside skin.
a,b=np.array(hp[0]),np.array(hp[1]);v=b-a;length=np.linalg.norm(v);u=v/length
angle=np.degrees(np.arctan2(v[1],v[0]));mid=(a+b)/2
# Polygon order clockwise: inside is right side of this edge.
inside=np.array([u[1],-u[0]])
def edgebox(w,depth,z,h,inset):
 c=mid+inside*inset
 return Manifold.cube((w,depth,h),True).translate((0,0,z+h/2)).rotate((0,0,angle)).translate((c[0],c[1],0))
cuts.append(edgebox(length-3.4,7,20.4,14.7,1.6))
cuts.append(edgebox(length-3.4,4.8,13.8,3.7,1.1))
# Fine glazing is fused to the deep rear face (depth 5.1), not free window bars.
for dx in [-4,-1.3,1.3,4]:
 c=mid+u*dx+inside*4.95
 details.append(Manifold.cube((.85,.65,14.7),True).translate((0,0,27.75)).rotate((0,0,angle)).translate((c[0],c[1],0)))
for z in [24.5,30.5]:details.append(edgebox(length-3.7,.65,z,.85,4.95))
# Entry classroom wing continues downhill-to-uphill from the foyer, with
# broad glazing and a roof block, not part of the neighbouring teaching building.
add(50.0,-31.6,2.8,18.4,30.5,25.3)
# External entry-wing colonnade: real open passage above raised landing.
add(38.1,-31.6,2.8,5.8,30.5,10.6)
add(38.1,-31.6,21.2,5.8,30.5,1.4)
for y in [-45.6,-32,-18]:add(35.9,y,13.1,2.4,2.4,8.4)
add(22.5,-22,12,37,9,1.4)
cut(24.5,-23,13.4,19,5.2,7.8)
add(50,-31.6,27.8,19.2,31.3,1.4)
for y in [-24,-39]:
 for z in [8,16,23]:
  cut(59.3,y,z,1.4,11,4)
  if z==23:cut(40.8,y,z,1.4,11,4)
for x in [45,54]:
 for z in [8,16,23]:cut(x,-47,z,6.5,1.3,4)
add(48,-20,28.5,12,7,4)
for p in parts:assert not p.is_empty()
solid=parts[0]
for p in parts[1:]:solid=solid+p
for p in cuts:solid=solid-p
for p in details:solid=solid+p
assert len(solid.decompose())==1,[(p.volume(),p.bounding_box()) for p in solid.decompose()]
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight,len(mesh.faces))
