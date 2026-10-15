"""Dense nominated-family rays against original STL triangles, never a proxy.
First solid chord from exterior avoids summing separated walls. Local probes only.
"""
from pathlib import Path
import numpy as np,trimesh,json,hashlib,math
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles;S=1.8;B=3.;e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0]
def hits(o,d):
 o=np.array(o,float);d=np.array(d,float);d/=np.linalg.norm(d);q=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,q);ok=abs(det)>1e-10;inv=np.zeros(len(T));inv[ok]=1/det[ok];s=o-T[:,0];u=np.einsum('ij,ij->i',s,q)*inv;r=np.cross(s,e1);v=r@d*inv;t=np.einsum('ij,ij->i',e2,r)*inv;t=np.sort(t[ok&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)]);return t[np.r_[True,np.diff(t)>1e-5]] if len(t) else t

j=json.loads((R/'detailed-component-check.json').read_text());warnings=[v for v in j['original_component_checks'] if v['opening_loss_fraction']>.01];rows=[]
for v in warnings:
 p=np.array([*v['centroid_xy'],v['z_mm']]);rc=np.array(v['rotated_rectangle_coords']);edges=np.diff(rc,axis=0);d2=edges[np.argmin(np.linalg.norm(edges,axis=1))];d=np.array([*d2,0.]);d/=np.linalg.norm(d)
 a=hits(p,d);b=hits(p,-d);assert len(a)%2==1 and len(b)%2==1,('not_inside',v)
 origin=p-d*(b[0]+.0001);h=hits(origin,d);w=float(h[1]-h[0]);assert w>=1.7,('caliper',v,w)
 down=hits(p,[0,0,-1]);assert len(down)%2==1;root=float(down[0]);landing=float(p[2]-root)
 header=(abs(p[0])<12*S and -31.5*S<p[1]<-23.8*S)
 assert abs(landing-(B+6.7*S if header else 0))<.01,('root_landing',v,root,landing)
 rows.append(dict(v,family=('entry_portico_columns' if p[1]<-60 else ('south_arc_piers_to_entry_lintel' if header else 'south_arc_piers_to_base')) if p[1]<0 else 'north_arc_screen_piers',original_face_caliper_mm=w,caliper_origin_mm=origin.tolist(),caliper_direction=d.tolist(),solid_down_to_verified_landing_mm=root,landing_z_mm=landing,landing_kind='entry_lintel' if header else 'base'))
r={'passed':True,'checks':{'all_warning_centroids_inside_original_solid':True,'all_warning_local_calipers_at_least_1p7mm':True,'all_warning_piers_or_columns_roots_to_base_or_entry_lintel':True},'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'warning_count':len(rows),'minimum_local_caliper_mm':min(v['original_face_caliper_mm'] for v in rows),'maximum_loss_fraction':max(v['opening_loss_fraction'] for v in rows),'maximum_outside_vertex_loss_mm2':max(v['loss_outside_0p41_vertex_mm2'] for v in rows),'samples':rows,'limits':'All >1% original Polygon samples. Original face ray along short rotated rectangle axis at centroid is a local caliper, not a global wall bound. Outside0.41 vertex-neighborhood loss is retained even nonzero. Exception approval requires independent/root review.'}
(R/'warning-caliper-check.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items() if k!='samples'})
