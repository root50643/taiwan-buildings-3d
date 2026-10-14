"""Original Kainan University library exterior miniature, units mm.
Nominal real-like dimensions are bounded estimates, not construction drawings.
2005 completed body: official 7 above-ground floors, not just four library floors.
"""
from pathlib import Path
import numpy as np,trimesh,math,json,hashlib
from manifold3d import Manifold,CrossSection
R=Path(__file__).resolve().parent;S=1.8;BASE=3.;parts=[];cuts=[];details=[]
def cub(x1,x2,y1,y2,z1,z2):return Manifold.cube(((x2-x1)*S,(y2-y1)*S,(z2-z1)*S)).translate((x1*S,y1*S,BASE+z1*S))
def add(x1,x2,y1,y2,z1,z2):
 # Original CSG construction overlap0.003m avoids coincident Boolean planes.
 e=.003;parts.append(cub(x1-e,x2+e,y1-e,y2+e,z1-e,z2+e))
def cut(*v):cuts.append(cub(*v))
def arch(cx,r,zbottom,zspring,y1,y2):
 # Counter-clockwise XZ silhouette extruded toward -Y, then placed at y2.
 p=[(cx-r,zbottom),(cx+r,zbottom),(cx+r,zspring)]
 for i in range(1,65):t=math.pi*i/64;p.append((cx+r*math.cos(t),zspring+r*math.sin(t)))
 return CrossSection([np.array(p)*S]).extrude((y2-y1)*S).rotate((90,0,0)).translate((0,y2*S,BASE))
def xz_prism(points,y1,y2):return CrossSection([np.array(points)*S]).extrude((y2-y1)*S).rotate((90,0,0)).translate((0,y2*S,BASE))
parts.append(Manifold.cube((150,122,BASE)).translate((-75,-69,0)))
# Main seven-storey central mass and lower side wings.
add(-37,37,-21.5,21.5,-.02,22.3)
# Layered image envelope: the low roof is about32m deep, while rear open
# frames extend to about40–42m. Ground43m remains an OSM bounded candidate.
add(-37,-16.5,-21.5,10.5,22.0,27.2)
add(16.5,37,-21.5,10.5,22.0,27.2)
add(-16.5,16.5,-21.5,21.5,22.0,24.0)
add(-16.5,16.5,-16.5,16.5,23.7,32.2)
# Side towers stand proud of the main wall; their deep arched openings are not
# pasted onto a single common facade plane.
for cx in [-20,20]:
 add(cx-7.5,cx+7.5,-26.2,-19.5,5.8,26.2)
 add(cx-5.9,cx+5.9,-26.8,-25.6,7.3,20.3)
 cuts.append(arch(cx,4.9,7.9,14.45,-27.0,-24.0))
 # Rooted white divisions inside the arched recess, backed by the solid body.
 for x in [cx-2.45,cx+2.45]:details.append(cub(x-.42,x+.42,-26.85,-23.7,7.8,19.0))
 for z in [11.7,15.7]:details.append(cub(cx-4.95,cx+4.95,-26.85,-23.7,z-.38,z+.38))
 # Three paired narrow openings above each large arch.
 for x in [cx-4.0,cx,cx+4.0]:
  for dx in [-.68,.68]:cut(x+dx-.42,x+dx+.42,-26.4,-25.65,22.0,24.6)
 add(cx-7.65,cx+7.65,-26.4,-19.3,25.8,26.55)
# Low outer-front pavilions, different from six-storey wings behind.
for sign in [-1,1]:
 x1,x2=sorted([sign*27.4,sign*37]);add(x1,x2,-25.4,-19.8,-.02,17.4)
 for x in np.linspace(x1+1.4,x2-1.4,3):
  cut(x-.48,x+.48,-25.6,-24.9,12.9,15.3)
  cut(x-.75,x+.75,-25.6,-24.9,8.8,10.8)
 add(x1-.15,x2+.15,-25.55,-19.7,17.0,17.7)
# Central entry arch projects to total plan depth54m. Backing wall/door plane
# remains; the tall arch recess is genuinely deep but not an invented tunnel.
add(-8.5,8.5,-32.5,-19.5,-.02,14.1)
cuts.append(arch(0,5.5,.55,5.9,-32.8,-22.7))
# Door glazing divisions are recessed only into the deep rear wall, leaving
# the full entry-arch depth open. Four door fields with upper transom band.
for xa,xb in [(-4.8,-2.6),(-2.2,-.25),(.25,2.2),(2.6,4.8)]:
 for za,zb in [(.9,4.1),(4.6,6.7)]:cut(xa,xb,-22.92,-22.3,za,zb)
for xa,xb in [(-3.6,-.25),(.25,3.6)]:cut(xa,xb,-22.92,-22.3,7.2,9.0)
# Stepped entry coping, no tiny free-standing classical moldings.
for xa,ya,z1,z2 in [(8.8,-32.7,13.8,14.6),(9.35,-33.0,14.6,15.35),(8.9,-32.75,15.35,16.15)]:add(-xa,xa,ya,-20,z1,z2)
# Low front arcade has real open bays under a continuous deck.
for xa,xb in [(-37,-8.3),(8.3,37)]:
 add(xa,xb,-28.2,-20.7,5.85,6.65)
 for x in np.linspace(xa+.75,xb-.75,7):add(x-.52,x+.52,-27.9,-26.6,-.02,6.1)
