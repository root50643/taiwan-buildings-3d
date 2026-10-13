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

def sector(r0,r1,a0,a1,z,h):
 angles=np.linspace(math.radians(a0),math.radians(a1),max(3,int(abs(a1-a0)/2)+1))
 pts=[(r1*math.cos(t),r1*math.sin(t)) for t in angles]+[(r0*math.cos(t),r0*math.sin(t)) for t in angles[::-1]]
 return CrossSection([pts]).extrude(h).translate((0,0,z))
def ring(r0,r1,z,h):return (Manifold.cylinder(h,r1,r1,circular_segments=180)-Manifold.cylinder(h+2,r0,r0,circular_segments=180).translate((0,0,-1))).translate((0,0,z))
def radialbox(a,r,z,w,d,h):return box(0,0,z,d,w,h).translate((r,0,0)).rotate((0,0,a))
# Haoran Library, principal plaza-facing exterior segment; NOT a full building survey.
# Source photos: NYCU Museum night exterior and lower colonnade/cylindrical glazing.
# Rear depth stops at a deliberate plain cut backing at y=24.
add(0,0,0,150,89,3)
# Main slab above a genuinely open three-storey colonnade.
add(-3,3,34.6,132,42,61.4)
# Two end piers and continuous deliberate rear cut backing.
add(-65,3,2.8,8,42,33)
add(61,3,2.8,8,42,33)
add(-3,22,2.8,124,4,33)
# Rounded glazed central lower lobby projects forward from the rear backing.
parts.append(Manifold.cylinder(31.9,27,27,circular_segments=96).translate((-1,21,2.9)))
# Source segment excludes the unobserved extension behind the cut line.
cuts.append(box(-1,52,2.7,80,56,34))
# Six deep broad round columns, pairs receding beneath the high suspended slab.
for x in [-45,-21,24,48]:
 column(x,-12,2.8,2.15,32.4)
for x in [-43,46]:column(x,7,2.8,2.15,32.4)
# Lower glazed cylindrical screen, shallow recesses with stout mullions left between bays.
for a in range(198,344,12):
 c=radialbox(a,26.7,6.4,4.2,2.1,23.5).translate((-1,21,0));cuts.append(c)
# Four long horizontal window ribbons, each shallow but legibly recessed.
for z in [38.6,49.8,61.0,72.2]:
 cut(-3,-17.9,z,126,3.3,6.7)
 add(-3,-19.0,z+7.1,130,3.2,1.45)
 for x in range(-64,62,6):details.append(box(x,-17.8,z-.1,1.0,3.7,7.0))
# Roof gallery: actual large rectangular openings and deep inward setback.
for x in [-61,-46.5,-32,-17.5,-3,11.5,26,40.5,55]:cut(x,-17.9,85.0,11.8,15.7,7.4)
# This opened strip retains a continuous rear gallery wall; solid cap 3.5 mm deep.
add(-3,3,95.3,134,44,1.7)
# Raised side service/stair block on the observed right of the principal facade.
add(66,7,2.8,9,34,94.2)
for z in [17,33,49,65,81]:cut(66,-10, z,4.5,2.8,1.6)
# Projecting rectangular entrance bay interrupts the lowest ribbon as in the exterior photo.
# Its deep porch remains open below; not a solid ornamental rectangle.
add(24,-22,25,40,12,11.3)
cut(24,-28,28,33,3.7,5.8)
for x in [11,19,27,35]:details.append(box(x,-27,28,1.1,3.0,5.8))
for x in [5.4,42.6]:add(x,-24,2.8,2.8,10,22.4)
add(24,-29,23.4,43,17,1.9)
# Low offset entry and broad approach steps attached to the building.
for i in range(6):add(24,-39+i*2.0,2.8,79,2.35,.65*(i+1))
# Front middle doors; the back is deliberately a plain scope-cut plane.
cut(0,-6,3,14,4,9)
# Fine cladding joints, trees, temporary signs, sculptures and interiors omitted.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
# Construction canonicalization: weld coincident float32 vertices and collapse only
# repeated-index triangles, then let Manifold simplify exact collinear edges.
from manifold3d import Mesh64
mesh.update_faces(np.array([len(set(f))==3 for f in mesh.faces]))
mesh.update_faces(mesh.unique_faces());mesh.remove_unreferenced_vertices()
solid32=Manifold(Mesh64(np.asarray(mesh.vertices),np.asarray(mesh.faces,dtype=np.uint64)))
assert solid32.status().name=='NoError'
m=solid32.simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.area_faces.min()>1e-9
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
