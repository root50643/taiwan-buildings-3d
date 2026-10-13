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
# Activity centre: short main facade at negative Y, long sawtooth sides from official plans.
add(0,0,0,100,150,3)
add(0,16,2.8,70,111,84)
# Seven plan-supported angled bays down each long side; unseen glazing intentionally omitted.
for x,ang in [(-33,18),(33,-18)]:
 for y in [-26,-11,4,19,34,49,64]:
  parts.append(box(0,0,2.8,12,15,84).rotate((0,0,ang)).translate((x,y,0)))
# Main entrance front extends ahead of the body. Two genuinely open circulation storeys.
add(0,-43,2.8,70,25,84)
cut(0,-52,3,57,30,31)
# Upper central wall set back between round balcony towers.
cut(0,-54,36,66,25,49)
add(0,-38.2,35,35,2.6,49)
# Broad lower window and upper clerestory on the recessed main wall, not invented windows on solid hall wall.
cut(0,-40.2,37,30,5.0,6)
cut(0,-40.2,75,30,5.0,7)
# Continuous floor slabs, piers and front circulation gallery.
for z in [19,34]:details.append(box(0,-48,z,66,21,2.3))
for x in [-30,30]:details.append(box(x,-54,3,3.2,4,32))
# Galleries on each side of the central hall; no artificial horizontal bands across solid central wall.
for x in [-28,28]:
 for z in [35,51,67,83]:details.append(box(x,-45,z,15,24,2.3))
# Semicircular balcony ends: backed arcs, floor-to-floor voids with robust parapet rims.
for x in [-20,20]:
 for z in [35,51,67]:
  disk=Manifold.cylinder(2.3,8,8,circular_segments=36).translate((x,-49,z))
  details.append(disk)
  ring=Manifold.cylinder(7.8,8,8,circular_segments=36)-Manifold.cylinder(8.2,6.3,6.3,circular_segments=36).translate((0,0,-.1))
  # Only outer front semicircle protrudes, its ends overlap the main mass.
  ring=ring ^ box(0,-5,0,18,10,8.2)
  details.append(ring.translate((x,-49,z)))
 # Vertical structural strip at back of balcony stack joins each floor.
 details.append(box(x,-43,34,2.0,7,50))
# Side front galleries visible in side photo: broad recessed gaps rather than invented rear window grids.
for x in [-35,35]:
 for z in [39,55,71]:cut(x,-36,z,9,22,9.5)
# Curved roof cornice over the central front, polygonal approximation of observed shallow bow.
poly=[(-35,-43),(-35,-53),(-25,-57),(0,-59),(25,-57),(35,-53),(35,-43)]
parts.append(CrossSection([poly]).extrude(3).translate((0,0,86)))
# External glass lift at front right: cylindrical mass with modest broad floor bands. Geometry is opaque printable approximation.
column(36,-57,2.8,7,91)
for z in [20,36,52,68,84]:parts.append(Manifold.cylinder(1.5,7.6,7.6,circular_segments=36).translate((36,-57,z)))
for x in [32,40]:details.append(box(x,-62.5,3,1.3,2.4,88))
# Roof perimeter remains plain where not observed.
add(0,71,86,71,1.8,2)
# Back of two-storey entrance is real glazing plane; minor door leaves simplified.
for x in [-20,-8,8,20]:cut(x,-37,5,8,4,11)
for i in range(3):details.append(box(0,-65+i*1.7,2.8,59,2,.6*(i+1)))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
