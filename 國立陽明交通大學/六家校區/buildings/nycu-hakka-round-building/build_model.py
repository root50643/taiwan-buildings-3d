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
# Liujia College of Hakka Studies: open circular courtyard, unequal roof heights,
# stepped outer crescent wings and a projecting rear conference drum.
add(0,0,0,150,147,3)
# Closed room backing, with courtyard circulation galleries kept genuinely open.
parts.append(ring(36,49,2.8,30.2))
parts.append(sector(36,49,12,168,32.8,10.2))
# Wide slabs and inner galleries, three front levels / four back levels.
for z in [3,13,23,33]:parts.append(ring(28,50,z,1.65))
parts.append(sector(28,50,12,168,43,1.65))
# Inner thin rails deliberately thickened to 1.2 mm and tied into slab and columns.
for z in [14.4,24.4]:parts.append(ring(28,29.25,z,1.6))
parts.append(sector(28,29.25,12,168,34.4,1.6))
for a in range(0,360,15):
 h=40.5 if 12<=a<=168 else 30.5
 column(29*math.cos(math.radians(a)),29*math.sin(math.radians(a)),2.9,.96,h)
# Nontransparent glazing on room backing is recessed in each actual radial bay.
for a in range(0,360,15):
 for z in [5.2,15.2,25.2]+([35.2] if 12<=a<=168 else []):
  if not 68<=a<=112:cuts.append(radialbox(a,36.1,z,8.2,2.9,6.2))
  cuts.append(radialbox(a,48.7,z,9.5,2.9,6.2))
# Two genuine entrance passages through the front half, not dark painted rectangles.
for a in [238,302]:cuts.append(radialbox(a,42,3,7.7,32,7.8))
# Flat accessible front rooftop terrace and low strong parapet.
parts.append(sector(28,29.3,181,359,34.2,1.5));parts.append(sector(48.7,50,181,359,34.2,1.5))
# Rear roofs form three fan-shaped planes: central higher fan and lower side fans.
# Slight stepped rise approximates radial pitch, not a flat full donut roof.
for a0,a1,zz in [(11,57,44.4),(57,123,46.8),(123,169,44.4)]:
 for r0,r1,dz in [(28,35,.0),(34.5,42,.8),(41.5,51,1.6)]:parts.append(sector(r0,r1,a0,a1,zz+dz,2.0))
 # broad radial edge piers connect all roof steps to the backing ring.
 for a in [a0+.8,a1-.8]:parts.append(radialbox(a,43,41.8,1.4,16,6.4))
# Rear central conference / studio projects inward, visible from courtyard and aerial.
parts.append(sector(18,37,68,112,2.9,41.6))
for z in [6,16,26,36]:cuts.append(sector(17.8,19.6,71,109,z,5.7))
for z in [13,23,33,43]:parts.append(sector(17.3,37,68,112,z,1.6))
parts.append(sector(16.5,38,65,115,44.1,2))
# Outer crescent low wings are not one full ring; open gaps separate them at front and rear.
for a0,a1 in [(-16,61),(119,196)]:
 parts.append(sector(57,66,a0,a1,2.9,11))
 parts.append(sector(56.5,66.5,a0,a1,13.5,1.7))
 parts.append(sector(65.2,66.5,a0,a1,15,1.5))
 for a in range(a0+7,a1,14):cuts.append(radialbox(a,65.8,5,7.5,2.7,6.7))
 # circulation link to the main ring is physically supported on both ends.
 for a in [a0+4,a1-4]:parts.append(radialbox(a,53,12.8,5.6,12,2.1))
# Short front entry canopy on reinforced posts, seen below the terraced ring.
parts.append(sector(48.6,56,244,296,12.1,1.8))
for a in [247,271,293]:column(54*math.cos(math.radians(a)),54*math.sin(math.radians(a)),2.9,1.05,10.6)
# Exterior side stairs climb up between ring and outer crescent.
for sign in [-1,1]:
 for i in range(7):add(sign*(55.2+i*.55),-22+i*1.9,2.9,5.5,2.1,1.4+i*1.7)
# No plants, light poles, railing wires or unsurveyed basement interiors are included.

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
