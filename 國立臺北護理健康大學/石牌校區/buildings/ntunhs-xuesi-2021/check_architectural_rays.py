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
checks={};probes={}
def cast(name,o,d):
 vals=ray(o,d);assert vals,name;probes[name]={'origin_mm':o,'direction':d,'distances_mm':vals};return vals
# Court open from sky to 3F roof / 4F floor; it does not penetrate the low podium.
h=cast('court_vertical',(12.7,0,120),(0,0,-1));checks['court_bottom_at_27p2mm']=abs(120-h[0]-27.2)<1e-4
xp=cast('court_east_wall',(12.7,0,40),(1,0,0));xm=cast('court_west_wall',(12.7,0,40),(-1,0,0))
yp=cast('court_north_wall',(12.7,0,40),(0,1,0));ym=cast('court_south_wall',(12.7,0,40),(0,-1,0))
checks['actual_court_clear_width_31p5']=abs(xp[0]+xm[0]-31.5)<1e-4
checks['actual_court_clear_depth_16p4']=abs(yp[0]+ym[0]-16.4)<1e-4
# Short-side open recesses at classroom and upper levels.
h=cast('west_recess_open',(-90,0,38),(1,0,0));checks['west_recess_reaches_back_wall']=abs(-90+h[0]+51)<1e-4
h=cast('east_lower_recess_open',(90,0,38),(-1,0,0));checks['east_lower_recess_reaches_back_wall']=abs(90-h[0]-59)<1e-4
h=cast('east_upper_recess_open',(90,0,70),(-1,0,0));checks['east_upper_recess_deeper_than_lower']=abs(90-h[0]-51)<1e-4
h=cast('west_behind_grille_vertical',(-60,0,80),(0,0,-1));checks['west_grille_cavity_connects_to_lower_recess']=abs(80-h[0]-11.6)<1e-4
h=cast('east_recess_vertical',(64,0,80),(0,0,-1));checks['east_recess_open_to_ground_roof']=abs(80-h[0]-11.6)<1e-4
# A deep west conference roof covers its end; no false open conference hall.
h=cast('conference_roof',(-48,20,120),(0,0,-1));checks['west_conference_roof_above_main_roof']=abs(120-h[0]-89)<1e-4
# Grille grooves all intersect exterior, retaining >=1.2 mm backing normal to face.
widths=[]
for z in [66,75,84]:
 for y in np.arange(-7,7.1,2.3):
  hits=ray((-90,float(y),z),(1,0,0));width=hits[1]-hits[0];assert width>=1.1999
  widths.append({'y_mm':float(y),'z_mm':z,'actual_normal_mm':width,'entry_x_mm':-90+hits[0]})
checks['west_grille_no_sealed_sub0p8_skin']=True;probes['grille_normal_spans']=widths
# Depths and backed roots of actual narrow windows and broad south mullions.
h=cast('north_small_window_recess',(-60.85,70,38),(0,-1,0));checks['north_actual_recess_half_mm']=abs(70-h[0]-31.9)<1e-4
h=cast('north_interwindow_root',(-62,70,38),(0,-1,0));checks['north_narrow_interwindow_strip_has_deep_backing']=h[1]-h[0]>20
h=cast('south_classroom_recess',(-60,-70,38),(0,1,0));checks['south_actual_recess_half_mm']=abs(-70+h[0]+31.9)<1e-4
h=cast('south_glass_mullion_root',(-58,-70,38),(0,1,0));checks['south_mullion_contiguous_to_backing']=h[1]-h[0]>20
# Verify every >1% section independently: 22 low columns, not 890 pillars.
loss=json.loads((R/'feature-loss-locations.json').read_text());rows=[];centres=set()
for c in loss['high_loss_components']:
 x1,y1,x2,y2=c['bounds'];o=[(x1+x2)/2,(y1+y2)/2,c['z_mm']]
 assert c['z_mm']<11.5 and c['loss_outside_bbox_corners_0p41_mm2']<1e-7
 assert abs((x2-x1)*(y2-y1)-c['original_area_mm2'])<1e-5
 xx=ray(o,[1,0,0])[0]+ray(o,[-1,0,0])[0];yy=ray(o,[0,1,0])[0]+ray(o,[0,-1,0])[0]
 down=o[2]-ray(o,[0,0,-1])[0];up=o[2]+ray(o,[0,0,1])[0]
 assert min(xx,yy)>2.5999 and abs(down)<1e-4 and up>=11.5
 centres.add(tuple(round(v,3) for v in o[:2]));rows.append({'z_mm':o[2],'xy_mm':o[:2],'actual_normal_x_mm':xx,'actual_normal_y_mm':yy,'root_bottom_z_mm':down,'root_top_z_mm':up,'loss_fraction':c['opening_loss_fraction'],'loss_outside_bbox_corners_0p41_mm2':c['loss_outside_bbox_corners_0p41_mm2']})
assert len(centres)==22 and len(rows)==890
checks['all_890_column_samples_have_2p6mm_normal_and_base_upper_root']=True
checks['all_high_losses_only_22_rectangular_column_corners']=True
report={'passed':all(checks.values()),'checks':checks,'probes':probes,'column_corner_sample_count':len(rows),'physical_column_count':len(centres),'column_samples':rows,'maximum_component_loss_fraction':max(r['loss_fraction'] for r in rows),'stl_sha256':__import__('hashlib').sha256((R/'model.stl').read_bytes()).hexdigest(),'limitations':'Raw STL normal-direction and root checks plus component corner localization, not exhaustive global thickness or physical print. The specific 22-column corner-loss exception is accepted subject to independent reproduction.'}
(R/'architectural-ray-check.json').write_text(json.dumps(report,indent=2));print(checks);assert report['passed']
