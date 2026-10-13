"""北藝大活動中心鼓樓段；2018、2024兩相反角度實拍近似，毫米。
含塔下坡端三層窗帶、上層通透樓廊、相鄰曲牆與局部階梯。
活動中心長翼在 +X/+Y 裁短；不是全棟，不含廣場或對面的鐘樓。
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
def profile_x(poly,y,d):return CrossSection([poly]).extrude(d).rotate((90,0,0)).translate((0,y+d/2,0))
def profile_y(poly,x,d):return CrossSection([poly]).extrude(d).rotate((90,0,90)).translate((x-d/2,0,0))
add(0,0,0,112,112,3)
# Solid tower lower floors, and just the adjoining local activity-centre wing.
add(-22,-5,2.8,47,44,75.2)
add(25,7,2.8,47,68,47.2)
add(36,20,49.8,25,40,39.2)
# Broad undulating wall next to tower. It is not a flat horizontal parapet.
points=[(1.3,79),(6,78),(11,76),(16,77),(22,74),(27,75),(33,72),(39,74),(45,79),(48.5,80)]
curve=[]
for (x0,z0),(x1,z1) in zip(points,points[1:]):
 for t in np.linspace(0,1,9,endpoint=False):curve.append((x0+(x1-x0)*t,z0+(z1-z0)*(t*t*(3-2*t))))
curve.append(points[-1]);poly=[(1.3,49)]+curve+[(48.5,49)]
parts.append(profile_x(list(reversed(poly)),-25.7,3.2))
# Local terrace and its solid parapet behind the curved front wall.
add(25,2.5,49,47,58,3.0)
add(48,4,51,3,56,11)
# Three narrow openings on the gray court-facing band below the open gallery.
for x in [-35.5,-22,-8.5]:cut(x,-27.1,57,5.8,4.2,16)
# Single nearby window: three unequal columns and short/tall/short rows.
add(19.0,-28.0,26.5,21.0,4.0,23.0)
cut(19.0,-30.0,29.0,17.5,4.0,18.5)
for x in [14.0,24.0]:details.append(box(x,-29.5,28.9,1.25,2.5,18.7))
for z in [33.0,43.5]:details.append(box(19.0,-29.5,z,17.7,2.5,1.25))
# Downhill outer gable side: gray channels in red brick are NOT a uniform grid.
for y in [-19,-5,9]:
 h=65 if y!=-5 else 42
 cut(-45.6,y,12.0,1.8,8.5,h)
cut(-45.6,-5,9.0,1.8,36.5,4.0)
# Two upper, three middle, one bottom opening, matching the 2024 photograph.
for y in [-19,9]:cut(-45.6,y,61,4.5,6.3,11.5)
for y in [-19,-5,9]:cut(-45.6,y,39,4.5,6.3,12.0)
cut(-45.6,9,17.5,4.5,6.3,11.5)
for z,ys in [(61,[-19,9]),(39,[-19,-5,9]),(17.5,[9])]:
 for y in ys:details.append(box(-44.7,y,z+8.0,2.8,6.55,1.2))
cut(-45.6,11.0,5.5,2.5,2.8,2.2)
cut(-45.6,-18.0,5.5,2.5,10.5,3.5)
# Gallery floor. Both open portal views are supported by the source angles.
add(-22,-5,76.5,47,44,2.5)
for y in [-26.0,16.0]:
 add(-22,y,78,47,2.5,7.7)
 for x in np.linspace(-39.5,-4.5,11):cut(float(x),y,79.3,1.75,3.8,4.9)
# Gable screens: three tall holes, each with a small lower balustrade.
for x in [-44.0,0.0]:
 add(x,-5,78,3.0,44,57)
 for y in [-19,-5,9]:
  cut(x,y,79.3,4.5,7.1,22.5)
  details.append(box(x,y,85.0,3.15,7.3,1.6))
  for yy in [y-2.3,y+2.3]:details.append(box(x,yy,79.1,3.15,1.25,6.1))
# Portal edge columns and top beams; no invented drum object is added inside.
for x in [-44,0]:
 for y in [-26,16]:add(x,y,77.8,4.0,3.0,58.0)
for y in [-26,16]:add(-22,y,132.8,47.8,3.8,4.5)
for x in [-44,0]:parts.append(profile_y([(-28,134),(18,134),(-5,146.8)],x,3.8))
parts.append(profile_y([(-32,133.8),(-5,145.6),(-5,148.0),(-32,136.2)],-22,49.0))
parts.append(profile_y([(-5,145.6),(22,133.8),(22,136.2),(-5,148.0)],-22,49.0))
for x in [-44,0]:parts.append(profile_y([(-12,145.8),(2,145.8),(2,150),(-1,149.2),(-7,146.7)],x,4.8))
for y in [-32,22]:parts.append(Manifold.cylinder(50.0,1.6,1.6,24).rotate((0,90,0)).translate((-47,y,135.0)))
# The near stairs and curved side retaining wall only; further flights are cropped.
for i in range(7):add(26,-47+i*4.2,3,31,4.5,2.6+i*2.6)
add(26,-18.5,3,31,6.5,20.8)
wp=[(-50,3),(-50,8),(-45,8.5),(-39,10),(-34,13),(-29,17),(-24,22),(-18,25),(-15,25),(-15,3)]
parts.append(profile_y(list(reversed(wp)),9.0,3.0))
# Deliberately plain cut ends; no mirrored invented windows.
cut(48.5,23,5,1,29,.7)
cut(25,41,5,40,1,.7)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1,[(p.volume(),p.bounding_box()) for p in solid.decompose()]
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('dimensions_mm',mesh.extents,'watertight',mesh.is_watertight,'volume',mesh.volume)
