"""Original exterior candidate: NPUST YuKang Library. Image bounded, not measured."""
from pathlib import Path
import json,numpy as np,trimesh
from manifold3d import Manifold,CrossSection,OpType,Mesh64
R=Path(__file__).parent; S=1.2; B=1.6
parts=[]; cuts=[]; reliefs=[]
def box(x,y,w,d,z0,z1):
 return Manifold.cube((w*S,d*S,(z1-z0)*S)).translate(((x-w/2)*S,(y-d/2)*S,B+z0*S))
def add(x,y,w,d,z0,z1):parts.append(box(x,y,w,d,z0,z1))
def cut(x,y,w,d,z0,z1):cuts.append(box(x,y,w,d,z0,z1))
def beam(a,b,w):
 a=np.array(a)*S+[0,0,B];b=np.array(b)*S+[0,0,B];v=b-a
 z=v/np.linalg.norm(v);ref=np.array([1.,0,0])
 if abs(z@ref)>.9:ref=np.array([0.,1,0])
 x=np.cross(ref,z);x/=np.linalg.norm(x);y=np.cross(z,x)
 M=np.column_stack([x,y,z,a]);return Manifold.cube((w*S,w*S,np.linalg.norm(v))).translate((-w*S/2,-w*S/2,0)).transform(M)
# Base and continuous raised podium. B1 exists but its full exposed ring is not inferred.
parts.append(Manifold.cube((150,96,B)).translate((-75,-48,0)))
add(0,0,118,52,-.03,2.5)
# Three connected lower-storey blocks: internal wall rectangle and exterior colonnades differ.
add(0,0,114,42.0,2.3,15.8)
# North/south high fourth-floor volumes overhang the lower walls.
for xc in [-36,36]:
 add(xc,0,44,50,15.5,22.0)
 # Four broad perimeter end piers at ends of each side recess.
 for xx in [xc-19,xc+19]:
  for yy in [-23.9,23.9]:add(xx,yy,6.8,2.2,2.3,15.8)
 # lower recessed long side windows, grouped in six large bays, not tiny uniform holes
 for yy in [-20.95,20.95]:
  for xx in np.linspace(xc-12,xc+12,5):
   for z in [3.4,7.8,12.2]:cut(xx,yy,4.9,.55,z,z+1.85)
 # continuous long fourth-floor glazing, shallow-backed fine mullions
 for yy in [-25,25]:
  cut(xc,yy,26.0,.7,17.0,18.65)
  for xx in np.linspace(xc-12,xc+12,19):
   reliefs.append(box(xx,np.sign(yy)*24.67,.22,.28,16.9,18.75))
 # main inner columns remain continuous and connect to the roof soffit
 for xx in np.linspace(xc-15,xc+15,6):
  for yy in [-23.9,23.9]:add(xx,yy,1.15,1.15,2.35,15.8)
 # flat roof parapet / PV equipment as broad backed slab, no free panel wires
 add(xc,0,43.3,49.3,21.8,22.55)
 add(xc,0,39.5,45.0,22.45,23.35)
 # shallow array group divisions: solid substrate retained
 for xx in np.linspace(xc-14.2,xc+14.2,5):cut(xx,0,.55,45.2,23.10,23.6)
 for yy in [-15,0,15]:cut(xc,yy,39.7,.55,23.10,23.6)
# Central five-bay front, official 2026 photo: 3 visible rows under low name beam.
for yy in [-20.95,20.95]:
 for xx in [-11.2,-5.6,0,5.6,11.2]:
  for z in [3.4,7.8,12.2]:cut(xx,yy,4.9,.55,z,z+1.85)
for xx in [-14,-8.4,-2.8,2.8,8.4,14]:
 add(xx,-24.1,1.15,1.15,2.3,16.0)
 # rear central columns, broad identity visible; fine windows unknown retained as coarse bands
 add(xx,24.1,1.15,1.15,2.3,16.0)
add(0,-24.6,30,1.9,15.1,16.3);add(0,24.6,30,1.9,15.1,16.3)
# Central low curved roof: bounded shallow segment, cap extends into high wing walls.
ys=np.linspace(-25,25,33);zs=16.0+1.6*(1-(ys/25)**2)
poly=[[float(y),float(z)]for y,z in zip(ys,zs)]+[[25,15.5],[-25,15.5]]
# cross section XY here is y,z; extrusion becomes long-axis x
cap=CrossSection([poly[::-1]]).extrude(29).transform([[0,0,1,-14.5],[1,0,0,0],[0,1,0,0]])
parts.append(cap.scale((S,S,S)).translate((0,0,B)))
# North-end existing steel frame as one original 2D union, then uniform extrusion.
# Nine modules; lower 2 levels X at 1/4/6/9, upper short N/V/X groups.
from shapely.geometry import Polygon,box as rect
from shapely.ops import unary_union
steel=[]
def pole(y,w,z0,z1):steel.append(rect(y-w/2,z0,y+w/2,z1))
def rail(z,h):steel.append(rect(-24.5,z-h/2,24.5,z+h/2))
def diagonal(a,b,w=.95):
 a=np.array(a);b=np.array(b);v=b-a;n=np.array([-v[1],v[0]])/np.linalg.norm(v)*w/2
 steel.append(Polygon([a+n,b+n,b-n,a-n]))
