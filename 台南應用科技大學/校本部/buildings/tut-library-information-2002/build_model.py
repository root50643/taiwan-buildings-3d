from pathlib import Path
import json,numpy as np,trimesh
from manifold3d import Manifold,CrossSection,OpType
from shapely.geometry import Polygon
O=Path(__file__).parent;P=[];C=[];D=[];M=.1373839611
px=[(185,48),(378,48),(526,181),(534,382),(288,615),(210,615)]
xy=lambda p:((p[0]-359.5)*M,(331.5-p[1])*M)
pts=[xy(p) for p in px];center=np.array(Polygon(pts).centroid.coords[0])
def sec(p):return CrossSection([p if Polygon(p).exterior.is_ccw else p[::-1]])
def poly(p,z,h):return sec(list(map(list,p))).extrude(h).translate((0,0,z))
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def frame(i):
 a=np.array(pts[i]);b=np.array(pts[(i+1)%6]);u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]])
 if n@(center-(a+b)/2)<0:n=-n
 return a,u,n,np.linalg.norm(b-a)
def piece(i,x,z,w,h,depth=.45,offset=0,cut=True):
 a,u,n,L=frame(i);q=a+u*x+n*offset
 ob=Manifold.cube((w,depth+.04,h)).transform(np.array([[u[0],n[0],0,q[0]-.02*n[0]],[u[1],n[1],0,q[1]-.02*n[1]],[0,0,1,z]]))
 (C if cut else P).append(ob)
P.append(poly(pts,0,46))
i=3;a,u,n,L=frame(i)
piece(i,2,0,L-4,9.4,2.8)
for x in [3,L*.29,L*.5,L*.71,L-3]:
 piece(i,x-.55,0,1.1,9.5,3.2,cut=False);D.append(P.pop())
for z,h in [(1,3.9),(5.4,3.0)]:
 for j in range(9):piece(i,2.5+j*(L-5)/9,z,(L-5)/9-.5,h,.3,offset=2.79)
left=L*.27;right=L*.73
piece(i,left,11.8,right-left,15.4,1.45,offset=-1.35,cut=False)
for j in range(8):
 for z,h in [(12.4,3),(15.9,3),(19.4,3),(22.9,3.8)]:piece(i,left+.5+j*(right-left-1)/8,z,(right-left-1)/8-.5,h,.22,offset=-1.36)
for x in [L*.10,L*.84]:
 for z,h in [(10.3,3),(14.2,3),(18.1,3),(22,3),(26,3),(30.4,3.3),(34.9,3.3),(39.4,3.3)]:piece(i,x,z,2.5,h)
for x in [L*.235,L*.715]:
 for z in [10.2,14.1,18,21.9,25.8]:piece(i,x,z,2.4,3.1)
for z in [30.4,34.9,39.4]:
 for j in range(6):
  x=L*.235+j*L*.09;w=L*.065
  piece(i,x,z,w,2.05,.8);piece(i,x,z+2.55,w,.6,.8)
# Four centre bays have deep framing and thin transom division on actual mesh.
for j in range(5):
 piece(i,L*.312+j*L*.09,34.55,.55,8.35,.65,offset=-.50,cut=False);D.append(P.pop())
for z in [34.55,42.6]:
 piece(i,L*.312,z,L*.36+.55,.5,.65,offset=-.50,cut=False);D.append(P.pop())
piece(i,L*.23,28,L*.54,.7,1.5,offset=-1.4,cut=False);D.append(P.pop())
piece(i,L*.41,29.1,L*.25,.65,1.9,offset=-1.8,cut=False)
i=2;a,u,n,L=frame(i)
for z in [31,35.5,40]:
 for j in range(4):piece(i,2+j*(L-4)/4,z,(L-4)/4-2,3)
for z in [1,6,11,16,21,26]:
 for x in [1.8,L-4.2]:piece(i,x,z,2.3,3.1)
piece(i,L*.35,12,L*.31,16,1.2,offset=-1.1,cut=False)
for z in [12.5,16.2,20,23.8]:
 for j in range(3):piece(i,L*.35+.5+j*(L*.31-1)/3,z,(L*.31-1)/3-.5,3.1,.22,offset=-1.11)
