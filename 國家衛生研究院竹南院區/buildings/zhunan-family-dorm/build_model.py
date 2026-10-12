"""NHRI Zhunan family dormitory. Approximate four-wing public exterior, mm.
Front evidence: NHRI 2017 panorama station41. Footprint: public campus map.
Unseen rear elevations remain plain rather than fabricated.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
add(0,0,0,98,98,3)
# Four diagonal wings joined by a central body, as drawn in the public footprint map.
# Wings hidden behind the observed front retain simple, explicitly approximate faces.
add(0,0,2.8,22,22,137.2)
add(0,-6.2,2.8,18,34.6,137.2)
for angle in [45,135,225,315]:
 parts.append(box(0,22,2.8,21,30,144.2).rotate((0,0,angle)))
 parts.append(box(0,36.3,146.5,22,2.0,1.5).rotate((0,0,angle)))
 # Tall solid outer edge piers make the skyline ends slightly taller than center.
 for x in [-9.7,9.7]:parts.append(box(x,36.1,2.8,1.6,2.3,147.2).rotate((0,0,angle)))
 # Only front-facing wings have photo-supported repeating facade details.
 if angle not in [135,225]:
  # Court-side public photo shows narrower end slots and window stacks.
  # Layout is a coarse correspondence, not an independently measured rear elevation.
  rear_side=1 if angle==45 else -1
  for level in range(13):
   rz=6.8+level*10.55
   cuts.append(box(0,37,rz,4.3,1.6,6.2).rotate((0,0,angle)))
   cuts.append(box(rear_side*10.5,29.8,rz,1.6,10.5,6.2).rotate((0,0,angle)))
  continue
 side=-1 if angle==135 else 1
 for level in range(13):
  z=5.4+level*10.55
  # Deep-looking balconies are backed relief, not empty interior spaces.
  cuts.append(box(side*10.5,29.8,z+1.3,2.2,11.4,6.7).rotate((0,0,angle)))
  # Broad end windows between substantial tiled end piers.
  cuts.append(box(0,37,z+1.4,14.2,1.6,6.5).rotate((0,0,angle)))
  # Integral three-part balcony glazing divisions, backed by the facade.
  for y in [26.0,30.0,34.0]:details.append(box(side*10.0,y,z+1.3,1.7,1.0,6.7).rotate((0,0,angle)))
# Central stair/glass stack in the photographed inward-facing V.
for z in np.arange(6.8,133,10.55):
 cut(0,-23.5,z,14.8,1.6,6.7)
 for x in [-4.8,0,4.8]:details.append(box(x,-23.15,z,1.0,1.5,6.7))
# Curved entrance canopy and two documented front supports.
xs=np.linspace(-18,18,37)
upper=[(float(x),14.5+3.3*(1-(float(x)/18)**2)) for x in xs]
lower=[(float(x),13.1+3.3*(1-(float(x)/18)**2)) for x in xs[::-1]]
parts.append(CrossSection([(upper+lower)[::-1]]).extrude(15).rotate((90,0,0)).translate((0,-21.5,0)))
for x in [-15.2,15.2]:parts.append(Manifold.cylinder(12.8,1.2,1.2,24).translate((x,-34.2,2.8)))
cut(0,-23.5,3.3,9.2,1.8,8.2)
add(0,-31,3,31,20,.55)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for q in details:solid=solid+q
solid=solid.simplify(.0001);m=solid.to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.update_faces(mesh.nondegenerate_faces());mesh.update_faces(mesh.unique_faces());mesh.remove_unreferenced_vertices()
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('Dimensions mm',mesh.extents,'watertight',mesh.is_watertight,'solid count',len(solid.decompose()))
