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
# Humanities & Social Sciences: public stepped wings and landmark tower.
# Envelope only. Relative wing depth/angle approximated, not a measured campus plan.
add(0,0,0,150,140,3)
# Two separated fore-wings with a low far connecting block.
add(-44,4,2.8,39,94,58.2)
add(39,-21,2.8,48,48,63.2)
add(39,29,2.8,48,52,78.2)
add(-2,44,2.8,59,23,45.2)
# Left/lower wing front and visible courtyard recessed window bands.
for z in [9,20,31,42,53]:
 cut(-44,-43,z,33,3.5,5.7)
 for x in [-57,-47,-37,-29]:det(x,-43,z,1.2,4,5.7)
 cut(-24.5,-5,z,3.5,70,5.7)
 for y in [-35,-20,-5,10,25,38]:det(-24.5,y,z,4,1.3,5.7)
# Raised front bays / vertical pilasters on outer wing.
for x in [-60,-42,-26]:det(x,-43,3,2,5,58)
# Right higher wing has several setbacks and projecting roof-prows.
for z in [9,21,33,45,57,69]:
 cut(39,-45,z,42,4,6)
 for x in [21,32,43,54,59]:
  if z<65:det(x,-45,z,1.3,4.5,6)
 cut(15,-5 if z<65 else 16,z,4,70 if z<65 else 28,6)
 for y in [-36,-21,-6,9,24,39,49]:
  if z<65 or y>3:det(15,y,z,4.5,1.3,6)
# Expressed concrete floor ledges and stepped piers on court side.
for z in [18,30,42,54,66,78]:det(14,5 if z<66 else 29,z,4,100 if z<66 else 52,1.8)
for y in [-39,-10,20,49]:det(13.5,y,3,5,2,63 if y<0 else 78)
# Distinct broad inward/upward projecting slanted eaves at staggered heights.
for y,z,w,depth in [(-24,65,49,37),(26,80,49,37)]:
 parts.append(wedge([(-8,z+22),(-8,z+18),(w,z-2),(w,z+2)],y,depth))
 # Thick angled brackets connect to facade, fewer than prototype for printing.
 for yy in [y-depth/2+3,y,y+depth/2-3]:
  parts.append(wedge([(-6,z+13),(49,z-5),(49,z+2),(-6,z+20)],yy,2.4))
# Clock tower rises from lower wing, with four upper corner posts/open belfry.
add(-44,19,58.8,14,15,62.2)
for z in [69,82,95,108]:cut(-44,11.5,z,1.8,2.2,6)
add(-44,19,119.5,18,19,2)
for x in [-50,-38]:
 for y in [12.5,25.5]:add(x,y,121,2.6,2.6,12)
# Deep saddle crown silhouette, robust abstraction of the sculptural capital.
parts.append(wedge([(-55,132),(-44,127),(-33,132),(-33,137),(-44,132),(-55,137)],19,21))
# Public courtyard stairs represented as shortened terraces; natural slope omitted.
for i in range(8):add(-4,-53+i*9,3,34,10,1+i*1.4)
# Back faces, distant hidden wing boundaries and tower sculpture details approximate.
solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
