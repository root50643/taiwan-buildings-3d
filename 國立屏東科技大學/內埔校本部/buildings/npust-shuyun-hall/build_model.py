"""述耘堂當代公開影像近似。mm。Front east = -Y; north = -X.
Not a 1990 restoration, survey, or verified 2026 condition.
NLSC aerial footprint; official 2024-upload front; historic photo only for matching visible forms.
"""
from pathlib import Path
import os
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def detail(x,y,z,w,d,h):details.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
# Aerial digitisation approx: main roof 180 x 140 px, entrance annex 65 x 165px.
# Long dimension follows east-west; base 150mm. No invented full-size metres.
roof_rise=float(os.environ.get('SHUYUN_ROOF_RISE','.7'))
rear_height=float(os.environ.get('SHUYUN_REAR_HEIGHT','25'))
add(0,0,0,114,150,2.8)
# Main auditorium shell and narrow lateral service strips, below roof.
add(0,15,2.6,83,94,38)
for x in [-46,46]:add(x,15,2.6,10,94,24)
# Broad main roof with bounded low central rise, not a conspicuous ridge.
add(0,15,39.7,86,97,2)
roof=CrossSection([[[-43,41.0],[43,41.0],[43,41.9],[1,41.9+roof_rise],[-1,41.9+roof_rise],[-43,41.9]]]).extrude(97).rotate((90,0,0)).translate((0,63.5,0))
parts.append(roof)
# Rear narrow attached band seen on aerial; exact elevations unknown.
add(0,65,2.6,92,9,rear_height)
for x in [-47.5,47.5]:
 add(x,64,2.6,10,11,rear_height+3)
 # Taller forward corner walls visible in contemporary/old matching end silhouette.
 add(x,-31,2.6,10,11,43)
# East entrance annex: matching rectangular roof, recessed continuous lower facade.
add(0,-52,2.6,100,38,39.4)
# Entrance front shifted eastward by 10mm to match aerial annex/roof depth ratio.
old_add,old_cut,old_detail=add,cut,detail
def add(x,y,z,w,d,h):old_add(x,y-10,z,w,d,h)
def cut(x,y,z,w,d,h):old_cut(x,y-10,z,w,d,h)
def detail(x,y,z,w,d,h):old_detail(x,y-10,z,w,d,h)
# True portico recess, backed by glazing wall. No invented windows on unseen west facade.
parts[-1]=parts[-1]-box(0,-70,3.4,92,9,25)
# Eighteen broad panels counted on the complete historical matching front.
# Modern cropped view confirms alternating wider structural seams and fine seams.
# Seams cut into a broad solid band: not twenty generic equal-width window slits.
for j in range(1,18):
 x=-49+j*(98/18)
 cut(x,-61.2,33.2,1.25 if j%2 else .65,3.0,5.8)
# Strong horizontal fascia, lintel, and continuous top parapet.
add(0,-61,29,101,2.4,3.3)
add(0,-61,39,101,2.4,3.2)
# Seven bays: 3 side bays, wide central entrance, 3 side bays.
# Eight cylindrical primary columns distinct from glazing mullions.
for x in [-47,-36,-25,-14,14,25,36,47]:
 details.append(Manifold.cylinder(26.5,1.2,1.2,circular_segments=24).translate((x,-71,2.5)))
# Rear wall to the porch begins at y=-55.5; glass panels shallowly recessed.
for x,w in [(-41.5,8),(-30.5,8),(-19.5,8),(0,24),(19.5,8),(30.5,8),(41.5,8)]:
 cut(x,-55.1,4.8,w,1.4,12)
 if x:
  cut(x,-55.1,18.3,w,1.4,8.5)
 else:cut(x,-55.1,18,24,1.4,9)
# Lower red spandrel panels hang in upper portion of six side bays, fused to backing.
# Model relief is rooted into wall; no loose mini-frames.
for x in [-41.5,-30.5,-19.5,19.5,30.5,41.5]:
 detail(x,-57.0,19,8,5.0,7.5)
 detail(x,-58.0,17.3,10.5,5.5,1.5)
# Central entrance glazing divisions backed by continuous glass mass.
for x in np.linspace(-10.8,10.8,9):detail(float(x),-55.0,4.6,.65,3.0,22.6)
for z in [14.2,17.3]:detail(0,-55.0,z,26,3.0,.8)
# Side face of foyer: sparse long upper divisions only, supported by historic matching ends.
for x in [-50,50]:
 for y in [-54,-47,-40]:cut(x,y,33.2,1.4,.9,5.8)
# Broad entry steps are fused to common base.
for i in range(3):add(0,-68+i*1.8,2.6,30,2.5,.5*(i+1))
solid=parts[1]
for p in parts[2:]:solid+=p
for c in cuts:solid-=c
for p in details:solid+=p
solid=solid.translate((0,4.8,0))+parts[0]
solid=solid.scale((.88,1,.88))
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