i=4;a,u,n,L=frame(i)
for z in [1,6,11,16,21,26,31,36,41]:
 for x in [1.5,L-3.7]:piece(i,x,z,2.2,3)
# Rear 2025 frame is cropped: populate the visible south portion only, leaving north unknown.
i=5;a,u,n,L=frame(i)
for z in [1.2,6.3,11.4,16.5]:
 for j in range(4):
  x=3+j*8.4
  piece(i,x,z,6.1,2.6,.8);piece(i,x,z+3.1,6.1,.75,.8)
 for x in [38,46]:piece(i,x,z,3.5,3.5,.65)
for x in [2.2,10.6,19,27.4,35.8]:piece(i,x,.7,.65,21.3,.7,offset=-.45,cut=False)
for z in [5.5,10.6,15.7,20.8]:piece(i,2.2,z,34.2,.55,.7,offset=-.45,cut=False)
piece(i,1.5,22.0,50,.85,1.35,offset=-1.15,cut=False)
for z in [23.8,28.1]:
 for j in range(4):piece(i,3+j*8.4,z,6.1,3.1,.65)
 for x in [38,46]:piece(i,x,z,3.5,3.1,.6)
for z in [33,37.4,41.7]:
 for j in range(6):
  x=3+j*8
  piece(i,x,z,4.4,2.0,.6);piece(i,x,z+2.5,4.4,.55,.6)
for x in [2.1,10.1,18.1,26.1,34.1]:piece(i,x,32.5,.55,12,.65,offset=-.4,cut=False)
P.append(poly([xy(p) for p in [(189,77),(241,77),(248,594),(211,594)]],46,1.4))
P.append(box(*xy((232,351)),46,11,13,3));P.append(box(*xy((284,81)),46,13,5,2.7))
P.append(Manifold.cylinder(1.8,4.4,4.4,64).translate((*xy((287,287)),46)))
i=3;a,u,n,L=frame(i);x0=L*.31;w=L*.38
curve=[(x0+w*t,6.6+1.7*np.sin(np.pi*t)) for t in np.linspace(0,1,33)]
profile=curve+[(x,z-1) for x,z in curve[::-1]]
D.append(sec(profile).extrude(9.3).transform(np.array([[u[0],0,n[0],a[0]-5.4*n[0]],[u[1],0,n[1],a[1]-5.4*n[1]],[0,1,0,0]])))
# Finite side-edge beams prevent knife-like section tongues at barrel springing.
for x in [x0,x0+w-.9]:
 piece(i,x-.03,5.35,.96,1.35,9.4,offset=-5.43,cut=False);D.append(P.pop())
for x in [x0+.65,x0+w-.65]:
 q=a+u*x-n*4.8;D.append(box(*q,0,1.1,1.1,7))
for k in range(3):piece(i,L*.29,-.03,L*.42,.2*(k+1),1.7*(3-k),offset=-1.7*(3-k),cut=False)
solid=Manifold.batch_boolean(P,OpType.Add)-Manifold.batch_boolean(C,OpType.Add)
solid=solid+Manifold.batch_boolean(D,OpType.Add)
lo=np.min(pts,axis=0)-7;hi=np.max(pts,axis=0)+3
solid=solid+box(*((lo+hi)/2),-1.2,*(hi-lo),1.2)
s=150/max(hi-lo);solid=solid.scale((s,s,s)).translate((0,0,s*1.2));m=solid.to_mesh64();mesh=trimesh.Trimesh(vertices=np.asarray(m.vert_properties[:,:3],dtype=np.float32),faces=np.asarray(m.tri_verts),process=False);mesh.export(O/'model.stl')
(O/'draft-parameters.json').write_text(json.dumps({'scale_mm_per_m':s,'body_height_nominal_m':46,'body_height_trial_bound_m':[42,50],'roof_equipment_height_bound_m':[1,4],'roof_pixel_trace':px,'aerial_m_per_px':M,'source_years':[2002,2018,2022,2025],'limitations':['No measured heights; cross-year approximate facade','North and northeast unknown windows omitted','Roof trace is parallax projection; not wall base overhang','Roof circle conservatively low cap; shape and height unknown','West observed south portion only; unknown northern windows omitted'],'status':'visual review draft; no release QA'},ensure_ascii=False,indent=2));print(len(mesh.faces),mesh.bounds)
