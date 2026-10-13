"""Ray-audit original STL recesses/open crown. No mesh repair, no real-world survey claim."""
from pathlib import Path
import json, hashlib
import numpy as np
import trimesh
R=Path(__file__).resolve().parent;p=R/'model.stl';before=p.read_bytes()
m=trimesh.load(p,force='mesh',process=False)
rows=[]
def test(name,origin,direction,axis,expected):
 hits,_,_=m.ray.intersects_location([origin],[direction],multiple_hits=True)
 assert len(hits),name+' no intersections'
 o=np.array(origin);d=np.array(direction,dtype=float);d/=np.linalg.norm(d)
 distances=(hits-o)@d;hits=hits[distances>1e-6];distances=distances[distances>1e-6]
 assert len(hits),name+' no forward intersections'
 hit=hits[np.argmin(distances)];value=float(hit[axis]);ok=expected[0]<=value<=expected[1]
 rows.append({'name':name,'origin_mm':origin,'direction':direction,'first_hit_mm':hit.tolist(),'axis_checked':axis,'expected_first_hit_range_mm':expected,'passed':ok})
 assert ok,(name,hit,expected)
test('front_shaft_single_window_recess',[0,-60,60],[0,1,0],1,[-17.71,-17.69])
test('right_shaft_single_window_recess',[60,0,60],[-1,0,0],0,[17.69,17.71])
test('front_head_glazing_recess',[0,-60,122],[0,1,0],1,[-16.76,-16.74])
test('balcony_open_walkway_deck',[22,1,130],[0,0,-1],2,[112.79,112.81])
test('front_balcony_through_square_hole',[-15,-60,114.8],[0,1,0],1,[-18.01,-17.99])
test('front_balcony_solid_parapet_control',[0,-60,114.8],[0,1,0],1,[-26.51,-26.49])
test('rear_blank_face',[0,60,60],[0,-1,0],1,[18.99,19.01])
test('gable_peak_top',[17,0,170],[0,0,-1],2,[149.99,150.01])
# Enumerate original ray intersections through the two ridge-end gables.
hits,_,_=m.ray.intersects_location([[60,0,149]], [[-1,0,0]],multiple_hits=True)
xs=sorted(set(round(float(h[0]),5) for h in hits),reverse=True)
assert xs==[18.5,15.5,-15.5,-18.5],xs
rows.append({'name':'two_gables_each_3mm_thick_original_stl','origin_mm':[60,0,149],'direction':[-1,0,0],'x_intersections_mm':xs,'wall_thicknesses_mm':[3.0,3.0],'passed':True})
# The ridge cap is deliberately flattened 5mm at each peak, no zero-width tip.
hits,_,_=m.ray.intersects_location([[17,-60,149.99]], [[0,1,0]],multiple_hits=True)
ys=sorted(set(round(float(h[1]),5) for h in hits))
assert len(ys)==2 and ys[1]-ys[0]>=5.0,ys
rows.append({'name':'finite_gable_peak_width_original_stl','origin_mm':[17,-60,149.99],'direction':[0,1,0],'y_intersections_mm':ys,'width_mm':ys[1]-ys[0],'passed':True})
# Four upturned gable ends have a deliberate 2mm plateau, verified just below top.
hits,_,_=m.ray.intersects_location([[17,-60,136.99]],[[0,1,0]],multiple_hits=True)
ys=sorted(set(round(float(h[1]),5) for h in hits))
assert len(ys)==6,ys
spans=[ys[i+1]-ys[i] for i in [0,2,4]]
assert min(spans)>=2.0,(ys,spans)
rows.append({'name':'gable_upturned_end_widths_at_136_99mm','origin_mm':[17,-60,136.99],'direction':[0,1,0],'y_intersections_mm':ys,'solid_spans_mm':spans,'minimum_tip_width_mm':min(spans),'passed':True})
# Outer eave corner cap is supported through 4.9mm of solid material.
hits,_,_=m.ray.intersects_location([[28,28,170]],[[0,0,-1]],multiple_hits=True)
zs=sorted(set(round(float(h[2]),5) for h in hits)),
zs=zs[0]
assert abs(zs[-1]-zs[-2]-4.9)<.001,zs
rows.append({'name':'outer_roof_corner_finite_vertical_thickness','origin_mm':[28,28,170],'direction':[0,0,-1],'z_intersections_mm':zs,'roof_thickness_mm':zs[-1]-zs[-2],'passed':True})
assert p.read_bytes()==before, 'STL changed during read-only audit'
report={'passed':all(x['passed'] for x in rows),'checks':{x['name']:x['passed'] for x in rows},'stl_sha256':hashlib.sha256(before).hexdigest(),'method':'First positive intersection on the original delivered STL; process=False preserves original STL triangles. No repair or modification. Coordinates in millimetres.','limitations':['This establishes modeled recess/open-air geometry, not exact real-world depth.','The plain rear elevation omits unknown openings and attachment to the main library; this is a tower segment only.'],'rays':rows}
(R/'recess-ray-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
