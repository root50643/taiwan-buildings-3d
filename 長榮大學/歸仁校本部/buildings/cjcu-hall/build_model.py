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
# Main circular bamboo assembly hall with conical metal roof and lantern.
# Exterior-only solid glass mass; no invented hollow interior or hidden bamboo trusses.
add(0,0,0,150,125,3)
column(-12,0,2.8,45,17.2)
# Visible glass facade expressed as recesses between the 24 perimeter posts.
for i in range(24):
 a=2*math.pi*i/24
 column(-12+44.8*math.cos(a),44.8*math.sin(a),3,1.1,18)
# Broad eave, shallow conical slope; proportions follow architect drone photograph.
parts.append(Manifold.cylinder(1.6,59.5,59.5,circular_segments=144).translate((-12,0,19.6)))
parts.append(Manifold.cylinder(19.4,59.5,10.5,circular_segments=144).translate((-12,0,21.0)))
# Raised roof ventilation lantern, vertically ribbed and capped.
column(-12,0,40.1,10.4,8.4)
for i in range(16):
 a=2*math.pi*i/16
 column(-12+10.2*math.cos(a),10.2*math.sin(a),40,0.65,8.8)
parts.append(Manifold.cylinder(1.6,13.4,13.4,circular_segments=96).translate((-12,0,48.2)))
parts.append(Manifold.cylinder(2,13.4,1.4,circular_segments=96).translate((-12,0,49.6)))
# Low round side service annex shown at the right in official completed aerial photo.
column(43,6,2.8,25,12.7)
column(43,6,15.2,26,1.5)
# Exterior glass recesses on main drum do not create an inaccessible inner cavity.
for i in range(24):
 a=360*i/24+7.5
 cuts.append(box(0,-44.9,5,8.5,1.8,12).rotate((0,0,a)).translate((-12,0,0)))
# Entrance threshold blends into the base. Trees, adjoining clock tower and canopy omitted.
step(-12,-48,25,3)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
