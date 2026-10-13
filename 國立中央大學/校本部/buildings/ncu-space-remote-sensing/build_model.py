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
# Three-storey U courtyard with roof receiver tower and a tilted thick bowl antenna.
add(0,0,0,150,143,3)
add(-46,0,2.8,35,120,49)
add(46,0,2.8,35,120,49)
add(0,40,2.8,93,40,49)
# Deep upper fascia around the three sides, preserving open courtyard.
add(-46,0,49,39,123,5)
add(46,0,49,39,123,5)
add(0,40,49,95,42,5)
# Visible front wings: paired recessed lower windows and high projecting box shades.
for x in [-46,46]:
 for z in [7,22,37]:
  for xx in [x-9,x+9]:cut(xx,-60,z,10,3,7)
  add(x,-61,z+8,31,5,4)
  cut(x,-63,z+9.2,27,5,1.8)
# Inner courtyard long side facades with horizontal box sunshades.
for side in [-1,1]:
 for y in [-46,-22,2,23]:
  for z in [7,22,37]:
   cut(side*28.5,y,z,3,17,7)
   add(side*27.5,y,z+8,5,21,4)
   cut(side*25.5,y,z+9.2,5,17,1.8)
# Courtyard rear bar.
for x in [-20,0,20]:
 for z in [7,22,37]:
  cut(x,20,z,14,3,7)
  add(x,19,z+8,18,5,4)
  cut(x,17,z+9.2,14,5,1.8)
# Entrance porch, robust rather than exact inscription/canopy ornament.
add(0,13,15,35,15,3)
for x in [-14,14]:add(x,7,3,2.5,3,12.2)
cut(0,20,3,15,3,11)
step(0,2,30,3)
# Roof housing below dish; photographed side staircase simplified to robust steps.
add(0,40,53.5,31,28,22)
add(0,40,74.5,38,35,2.6)
for x in [-8,8]:cut(x,26,60,6,3,8)
for i in range(12):add(-19,29+i*1.8,54,5,1.9,(i+1)*1.65)
add(-19,51,72.8,7,6,2)
# Small adjacent rooftop room observed behind dish tower; approximate relationship.
add(36,40,53.5,18,24,10)
add(36,40,62.5,21,27,2)
# Continuous solid support and thickened paraboloid dish: no detached aerial or fine feed cables.
column(0,40,76,3.8,9.2)
rr=np.linspace(0,25,26)
profile_points=[(float(r),float(r*r/100)) for r in rr]+[(float(r),float(r*r/100-2)) for r in rr[::-1]]
profile_points=profile_points[::-1]
dish=CrossSection([profile_points]).revolve(96).rotate((-35,0,0)).translate((0,40,86))
parts.append(dish)
# Feed struts and underside lattice deliberately omitted: unsafe at miniature scale.
# Unseen outer rear and side fenestration not reconstructed.
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
