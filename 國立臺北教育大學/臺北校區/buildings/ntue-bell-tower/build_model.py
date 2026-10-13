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
# Centennial memorial tower. Multiple public photographs support square four-way openings and crossing gables.
add(0,0,0,110,110,3)
# Broad three-course pedestal; steps represented on four faces, landscape excluded.
add(0,0,2.8,102,102,1.7);add(0,0,4.3,95,95,1.7);add(0,0,5.8,87,87,2)
add(0,0,7.5,84,84,64)
for a in [0,90]:cuts.append(segment(0,0,7.6,56,55,14,90).rotate((0,0,a)))
# Coarse stone base relief and the two-stage projecting cornice.
for x in [-36,36]:
 for y in [-36,36]:add(x,y,7.5,13,13,14)
add(0,0,69.5,88,88,3.5);add(0,0,72.5,94,94,3.5)
# Narrow upper bell chamber and four genuinely open segmental arches.
add(0,0,75.5,66,66,44)
for a in [0,90]:cuts.append(segment(0,0,76,46,36,10,72).rotate((0,0,a)))
# Four triangular gables from crossing pitched roof solids. No imaginary roof machinery.
roof=profile([(-35,118.5),(35,118.5),(0,144)],0,70)
parts.extend([roof,roof.rotate((0,0,90))])
# Four gable face bands, following visible shallow roof overhangs.
for a in [0,90,180,270]:
 band=profile([(-36,118),(-36,121),(0,147),(36,121),(36,118),(0,144)],-35,2.5)
 # CCW wedge strips below are unioned to avoid negative concave polygon orientation ambiguity.
 band=profile([(-36,118),(0,144),(0,147),(-36,121)],-35,2.5)+profile([(0,144),(36,118),(36,121),(0,147)],-35,2.5)
 details.append(band.rotate((0,0,a)))
 # Lower and upper backed stone arch surrounds.
 details.append(segment_trim(0,-42,7.6,56,55,14,3).rotate((0,0,a)))
 details.append(segment_trim(0,-33,76,46,36,10,2.2).rotate((0,0,a)))
 # Clock disc with broad rim; digits and clock time not reproduced.
 disc=Manifold.cylinder(2.2,8.5,8.5,circular_segments=48).rotate((90,0,0)).translate((0,-33,130))
 rim=(Manifold.cylinder(1.2,9.3,9.3,circular_segments=48)-Manifold.cylinder(1.5,7.6,7.6,circular_segments=48).translate((0,0,-.1))).rotate((90,0,0)).translate((0,-34.8,130))
 details.extend([disc.rotate((0,0,a)),rim.rotate((0,0,a))])
# Fused, opaque bell based on historical visible bell; neck joins ceiling, no floating shell.
details.append(Manifold.cylinder(22,10,6,circular_segments=40).translate((0,0,88)))
details.append(Manifold.cylinder(3,11.5,10,circular_segments=40).translate((0,0,86)))
details.append(Manifold.cylinder(10,3,3,circular_segments=24).translate((0,0,109)))
# Small ridge knob, overall original STL height exactly150 mm.
for a in [0,90,180,270]:details.append(Manifold.sphere(3,circular_segments=24).translate((0,-35,147)).rotate((0,0,a)))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
