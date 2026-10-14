"""HFU library bounded prototype. Metre parameters, exported at 2 mm per metre.
X along building east; Y along building north, approximate bearing18deg from true east.
Ground/elevation not surveyed: south B1 datum=0, south terrace=15.2,
north terrace=19.2, uphill road=15.2. Rooftops traced from 2024/2017 orthophotos.
"""
from pathlib import Path
import numpy as np,trimesh,json
from manifold3d import Manifold
O=Path(__file__).resolve().parent
P=[];C=[];D=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):P.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):C.append(box(x,y,z,w,d,h))
def hip(x,y,z,w,d,h):
 # shallow hipped roof and robust short ridge; no wafer-thin cusp
 r=max(1.1,(w-d)/2)
 return Manifold.hull_points([(x+a,y+b,z+c) for a,b,c in [(-w/2,-d/2,0),(w/2,-d/2,0),(w/2,d/2,0),(-w/2,d/2,0),(-r,-.55,h),(r,-.55,h),(r,.55,h),(-r,.55,h)]])
def roof(x,y,z,w,d,h,rotate=False):
 p=hip(0,0,z,d,w,h).rotate((0,0,90)).translate((x,y,0)) if rotate else hip(x,y,z,w,d,h)
 P.append(p);add(x,y,z-.3,w,d,.65)
def railx(x,y,z,w):
 q=box(x,y,z,w,.8,1.25)
 for a in np.arange(x-w/2+1.5,x+w/2-1.1,1.15):q=q-box(a,y-.41,z+.35,.5,.46,.55)
 P.append(q)
def raily(x,y,z,d):
 q=box(x,y,z,.8,d,1.25)
 for b in np.arange(y-d/2+1.5,y+d/2-1.1,1.15):q=q-box(x+(-.41 if x<0 else .41),b,z+.35,.46,.5,.55)
 P.append(q)
def winS(x,y,z,w=2.3,h=2.5,vertical=True):
 cut(x,y,z,w,.6,h)
 if vertical:D.append(box(x,y+.30,z,.38,.5,h))
 D.append(box(x,y+.30,z+h*.58,w-.25,.5,.24))
def winE(x,y,z,w=2.2,h=2.5,vertical=True):
 cut(x,y,z,.6,w,h)
 if vertical:D.append(box(x-.30,y,z,.5,.38,h))
 D.append(box(x-.30,y,z+h*.58,.5,w-.25,.24))
# Separate compact base and bounded stepped slope. Terrain is not a survey.
add(0,0,-1.5,70,75,1.5)
# north uphill supporting mass; only the northernmost band reaches the road
P.append(Manifold.hull_points([(x,y,z) for x in [-33.5,33.5] for y,z in [(10,-.1),(37.5,-.1),(37.5,15.2),(32,15.2)]]))
# Main two sealed floor/roof plates. South width approx50m, north46m.
add(1,-11.4,-.1,48,30.8,15.3)
add(0,21,-.1,46,22,19.3)
# middle northern facade extends to high terrace's south edge
add(0,9,-.1,46,7,19.3)
# Southern and northern parapets as rooted rails; plate is not an open atrium
railx(1,-26.5,15.1,38);raily(-22,-5.8,15.1,20.4);raily(24.6,-11,15.1,30)
railx(0,5.6,19.1,46);raily(-22,25.5,19.1,17);raily(22,25.5,19.1,17)
# Four actual open pavilions; three openings per broad side, narrower south ends
for x,y,w,d,z in [(-20,11,13.5,9.5,19.2),(21,12,13.5,9.5,19.2),(-22,-22,8.5,11,15.2),(26,-22,8.5,11,15.2)]:
 add(x,y,0,w-1.8,d-1.8,z)
 for yy in [y-d/2+1.1,y+d/2-1.1]:add(x,yy,z-.1,w-1.2,.8,.9)
 # full-depth independently rooted frame pillars, never sealed window boxes
 xs=[x-w/2+1.1,x-w/6,x+w/6,x+w/2-1.1]
 ys=[y-d/2+1.1,y,y+d/2-1.1]
 for a,b in sorted({(a,b) for a in xs for b in [ys[0],ys[-1]]}|{(a,b) for a in [xs[0],xs[-1]] for b in ys}):add(a,b,z-.1,1.05,1.05,4.75)
 # beam and pierced high transom band, rooted to pillars
 for b in [ys[0],ys[-1]]:
  add(x,b,z+3.95,w-1.1,1.1,.6);add(x,b,z+3.05,w-1.2,.55,.4)
  for a in xs:add(a,b,z+3.0,.55,.6,1.5)
 for a in [xs[0],xs[-1]]:add(a,y,z+3.95,1.1,d-1.1,.6)
 roof(x,y,z+4.4,w+1.8,d+1.8,1.65,rotate=d>w)
 # tower lower facade windows: three long west/east openings (vertical central glass)
 for lev in [1.1,4.9,8.7,12.5]:
  if lev+2.5<z:
   for a in [x-2,x,x+2]:
    if y<0:winS(a,min(y-(d-1.8)/2,-26.8),lev,1.2,2.5,False)
 if x>0:
  cut(x+(w-1.8)/2,y,1.2,1,3.4,z-2.1)
  for zz in np.arange(2.4,z-1,1.8):D.append(box(x+(w-1.8)/2-.3,y,zz,.5,3.2,.3))
  D.append(box(x+(w-1.8)/2-.3,y,1.2,.5,.4,z-2.1))
  for b in [y-d/2+2.4,y+d/2-2.4]:
   for lev in [1.1,4.9,8.7,12.5]:
    if lev+2.5<z and not (y>0 and b>14):winE(x+(w-1.8)/2,b,lev,1.2,2.5,False)
