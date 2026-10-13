"""Public-exterior miniature in millimeters. Rebuild: python build_model.py.
Photo-interpreted, independent scale. No interior or security systems represented.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, OpType
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def detail(x,y,z,w,d,h):details.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def poly(points,z,h):
 if sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))<0:points=list(reversed(points))
 return CrossSection([points]).extrude(h).translate((0,0,z))
def yz(points,x,w):return CrossSection([points]).extrude(w).rotate((90,0,0)).rotate((0,0,90)).translate((x,0,0))
def roof(x,y,w,d,z,rise):
 add(x,y,z-.2,w,d,.75)
 parts.append(yz([(y-d/2,z),(y+d/2,z),(y,z+rise)],x-w/2,w))
def windows(x0,x1,y,zs,w=2.3,h=4.1,step=6):
 for x in np.arange(x0,x1+.01,step):
  for z in zs:cut(float(x),y,z,w,1.4,h)
add(0,0,0,150,100,2.4)
# Lakeside front is -Y. Mountain-roof main library and low information wing.
# Two long ramp solids form the opened-book silhouette; notch remains open to sky.
parts.append(yz([(-25,2.3),(42,2.3),(42,4),(-22,51),(-25,51)],-59,63))
# Chamfer the high front shoulders; broadly photo-estimated, not measured.
cuts.append(poly([(-27.5,-12),(-48,44),(-7,44)],2.5,60))
# Deep recess splitting the mountain-facing wall near the summit.
# Open V-shaped cut produces the two facing triangular walls visible in the approach.
# Window positions are consolidated but now sit on the observed inner faces.
for y in [0,8,16,24,32]:
 height=51-(y+22)*47/64
 for z in np.arange(5,height-3,7):
  for side in [-1,1]:
   x=-27.5+side*(y+12)*20.5/56
   cut(float(x),y,float(z),3.2,2.4,2.2)
cuts.append(CrossSection([[(-70,29),(-49,51),(-49,65),(-70,65)]]).extrude(72).rotate((90,0,0)).translate((0,44,0)))
cuts.append(CrossSection([[(15,29),(15,65),(-6,65),(-6,51)]]).extrude(72).rotate((90,0,0)).translate((0,44,0)))
# Central glazing of the lake facade, framed by the concrete main volume.
cut(-27.5,-25,16,19,2.3,32)
for x in np.arange(-35,-19,3.2):detail(float(x),-24.0,15.9,.8,1.1,32.2)
for z in np.arange(20,47,4.8):detail(-27.5,-24.0,float(z),19.2,1.1,.8)
# Deliberately simplified scattered window rhythm; no claimed exact window schedule.
for i,x in enumerate(np.arange(-55,1,5)):
 if -39<x<-16:continue
 for j,z in enumerate([18,25,33,40]):
  cut(float(x),-25,float(z+(i%3)),1.5+(i+j)%3*.6,1.6,1.5+(i%2)*1.5)
# Low, slightly curved information wing follows a segmented public-photo outline.
pts=[(-67,-34),(-40,-37),(-8,-35),(21,-30),(45,-26),(66,-19),(67,-5),(44,-11),(19,-14),(-9,-17),(-40,-19),(-67,-17)]
parts.append(poly(pts,2.3,12.5))
# Roof band follows the same footprint, supported by solid exterior volume.
parts.append(poly(pts,14.4,1.0))
# Shallow lakefront colonnade and glazing at robust printable depth.
for x in np.arange(-61,62,5.2):
 y=float(np.interp(x,[-67,-40,-8,21,45,66],[-34,-37,-35,-30,-26,-19]))-.45
 cut(float(x),y,3.5,3.2,3.0,9.2)
# Two-storey colonnade horizontal intermediate slab from the lakeside photo.
for x0,x1,y0,y1 in [(-67,-40,-34,-37),(-40,-8,-37,-35),(-8,21,-35,-30),(21,45,-30,-26),(45,66,-26,-19)]:
 for x in np.arange(x0,x1,2):
  yy=float(np.interp(x,[x0,x1],[y0,y1]))
  detail(float(x),yy+.4,8.2,2.2,2.6,.9)
# Distinct intermediate entrance wedge/flat roof at the information wing.
add(41,-13,14.4,18,16,2.7)
# Main exterior texture represented only by narrow horizontal relief accents.

# Grass-facing roof seams indicate roof planes; vegetation and thin railings omitted.
# Low solid entry apron, three broad printable steps on lake front.
for i in range(3):add(-26,-40+i*1.2,2.3,28,1.5,.55*(i+1))

result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.volume>0
mesh.export(OUT/'model.stl')
print(OUT.name,mesh.extents,len(mesh.faces))
