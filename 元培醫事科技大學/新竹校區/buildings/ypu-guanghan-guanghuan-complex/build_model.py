"""YPU L/H appearance candidate only. Heights/terrain are bounded image estimates, not survey."""
from pathlib import Path
import json, numpy as np, trimesh
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
from manifold3d import Manifold,CrossSection,OpType,Mesh64
R=Path(__file__).parent;D=json.loads((R/'plan-registration.json').read_text()); S=1.07; B=1.6; MPP=.13554824373866425
parts=[];cuts=[]
def xy(p): return np.array([(p[0]-790)*MPP,(640-p[1])*MPP])
def coords(points,k=None):
 p=np.array(points,float)
 if k:p=(np.c_[p,np.ones(len(p))]@np.array(D[k]['matrix']).T)[:,:2]
 return np.array([xy(v) for v in p])
def extr(p,z0,z1):
 p=np.round(np.asarray(p)*S,4)
 if not Polygon(p).exterior.is_ccw:p=p[::-1]
 return CrossSection([p.tolist()]).extrude((z1-z0)*S).translate((0,0,B+z0*S))
def box(x,y,w,d,z0,z1):return Manifold.cube((w*S,d*S,(z1-z0)*S)).translate(((x-w/2)*S,(y-d/2)*S,B+z0*S))
def addpoly(p,z0,z1):parts.append(extr(p,z0,z1))
def linebar(a,b,w,z0,z1):
 a=np.asarray(a);b=np.asarray(b);v=b-a;n=np.array([-v[1],v[0]])/np.linalg.norm(v)*w/2
 return extr([a+n,b+n,b-n,a-n],z0,z1)
Lsrc=[[95,333],[150,313],[210,298],[325,285],[440,290],[555,315],[660,355],[760,413],[820,450],[730,610],[650,570],[520,490],[480,570],[320,540],[260,530],[100,550],[30,420]]
Gsrc=[[100,550],[130,640],[210,680],[300,698],[380,680],[450,640],[490,580],[480,570],[320,540],[260,530]]
Hsrc=[[15,180],[30,153],[65,148],[80,155],[145,100],[175,75],[205,75],[230,90],[240,118],[275,120],[340,145],[380,185],[395,210],[510,190],[635,190],[760,205],[880,240],[1020,300],[910,500],[790,465],[650,450],[530,460],[410,500],[285,560],[175,510],[80,410],[30,300]]
L=coords(Lsrc,'L');G=coords(Gsrc,'L');H=coords(Hsrc,'H')
for p in [L,G,H]:assert Polygon(p).is_valid
body_plan=unary_union([Polygon(p)for p in [L,G,H]]+[Polygon(coords([[700,815],[752,820],[766,700],[733,691]]))])
# All ground grades schematic. Front raised forecourt; rear visible grey podium not two full exposed floors.
parts.append(Manifold.cube((150,102,B)).translate((-75,-51,0)))
for p in [L,H]:addpoly(p,-.05,26)
addpoly(G,-.05,24.3)
# robust central seam connection (within observed continuous crescent)
addpoly(coords([[700,815],[752,820],[766,700],[733,691]]),-.05,26)
# Grey plinth shown through continuous shallow perimeter reveal, not a separate floating structure.
# Curved front bands: source-specific seven H broad bays, L tall white piers, five rows.
# Cut shallow window panels along individually traced polygon segments.
def facade(points,rows,baywidth=3.0,depth=.34,margin=.8,counts=None):
 for seg,(a,b) in enumerate(zip(points[:-1],points[1:])):
  a=np.array(a);b=np.array(b);v=b-a;length=np.linalg.norm(v)
  if length<2:continue
  u=v/length;n=np.array([-u[1],u[0]])
  count=counts[seg] if counts else max(1,round(length/baywidth))
  for j in range(count):
   mg=margin[seg] if isinstance(margin,list) else margin
   if length/count<=mg+.8:continue
   q=a+u*(length*j/count+mg/2);r=a+u*(length*(j+1)/count-mg/2)
   cutpoly=[q+n*depth,r+n*depth,r-n*depth,q-n*depth]
   if Polygon(cutpoly).difference(body_plan).area < .01:continue
   for lo,hi in rows:cuts.append(extr(cutpoly,lo,hi))
rows=[(5.4,8.0),(9.5,12.2),(13.7,16.4),(17.9,20.6),(22.1,24.8)]
# Inward front arc points taken from plans, not arbitrary mirrored rear grid.
Hfront=coords([[910,500],[790,465],[650,450],[530,460],[410,500],[285,560]],'H');facade(Hfront,rows,6.8,margin=[4,1.25,1.25,1.25,1.25],counts=[1,2,1,1,2])
Lfront=coords([[730,610],[650,570],[520,490]],'L');facade(Lfront,rows,6.4,margin=[3.0,1.15],counts=[1,2])
# L west external wall visible in historic garden picture: major tall bays with grey podium.
Lrear=coords([[95,333],[150,313],[210,298],[325,285],[440,290],[555,315],[660,355],[760,413]],'L');facade(Lrear,rows,3.4)
# H unknown outer windows intentionally omitted. End curved room two bulges are retained.
Hend=coords(Hsrc[:11],'H') # Unknown outer-terminal fine windows omitted; observed oval wide windows remain.
# Glazed entry convex shell: backed shallow windows, continuous thick solid substrate.
Gface=coords(Gsrc[:6],'L');facade(Gface,[(6,8.5),(9.5,12),(13,15.5),(16.5,19),(20,23.3)],3.6,.15,1.0)
# Main roof cap, roof slope is not measured. Keep generous connected cap thickness.
for p in [L,H]:addpoly(p,25.8,26.8)
# front roof edge pergola rendered as thick backed relief on roof, no unsupported paper-thin lattice.
for chain in [Hfront,Lfront]:
 for a,b in zip(chain[:-1],chain[1:]):parts.append(linebar(a,b,1.1,26.6,27.6))
