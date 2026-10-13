"""NCNU Paiwan slate house: observed completed-building exterior approximation.
2017 front/side photos and a university-provided photo published in 2025.
Independent hand-built solid, mm. Not a scanned mesh or exact carving replica.
Rear, internal room and off-building ancestral stele are outside detailed scope.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];reliefs=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def hull(p):return Manifold.hull_points(np.asarray(p,float))
def yzpoly(points,x,w):return CrossSection([points]).extrude(w).rotate((90,0,90)).translate((x,0,0))
def disc(x,y,z,rx,rz,d=.75):
 return Manifold.cylinder(d,1,1,24).rotate((90,0,0)).scale((rx,1,rz)).translate((x,y,z))
add(0,0,0,150,101,2.5)
# Low rectangular classroom with gable across the shorter dimension.
add(0,2,2.4,128,68,38.6)
parts.append(yzpoly([(-32,40.8),(36,40.8),(2,50.0)],-64,128))
# Layered slate gable roof. Top two planes are measured visually, not surveyed.
parts.append(yzpoly([(-36,40.4),(2,51.0),(40,40.4),(40,42.4),(2,53.0),(-36,42.4)],-68,136))
# Roof slate seams: shallow regularized grooves joined to the full thick roof.
# Do not cut cross-slope grooves: they form sub-nozzle horizontal lips at some Z.
# Longer slate-panel joints retain visible roof articulation with a continuous roof.
for x in [-55,-36,-15,5,25,46,60]:
 # Shallow joints on the visible front slope only, not hypothetical rear details.
 for ya,yb in [(-35,-24),(-23,-11),(-10,1)]:
  z1=53-abs(ya-2)*(10.6/38);z2=53-abs(yb-2)*(10.6/38)
  cuts.append(hull([(x+dx,y,z+dz) for dx in [-.27,.27] for y,z in [(ya,z1),(yb,z2)] for dz in [-.28,.8]]))
# Six irregular pale ridge weights are visible in the university photo.
# Low faceted stones, not decorative round discs or chimney pots.
for x in [-51,-31,-11,9,29,49]:
 pts=[]
 for j in range(8):
  a=2*math.pi*j/8;r=[1,.96,1.08,.93,1.04,.95,1,.93][j]
  pts.append((x+2.5*r*math.cos(a),2+2.0*r*math.sin(a),52.65))
  pts.append((x+1.9*r*math.cos(a),2+1.5*r*math.sin(a),54.3+(.07 if j in [1,4] else 0)))
 parts.append(hull(pts))
# Front door and two shuttered square windows, blind pockets keep robust solid core.
cuts.append(box(-41,-33.2,3.8,20,10,29.8))
for x in [-4,35]:cuts.append(box(x,-32.8,15.0,23,7,20.4))
# Thick doorway jambs retain visibly stacked slate versus flat front slabs.
for x in [-54,-28]:add(x,-33.0,2.4,6.0,4,32.6)
# Broad carved lintel spanning the front. Relief motifs are intentionally coarse.
add(0,-33.3,35.2,128,3.3,6.8)
for x in [-47,-34,-21,5,37,50]:
 # Head silhouette tapers into a chin; no circular-coin substitutions.
 reliefs.append(hull([(x+dx,y,38.7+dz) for y in [-35.0,-35.85] for dx,dz in [(-2.4,.5),(-1.8,2.5),(1.8,2.5),(2.4,.5),(1.4,-2.4),(-1.4,-2.4)]]))
for x in [-59,-8]:
 # Paired coiled-snake silhouettes from the photographed band, gross outline only.
 for dx in [-1.65,1.65]:
  outer=disc(x+dx,-35.0,37.8,1.35,1.35,.75)
  inner=disc(x+dx,-34.8,37.8,.65,.65,1.2)
  reliefs.append(outer-inner)
  reliefs.append(box(x+dx,-35.25,38.1,.8,.8,2.7))
  reliefs.append(hull([(x+dx+xx,y,z) for y in [-35.0,-35.8] for xx,z in [(-.85,40.4),(.85,40.4),(0,41.5)]]))
# One broad pot silhouette, rather than a fabricated raised circular plate.
reliefs.append(hull([(23+dx,y,38.7+dz) for y in [-35.0,-35.85] for dx,dz in [(-1.8,2.5),(1.8,2.5),(3.0,.6),(2.4,-1.0),(0,-2.5),(-2.4,-1.0),(-3.0,.6)]]))
# Triangular saw-tooth lower lintel edge, simplified from source carved strip.
for x in np.arange(-61,63,5):
 reliefs.append(hull([(x+dx,y,z) for y in [-35.2,-34.8] for dx,z in [(-1.8,35.8),(1.8,35.8),(0,37.3)]]))
# Two awning shutters are real solid sloping plates attached to their lintels.
for x in [-4,35]:
 reliefs.append(hull([(x+dx,y,z+dz) for dx in [-12.0,12.0] for y,z in [(-32.4,35.1),(-39.3,32.3)] for dz in [0,1.35]]))
 # Fixed bottom sills and broad wood frame, no floating simulated pane.
 reliefs.append(box(x,-33.8,14.3,25,4.0,1.3))
 for dx in [-12,12]:reliefs.append(box(x+dx,-32.4,14.5,1.45,2.8,20.8))
# Raised doorstep and paved front apron.
add(0,-39.8,2.4,130,17.5,1.7)
add(-41,-43.8,2.4,24,10,2.2)
# Stacked slate side wall, observed at X=-64; no invented pattern on unseen rear.
for z in np.arange(5.0,40.0,1.65):
 cuts.append(box(-64.0,2,float(z),.8,67,.42))
 if z<35:
  for x in [-54,-28]:cuts.append(box(x,-35.0,float(z),6.2,.7,.42))
# Large front slate panel joints, not a conventional window-grid building.
for x in [-62,-15,15,57]:cuts.append(box(x,-32.0,4.0,.55,.8,30.6))
# Right side and rear retain unadorned simplified massing; no mirrored door.
solid=parts[0]
for n,p in enumerate(parts[1:]):
 assert p.status().name=='NoError',(n,p.status());solid=solid+p
for p in cuts:solid=solid-p
for p in reliefs:solid=solid+p
assert solid.status().name=='NoError';assert len(solid.decompose())==1,[(q.volume(),q.bounding_box()) for q in solid.decompose()]
m=solid.simplify(.00001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight)
