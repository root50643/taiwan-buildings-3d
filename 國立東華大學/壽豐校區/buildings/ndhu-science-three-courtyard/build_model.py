"""理工三館四翼院落外觀 — 2012–2017 reference approximation, not 2026 as-built.
A/B four-storey L, C/D lower court wings; hand-written miniature-mm CSG.
Official floor guide supplies wing boundaries; obscured roof/service details simplified.
"""
from pathlib import Path
import math,numpy as np,trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
P={'base_mm':[150,116,2.5],'AB_top':41.0,'low_CD_top':11.3,'min_support_mm':1.6}
parts=[];cuts=[];after=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def poly(pts,z,h):return CrossSection([pts]).extrude(h).translate((0,0,z))
def cyl(x,y,z,r,h):return Manifold.cylinder(h,r,r,40).translate((x,y,z))
def gable(x,y,z,w,d,rise,along='x'):
 # Solid shallow roof, long ridge; flat eave thickness 1.2mm avoids razor edges.
 if along=='x':
  cs=[(-d/2,0),(d/2,0),(d/2,1.2),(0,rise+1.2),(-d/2,1.2)]
  m=CrossSection([cs]).extrude(w).rotate((90,0,90)).translate((x-w/2,y,z))
 else:
  cs=[(-w/2,0),(w/2,0),(w/2,1.2),(0,rise+1.2),(-w/2,1.2)]
  m=CrossSection([cs]).extrude(d).rotate((90,0,0)).translate((x,y+d/2,z))
 parts.append(m)
add(0,0,0,*P['base_mm'])
# A and B main teaching/research wings, surrounding rather than filling the court.
add(18,-27,2.4,88,30,38.6)
add(-49,0,2.4,26,94,38.6)
# Connecting lobby and concrete service core at the L bend.
add(-27,-31,2.4,21,26,38.6)
add(-19,-9,2.4,18,9,38.6)
# B north ground floor has an open piloti zone seen in 2012 and 2017 photographs.
cuts.append(box(-49,19.7,2.5,28,43,8.5))
for xx in [-59,-39]:
 for yy in [1,20,39]:after.append(cyl(xx,yy,2.4,1.8,8.9))
# Both B ends retain their supported concrete / glass staircase cores.
add(-37,-43,2.4,8,12,44.2)
add(-47,46,2.4,12,8,40.0)
# C/D are one-storey volumes on the northern/eastern sides, not four-storey duplicates.
add(8,37,2.4,92,20,8.9)
add(58,13,2.4,20,49,8.9)
add(8,37,11.1,94,22,1.6);add(58,13,11.1,22,49,1.6)
# Exterior diagonal ramp rising onto the low classroom roof, broad solid backing.
cs=[(-23,0),(23,0),(23,10.2),(-23,1.0)]
ramp=CrossSection([cs]).extrude(7).rotate((90,0,90)).translate((42,-1,2.4));parts.append(ramp)
# Low roof parapets and thick ramp side wall; no microscopic handrails.
add(8,47.1,12.5,94,1.6,1.6);add(68.1,15,12.5,1.6,43,1.6)
rail=CrossSection([[(-23,1), (23,10.2),(23,11.8),(-23,2.6)]]).extrude(1.6).rotate((90,0,90)).translate((41.6,-1,2.4));parts.append(rail)
# Roof ridges and short robust rooftop ventilators visible above A/B parapets.
gable(18,-27,40.6,85,27,2.4)
gable(-49,0,40.6,23,89,3.7,'y')
for xx in [-9,7,23,39,55]:add(xx,-27,43.0,5.5,3.2,1.6)
add(-37,-43,46.3,10,13.6,1.5)
# Broad glazed lobby face, with a few thick horizontal transoms rather than fine glass mesh.
cuts.append(box(-25,-44.0,10.2,17,3.0,26.0))
for z in [15.8,22.2,28.6]:after.append(box(-25,-43.2,z,18.4,2.0,1.3))
# Main entrance is deeply inset but has a solid interior backing, no unobserved interior rooms.
cuts.append(box(-25,-43.3,3.2,14,5.0,6.2))
after.append(box(-25,-45.2,9.1,18,4.0,1.5))
# Tall stair glass strip at the entrance tower, with supported concrete face.
for z in [5,13,21,29,37]:cuts.append(box(-33,-43,z,2.2,6.0,6.4))
cuts.append(box(-37,-49.1,40.0,4.5,1.9,5.6))
# B south end has a few narrow windows; other plain concrete sections remain plain.
for z in [13,22,31]:cuts.append(box(-57,-47.1,z,3.0,1.8,5.5))
# Integral approach steps; not a full model of the landscaped forecourt.
for i in range(3):add(-25,-48-i*2.0,2.4,24,6.0-i*1.1,2.7-i*.7)
# A south outside: narrow openings, irregular doubles near east, white base below.
for z in [4.0,13.0,22.0,31.0]:
 for xx in [-4,7,18,29,40,51,60]:
  ww=4.6 if xx!=40 else 6.1
  cuts.append(box(xx,-42.0,z,ww,2.1,6.4))
# A courtyard side has projecting balcony boxes, distinct from south facade.
for z in [13,22,31]:
 for xx in [-4,7,18,29,40,51,60]:
  cuts.append(box(xx,-11.9,z,3.6,2.0,6.0))
  after.append(box(xx,-10.5,z,5.3,3.0,1.5))
# B long outside has large shaded recesses over open ground; alternate end top bay is broad.
for z in [13,22,31]:
 for yy in [-34,-22,-10,2,14,26,38]:
  cuts.append(box(-62.0,yy,z,2.8,6.0,7.0))
  after.append(box(-62.8,yy+3.0,z,2.7,1.6,7.0))
  after.append(box(-62.6,yy,z,2.5,6.9,1.1))
# B inner court upper floors, not a mirrored outer grid of projecting fins.
for z in [13,22,31]:
 for yy in [0,12,24,36]:cuts.append(box(-35.9,yy,z,2.2,5.7,6.6))
# A service core horizontal slot windows.
for z in [6,15,24,33]:cuts.append(box(-19,-4.45,z,13,2.0,2.0))
# Main A east stair glazing, a tall relieved strip rather than detached frame.
add(64,-26,2.4,7,29,37)
for z in [5,13,21,29]:cuts.append(box(67.6,-26,z,1.8,18,6.1))
# Ground C and D windows viewed from the rear; unobserved tiny utilities omitted.
for xx in np.arange(-29,48,8):cuts.append(box(xx,47.0,4.0,3.4,2.0,6.2))
for yy in [-4,6,16,26]:cuts.append(box(68.0,yy,4.0,2.0,4.0,6.0))
# B end core rear glazing and robust window openings.
for z in [5,14,23,32]:cuts.append(box(-47,50,z,7.0,2.0,6.5))
solid=parts[0]
for p in parts[1:]:solid+=p
for c in cuts:solid-=c
for p in after:solid+=p
assert len(solid.decompose())==1,[(s.volume(),s.bounding_box()) for s in solid.decompose()]
m=solid.simplify(.001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,len(mesh.faces),mesh.is_watertight)
