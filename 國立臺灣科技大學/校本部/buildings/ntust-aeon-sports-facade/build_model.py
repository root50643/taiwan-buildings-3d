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

def xy(poly,z,h):
 if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))<0:poly=poly[::-1]
 return CrossSection([poly]).extrude(h).translate((0,0,z))
def rod(a,b,r):
 # Convex hull of two spheres gives a printable rounded strut, with deliberate overlaps.
 return Manifold.batch_hull([Manifold.sphere(r,12).translate(a),Manifold.sphere(r,12).translate(b)])
# TR AAEON / Research and Teaching Building: sports-ground facade segment.
# End and reverse depth are a 22mm study backing; this is not the complete building.
add(0,0,0,150,61,3)
add(0,6,2.8,136,22,97.2)
# Documented ten major floors plus rooftop eleventh block.
# Lower six-level louver zone: left open horizontal bays; six screened groups.
for z in [14,24,34,44,54,64]:
 for x in [-48,-30,-12,6,24,42,60]:
  cut(x,-5,z,14.5,4.4,6.5)
  if x>=-30:
   for dx in [-5.4,-2.7,0,2.7,5.4]:details.append(box(x+dx,-6.2,z,1.15,4.2,6.5))
 # narrow stacked window at left core, deliberately distinct from louver groups
 cut(-64,-5,z,3.8,3.6,5.9)
# Two upper floors of paired square windows, no lower screening carried through them.
for z in [84,94]:
 for x in [-64,-53,-43,-35,-25,-17,-7,1,11,19,29,37,47,55,64]:
  cut(x,-5,z,4.2,3.4,5.1)
# first continuous plain band below upper windows; bounded shallow line only

for x in [-48,-30,-12,6,24,42,60]:cut(x,-5,74,14.5,4.0,6.5)
# End walls plain because their complete fenestration is not observed.
add(0,6,99.6,138,24,1.4)
# Left roof volume has an oversailing flat eave and an open recessed front.
add(-42,7,100.6,40,19,9.2)
cut(-42,-2.6,101.3,34,6,6.5)
for x in [-56,-47,-38,-29]:details.append(box(x,-4.8,101.3,1.6,6,6.5))
add(-42,6.5,109.5,48,27,1.8)
# Small visible right roof equipment room, not an invented floor.
add(48,10,100.6,21,13,3.2)
# Entrance recesses and shallow apron, tennis courts excluded.
for x in [-48,-30,-12,6,24,42,60]:cut(x,6,2.99,13.5,27,8.0)
cut(-64,-5,3,3.8,3.6,8.0)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.apply_scale(150.0/mesh.extents.max())
mesh=trimesh.Trimesh(np.asarray(mesh.vertices,dtype=np.float32),mesh.faces,process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