# Front wall behind tower/entry recesses: upper centre and six-row side wings.
for x in [-10.5,-6.3,-2.1,2.1,6.3,10.5]:
 cut(x-.85,x+.85,-16.7,-15.9,24.4,26.7)
 for dx in [-.6,.6]:cut(x+dx-.4,x+dx+.4,-16.7,-15.9,28.4,30.5)
# Main central glazed band has three broad groups and strong major piers.
for xa,xb in [(-12.1,-5.4),(-4.4,4.4),(5.4,12.1)]:
 for za,zb in [(17.7,19.4),(20.0,22.8)]:cut(xa,xb,-21.7,-20.8,za,zb)
for z in [8.2,12.8]:
 for x in [-12.0,-9.1,9.1,12.0]:cut(x-.55,x+.55,-21.7,-20.8,z,z+2.4)
# Wing front windows not hidden by forward towers, two outer upper bays.
for sign in [-1,1]:
 for x in [sign*31.0,sign*34.2]:
  for za,zb in [(18.7,21.2),(23.6,26.0)]:cut(x-.65,x+.65,-21.7,-20.8,za,zb)
# Southwest side confirmed in official photo: six distinct horizontal levels.
# Northeast side uses same structural rhythm only; rear detail remains restrained.
for x1,x2 in [(-37.2,-36.45),(36.45,37.2)]:
 for y in [-17,-11,-5,1,7,13,18]:
  for za,zb in [(1.3,3.6),(5.8,8.1),(10.3,12.6),(14.8,17.1),(19.3,21.6),(23.8,26.0)]:
   if za<23 or y<=8.8:cut(x1,x2,y-1.25,y+1.25,za,zb)
# Horizontal bands wrap the main walls. Robust shallow relief, not fragile rails.
for z in [4.2,8.7,13.2,17.7,22.2,26.7]:
 rear=10.6 if z>22.3 else 21.6
 add(-37.2,-36.8,-21.6,rear,z-.18,z+.24);add(36.8,37.2,-21.6,rear,z-.18,z+.24)
 if z<23:add(-37.1,37.1,21.2,21.7,z-.18,z+.24)
# Rear is a bounded simple structural envelope, not a mirrored decorative front.
# Specific rear openings are deferred until a reliable pond-side photograph.
# Flat lower roofs and low rooftop plant visible in aerial image.
for xa,xb in [(-37,-16.5),(16.5,37)]:add(xa-.3,xb+.3,-21.8,10.8,27.0,27.7);add(xa-.3,xb+.3,10.3,21.8,22.1,22.7)
for xa,xb in [(-34,-28),(28,34)]:add(xa,xb,3,9,27.5,29.2)
# Roof overhang plate roots the front/rear framing beyond the wall line.
add(-17,17,-17.8,17.8,31.7,32.3)
# Central dark skylight is closed, not a fictitious open courtyard.
add(-7.4,7.4,-6.0,8.0,32.15,32.9)
# Three groups of open projecting concrete eaves. Columns/rafters are thickened
# and rooted; no tiled hip roof or solid triangular wall substitutes.
def roof_frame(cx,half,yfront,yrear,body_top,beam_bottom,top):
 # Header and rear rail, open support band underneath.
 for y in [yfront,yrear]:
  add(cx-half*.63,cx+half*.63,y-.65,y+.65,beam_bottom,top-.45)
  support_base=22.2 if half<10 and y>10.5 else body_top-.25
  for x in np.linspace(cx-half*.55,cx+half*.55,7):add(x-.5,x+.5,y-.55,y+.55,support_base,beam_bottom+.25)
  # Upturned cantilever tips with finite flat landings (>0.8mm at scale).
  poly=[(cx+half*.60,beam_bottom),(cx+half,top-.9),(cx+half,top),(cx+half-1.35,top),(cx+half*.60,beam_bottom+.65)]
  parts.append(xz_prism(poly,y-1.15,y+1.15))
  parts.append(xz_prism([(-x+2*cx,z) for x,z in poly][::-1],y-1.15,y+1.15))
 # Side longitudinal beams form two perforated rows, connected by roof-rooted
 # transverse rafters. Rectangular clear slots remain open to the sky.
 for sign in [-1,1]:
  outer=cx+sign*(half-.55);inner=cx+sign*(half*.77)
  add(outer-.55,outer+.55,yfront-1.15,yrear+1.15,top-1.05,top)
  for y in np.linspace(yfront+1.0,yrear-1.0,10):
   x1,x2=sorted([inner,outer]);add(x1-.2,x2+.2,y-.5,y+.5,top-1.25,top-.30)
   support_base=22.2 if half<10 and y>10.5 else body_top-.25
   add(inner-.52,inner+.52,y-.5,y+.5,support_base,top-.6)
roof_frame(0,19.8,-16.6,16.6,32.1,34.3,36.3)
for cx in [-30.8,30.8]:roof_frame(cx,6.7,-20.8,18.6,27.6,28.6,30.0)
# Front approach steps with robust vertical risers, landscape omitted.
for i in range(4):add(-7.4,7.4,-35.1+i*.55,-32.3,0,.18*(i+1))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00005).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=False);mesh.export(R/'model.stl')
print(json.dumps({'dimensions_mm':mesh.extents.tolist(),'triangles':len(mesh.faces),'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()}))
