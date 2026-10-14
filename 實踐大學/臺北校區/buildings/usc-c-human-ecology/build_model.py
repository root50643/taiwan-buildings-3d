"""Original plan/section-based USC C building, 2016–2017 renovation approximation.
Units mm. Source plan 8m bar =177px on private 4200px source crop.
North +Y, east +X. Paper plan Y increases south and is reflected at export.
"""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
S=2.8; BASE=2.4;X0=25.25;Y0=4.1
parts=[];cuts=[]
def cub(a,b,c,d,e,f):return Manifold.cube(((b-a)*S,(d-c)*S,(f-e)*S)).translate(((a-X0)*S,(c-Y0)*S,BASE+e*S))
def add(a,b,c,d,e,f):parts.append(cub(a-.001,b+.001,c-.001,d+.001,e-.001,f+.001))
def cut(a,b,c,d,e,f):cuts.append(cub(a,b,c,d,e,f))
parts.append(Manifold.cube((150,53,BASE)).translate((-75,-26.5,0)))
# 50.53m long main teaching bar. Plan room depth 6.45m; south gallery 2.2m.
add(2.15,9.15,0,6.45,-.03,8.05)
add(12.35,40.55,0,6.45,-.03,8.05)
# East stair / toilet core with the plan's recessed gallery face.
add(45.9,50.5,0,6.45,-.03,8.15)
add(40.4,43.15,0,3.3,-.03,8.15)
# West side wall, open outdoor cafe / upper circulation bay retained.
add(0,.5,0,12.35,-.03,8.3)
# Slabs: full long south gallery plus deeper western end / stair apron.
for z in [0,2.7,5.4,8.1]:
 add(0,50.5,0,8.85,max(-.03,z-.43),z+.02)
 add(0,12.5,8.7,12.35,max(-.03,z-.43),z+.02)
# West side gallery apertures, aligned to floors; no invented solid west wall.
for z in [0,2.7,5.4]:
 for ya,yb in [(6.95,8.35),(9.1,11.5)]:cut(-.2,.7,ya,yb,z+.15,z+2.2)
# South main colonnade, 10 source main spans between west and east cores.
for x in [12.35,15.15,17.95,20.75,23.55,26.35,29.15,31.95,34.75,37.55,40.55,43.3,46.7,50.2]:
 add(x-.24,x+.24,8.25,8.82,-.03,8.3)
# West end corner and side columns, robust 1.34mm roots.
for x in [.3,2.2,5.6,9.0,12.2]:add(x-.24,x+.24,11.8,12.35,-.03,10.9 if x in [.3,12.2] else 8.3)
for y in [6.5,8.7]:add(.01,.5,y-.24,y+.24,-.03,8.3)
# Classroom doors / long windows are recessed from the real open gallery.
for z in [0,2.7,5.4]:
 for xa,xb in [(2.7,8.55),(13,16.5),(17.1,20.6),(21.2,24.7),(25.3,28.8),(29.4,32.9),(33.5,36.8),(37.4,39.9)]:cut(xa,xb,6.1,6.6,z+.5,z+2.2)
 # Rear openings follow plan bay groups; window detailing unknown and simplified.
 for xa,xb in [(2.8,5.1),(5.7,8.5),(13,17),(17.6,22),(22.6,25.5),(26.2,30.4),(31,34.1),(34.8,39.9),(46.7,49.7)]:cut(xa,xb,-.2,.38,z+.8,z+2.15)
 for ya,yb in [(1,2.6),(3.4,5.7)]:cut(50.15,50.7,ya,yb,z+.8,z+2.15)
# Western high perforated screen: a two-storey-plus parapet hanging above 1F.
# Diamond motifs coarsened to 1.0mm-plus ligaments, not exact 390mm castings.
add(0,12.5,11.88,12.35,2.68,10.9)
for row in range(8):
 z=3.32+row*.94
 for col in range(13):
  x=.85+col*.9
  # Diamond in XZ; depth cuts through screen, broad corner ligaments retained.
  hole=Manifold.cube((.38*S,1.0*S,.38*S),center=True).rotate((0,45,0)).translate(((x-X0)*S,(12.1-Y0)*S,BASE+z*S))
  cuts.append(hole)
# Top and two side screen frames; upper roof service strip behind screen.
add(0,12.5,11.65,12.48,10.42,10.9)
add(0,.52,11.65,12.48,2.65,10.9);add(11.98,12.5,11.65,12.48,2.65,10.9)
add(.25,12.25,10.4,11.95,8.06,8.55)
# Retained timber-truss pitched roof expressed as outer roof envelope.
# No visible truss fabricated inside a solid printing miniature.
roof=CrossSection([[(0,8.02),(6.55,8.02),(6.55,8.48),(3.5,9.8),(3.05,9.8),(0,8.48)]]).extrude((40.6-12.3)).rotate((90,0,90)).scale((S,S,S)).translate(((12.3-X0)*S,(0-Y0)*S,BASE))
parts.append(roof)
# West roof terrace and east flat stair roof, lower than high west screen.
for a,b in [(0,12.4),(40.5,50.5)]:
 add(a,b,-.1,.4,8.05,8.4)
add(0,.5,0,11.9,8.05,8.6)
add(40.55,43.2,.2,3.45,8.1,9.0)
# North circulation projection and bridge towards D: only 4m of C connection.
# Ground piers are rooted; 2F/3F deck and rails remain open beneath.
for x in [9.05,11.85]:add(x-.30,x+.30,-4,.65,-.03,8.35)
for z in [2.7,5.4,8.1]:
 add(9.1,12.1,-4,.3,z-.43,z+.03)
 if z<8:
  add(9.1,9.58,-4,.25,z-.05,z+.9);add(11.62,12.1,-4,.25,z-.05,z+.9)
# North upper stair/landing projection directly beside the bridge.
add(3.0,9.2,-1.1,.25,5.0,5.43)
add(3.0,9.2,-1.1,-.62,5.35,6.25)
for x in [3,8.75]:add(x,x+.48,-1.1,.35,5.35,6.25)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
assert len(solid.decompose())==1
solid=solid.scale((1,-1,1));m=solid.simplify(.000001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(json.dumps({'dimensions_mm':mesh.extents.tolist(),'faces':len(mesh.faces),'watertight':bool(mesh.is_watertight),'sha256':hashlib.sha256((OUT/'model.stl').read_bytes()).hexdigest()}))
