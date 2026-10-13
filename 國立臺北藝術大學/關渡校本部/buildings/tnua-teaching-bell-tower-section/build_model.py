"""北藝大教學大樓鐘樓段，2023/2024 實拍近似；毫米。自建非測繪。
+Y 是朝教學長翼的截斷背面，-Y 為鐘樓正面。局部量體不是全棟。
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
def profile_x(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def profile_y(poly,x,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,90)).translate((x-depth/2,0,0))
# Short local plinth, no neighbouring research building or complete arts forum.
add(0,0,0,112,100,3)
# Two lower storeys and the front terrace; rear cuts into the teaching wing.
add(0,6,2.8,88,64,45.2)
add(20.5,-5,47.8,47,44,29.2)
add(-25,16,47.8,38,44,12.2)
# Front parapet is stepped and curved, as visible beside the tower.
profile=[(-44,47.4),(-44,59),(-40,59),(-36,60),(-32,64),(-27,65),(-24,65),(-20,69),(-14,70),(-8,74),(-3,76),(-3,47.4)]
# Smooth low-amplitude curved transitions preserve the photo's rolling parapet.
top=profile[1:-1]; sm=[]
for (x0,z0),(x1,z1) in zip(top,top[1:]):
 for t in np.linspace(0,1,7,endpoint=False):sm.append((x0+(x1-x0)*t,z0+(z1-z0)*(t*t*(3-2*t))))
sm.append(top[-1]);profile=[profile[0]]+sm+[profile[-1]]
parts.append(profile_x(list(reversed(profile)),-25,2.6))
# Central projecting front window and door at different depths.
add(-20.5,-27,22.5,18,5,21)
cut(-20.5,-29.5,26,14.5,3,15)
for x in [-25.7,-15.3]:details.append(box(x,-28.8,25.9,1.2,2.8,15.2))
details.append(box(-20.5,-28.8,34,14.6,2.8,1.15))
cut(-20.5,-26,3,15.5,5,17.5)
details.append(box(-20.5,-26.5,3,1.3,3,17.7))
# Three narrow windows in the gray band beneath the bell gallery.
for x in [7,20.5,34]:cut(x,-27.1,53.5,5.7,4,16)
# The partly tree-occluded side shows one wider recessed window near the low wing.
# Unseen windows are not filled with a generic repetitive array.
cut(44.1,20,27,3.8,14,14)
for y in [16,23]:details.append(box(43.0,y,26.9,3,1.2,14.2))
details.append(box(43.0,20,33.8,3,14.2,1.2))
# Bell-gallery slab and front/back balustrades. Slots kept >= 1.6mm.
add(20.5,-5,76,47,44,2.2)
for y in [-25.9,15.9]:
 add(20.5,y,78,47,2.2,7)
 for x in [3.1,7.45,11.8,16.15,20.5,24.85,29.2,33.55,37.9]:cut(x,y,79.2,2.3,3.4,4.5)
# Two thick side screens have three real vertical openings, not generic windows.
for x in [-1.1,42.1]:
 add(x,-5,78,4.8,44,57.5)
 for y in [-19,-5,9]:cut(x,y,85,6,7.2,18)
# Tall open front and rear portal retains the through-view.
for x in [-1.1,42.1]:
 for y in [-25.6,15.6]:add(x,y,77,5.2,3.0,59.2)
for y in [-25.6,15.6]:add(20.5,y,133,47.6,4.2,5)
# Two side gables and two slopes of the small tiled roof; tiles omitted.
for x in [-1.1,42.1]:parts.append(profile_y([(-28,134),(18,134),(-5,146.8)],x,4.8))
# Both slopes are solid 2.4 mm slabs fused along ridge and gable walls.
parts.append(profile_y([(-32,133.9),(-5,146),( -5,148.4),(-32,136.3)],20.5,49.2))
parts.append(profile_y([(-5,146),(22,133.9),(22,136.3),(-5,148.4)],20.5,49.2))
for x in [-1.1,42.1]:parts.append(profile_y([(-11,146),(1,146),(1,150),(-11,150)],x,8.0))
for y in [-32,22]:parts.append(Manifold.cylinder(50.2,1.6,1.6,24).rotate((0,90,0)).translate((-4.6,y,135.0)))
# Thickened horizontal carrier and hanging bell: print supports needed underneath.
add(20.5,-5,118.5,42.8,2.6,2.6)
parts.append(Manifold.cylinder(14,1.2,1.2,24).translate((20.5,-5,105)))
parts.append(Manifold.cylinder(6.4,3.6,2.0,32).translate((20.5,-5,99)))
add(20.5,-5,98.5,7.4,6.7,1.3)
# Local front landing and left stair, simplified but not a fictitious full plaza.
add(-5,-37,3,91,18,3.6)
for i in range(9):add(-46,-33+i*5,3,9.6,5.4,3.4+i*3.8)
# Curving stair-side retaining wall rises into the adjacent low teaching volume.
wall=[(-38,3),(-38,8),(-33,10),(-28,13),(-23,15),(-18,17),(-13,20),(-8,24),(-3,27),(2,30),(7,35),(12,41),(16,45),(16,3)]
parts.append(profile_y(list(reversed(wall)),-51,2.6))
# Deliberately plain truncated rear: only shallow cut marker, no invented fenestration.
cut(-18,38,6,43,1.0,.65)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1,[(p.volume(),p.bounding_box()) for p in solid.decompose()]
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('dimensions_mm',mesh.extents,'watertight',mesh.is_watertight,'volume',mesh.volume)
