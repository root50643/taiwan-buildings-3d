"""Original TNNUA exterior miniature, millimetres. Public photo-derived estimates.
Run: python build_model.py. No source 3D assets or interior/security details used.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def det(x,y,z,w,d,h):details.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def ellipse(x,y,z,rx,ry,h):return Manifold.cylinder(h,1,1,circular_segments=128).scale((rx,ry,1)).translate((x,y,z))
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def slope(poly,width):return CrossSection([poly]).extrude(width).rotate((90,0,90)).translate((-width/2,0,0))
def col(x,y,z,r,h):parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
add(0,0,0,150,140,3)
# Paired annular elliptical gallery arms wrap the courtyard; open on main axis.
def ring(z,h,outer=(68,82),inner=(49,66)):
 return ellipse(0,10,z,*outer,h)-ellipse(0,10,z-.1,*inner,h+.2)
def curve(z,h,outer=(68,82),inner=(49,66)):
 return ring(z,h,outer,inner)^box(0,11.5,z-.1,142,93,h+.2)
parts.append(curve(2.8,22))
parts.append(curve(24.5,2.1,(69,83),(48,65)))
# Thin continuous ledges trace the same curve rather than straightening it.
for z in [8,19.5]:parts.append(curve(z,1.2,(68.8,82.8),(48.2,65.2)))
# Individual covered openings tangent to the inner curve; their depth is approximate.
for sign in [-1,1]:
 for y in [-27,-10,8,26,44]:
  x=sign*49*math.sqrt(1-((y-10)/66)**2)
  cut(x,y,3.2,10,10,10)
 # Nearer entrance pier, locally higher than the long gallery roof.
 add(sign*49,-31,2.8,15,17,30)
 add(sign*49,-31,32.5,16,18,1.8)
 cut(sign*49,-40,3.2,9,4,12)
 # Outer wall openings limited to visible side groupings.
 for y in [-10,22,44]:
  x=sign*68*math.sqrt(1-((y-10)/82)**2)
  cut(x,y,12,4,8,6)
# Low curved foreground screen follows the courtyard edge with broad central gateway.
low=ring(3,5,(68,82),(66,80))^box(0,-48,2.9,145,35,6)
low=low-box(0,-55,2.8,35,40,7)
parts.append(low)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
