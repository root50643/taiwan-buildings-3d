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
# IB international building: plaza-facing connected wings and lower curved pavilion.
# Local x/y coordinates do not claim geographic north. Public 2012 photographs.
add(0,0,0,150,119,3)
# Rear cross-wing, 12 storeys; right main wing continues toward the forecourt.
add(-4,32,2.8,112,26,105)
add(47,-3,2.8,28,96,114)
# Through-ground pedestrian openings seen in the photo; do not fill these with a box.
for x in [-38,-15,8,28]:cut(x,32,3,16,32,10)
# Six genuinely recessed exterior gallery levels above the entrance level.
for z in [16,26,36,46,56,66]:
 cut(-6,18.9,z,87,26,7.8)
 for x in [-50,-28,-6,16,38]:details.append(box(x,20.7,z-.3,3.4,3.6,8.4))
 # balcony parapet is 1.3mm thick, joined to side piers and floor.
 for x in [-39,-17,5,27]:details.append(box(x,19.5,z-.3,18.8,1.5,1.8))
# Upper four enclosed levels, broad sunshade strips, grouped glazing.
for z in [78,87,96,105]:
 for x in [-39,-17,5,27]:cut(x,18.8,z-3.6,18,3.8,3.2)
 add(-6,18,z-.2,103,4.6,1.35)
 for x in [-45,-39,-33,-23,-17,-11,-1,5,11,21,27,33]:details.append(box(x,20.5,z-3.8,1.0,3.2,3.6))
# Left tall elevator/stair: lower regular glazed strip and cap.
add(-61,30,2.8,16,30,114)
cut(-59,14.6,7,9,3.8,99)
for z in range(7,107,10):details.append(box(-59,13.7,z,11,4.0,1.2))
add(-67.2,30,8,3,31,95)
add(-61,29,116,19,32,2.1)
# Inner face of right wing: small deep windows on upper floors.
for z in range(42,111,9):
 for y in [-43,-31,-19,-7,5]:cut(32.8,y,z,4.4,4.8,5.8)
# Street-facing short end: glazed central vertical slot, two differently high side blades.
cut(47,-51,7,12,4,102)
for z in range(10,108,9):details.append(box(47,-51.3,z,12.3,3.4,1.1))
add(58,-44,115,7,14,10)
add(37,-43,115,7,16,4.5)
# Low pavilion curves along the inner side of the perpendicular wing.
# Approximate convex footprint from the completed photo, not a straight replacement.
arc=[(34-26*math.cos(t),-15+33*math.sin(t)) for t in np.linspace(-math.pi/2,math.pi/2,33)]
parts.append(xy(arc,2.8,34))
# Shallow floor-band grooves track the same curved outer edge; panel fields remain solid backed.
for z in [8,15,22,29]:
 # remove a broad skin strip then re-add the deeper core, retaining real curved outline
 outer=xy(arc,z,3.7)
 inner=xy([(x+1.4 if x<33 else x,y) for x,y in arc],z-.1,3.9)
 cuts.append(outer-inner)
# Curved roof lip, supported on the podium rather than a floating ring.
parts.append(xy(arc,36.1,1.6))
# Courtyard stair rises against the rear wing; open court kept empty.
for i in range(7):add(-18,2+i*2.2,2.8,47,2.5,1.3+i*1.5)
# Rear and exterior right elevations are deliberately plain, lacking photo survey.
# Roof/service volumes only those visible over the principal skyline.
add(44,30,116.5,16,21,4)

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