ys=np.linspace(-24,24,10)
for j in [0,1,3,4,5,6,8,9]:pole(ys[j],1.1,2.3,15.8)
for z in [2.7,7.4,12.3,15.4]:rail(z,.88)
for j in [0,3,5,8]:
 for lo,hi in [(2.7,7.4),(7.4,12.3),(12.3,15.4)]:
  a,b=ys[j:j+2];diagonal((a,lo),(b,hi));diagonal((b,lo),(a,hi))
for lo,hi,rev in [(1,3,False),(6,8,True)]:
 vs=np.linspace(ys[lo],ys[hi],5)
 for y in vs[1:-1]:pole(y,.95,12.2,15.5)
 for a,b in zip(vs[:-1],vs[1:]):diagonal((a,12.3 if rev else 15.4),(b,15.4 if rev else 12.3))
mid=(ys[4]+ys[5])/2;pole(mid,.95,12.2,15.5)
diagonal((ys[4],15.4),(mid,12.3));diagonal((mid,12.3),(ys[5],15.4))
assert all(g.is_valid for g in steel)
g=unary_union(steel);assert g.is_valid and g.geom_type=='Polygon'
contours=[np.array(g.exterior.coords[:-1]).tolist()]+[np.array(h.coords[:-1]).tolist()for h in g.interiors]
# Shapely exterior clockwise normalized to positive winding and holes negative.
from shapely.geometry.polygon import orient
g=orient(g,sign=1);contours=[list(g.exterior.coords[:-1])]+[list(h.coords[:-1])for h in g.interiors]
frame=CrossSection(contours).extrude(1.1).transform([[0,0,1,-58.7],[1,0,0,0],[0,1,0,0]])
reliefs.append(frame.scale((S,S,S)).translate((0,0,B)))
# Northern inner end window bands behind braces; southern end restrained because hidden.
for yy in np.linspace(-14.7,14.7,6):
 for z in [3.4,7.8,12.2]:cut(-57,yy,.65,4.4,z,z+2.15)
cut(-58,0,.7,45.0,17,18.65)
for yy in np.linspace(-21.5,21.5,31):reliefs.append(box(-57.67,yy,.28,.22,16.9,18.75))
# Central broad west approach rises into same podium; finite sturdy treads.
stairs=[[-38.05,-.03],[-38.05,.25]]
for j in range(1,10):stairs.extend([[-38.05+j*1.3,j*.25],[-38.05+j*1.3,(j+1)*.25]])
stairs.extend([[-24.45,2.5],[-24.45,-.03]])
step=CrossSection([stairs[::-1]]).extrude(34).transform([[0,0,1,-17],[1,0,0,0],[0,1,0,0]])
parts.append(step.scale((S,S,S)).translate((0,0,B)))
# No inferred full B1 glazing, exact small service structures omitted.
def grid(p):
 m=p.to_mesh64();return Manifold(Mesh64(np.ascontiguousarray(np.round(m.vert_properties,4)),np.array(m.tri_verts,dtype=np.uint64,copy=True)))
print([(i,p.status())for i,p in enumerate(parts+cuts)if p.status().name!='NoError']); assert all(p.status().name=='NoError'for p in parts+cuts)
solid=Manifold.batch_boolean([grid(p)for p in parts],OpType.Add)-Manifold.batch_boolean([grid(c)for c in cuts],OpType.Add)
solid=solid+Manifold.batch_boolean([grid(r)for r in reliefs],OpType.Add)
assert solid.status().name=='NoError';m=solid.to_mesh64();mesh=trimesh.Trimesh(np.array(m.vert_properties[:,:3],dtype=np.float32),np.array(m.tri_verts),process=False);mesh.export(R/'model.stl')
(R/'candidate-assumptions.json').write_text(json.dumps({'status':'bounded exterior; approval status and numerical limitations are recorded separately in QA','scale_mm_per_m':S,'roof_outer_m':[116,50],'wall_rectangle_m':[114,42.0],'height_working_m':22,'height_range_m':[19,25],'central_roof_m':[16,17.6],'sources_versions':'1991 official front; 2012 east streetview; 105 academic-year north; 2024-labeled roof; 2026 official front','print_simplifications':['X steel braces enlarged','PV thick solid slabs with shallow array divisions','window frames backed shallow relief','B1 exposure not invented'],'unknowns':['south short facade details','exact story elevations','central barrel rise','roof PV installation date']},ensure_ascii=False,indent=2))
print('faces',len(mesh.faces),'bounds',mesh.bounds.tolist(),'watertight',mesh.is_watertight,'components',len(mesh.split(only_watertight=False)))
