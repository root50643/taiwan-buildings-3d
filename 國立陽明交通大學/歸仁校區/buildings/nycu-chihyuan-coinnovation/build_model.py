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
# Chih-Yuan Co-Innovation building, Gueiren. Original photo-derived CSG.
# Completed architect photos and published ground plan, not rendered design imagery.
# Coordinates are local; no geographic-north accuracy is claimed.
add(0,0,0,150,140,3)
# Building surrounds a real 50x51 central courtyard; rooms do not fill it.
# Front street wing: 2-storey base + deep open third-floor terrace + 2 upper screened floors.
add(1,-43,2.8,126,23,20.4)
add(9,-38,22.9,108,13,10.4)
add(9,-43,32.8,108,23,20.4)
add(1,-43,22.3,128,25,1.5)
add(9,-43,32.3,111,26,1.5)
add(9,-43,53,111,26,1.6)
# True open third-floor exterior gallery, 8-mm depth and seven piers.
for x in [-43,-25,-7,11,29,47,62]:add(x,-53,23.5,2.0,3.6,9.2)
add(8,-54,23.4,108,1.3,1.6)
# White vertical screening across the two upper storeys, with recessed window groups.
for z in [35.4,45.4]:
 cut(9,-54.0,z,105,3.3,6.3)
 for x in range(-43,64,4):details.append(box(x,-54.7,z-.2,1.1,4.0,7.0))
add(9,-54.9,43.0,111,3.2,1.25)
# Lower asymmetric narrow windows and doors, as documented street elevation.
for z in [5.5,15.5]:
 for i,x in enumerate([-54,-44,-34,-24,-14,-4,6,16,26,36,46,56]):
  cut(x,-54.4,z,3.2 if i%3==0 else 5.3,3.0,6.0)
# Left tall stair tower projects above roof and facade, six glazed levels.
add(-59,-40,2.8,15,31,60.6)
for z in [5,15,25,35,45,55]:
 cut(-59,-56,z,11,3.2,6.8)
 for x in [-62.5,-59,-55.5]:details.append(box(x,-56,z,1.0,3.3,6.9))
 add(-59,-57.0,z+7.0,17,3.4,1.2)
# Open notch through upper side of tower, documented at the projecting skyline.
cut(-59,-36,56,18,19,5.3)
# Rear wing: high 3-storey screen floats over a two-storey deeply recessed colonnade.
add(15,45,22.8,94,23,30.4)
add(15,40,2.8,94,13,20.5)
add(15,45,12.6,95,25,1.7)
add(15,45,22.6,96,26,1.7)
add(15,45,53.0,97,27,1.7)
for x in [-32,-10,12,34,61]:add(x,56,2.8,2.5,3.7,20.7)
# Broad recessed ground glazing and upper open corridor behind the front column line.
for x in [-20,3,26,49]:cut(x,46.3,4.5,16,3.5,6.8)
for x in [-19,5,29,51]:cut(x,46.2,15.4,17,3.4,5.0)
# Nine clearly distinct thin horizontal sunshade bands with staggered folded fins.
# All stock thickened to >=1 mm; original painted yellow accents omitted in monochrome STL.
cut(15,56.25,24.4,92,3.1,27.1)
for j in range(10):
 z=23.7+j*3.2
 details.append(box(15,56.4,z,96,4.0,1.05))
for j in range(9):
 z=24.5+j*3.2
 xs=np.arange(-30+(3.8 if j%2 else 0),62,7.6)
 for x in xs:
  # Truncated chevron plate: printable solid-ended folded-screen impression.
  poly=[(x-1.7,z+2.6),(x-.55,z),(x+.55,z),(x+1.7,z+2.6),(x+.55,z+2.6),(x,z+1.3),(x-.55,z+2.6)]
  details.append(profile(poly,56.5,4.3))
# Left short wing, three-storey end block and vertical circulation / return.
add(-49,29,2.8,23,53,39.6)
add(-49,29,42,25,55,1.5)
# Lower side bay intentionally open, deep portals supported by pillars and rear wall.
cut(-49,29,3,27,36,9.7)
for y in [8,26,46]:add(-59.5,y,2.8,2.5,2.5,10.3)
for z in [15.5,25.5,35.5]:
 for y in [9,22,35,48]:cut(-60.3,y,z,3.2,5.4,6)
 for x in [-54,-45]:cut(x,55.5,z,5.2,3.0,6)
# Left middle link: staggered open landings and stairs, not a solid sidewall.
for z in [13,23,33]:
 add(-46,-6,z,31,27,1.7)
 add(-59,-6,z,3.0,27,9.6)
 add(-32,-6,z,2.5,27,9.6)
# Rear court windows, distinct from outer screen facade.
for z in [25,35,45]:
 for x in [-22,-7,8,23]:cut(x,33.7,z,5.8,3.0,6.7)
# Right side two-level terrace, with three upper storeys at its rear end.
add(53,-2,2.8,22,76,10.3)
add(47,7,12.8,32,57,10.4)
add(51,27,22.8,26,29,30.4)
add(53,-2,12.6,25,79,1.6)
add(47,7,22.6,35,60,1.7)
add(51,27,53,28,31,1.6)
# Tall open wind-corridor portal in the terrace side, a major identifiable feature.
cut(48,-13,13,19,22,8.7)
# Main windows on side upper block and inner court.
for z in [25.4,35.4,45.4]:
 for y in [17,27,37]:cut(64.0,y,z,3.0,4.6,6.4)
 for x in [42,52,60]:cut(x,12.4,z,4.3,3.0,6.4)
for y in [-33,-21,-9,3,15]:cut(64,y,5.0,3,4,6.0)
# Short bridges across courtyard-side gap at upper two levels: actual air remains beneath.
for z in [33,43]:
 add(41,-15,z,44,9,1.7)
 add(41,-18.7,z+1.4,44,1.3,1.7)
 add(21,-15,2.8,2.6,9,40.4)
 add(61,-15,23,2.6,9,20.2)
# Terraces low guards use attached 1.25mm parapets instead of sub-resolution wire railings.
for z,x,y,w,d in [(14,65,-2,1.3,78),(24.1,63,7,1.3,59),(24.1,47,-22.7,33,1.3), (43.4,-60.7,29,1.3,53)]:add(x,y,z,w,d,1.7)
# Exterior stair on right links ground to upper terrace in two attached straight flights.
for i in range(12):add(68,-25+i*2.1,2.9,7.0,2.35,1.05+i*.9)
for i in range(10):add(57,-28+i*1.8,12.7,7,2.1,1.0+i*1.03)
# Central courtyard stays fully open to sky. Landscape and wandering fine handrails omitted.

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
