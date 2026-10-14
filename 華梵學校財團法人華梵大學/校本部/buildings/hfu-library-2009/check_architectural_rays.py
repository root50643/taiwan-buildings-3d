"""Original unprocessed STL rays for open pavilions, porch, rail backing and loss components. No repair."""
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
# 77 physical square-column segments:18 south,9 north,10 east upper,40 pavilions.
registry=[]
for z in [3.8,7.6]:
 for x in [-16,-11.75,-7.5,-3.25,1,5.25,9.5,13.75,18]:registry.append(('south_corridor',x,-29.9,z,3.6))
for x in [-20,-15,-10,-5,0,5,10,15,20]:registry.append(('north_entry',x,34,15.5,3.6))
for y in [-12.4,-8.55,-4.7,-.85,3]:
 for x in [24.5,31]:registry.append(('east_upper',x,y,14.8,3.5))
for x,y,w,d,z in [(-20,11,13.5,9.5,19.2),(21,12,13.5,9.5,19.2),(-22,-22,8.5,11,15.2),(26,-22,8.5,11,15.2)]:
 xs=[x-w/2+1.1,x-w/6,x+w/6,x+w/2-1.1];ys=[y-d/2+1.1,y,y+d/2-1.1]
 for a,b in sorted({(a,b) for a in xs for b in [ys[0],ys[-1]]}|{(a,b) for a in [xs[0],xs[-1]] for b in ys}):registry.append(('open_pavilion',a,b,z-.1,4.75))
assert len(registry)==77
for name,x,y,z,h in registry:
 o=[2*x,2*y,3+2*(z+h*.50)];sx=span(o,0);sy=span(o,1);lo,hi=roots(o)
 assert min(sx,sy)>2.0998,(name,o,sx,sy)
 assert lo<3+2*z+.0001 and hi>3+2*(z+h)-.0001,(name,o,lo,hi)
 columns.append({'feature':name,'centre_probe_mm':o,'normal_x_mm':sx,'normal_y_mm':sy,'downward_connected_solid_to_z_mm':lo,'upward_connected_solid_to_z_mm':hi,'source_column_bottom_mm':3+2*z,'source_column_top_mm':3+2*(z+h)})
checks['all77_square_column_segments_have_actual2p1mm_normals_and_both_roots']=True
# Two tall round columns: min diameter on raw polygon normals slightly under nominal3.28.
rounds=[]
for y in [-10.5,1.1]:
 o=[60,2*y,18];sx=span(o,0);sy=span(o,1);lo,hi=roots(o);assert min(sx,sy)>3.2798 and lo<10.7 and hi>31
 rounds.append({'origin_mm':o,'normal_x_mm':sx,'normal_y_mm':sy,'down_root_z_mm':lo,'up_root_z_mm':hi})
checks['two_high_round_columns_have_actual3p28mm_and_roots']=True
# Clear internal air rays: no artificial glazing plane across any pavilion.
open_air=[]
for x,y,w,d,z in [(-20,11,13.5,9.5,19.2),(21,12,13.5,9.5,19.2),(-22,-22,8.5,11,15.2),(26,-22,8.5,11,15.2)]:
 # local centre y is clear between the north/south column lines
 o=[2*x,2*y,3+2*(z+2)];a=ray(o,[0,1,0]);b=ray(o,[0,-1,0]);assert (not a or a[0]>d-1) and (not b or b[0]>d-1),(o,a,b)
 down=ray(o,[0,0,-1])[0];up=ray(o,[0,0,1])[0];assert down>3.9 and up>4.19,(o,down,up)
 open_air.append({'origin_mm':o,'north_hits_mm':a,'south_hits_mm':b,'air_to_floor_mm':down,'air_to_roof_mm':up})
checks['all_four_pavilions_are_true_open_column_frames']=True
# East upper porch clear aisle in between front/rear column rows.
o=[56,-7,36.8];a=ray(o,[1,0,0]);b=ray(o,[-1,0,0]);assert not a or a[0]>8;assert not b or b[0]>7
probes['east_upper_clear_aisle']={'origin':o,'east_hits':a,'west_hits':b}
# Entry glass back: starts at x49.4, front colonnade at x60/62.
o=[85,-9.4,14];a=ray(o,[-1,0,0]);assert a and a[0]>30
probes['east_low_entry_clear_to_back']={'origin':o,'hits':a,'first_x':85-a[0]}
checks['east_porches_open_and_glazing_recessed_behind_columns']=True
# Every high-loss original rectangular sample gets original-face X/Y and vertical rays.
loss=json.loads((R/'feature-loss-locations.json').read_text());rr=[];nonrect=[]
for row in loss['high_loss_components']:
 x1,y1,x2,y2=row['bounds'];o=[(x1+x2)/2,(y1+y2)/2,row['z_mm']]
 if abs(row['bbox_area_mm2']-row['original_area_mm2'])<1e-5:
  xx=span(o,0);yy=span(o,1);lo,hi=roots(o);assert min(xx,yy)>2.0998
  assert lo<o[2]-.2 and hi>o[2]+.005
  rr.append({'origin_mm':o,'normal_x_mm':xx,'normal_y_mm':yy,'down_root_z_mm':lo,'up_root_z_mm':hi,'loss_fraction':row['opening_loss_fraction'],'raw_loss_outside_vertex0p41_mm2':row['loss_outside_0p41_vertex_mm2'],'rectangle_area_deviation_mm2':row['bbox_area_mm2']-row['original_area_mm2']})
 else:
  assert row['loss_outside_0p41_vertex_mm2']<1e-10
  nonrect.append({'z_mm':row['z_mm'],'bounds':row['bounds'],'loss_fraction':row['opening_loss_fraction'],'loss_outside_vertex0p41_mm2':row['loss_outside_0p41_vertex_mm2']})
