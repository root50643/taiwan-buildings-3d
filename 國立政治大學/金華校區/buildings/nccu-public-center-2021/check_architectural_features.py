"""Ray/point evidence on the exact STL for source-critical exterior features.
Coordinates use the documented architectural metre frame (+X east, +Y south).
This checks retention, not survey accuracy; independent visual comparison remains required.
"""
from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from original_rays import OriginalRays
R=Path(__file__).resolve().parent;p=json.loads((R/'parameters.json').read_text());m=trimesh.load(R/'model.stl',process=False);ray=OriginalRays(m)
s=p['scale_mm_per_m'];base=p['base_thickness_mm'];rows=[]
def point(q):return np.array([q[0]*s,-q[1]*s,base+q[2]*s])
d=np.array([.813,.479,.332]);d/=np.linalg.norm(d)
def sample(name,xyz,solid):
    h=ray.hits(point(xyz),d);inside=len(h)%2==1
    rows.append({'name':name,'point_arch_m':xyz,'expected_material':solid,'observed_material':inside,'passed':inside==solid,'original_forward_hits':h})
H=p['hotel_parapet_m'];E=p['exhibition_parapet_m'];G=p['exhibition_central_garden_m']
sample('hotel north projecting core',[3.0,6.5,35.0],True)
for i,(a,b) in enumerate([(39.15,41.35),(47.05,47.95),(49.25,50.15),(58.5,60.7)]):
    origin=point([(a+b)/2,-5,7.0]);h=ray.hits(origin,np.array([0.,-1.,0.]));depth=h[0][0]-5*s
    rows.append({'name':f'four north vertical bands {i+1}','first_hit_depth_mm':depth,'expected_mm':.38*s,'passed':abs(depth-.38*s)<2e-4,'original_hits':h})
for x in [38.1,44.0,48.6,54.5,61.5]:
    origin=point([x,-5,7.0]);h=ray.hits(origin,np.array([0.,-1.,0.]));depth=h[0][0]-5*s
    rows.append({'name':f'north stone interval x{x}','first_hit_depth_mm':depth,'passed':abs(depth)<2e-4,'original_hits':h})
for yi in [16.7,35.1]:sample('east projecting box stack',[64.8,yi,11.0],True)
for yi in [22.0,29.0]:sample('air between east projecting stacks',[64.8,yi,11.0],False)
for side,y in [('south',25.44),('north',8.72)]:
    for row,z in enumerate(p['hotel_window_bottoms_m']):
        x=p['hotel_window_centers_x_m'][2];origin=point([x,y+(3 if side=='south' else -3),z+.75]);direction=np.array([0.,1. if side=='south' else -1.,0.]);h=ray.hits(origin,direction);depth=h[0][0]-3*s
        rows.append({'name':f'hotel {side} recessed row {row+1}','depth_mm':depth,'passed':abs(depth-p['window_recess_mm'])<2e-4,'original_hits':h})
for name,z0z1 in [('4F',p['bridge_lower_m']),('6F',p['bridge_upper_m'])]:sample(name+' bridge solid',[31,25.9,sum(z0z1)/2],True)
sample('air under lower bridge',[31,25.9,p['bridge_lower_m'][0]-.7],False)
sample('air between bridges',[31,25.9,(p['bridge_lower_m'][1]+p['bridge_upper_m'][0])/2],False)
sample('no false high cross bridge',[31,25.9,36.0],False)
sample('lower connecting terrace',[31,19,p['connecting_lower_garden_m']-.4],True)
sample('upper connecting terrace',[31,19,p['connecting_garden_m']-.4],True)
sample('air above connecting roof',[31,19,p['connecting_garden_m']+2.0],False)
sample('central roof garden below floor',[47,22,G-.3],True)
sample('central roof garden open above floor',[47,22,G+1.0],False)
sample('western glazed garden boundary',[37.95,23,G+.5],True)
sample('upper court oblique stair solid',[44,30,G+4],True)
sample('court air north of oblique stair',[44,26,G+4],False)
sample('north roof retained',[44,4,E-1.0],True)
sample('upper south auditorium retained',[53,47,E-1.0],True)
sample('south terrace setback remains open',[53,54,p['exhibition_lower_terrace_m']+2.0],False)
sample('PV array raised relief',[48,44,E+.15],True)
sample('roof space above PV',[48,44,E+1.0],False)
sample('hotel equipment core',[4,11,p['hotel_rooftop_max_m']-.5],True)
sample('exhibition equipment core',[56,18,p['exhibition_rooftop_max_m']-.5],True)
out={'passed':all(q['passed']for q in rows),'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'parameters_sha256':hashlib.sha256((R/'parameters.json').read_bytes()).hexdigest(),'checks':rows,'limitations':'These original-STL ray/point checks preserve named geometry. They do not verify the real-building dimensions or every exterior feature.'}
(R/'architectural-features.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'passed':out['passed'],'failed':[q for q in rows if not q['passed']]},indent=2));raise SystemExit(0 if out['passed']else 1)
