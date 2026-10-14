"""STUST W living services building + integral gate, bounded exterior approximation.
Roof traced from 2023 ortho; wall bases/back service line provisional. Not surveyed.
World X east,Y north,Z up. All construction units nominal metres, output mm.
"""
from pathlib import Path
import numpy as np,json,trimesh
from manifold3d import Manifold,CrossSection,OpType
from shapely.geometry import Polygon
O=Path(__file__).parent; P=[];C=[];D=[]
M=.1375
def xy(p):return ((p[0]-1000)*M,(800-p[1])*M)
def section(ps):
 ps=list(ps)
 if Polygon(ps).exterior.is_ccw==False:ps=ps[::-1]
 return CrossSection([ps])
def poly(ps,z,h):return section(ps).extrude(h).translate((0,0,z))
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
# Plan trace is an aerial projection, not a surveyed wall-base trace.
roofpx=[(750,710),(860,1070),(1240,820),(970,500),(971,540),(965,575),(947,610),(918,640),(880,661),(835,681),(790,698)]
# Smooth cubic follows the observed concave plan edge, without changing gate/body endpoints.
ctrl=np.array([(970,500),(990,645),(880,673),(750,710)],float)
curve=[((1-t)**3*ctrl[0]+3*(1-t)**2*t*ctrl[1]+3*(1-t)*t*t*ctrl[2]+t**3*ctrl[3]).tolist() for t in np.linspace(0,1,33)]
roofpx=roofpx[:3]+curve[:-1]
bodypx=[(767,723),(870,1050),(1217,815),(1100,665)]
voidpx=[(900,790),(940,920),(1075,880),(1025,740)]
roof=[xy(p) for p in roofpx];body=[xy(p) for p in bodypx];court=[xy(p) for p in voidpx]
bp=Polygon(body);centre=np.array(bp.centroid.coords[0]); footprint=list(bp.buffer(-4.0,join_style=2).exterior.coords)[:-1]
P.append(poly(footprint,0,13.8));P.append(poly(body,13.5,27.0))
gate_tip=np.array(xy((970,500)))
cap=poly(roof,40.4,1.8)
cap=cap.warp(lambda v:(v[0],v[1],v[2]+.8*min(1,max(0,(v[1]-20.0)/17.0))))
P.append(cap)
# Actual open-sky upper courtyard has a solid 4F floor. 13.5m is bounded fit, not published elevation.
C.append(poly(court,13.5,35))
# Broad wall-like gate pier directly joins the curved-in-plan roof cap. No invented vertical arch.
gate=[xy(p) for p in [(956,510),(971,500),(1002,537),(987,549)]]
gate_print=list(Polygon(gate).buffer(.15,join_style=2).exterior.coords)[:-1]
P.append(poly(gate_print,0,43))
# Facade cutters are shallow, permanently backed by mass, not detached triangular louvers.
def facade_cut(a,b,verts,depth=.12,slant=0):
 a=np.array(a);b=np.array(b);u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]])
 if np.dot(n,centre-(a+b)/2)<0:n=-n
 # local x=facade distance,y=height,z=depth; transform into world.
 v=section(verts).extrude(depth+.05)
 if slant:
  top=max(p[1] for p in verts)
  v=v.warp(lambda q:(q[0],q[1]-slant*q[2] if abs(q[1]-top)<1e-7 else q[1],q[2]))
 mat=np.array([[u[0],-slant*n[0],n[0],a[0]+(13.0*slant-.05)*n[0]],[u[1],-slant*n[1],n[1],a[1]+(13.0*slant-.05)*n[1]],[0,1,slant,0]])
 C.append(v.transform(mat))
def panelwall(a,b,count):
 L=np.linalg.norm(np.array(b)-a);w=L/count
 for i in range(count):
  for j in range(7):
   x0=i*w+(.8 if i==0 else .20);x1=(i+1)*w-(.8 if i==count-1 else .20)
   z=13.8+j*3.76
   facade_cut(a,b,[(x0,z+3.43),(x1,z+3.43),(x0,z+.20)])
# North campus face and east road face separately counted in architect photographs.
NW,SW,SE,NE=body
panelwall(NW,NE,20);panelwall(NE,SE,15)
# Photo00 shows a short triangular return before the white service strip; do not texture the unknown full rear.
return_end=np.array(NW)+(np.array(SW)-NW)*.20
panelwall(NW,return_end,4)
# Three-storey public base: setback ground, continuous upper glass band.
# Source north glass is folded inward below upper tower, with lower sloping canopy.
a=np.array(NW);b=np.array(NE);u=(b-a)/np.linalg.norm(b-a);n=np.array([u[1],-u[0]]);L=np.linalg.norm(b-a)
if np.dot(n,centre-(a+b)/2)<0:n=-n
# A backed sectional prism forms the characteristic folded face, attached to solid base.
fold_section=[(0,13.6),(0,13.0),(3.5,4.6),(-.3,3.1523809523809523),(-.3,2.65),(8.0,2.7),(8.0,13.6)]
fold=section(fold_section).extrude(L-.10)
a=a+u*.05-n*.03
# section x=inward distance,y=height, extrusion z=along wall
P.append(fold.transform(np.array([[n[0],0,u[0],a[0]],[n[1],0,u[1],a[1]],[0,1,0,0]])))
# Ground main entrance recessed inside the base, leaving substantive side roots.
for i in range(1,19):
 for z,h in [(5.05,2.25),(7.8,2.2),(10.5,2.25)]:
  # Cut into backed glass slope; approximate panel positions shift with slope.
  shift=(13.5-z)*2.5/8.9
  aa=a;bb=b
  facade_cut(aa,bb,[(i*L/20+.25,z),((i+1)*L/20-.25,z),((i+1)*L/20-.25,z+h),(i*L/20+.25,z+h)],.35,3.5/8.4)
