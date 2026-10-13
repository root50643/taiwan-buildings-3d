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
# Yida Corridor, the observed southern museum-end six-bay exterior SECTION.
# This is not the full L-shaped historic building: the north continuation is cut
# off at x=-60; small rooftop vents and the distant east-west wing are excluded.
add(0,0,0,150,74,3)
add(0,6,2.8,120,30,24.8)
# Small black-base plinth rendered as robust relief; the museum rooms are solid.
add(0,6,3,121,31,1.5)
# Main roof higher than lower covered corridor; solid slab with shallow parapet.
add(0,6,27.0,122,32,1.7)
add(0,20.7,28.4,122,2.2,3.2)
add(59.5,6,28.4,2.2,32,3.2)
# Pilasters and windows on the photographed outer long wall.
for xx in [-58,-38,-18,2,22,42,59]:
 add(xx,21,4.3,3.4,2.8,24.4)
 add(xx,21,28.4,4.1,3.5,4.4)
for xx in [-48,-28,-8,12,32,50]:
 cut(xx,21,8.5,11.2,3.9,14)
 details.append(box(xx,20.5,8.5,1.25,2.8,14))
 for zz in [12.4,17.0,20.4]:details.append(box(xx,20.5,zz,12,2.8,1.0))
 add(xx,21,7.2,13,3.2,1.3)
# Arcade front: actual covered walkway depth and octagonal RC columns.
add(0,-15.3,2.9,122,14.6,.9)
add(0,-15.3,24.1,124,15.6,1.8)
add(0,-22.2,24.0,124,2.1,3.1)
for xx in [-59,-39,-19,1,21,41,61]:
 parts.append(Manifold.cylinder(20.8,1.65,1.65,circular_segments=8).rotate((0,0,22.5)).translate((xx,-21.3,3.6)))
 parts.append(Manifold.cylinder(1.5,2.15,2.15,circular_segments=8).rotate((0,0,22.5)).translate((xx,-21.3,3.4)))
 parts.append(Manifold.cylinder(1.6,2.2,2.2,circular_segments=8).rotate((0,0,22.5)).translate((xx,-21.3,22.9)))
# Recessed windows and the museum door behind the arcade. Their small muntins
# are merged into recessed surfaces, not disconnected freestanding fragments.
for xx in [-49,-29,-9,31,50]:
 cut(xx,-9,8.5,11.0,4.1,13.8)
 details.append(box(xx,-8.4,8.5,1.25,2.7,13.8))
 for zz in [12.4,17.0,20.5]:details.append(box(xx,-8.4,zz,11.8,2.7,1.0))
 add(xx,-9,7.3,12.8,3.1,1.2)
# Rounded top doorway seen behind columns, anchored flat glazing surface.
cuts.append(arch(11,-9,3.8,11,19.2,4.5))
details.append(box(11,-8.2,3.8,1.4,3.6,17.5))
# Thin upper clerestory recesses are above the lower corridor roof.
for xx in [-48,-28,-8,12,32,50]:cut(xx,-9,26.0,10,3.1,1.8)
# South end wall window and large corner structural piers.
cut(60,6,8.5,4.2,11.2,14)
details.append(box(59.4,6,8.5,2.8,1.25,14))
for zz in [12.4,17.0,20.4]:details.append(box(59.4,6,zz,2.8,12,1.0))
add(60,6,7.2,3.2,13,1.3)
for yy in [-9,21]:add(60,yy,3.2,4.0,4.0,27.0)
# Current white steel south-end canopy, bounded and thicker than prototype.
# Four corner posts and pitched edge beams are all joined at both ends.
for xx in [61,69]:
 for yy in [-22,22]:add(xx,yy,3.0,1.8,1.8,22.8)
for yy in [-22,22]:add(65,yy,24.3,10,2.0,1.9)
for xx in [61,69]:
 for pp in [[(-23.0,24.2),(0,27.2),(0,29.1),(-23.0,26.1)],[(0,27.2),(23.0,24.2),(23.0,26.1),(0,29.1)]]:
  parts.append(profile(pp,0,2.0).rotate((0,0,90)).translate((xx,0,0)))
add(65,0,27.3,10,1.8,1.7)
# Museum name board relief, no invented tiny letters.
add(62.1,-9,11.2,1.2,3.5,11.2)
# The north end is an intentional flat cut-off; no guessed attachment drawn.
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
