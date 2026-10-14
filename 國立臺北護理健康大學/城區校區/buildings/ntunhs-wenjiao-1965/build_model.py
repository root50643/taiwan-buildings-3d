"""國立臺北護理健康大學城區文教大樓：1965 原始主棟外形近似。
原創參數實體，毫米。以1965使照1–4F與校方歷史立面／照片重建。
This is an exterior approximation, not an as-built survey or a 2025 model.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def footprint(poly,z,h):return CrossSection([poly]).extrude(h).translate((0,0,z))
def stairs(start,end,width,z0,z1,n):
 # Continuous inclined structural slab with treads; no isolated step islands.
 x0,y0=start;x1,y1=end;L=math.hypot(x1-x0,y1-y0);dx=(x1-x0)/L;dy=(y1-y0)/L
 angle=math.degrees(math.atan2(dy,dx))
 poly=[(0,z0-1.3),(L,z1-1.3),(L,z1),(0,z0)]
 slab=CrossSection([poly]).extrude(width).rotate((90,0,0)).translate((0,width/2,0)).rotate((0,0,angle)).translate((x0,y0,0));parts.append(slab)
 for i in range(n):
  # Overlap treads into the sloping substrate rather than feathering their base.
  t=(i+.5)/n;zi=z0+(z1-z0)*(i+1)/n
  step=box(L*t,0,zi-1.5,L/n+.08,width,1.5).rotate((0,0,angle)).translate((x0,y0,0));parts.append(step)
 # Fine original handrails are omitted at this miniature scale.
# Front = south = -Y; north = +Y. Thin base is the only invented site element.
add(0,3.2,0,150,64,2.4)
# 1965 open ground-floor column grid. The two broad ends are not infilled classrooms.
xs=[-68,-45,-35,-25,-15,-5,5,15,25,35,45,68]
for x in xs:
 for y in [-20,20]:add(x,y,2.2,1.8,1.8,8.6)
for x in xs[2:-2]:
 for y in [-7,4]:add(x,y,2.2,1.8,1.8,8.6)
# Small original service core and stair cores from 1F diagram, not later classrooms.
add(39.5,-18,2.2,6.6,5.0,8.6)
add(-38.5,11,2.2,1.6,9.6,8.6)
add(-42.0,15,2.2,7.6,1.6,8.6)
# An open interior stair mass is retained under the west-side original stair core.
stairs((-40.5,5.5),(-40.5,13.5),4.0,2.7,7.0,10)
add(-40.5,14.5,5.7,4.0,3.0,1.4)
stairs((-35.8,14.5),(-35.8,7.0),4.0,7.0,10.3,8)
add(-38.1,14.5,5.7,8.8,3.0,1.4)
# Slabs follow end volumes projecting slightly north/south of the central strip.
outline=[(-70.7,-22.3),(-46.3,-22.3),(-46.3,-20.4),(46.3,-20.4),(46.3,-22.3),(70.7,-22.3),(70.7,22.3),(46.3,22.3),(46.3,20.9),(-46.3,20.9),(-46.3,22.3),(-70.7,22.3)]
for z in [9.9,18.6,27.3,36.0]:parts.append(footprint(outline,z,1.25))
# Upper three storeys. Main room backing stops behind open north corridor.
add(0,-2.65,10.1,92.6,34.1,26.1)
for x in [-58.2,58.2]:add(x,0,10.1,24.4,44.9,26.1)
# Continuous south fins. 35 blade axes represent the drawn close-spaced screen;
# every blade is fused into glazing backing, widened to >=1.05mm at miniature size.
for x in np.linspace(-44.8,44.8,35):
 fin=box(0,0,10.6,1.1,3.0,25.5).rotate((0,0,-25)).translate((x,-20.0,0));details.append(fin)
# Glazing transom relief and visible storey bands behind the screen.
for z in [12.0,20.7,29.4]:
 cut(0,-19.6,z,92.0,1.0,5.4)
for z in [18.6,27.3]:add(0,-20.4,z,93.0,1.3,1.2)
# North corridor: genuine deep open strip, not a black texture or shallow recess.
for z in [11.15,19.85,28.55]:
 for x in [-45,-35,-25,-15,-5,5,15,25,35,45]:
  add(x,20.1,z-.25,1.8,1.8,8.4)
 # Thickened railing wall as connected relief; no brittle isolated miniature bars.
 add(0,20.1,z,94.0,1.4,2.1)
 add(0,20.1,z+1.9,94.0,1.7,1.0)
 for x in [-40,-30,-20,-10,0,10,20,30,40]:
  # Rail channels and inset wall windows have different counts from main columns.
  for dx in [-3,-1,1,3]:cut(x+dx,20.76,z+.25,.6,.30,1.5)
  cut(x,14.35,z+2.1,7.6,1.2,4.7)
  details.append(box(x,14.15,z+2.1,1.1,1.2,4.7))
# East and west ends: six principal glazed bays and closely spaced horizontal shades.
for side in [-1,1]:
 x=side*70.6
 for z in [11.3,20.0,28.7]:
  for y in np.linspace(-17.2,17.2,6):cut(x,y,z,1.35,5.35,6.6)
  for zz in [z+4.8,z+6.1]:add(side*70.7,0,zz,2.0,41.8,1.0)
 for y in np.linspace(-20.8,20.8,7):add(side*70.5,y,10.2,1.6,1.1,25.9)
# East original half-outdoor folding access stair, only ground to 2F.
# Top landing protrudes north; upper-storey stairs remain within the original body.
add(39.0,21.0,6.4,12.0,4.8,1.4)
stairs((42.6,31.0),(39.8,23.2),6.0,2.7,7.8,11)
add(32.4,21.0,6.4,4.8,4.8,1.4)
stairs((32.4,19.8),(32.4,11.2),4.8,7.8,10.8,9)
# Platform support is deliberately retained, with clear under-stair air space.
for x,y in [(31.0,22.0),(44.0,21.0)]:add(x,y,2.2,1.7,1.7,4.9)
# Main flat roof and continuous modest rim, not a fictitious interior courtyard.
roof_outline=[(-71.3,-22.8),(-46.5,-22.8),(-46.5,-22.3),(46.5,-22.3),(46.5,-22.8),(71.3,-22.8),(71.3,22.8),(46.5,22.8),(46.5,21.4),(-46.5,21.4),(-46.5,22.8),(-71.3,22.8)]
parts.append(footprint(roof_outline,36.0,1.7))
# Two low longitudinal service housings: front and end orthographic projections.
# Their three-axis envelope is approximate; internal equipment is not modelled.
for x in [-40.6,40.6]:
 add(x,0,37.5,10.0,33.3,4.8)
 # End-face door/window relief is omitted because opposing individual details differ.
solid=Manifold.batch_boolean(parts,op=__import__('manifold3d').OpType.Add)
for c in cuts:solid=solid-c
for d in details:solid=solid+d
assert solid.status()==__import__('manifold3d').Error.NoError,solid.status()
assert len(solid.decompose())==1,'Every component must be structurally connected'
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print({'dimensions_mm':mesh.extents.tolist(),'faces':len(mesh.faces),'watertight':mesh.is_watertight,'volume':mesh.volume})
