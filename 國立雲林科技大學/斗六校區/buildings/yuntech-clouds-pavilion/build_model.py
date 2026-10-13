"""國立雲林科技大學觀雲閣外觀縮模。毫米；自建幾何，不含第三方網格。
依校方公開1-13F平面與2021/2024實拍；層高與基座比例為照片估計。
"""
from pathlib import Path
import numpy as np, trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def rotated(part,angle):return part.rotate((0,0,angle))
def facebox(x,y,z,w,d,h,angle=0):return rotated(box(x,y,z,w,d,h),angle)
def stepped_square(w,c=3.3):
 # Three re-entrant steps per corner, from the published 865 cm square footprint.
 a=w/2;b=a-c;s=c/3
 pts=[(-b,-a),(b,-a),(b,-a+s),(b+s,-a+s),(b+s,-a+2*s),(a,-a+2*s),(a,b),(a-s,b),(a-s,b+s),(a-2*s,b+s),(a-2*s,a),(-b,a),(-b,a-s),(-b-s,a-s),(-b-s,a-2*s),(-a,a-2*s),(-a,-b),(-a+s,-b),(-a+s,-b-s),(-a+2*s,-b-s),(-a+2*s,-a)]
 return CrossSection([pts])
# Compact base: tower itself sets the 150 mm maximum extent.
add(0,0,0,76,76,3)
# Two-level open monumental pedestal, preserved as actual open arcades around core.
add(0,0,2.8,66,66,1.7)
add(0,0,3.6,30,30,22.5)
# Three bays per side; all pillars connect the base, cornice and intermediate spandrel.
for angle in [0,90,180,270]:
 for x in [-31,-10.5,10.5,31]:parts.append(facebox(x,-31,4,3.4,3.4,20.2,angle))
 parts.append(facebox(0,-31,13.7,64,3.2,2.1,angle))
 parts.append(facebox(0,-31,21.5,65,3.6,3.2,angle))
 # Facade pilasters are attached, never floating.
 for x in [-31,-10.5,10.5,31]:parts.append(facebox(x,-32,4.5,4.4,2.4,17.5,angle))
 # Closed waist panels on outer arcade preserve the observed upper window openings.
 for x in [-20.7,0,20.7]:parts.append(facebox(x,-31,12.8,18.4,2.8,3.0,angle))
add(0,0,24.2,68.5,68.5,1.4)
add(0,0,25.4,66.5,66.5,1.6)
add(0,0,26.8,68.5,68.5,1.3)
# Tall 1-10F shaft, stepped corners and single-window stack on four elevations.
parts.append(stepped_square(27,3.45).extrude(88.0).translate((0,0,27.4)))
for angle in [0,90,180,270]:
 for z in [33,43,53,63,73,83,93,103]:
  cuts.append(facebox(0,-13.55,z,4.8,2.0,5.4,angle))
  # Stout backed sill, thin muntins omitted at this scale.
  details.append(facebox(0,-13.8,z-.8,6.2,1.5,1.0,angle))
 # Balcony-like dressed relief below observation-storey cornice.
 parts.append(facebox(0,-14.0,109,9.6,2.8,3.1,angle))
 for x in [-3.5,0,3.5]:cuts.append(facebox(x,-15.05,109.8,1.3,1.2,1.45,angle))
# Strong layered cornice beneath glazed observation room.
add(0,0,114.4,30.5,30.5,1.6)
add(0,0,115.8,32,32,1.7)
add(0,0,117.2,30.5,30.5,1.6)
add(0,0,118.6,28.2,28.2,15.7)
for angle in [0,90,180,270]:
 for x in [-8.5,0,8.5]:
  cuts.append(facebox(x,-14.15,121,4.9,2.6,10.4,angle))
  # Fine transverse glazing bars omitted to retain the tall-window reading.
 parts.append(facebox(0,-14.4,132.4,29.7,2.0,1.5,angle))
add(0,0,134,32,32,1.6)
add(0,0,135.3,29.6,29.6,1.4)
# 12F setback and 13F square roof tank, matching the documented 510 cm tier.
add(0,0,136.5,17.9,17.9,11.8)
add(0,0,136.4,20.3,20.3,1.4)
add(0,0,147.8,20.3,20.3,2.2)
# School mark simplified to a sturdy backed medallion, no invented clock hands/text.
for angle in [0,90,180,270]:
 for x in [-6.4,6.4]:parts.append(facebox(x,-9.1,138.2,1.5,1.2,9.7,angle))
 disk=Manifold.cylinder(1.3,3.0,3.0,24).rotate((90,0,0)).translate((0,-8.5,143.5))
 parts.append(rotated(disk,angle))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1,'Disconnected solid'
m=solid.simplify(1e-5).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight)
