"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. No survey or interior data used.
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
# Elliptical, stepped pine-cone auditorium. x-negative is stage/rear.
add(0,0,0,150,118,3)
def ellipse(rx,ry,z,h):return Manifold.cylinder(h,1,1,circular_segments=144).scale((rx,ry,1)).translate((0,0,z))
# Low glazed outer lobby wraps the larger entrance side.
parts.append(ellipse(66,48,2.8,44))
# Main auditorium, clipped longitudinal roof strips with deliberately distinct risers.
for xa,xb,h0,h1 in [(-58,-24,80,83),(-24,-4,78,71),(-4,15,75,68),(15,33,72,64),(33,57,68,57)]:
 sweep=lambda y:.005*y*y
 poly=[(xa+sweep(y),y) for y in range(-50,51,2)]+[(xb+.06+sweep(y),y) for y in range(50,-51,-2)]
 seg=ellipse(58,39,2.8,84)^CrossSection([poly[::-1]]).extrude(90)
 roof=profile([(xa-2,2),(xb+16,2),(xb+16,h1-3),(xa-2,h0+1)],0,110)
 # barrel-like roofs are slightly lowered at the lateral edges.
 barrel=profile([(-55,2),(55,2)]+[(y,84-8*(y/39)**2) for y in range(55,-56,-5)],0,160).rotate((0,0,90))
 parts.append(seg ^ roof ^ barrel)
# Rear white curved stage wall exceeds the stepped roofs, with large open-air stage recess.
rear=ellipse(61,41,2.8,82)^box(-49,0,2,52,100,86)
parts.append(rear)
cut(-61,0,9,14,29,29)
add(-60,0,7,14,32,2)
# Outer foyer horizontal frames are relief on the solid envelope.
for z in [10,17,24,31,38,45]:
 band=ellipse(67,49,z,1.15)-ellipse(64.8,46.8,z-.1,1.5)
 band=band ^ box(28,0,z-1,84,115,4)
 details.append(band)
# Entrance-sector mullions are robust and fuse to curved outer body.
for a in range(-88,89,11):
 t=math.radians(a);x=66*math.cos(t);y=48*math.sin(t)
 details.append(Manifold.cylinder(43,1.0,1.0,circular_segments=12).translate((x,y,3)))
# Exposed curved roof parapet on stage roof, kept fused and thicker than true scale.
rim=(ellipse(61.5,41.5,83,1.8)-ellipse(59.6,39.6,82.8,2.4))^box(-48,0,82,55,100,5)
details.append(rim)
# Connected access bridge is omitted at property split; no floating connector.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
