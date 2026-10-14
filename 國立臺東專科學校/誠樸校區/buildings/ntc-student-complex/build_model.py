"""Original C03 exterior approximation. Output unit mm. Not a measured survey.
Plan numbers 5848 x 2380 are documented; interpreting the unit as cm is inferred.
Four-storey completion-era body, 2017 as-built photo, NLSC 2023-marked roof.
Requires Python 3.12; requirements.txt. Only model.stl is exported.
"""
from pathlib import Path
import json, hashlib, math
import numpy as np
import trimesh
from manifold3d import Manifold
OUT=Path(__file__).resolve().parent
S=2.25  # model mm per inferred real metre (~1:444.44), uniform XYZ
BASE=3.0; FLOOR=4.1; X0=29.24; Y0=10.2
parts=[];cuts=[]
def cub(x1,x2,y1,y2,z1,z2):
    return Manifold.cube(((x2-x1)*S,(y2-y1)*S,(z2-z1)*S)).translate(((x1-X0)*S,(y1-Y0)*S,BASE+z1*S))
# Construction overlap 0.001 m (0.00225 mm) avoids coplanar boolean slivers.
def add(x1,x2,y1,y2,z1,z2):parts.append(cub(x1-.001,x2+.001,y1-.001,y2+.001,z1-.001,z2+.001))
def cut(x1,x2,y1,y2,z1,z2):cuts.append(cub(x1,x2,y1,y2,z1,z2))
# Plan-input Y grows south as on the paper drawing. Final solid is reflected
# into conventional east +X, north +Y, up +Z before export; never mirror evidence.
parts.append(Manifold.cube((150,70,BASE)).translate((-75,-35,0)))
# 1F–3F trace: north main bar, southwest protruding low wing, south central
# recess and distinct stair/circulation masses; no imaginary rear wing.
add(5.73,58.48,0,9.8,-.04,3*FLOOR)
# C031/C032 north glazing projects ~1.8m beyond grid line Y=0.
add(13.73,45.73,-1.8,.04,-.04,2*FLOOR)
add(2.13,5.73,0,9.8,-.04,4*FLOOR+.85)
add(0,13.73,9.8,23.8,-.04,3*FLOOR)
add(13.73,21.73,9.8,13.7,-.04,4*FLOOR)
add(13.73,16.3,13.7,18.0,-.04,3*FLOOR)
add(16.3,21.73,13.7,15.8,-.04,3*FLOOR)
add(29.73,45.73,9.8,17.7,-.04,2*FLOOR)
add(29.73,45.73,9.8,15.8,2*FLOOR-.04,3*FLOOR)
add(45.73,51.73,9.8,18.5,-.04,4*FLOOR)
add(51.73,58.48,9.8,15.8,-.04,4*FLOOR)
# 4F has narrower north/east volume, and southwest wing terminates at 3F.
add(5.73,51.73,0,9.8,3*FLOOR-.05,4*FLOOR)
add(51.73,55.0,0,7.22,3*FLOOR-.05,4*FLOOR)
add(51.73,58.48,7.18,9.8,3*FLOOR-.05,4*FLOOR)
add(29.73,37.73,9.8,15.8,3*FLOOR-.05,4*FLOOR)
add(37.73,45.73,9.8,17.7,3*FLOOR-.05,4*FLOOR)
# C034 room07/06 north of the low southwest roof (visible step-down).
add(5.73,13.73,7.2,9.8,3*FLOOR-.05,4*FLOOR)
# East staircase + elevator roof volumes, mapped to floor-plan core positions.
add(54.9,58.48,9.8,15.8,4*FLOOR-.05,4*FLOOR+1.55)
add(51.9,54.9,10.0,13.2,4*FLOOR-.05,4*FLOOR+1.1)
# Solid low roof coping (no invented fifth storey).
for x1,x2,y1,y2,z in [(0,13.73,9.8,23.8,3*FLOOR),(55,58.48,0,7.2,3*FLOOR)]:
    add(x1-.15,x2+.15,y1-.15,y2+.15,z-.1,z+.42)
# Thin photographed fascia made printable: .5m (=1.125mm) thick, .45m relief.
for z in [FLOOR,2*FLOOR,3*FLOOR]:
    for x1,x2,y in [(0,13.73,23.8),(45.73,51.73,18.5),(51.73,58.48,15.8)]:
        add(x1-.08,x2+.08,y-.16,y+.45,z-.42,z+.08)
# North-facing balcony decks at 3F and 4F; 4F apartment balcony grouping from
# C034. Raised edges/partition roots exaggerated to >=1.125mm for the miniature.
breaks=[5.73,13.73,17.73,21.73,25.73,29.73,33.73,37.73,41.73,45.73,51.73]
for z in [2*FLOOR,3*FLOOR]:
    add(5.73,51.73,-1.75,.15,z-.48,z+.02)
    add(5.73,51.73,-1.75,-1.25,z-.1,z+1.05)
    for x in breaks:add(x-.25,x+.25,-1.75,.2,z-.1,z+2.7)
    for xa,xb in zip(breaks[:-1],breaks[1:]):
        cut(xa+.6,xb-.6,-.25,.42,z+1.25,z+3.25)
# Ground/second-floor north folding-door bands, using 800cm major grid breaks.
for z in [0,FLOOR]:
    for xa,xb in zip([13.73,21.73,29.73,37.73],[21.73,29.73,37.73,45.73]):
        cut(xa+.6,xb-.6,-2.0,-1.42,z+.65,z+3.2)
