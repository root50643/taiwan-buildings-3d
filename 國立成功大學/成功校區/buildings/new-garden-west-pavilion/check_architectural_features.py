"""Source-specific probes on actual unrepaired STL, independent of build parts.
Positive and negative occupancy probes use three ray directions to detect ambiguity.
"""
from pathlib import Path
import hashlib,json
import numpy as np,trimesh
from original_rays import OriginalRays
R=Path(__file__).resolve().parent
p=json.loads((R/'parameters.json').read_text());s=p['scale_mm_per_m'];floor=p['plinth_top_mm']
m=trimesh.load(R/'model.stl',process=False);ray=OriginalRays(m);T=m.triangles
rows=[]
def occupancy(name,x,y,z,expected):
    q=np.array([x*s,-y*s,floor+z*s]);votes=[]
    for d in [(0.713123,.431977,.552111),(.231513,.877319,.420133),(-.813113,.313177,.492121)]:
        d=np.array(d);d/=np.linalg.norm(d);votes.append(len(ray.hits(q,d))%2==1)
    rows.append({'name':name,'point_mm':q.tolist(),'expected_solid':expected,
                 'three_ray_votes':votes,'passed':all(v==expected for v in votes)})
# Inside roof slab, above low roof: actual triangle intersections must form a
# 99 x 99 mm envelope. No parameter-only roof dimension claim is accepted.
roof_z=floor+p['main_roof_top_m']*s-.35;hits=[]
for tri in T[(T[:,:,2].min(axis=1)<roof_z)&(T[:,:,2].max(axis=1)>roof_z)]:
    for a,b in [(tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])]:
        if min(a[2],b[2])<roof_z<max(a[2],b[2]):hits.append(a+(b-a)*(roof_z-a[2])/(b[2]-a[2]))
if not hits:raise RuntimeError('No actual main-roof section')
h=np.array(hits);extent=np.ptp(h[:,:2],axis=0)
checks={'actual_main_roof_section_99mm_square':bool(np.allclose(extent,[99,99],atol=1e-5)),
        'main_roof_aspect_one':bool(abs(extent[0]/extent[1]-1)<1e-6)}
for name,x,y,z,inside in [
 ('junction_core',8,17,1,True),('west_recess_not_box',3,17,1,False),
 ('east_recess_not_box',14,17,1,False),('northeast_empty_service_envelope',20,17,1,False),
 ('north_low_roof_overlap',3,17,3.05,True),('far_east_service_tail',20,23,1,True),
 ('roof_enclosure',14,15,4.8,True),('outside_roof_enclosure',13,15,4.8,False),
 ('west_tall_window',2+.4/s,20,1.5,False),('west_window_sill',2+.4/s,20,.25,True),
 ('east_service_ground_door',21-.4/s,22.7,.25,False),('east_service_adjacent_wall',21-.4/s,20,.25,True),
 ('west_low_wall',.12,12,.4,True),('west_low_wall_entrance_gap',.12,5,.4,False)]:occupancy(name,x,y,z,inside)
for side,start in [('north',7),('east',7),('west',5)]:
 for leaf in range(6):
  t=start+leaf+.5
  if side=='north':x,y=t,2+.3/s
  elif side=='east':x,y=16-.3/s,t
  else:x,y=2+.3/s,t
  occupancy(f'{side}_door_leaf_{leaf+1}_near_ground',x,y,.25,False)
  occupancy(f'{side}_door_leaf_{leaf+1}_head',x,y,2.30,True)
checks['all_source_specific_solid_air_probes']=all(r['passed'] for r in rows)
r={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),
   'main_roof_section_z_mm':roof_z,'main_roof_section_actual_extents_mm':extent.tolist(),'probes':rows,
   'limits':'Finite probes verify selected source-supported landmarks, not every detail or surveyed precision.'}
(R/'architectural-features.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='probes'},indent=2))
if not r['passed']:raise SystemExit(1)
