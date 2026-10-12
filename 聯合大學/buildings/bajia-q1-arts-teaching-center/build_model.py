"""NUU Q1 藝文教學中心：official exterior-photo interpretation, mm, front=-Y.
Run python build_model.py. Public photo files are not required for rebuilding.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection,OpType
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def detail(x,y,z,w,d,h):details.append(box(x,y,z,w,d,h))
def yz_prism(points,x,width):
 if sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))<0:points=list(reversed(points))
 return CrossSection([points]).extrude(width).rotate((90,0,0)).rotate((0,0,90)).translate((x,0,0))
# Official aerial verifies the left teaching volume, central glass tower, low link,
# and right flat-roof hall as one exterior group. No neighboring D1/D2 is included.
add(0,0,0,150,100,2.4)
# Front lower storey and stepped main teaching mass; depths remain photo estimates.
add(-29,-7,2.3,66,58,18.4)
add(-38,7,20.5,40,34,30.0)
add(-55,18,2.3,19,26,42.2)
# Tall glass stair/entrance tower inside a substantial rectangular concrete frame.
add(-8,5,20.5,24,36,40.0)
cut(-8,-13,22.5,19,2.2,34.8)
for x in np.linspace(-16.5,.5,8):detail(float(x),-12.6,22.4,.75,2.0,35.0)
# Staggered mullion/transom pattern, characteristic of the photographed glass facade.
for i,x in enumerate(np.linspace(-16.5,.5,8)):
 for z in np.arange(25.5+(i%2)*2.5,56,7.7):detail(float(x),-12.6,float(z),2.7,2.0,.75)
# Concrete tower lintel and roof; retained as flat roof from the aerial evidence.
add(-8,5,59.4,25.5,37,1.6)
# Main window bands to the tower's left, each divided into narrow panes.
for z in [25.0,39.0]:
 cut(-40,-10,z,35.0,1.6,7.9)
 for x in np.arange(-55.5,-23,4.2):detail(float(x),-9.8,z-.1,.85,1.5,8.1)
 detail(-40,-9.8,z+5.7,35.1,1.5,.85)
 add(-40,-10.65,z-.65,35.8,1.5,.85)
# Front low entrance, broad glass door and projecting terrace lintel.
add(-8,-26,2.3,29,13,18.7)
cut(-8,-35.0,3.0,25.5,7.0,15.5)
for x in [-18.6,-13.3,-8,-2.7,2.6]:detail(x,-32.2,2.9,.9,1.6,15.7)
detail(-8,-32.2,14.1,25.6,1.6,.9)
add(-8,-27,20.2,33.0,16.0,2.0)
# Lower left gallery wall, discreet shallow doorway slots visible at its edge.
for x in [-57.5,-26.5]:cut(x,-36,4.3,3.4,1.6,13.5)
# Left terrace band and sparse, thickened rail, not detailed wall artworks.
add(-43,-35.2,20.0,38,2.0,1.6)
for x in np.arange(-61,7,3.8):add(float(x),-31.0,21.5,.95,.95,3.4)
add(-28,-31,24.0,72.0,1.0,.95)
# Right separate-looking hall connected through the low center portion.
add(45,7,2.3,44,43,31.5)
add(45,7,33.0,47,46,1.7)
# Aerial front is a deep glazed panel in a rectangular frame. Exact panes are estimated.
cut(45,-14.5,5.2,36.0,2.1,24.8)
for x in [29,37,45,53,61]:detail(x,-14.1,5.1,.95,2.0,25.0)
for z in [12.8,22.0]:detail(45,-14.1,z,36.2,2.0,.95)
# Low connecting roof behind the documented stair; adjoining openings are not guessed.
add(13,10,2.3,23,34,18.4)
# Two exterior stair runs with central landing, descending toward the forecourt.
# Steps are solid from the ground so there is no enclosed unseen under-stair cavity.
for i in range(12):add(13,-39+i*.9,2.3,15,1.0,.78*(i+1))
add(13,-27.5,2.3,15,3.1,9.4)
for i in range(12):add(13,-25.5+i*.9,2.3,15,1.0,9.4+.78*(i+1))
# Continuous reinforced side walls follow the two slopes and landing.
for x in [5.2,20.0]:
 parts.append(yz_prism([(-39.5,2.3),(-39.5,5.1),(-28.0,14.7),(-26.0,14.7),(-14.0,24.1),(-14.0,2.3)],x,1.5))
# Handrail represented by robust top/vertical members, resting on solid side cheeks.
for x in [6.0,20.7]:
 for y in np.arange(-38.5,-14.0,3.5):
  rise=(y+39.5)/25.5*19.0
  add(x,float(y),5.0+rise,.9,.9,2.5)
 parts.append(yz_prism([(-39,7.4),(-14,26.1),(-14,27.0),(-39,8.5)],x-.6,1.2))
# Hall's upper side edge rail is visible to the right in the gallery oblique.
for y in np.arange(-12.5,28,3.8):add(23.2,float(y),34.5,.95,.95,2.9)
add(23.2,7.5,36.6,.95,42.5,.95)
# Roof rims emphasize the stepped geometry. Backs stay plain because not photographed.
for x,y,w,d,z in [(-38,7,40,34,50.1),(-55,18,19,26,44.1)]:add(x,y,z,w+.8,d+.8,1.2)
result=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
if not mesh.is_watertight or len(mesh.split(only_watertight=False))!=1:
 print([(q.volume,q.bounds.tolist()) for q in mesh.split(only_watertight=False)]);raise RuntimeError('Single watertight exterior boundary required')
mesh.export(OUT/'model.stl');print('Exported',mesh.extents.tolist(),'mm;',len(mesh.faces),'triangles')
