"""Original upper-entry/roof-segment study, millimetres, not the whole museum.
Uses photographed front glass portico and nested curving roof walls; uphill
neighbouring library/research blocks and downhill lower storeys are excluded.
No downloaded third-party mesh. Ground and unknown lower elevations are cropped.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def wave(x,y,z,w,depth=2.4,h=10):
 # Smooth scroll parapet silhouette: flanking shoulders, two low saddles,
 # and the broad central rise seen in the frontal and 2024 rooftop photographs.
 anchors=[(-.5,.78),(-.44,.78),(-.36,.48),(-.25,.39),(-.15,.48),(-.10,.73),(0,1),(.10,.73),(.15,.48),(.25,.39),(.36,.48),(.44,.78),(.5,.78)]
 top=[]
 for (u0,v0),(u1,v1) in zip(anchors,anchors[1:]):
  for t in np.linspace(0,1,7,endpoint=False):
   s=t*t*(3-2*t);top.append((x+(u0+(u1-u0)*t)*w,z+h*(v0+(v1-v0)*s)))
 top.append((x+w/2,z+h*.78))
 return profile([(x-w/2,z-.6),(x+w/2,z-.6)]+list(reversed(top)),y,depth)
def wave_ring(x,y,w,d,z,h):
 for yy in [y-d/2,y+d/2]:parts.append(wave(x,yy,z,w,2.6,h))
 for xx in [x-w/2,x+w/2]:parts.append(wave(0,0,z,d,2.6,h).rotate((0,0,90)).translate((xx,y,0)))
def cylinder_ellipse(x,y,z,w,d,h):return Manifold.cylinder(h,1,1,circular_segments=96).scale((w/2,d/2,1)).translate((x,y,z))
def beam(a,b,r=0.6):
 a=np.array(a);b=np.array(b);v=b-a;l=float(np.linalg.norm(v));v=v/l
 theta=math.degrees(math.acos(v[2]));phi=math.degrees(math.atan2(v[1],v[0]))
 return Manifold.cylinder(l,r,r,circular_segments=12).rotate((0,theta,phi)).translate(tuple(a))
add(0,0,0,150,112,3)
# Cropped segment body: three staggered terrace levels, not five invented floors.
add(-32,7,2.8,74,79,28.5)
add(-33,12,30.8,58,60,5.6)
add(-35,15,35.8,45,46,6.3)
# Broad roof terrace beside the curved tower; boundaries evidenced by 2024 photograph.
add(26,14,2.8,73,64,35.3)
# Three nested raised curved wall outlines, with visible terraced offsets.
wave_ring(-32,7,74,79,30.8,9.5)
wave_ring(-33,12,58,60,35.8,11.0)
wave_ring(-35,15,45,46,41.7,11.8)
# Front banner wall is architectural surface; ephemeral exhibition banners omitted.
add(12,-31,2.8,33,3,39.5)
add(12,-32.2,41.5,34,2.8,1.5)
# Brick inset is represented as a shallow panel, without artificial brick texture.
cut(4,-32.6,7,25,1.4,19)
# Glass pyramid skylight retained as a closed, backed solid.
parts.append(CrossSection.square((39,39),center=True).extrude(11.4,scale_top=(.025,.025)).translate((-35,15,42.0)))
# Strong edges and diagonal glazing ribs of the actual skylight. Fused into roof.
apex=(-35,15,53.4)
for dx,dy in [(-19.5,-19.5),(-19.5,19.5),(19.5,-19.5),(19.5,19.5)]:details.append(beam((-35+dx,15+dy,42.1),apex,.65))
# Central ridge across each triangular face; backed rather than suspended wireframe.
for dx,dy in [(-19.5,0),(19.5,0),(0,-19.5),(0,19.5)]:details.append(beam((-35+dx,15+dy,42.1),apex,.55))
# Rectangular glass entrance: five major front bays and five side bays;
# three unequal-height visible glazing rows. The frame remains a solid recess model.
add(45,-24,5.7,36,29,49)
add(45,-24,54.2,39,32,1.8)
front_y=-38.5; left=27; right=63
for lo,hi in [(7.2,20.4),(21.8,36.4),(37.8,53.0)]:
 for i in range(5):cut(left+3.6+7.2*i,front_y,lo,5.8,3.4,hi-lo)
# The right-hand curtain wall also has five main bays, viewed in the architect photograph.
for lo,hi in [(7.2,20.4),(21.8,36.4),(37.8,53.0)]:
 for i in range(5):cut(right,-35.6+5.8*i,lo,3.4,4.45,hi-lo)
# Low door frames at front: paired narrow leaves inside the five large structural bays.
for x in [30.6,37.8,45,52.2,59.4]:details.append(box(x,-37.4,7.1,.95,1.4,13.5))
# Sweeping shallow steps. Back halves merge into the entrance platform/segment.
for i in range(5):parts.append(cylinder_ellipse(35,-25,2.9,79-i*3.0,56-i*3.0,.9*(i+1)))
# Low curved wall beside stairs: fixed in the base, no isolated plaque or artwork.
outer=cylinder_ellipse(-1,-24,3,44,50,7)
inner=cylinder_ellipse(-1,-24,2.9,39,45,7.3)
ring=outer-inner
# Retain only the front-left arc.
ring=ring ^ box(-15,-44,2.9,29,28,7.3)
parts.append(ring)
# Back edge: simple roof terrace parapet. Other connected campus wings are omitted.
add(29,45.2,37.7,68,1.8,2.8)
add(62.3,16,37.7,1.8,60,2.8)
# A narrow low service cover visible behind the skylight; plant tanks omitted.
add(-3,30,37.8,14,25,1.5)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1,[(p.volume(),p.bounding_box()) for p in solid.decompose()]
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('dimensions_mm',mesh.extents,'watertight',mesh.is_watertight,'volume',mesh.volume)
