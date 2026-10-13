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
# Five-level mechanical hall; front courtyard and projecting right wing.
add(0,0,0,150,126,3)
add(0,28,2.8,130,37,68)
add(-56,0,2.8,18,90,77)
# Upper left-to-middle teaching bar over recessed glazed lower gallery.
add(-11,2,36,93,29,35)
add(48,-10,2.8,34,95,24)
add(48,-12,38,34,96,22)
# Right elevated classroom bar bears on upper recessed lower wing.
add(48,-7,26,29,80,12.3)
# Lower inner gallery recessed behind suspended bar.
add(-6,12,3,94,17,33.5)
for z in [6,23]:
 cut(-10,3.5,z,80,3,9)
 for x in [-45,-28,-11,6,23]:details.append(box(x,3.5,z,1.8,3.5,9))
# Main suspended block windows.
for z in [42,58]:
 for x in [-42,-23,-4,15]:cut(x,-12.5,z,15,3,8)
# Right wing front and courtyard openings.
for z in [29,43]:
 cut(48,-60,z,25,6,9)
 for y in [-46,-26,-6]:cut(31,y,z,3,14,8)
# Low entrance canopy with robust supports.
add(-4,-13,17,96,23,2.2)
for x in [-44,-13,18]:add(x,-23,3,2,2,14.2)
# External staircase at right is visible in official oblique photo.
for i in range(12):add(60,-51+i*3,3,11,3.1,(i+1)*1.85)
add(60,-15,23.5,11,6,2)
# Solar panels already visible above roof in 2014; simplified groups, not complete array survey.
for x in [-17,31]:
 parts.append(profile([(x-9,70.5),(x+9,70.5),(x+9,75),(x-9,72)],28,12))
step(-5,-36,68,3)
# Hidden rear left plain; overall wing depths and roof equipment estimated.
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
