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
# Science Hall 1: explicitly LIMITED to observed principal facade and entrance corner.
# Unseen rear is a plain closing cut plane, not a reconstructed rear elevation.
add(0,0,0,150,52,3)
add(0,3,2.8,136,28,94)
# Two-level lower facade has real recessed balconies/windows and heavy vertical screens.
for x in [-54,-27,0,27]:
 for z in [6,21]:
  cut(x,-11.3,z,19,6,11)
  details.append(box(x,-9.9,z,1.2,4,11))
 # Thick low parapet face at each recessed balcony.
 for z in [5,20]:add(x,-13.3,z,19,6,2.4)
for x in [-66,-40,-13,14,40]:add(x,-12.5,3,3.0,5,31)
# Right entrance bay: offset yellow double canopy and broad glazing above.
cut(55,-11.3,5,19,4,14)
cut(55,-11.3,23,21,4,10)
for x in [49,55,61]:details.append(box(x,-12,5,1.2,3.2,14))
add(55,-15.5,19.0,28,9,1.7);add(55,-14.7,21.6,26,8.4,1.4)
for i in range(3):add(55,-21+i*1.9,2.8,27,2.2,.8+i*.65)
# Long projecting belt separates lower two levels from middle two.
add(0,-11.5,34,141,8,1.8)
# Middle two floors, projecting paired central frame and narrow louver strips.
for z in [38,53]:
 for x in [-54,-28,-5,24,47]:
  cut(x,-11.2,z,17,4.5,10.5)
  details.append(box(x,-11.4,z,1.2,4,10.5))
for x in [-66,-40,-15,9,37,62]:add(x,-13,35,2.5,6,32)
for x in [-41,-38,-15,-12]:add(x,-16,36,1.0,12,30)
# Upper frame at left-middle projects around two recessed bays, not a generic window grid.
add(-27,-12,67,46,6,29)
for z in [70,84]:
 for x in [-38,-17]:cut(x,-15, z,16,7,10)
for x in [-49,-5]:add(x,-15,67,2.2,5,29)
# Right upper windows as individually projecting square hoods.
for z in [70,84]:
 for x in [23,47]:
  add(x,-14.3,z-1.4,21,8,13.2)
  cut(x,-17.1,z,16,5.5,9)
  details.append(box(x,-17,z,1.0,4,9))
 # Far left upper window below roof, partially tree-obscured in source.
 add(-60,-13.3,z-1,15,6,12)
 cut(-60,-15.4,z,11,4,8.5)
# Asymmetrical right sign wall stops below roof; side narrow vertical opening.
add(63,0,34.5,10,32,45)
for z in [40,55,70,85]:cut(61,-14,z,3.8,4,8)
add(64,-12,78.6,13,8,1.7)
# Tree motif and perforated screens simplified to backed relief with durable >1mm ribs.
for x in [-41,13]:
 for z in [7,11,24,28,42,46]:cut(x,-15,z,1.2,2,1.5)
add(13,-14,3,1.2,2,92)
# Broad flat eave, no conjectured roof equipment or rear window rows.
for x in [-66,-40,-13,14,40,66]:add(x,1,96.5,2.4,24,7.5)
add(-2,2.5,104,138,32,2)
# Short documented right-side opening; end plane behind it is left plain.
for z in [7,23]:cut(68,3,z,4,13,11)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
