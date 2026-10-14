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
checks={};probes={};columns=[]
def mm(x,y,z):return [x*1.5,y*1.5,z*1.5+3]
for name,x,y,z,r,h in [('lower1',-17,-1.1,1.1,.85,7.8),('lower2',-17,14,1.1,.85,7.8),('upper',-12.8,-.6,19.1,.8,10.3)]:
 o=mm(x,y,z+h*.5);sx=span(o,0);sy=span(o,1);lo,hi=roots(o)
 assert min(sx,sy)>2*r*1.5-.001,(name,sx,sy)
 assert lo<3+1.5*z and hi>3+1.5*(z+h),(name,lo,hi)
 columns.append({'feature':name,'origin_mm':o,'normal_x_mm':sx,'normal_y_mm':sy,'down_root_z_mm':lo,'up_root_z_mm':hi})
checks['three_round_supports_actual_normals_and_roots']=True
for name,o in [('lower_portal',[-80,0,10]),('upper_portal',[-80,-9,36])]:
 a=ray(o,[1,0,0]);assert a and a[0]>95,(name,a)
 probes[name]={'origin_mm':o,'east_hits_mm':a,'first_solid_x_mm':o[0]+a[0]}
checks['west_opening_is_true_open_to_back_not_a_facade_plane']=True
# Main court has real air below an opaque print surrogate for the glass cover.
o=mm(3,-2,26);up=ray(o,[0,0,1]);down=ray(o,[0,0,-1]);assert up and 5<up[0]<7 and down[0]>35
probes['main_glass_air']={'origin_mm':o,'up_hits_mm':up,'down_hits_mm':down}
# Pick actual recessed cell centres at each glass cover: slab thickness measured in raw STL.
backs=[]
for name,x,y,z,w,d in [('main',3.2,-2.6,30.1,15.6,29.2),('extension',23.2,-39.7,11.3,16,13.2)]:
 for a in [x-w/2+.55,x-w/2+2.35]:
  b=y-d/2+.55;o=mm(a,b,z+.3);lo,hi=roots(o);thick=hi-lo
  assert thick>1.0198,(name,o,thick)
  backs.append({'feature':name,'origin_mm':o,'down_solid_z_mm':lo,'up_solid_z_mm':hi,'vertical_solid_mm':thick})
checks['two_glass_roof_recesses_have_real_solid_backing']=True
# Twelve rail runs retain wall root after windows; all roots added after local wall cuts.
rails=[]
for z in [5.4,9.5,13.6,17.7,21.8,25.9]:
 for y in [9.1,-14.3]:
  o=mm(5,y,z+1.1);sy=span(o,1);east=ray(o,[1,0,0]);lo,hi=roots(o)
  assert sy>1.2748 and east and east[0]>29,(o,sy,east)
  assert lo<o[2]-1.4,(o,lo)
  rails.append({'origin_mm':o,'normal_y_mm':sy,'east_connected_root_length_mm':east[0],'down_root_z_mm':lo,'up_surface_z_mm':hi})
checks['all12_gallery_rail_runs_have_back_wall_and_lower_slab_roots']=True
# Local recessed facade backing, measured between original parallel faces after the visible groove.
facades=[]
for name,o,axis,lower in [('suspended_west_glass',mm(-18.5,0,10),0,14),('east_tall_window_back',mm(25.0,14.5,4.2),0,19),('south_grouped_window_back',mm(10,-25.0,13.2),1,10),('low_east_glass_back',mm(41.6,-40,3),0,18),('entry_small_glass_back',mm(-16.2,-15.9,2),0,8)]:
 width=span(o,axis);assert width>lower,(name,width)
 facades.append({'feature':name,'inside_origin_mm':o,'axis':axis,'original_surface_solid_span_mm':width})
checks['five_backed_facade_recesses_have_original_face_solid_depth']=True
# All six high-loss original section samples are complete rectangles, with original-face roots.
loss=json.loads((R/'feature-loss-locations.json').read_text());corners=[]
for row in loss['high_loss_components']:
 assert abs(row['bbox_area_mm2']-row['original_area_mm2'])<1e-5
 assert row['loss_outside_0p41_vertex_mm2']<1e-10
 x1,y1,x2,y2=row['bounds'];o=[(x1+x2)/2,(y1+y2)/2,row['z_mm']]
 sx=span(o,0);sy=span(o,1);lo,hi=roots(o)
 assert min(sx,sy)>1.2748 and lo<.0001 and hi>o[2]
 corners.append({'origin_mm':o,'normal_x_mm':sx,'normal_y_mm':sy,'down_root_z_mm':lo,'up_surface_z_mm':hi,'loss_fraction':row['opening_loss_fraction'],'loss_outside_original_vertex0p41_mm2':row['loss_outside_0p41_vertex_mm2'],'physical_feature':'top_entry_stair_tread' if row['z_mm']<20 else 'east_projecting_blade_tip'})
checks['six_specific_corner_samples_have_actual_normals_and_base_roots']=True
report={'passed':all(checks.values()),'checks':checks,'round_supports':columns,'portal_probes':probes,'glass_backing':backs,'gallery_roots':rails,'specific_corner_samples':corners,'facade_backing':facades,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'method':'Moller-Trumbore intersections on unprocessed original STL faces; no repair. Specific probes, not a global minimum-wall certificate. Not physically printed.'}
(R/'architectural-ray-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
