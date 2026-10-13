"""NCNU swimming wing observed long-front and balcony-end exterior segment.
Self-built from official/architect photos, mm. Rear and connector cut are plain.
No whole-center floorplan or surveyed dimensions are claimed.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];reliefs=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def hull(p):return Manifold.hull_points(np.asarray(p,float))
def yzpoly(points,x,w):return CrossSection([points]).extrude(w).rotate((90,0,90)).translate((x,0,0))
def bar(p,q,r=.7):
 p=np.array(p);q=np.array(q);v=q-p;L=np.linalg.norm(v)
 return Manifold.cylinder(L,r,r,12).rotate((0,np.degrees(np.arccos(v[2]/L)),np.degrees(np.arctan2(v[1],v[0])))).translate(p)
# Broad flat base includes slightly raised grassy-end platform, no landscaping props.
add(0,0,0,150,100,2.5)
add(0,1,2.4,124,68,55.7)
# Arc across short span, visible large roof overhang and solid upper infill.
ys=np.linspace(-40,40,33);top=61.2+8.5*(1-(ys/40)**2)
roof=list(zip(ys,top))+list(zip(ys[::-1],top[::-1]-1.9))
parts.append(yzpoly(roof[::-1],-67,134))
infill=[(-34,57.6),(34,57.6)]+[(float(y),61.2+8.5*(1-(y/40)**2)-1.6) for y in np.linspace(34,-34,27)]
parts.append(yzpoly(infill,-62,124))
# Long raised roof monitor is visible above the curved roof in official sport-l.
add(0,5.2,68.0,119,11.4,5.6)
add(0,5.2,73.1,123,13.2,1.25)
for x in range(-56,57,7):
 cuts.append(box(x,-.7,70.4,5.6,2.2,2.1))
# Observed long face -Y: five rectangular strip-window bays, not ball-hall diamonds.
for x in [-50,-25,0,25,50]:
 cuts.append(box(x,-33.4,35.7,21.4,3.6,7.0))
 cuts.append(box(x,-33.4,49.7,21.6,3.6,8.5))
 for dx in [-6.9,0,6.9]:reliefs.append(box(x+dx,-33.8,35.5,1.2,3.1,7.6))
 reliefs.append(box(x,-33.8,40.9,22,3.1,1.0))
 for z in [51.1,52.7,54.3]:reliefs.append(box(x,-33.8,z,22,3.1,.95))
 for dx in [-7,-3.5,0,3.5,7]:reliefs.append(box(x+dx,-33.8,56.0,1.15,3.1,2.6))
# Recessed lower right entry and small under-balcony basement bays on the end.
cuts.append(box(49,-33.8,3,17,7,22))
reliefs.append(box(49,-34,3,1.5,6,22))
for x in [-62,-37.5,-12.5,12.5,37.5,62]:
 add(x,-34.1,2.4,2.7,3.5,54.8)
 # Actual triangular eave gussets; both ends overlap wall/roof.
 parts.append(hull([(x+dx,y,z) for dx in [-.8,.8] for y,z in [(-34.5,43.9),(-41.1,60.9),(-33.0,58.8)]]))
 parts.append(bar((x+2.8,-33.0,46),(x+4.5,-39.6,60.4),.7))
for z in [9.0,17.7,30.7,44.5]:add(0,-33.6,z,124,1.8,1.05)
# Balcony at X=-62 photographed end: deep box framed void, rails and inset doors.
cuts.append(box(-62,0,31.5,18,50,18.3))
# Lower bank of three glazed entrances with transoms beneath balcony.
for y in [-18,0,18]:
 cuts.append(box(-62,y,13.1,6,15.6,14.5))
 reliefs.append(box(-63.1,y,13.0,4.6,1.15,14.9))
 reliefs.append(box(-63.1,y,24.2,4.6,16.1,1.1))
# Ground rises toward this end, so basement opening heights are partly concealed.
add(-66,10,2.4,12,52,10.7)
for y in [-29,-20]:cuts.append(box(-62.1,y,2.5,8,6.3,9))
# Protruding balcony floor/side cheek/ceiling are robust genuine solid elements.
add(-63.0,0,29.8,13.0,53,2)
add(-63.0,0,49.0,13.0,53,1.8)
for y in [-25.4,25.4]:add(-63.0,y,30.0,13,2.2,20.3)
for y in np.arange(-22.7,23,5.05):reliefs.append(box(-69.0,float(y),31.5,1.25,1.2,7.0))
for z in [31.6,34.5,37.2]:reliefs.append(box(-69.0,0,z,1.3,49.5,1.05))
# Doors in the balcony back wall, not through-holes or free-floating glazing.
for y in [-17,0,17]:
 cuts.append(box(-54,y,32.0,2.8,13.8,12.8))
 reliefs.append(box(-53.2,y,32.0,3.8,1.2,12.8))
# Prominent red-brick screen wall rises in front of the long facade.
# End at the right is outside connector hall, which is deliberately not included.
add(-13,-38.4,2.4,98,3.0,30.2)
for z in [9,17.7,30.7]:add(-13,-40.0,z,98,1.0,1.05)
# End-wall horizontal bands visible below the curved white gable.
for z in [17.7,30.7,51.8]:add(-62.4,0,z,1.7,68,1.05)
# Plain rear & right cut: no reflected front windows, balconies, or pool claim.
solid=parts[0]
for n,p in enumerate(parts[1:]):
 assert p.status().name=='NoError',(n,p.status());solid=solid+p
for p in cuts:solid=solid-p
for p in reliefs:solid=solid+p
assert solid.status().name=='NoError';assert len(solid.decompose())==1,[(q.volume(),q.bounding_box()) for q in solid.decompose()]
m=solid.simplify(.00001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight)
