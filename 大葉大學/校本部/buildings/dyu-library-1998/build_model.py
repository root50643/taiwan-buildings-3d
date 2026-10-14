"""Da-Yeh University library: bounded evidence-based draft, not surveyed.
Local X facade right, Y rear. Main fan~85m, main roof18.5m estimated.
"""
from pathlib import Path
import json,numpy as np,trimesh
from manifold3d import Manifold,OpType,CrossSection,Mesh64
O=Path(__file__).resolve().parent;P=[];C=[];D=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):P.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):C.append(box(x,y,z,w,d,h))
def hull(v):return Manifold.hull_points(v)
def extrude(points,z,h):return CrossSection([points]).extrude(h).translate((0,0,z))
def angled_cut(a,b,z,h,parts=3):
 a=np.array(a);b=np.array(b);v=b-a;length=np.linalg.norm(v);angle=np.degrees(np.arctan2(v[1],v[0]));u=v/length
 for t in range(parts):
  center=a+u*(length*(t+.5)/parts)
  C.append(Manifold.cube((length/parts-.75,.64,h)).translate((-(length/parts-.75)/2,-.32,0)).rotate((0,0,angle)).translate((center[0],center[1],z)))
# Base, overall width94m ->150mm with base thickness2mm.
add(0,22,-1.2533333333333,94,64,1.2533333333333)
angles=np.linspace(0,np.pi,17)
outer=[(42.5*np.cos(a),10+36*np.sin(a)) for a in angles]
inner_ring=[(17.1*np.cos(a),5+17.1*np.sin(a)) for a in angles]
# Single explicit surface mesh across flat rear roof and sloped half-fan: no internal seams.
verts=[];faces=[];lookup={}
def V(x,y,z):
 key=(float(x),float(y),float(z))
 if key not in lookup:lookup[key]=len(verts);verts.append(key)
 return lookup[key]
def T(a,b,c):
 if np.linalg.norm(np.cross(np.array(b)-a,np.array(c)-a))>1e-10:faces.append((V(*a),V(*b),V(*c)))
cb=(0,5,0);ct=(0,5,10.8)
for i in range(len(outer)-1):
 a,b=outer[i],outer[i+1];u,v=inner_ring[i],inner_ring[i+1]
 A=(*a,18.5);B=(*b,18.5);U=(*u,18.5);W=(*v,18.5)
 T(cb,(*b,0),(*a,0));T(A,B,W);T(A,W,U);T(ct,U,W)
# Bottom front wedges and boundary walls, matching all shared vertices exactly.
T(cb,(*outer[0],0),(*inner_ring[0],0));T(cb,(*inner_ring[-1],0),(*outer[-1],0))
boundary=[(*p,18.5) for p in outer]+[(*inner_ring[-1],18.5),ct,(*inner_ring[0],18.5)]
for i,A in enumerate(boundary):
 B=boundary[(i+1)%len(boundary)];a=(A[0],A[1],0);b=(B[0],B[1],0)
 T(a,b,B);T(a,B,A)
P.append(Manifold(Mesh64(np.asarray(verts,float),np.asarray(faces,np.uint64))))
# Lower front rooms/terrace remain below the cone with a genuine open garden gap.
add(0,5,0,58,10,10.3)
rmax=17.1
# Shallow glass panes as conical wedge recesses with a strong solid backing.
for a in np.linspace(.025,np.pi-.025,21)[:-1]:
 b=min(a+(np.pi-.05)/20-.022,np.pi-.025)
 for ri,ro in [(1.8,4.2),(4.65,7.05),(7.5,9.9),(10.35,12.75),(13.2,15.6),(16.05,16.65)]:
  vertices=[]
  for rr,aa in [(ri,a),(ro,a),(ro,b),(ri,b)]:
   zz=10.8+7.7*rr/rmax
   vertices.extend([(rr*np.cos(aa),5+rr*np.sin(aa),zz-.08),(rr*np.cos(aa),5+rr*np.sin(aa),zz+.35)])
  C.append(Manifold.batch_boolean([hull(vertices),box(0,35,0,60,58.2,30)],OpType.Intersect))
# Front vertical V-shaped glass edges below the sloped roof; shallow backed panes.
for x in np.arange(-15.7,15.8,2.1):
 top=10.8+7.75*abs(x)/rmax
 for z in np.arange(10.6,top-1.0,1.8):cut(x,5,z,1.65,.32,min(1.4,top-z-.8))
