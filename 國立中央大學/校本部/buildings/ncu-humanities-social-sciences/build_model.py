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
# Stepped courtyard complex, front lecture/theatre block, tall teaching bar and outdoor stair.
add(0,0,0,150,146,3)
# Tall left bar and rear returning wing frame the open courtyard.
add(-42,3,2.8,26,113,78)
add(0,47,2.8,78,25,65)
# Forward taller stair core at the left terminus, and slightly lower rear roof frame.
add(-43,-43,2.8,25,20,86)
cut(-44,-53,13,7,3,70)
for z in range(21,78,13):details.append(box(-44,-53,z,7.8,2,1.4))
# Narrow alternating facade window slots on inward face of tall bar.
for y in [-30,-13,4,21,38]:
 cut(-28.8,y,27,3,5.2,47)
 for z in [39,53,67]:details.append(box(-29.3,y,z,3,6,1.4))
# Rear court elevation is a continuous strip of narrower vertical openings.
for x in [-26,-12,2,16,30]:cut(x,34.5,25,4.8,3,33)
# Raised front theatre / teaching volume is distinctly lower and projecting.
add(37,-16,2.8,48,68,42)
# Main upper frontal bay projects with a thick shaded top/side frame.
add(37,-52,32,45,9,12)
cut(37,-57,33.5,40,3,8)
for x in [21,31,41,51]:details.append(box(x,-57,33.5,1.1,2,8))
# Raised public platform through the courtyard, open under the central portion.
add(-9,-27,17,62,17,3)
for x in [-33,8]:add(x,-30,3,2.6,5,14.2)
add(-8,-39,17,10,29,3)
# Central rear cross-bridge and thick printable rail, seen in architect courtyard photo.
add(2,11,28,65,6,2.5)
add(2,8.3,30.2,65,1.3,2.5)
# Exterior stair ascends from right foreground to raised platform at center-left.
for i in range(19):
 x=56-i*3.4
 add(x,-53,2.8,3.7,12,1+i*.85)
# Retaining triangular stair-side wall follows the real rising route, not flat box.
parts.append(profile([(-7,3),(60,3),(-7,21)],-59,1.8))
# Side access openings below tall bar/platform.
for y in [-27,-8,11]:cut(-28,y,3,4,12,14)
# Small framed roof structure at rear; interiors remain unmodeled.
for x in [15,32]:add(x,47,67.7,2.2,14,8)
add(23.5,47,75,21,16,2)
# Rear and exterior flank have no reliable full-elevation photographs; intentionally plain.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
