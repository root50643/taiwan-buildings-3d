"""Original polygon warning locations, original STL face-normal edge chords and vertical roots."""
from pathlib import Path
import numpy as np,trimesh,json,gzip,hashlib
from shapely import wkt
from shapely.geometry import Point
O=Path(__file__).parent;m=trimesh.load(O/'model.stl',process=False);T=m.triangles
def ray(o,d):
 o=np.array(o);d=np.array(d);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];p=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,p);good=abs(det)>1e-10;inv=np.zeros(len(T));inv[good]=1/det[good];s=o-T[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;t=np.einsum('ij,ij->i',e2,q)*inv;hs=sorted(set(round(float(x),7) for x in t[good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)]));return [x for j,x in enumerate(hs) if j==0 or x-hs[j-1]>1e-6]
j=json.load(gzip.open(O/'feature-loss-locations.json.gz','rt'));rows=[]
for r in j['high_loss_components']:
 p=wkt.loads(r['original_polygon_wkt']);z=r['z_mm'];q=p.simplify(1e-6,preserve_topology=True);edges=[]
 for ring in [q.exterior,*q.interiors]:
  cs=list(ring.coords)
  for a,b in zip(cs[:-1],cs[1:]):
   a=np.array(a);b=np.array(b);v=b-a;mid=(a+b)/2;n=np.array([v[1],-v[0]])/np.linalg.norm(v)
   if not p.contains(Point(mid-n*.0001)):n=-n
   origin=[*(mid+n*.0001),z];direction=[*(-n),0];h=ray(origin,direction);edges.append({'origin_mm':origin,'inward_xy_normal':direction,'hits_mm':h[:4],'first_solid_mm':h[1]-h[0] if len(h)>=2 else None})
 xy=list(p.representative_point().coords)[0];down=ray([*xy,z],[0,0,-1]);up=ray([*xy,z],[0,0,1]);role='south west sloped parapet' if z<20 else ('roof grid backed cell' if p.area<3 else 'roof grid outer ring')
 rows.append({'role':role,'z_mm':z,'original_component_index':r['original_component_index'],'original_polygon_wkt':r['original_polygon_wkt'],'opening_loss_fraction':r['opening_loss_fraction'],'true_corner_outside_loss_mm2':r['loss_outside_true_corner_mask_0p41_mm2'],'edge_normal_probes':edges,'vertical_root_point_mm':[*xy,z],'down_hits_mm':down,'up_hits_mm':up,'first_down_exit_z_mm':z-down[0] if down else None})
report={'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest(),'sample_count':len(rows),'samples':rows,'minimum_sampled_edge_first_chord_mm':min(e['first_solid_mm'] for r in rows for e in r['edge_normal_probes'] if e['first_solid_mm'] is not None),'limitations':'47 cross-layer warning samples, not47 physical columns. Actual original WKT and original STL chords. XY edge normals do not replace sloped-face normals; dense original face controls are separate. Exceptions pending independent review; not a global minimum-wall or print guarantee.'}
(O/'feature-root-check.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='samples'})
