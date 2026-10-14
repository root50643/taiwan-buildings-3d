"""Local raw-STL normal probes of every >1% warning section component.
Paired directions from the minimum rotated rectangle are only local probes;
rotated-box width by itself is never accepted as a wall-thickness measurement.
"""
from pathlib import Path
import json,hashlib,math,numpy as np,trimesh
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles
zmin=T[:,:,2].min(axis=1);zmax=T[:,:,2].max(axis=1)
def ray(o,d):
 o=np.array(o,float);d=np.array(d,float);d/=np.linalg.norm(d);tt=T[(zmin<=o[2]+1e-7)&(zmax>=o[2]-1e-7)]
 e1=tt[:,1]-tt[:,0];e2=tt[:,2]-tt[:,0];p=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,p);good=abs(det)>1e-10;inv=np.zeros(len(tt));inv[good]=1/det[good];s=o-tt[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;t=np.einsum('ij,ij->i',e2,q)*inv
 hits=t[good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)];assert len(hits);return float(hits.min())
j=json.loads((R/'detailed-component-check.json').read_text());rows=[]
for c in j['original_component_checks']:
 if c['opening_loss_fraction']<=.01:continue
 o=c['centroid_xy']+[c['z_mm']];rect=np.array(c['rotated_rectangle_coords']);ws=[]
 for k in range(2):
  v=rect[k+1]-rect[k];d=np.array([-v[1],v[0],0.]);d/=np.linalg.norm(d);ws.append(ray(o,d)+ray(o,-d))
 assert min(ws)>=.8, (c['z_mm'],c['original_component_index'],ws)
 x,y=c['centroid_xy'];z=c['z_mm']
 if z<20 and y<-64 and abs(abs(x)-21.87)<.01:family='two_front_canopy_columns'
 elif 58<z<61 and -61<y<-58:family='front_arch_crowns_and_border_segments'
 elif z>65 and abs(x)<1 and abs(y)<1:family='truncated_skylight_apex'
 else:raise AssertionError(('unclassified warning component',z,x,y))
 rows.append({'feature_family':family,'z_mm':c['z_mm'],'component_index':c['original_component_index'],'origin_xy':c['centroid_xy'],'normal_widths_mm':ws,'convex_area_difference_mm2':c['convex_area_difference_mm2'],'opening_loss_fraction':c['opening_loss_fraction'],'loss_area_mm2':c['loss_area_mm2'],'loss_outside_0p41_vertex_mm2':c['loss_outside_0p41_vertex_mm2']})
report={'passed':True,'checks':{'every_warning_component_probed':len(rows)==sum(c['opening_loss_fraction']>.01 for c in j['original_component_checks']),'all_measured_normal_widths_at_least_0p8mm':True},'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'warning_component_samples':len(rows),'minimum_sampled_width_mm':min(min(x['normal_widths_mm']) for x in rows),'maximum_component_loss_fraction':max(x['opening_loss_fraction'] for x in rows),'maximum_outside_vertex_loss_mm2':max(x['loss_outside_0p41_vertex_mm2'] for x in rows),'family_sample_counts':{f:sum(x['feature_family']==f for x in rows) for f in sorted(set(x['feature_family'] for x in rows))},'samples':rows,'limits':'Two local centroid-normal directions per warning component; actual original STL intersections. Not all-direction global thickness, arbitrary-shape bounding-box proof, full support analysis or physical print validation.'}
(R/'warning-caliper-check.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='samples'})
