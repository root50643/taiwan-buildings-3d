from pathlib import Path
import json,numpy as np,trimesh,hashlib
from shapely import wkt
from shapely.geometry import Point
O=Path(__file__).parent;W=O;m=trimesh.load(W/'model.stl',process=False);T=m.triangles
def ray(o,d):
 o=np.array(o,float);d=np.array(d,float);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];p=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,p);good=abs(det)>1e-10;inv=np.zeros(len(T));inv[good]=1/det[good];s=o-T[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;t=np.einsum('ij,ij->i',e2,q)*inv;return sorted(set(round(float(x),7) for x in t[good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)]))

d=json.loads((W/'original-sections.json').read_text());rows=[]
for c in d['original_component_checks']:
 if c['z_mm']<2.4 or c['z_mm']>14:continue
 p=wkt.loads(c['original_polygon_wkt']).simplify(1e-5,preserve_topology=True)
 for ring in [p.exterior,*p.interiors]:
  cc=np.array(ring.coords)
  for a,b in zip(cc,cc[1:]):
   v=b-a;length=np.linalg.norm(v)
   if length<.5:continue
   mid=(a+b)/2
   if not (20<=mid[0]<=48 and -31<=mid[1]<=-11):continue
   n=np.array([-v[1],v[0]])/length;pt=mid+n*.01
   if not p.contains(Point(pt)):n=-n;pt=mid+n*.01
   if not p.contains(Point(pt)):continue
   o=np.array([*pt,c['z_mm']]);direction=np.array([-n[0],-n[1],0]);h=ray(o,direction);assert h
   hit=o+direction*h[0];near=trimesh.triangles.closest_point(T,np.repeat(hit[None,:],len(T),axis=0));ix=np.argmin(np.linalg.norm(near-hit,axis=1));assert np.linalg.norm(near[ix]-hit)<1e-5;normal=np.cross(T[ix,1]-T[ix,0],T[ix,2]-T[ix,0]);normal/=np.linalg.norm(normal);hh=ray(hit+normal*.001,-normal);assert len(hh)>=2
   rows.append({'z':c['z_mm'],'origin':o.tolist(),'edge_length_mm':length,'original_triangle_index':int(ix),'actual_surface_point_mm':hit.tolist(),'outward_probe_direction':direction.tolist(),'actual_normal_mm':hh[1]-hh[0],'normal':normal.tolist(),'down_z':o[2]-ray(o,[0,0,-1])[0]})
r={'passed':all(x['actual_normal_mm']>=.8 for x in rows),'samples':rows,'count':len(rows),'min_normal_mm':min(x['actual_normal_mm'] for x in rows),'limits':'Nominated white-band actual face normals at every simplified section edge >=0.5mm; no global wall claim.'};r['stl_sha256']=hashlib.sha256((W/'model.stl').read_bytes()).hexdigest();r['checks']={'all_white_ROI_original_face_chords_ge_reference_0p8mm':r['passed']};r['scope']='All original section polygons at z2.4..14; midpoint ROI x20..48/y-31..-11; simplified1e-5 edge>=0.5mm. No loss-percentage filter, no mesh repair, not global minimum wall.'
(O/'white-roi-rays.json').write_text(json.dumps(r,indent=2));print('done',r['passed'],r['count'],r['min_normal_mm']);print(sorted(rows,key=lambda x:x['actual_normal_mm'])[:4])

assert r['passed'], 'White-band original-face chord below 0.8mm reference'
