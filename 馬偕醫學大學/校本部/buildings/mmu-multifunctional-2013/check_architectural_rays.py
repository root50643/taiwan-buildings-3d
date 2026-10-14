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
# Both distinct large glazing systems: actual normal material spans through back.
normal_rows=[]
for name,o,d in [('downhill_glass',[-52,60,28],[0,-1,0]),('downhill_mullion',[-54.2,60,28],[0,-1,0]),('uphill_glass',[-48,-60,25],[0,1,0]),('uphill_mullion',[-50.2,-60,25],[0,1,0]),('equipment_strip',[-90,12,27],[1,0,0])]:
 h=cast(name,o,d);assert len(h)>=2
 span=h[1]-h[0];assert span>1.0
 normal_rows.append({'feature':name,'first_surface_mm':[o[i]+d[i]*h[0] for i in range(3)],'uninterrupted_normal_material_mm':span})
checks['sampled_glass_and_frames_have_solid_backing_no_thin_outer_skin']=True
# Oblique auditorium cutter must reach the real outside face, not create cavity.
a=np.array([29.952,35.022]);b=np.array([44.382,45.006]);u=(b-a)/np.linalg.norm(b-a);inside=np.array([u[1],-u[0]]);mid=(a+b)/2
hall=[]
for z,dx,expected in [(27,0,5.1),(15,0,3.5),(27,1.3,4.625),(31,4,4.625)]:
 xy=mid+u*dx-inside*10;o=[float(xy[0]),float(xy[1]),z];d=[float(inside[0]),float(inside[1]),0]
 h=cast(f'hall_oblique_z{z}_offset{dx}',o,d);assert abs(h[0]-(10+expected))<.0001 and h[1]-h[0]>5
 hall.append({'z_mm':z,'offset_mm':dx,'actual_recess_from_exterior_mm':h[0]-10,'normal_solid_mm':h[1]-h[0]})
checks['hall_deep_recess_is_externally_open_with_thick_back']=True
# Equipment channels open from sky onto tray, not sealed perimeter cavities.
for name,xy,z in [('left_equipment',[-66.8,16],31.3),('right_equipment',[28,12],31.8)]:
 h=cast(name,[*xy,80],[0,0,-1]);assert abs(80-h[0]-z)<.001
checks['equipment_trays_have_open_sky']=True
# Entry: stair meets 12mm landing and recessed foyer; external wing passage
# is genuinely open beneath 21.2mm canopy between the columns and classroom.
h=cast('entry_foyer', [24.5,-70,17],[0,1,0]);checks['entry_foyer_recess_reaches_minus20p4']=abs(-70+h[0]+20.4)<.0001
h=cast('entry_landing', [22.5,-24,40],[0,0,-1]);checks['landing_top_13p4']=abs(40-h[0]-13.4)<.0001
h=cast('wing_corridor_cross',[20,-38,17],[1,0,0]);checks['wing_corridor_cross_open_to_classroom_wall']=abs(20+h[0]-40.8)<.0001
h=cast('wing_corridor_long',[38.5,-70,17],[0,1,0]);checks['wing_corridor_length_open_to_foyer']=(-70+h[0])>-23
h=cast('wing_corridor_down',[38.5,-38,17],[0,0,-1]);checks['corridor_landing_z13p4']=abs(17-h[0]-13.4)<.0001
h=cast('wing_corridor_up',[38.5,-38,17],[0,0,1]);checks['corridor_canopy_underside_z21p2']=abs(17+h[0]-21.2)<.0001
# Flatten only the needle tip of the folded hall, retaining its sloping facets.
from shapely.geometry import MultiPoint
tri=m.triangles
flat=tri[np.all(np.abs(tri[:,:,2]-38.2)<.0001,axis=1)]
assert len(flat)>0
cap=MultiPoint(flat[:,:,:2].reshape(-1,2)).convex_hull;rect=list(cap.minimum_rotated_rectangle.exterior.coords)
cap_width=min(np.linalg.norm(np.array(rect[i])-rect[i+1]) for i in range(4));assert cap_width>.8
c=cap.representative_point();h=cast('hall_flat_cap_down',[c.x,c.y,38.199],[0,0,-1]);assert h[0]>5
checks['hall_flat_cap_has_width_and_downward_solid_root']=True
# Every original polygon over1% loss is independently localized and ray-tested.
loss=json.loads((R/'feature-loss-locations.json').read_text());rows=[];centres=set()
for c in loss['high_loss_components']:
 x1,y1,x2,y2=c['bounds'];o=[(x1+x2)/2,(y1+y2)/2,c['z_mm']]
 assert 13.4<o[2]<21.2 and c['loss_outside_bbox_corners_0p41_mm2']<1e-7
 assert abs((x2-x1)*(y2-y1)-c['original_area_mm2'])<1e-5
 xx=ray(o,[1,0,0])[0]+ray(o,[-1,0,0])[0];yy=ray(o,[0,1,0])[0]+ray(o,[0,-1,0])[0]
 down=o[2]-ray(o,[0,0,-1])[0];up=o[2]+ray(o,[0,0,1])[0]
 assert min(xx,yy)>2.3999 and down<13.4 and up>=22.5999
 centres.add(tuple(round(v,3) for v in o[:2]));rows.append({'z_mm':o[2],'xy_mm':o[:2],'actual_normal_x_mm':xx,'actual_normal_y_mm':yy,'root_bottom_z_mm':down,'root_top_z_mm':up,'loss_fraction':c['opening_loss_fraction'],'loss_outside_bbox_corners_0p41_mm2':c['loss_outside_bbox_corners_0p41_mm2']})
assert len(centres)==2 and len(rows)==78
checks['all78_corner_samples_two_columns_have2p4mm_normal_and_roots']=True
report={'passed':all(checks.values()),'checks':checks,'probes':probes,'normal_samples':normal_rows,'hall_recess_actual_samples':hall,'hall_flat_cap':{'z_mm':38.2,'original_point_z_mm':39,'tip_reduction_mm':.8,'actual_flat_area_mm2':cap.area,'minimum_rotated_bbox_width_mm':float(cap_width)},'column_corner_sample_count':len(rows),'physical_column_count_with_corner_loss':len(centres),'column_samples':rows,'maximum_component_loss_fraction':max(r['loss_fraction'] for r in rows),'stl_sha256':__import__('hashlib').sha256((R/'model.stl').read_bytes()).hexdigest(),'limitations':'Actual original-STL normal and root probes, not global minimum wall or physical print. Two 2.4mm square columns have localized corner loss; requires explicit acceptance.'}
(R/'architectural-ray-check.json').write_text(json.dumps(report,indent=2));print(checks);assert report['passed']
