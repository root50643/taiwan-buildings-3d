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
S=150/94
mm=lambda x,y,z:[x*S,y*S,z*S+2]
checks={};columns=[];air=[];backs=[]
for x in [-5.7,5.7]:
 o=mm(x,.1,5);sx=span(o,0);sy=span(o,1);lo,hi=roots(o)
 assert min(sx,sy)>2.3933 and abs(lo)<1e-5 and hi>17.4
 columns.append({'origin_mm':o,'normal_x_mm':sx,'normal_y_mm':sy,'down_root_z_mm':lo,'up_root_z_mm':hi})
checks['two_entry_piers_original_normals_and_both_roots']=True
for x in [0,-7.2,7.2]:
 o=mm(x,-4,5);a=ray(o,[0,1,0]);assert a and 15<a[0]<17
 air.append({'feature':'entry_clear_to_recessed_back','origin_mm':o,'forward_hits_mm':a})
o=mm(0,0,5);left=ray(o,[-1,0,0]);right=ray(o,[1,0,0]);assert left[0]>7.8 and right[0]>7.8
checks['entry_has_true_deep_three_bay_open_porch']=True
for x in [-6.5,0,6.5]:
 o=mm(x,2,11.4);up=ray(o,[0,0,1]);down=ray(o,[0,0,-1]);assert not up and 1.7<down[0]<1.8
 air.append({'feature':'open_roof_garden','origin_mm':o,'up_hits_mm':up,'down_to_terrace_mm':down[0]})
checks['front_roof_garden_is_open_air_not_high_infill']=True
for x in [-25,-16,-8,0,8,16,25]:
 h=11.3+8.2*(x/29)**2;o=mm(x,0,h-.35);width=span(o,1);assert width>2.0742
 backs.append({'feature':'concave_front_screen','origin_mm':o,'normal_y_mm':width})
for sg in [-1,1]:
 o=mm(sg*28.45,4.5,16.5);width=span(o,0);back=ray(o,[0,1,0]);assert width>1.5955 and back[0]>35
 backs.append({'feature':'inward_return_backing','origin_mm':o,'normal_x_mm':width,'continuous_rear_root_length_mm':back[0]})
checks['screen_and_two_end_backings_have_actual_solid_widths_and_roots']=True
# All actual upper sloped-glass face centroids, directed inward along saved geometric normals.
normal=np.cross(e1,e2);normal/=np.linalg.norm(normal,axis=1)[:,None];centres=tri.mean(axis=1);rows=[]
for i,(c,n) in enumerate(zip(centres,normal)):
 x,y=(c[0]/S,c[1]/S-5);rr=np.hypot(x,y)
 if 1.0<rr<17.11 and y>-.00001 and c[2]>18 and .7<n[2]<.999 and abs(n[0])+abs(n[1])>.12:
  a=ray(c-n*1e-4,-n);assert a and a[0]>.8,(i,c,n,a)
  rows.append({'face_index':i,'centroid_mm':c.tolist(),'inward_normal':(-n).tolist(),'first_opposite_face_mm':a[0]+1e-4})
assert len(rows)>30
checks['actual_sloping_glass_faces_have_inward_solid_backing']=True
loss=json.loads((R/'feature-loss-locations.json').read_text());warn=[]
for row in loss['high_loss_components']:
 x1,y1,x2,y2=row['bounds'];o=[(x1+x2)/2,(y1+y2)/2,row['z_mm']];sx=span(o,0);sy=span(o,1);lo,hi=roots(o)
 assert min(sx,sy)>.8 and lo<o[2]-.2 and hi>o[2]
 warn.append({'origin_mm':o,'normal_x_mm':sx,'normal_y_mm':sy,'down_root_z_mm':lo,'up_surface_z_mm':hi,'loss_fraction':row['opening_loss_fraction'],'loss_outside_vertex0p41_mm2':row['loss_outside_0p41_vertex_mm2'],'bbox_area_minus_polygon_mm2':row['bbox_area_mm2']-row['original_area_mm2']})
checks['all_original_high_loss_samples_have_actual_width_and_vertical_roots']=True
report={'passed':all(checks.values()),'checks':checks,'entry_piers':columns,'air_probes':air,'screen_and_return_backing':backs,'sloped_glass_original_face_normals':rows,'minimum_sloped_face_normal_mm':min(x['first_opposite_face_mm'] for x in rows),'high_loss_samples':warn,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'method':'Unprocessed original triangle Moller-Trumbore rays; specified actual-face and axis normals, no repair; not a global wall certificate or physical print test.'}
(R/'architectural-ray-check.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k not in ['entry_piers','air_probes','screen_and_return_backing','sloped_glass_original_face_normals','high_loss_samples']})
