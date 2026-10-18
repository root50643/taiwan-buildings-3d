from pathlib import Path
import json,sys
import check_chengqin_independent as m
from shapely.geometry import Polygon
from shapely.ops import triangulate

def extrude(poly):
    n=len(poly); v=[(float(x),float(y),z) for z in (0.,2.) for x,y in poly]; lookup={tuple(p):i for i,p in enumerate(poly)}; f=[]
    p=Polygon(poly)
    for t in triangulate(p):
        if not p.covers(t): continue
        ids=[lookup[tuple(q)] for q in list(t.exterior.coords)[:3]]
        f.extend([tuple(ids),tuple(i+n for i in ids)])
    for i in range(n):
        j=(i+1)%n; f.extend([(i,j,j+n),(i,j+n,i+n)])
    return v,f

def frustum():
    v=[(x,y,z) for z,b in [(0.,1.),(2.,5.)] for x,y in [(-b,-b),(b,-b),(b,b),(-b,b)]]
    f=[(0,2,1),(0,3,2),(4,5,6),(4,6,7)]
    for i in range(4):
        j=(i+1)%4; f.extend([(i,j,j+4),(i,j+4,i+4)])
    return v,f

zs=[.05+.1*i for i in range(20)]
inputs={
 'clean_cube':extrude([(0,0),(2,0),(2,2),(0,2)]),
 'thin_bar':extrude([(0,0),(.4,0),(.4,2),(0,2)]),
 'thin_neck':extrude([(0,0),(2,0),(2,.8),(4,.8),(4,0),(6,0),(6,2),(4,2),(4,1.2),(2,1.2),(2,2),(0,2)]),
 'steep_frustum':frustum(),
}
v,f=inputs['clean_cube'];inputs['two_supported_components']=(v+[(x+4,y,z) for x,y,z in v],f+[tuple(i+len(v) for i in q) for q in f])
rows={}
for name,(v,f) in inputs.items():
    r=m.sections(v,f,zs)
    rows[name]={k:r[k] for k in ['section_count','max_components','invalid_or_open_sections','component_core_failures','maximum_outside_support_envelope_mm2','support_violations_over_1e_5_mm2']}
    if name=='thin_bar': ok=len(r['component_core_failures'])==20 and all(c['core_components']==0 for row in r['component_core_failures'] for c in row['components'])
    elif name=='thin_neck': ok=len(r['component_core_failures'])==20 and all(c['core_components']==2 for row in r['component_core_failures'] for c in row['components'])
    elif name=='steep_frustum': ok=len(r['support_violations_over_1e_5_mm2'])==19
    else: ok=not r['invalid_or_open_sections'] and not r['component_core_failures'] and not r['support_violations_over_1e_5_mm2']
    rows[name]['passes_expected_behavior']=ok
result={'method':'Own analytic extrusion/frustum fixtures; exercises same independent section code; no candidate QA functions or outputs used. These fixtures are not building QA.','controls':rows,'all_pass':all(r['passes_expected_behavior'] for r in rows.values())}
Path(__file__).with_name('section-controls.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:r['passes_expected_behavior'] for k,r in rows.items()}))
if not result['all_pass']: raise SystemExit(1)
