"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. Public plan outlines guide massing; interiors are not reconstructed.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def gable(x,y,z,w,d,h):parts.append(profile([(x-w/2,z),(x+w/2,z),(x,z+h)],y,d))
def arch(x,y,z,w,h,depth):
 r=w/2; spring=z+h-r
 pts=[(x-r,z),(x+r,z),(x+r,spring)]
 pts += [(x+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,25)[1:]]
 return profile(pts,y,depth)
def arch_cut(x,y,z,w,h,depth):cuts.append(arch(x,y,z,w,h,depth))
def arch_trim(x,y,z,w,h):
 # Backed relief ring, fused into the wall, not a separate floating shell.
 details.append(arch(x,y,z,w+1.7,h+.85,1.7)-arch(x,y-.1,z-.2,w,h+.2,2.3))
def hip(x,y,z,w,d,h):parts.append(CrossSection.square((w,d),center=True).extrude(h,scale_top=(.72,.03)).translate((x,y,z)))
def column(x,y,z,r,h):parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
def step(x,y,w,n=3):
 for i in range(n):add(x,y+i*1.4,2.8,w,1.7,.7*(i+1))
# Physical education hall: long rectangular hall, distinctive stepped front relief.
add(0,-4,0,96,150,3)
add(0,3,2.8,74,132,53)
# Flat roof edge visible from ground; no invented rooftop equipment.
add(0,3,55,75,133,1.6)
for y in [-63,69]:add(0,y,55.8,75,1.5,1.6)
for x in [-37,37]:add(x,3,55.8,1.5,133,1.6)
add(0,-63,57,58,1.6,1.6)
# Front corner stairs: five small punched window rows, asymmetric upper inset.
for x in [-31,31]:
 for z in [10,19,28,37,46]:cut(x,-63,z,2.4,4,3.3)
for x in [-23,23]:
 for z in [13,25,37,48]:cut(x,-63,z,2.5,4,3.3)
# Large stepped grey perimeter frame drawn as backed relief, with stepped cap.
parts.append(profile([(-33,5),(-31.3,5),(-26.15,40),(-27.85,40)],-64.4,3.2))
parts.append(profile([(31.3,5),(33,5),(27.85,40),(26.15,40)],-64.4,3.2))
for x in [-21,21]:add(x,-64.4,39,12,3.2,1.6)
for x in [-15,15]:add(x,-64.4,39,1.7,3.2,3.1)
add(0,-64.4,41,31.7,3.2,1.6)
# Upper broad thin window row and highest paired panes.
for x in [-10,-5,0,5,10]:cut(x,-63,34,4.1,3.6,2.5)
for x in [-20,-17,-12,-9.3,-6.6,-3.9,-1.2,1.5,4.2,6.9,9.6,12.3,17,20]:
 cut(x,-63,47,1.7,3.5,5)
 details.append(box(x,-63,49.2,1.7,2,1.0))
# Semicircular entrance balcony, borne on two front columns, glazing behind.
parts.append((Manifold.cylinder(3,16,16,circular_segments=48) ^ box(0,-10,0,40,20,4)).translate((0,-62,17)))
for x in [-12,12]:column(x,-69,3,1.25,15)
for x in [-12,-6,6,12]:cut(x,-63,5,4.6,5,10)
# Curved balcony parapet and recessed window band over balcony.
outer=Manifold.cylinder(5,16,16,circular_segments=48)-Manifold.cylinder(6,14.4,14.4,circular_segments=48).translate((0,0,-.5))
parts.append((outer ^ box(0,-9,0,40,20,6)).translate((0,-62,19)))
for x in [-13,-7,0,7,13]:cut(x,-63,26,4.8,3.5,3)
for i in range(5):add(0,-73+i*1.5,2.8,49,2.1,.65*(i+1))
# Observed long east facade: high repeated window groups above two lower rows.
for y in [-52,-42,-32,-22,-12,-2,8,18,28,38,48,58]:
 cut(37,y,43,4,7.6,9)
 for yy in [y-1.4,y+1.4]:details.append(box(36.6,yy,43,2.5,1,9))
for y in [-49,-35,-21,-7,7,21,35,49]:
 for z in [9,22,33]:cut(37,y,z,4,10,6)
# Deep colonnade impression: piers proud of backed glazing, not filled front blocks.
for y in [-54,-40,-26,-12,2,16,30,44,55]:add(38.2,y,3,4.2,1.8,36)
add(38,1,38,4,113,1.7)
# Side portal projects from mid-left long facade; rear/other side left unobserved plain.
add(41,-24,19,12,30,2.2)
for y in [-36,-12]:add(42,y,3,3,2.8,17)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