# Open-book screen: continuous concave profile along the facade.
screen=[(-29,0),(29,0)]+[(x,min(19.0,11.3+8.2*(x/29)**2)) for x in np.linspace(29,-29,81)]
P.append(CrossSection([screen]).extrude(1.3).rotate((90,0,0)).translate((0,.65,0)))
# End rooms sit below tall ends; side screen returns taper back, not full-height infill.
for sg in [-1,1]:
 add(sg*25.2,5,10.2,7.6,9.8,3.6)
 D.append(hull([(sg*28.4+dx,y,z) for dx in [-.6,.6] for y,h in [(0,19.0),(10,14.0)] for z in [10.1,h]]))
 # Inward backing along end screen: connect to main roof, preserving outer tapered face.
 D.append(box(sg*28.45,4.7,13.5,1.0,9.4,5.1))
 # Local cap backing after0.8mm truncation, no global lowering of curved wall.
 D.append(box(sg*28.4,.6,18.4,1.2,2.5,.6))
 # Terrace end-room window faces into the garden.
 cut(sg*21.4,4.3,11.0,.3,3.8,2.0)
# True recessed central portal; a rear glass plane remains behind the covered entry.
cut(0,2.3,1.15,17.5,7.0,8.4)
add(0,6.1,1.1,17.5,.8,8.5)
for x in [-7,-4.7,-2.35,0,2.35,4.7,7]:
 for z,h in [(1.4,3.2),(5.0,2.3),(7.7,1.3)]:cut(x,5.8,z,1.8,.3,h)
# Front long bands: four upper groups and three broader lower panes per low wing.
for side in [-1,1]:
 for z,h in [(1.4,3.0),(6.0,2.8)]:cut(side*18.7,-.65,z,17.8,.45,h)
 for x in [14.2,19.2,24.2]:D.append(box(side*x,-.15,6.0,.65,1.0,2.8))
 for x in [16.2,22.5]:D.append(box(side*x,-.15,1.4,.65,1.0,3.0))
# Two full-height entrance piers, locally fluted before fusing after portal cut.
for x in [-5.7,5.7]:
 q=box(x,.1,1.1,1.5,1.5,8.6)
 # Fine flutes on these independent piers omitted; outer wall jamb flutes remain.
 D.append(q)
# Broad entry piers carry shallow vertical flutes, not tiny added columns.
for x in [-9.4,9.4]:
 for dx in [-.55,0,.55]:
  for z in [1.3,4.4,7.5]:cut(x+dx,-.65,z,.22,.24,2.5)
# Two source-visible outer side low-wing window rows.
for sg in [-1,1]:
 for y in [2.5,6.5]:
  for z in [1.6,6.0]:cut(sg*29,y,z,.4,2.8,2.65)
# High front radial faces show one upper long window level above the lower wings.
angled_cut((42.5,10),(17.1,5),14.1,3.1,6)
angled_cut((-17.1,5),(-42.5,10),14.1,3.1,6)
# Rear exterior window rhythm is conservative: floor plans + interior photos, not surveyed bays.
for a,b in zip(outer[:-1],outer[1:]):
 for z in [1.3,5.6,9.9,14.2]:angled_cut(a,b,z,3.1,3)
# Higher service core on facade-right only, seen in2020 high angle.
add(23,13,18.3,9.5,7.8,4.6)
cut(23,9.1,20.0,6.8,.4,1.5)
# Low side extension/cap of that core, not a mirrored second tower.
add(16.9,13,21.9,3.1,7.8,1.0)
D.append(box(16.1,13,17.5,1.2,7.8,4.6))
# Terrace planters are rooted low relief; clear walking air remains around them.
for x in [-11.5,11.5]:P.append(Manifold.cylinder(.7,1.8,1.8,32).scale((1.3,1,1)).translate((x,2.5,10.3)))
# Source entrance steps down to forecourt.
for i in range(9):add(0,-5.0+i*.55,0,15.5,.8,.14*(i+1))
solid=Manifold.batch_boolean(P,OpType.Add)-Manifold.batch_boolean(C,OpType.Add)
solid=solid+Manifold.batch_boolean(D,OpType.Add)
scale=150/94
solid=solid.scale((scale,scale,scale)).translate((0,0,2)).simplify(.000005)
m=solid.to_mesh64();mesh=trimesh.Trimesh(vertices=np.asarray(m.vert_properties[:,:3],dtype=np.float32).astype(float),faces=np.asarray(m.tri_verts),process=True);mesh.export(O/'model.stl');print(mesh.bounds,mesh.is_watertight,len(mesh.faces))
(O/'draft-parameters.json').write_text(json.dumps({'status':'bounded exterior approximation; not surveyed','main_roof_m':18.5,'roof_range_m':[16,22],'rear_fan_width_m':85,'front_low_wing_width_m':58,'roof_terrace_m':10.3,'front_screen_centre_end_nominal_m':[11.3,19.5],'printed_end_cap_m':19.0,'glass_apex_outer_m':[10.8,18.5],'scale_mm_per_estimated_m':scale,'unknown':'Official1F drawing has inconsistent relative scale versus2–4F. Front footprint uses roof and2–4F bounded fit; terrace4F assignment remains a candidate. Rear exterior exact bays and all heights unmeasured.'},indent=2))
