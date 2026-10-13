"""Ray-audit original STL recesses/open courtyard. No mesh repair, no real-world survey claim."""
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
test('courtyard_center_open_to_sky',[0,0,150],[0,0,-1],2,[2.99,3.01])
test('courtyard_mouth_open_to_sky',[0,-58,150],[0,0,-1],2,[2.99,3.01])
test('courtyard_back_open_to_sky',[0,24,150],[0,0,-1],2,[2.99,3.01])
test('courtyard_entry_clear_to_back',[5,-90,10],[0,1,0],1,[41.99,42.01])
test('left_balcony_recess',[0,-43,47],[-1,0,0],0,[-30.01,-29.99])
test('right_balcony_recess',[0,-43,47],[1,0,0],0,[29.99,30.01])
test('classroom_shoulder_roof_below_outer_roof',[36,0,150],[0,0,-1],2,[78.79,78.81])
test('outer_wing_higher_roof',[56,0,150],[0,0,-1],2,[91.29,91.31])
test('right_rooftop_loggia_horizontal_gap',[0,0,72],[1,0,0],0,[41.49,41.51])
test('left_rooftop_loggia_horizontal_gap',[0,0,72],[-1,0,0],0,[-41.51,-41.49])
test('lower_classroom_wall_control',[0,0,64],[1,0,0],0,[27.99,28.01])
assert p.read_bytes()==before, 'STL changed during read-only audit'
report={'passed':all(x['passed'] for x in rows),'checks':{x['name']:x['passed'] for x in rows},'stl_sha256':hashlib.sha256(before).hexdigest(),'method':'First positive intersection on the original delivered STL; process=False preserves original STL triangles. No repair or modification. Coordinates in millimetres.','limitations':['This establishes modeled recess/open-air geometry, not exact real-world depth.','Positive material behind deep loggia remains deliberately present where actual through-route is unverified.'],'rays':rows}
(R/'recess-ray-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
