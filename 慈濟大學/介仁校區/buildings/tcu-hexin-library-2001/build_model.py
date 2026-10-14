"""TCU Jieren Hexin2A bounded draft. Image-derived heights, not survey. X east, Y south in building axes."""
from pathlib import Path
import json,numpy as np,trimesh
from manifold3d import Manifold,OpType,CrossSection
O=Path(__file__).resolve().parent;P=[];C=[];D=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):P.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):C.append(box(x,y,z,w,d,h))
def poly(ps,z,h):return CrossSection([ps]).extrude(h).translate((0,0,z))
def edgepanes(a,b,z,h,step=2.0,depth=.24,gap=.35):
 a=np.array(a,float);b=np.array(b,float);v=b-a;L=np.linalg.norm(v);u=v/L;angle=np.degrees(np.arctan2(v[1],v[0]));n=max(1,round(L/step))
 for i in range(n):
  mid=a+u*L*(i+.5)/n;w=L/n-gap
  # Leave an explicit inward-backed corner pier at each facade segment end.
  if i==0:mid+=u*.3;w-=.6
  if i==n-1:mid-=u*.3;w-=.6
  C.append(box(0,0,0,w,depth,h).rotate((0,0,angle)).translate((mid[0],mid[1],z)))
# Continuous base, 96 estimated metres long maps to150mm.
add(3,18,-1.28,88,96,1.28)
# Upper main hall, gently bowed northern glass edge, not a high barrel roof.
north=[(5,-23),(11,-24.3),(18,-25),(26,-25),(34,-24.4),(42,-23)]
foot=north+[(42,-3),(5,-3)]
P.append(poly(foot,4,12))
# Solid recessed rear wall under the glazed cantilever; true north/east undercroft.
add(20.5,-10.2,0,31,14.4,4.2)
for x,y in [(7,-22.1),(13,-23.1),(20,-23.6),(27,-23.5),(34,-22.8),(40.3,-21.7),(40.3,-13.5),(40.3,-5.4)]:
 D.append(box(x,y,0,1.35,1.35,4.2))
# Roof rim with substantial backing: no detached thin parapet skin.
# Source north glazing: opaque-tall bottom strip, two short opening bands,
# broad middle panes and closer paired upper transoms; not uniform floors.
north_bands=[(4.4,1.8),(6.45,.70),(7.40,.70),(8.35,1.0),(9.60,1.0),(10.85,1.0),(12.10,1.0),(13.35,.75),(14.35,1.0)]
for a,b in zip(north[:-1],north[1:]):
 for z,h in north_bands:edgepanes(a,b,z,h,2.05,.28,.25)
for z,h in north_bands:edgepanes((42,-23),(42,-3),z,h,2.1,.28,.25)
for x in [9,15,21,27,33]:cut(x,-17.4,1.7,2.2,.28,.65)
# Southern solid strip and stepped western connector, both around three normal levels.
add(19,1,0,46,8,13)
add(-11,-7,0,14,24,13)
add(.2,-10.5,0,8.6,17,13)
# Main south: sparse narrow ribbon below a deeper top glazing band, not north grid.
cut(19,5,10.3,44.5,.32,2.1)
for x in np.arange(-2,41,2.75):D.append(box(x,4.92,10.3,.2,.44,2.1))
D.append(box(19,4.92,11.8,44.5,.44,.16))
cut(19,5,8.1,24,1.0,.75)
for x in np.arange(8,31,3.0):D.append(box(x,4.7,8.1,.2,.65,.75))
for x in [0,28]:cut(x,5,0.7,3.1,.5,2.7)
# Link to the longer administrative/library wing, glass on east face.
add(-8,9,0,7.2,10,12.5)
for y in [5.7,7.9,10.1,12.3]:
 for z in [1.1,3.3,5.5,7.7,9.9]:cut(-4.4,y,z,.28,1.65,1.65)
# Low roof is deliberately solid below F/G; no invented through-courtyard.
add(-16.5,37.5,0,38,47,11.8)
# E long east facade above the low roof. Three source-visible rows.
add(-1,37.5,0,8,47,13)
# Recessed two-storey entrance in east E facade, backed at west.
cut(1.0,34,0.4,7.0,11,8.5)
add(-3.6,34,0,1.2,11,9)
# Balcony / rear entry glass remains inside the portal; no front full-height plug.
D.append(box(-2.0,34,4.2,2.2,11,1.1))
for y in [29.7,32.5,35.3,38.1]:
 for z in [0.8,2.6,6.0]:cut(-2.5,y,z,.3,2.2,1.4)
# Lower two storeys: paired tall windows, connected narrow mullions and footlights.
for y in [16.8,20.9,25.0,43.0,47.1,51.2,55.3,59.0]:
 for z,h in [(.75,3.35),(5.0,3.35)]:
  cut(3,y,z,.32,3.0,h)
  D.append(box(2.92,y,z,.44,.18,h))
  D.append(box(2.92,y,z+.6,.44,3.0,.16))
# Continuous upper glazed ribbon, two fine top transoms and slender backed uprights.
cut(3,37.5,10.0,.32,45,2.5)
for y in np.arange(15.4,60.0,2.05):D.append(box(2.92,y,10.0,.44,.19,2.5))
for z in [11.65,12.10]:D.append(box(2.92,37.5,z,.44,45,.16))
# Raised flat pavilion roofs, plan curves from official map/2018 ortho; height1–4m bounded.
# Inward-facing west-edge curve is kept shallow; no arbitrary vault.
F=[(-35.5,15),(-8,15),(-8,30),(-15,31),(-26,31),(-35.5,29.5)]
G=[(-34.5,45),(-7,44),(-7,61),(-15,62),(-25,62),(-34.5,60.5)]
for ps in [F,G]:
 P.append(poly(ps,11.5,3.0))
 # Short clerestory reveal beneath plate inferred from official3D; no invented window array.
 # Omit west/south unknown glazing rather than copying eastern facade.
# Western low wing only conservative massing, exact windows unavailable.
solid=Manifold.batch_boolean(P,OpType.Add)-Manifold.batch_boolean(C,OpType.Add)
solid=solid+Manifold.batch_boolean(D,OpType.Add)
s=150/96;solid=solid.scale((s,s,s)).translate((0,0,2))
m=solid.to_mesh64();mesh=trimesh.Trimesh(vertices=np.asarray(m.vert_properties[:,:3],dtype=np.float32).astype(float),faces=np.asarray(m.tri_verts),process=True);mesh.apply_transform(np.diag([1,-1,1,1]));mesh.export(O/'model.stl');print(mesh.bounds,mesh.is_watertight,len(mesh.faces))
(O/'draft-parameters.json').write_text(json.dumps({'status':'appearance review draft; QA pending; image based, not surveyed','main_height_m':16,'main_bound_m':[14,19],'E_height_m':13,'E_bound_m':[11.5,15],'FG_roof_m':14.5,'FG_low_roof_m':11.8,'FG_height_difference_bound_m':[1,4],'scope':'2A candidate main building and connected southwest wing, not entire campus','unknown':'FG low roof exact floor level and possible small skylight unknown; solid approximation. West windows omitted. Roof projection parallax not surveyed wall bases.','scale':s},indent=2))
