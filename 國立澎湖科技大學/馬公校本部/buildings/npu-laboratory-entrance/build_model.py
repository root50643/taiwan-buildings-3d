"""國立澎湖科技大學實驗大樓入口門廊段，毫米、自建照片近似。
不是全館；只取官方近照可核之門廊與後方兩層立面。側/背/屋面進深均截短。
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def frame(x,z,w,h,vertical,horizontal):
 # The glass plane remains backed. Thick mullions fuse deeply into that backing.
 cut(x,-.8,z,w,4.4,h)
 for off in vertical:details.append(box(x+off,2.2,z-.2,1.2,4.0,h+.4))
 for off in horizontal:details.append(box(x,2.2,z+off,w+1.0,4.0,1.2))
# Independent millimetre scale for the facade segment.
add(0,-12,0,150,78,3)
# Rear y=20 and x=+-68 are artificial termination planes, not true elevations.
add(0,10,2.8,136,20,76.2)
# Three ground glazing groups are unequal: west glazing, central doors, east glazing.
frame(-42,8.8,24,24,[-8,0,8],[4.2,18.7])
frame(-7,8.8,32,24,[-10,0,10],[18.7])
frame(43,8.8,36,24,[-12,-6,0,6,12],[4.2,10.3,18.7])
# Central actual door zone is further recessed than adjacent glazing.
cut(-7,1.1,8.8,14,7.2,18.5)
# Robust door jamb and transom, retain connected backed mullion, no floating frame.
details += [box(-7,3.8,8.6,1.3,4.5,18.9),box(-7,3.8,26,15.4,4.5,1.3)]
# Two upper glazed groups. Photo supports a broad centre flanked by narrow panes.
# Western left details are partly obscured by the canopy and deliberately omitted.
frame(-28,50,55,20,[-19,-12,0,12,19],[4.2,15.1])
frame(42,50,43,20,[-16,-10,0,10,16],[4.2,15.1])
# Upper projecting concrete beam (NOT the full-building eave), with two visible soffit bay breaks.
add(0,-2.5,73,140,11,8)
for x in [-65,5,65]:add(x,-2.5,69.8,3,11,4.0)
add(0,-3,80,142,12,1.6)
# Upper boundary is deliberately cropped at this projecting beam.
# Higher set-back glazing and gable seen in the wide photo are EXCLUDED.
# Central entrance canopy: deep projection and thick fascia supported by two cylinders.
add(-23,-18,36.5,79,39,7.8)
for x in [-50,4]:
 parts.append(Manifold.cylinder(31,3.6,3.6,circular_segments=64).translate((x,-32,6.8)))
# Step stack meets all piers and entrance floor with real volume overlaps.
for i in range(4):add(-5,-31+i*2,2.8,126,27-i*4,1.1*(i+1))
# Right-side thin framed rain canopy adjoining portico, simplified to print-safe beams.
add(43,-8.5,43,43,18,1.5)
add(43,-16.5,41.8,43,1.8,2.8)
for x in [24,33.5,43,52.5,62]:add(x,-8,40.8,1.8,18,2.4)
# No building lettering, tiny lamps, handrail or plants; no false adjoining towers.
solid=parts[0]
for p in parts[1:]:solid+=p
for c in cuts:solid-=c
for p in details:solid+=p
assert len(solid.decompose())==1
m=solid.simplify(.000001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight,len(mesh.faces))
