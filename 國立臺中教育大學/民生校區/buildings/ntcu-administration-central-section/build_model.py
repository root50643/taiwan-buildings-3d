"""NTCU Administration Building central entrance SECTION, millimetres.
Photo-based estimates, arbitrary cutoff depth, blank rear; NOT entire U-shaped building.
"""
from pathlib import Path
import numpy as np, math, trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent;parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def profile(poly,y,d):return CrossSection([poly]).extrude(d).rotate((90,0,0)).translate((0,y+d/2,0))
def arch(x,y,z,w,h,d):
 r=w/2;rise=w*.20;spring=z+h-rise
 pts=[(x-r,z),(x+r,z),(x+r,spring)]+[(x+r*math.cos(t),spring+rise*math.sin(t)) for t in np.linspace(0,math.pi,33)[1:]]
 return profile(pts,y,d)
add(0,0,0,150,50,3)
# Flat top and back are deliberate SECTION planes. Central bay projects slightly.
add(0,5,2.8,138,26,91.2)
add(0,3,2.8,34,30,96.2)
# Ground-storey stone band and horizontal course lines.
add(0,-8.3,3,140,2.2,4.0)
add(0,-8.2,28.3,140,2.0,2.2)
add(0,-8.2,91.8,140,2.0,2.1)
for z in [9,15,21,27]:cut(0,-8.65,z,137,.8,.55)
# Recessed panels between window groups, visual paired/fluted stone piers.
for x in [-69,-21,21,69]:
 add(x,-8.5,3,3.4,3.0,93.6)
 for z in [12,20,28,38,46,54,62,70,78,86]:cut(x,-10,z,3.6,.5,.45)
# Side bays: three separate tall windows on each storey.
def win(x,y,z,w,h):
 cut(x,y,z,w,2.3,h)
 for xx in [x-w/2-.7,x+w/2+.7]:details.append(box(xx,y-.15,z-.6,1.4,2.4,h+1.2))
 for zz in [z-.9,z+h]:details.append(box(x,y-.15,zz,w+2.8,2.4,1.25))
 # Window dividers are relief, backed 1.2mm into the solid substrate.
 details.append(box(x,y+.35,z,1.05,3.0,h))
 for zz in [z+h*.32,z+h*.67]:details.append(box(x,y+.35,zz,w+1.2,3.0,1.0))
for side in [-1,1]:
 for x in [32,46,60]:
  for z,h in [(7.8,17.5),(38,19.8),(67,19.8)]:win(side*x,-8.5,z,7.4,h)
# Central raised bay: three narrow windows, not generic broad three-bay glazing.
for x in [-10,0,10]:
 win(x,-12.1,41.5,6.4,16.3)
 win(x,-12.1,69,6.4,17.8)
# Top central decorative plaques simplified as backed recesses.
for x in [-10,0,10]:
 cut(x,-12.1,92,6.1,2.0,5)
 details.append(box(x,-12.35,91.8,1.0,1.0,5.7))
add(0,-12.1,88.5,34,2.2,1.8)
# Low castellated parapet strip. Alternating shallow top notches, no false turrets.
add(0,5,93.6,140,26,3.2)
for x in [-57,-36,36,57]:cut(x,-8.2,96.0,3.8,3.4,1.8)
add(0,3,98.2,35.4,30,1.6)
# Central gabled entrance porch: real deep arch void to recessed door, robust jambs.
add(0,-15.5,3,37,16,32.3)
parts.append(profile([(-18.5,34),(18.5,34),(0,44)],-15.5,16))
cuts.append(arch(0,-16,2.8,23,28.5,20))
# Recessed entry back at main-wall face. Fine doors/windows remain backed.
cut(0,-6,4,21,2.0,21)
for x in [-7,0,7]:details.append(box(x,-5.7,4,1.2,2.8,21))
for z in [17,24]:details.append(box(0,-5.7,z,22.2,2.8,1.2))
# Two-layer arch trim penetrates outer masonry to avoid disconnected rings.
outer=arch(0,-23.15,3,27.5,31.8,2.6)
inner=arch(0,-23.15,2.8,23,28.7,4)
details.append(outer-inner)
for x in [-15.6,15.6]:
 add(x,-16,3,6.0,17.0,4.3)
 for z in [8,14,20,26]:cut(x,-23.7,z,6.5,.7,.55)
# Gable coping is sloped, not a rectangular block.
parts.append(profile([(-19.2,34.3),(0,44.8),(19.2,34.3),(19.2,36),(0,46.5),(-19.2,36)],-16,18))
# Plaque panel without invented lettering.
add(0,-23.45,33.8,14,1.5,4.8)
for x in [-4.6,0,4.6]:cut(x,-24.15,34.5,3.2,1.0,3.3)
for i in range(3):add(0,-23+i*1.3,2.9,26,2.6,.7*(i+1))
solid=parts[0]
for a in parts[1:]:solid=solid+a
for a in cuts:solid=solid-a
for a in details:solid=solid+a
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj');print(mesh.extents,mesh.is_watertight,len(mesh.faces))