# Southwest 3-storey wing: plan-confirmed perimeter openings, no tiny invented mullions.
for z in [0,FLOOR,2*FLOOR]:
    for xa,xb in [(1.0,4.8),(6.3,9.2),(10.0,12.65)]:cut(xa,xb,23.45,24,z+.85,z+3.0)
    for ya,yb in [(10.8,13.3),(14.2,17.1),(18.0,20.5),(21.2,22.8)]:cut(-.2,.36,ya,yb,z+.85,z+3.0)
# The south facade is not one repeated rectangle: 1F/2F rooms project
# to Y17.7; 3F rooms retreat to Y15.8 with a balcony; 4F's eastern half
# projects again while the western half remains recessed (C032–C034).
for z in [0,FLOOR]:
    for xa,xb in [(30.5,36.9),(38.5,44.95)]:cut(xa,xb,17.35,17.9,z+.85,z+3.15)
for xa,xb in [(30.5,36.9),(38.5,44.95)]:cut(xa,xb,15.42,16.0,2*FLOOR+.85,3*FLOOR-.8)
cut(30.5,36.9,15.42,16.0,3*FLOOR+.85,4*FLOOR-.8)
for xa,xb in [(38.5,41.0),(42.0,44.95)]:cut(xa,xb,17.35,17.9,3*FLOOR+.85,4*FLOOR-.8)
# Actual open south balconies: 2F extends to ~19.4m, 3F to ~17.7m,
# 4F only the western 8m bay. Rails are robust wall-backed miniature relief.
for x1,x2,y1,y2,z in [(29.73,45.73,17.55,19.4,FLOOR),(29.73,45.73,15.65,17.7,2*FLOOR),(29.73,37.73,15.65,17.7,3*FLOOR)]:
    add(x1-.08,x2+.08,y1,y2,z-.48,z+.02)
    add(x1-.08,x2+.08,y2-.5,y2,z-.08,z+1.05)
    for x in [x1,x2]:add(x-.25,x+.25,y1,y2,z-.08,z+1.05)
# East service-wing windows are simplified and explicitly not a surveyed rear facade.
for z in [0,FLOOR,2*FLOOR]:
    for ya,yb in [(1.0,4.0),(5.2,8.4)]:cut(58.12,58.7,ya,yb,z+.85,z+3.0)
# Main entrance recess is physically clear from the south to the north wall:
# preserve central notch x21.73–29.73 instead of filling it as a rectangle.
# The source 3F drawing labels a balcony here; a balcony deck at 3F is modeled
# with a ground-level underpass; open above toward the sky, no fictitious atrium.
add(21.63,29.83,9.65,17.7,2*FLOOR-.48,2*FLOOR+.02)
add(21.63,29.83,17.2,17.7,2*FLOOR-.08,2*FLOOR+1.05)
# Robust side upstands connect deck and rear volume (not unsupported isolated rods).
for x in [21.73,29.73]:add(x-.25,x+.25,9.65,17.7,2*FLOOR-.08,2*FLOOR+1.05)
# C034 directly labels an L-shaped 4F balcony south of the central stair;
# this is separate from the larger 3F platform to its east.
z=3*FLOOR
add(13.65,21.8,13.55,16.2,z-.48,z+.02)
add(13.65,16.3,16.1,18.0,z-.48,z+.02)
add(16.05,21.8,15.7,16.2,z-.08,z+1.05)
add(21.3,21.8,13.55,16.2,z-.08,z+1.05)
add(15.8,16.3,15.7,18.0,z-.08,z+1.05)
add(13.65,16.3,17.5,18.0,z-.08,z+1.05)
add(13.65,14.15,13.55,18.0,z-.08,z+1.05)
# Main roof slabs, exact step grouping follows C034.
for x1,x2,y1,y2 in [(5.73,51.73,-1.9,9.95),(51.73,55.15,-.15,7.2),(51.73,58.63,7.05,9.95),(29.58,37.88,9.7,15.95),(37.58,45.88,9.7,17.85),(45.58,51.88,9.7,18.65),(51.58,58.63,9.7,15.95),(13.58,21.88,9.7,13.85)]:
    add(x1,x2,y1,y2,4*FLOOR-.08,4*FLOOR+.48)
# Stair caps connected to cores. Detailed rooftop mechanical plant omitted.
add(1.93,5.93,-.2,10.0,4*FLOOR+.75,4*FLOOR+1.25)
add(54.7,58.68,9.6,16.0,4*FLOOR+1.45,4*FLOOR+1.95)
# Solar collector field visible in NLSC 2023-marked imagery; simplified attached
# plinths, not a claim about 2016 roof equipment or exact individual module count.
for x1,x2 in [(10,24),(25,39),(40,47.8)]:
    add(x1,x2,0.9,3.2,4*FLOOR+.40,4*FLOOR+1.03)
    add(x1,x2,3.65,5.95,4*FLOOR+.40,4*FLOOR+1.03)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
assert len(solid.decompose())==1, 'disconnected result'
solid=solid.scale((1,-1,1))
m=solid.simplify(.000001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(json.dumps({'dimensions_mm':mesh.extents.tolist(),'faces':len(mesh.faces),'watertight':bool(mesh.is_watertight),'sha256':hashlib.sha256((OUT/'model.stl').read_bytes()).hexdigest()}))