checks['all_high_loss_rectangular_original_samples_have_actual_normals_and_roots']=True
checks['all_nonrectangular_high_loss_is_within_original_vertex0p41_neighbourhoods']=True
# Explicit raw face backing at actual balustrade slot centres and lower transom frames.
rail_rows=[]
# Geometry-derived slot positions, in final mm. These are backing, not unsupported small piers.
for name,x,y,z,axis in [('south_lower_rail',-14.25,-30.5,4.65,1),('south_upper_rail',-14.25,-30.5,8.45,1),('south_roof_rail',-16.5,-26.5,15.7,1),('east_upper_rail',31.6,-11.05,15.4,0),('north_roof_rail',-21.5,5.6,19.7,1)]:
 # use inward point behind the shallow exterior slot
 o=[2*x,2*y,3+2*z];o[axis]+=(-.15 if axis==0 else .15)
 val=span(o,axis);lo,hi=roots(o);assert val>1.1198,(name,val)
 rail_rows.append({'name':name,'origin_mm':o,'actual_normal_mm':val,'down_root_z_mm':lo,'up_root_z_mm':hi})
checks['sampled_backed_rail_slots_have_at_least1p12mm_actual_normal']=True
# At every nonrectangular warning sample, probe each sufficiently long original
# edge midpoint normal, including hole boundaries. No polygon repair/simplify.
from shapely.geometry import Polygon,Point
edge_probes=[]
for row in loss['high_loss_components']:
 if abs(row['bbox_area_mm2']-row['original_area_mm2'])<1e-5:continue
 poly=Polygon(row['original_exterior_mm'],row['original_holes_mm']);assert poly.is_valid
 for ring in [poly.exterior,*poly.interiors]:
  cc=list(ring.coords)
  for a,b in zip(cc,cc[1:]):
   a=np.array(a);b=np.array(b);v=b-a;length=np.linalg.norm(v)
   if length<.8:continue
   n=np.array([-v[1],v[0]])/length;mid=(a+b)/2;pt=mid+.03*n
   if not poly.contains(Point(pt)):n=-n;pt=mid+.03*n
   assert poly.contains(Point(pt)),('edge interior',row['z_mm'],a,b)
   o=[float(pt[0]),float(pt[1]),row['z_mm']];d=[float(n[0]),float(n[1]),0]
   h1=ray(o,d);h2=ray(o,[-d[0],-d[1],0]);assert h1 and h2
   thick=h1[0]+h2[0];lo,hi=roots(o)
   edge_probes.append({'z_mm':row['z_mm'],'origin_mm':o,'normal_direction':d,'edge_length_mm':length,'raw_normal_mm':thick,'down_root_z_mm':lo,'up_root_z_mm':hi})
   assert thick>1.0898,('thin nonrectangular warning edge',o,thick)
checks['all_nonrect_warning_long_edges_actual_normals_at_least1p09mm']=True
report={'passed':all(checks.values()),'checks':checks,'nonrectangular_original_edge_normal_probes':edge_probes,'square_column_segments':columns,'square_column_count':len(columns),'round_columns':rounds,'open_pavilions':open_air,'architectural_air_probes':probes,'rectangular_high_loss_samples':rr,'nonrectangular_high_loss_samples':nonrect,'rail_backing_samples':rail_rows,'high_loss_sample_count':len(loss['high_loss_components']),'rectangular_sample_count':len(rr),'nonrectangular_sample_count':len(nonrect),'max_original_component_loss_fraction':loss['maximum_original_component_loss_fraction'],'specific_exception_status':'pending parent and independent review; numerical buffer deviations on near-collinear raw section vertices retained, not repaired','stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'limitations':'Selected raw normal/root rays; not exhaustive global minimum wall or physical printing.'}
(R/'architectural-ray-check.json').write_text(json.dumps(report,indent=2));print(checks)
