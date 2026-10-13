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
test('ground_arcade_recess_behind_front_piers',[2,-80,12],[0,1,0],1,[-35.66,-35.64])
test('upper_arcade_recess_behind_front_piers',[0,-80,32],[0,1,0],1,[-37.01,-36.99])
test('lower_glazing_recess_off_mullion',[2,-80,55],[0,1,0],1,[-51.51,-51.49])
test('upper_glazing_recess_off_mullion',[2,-80,79],[0,1,0],1,[-51.51,-51.49])
test('opaque_spandrel_control',[0,-80,69],[0,1,0],1,[-54.01,-53.99])
test('roof_floor_below_open_crown',[0,-20,150],[0,0,-1],2,[99.99,100.01])
test('crown_rim_top_control',[0,-54,150],[0,0,-1],2,[121.99,122.01])
test('crop_back_plain_face',[0,50,60],[0,-1,0],1,[-.01,.01])
hits,_,_=m.ray.intersects_location([[0,-80,110]],[[0,1,0]],multiple_hits=True)
assert len(hits)==0, 'Crown opening must remain through-open on cropped model'
rows.append({'name':'crown_opening_has_no_blocking_face','origin_mm':[0,-80,110],'direction':[0,1,0],'intersections':0,'passed':True})
assert p.read_bytes()==before, 'STL changed during read-only audit'
report={'passed':all(x['passed'] for x in rows),'checks':{x['name']:x['passed'] for x in rows},'stl_sha256':hashlib.sha256(before).hexdigest(),'method':'First positive intersection on the original delivered STL; process=False preserves original STL triangles. No repair or modification. Coordinates in millimetres.','limitations':['This establishes modeled recess/open-air geometry, not exact real-world depth.','The plain rear plane is an explicit crop, not a documented rear elevation.'],'rays':rows}
(R/'recess-ray-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
