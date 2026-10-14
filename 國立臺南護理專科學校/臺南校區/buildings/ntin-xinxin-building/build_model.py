"""Original image-derived Xin-Xin building exterior, 2014–2015 appearance.
Units: mm. Independent approximation, not survey/BIM. No third-party mesh.
Python build_model.py [--output DIR]; deterministic STL bytes.
"""
from pathlib import Path
import argparse, json
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
P=dict(base_width=150.,base_depth=48.,base_thickness=2.4,body_width=136.,body_depth=27.2,body_top=35.4,roof_width=141.6,roof_depth=32.0,roof_height=5.8,ridge_width=112.,ridge_depth=1.6,corridor_depth=5.0,corridor_width=114.,gallery_bays=9,column_diameter=1.8,portico_column_diameter=2.5)
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent);out=parser.parse_args().output;out.mkdir(parents=True,exist_ok=True)
parts=[];cuts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def cyl(x,y,z,r,h):parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
# Base and complete rectangular two-storey core. Front faces negative Y.
add(0,-2,0,150,48,2.4)
add(0,0,2.2,136,27.2,33.2)
# Ground plinth, first-floor sill / corridor balustrade, continuous upper cornice.
add(0,-.1,2.4,137.2,27.6,1.9)
add(0,-.2,21.0,137.2,27.8,1.2)
add(0,-.3,24.2,137.2,28.0,1.1)
add(0,0,33.2,138.4,29.0,2.2)
# Real open recess of upper gallery. Eight primary columns create nine broad bays.
# Main columns and the smaller recessed window divisions are deliberately separate.
cut(0,-12.0,25.3,114.0,6.8,7.9)
for i in range(1,9):
 x=-57+i*(114/9)
 cyl(x,-13.05,25.0,.9,8.6)
 # A substantial supported capital and foot, not needle-like decoration.
 add(x,-13.0,32.45,2.25,2.4,.95)
 add(x,-13.0,24.95,2.1,2.25,.9)
# Backed window recesses, two per broad bay. No fragile glazing mullions.
for i in range(18):
 x=-53.83+i*(114/18)
 cut(x,-8.82,26.2,3.9,1.6,5.7)
# Ground front: eighteen principal narrow positions; central two form one doorway.
for i in range(18):
 x=-53.83+i*(114/18)
 if abs(x)<5:continue
 cut(x,-13.55,5.3,3.5,1.45,14.8)
 # Backed solid crossbar for the tall window's low transom.
 add(x,-13.03,7.0,3.7,.7,1.0)
cut(0,-13.35,4.0,9.3,2.3,16.1)
# Both solid end returns have two vertically elongated facade recesses per storey.
for side in [-1,1]:
 for x0 in [61.0,65.6]:
  x=side*x0
  cut(x,-13.52,5.3,2.8,1.42,14.8)
  cut(x,-13.52,24.0,2.8,1.42,9.6)
# Low-relief balustrade ventilation rhythm. No tiny through-perforated lattice.
for i in range(15):
 x=-53.2+i*7.6
 if abs(x)<16.5:continue
 cut(x,-14.05,22.0,2.6,1.2,1.4)
# Historically documented side elevations; their small window divisions simplified.
# No unsupported rear window pattern is invented: rear wall stays plain.
for side in [-1,1]:
 for y in [-7.5,0,7.5]:
  for z,h in [(6.0,13.2),(25.0,7.5)]:cut(side*67.7,y,z,1.8,3.4,h)
# Central projecting porch with an open underside and two sturdy columns.
add(0,-18.8,2.35,34,13.8,1.25)
add(0,-21.6,2.35,29.0,8.2,.7)
for x in [-9.5,9.5]:
 add(x,-21.15,3.3,3.4,3.5,1.2)
 cyl(x,-21.15,4.15,1.25,16.65)
 add(x,-21.15,20.0,3.0,3.2,1.4)
# Flat portico canopy, shallow two-step cornice, joined directly to the main wall.
add(0,-18.9,20.55,29.8,11.8,1.4)
add(0,-18.8,21.75,33.2,12.0,1.0)
# Main roof: all four slopes, shortened ridge, end hips; small ridge plateau
# of 1.6 mm is an explicit printing simplification instead of a vanishing knife edge.
add(0,0,35.05,141.6,32.0,.85)
roof=CrossSection.square((141.6,32.0),center=True).extrude(5.8,scale_top=(112/141.6,1.6/32)).translate((0,0,35.9))
parts.append(roof)
solid=Manifold.batch_boolean(parts, __import__('manifold3d').OpType.Add)
for c in cuts:solid=solid-c
# The gallery cut removes its full volume, so restore its true structural columns.
for i in range(1,9):
 x=-57+i*(114/9)
 solid=solid+Manifold.cylinder(8.6,.9,.9,circular_segments=24).translate((x,-13.05,25.0))
 solid=solid+box(x,-13.0,32.45,2.25,2.4,.95)+box(x,-13.0,24.95,2.1,2.25,.9)
# Re-add window transoms because front recesses were subtracted after the main union.
for i in range(18):
 x=-53.83+i*(114/18)
 if abs(x)>=5:solid=solid+box(x,-13.00,7.0,3.7,.8,1.0)
assert len(solid.decompose())==1, 'Detached volume'
mm=solid.to_mesh64()
mesh=trimesh.Trimesh(np.asarray(mm.vert_properties)[:,:3],np.asarray(mm.tri_verts),process=False)
assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
mesh.export(out/'model.stl')
(out/'model-parameters.json').write_text(json.dumps(P,indent=2)+'\n')
print(json.dumps({'extents_mm':mesh.extents.tolist(),'triangles':len(mesh.faces),'volume_mm3':mesh.volume}))
