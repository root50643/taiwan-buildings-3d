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
# Yangming Library, Information and Research Building.
# Original photo-derived approximate CSG. Local XY, not survey coordinates.
add(0,7,0,142,178,3)
# Unequal-width parallel research wings above the three-floor library plinth.
# Front is the documented library entrance; rear faces uphill.
add(-36,3,2.8,44,112,99.2)
add(37,3,2.8,31,112,95.2)
# The lower library occupies three levels; upper courtyard is not filled.
add(0,3,2.8,105,112,31.2)
# Recessed central entrance with tall connected glazed spine set well back.
cut(1,-47,3,30,28,28.8)
details.append(box(1,-35,3,29,3.6,31.3))
for z in [6,13.8,21.6,29.4]:
 cut(1,-36.3,z,26,1.7,5.8)
 for x in [-10,-3,4,11]:details.append(box(x,-36.7,z,1.0,1.9,6.0))
# Sidewalls of the central raised court: photograph documents glazed galleries.
for z in [38,48.4,58.8,69.2,79.6,90]:
 for y in [-35,-19,-3,13,29,45]:
  cut(-13.5,y,z,2.8,11.5,7.1)
  cut(21.6,y,z,2.8,11.5,7.1)
# Rear ends remain separated above the library plinth, as in official route map.
# No unsupported tall bridge closes this gap.
# A glazed cross-gallery at the entry side links the upper wings over the approach.
add(2,-37,33.4,39,11,61.6)
cut(2,-38,34.5,32,14,57.9)
for z in [33.6,44,54.4,64.8,75.2,85.6,94]:
 add(2,-37,z,38,12,1.6)
for x in [-13,17]:add(x,-42.7,33.5,2,1.8,61.7)
# Inset glass is represented by thick backed panels, not an opaque courtyard filler.
details.append(box(2,-33.2,33.5,31,1.8,61.7))
for z in [37,47.4,57.8,68.2,78.6,89]:
 cut(2,-34.3,z,28,1.0,6.4)
 for x in [-7,2,11]:details.append(box(x,-34.55,z,1.0,2.3,6.5))
# Rooflight lies on the third-floor court deck. It does not close the upper court.
add(3,4,34,25,54,1.2)
for y in [-18,-9,0,9,18,27]:add(3,y,35,26,1.1,1.1)
for x in [-8,3,14]:add(x,4,35,1.1,55,1.1)
# Front left broad stone end has two three-storey projecting bay-window stacks.
# Their solid backs are fused to walls; sunshade lips are thickened for printing.
for x in [-48,-26]:
 for z in [49,59.4,69.8,80.2]:
  add(x,-54,z,11,8,8.9)
  cut(x,-58.2,z+1.3,8.8,2.6,6.1)
  for xx in [x-3.8,x+3.8]:details.append(box(xx,-58,z+1,1.05,2.8,6.8))
  add(x,-55.7,z+8.0,14,12,1.2)
# Narrow unpaired upper/lower windows on the thick front wall.
for x in [-54,-37,-17]:
 for z in [38,90]:cut(x,-53.3,z,3.6,2.6,6.4)
for x in [-43,-30]:
 for z in [38,90]:cut(x,-53.3,z,5.3,2.6,7.0)
# Stone stair tower between the entry and the outer screen wing.
add(19.8,-43,2.8,7,24,97.1)
cut(20,-55.4,7,3.0,2.0,24)
# Right end and long outer elevation: six repeated projecting glass ribbons.
for k in range(6):
 z=35.8+k*10.1
 # End-face glazed projection.
 add(39,-54.7,z,24,8.7,8.9)
 cut(39,-59.2,z+1.3,21.8,2.8,5.9)
 for x in [30,36,42,48]:details.append(box(x,-59.0,z+1.0,1,2.8,6.4))
 add(39,-55.0,z+8.0,27,10.5,1.3)
 # Outer long side, actual full-width window bands with strong horizontal shades.
 cut(52.1,2,z+1.1,3.4,102,6.3)
 for y in range(-44,52,8):details.append(box(52.0,y,z+.9,3.5,1.05,6.8))
 add(53,2,z+7.8,5.2,108,1.4)
