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
# Public low-carbon teaching building exterior. No internal or technical layouts.
add(0,0,0,150,140,3)
# Raised main block, visibly recessed ground colonnade and lower attached wing.
add(10,16,17,102,72,79)
add(12,24,2.8,93,43,14.3)
for x in [-36,-16,4,24,44,59]:add(x,-15,3,3.4,5,14.2)
add(-43,7,2.8,50,99,26.2)
# Main front random-sized square apertures seen through white expanded-metal skin.
for row,z in enumerate([24,38,52,66,80]):
 for j,x in enumerate([-30,-17,-4,9,22,35,48]):
  # Reserved central-right opening is the distinctive projecting orange frame.
  if (22<=x<=48 and 52<=z<=66) or (z==24 and x<-18):continue
  w=[4,7,5,9][(j+row)%4];h=[5,7,4,6][(2*j+row)%4]
  cut(x,-20,z,w,3.4,h)
# Left visible side horizontal recess and individually punctured upper field.
cut(-41,15,36,4,59,9)
for z in [52,66,80]:
 for j,y in enumerate([-12,0,12,24,36,46]):cut(-41,y,z,3.4,5+(j%2)*3,6)
# Orange front box is a genuinely deep framed recess, with back glazing ribs.
cut(32,-20,52,27,12,26)
for x in [17,47]:det(x,-24,50,3.2,14,30)
for z in [50,77]:det(32,-24,z,33,14,3)
for x in [22,32,42]:det(x,-15,52,1.3,3,25)
det(32,-15,61,25,3,1.3)
# Low orange cube at fore-left, distinct from the upper box.
cut(-44,-42.5,5,23,5,21)
for x in [-57,-31]:det(x,-45,4,2.6,9,24)
for z in [4,26]:det(-44,-45,z,29,9,2.5)
for x in [-52,-44,-36]:det(x,-41,5,1.2,4,21)
for z in [12,20]:det(-44,-41,z,23,4,1.2)
# Low side has a broad glazed strip; lower podium boundaries simplified.
cut(-67.5,9,9,3.4,83,11)
for y in range(-28,49,8):det(-67.5,y,9,4,1.2,11)
# Opposite publicly photographed garden side: exposed balcony bands, shallower left mesh.
for z in [37,51,65,79]:
 cut(32,52,z,53,5,8)
 for x in [10,24,38,52]:det(x,52,z,1.5,5.5,8)
 for x in [-31,-16,-3]:cut(x,52,z,5,3,5)
# Ground garden glass visible under main block to right.
cut(32,45.5,5,46,3,9)
for x in [12,24,36,48]:det(x,45.5,5,1.3,3.5,9)
# Mesh weave represented by sparse shallow attached horizontal ribs, not copied skin.
# Microscopic expanded-metal weave omitted; square aperture pattern retained.
# Upper parapet, solid simplified roof; no plant or services modeled.
add(10,16,95,105,75,2)
add(-43,7,28,52,101,1.8)
solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
