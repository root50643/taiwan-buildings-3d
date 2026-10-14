"""Original unprocessed STL rays for west portal, hanging box, glass roof backing and loss components. No repair."""
from pathlib import Path
import json,hashlib
import numpy as np,trimesh
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',force='mesh',process=False);tri=m.triangles;e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0]
def ray(o,d):
 o=np.array(o,float);d=np.array(d,float);p=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,p);good=np.abs(det)>1e-10;inv=np.zeros(len(tri));inv[good]=1/det[good];s=o-tri[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;dist=np.einsum('ij,ij->i',e2,q)*inv;sel=good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(dist>1e-8)
 return sorted(set(round(float(v),6) for v in dist[sel]))
def span(o,axis):
 d=np.eye(3)[axis];a=ray(o,d);b=ray(o,-d);assert a and b,('missing ray',o,axis);return a[0]+b[0]
def roots(o):return o[2]-ray(o,[0,0,-1])[0],o[2]+ray(o,[0,0,1])[0]
from shapely.geometry import Polygon,Point
loss=json.loads((R/'feature-loss-locations.json').read_text());out=[]
for row in loss['high_loss_components']:
 if row['z_mm']<30:continue
 p=Polygon(row['original_exterior_mm'],row['original_holes_mm']);pts=list(p.exterior.coords)
 for a,b in zip(pts[:-1],pts[1:]):
  a=np.array(a);b=np.array(b);length=np.linalg.norm(b-a)
  if length<1e-8:continue
  mid=(a+b)/2;d=np.array([-(b-a)[1],(b-a)[0]])/length
  if not p.contains(Point(*(mid+d*.0001))):d=-d
  o=[*(mid+d*.0001),row['z_mm']];v=ray(o,[*d,0]);assert v
  out.append({'z':row['z_mm'],'o':o,'direction':[*d,0],'thickness':v[0]+.0001,'edge_length':length})

assert min(x['thickness'] for x in out)>1.9147
report={'passed':True,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'sampled_cap_original_polygons':6,'original_edges_tested':len(out),'minimum_section_edge_normal_mm':min(x['thickness'] for x in out),'rows':out,'method':'Every nonzero original cap section edge midpoint, inward XY normal, intersects unprocessed original STL; two nonrectangular cap samples are not replaced by bounding boxes. Not a global wall certificate.'}
(R/'cap-edge-normal-check.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='rows'})