# East public facade is recessed and upright, unlike folded campus facade.
for z in [4.7,8.8]:
 aa=np.array(NE);bb=np.array(SE);vv=bb-aa;nn=np.array([-vv[1],vv[0]]);nn=nn/np.linalg.norm(nn)
 if np.dot(nn,centre-(aa+bb)/2)<0:nn=-nn
 aa+=nn*4.0;bb+=nn*4.0; le=np.linalg.norm(bb-aa)
 for i in range(3,12):facade_cut(aa,bb,[(i*le/12+.25,z),((i+1)*le/12-.25,z),((i+1)*le/12-.25,z+3.3),(i*le/12+.25,z+3.3)],.3)
# Ground frontage retreats behind the awning. Four substantive posts support the canopy.
a=np.array(NW);b=np.array(NE);u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]])
if np.dot(n,centre-(a+b)/2)<0:n=-n
L=np.linalg.norm(b-a)
# The lower core is set back4m; broad entrance recess retains the rear solid.
facade_cut(a+n*3.95,b+n*3.95,[(3.0,.2),(L-3.0,.2),(L-3.0,2.65),(3.0,2.65)],2.0)
facade_cut(a+n*3.95,b+n*3.95,[(L*.43,.2),(L*.58,.2),(L*.58,3.0),(L*.43,3.0)],5.0)
for t in [.15,.35,.65,.85]:
 c=a+u*L*t+n*2.0;D.append(box(c[0],c[1],0,1.2,1.2,3.1))
# Road-side low entrance canopy, seen below the two recessed upper glass levels.
aa=np.array(NE);bb=np.array(SE);uu=(bb-aa)/np.linalg.norm(bb-aa);nn=np.array([-uu[1],uu[0]])
if np.dot(nn,centre-(aa+bb)/2)<0:nn=-nn
strip=[aa-nn*.5,bb-nn*.5,bb+nn*4.8,aa+nn*4.8]
D.append(poly(strip,3.0,.7))
for t in [.25,.75]:
 c=aa+(bb-aa)*t+nn*.1;D.append(box(c[0],c[1],0,1.2,1.2,3.3))
# Inner gallery bands recessed into real walls; retain continuous backing.
for aa,bb in zip(court,court[1:]+court[:1]):
 # cutter helper normally points toward body centre; use simple buffered outward courtyard strips.
 pa=np.array(aa);pb=np.array(bb);u=(pb-pa)/np.linalg.norm(pb-pa);n=np.array([-u[1],u[0]])
 cc=np.array(Polygon(court).centroid.coords[0]);
 if np.dot(n,cc-(pa+pb)/2)>0:n=-n
 pa=pa+u*.3;pb=pb-u*.3
 strip=[pa-.05*n,pb-.05*n,pb+.32*n,pa+.32*n]
 for j in range(6):C.append(poly(strip,17.3+j*3.76,2.7))
assert all(str(p.status())=="Error.NoError" for p in P+C+D), "Invalid source construction"
solid=Manifold.batch_boolean(P,OpType.Add)-Manifold.batch_boolean(C,OpType.Add)
solid=solid+Manifold.batch_boolean(D,OpType.Add)
# Minimal base joins gate and hall, without exposing underground storeys.
mins=np.min(np.array(roof+gate),axis=0)-2;maxs=np.max(np.array(roof+gate),axis=0)+2
solid=solid+box(*((mins+maxs)/2),-1.2,*(maxs-mins),1.2)
s=150/max(maxs-mins);solid=solid.scale((s,s,s)).translate((0,0,1.2*s))
m=solid.to_mesh64();mesh=trimesh.Trimesh(vertices=np.asarray(m.vert_properties[:,:3],dtype=np.float32),faces=np.asarray(m.tri_verts),process=False);mesh.export(O/'model.stl')
print(mesh.bounds,len(mesh.faces))
(O/'draft-parameters.json').write_text(json.dumps({'status':'Bounded author model; independent release audit required','height_official_m':42.2,'gate_official_m':43,'cap_top_main_m':42.2,'cap_gate_tip_m':43,'body_top_m':40.4,'court_floor_nominal_m':13.5,'court_floor_bound_m':[12,15],'scale_mm_per_m':s,'source_pixel_polygons':{'roof':roofpx,'body_provisional':bodypx,'courtyard':voidpx},'aerial_m_per_pixel':M,'uncertainties':['High body northeast cap attachment line estimated from exterior photographs; rear service wall footprint uncertain','Roof projection contains height parallax, not surveyed wall bases','Back windows and unverified 1F rear appendage omitted','Courtyard floor at4F supported; its absolute elevation and inner balcony projections are bounded simplifications','Gate cap is curved in plan; no unsupported vertical arch added'],'underground':'not exposed; B2 supported by school and field signage'},ensure_ascii=False,indent=2))