# South facade: real recessed two-floor colonnade, 9 bays and rear upper window band
# Main rear wall retained, open verandas project in front of it.
for z in [3.8,7.6]:
 add(1,-28.4,z-.2,36,4.6,.7)
 for x in [-16,-11.75,-7.5,-3.25,1,5.25,9.5,13.75,18]:
  add(x,-29.9,z,1.05,1.05,3.6)
 railx(1,-30.5,z+.25,35.8)
 if z>7:
  rz=z+3.35
  # South upper eave: hip-and-gable ends, not a pure hip or hard vertical gable.
  P.append(Manifold.hull_points([(1+a,-28.4+b,rz+c) for a,b,c in [(-19,-3.15,0),(19,-3.15,0),(19,3.15,0),(-19,3.15,0),(-18,-2.15,.65),(18,-2.15,.65),(18,2.15,.65),(-18,2.15,.65)]]))
  P.append(Manifold.hull_points([(1+a,-28.4+b,rz+c) for a in [-18,18] for b,c in [(-2.15,.6),(2.15,.6),(.55,1.75),(-.55,1.75)]]))
  add(1,-28.4,rz-.3,38,6.3,.65)
 else:roof(1,-28.4,z+3.35,38,6.3,.85)
for x in [-15,-10.8,-6.6,-2.4,1.8,6,10.2,14.4,18.6]:
 for z in [.7,4.6,8.4,12.2]:winS(x,-26.8,z,2.6,2.5)
# East entrance spans the two unequal-height towers: high two-round-column porch
# low public approach is 1F at3.8m above the bounded basement datum
add(27,-4.7,3.55,10.5,20,.65)
for y in [-10.5,1.1]:P.append(Manifold.cylinder(10.7,.82,.82,40).translate((30,y,3.7)))
add(28,-4.7,14.3,8.5,19,.65)
add(30,-4.7,10.5,1.6,18,.8)
for y in [-12.4,-8.55,-4.7,-.85,3]:
 for x in [24.5,31.0]:add(x,y,14.8,1.05,1.05,3.5)
roof(28,-4.7,18.2,9.6,21,1.25,rotate=True)
roof(28,-4.7,14.4,10.5,21.5,.8,rotate=True)
raily(31.6,-4.7,14.8,18)
# shallow actual entry glazing behind the two free columns
for y in [-9,-4.7,-.4]:winE(25,y,4.2,3.2,6)
for y in [-13,-8.6,-4.2,.2]:
 for z in [8.5,12.2]:winE(25,y,z,2.6,2.5)
# approach steps connected to platform rather than isolated ornament
for i in range(7):add(33.8-i*.55,-4.7,0,1.,17,(i+1)*.54)
# High north wing: side two classroom rows and upper sheltered strip
for y in [17,21.5,26]:
 for z in [9.1,13.1]:winE(23,y,z,3.1,2.7)
for x in np.arange(-19,20,4.2):
 for z in [13.1,17]:
  if z<18:winS(x,5.5,z,2.8,2.6 if z<16 else 1.5)
# North low roof and recessed road entrance at5F, road datum15.2m.
add(0,32.5,15.1,43,5.2,.6)
for x in [-20,-15,-10,-5,0,5,10,15,20]:add(x,34,15.5,1.05,1.05,3.6)
roof(0,33,19,45,7,1.2)
# northern road bridge integrated into bounded high terrace
add(0,35.4,14.9,10,4.2,.65)
# conservative west facade levels (no invented ornate backside windows)
for z in [3.7,7.5,11.3,15.1]:add(-23.2,-2,z,1.,50,.55)
# rooted roof service box and small pyramidal skylight (not giant atrium)
add(-7,12,19.1,4,10,1.4)
P.append(Manifold.hull_points([(x,y,19.2) for x in [-2,2] for y in [9,13]]+[(x,y,20.5) for x in [-.6,.6] for y in [10.4,11.6]]))
solid=Manifold.batch_boolean(P, __import__('manifold3d').OpType.Add)
if C:solid=solid-Manifold.batch_boolean(C,__import__('manifold3d').OpType.Add)
if D:solid=solid+Manifold.batch_boolean(D,__import__('manifold3d').OpType.Add)
solid=solid.scale((2,2,2)).translate((0,0,3)).simplify(.00001)
m=solid.to_mesh64();mesh=trimesh.Trimesh(vertices=np.asarray(m.vert_properties[:,:3],dtype=np.float32),faces=np.array(m.tri_verts),process=False)
mesh.export(O/'model.stl');print(mesh.bounds,mesh.is_watertight,len(mesh.faces),'not repaired')
(O/'model-parameters.json').write_text(json.dumps({'status':'bounded source-limited approximation; see README','mm_per_estimated_m':2,'south_roof_m':15.2,'north_roof_m':19.2,'road_m':15.2,'north_max_m':25.25,'ground_datum':'bounded B1 south, not survey','four_pavilions':'open column frames'},indent=2))
