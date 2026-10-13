"""Ray-audit original STL recesses/entry portico. No mesh repair, no real-world survey claim."""
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
test('open_portico_to_recessed_glazing',[-20,-70,20],[0,1,0],1,[1.39,1.41])
test('entrance_door_recess_beyond_glazing',[-9,-70,16],[0,1,0],1,[4.69,4.71])
test('left_round_pier_control',[-50,-70,20],[0,1,0],1,[-35.61,-35.59])
test('right_round_pier_control',[4,-70,20],[0,1,0],1,[-35.61,-35.59])
test('plain_wall_control',[-63,-70,20],[0,1,0],1,[-.01,.01])
test('upper_left_glazing_recess',[-31,-70,60],[0,1,0],1,[1.39,1.41])
test('upper_right_glazing_recess',[38,-70,60],[0,1,0],1,[1.39,1.41])
test('concrete_portico_roof',[-20,-20,130],[0,0,-1],2,[44.29,44.31])
test('right_rain_canopy',[43,-10,130],[0,0,-1],2,[44.49,44.51])
test('recess_under_projecting_upper_beam',[-20,-70,71],[0,1,0],1,[-.01,.01])
test('upper_projecting_lintel_control',[-20,-70,75],[0,1,0],1,[-8.01,-7.99])
test('cropped_upper_beam_top',[20,2,130],[0,0,-1],2,[81.59,81.61])
test('plain_rear_termination',[0,50,60],[0,-1,0],1,[19.99,20.01])
assert p.read_bytes()==before, 'STL changed during read-only audit'
report={'passed':all(x['passed'] for x in rows),'checks':{x['name']:x['passed'] for x in rows},'stl_sha256':hashlib.sha256(before).hexdigest(),'method':'First positive intersection on the original delivered STL; process=False preserves original STL triangles. No repair or modification. Coordinates in millimetres.','limitations':['This establishes modeled recess/open-air geometry, not exact real-world depth.','Only the entry facade is modeled. Rear and side termination planes are not documented elevations.'],'rays':rows}
(R/'recess-ray-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
