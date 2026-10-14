"""Original-STL rays: gable back, RC/gable segmentation, rose roots and localized corner losses; no repair."""
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
checks={};probes={}
def cast(name,o,d):
 vals=ray(o,d);assert vals,name;probes[name]={'origin_mm':o,'direction':d,'distances_mm':vals};return vals
# The west gable failed erosion until its backing was added inward by1.3mm.
# Probe original STL normals at ALL three real recesses and the inter-arch roots.
gable=[]
for y,top in [(-2.4,55.3),(0,56.6),(2.4,55.3)]:
 for z in np.arange(51.071,top-.3,.2):
  hits=ray([-80,y,float(z)],[1,0,0]);assert len(hits)>=2
  span=hits[1]-hits[0];assert span>1.6998
  gable.append({'y_mm':y,'z_mm':float(z),'entry_x_mm':-80+hits[0],'actual_normal_mm':span})
checks['all_west_three_arch_sampled_backs_at_least1p7mm']=True
for y in [-1.2,1.2]:
 h=cast('west_interarch_'+str(y),[-80,y,52],[1,0,0]);assert h[1]-h[0]>=3.0998
checks['west_interarch_back_roots3p1mm']=True
# Original sharp apex would disappear at61.071: local0.4mm truncation only.
h=cast('gable_flat_ridge_top',[-57.7,0,90],[0,0,-1]);assert abs(90-h[0]-60.8)<.0001
ridge_z=60.79;o=[-57.7,0,ridge_z]
w=ray(o,[0,1,0])[0]+ray(o,[0,-1,0])[0];t=ray(o,[1,0,0])[0]+ray(o,[-1,0,0])[0]
down=ray(o,[0,0,-1])[0];assert w>1.44 and t>3.0998 and down>50
checks['gable_local_flat_ridge_has_root_width_and_thickness']=True
# Upper bell window recesses remain outside-open with broad solid backs.
bells=[]
for y,sgn in [(14.5,1),(31.5,-1)]:
 for x in [53.2,58.5,63.8]:
  for z in [63,68,73]:
   o=[x,y-sgn*10,z];d=[0,sgn,0];h=ray(o,d);assert abs(h[0]-10.35)<.0001 and h[1]-h[0]>15
   bells.append({'origin':o,'direction':d,'recess_mm':h[0]-10,'solid_back_mm':h[1]-h[0]})
checks['bell_recesses_shallow_and_externally_open']=True
# West RC vestibule is genuinely a separate flat roof, behind the raised front.
h=cast('west_RC_plateau',[-47,0,100],[0,0,-1]);assert abs(100-h[0]-46.3)<.0001
h=cast('rear_nave_ridge',[0,0,100],[0,0,-1]);assert abs(100-h[0]-60.8)<.0001
checks['west_RC_flat_and_rear_gable_are_distinct']=True
# Rose and fine mullions root inward into backing, not disconnected tracery.
for name,o,d in [('rose_ring',[-80,0,39.5],[1,0,0]),('rose_petal',[-80,0,44.3],[1,0,0]),('west_window_mullion',[-80,13.7,14],[1,0,0]),('south_window_mullion',[-20.5,-50,15],[0,1,0])]:
 h=cast(name,o,d);assert len(h)>=2 and h[1]-h[0]>10
checks['sampled_rose_and_window_frames_have_contiguous_deep_backing']=True
# Portal arch clears the projecting porch; doorway remains wall-backed.
for y,sgn in [(-20.25,1),(20.25,-1)]:
 h=cast('porch_axis_'+str(y),[4.5,y-sgn*15,12],[0,sgn,0]);assert h[0]>12
checks['side_porch_open_recesses_are_real_geometry']=True
# Localize every over1% original Polygon: only rectangular gable crest slices
# and twelve widened tower-cap tips. No threshold change or skin exception.
loss=json.loads((R/'feature-loss-locations.json').read_text());corner_rows=[];roof_centres=set();crest_count=0
for row in loss['high_loss_components']:
 x1,y1,x2,y2=row['bounds'];o=[(x1+x2)/2,(y1+y2)/2,row['z_mm']]
 assert abs((x2-x1)*(y2-y1)-row['original_area_mm2'])<1e-5
 assert row['loss_outside_bbox_corners_0p41_mm2']<1e-7
 xx=ray(o,[1,0,0])[0]+ray(o,[-1,0,0])[0];yy=ray(o,[0,1,0])[0]+ray(o,[0,-1,0])[0]
 downz=o[2]-ray(o,[0,0,-1])[0];upz=o[2]+ray(o,[0,0,1])[0]
 if x1<0:
  assert xx>3.0998 and yy>1.9143 and abs(upz-60.8)<.0001 and abs(downz)<.0001
  feature='western_gable_crest';crest_count+=1
 else:
  assert min(xx,yy)>2.3998 and abs(upz-81.8)<.0001 and abs(downz)<.0001
  feature='tower_cap_pier';roof_centres.add(tuple(round(t,4) for t in o[:2]))
 corner_rows.append({'feature':feature,'origin_mm':o,'normal_x_mm':xx,'normal_y_mm':yy,'bottom_root_z_mm':downz,'top_z_mm':upz,'loss_fraction':row['opening_loss_fraction'],'loss_outside_corners_0p41_mm2':row['loss_outside_bbox_corners_0p41_mm2']})
assert crest_count==4 and len(roof_centres)==12 and len(corner_rows)==52
checks['all52_high_loss_samples_only_rooted_rectangular_corner_loss']=True
captri=m.triangles[(m.triangles[:,:,0].max(axis=1)<-55)&(np.abs(m.triangles[:,:,2]-60.8).max(axis=1)<.0001)];assert len(captri)>0
actual_cap_width=float(captri[:,:,1].max()-captri[:,:,1].min());assert actual_cap_width>1.4475
report={'passed':all(checks.values()),'checks':checks,'probes':probes,'gable_arch_normal_samples':gable,'gable_ridge':{'z_mm':60.8,'local_truncation_mm':.4,'actual_top_plane_width_mm':actual_cap_width,'sample_z_mm':ridge_z,'normal_x_mm':t,'width_y_mm':w,'uninterrupted_down_root_mm':down},'bell_samples':bells,'specific_corner_exception':{'gable_crest_samples':crest_count,'tower_cap_piers':len(roof_centres),'tower_cap_samples':len(corner_rows)-crest_count,'total_samples':len(corner_rows),'samples':corner_rows,'maximum_loss_fraction':max(r['loss_fraction'] for r in corner_rows)},'stl_sha256':__import__('hashlib').sha256((R/'model.stl').read_bytes()).hexdigest(),'limitations':'Selected actual original-STL normal/root rays; not an exhaustive global wall test or physical print.'}
(R/'architectural-ray-check.json').write_text(json.dumps(report,indent=2));print(checks);assert report['passed']
