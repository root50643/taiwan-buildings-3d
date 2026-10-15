"""Dense short first-chord classification with original surface tangent curves and backing."""
from pathlib import Path
import gzip,json,numpy as np,hashlib,trimesh
O=Path(__file__).parent;m=trimesh.load(O/'model.stl',process=False);T=m.triangles
def ray(o,d):
 o=np.array(o);d=np.array(d);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];p=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,p);good=abs(det)>1e-10;inv=np.zeros(len(T));inv[good]=1/det[good];s=o-T[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;t=np.einsum('ij,ij->i',e2,q)*inv;hs=sorted(set(round(float(x),7) for x in t[good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)]));return [x for j,x in enumerate(hs) if j==0 or x-hs[j-1]>1e-6]
j=json.load(gzip.open(O/'dense-first-chords.json.gz','rt'));assert j['stl_sha256']==hashlib.sha256((O/'model.stl').read_bytes()).hexdigest()
rows=[]
for r in j['samples']:
 if r['first_solid_mm']>=.8:continue
 p=np.array(r['point_mm']);n=np.array(r['normal']);src=p/(150/83.5)-[0,0,1.2];relief=12.4<src[2]<18.8 and 16.85<abs(src[1])<17.2 and abs(n[0])>.99
 row={**r,'class':'backed shallow window mullion' if relief else 'finite XY outline corner'}
 if relief:
  # Original side point moved only0.0001mm into its printed rib, then towards broad backing.
  start=p-n*.0001;d=np.array([0,-np.sign(p[1]),0]);hs=ray(start,d);row['backing_direction']=d.tolist();row['backing_first_exit_mm']=hs[0] if hs else None;row['backing_hits_mm']=hs[:4]
 else:
  tangent=np.array([-n[1],n[0],0]);curves=[]
  for sign in [-1,1]:
   curve=[]
   for offset in [0,.1,.2,.4,.8,1.2]:
    q=p+sign*tangent*offset;hs=ray(q+n*.0001,-n);valid=len(hs)>=2 and abs(hs[0]-.0001)<.00005
    curve.append({'offset_mm':offset,'point_mm':q.tolist(),'on_original_plane_surface':valid,'first_solid_mm':hs[1]-hs[0] if valid else None,'hits_mm':hs[:4]})
   curves.append({'tangent_direction':(sign*tangent).tolist(),'curve':curve})
  row['two_tangent_curves']=curves
 rows.append(row)
rel=[r for r in rows if r['class'].startswith('backed')];corn=[r for r in rows if not r['class'].startswith('backed')]
report={'stl_sha256':j['stl_sha256'],'short_samples':len(rows),'backed_relief_samples':len(rel),'finite_corner_samples':len(corn),'minimum_relief_backing_first_exit_mm':min(r['backing_first_exit_mm'] for r in rel),'corners_recover_0p8_within_0p4_count':sum(any(any(q['offset_mm']<=.4 and q['first_solid_mm'] is not None and q['first_solid_mm']>=.8 for q in c['curve']) for c in r['two_tangent_curves']) for r in corn),'samples':rows,'limitations':'Short first intervals retained, not replaced. Backing direction is distinct from original normal. Tangent curves on original plane require nearest hit at original surface. Not a global minimum-wall guarantee; independent review required.'}
with gzip.open(O/'short-section-check.json.gz','wt',encoding='utf-8') as f:json.dump(report,f,separators=(',',':'))
print({k:v for k,v in report.items() if k!='samples'})