# Tall lower colonnade at the outer research wing with true recess behind.
cut(52,2,13.8,13,95,21.3)
for y in [-46,-29,-12,5,22,39,51]:add(55.5,y,13.5,3.0,3.1,23)
add(53,2,34,7,109,2.0)
for z in [17,26]:
 for y in [-38,-21,-4,13,30,46]:cut(45.9,y,z,3.0,11,6.5)
# The lowest library plinth extends under the colonnade and carries a narrow window row.
add(54,2,2.8,11,115,10.8)
for y in range(-46,54,9):cut(59.2,y,5,2.8,4.5,6.6)
# Unseen outer long face deliberately remains plain; no mirrored window array.
# Rear projecting round stair tower: open undercroft and radiating sunshades.
# Position cross-checked with the aerial: inner corner of wide rear wing,
# distinct from the large round tower of the neighboring Biomedical Building.
# Upper wing overhangs a genuinely recessed rear lower gallery.
cut(-31,56,14,55,15,19.6)
for x in [-57,-28,-14]:details.append(box(x,57,13,3.2,4,21.5))
column(-22,62,34.0,10.0,62.3)
details.append(box(-22,65,13,5.6,6.6,21.5))
for z in [38,48.4,58.8,69.2,79.6,90]:
 cut(-44,59,z,21,3.0,6.6)
# Visible rear end window fields; middle connector's unseen panes are omitted.
for z in [38,48.4,58.8,69.2,79.6,90]:
 cut(39,59,z,23,3,6.4)
 add(39,59,z+7,25,4.5,1.2)
for k in range(6):
 z=35.5+k*10.2
 parts.append(Manifold.cylinder(1.25,11.9,11.9,circular_segments=48).translate((-22,62,z+8.2)))
 for ang in [15,45,75,105,135]:
  a=math.radians(ang);px=-22+10*math.cos(a);py=62+10*math.sin(a)
  cuts.append(box(0,0,z+1.5,4.7,2.7,5.6).rotate((0,0,ang-90)).translate((px,py,0)))
# Rear uphill stair landing, photographed high doorway and external broad stair.
add(-8,61,2.8,104,11,10.3)
for i in range(10):add(-9,86-i*2.1,2.8,60,2.4,1.05+i*1.03)
# Rear two-storey recessed glazing, photographed behind the freestanding columns.
for z in [16,25]:
 for x in [-51,-37,-23]:cut(x,48.3,z,9,2.5,6.2)
# Four cylindrical entry columns carry a deep perforated pergola at three-floor height.
for x in [-21,-7,7,21]:column(x,-62,3,1.55,28.0)
add(0,-62,30,54,3.3,2.0)
add(0,-46,30,54,3.0,2.0)
for x in [-26,-18,-10,-2,6,14,22,26]:add(x,-54,30,1.8,19,2.0)
# Lower arrival canopy has separate shorter columns, matching observed nested frame.
for x in [-13,13]:column(x,-66.5,3,1.35,11.0)
add(0,-59,13,31,19,1.9)
for i in range(5):add(0,-71+i*1.25,2.8,34,1.6,.55*(i+1))
# Distinct rooftop plant enclosures; small ducts omitted, documented roof volumes retained.
add(-33,9,101.6,23,57,5)
add(-36,49,101.6,25,17,8)
add(37,8,97.7,19,69,4.4)
add(36,-37,97.7,19,16,7)
# Parapets connect to roof edges and preserve the roof terraces.
for x,w,z in [(-36,44,102),(37,31,98)]:
 for y in [-52.4,58.4]:add(x,y,z-.4,w,1.2,1.8)
 for xx in [x-w/2+.6,x+w/2-.6]:add(xx,3,z-.4,1.2,112,1.8)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
solid=solid.scale((150/178,150/178,150/178))
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
