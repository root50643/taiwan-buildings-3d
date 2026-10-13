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

def segment(x,y,z,w,h,rise,depth):
 spring=z+h-rise
 pts=[(x-w/2,z),(x+w/2,z),(x+w/2,spring)]
 pts += [(x+w/2*math.cos(t),spring+rise*math.sin(t)) for t in np.linspace(0,math.pi,33)[1:]]
 return profile(pts,y,depth)
def segment_trim(x,y,z,w,h,rise,th=2.0):
 return segment(x,y,z,w+2*th,h+th,rise+th,2.4)-segment(x,y-.1,z-.2,w,h+.2,rise,3.2)
# Historical 2024 visible building wing segment only. Rear cutoff intentionally plain, no invented room plan.
add(0,0,0,150,110,3)
# Raised masonry plinth, setback lower wing and projecting timber gabled bay.
add(-29,8,2.8,78,56,7);add(35,-31,2.8,59,35,7)
add(-29,8,9.5,78,56,42);add(35,-31,9.5,59,35,44)
# Observable long clapboard courses, exaggerated enough to fuse and resolve in print.
for z in range(12,52,4):
 add(-29,-20.1,z,78,.8,.8)
 add(35,-48.6,z,59,.8,.8)
# Heights follow the visible 2024 eave/ridge ratio; unseen rear is capped at69, not reconstructed as a tall roof.
# Lower long-wing roof: hipped end approximated; upper main bay has a clipped gable nose.
parts.append(CrossSection.square((86,64),center=True).extrude(11,scale_top=(.72,.04)).translate((-29,8,51)))
roof=profile([(2,53),(68,53),(35,69)],-31,43)
parts.append(roof)
# Clip upper front peak: visible half-hip, not a false full triangular gable.
wedge=profile([(-56,64),(-39,69),(-39,86),(-56,86)],-35,76).rotate((0,0,90))
cuts.append(wedge)
# Exposed gable timber infill under the roof, central attic vent and coarse brackets.
parts.append(profile([(5.5,52),(64.5,52),(43,65),(27,65)],-46.8,3.8))
cut(35,-52.5,57,9,5,8)
for z in [58.5,61.2,63.9]:details.append(box(35,-52.5,z,9.4,2.5,1.0))
for x,h in [(16,7),(25,10),(45,10),(54,7)]:details.append(box(x,-52.7,53,1.8,2.5,h))
# Large main window and smaller tall left-wing opening. Pane bars are minor supported relief.
cut(35,-48.5,16,34,5,27)
## Main fine iron bars deliberately omitted: one broad shallow window recess.

cut(-30,-20,13,22,5,32)
for x in [-34,-26]:details.append(box(x,-19.1,13,1.3,3.6,32))
for z in [25,36]:details.append(box(-30,-19.1,z,22,3.6,1.4))
# Two observed subfloor ventilation openings.
for x in [19,51]:cut(x,-48.5,4,7.5,4,5)
# Added sheet-metal window hood from 2024 image, modeled as thick sloping sheet, not assumed original1926 form.
parts.append(profile([(-55,42),(-48,44),(-48,46),(-55,44)],-35,41).rotate((0,0,90)))
# Simple historic roof edge bands are supported, no tiny decay fragments or roof moss.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
