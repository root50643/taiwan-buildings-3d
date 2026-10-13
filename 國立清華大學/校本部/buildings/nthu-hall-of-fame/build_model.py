"""Original photo-derived NTHU exterior miniature, dimensions in millimetres.
No source 3D assets, survey plans, or interior arrangements used.
Run: python build_model.py (see requirements.txt).
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h): return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h): parts.append(box(x,y,z,w,d,h))
def det(x,y,z,w,d,h): details.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h): cuts.append(box(x,y,z,w,d,h))
def ellipse(x,y,z,rx,ry,h): return Manifold.cylinder(h,1,1,circular_segments=96).scale((rx,ry,1)).translate((x,y,z))
def wedge(poly,y,depth): return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def column(x,y,z,r,h): parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
# Front arc and deep upper balcony follow official whole-front photograph.
add(0,0,0,150,95,3)
# Rounded exterior front section, joined to a deliberately plain inferred back.
front=ellipse(-6,7,2.8,65,34,38) ^ box(-10,-7,2.7,118,48,39)
parts.append(front)
add(-10,12,2.8,118,29,38)
# Deep curved balcony recess beneath the full projecting roof band.
ring=ellipse(-6,7,23,66,35,13)-ellipse(-6,7,22.9,60,29,13.2)
cuts.append(ring ^ box(-10,-20,22.9,110,39,13.3))
# Lower tall glazed groups cut into the curved wall, with broad masonry piers.
for x in [-51,-32,-12,8,27]:
 ring=ellipse(-6,7,5,65.5,34.5,14)-ellipse(-6,7,4.9,63.5,32.5,14.2)
 cuts.append(ring ^ box(x,-22,4.9,14,32,14.3))
# Upper glazing back is a solid wall; mullions are thick and attached.
for x in [-43,-31,-19,-7,5,17,29]:
 yy=7-29*math.sqrt(max(0,1-((x+6)/60)**2))
 det(x,yy,24,1.2,2.5,12)
# Three orange steel ribs are prominent full-height exterior fins in the photo.
for x in [12,19,26]:
 yy=7-34*math.sqrt(max(0,1-((x+6)/65)**2))
 det(x,yy-.6,3,1.8,5,41)
# Left tall louver screen, attached and not a floating sheet.
for z in np.arange(6,38,2):det(-56,-6,float(z),3,19,.8)
# Right entrance facade and broad metal canopy, observed in entrance photograph.
add(51,-3,3,18,29,36)
cut(51,-17.5,5,13,2,11)
cut(51,-17.5,25,13,2,10)
add(48,-26,18,33,20,2)
for x in [33,63]:add(x,-33,3,2.2,2.2,16)
# Canopy's strengthened transverse ribs stay fused in the roof plate.
for x in [35,41,47,53,59]:add(x,-26,19,1.1,21,1.2)
# Entrance relief wall left blank: portraits and lettering are not reproduced.
add(49,-18.5,3,22,2,13)

solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
