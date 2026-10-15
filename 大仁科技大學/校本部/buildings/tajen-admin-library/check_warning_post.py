"""Source-defined support axes and real first-hit surfaces; never skip air intervals."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles;E1=T[:,1]-T[:,0];E2=T[:,2]-T[:,0];S=150/62;BASE=2

def hits(o,d):
 q=np.cross(d,E2);det=np.einsum('ij,ij->i',E1,q);ok=abs(det)>1e-13;iv=np.zeros(len(T));iv[ok]=1/det[ok];ss=o-T[:,0];u=np.einsum('ij,ij->i',ss,q)*iv;r=np.cross(ss,E1);v=r@d*iv;t=np.einsum('ij,ij->i',E2,r)*iv;ix=np.flatnonzero(ok&(u>=-1e-12)&(v>=-1e-12)&(u+v<=1+1e-12)&(t>1e-9));ix=ix[np.argsort(t[ix])];keep=[]
 for i in ix:
  if not keep or t[i]-t[keep[-1]]>1e-7:keep.append(i)
 return [{'face':int(i),'distance_mm':float(t[i]),'point_mm':(o+d*t[i]).tolist()} for i in keep]
rows=[]
a=json.loads((R/'detailed-component-check.json').read_text())['original_component_checks'];warnings=[r for r in a if r['opening_loss_fraction']>.01]
for r in warnings:
 x,y=r['centroid_xy'];z=r['z_mm'];b=r['bounds'];assert -46<b[0]<-44 and -58<b[1]<-56
 hx=hits(np.array([b[2]+1,y,z]),np.array([-1.,0,0]));hy=hits(np.array([x,b[1]-1,z]),np.array([0.,1.,0]));hz=hits(np.array([x,y,100.]),np.array([0.,0.,-1.]));wx=hx[1]['distance_mm']-hx[0]['distance_mm'];wy=hy[1]['distance_mm']-hy[0]['distance_mm'];ok=abs(wx-(b[2]-b[0]))<1e-5 and abs(wy-(b[3]-b[1]))<1e-5 and hz[1]['point_mm'][2]<1e-6
 rows.append({'original_component':r,'x_normal_hits':hx,'y_normal_hits':hy,'downward_actual_top_surface_root_hits':hz,'original_x_normal_thickness_mm':wx,'original_y_normal_thickness_mm':wy,'top_to_ground_continuous_solid_mm':hz[1]['distance_mm']-hz[0]['distance_mm'],'passed':bool(ok)})
j={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'passed':all(x['passed'] for x in rows),'checks':{'all_warning_post_normal_calipers_and_ground_roots_pass':all(x['passed'] for x in rows)},'family':'southwest vertical end trim above terrace; not a window mullion','warning_count':len(rows),'minimum_original_normal_caliper_mm':min(min(x['original_x_normal_thickness_mm'],x['original_y_normal_thickness_mm']) for x in rows),'maximum_opening_loss_fraction':max(x['original_component']['opening_loss_fraction'] for x in rows),'maximum_loss_outside_0p41_rectangle_corners_mm2':max(x['original_component']['loss_outside_0p41_rectangle_corner_mm2'] for x in rows),'rows':rows,'limits':'Exception NOT approved by author. Opening loss includes nonzero corner-exterior numeric remnants, not claimed purely four corners. Rectangle caliper and nominated ground path are local measures, not global wall thickness.'};(R/'warning-post-check.json').write_text(json.dumps(j,indent=2));print({k:v for k,v in j.items() if k not in ['rows','limits']});assert j['passed']