# Front open pergola, coarse connected posts and top rails, source-visible major rhythm.
for chain in [Hfront,Lfront]:
 for a,b in zip(chain[:-1],chain[1:]):
  parts.append(linebar(a,b,1.6,28.3,29.3))
  for t in np.linspace(0,1,max(2,round(np.linalg.norm(b-a)/3))):
   q=a+(b-a)*t;parts.append(box(q[0],q[1],1.4,1.4,26.5,28.6))
# Bounded rear landscape grade only, not a claimed B1/B2 design elevation.
slope_plan=LineString(Lrear).buffer(4.0,cap_style=2,join_style=2)
assert slope_plan.is_valid
slope=extr(np.array(slope_plan.exterior.coords)[:-1],-.03,1.0)
sm=slope.to_mesh64();sv=np.array(sm.vert_properties,copy=True);top=sv[:,2]>B+.5*S
axis=Lrear[-1]-Lrear[0];u=((sv[top,:2]/S-Lrear[0])@axis)/(axis@axis)
sv[top,2]=B+(.5+2.3*u)*S
parts.append(Manifold(Mesh64(sv,np.array(sm.tri_verts,dtype=np.uint64,copy=True))))
# L west dual stair enclosures and central outer single stair, traced separately.
for plan,z in [([[750,420],[830,450],[795,500],[720,470]],30.0),([[720,495],[795,520],[735,610],[680,570]],28.8),([[30,420],[100,390],[140,450],[65,485]],29.2)]:addpoly(coords(plan,'L'),-.03,z)
# H east oval roof tower is a curved open perimeter in source. Thick solid rear-backed oval cue for draft.
c=xy([1152,679]);ang=np.linspace(0,2*np.pi,48,endpoint=False);rot=np.array([[np.cos(-.80),-np.sin(-.80)],[np.sin(-.80),np.cos(-.80)]]);oval=np.c_[7*np.cos(ang),3.5*np.sin(ang)]@rot.T+c
addpoly(oval,-.03,29.1)
inner_oval=np.c_[5.8*np.cos(ang),2.3*np.sin(ang)]@rot.T+c
cuts.append(extr(inner_oval,26.9,29.6))
# H end photographed broad horizontal windows, plus narrow stair strips.

for lo,hi in rows:
 # long exterior-facing slots in H terminal oval; back remains thick.
 cuts.append(extr(np.array([[-4,2.975],[4,2.975],[4,3.725],[-4,3.725]])@rot.T+c,lo,hi))
for t in [-.6,.6]:
 cuts.append(extr((np.array([[6.35,t-.35],[7.15,t-.35],[7.15,t+.35],[6.35,t+.35]])@rot.T+c),6,24.4))
# Forecourt at estimated +4m. Five compact entrance treads connect glass base.
fore=coords([[545,582],[750,684],[900,670],[1050,610],[1000,490],[700,460]])
addpoly(fore,-.03,4)
entry=xy([700,650]);n=np.array([.6,.8]);u=np.array([-.8,.6])
for j in range(5):
 depth=4.0-j*.65
 step=[entry-u*6-n*.8,entry+u*6-n*.8,entry+u*6+n*depth,entry-u*6+n*depth]
 addpoly(step,-.03,4.25+j*.25)
print('part statuses',[(i,p.status())for i,p in enumerate(parts)if p.status().name!='NoError'],'cut statuses',[(i,p.status())for i,p in enumerate(cuts)if p.status().name!='NoError'])
def grid(p):
 m=p.to_mesh64();return Manifold(Mesh64(np.ascontiguousarray(np.round(m.vert_properties,4)),np.array(m.tri_verts,dtype=np.uint64,copy=True)))
mass=Manifold.batch_boolean([grid(p)for p in parts],OpType.Add)
exposed_cuts=[grid(p) for p in cuts if (grid(p)-mass).volume()>1e-6]
solid=mass-Manifold.batch_boolean(exposed_cuts,OpType.Add)
assert solid.status().name=='NoError';m=solid.to_mesh64();mesh=trimesh.Trimesh(np.array(m.vert_properties[:,:3],dtype=np.float32),np.array(m.tri_verts),process=False);mesh.export(R/'model.stl')
(R/'candidate-assumptions.json').write_text(json.dumps({'status':'appearance-only candidate; QA not complete','scale_mm_per_m':S,'wall_roof_m':26,'working_roof_range_m':[23,29],'highest_service_m':30,'forecourt_m':4,'basement_exposure':'not measured; terrain and grey plinth schematic','unknown_H_rear_windows':'omitted','plans':D,'components':{'L':L.tolist(),'H':H.tolist(),'glazed_entry':G.tolist()}},ensure_ascii=False,indent=2))
print('faces',len(mesh.faces),'bounds',mesh.bounds.tolist(),'watertight',mesh.is_watertight,'components',len(mesh.split(only_watertight=False)))
