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
def poly(points,z,h):return CrossSection([points]).extrude(h).translate((0,0,z))
def yz(points,x,w):return CrossSection([points]).extrude(w).rotate((90,0,0)).rotate((0,0,90)).translate((x,0,0))
def roof(x,y,w,d,z,rise):
 add(x,y,z-.2,w,d,.75)
 parts.append(yz([(y-d/2,z),(y+d/2,z),(y,z+rise)],x-w/2,w))
def windows(x0,x1,y,zs,w=2.3,h=4.1,step=6):
 for x in np.arange(x0,x1+.01,step):
  for z in zs:cut(float(x),y,z,w,1.4,h)
add(0,0,0,150,100,2.4)
# Principal photographed four-storey teaching block, not every college courtyard wing.
# Long left bar and taller right bar meet at a square staircase tower.
add(-30,2,2.3,67,25,29.5)
roof(-30,2,69,27,31.6,5.4)
add(36,4,2.3,52,29,34.2)
roof(36,4,54,31,36.2,5.4)
# Stair tower, asymmetric top, sheltered vertical glass strip.
add(5,-2,2.3,18,33,40.5)
add(9,-3,41.8,10,30,2.0)
parts.append(yz([(-19,42),(16,42),(16,46),(-19,43.5)],-5,12))
cut(0,-18.5,5,5.5,2.4,34.2)
for z in [12,20,28,36]:detail(0,-18, z,5.7,1.1,.8)
# Deep facade galleries between white piers, as seen in the school oblique.
# Recesses stay open outwards, not internal rooms. Floors are retained solid.
for x in np.arange(20,60,6.4):
 for z in [4.5,12.3,20.1]:cut(float(x),-10.0,z,4.7,6.0,6.1)
# Recessed glazing sits at the back of the gallery; piers project visibly forward.
for x in np.arange(17,62,6.4):detail(float(x),-11.2,2.3,1.45,2.8,32.4)
for z in [10.4,18.2,26.0]:detail(37,-11.2,z,53,2.8,1.1)
# Left low wing also has narrow recessed bays and continuous white vertical piers.
for x in np.arange(-59,-8,5.8):
 for z in [4.8,12.6,20.4]:cut(float(x),-10.5,z,3.8,4.0,6.0)
for x in np.arange(-62,-5,5.8):detail(float(x),-10.8,2.3,1.25,1.8,28.5)
for z in [10.6,18.4,26.2]:detail(-30,-10.8,z,67,1.8,.9)
# Tower's open vertical recess and four recessed landing bands.
cut(0,-18.2,5,7.0,5.4,34.2)
for z in [11.5,19.5,27.5,35.5]:detail(0,-18.0,z,7.3,5.4,1.0)
# Repeated narrow white piers/window bays on the observed facade.
windows(-59,-8,-10.5,[5.5,13.3,21.1,28.5],2.5,3.2,5.8)
windows(20,59,-10.5,[5.3,13.1,20.9,28.7],2.8,4.0,6.4)
for x in np.arange(17,62,6.4):add(float(x),-11.0,2.3,1.4,1.1,32.4)
# Continuous second-level shading on the higher right wing.
add(37,-11.3,26.6,53,2.4,1.0)
# Rear lower perpendicular wing seen in the official map; plain as less evidenced.
add(-52,25,2.3,19,30,23)
roof(-52,25,21,32,24.8,4.8)
# End-wall paired slot windows visible in oblique evidence.
for y in [-3,5,13]:
 for z in [7,15,23,31]:cut(62.1,y,z,1.4,2.4,3.2)
# Solid front stair plinth and entry landing.
for i in range(5):add(5,-24+i*.95,2.3,19,1.2,.65*(i+1))

result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.volume>0
mesh.export(OUT/'model.stl')
print(OUT.name,mesh.extents,len(mesh.faces))
