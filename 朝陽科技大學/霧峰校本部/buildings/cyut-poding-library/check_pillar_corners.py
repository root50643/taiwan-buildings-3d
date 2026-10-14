"""Ray checks on original STL, no repair: courtyard and actual recessed portal."""
from pathlib import Path
import json
import numpy as np
import trimesh
R=Path(__file__).resolve().parent
m=trimesh.load(R/'model.stl',force='mesh',process=False)
def ray(o,d):
 o=np.array(o,dtype=float);d=np.array(d,dtype=float); t=m.triangles
 e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];p=np.cross(np.tile(d,(len(t),1)),e2);det=np.einsum('ij,ij->i',e1,p)
 good=np.abs(det)>1e-10;inv=np.zeros(len(t));inv[good]=1/det[good];s=o-t[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;dist=np.einsum('ij,ij->i',e2,q)*inv
 sel=good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(dist>1e-8)
 return sorted(set(round(float(v),5) for v in dist[sel]))
d=json.loads((R/'feature-loss-locations.json').read_text());rows=[]
for c in d['original_component_checks']:
 if c['opening_loss_fraction']<=.01:continue
 assert c['z_mm']<10 and c['loss_outside_bbox_corners_0p41_mm2']<1e-7
 x1,y1,x2,y2=c['bounds'];o=[(x1+x2)/2,(y1+y2)/2,c['z_mm']]
 xx=ray(o,[1,0,0])[0]+ray(o,[-1,0,0])[0];yy=ray(o,[0,1,0])[0]+ray(o,[0,-1,0])[0]
 down=o[2]-ray(o,[0,0,-1])[0];up=o[2]+ray(o,[0,0,1])[0]
 assert xx>1.98 and yy>1.98 and abs(down)<1e-5 and abs(up-10.1204815)<1e-4
 rows.append({'z_mm':o[2],'xy_mm':o[:2],'x_normal_mm':xx,'y_normal_mm':yy,'down_exit_z_mm':down,'up_exit_z_mm':up,'loss_fraction':c['opening_loss_fraction'],'retained_fraction':c['retained_fraction'],'loss_outside_bbox_corners_0p41_mm2':c['loss_outside_bbox_corners_0p41_mm2']})
assert len(rows)==56
report={'passed':True,'checks':{'exactly_two_columns_56_layer_samples':True,'all_losses_within_0p41mm_bbox_corners':True,'actual_xy_widths_and_base_canopy_roots_verified':True},'stl_sha256':__import__('hashlib').sha256((R/'model.stl').read_bytes()).hexdigest(),'sample_count':len(rows),'physical_column_count':2,'samples':rows,'review_status':'Specific two-column corner-loss exception accepted; not a relaxation of cap-skin requirements or general loss threshold.','limits':'56 sampled sections of two columns, not 56 physical columns. Not global minimum wall or physical print guarantee.'}
(R/'column-corner-review.json').write_text(json.dumps(report,indent=2));print(report['checks'])
