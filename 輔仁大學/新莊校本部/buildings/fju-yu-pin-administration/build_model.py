"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. No survey or interior data used.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, Mesh64
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
# Cardinal Yu Pin administrative building. 2025 front plus official 2023 entrance.
add(0,0,0,150,94,3)
# Main front block, flanking shallow forward wings and stepped roof line.
add(0,8,2.8,128,48,57)
add(-54,5,2.8,20,54,58);add(54,5,2.8,20,54,58)
# Three storeys below continuous top clerestory: slender full-height recessed slots.
for x in [-36,-27,-18,18,27,36]:
 cut(x,-16,6,3.4,3.4,37)
 for z in [17,30]:details.append(box(x,-16.5,z,3.5,3.5,1.2))
# End wings carry paired punched windows rather than the middle tall slots.
for x in [-55,-49,49,55]:
 for z in [8,21,34]:cut(x,-22,z,3.6,3.5,7.8)
# One broad top window stripe, behind many thin projecting vertical shading fins.
cut(0,-16,47,86,3.3,9)
for x in range(-41,42,4):
 details.append(box(x,-16.8,46,1.1,3.8,12))
# Wing top windows are actually further forward and separately cut.
for side in [-1,1]:
 cut(side*54,-22,48,18,3.4,9)
 for x in range(-7,8,4):details.append(box(side*54+x,-22.8,47,1.1,3.8,12))
# Strong raised roof fascia at center and each end.
add(0,8,58.5,130,49,3.2)
add(-54,5,60.5,22,55,3.0);add(54,5,60.5,22,55,3)
# Screen above the entry, backed by glazing. Open interstices end in dark shallow recess.
add(0,-18,19,27,6,27)
cut(0,-21.1,20,24,3.2,24.5)
for x in range(-11,12,3):details.append(box(x,-21.3,20,1.0,3.1,25))
for z in range(20,46,3):details.append(box(0,-21.3,z,24,3.1,1.0))
# Entry canopy is distinct, on two side jambs, recessed lobby remains visibly open.
cut(0,-16,5,26,9,12)
add(0,-24,16.2,32,15,2.2)
for x in [-14,14]:add(x,-20,4,2.0,9,13.5)
for i in range(6):add(0,-36+i*2,2.8,33,2.4,.8+i*.85)
# Rooftop service room visible right of center; hidden rear layout kept conservative.
add(31,16,61,28,18,8)
cut(24,7,63,4,3,4)
# No statue, temporary banners, tree models, or guessed back windows.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
