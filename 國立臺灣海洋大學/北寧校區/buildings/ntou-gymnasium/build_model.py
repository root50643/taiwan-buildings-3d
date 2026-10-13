"""NTOU gymnasium exterior, self-authored from official photographs. Millimetres.
The stadium-facing curved indoor-track enclosure and flat-roof court hall are one
building. No downloaded 3D mesh, surveyed dimensions, or invented internal rooms.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def along_x(poly,x,length):
 poly=[(round(float(a),5),round(float(b),5)) for a,b in poly]
 if sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1]))<0:poly=poly[::-1]
 return CrossSection([poly]).extrude(length).rotate((90,0,90)).translate((x,0,0))
def cyl(x,y,z,r,h):return Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z))
# Base and the clearly visible rectangular court hall behind the rounded track.
add(0,4,0,150,111,2.8)
add(0,11,2.7,115,68,36.8)
# Slightly raised perimeter parapet surrounding a recessed, solid roof deck.
add(0,11,39.0,118,71,2.2)
cut(0,11,40.0,112,65,2.0)
# The long rounded track enclosure is front of, not the whole of, the court hall.
# Smooth semieliptic outward skin, return embedded into the main hall.
curve=[(-20,15)]
curve += [(-22-19*np.sin(a),15+26*(1-np.cos(a))/2) for a in np.linspace(0,np.pi,41)]
curve += [(-14,41),(-14,15)]
parts.append(along_x(curve,-69,138))
# Recess the two glazed horizontal strips in each span while preserving rounded ribs.
# Cutters only remove the outward 1.0-1.8 mm, leaving solid curved backing.
ribxs=np.linspace(-69,69,13)
for x0,x1 in zip(ribxs[:-1],ribxs[1:]):
 x=(x0+x1)/2
 cut(x,-40.4,26.7,x1-x0-1.7,4.0,7.2)
 cut(x,-37.0,18.4,x1-x0-1.7,6.0,4.0)
 # Narrow supported mullions are relief fixed to the backing, not isolated slivers.
 # Window subdivisions below 0.8 mm at this scale are omitted.
# Transverse raised ribs follow the actual outer curvature and fuse into its shell.
outer=[(-22-20*np.sin(a),14.5+27.4*(1-np.cos(a))/2) for a in np.linspace(0,np.pi,41)]
inner=[(-22-18.5*np.sin(a),15.3+25.9*(1-np.cos(a))/2) for a in np.linspace(np.pi,0,41)]
for x in ribxs:
 details.append(along_x(outer+[(-13,41.9),(-13,14.5)],float(x)-.85,1.7))
# Lower long colonnade with recessed doors and backed window panels.
add(0,-24.0,2.7,138,8.0,12.7)
add(0,-30.0,14.6,140,23,1.7)
for x in ribxs:
 parts.append(cyl(float(x),-35.6,2.7,1.45,12.9))
for i,(x0,x1) in enumerate(zip(ribxs[:-1],ribxs[1:])):
 x=(x0+x1)/2
 if i in [2,5,8]:
  cut(x,-28,3.5,7.3,2.0,8.9)
 else:
  cut(x,-28,7.1,8.4,2.0,4.7)
  # Backed window recess, tiny glazing bars omitted for print resolution.
# End caps: the glass under the long curve is divided into broad backed panels.
for sx in [-1,1]:
 for y,z,w,h in [(-23,18,7,7),(-32,20,6.4,8),(-28,30,7,7)]:
  cut(sx*69,y,z,2.0,w,h)
# Main hall side windows visible in official aerial; hidden rear kept restrained.
for sx in [-1,1]:
 for y in [-13,-1,11,23,35]:
  cut(sx*57.5,y,15,2,8.1,6.6)
  details.append(box(sx*58,y,14.1,1.8,9.7,1.0))
for x in [-46,-23,0,23,46]:
 cut(x,45,15,16,2,6.6)
# Hall base and strong floor bands support the whole flat-roof block.
for z in [13.0,25.0]:
 add(0,11,z,116.3,69.3,1.25)
# Low connection volume where the long barrel overlaps the hall, visible in aerial.
add(0,-14.4,39.0,111,4.8,2.5)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for p in details:solid=solid+p
for p in cuts:solid=solid-p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('Dimensions mm',mesh.extents,'watertight',mesh.is_watertight)
