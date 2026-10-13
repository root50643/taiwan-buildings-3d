"""NTCU Lin Chih-Chu atelier courtyard elevation SECTION, photo-derived millimetres.
Deliberately shallow, blank rear is an arbitrary model cutoff, NOT actual building depth.
Built from primitives, no external mesh. Single solid with backed facade recesses.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
# SECTION dimension and base. Front is -Y; back is an intentional cut plane.
add(0,0,0,150,32,3)
add(0,2,2.8,138,18,60.2)
add(0,1.8,3,139,18.4,4.5)
# Lower concrete strip and red brick plinth; brickwork omitted below practical resolution.
add(0,-7.4,3,140,2.0,2.5)
# Timber framing is backed relief, never free-standing structural columns.
for x in [-68,-32,-17,0,18,37,53,68]:add(x,-7.25,7,1.4,1.7,54.8)
# Broad weatherboards shallow seams. Interruptions are opened by window cuts below.
for z in np.arange(10.0,60,4.4):cut(0,-7.2,float(z),136,.65,.5)
# Door bay on left: wooden lower panel, three rows of glazing and high transom.
cut(-48,-7.25,21,29,2.0,20)
cut(-48,-7.25,44,29,2.0,5.2)
for x in [-62.8,-48,-33.2]:details.append(box(x,-7.3,8.1,1.4,1.3,41.5))
for x in [-55.4,-40.6]:details.append(box(x,-7.25,21,1.15,1.25,20))
for z in [27.6,34.2,40.4]:details.append(box(-48,-7.25,z,29,1.25,1.15))
for x in [-55.4,-40.6]:details.append(box(x,-7.25,44,1.15,1.25,5.2))
# Door panel recessed seams stay backed.
for x in [-55.4,-48,-40.6]:cut(x,-7.25,9, .6,.8,10)
# Two separately framed gridded windows; decorative narrow bars thickened / reduced.
# Main dimensions and grouping follow NTCU pano502 face 0; NOT columns.
for x,w in [(3,34),(49,28)]:
 cut(x,-7.35,18.5,w,2.2,25)
 for xx in [x-w/2-.8,x+w/2+.8]:details.append(box(xx,-8.0,17.8,1.6,2.6,26.4))
 for zz in [17.7,43.5]:details.append(box(x,-8,zz,w+3.1,2.6,1.6))
 # Recess bottom at -6.25; bars penetrate wall backing so no tiny freestanding edges.
 for xx in np.arange(x-w/2+2,x+w/2,2.5):details.append(box(float(xx),-7.1,18.4,1.0,2.0,25.3))
 for zz in [25.5,36.1]:details.append(box(x,-7.1,zz,w+1.2,2.0,1.0))
 # Separate projecting window hood, anchored deeply in wall.
 add(x,-8.1,45.0,w+5.0,5.8,1.8)
# Door has its own hood and lintel; not a giant fictitious continuous concrete slab.
add(-48,-8.2,50.5,35,6.0,1.8)
add(-48,-7.6,41.4,32,2.4,1.8)
# Visible high upper wood wall and continuous eave. Roof limited to a 12mm cutoff strip.
add(0,-7.6,60.5,142,3.2,2.0)
roof=CrossSection([[(-71,62),(71,62),(71,64.2),(-71,64.2)]]).extrude(22).rotate((90,0,0)).translate((0,12,0))
parts.append(roof)
# Rounded continuous tile edge is deliberately simplified as 1.4mm fused battens.
for x in np.arange(-69,70,3):add(float(x),1,63.9,1.2,22,1.0)
solid=parts[0]
for q in parts[1:]:solid=solid+q
for q in cuts:solid=solid-q
for q in details:solid=solid+q
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print(mesh.extents,mesh.is_watertight,len(mesh.faces))
