"""Photo-derived NTHU exterior miniature, dimensions in millimetres.
2026-10-18 review candidate: front roof/terrace refinement only.
No source 3D assets, survey dimensions, or interior arrangements used.
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
def yz_prism(profile, xmin=-60, width=76):
 # Profile uses (model Y, Z), with rear +Y, front -Y. Extrude along X.
 return CrossSection([profile]).extrude(width).transform(((0,0,1,xmin),(1,0,0,0),(0,1,0,0)))
# Overall body is a deliberately approximate exterior interpretation.
add(0,0,0,150,124,3)
# Rear seven-storey open-book mass. Wings angle away from central spine.
for x,ang in [(-30,-14),(30,14)]:
 parts.append(box(0,0,2.8,66,23,62).rotate((0,0,ang)).translate((x,30,0)))
add(0,32,3,16,27,65)
# Oval front body: three lower levels and an inset fourth level.
# R-03 and B-02 show a curved terrace outside the inset glazed top storey.
# Terrace width, heights and curve samples below are miniature estimates.
parts.append(ellipse(-22,-24,2.8,35,25,29))
parts.append(ellipse(-22,-24,31.3,35,25,1.5))
upper_footprint=ellipse(-22,-24,32.2,28.5,18.5,25)
# Low front roof meets the main roof at Y=-30. The main roof rises toward
# the rear (+Y), unlike the previous X-Z triangular ridge.
roof_profile=[(-44,40.5),(-30,39.8),(-26,40.3),(-22,41.4),
              (-18,43.0),(-14,45.2),(-10,48.0),(-7,50.8)]
body_profile=[(-44,32.2),(-7,32.2)]+list(reversed(roof_profile))
parts.append(yz_prism(body_profile) ^ upper_footprint)
# A 1.3 mm solid roof skin, clipped to a smaller oval than the terrace.
roof_skin=[(y,z-0.25) for y,z in roof_profile]+[(y,z+1.05) for y,z in reversed(roof_profile)]
parts.append(yz_prism(roof_skin) ^ ellipse(-22,-24,32,30,20,25))
# High-side clerestory is attached to the rear end of the upper storey.
# It is part of the front roof, not a new equipment block or extra floor.
clerestory=upper_footprint ^ box(-22,-5.7,32.2,60,3.0,22.3)
parts.append(clerestory)
parts.append(ellipse(-22,-24,54.1,29.5,19.5,1.3) ^ box(-22,-5.7,54,62,4.0,2))
cut(-22,-7.1,50.8,35,1.2,2.5)
# Public entrance connector closes the miniature rather than exposing interiors.
add(25,-6,3,32,26,38)
# Right entrance wing in photo, with supported ground-level arcade.
add(48,-8,3,29,24,48)
cut(48,-20,3.2,24,3.2,10)
for x in [38,58]:column(x,-20.1,3,1.4,11)
# Three broad framed upper window levels and vertical sun fins.
for z in [25,34,43]:
 cut(48,-20,z,24,1.8,7)
 add(48,-21,z-1,29,3,1)
for x in [37,43,49,55,61]:add(x,-20.8,25,1,2.3,25)
# Connector glazed-grid relief, opaque and shallow.
cut(25,-19,7,17,1.4,31)
for x in [18,23,28,33]:det(x,-19.1,7,.8,2,31)
for z in [14,21,28,35]:det(25,-19.1,z,17,2,.8)
# Distinct horizontal long windows in the visible oval front, with solid piers.
for z in [14,25]:
 ring=ellipse(-22,-24,z,35.5,25.5,4)-ellipse(-22,-24,z-.1,33.8,23.8,4.2)
 for x in [-43,-23,-3]:
  cuts.append(ring ^ box(x,-43,z-.1,15,24,4.3))
# Public exterior stair climbing along the curved facade; solid robust risers.
# An approximate position and pitch reproduce the visible sloping outer cheek wall.
for i in range(18):
 add(-31+i*2,-47,2.9,2.2,13,1.5*(i+1))
parts.append(wedge([(-33,3),(5,3),(5,32),(-33,6)],-54,1.6))
add(5,-46,28,4,17,2.3)
# Seven-storey rear wing visible from lawn: recessed glazing bands with deep eaves.
for x,ang in [(-30,-14),(30,14)]:
 for z in [18,29,40,51]:
  cuts.append(box(0,-11.5,z,55,3.5,6).rotate((0,0,ang)).translate((x,30,0)))
  # Broader visible roof and floor shading lines, kept attached to wall.
  details.append(box(0,-11.4,z-1,64,3.2,1.1).rotate((0,0,ang)).translate((x,30,0)))
 for z in [62]:
  details.append(box(0,0,z,67,25,1.2).rotate((0,0,ang)).translate((x,30,0)))
# Robust roof service blocks, placement approximate.



solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
