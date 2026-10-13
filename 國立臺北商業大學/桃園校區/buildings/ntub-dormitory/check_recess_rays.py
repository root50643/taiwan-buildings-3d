"""Ray-audit original STL recesses/open courtyard. No mesh repair, no real-world survey claim."""
from pathlib import Path
import json, hashlib
import numpy as np
import trimesh
R=Path(__file__).resolve().parent;p=R/'model.stl';before=p.read_bytes()
m=trimesh.load(p,force='mesh',process=True)
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
test('east_lower_double_floor_loggia',[-90,3,36],[1,0,0],0,[-42.51,-42.49])
test('east_upper_double_floor_loggia',[-90,-54,63],[1,0,0],0,[-42.51,-42.49])
test('east_intact_band_control',[-90,3,27],[1,0,0],0,[-66.01,-65.99])
test('courtyard_center_open_to_sky',[0,0,150],[0,0,-1],2,[2.99,3.01])
test('courtyard_north_open_to_sky',[0,-50,150],[0,0,-1],2,[2.99,3.01])
test('courtyard_rear_open_to_sky',[0,18,150],[0,0,-1],2,[2.99,3.01])
test('north_entry_clear_to_rear_wing',[5,-90,10],[0,1,0],1,[39.49,39.51])
test('covered_walkway_does_not_fill_court',[31,0,150],[0,0,-1],2,[15.69,15.71])
assert p.read_bytes()==before, 'STL changed during read-only audit'
report={'passed':all(x['passed'] for x in rows),'checks':{x['name']:x['passed'] for x in rows},'stl_sha256':hashlib.sha256(before).hexdigest(),'method':'First positive intersection on the original delivered STL; process=True only merges matching STL vertices. No repair or modification. Coordinates in millimetres.','limitations':['This establishes modeled recess/open-air geometry, not exact real-world depth.','Positive material behind deep loggia remains deliberately present where actual through-route is unverified.'],'rays':rows}
(R/'recess-ray-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
