from pathlib import Path
import numpy as np,json,hashlib,trimesh
W=Path(__file__).resolve().parent;T=trimesh.load(W/'model.stl',process=False).triangles
def ray(o,d):
 o=np.array(o,float);d=np.array(d,float);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];p=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,p);good=abs(det)>1e-10;inv=np.zeros(len(T));inv[good]=1/det[good];s=o-T[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;t=np.einsum('ij,ij->i',e2,q)*inv;return sorted(set(round(float(x),7) for x in t[good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)]))
d=json.loads((W/'detailed-component-check.json').read_text());rows=[]
for c in d['original_component_checks']:
 if c['opening_loss_fraction']<=.01:continue
 x1,y1,x2,y2=c['bounds'];o=[(x1+x2)/2,(y1+y2)/2,c['z_mm']];xx=ray(o,[1,0,0])[0]+ray(o,[-1,0,0])[0];yy=ray(o,[0,1,0])[0]+ray(o,[0,-1,0])[0];assert xx>=1.59249 and yy>=1.59249;rows.append({'z_mm':c['z_mm'],'component':c['original_component_index'],'bounds':c['bounds'],'x_normal_mm':xx,'y_normal_mm':yy,'area_matches_rectangle':abs((x2-x1)*(y2-y1)-c['original_area_mm2'])<1e-7,'retained_fraction':c['retained_fraction'],'loss_outside_0p41_vertex_fraction':c['loss_outside_0p41_vertex_mm2']/c['original_area_mm2']})
roots=[]
for x in [-.5,0,.5]:
 hit=ray([x,0,78],[0,0,-1]);assert hit;exit_z=78-hit[0];assert exit_z<70.7;roots.append({'x':x,'first_down_exit_z':exit_z})
pillar_roots=[]
for x in [-55.055,55.055]:
 for y in [-45.955,45.955]:
  down=ray([x,y,15],[0,0,-1])[0];up=ray([x,y,15],[0,0,1])[0];assert abs(15-down)<1e-6 and 15+up>23;pillar_roots.append({'xy':[x,y],'down_exit_z':15-down,'up_exit_z':15+up})
assert all(x['area_matches_rectangle'] for x in rows)
r={'pillar_root_rays':pillar_roots,'passed':True,'stl_sha256':hashlib.sha256((W/'model.stl').read_bytes()).hexdigest(),'warning_component_samples':len(rows),'normal_ray_samples':rows,'cross_root_rays':roots,'all_warning_components_rectangle_area':all(x['area_matches_rectangle'] for x in rows),'min_measured_axis_normal_mm':min(min(x['x_normal_mm'],x['y_normal_mm']) for x in rows),'max_outside_fraction':max(x['loss_outside_0p41_vertex_fraction'] for x in rows),'limits':'Specified axis-aligned warning sections and root probes only. Not an exhaustive global minimum-wall scan or physical print guarantee.'};(W/'local-caliper-root-check.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items() if not isinstance(v,list)})
