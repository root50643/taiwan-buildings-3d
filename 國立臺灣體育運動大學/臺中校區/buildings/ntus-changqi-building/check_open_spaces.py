"""Ray-check specified actual-STL exterior openings. No mesh repair."""
from pathlib import Path
import json,numpy as np,trimesh
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',force='mesh',process=True)
S=150/68
def p(x,y,z):return np.array([(x-30)*S,-(y-13)*S,(z+1.2)*S])
def ray(name,origin,direction,expected_min,expected_max=None):
 o=np.array(origin);d=np.array(direction,dtype=float);d/=np.linalg.norm(d)
 loc,ri,ti=m.ray.intersects_location([o],[d],multiple_hits=True)
 ds=sorted(float(np.dot(q-o,d)) for q in loc if np.dot(q-o,d)>1e-5)
 nearest=ds[0] if ds else None
 passed=(nearest is None or nearest>expected_min) if expected_max is None else (nearest is not None and expected_min<nearest<expected_max)
 assert passed,(name,nearest,expected_min,expected_max)
 return {'name':name,'origin_mm':o.tolist(),'direction':d.tolist(),'nearest_surface_mm':nearest,'expected_clearance_min_mm':expected_min,'expected_contact_max_mm':expected_max,'passed':passed}
rows=[]
rows.append(ray('Open north external plaza, vertical sky clearance',p(37,4,.3),[0,0,1],100))
rows.append(ray('Open north external plaza, lateral passage to outside',p(27.5,4,2),[1,0,0],70))
rows.append(ray('Canopy front edge to entrance recessed back wall',p(-2.5,5.6,2),[1,0,0],10.0,10.3))
rows.append(ray('Entrance center to canopy underside',p(-1,5.6,1.5),[0,0,1],4.1,4.3))
rows.append(ray('Entrance center to threshold top',p(-1,5.6,1.5),[0,0,-1],2.85,3.05))
rows.append(ray('North stair facade recess is genuinely deep',p(15.2,-5.5,10),[0,-1,0],4.2,4.4))
rows.append(ray('South stair facade recess is genuinely deep',p(10.1,30.5,10),[0,1,0],4.2,4.4))
rows.append(ray('High original green roof is open overhead',p(4.0,10,28.0),[0,0,1],100))
rows.append(ray('Low green terrace is open overhead',p(42,27,21.7),[0,0,1],100))
report={'passed':all(x['passed'] for x in rows),'checks':{'external_plaza_open_to_sky':True,'external_plaza_connects_to_outside':True,'entrance_is_recessed_below_canopy':True,'stair_recesses_have_real_depth':True,'roof_terraces_open_to_sky':True},'rays':rows,'actual_clearances_mm':{'entrance_canopy_front_to_back_wall':rows[2]['nearest_surface_mm'],'entrance_canopy_underside_to_threshold_top':rows[3]['nearest_surface_mm']+rows[4]['nearest_surface_mm'],'north_stair_face_to_recess_back':rows[5]['nearest_surface_mm'],'south_stair_face_to_recess_back':rows[6]['nearest_surface_mm']},'limitations':'Only specified rays are checked. No enclosed courtyard or unsupported all-building through-passage is claimed. The real entrance has a back wall; this test does not invent a through-tunnel.'}
(R/'open-space-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
